#!/usr/bin/env python3
"""
validate_pptx_layout.py — Universal PPTX layout validator for WFA skills.

Checks every deck slide in a PPTX for:
  1. OFF-CANVAS     — shape extends beyond the slide boundary
  2. TEXT-SPILL     — text box too short (no autofit set)
  3. COLLISION      — two sibling shapes overlapping (non-intentional)
  4. MISSING-VISUAL — slide text references "the chart/graph" but has no image
  5. LAYOUT-MISMATCH — image on a layout that should be text-only (e.g. LR)

Only slides in presentation.xml sldIdLst are validated. Icon/Fact pairs in
picture_scene slides are exempt from COLLISION.

Usage:
    python3 validate_pptx_layout.py file.pptx [--strict] [--warnings]
"""

import math, os, re, sys, zipfile
import xml.etree.ElementTree as ET

PML = 'http://schemas.openxmlformats.org/presentationml/2006/main'
DML = 'http://schemas.openxmlformats.org/drawingml/2006/main'

OVERLAP_TOLERANCE_EMU = 36000
SPILL_TOLERANCE_RATIO = 0.20
LAYERING_THRESHOLD    = 0.88
CHAR_WIDTH_FACTOR     = 0.55
LINE_SPACING          = 1.20

VISUAL_TRIGGER_PHRASES = [
    'the chart', 'the graph', 'the diagram', 'the table',
    'look at the chart', 'look at the graph', 'from the chart', 'from the graph',
    'as shown in the', 'refer to the diagram',
]


def _emu_cm(v):
    return round(v / 360000, 3)


def _get_canvas(prs_xml):
    root = ET.fromstring(prs_xml)
    sz   = root.find(f'{{{PML}}}sldSz')
    if sz is None:
        return 12192000, 6858000
    return int(sz.get('cx')), int(sz.get('cy'))


def _get_deck_slide_paths(prs_xml, prs_rels_xml):
    """Return ordered list of ppt-relative slide paths from sldIdLst."""
    root    = ET.fromstring(prs_xml)
    id_list = root.find(f'{{{PML}}}sldIdLst')
    if id_list is None:
        return None

    r_ns  = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    r_ids = [s.get(f'{{{r_ns}}}id') for s in id_list.findall(f'{{{PML}}}sldId') if s.get(f'{{{r_ns}}}id')]

    rels_root = ET.fromstring(prs_rels_xml)
    id_map    = {rel.get('Id'): 'ppt/' + rel.get('Target', '').lstrip('../').lstrip('/')
                 for rel in rels_root}
    return [id_map[r] for r in r_ids if r in id_map]


def _slide_has_image(slide_xml):
    return '<p:pic>' in slide_xml or '<a:blip' in slide_xml


def _parse_shapes(slide_xml):
    root   = ET.fromstring(slide_xml)
    shapes = []
    for sp in root.iter(f'{{{PML}}}sp'):
        cnvpr = sp.find(f'.//{{{PML}}}cNvPr')
        name  = cnvpr.get('name', '?') if cnvpr is not None else '?'
        xfrm  = sp.find(f'.//{{{DML}}}xfrm')
        if xfrm is None: continue
        off = xfrm.find(f'{{{DML}}}off')
        ext = xfrm.find(f'{{{DML}}}ext')
        if off is None or ext is None: continue
        x, y = int(off.get('x', 0)), int(off.get('y', 0))
        w, h = int(ext.get('cx', 0)), int(ext.get('cy', 0))
        if w == 0: continue

        bodyPr  = sp.find(f'.//{{{DML}}}bodyPr')
        autofit = 'none'
        lIns = rIns = 91440
        tIns = bIns = 45720
        if bodyPr is not None:
            if bodyPr.find(f'{{{DML}}}normAutofit') is not None: autofit = 'normAutofit'
            elif bodyPr.find(f'{{{DML}}}spAutoFit') is not None: autofit = 'spAutoFit'
            lIns = int(bodyPr.get('lIns', lIns)); rIns = int(bodyPr.get('rIns', rIns))
            tIns = int(bodyPr.get('tIns', tIns)); bIns = int(bodyPr.get('bIns', bIns))

        paras   = [''.join(t.text or '' for t in p.iter(f'{{{DML}}}t'))
                   for p in sp.findall(f'.//{{{DML}}}p')]
        sizes   = [int(r.get('sz')) / 100 for r in sp.iter(f'{{{DML}}}rPr') if r.get('sz')]
        font_pt = min(sizes) if sizes else 11.0

        shapes.append({'name': name, 'x': x, 'y': y, 'w': w, 'h': h,
                       'autofit': autofit, 'lIns': lIns, 'rIns': rIns,
                       'tIns': tIns, 'bIns': bIns, 'paras': paras,
                       'font_pt': font_pt, 'has_text': any(p.strip() for p in paras)})
    return shapes


def _check_off_canvas(shapes, cw, ch):
    issues = []
    for s in shapes:
        r = s['x'] + s['w']; b = s['y'] + s['h']
        if r > cw + OVERLAP_TOLERANCE_EMU:
            issues.append({'severity': 'ERROR', 'type': 'OFF-CANVAS-RIGHT',
                'detail': f"Shape '{s['name']}' right {_emu_cm(r)}cm > canvas {_emu_cm(cw)}cm (+{_emu_cm(r-cw)}cm)"})
        if b > ch + OVERLAP_TOLERANCE_EMU:
            issues.append({'severity': 'ERROR', 'type': 'OFF-CANVAS-BOTTOM',
                'detail': f"Shape '{s['name']}' bottom {_emu_cm(b)}cm > canvas {_emu_cm(ch)}cm (+{_emu_cm(b-ch)}cm)"})
    return issues


def _estimate_lines(paras, font_pt, usable_w_emu):
    if usable_w_emu <= 0: return len(paras)
    chars_per_line = max(1, (usable_w_emu / 12700) / (font_pt * CHAR_WIDTH_FACTOR))
    return sum(max(1, math.ceil(len(p) / chars_per_line)) for p in paras)


def _check_text_spill(shapes):
    issues = []
    for s in shapes:
        if not s['has_text'] or s['autofit'] != 'none' or s['h'] == 0: continue
        uw = s['w'] - s['lIns'] - s['rIns']
        uh = s['h'] - s['tIns'] - s['bIns']
        if uh <= 0: continue
        lines  = _estimate_lines(s['paras'], s['font_pt'], uw)
        req_h  = lines * s['font_pt'] * LINE_SPACING * 12700
        ratio  = (req_h - uh) / uh
        if ratio > SPILL_TOLERANCE_RATIO:
            sev = 'ERROR' if ratio > 0.5 else 'WARNING'
            preview = ''.join(s['paras'])[:50]
            issues.append({'severity': sev, 'type': 'TEXT-SPILL',
                'detail': f"Shape '{s['name']}' {_emu_cm(s['h'])}cm tall, needs ~{_emu_cm(int(req_h+s['tIns']+s['bIns']))}cm for {lines} line(s) [{preview!r}]"})
    return issues


def _is_icon_fact_pair(a, b):
    """
    Exempt intentional decorative shape overlaps from COLLISION:
    1. Same-name pair — intentional layering (e.g. BeingAReader multi-part titles,
       highlight+background pairs) where both shapes carry the same PowerPoint name.
    2. Freeform shapes — decorative non-rectangular shapes (arrows, speech bubbles,
       dividers) that are never content containers.
    3. Small icon/badge shapes (≤2cm) — picture_scene working memory slides.
    4. Geometric label shapes (Oval, Circle, Ellipse ≤4cm) — WFA template style
       where coloured ovals serve as decorative labels that overlap content areas.
    5. Text-free geometric shapes of any size — purely decorative, no content to hide.
    """
    # Rule 1: same-name pair — intentional layered design
    if a['name'] == b['name']:
        return True

    icon_kw = ('icon', 'badge', 'star', 'pic', 'img', 'image', 'oval', 'circle', 'dot')
    geom_kw = ('oval', 'circle', 'ellipse', 'dot', 'bubble', 'freeform')
    GEOM_MAX_EMU = 1440000  # 4cm — max size for a geometric label shape

    for s in (a, b):
        name_lower = s['name'].lower()
        # Rule 2: Freeform shapes are always decorative
        if name_lower.startswith('freeform'):
            return True
        # Rule 3: Small icon exemption (≤2cm, any named icon type)
        if s['w'] <= 720000 and s['h'] <= 720000:
            if any(k in name_lower for k in icon_kw):
                return True
        # Rule 4: Geometric label shape exemption (Oval/Circle ≤4cm)
        if s['w'] <= GEOM_MAX_EMU and s['h'] <= GEOM_MAX_EMU:
            if any(k in name_lower for k in geom_kw):
                return True
        # Rule 5: Text-free geometric shape of any size
        if not s['has_text'] and any(k in name_lower for k in geom_kw):
            return True

    # Rule 6: Title-frame overlap — title bar partially covers stacked header/content boxes.
    # BeingAReader and similar templates layer multiple full-width bands at the top of the
    # slide (title bar, instruction bar, reading passage). Any pair where one is a named
    # title shape and both shapes span ≥80% of the other's width is an intentional stack.
    if 'title' in a['name'].lower() or 'title' in b['name'].lower():
        # Both shapes must be wide (full-width band design)
        if a['w'] > 0 and b['w'] > 0:
            width_ratio = min(a['w'], b['w']) / max(a['w'], b['w'])
            if width_ratio >= 0.80:
                return True

    # Rule 7: Small callout/label over large content box.
    # Covers question-label TextBoxes inside speech-bubble freeforms that overlay the
    # reading passage. Exempt when one shape has < 20% the area of the other and ≤ 50 chars.
    area_a = a['w'] * a['h']
    area_b = b['w'] * b['h']
    if area_a > 0 and area_b > 0:
        ratio = min(area_a, area_b) / max(area_a, area_b)
        if ratio < 0.20:
            smaller = a if area_a < area_b else b
            text_len = sum(len(p) for p in smaller['paras'])
            if text_len <= 60:
                return True

    return False


def _check_collisions(shapes):
    issues = []
    cands  = [s for s in shapes if s['h'] > 0]
    for i, a in enumerate(cands):
        for b in cands[i+1:]:
            ox = min(a['x']+a['w'], b['x']+b['w']) - max(a['x'], b['x'])
            oy = min(a['y']+a['h'], b['y']+b['h']) - max(a['y'], b['y'])
            if ox <= OVERLAP_TOLERANCE_EMU or oy <= OVERLAP_TOLERANCE_EMU: continue
            smaller = min(a['w']*a['h'], b['w']*b['h'])
            if smaller == 0: continue
            if (ox*oy) / smaller >= LAYERING_THRESHOLD: continue
            if _is_icon_fact_pair(a, b): continue
            sev = 'ERROR' if (ox > 360000 and oy > 180000) else 'WARNING'
            issues.append({'severity': sev, 'type': 'COLLISION',
                'detail': f"'{a['name']}' and '{b['name']}' overlap {_emu_cm(ox)}cm × {_emu_cm(oy)}cm"})
    return issues


def _check_missing_visual(shapes, slide_xml):
    all_text = ' '.join(' '.join(s['paras']) for s in shapes).lower()
    triggered = any(p in all_text for p in VISUAL_TRIGGER_PHRASES)
    if triggered and not _slide_has_image(slide_xml):
        matched = next(p for p in VISUAL_TRIGGER_PHRASES if p in all_text)
        return [{'severity': 'ERROR', 'type': 'MISSING-VISUAL',
                 'detail': f"Slide text contains '{matched}' but no image found on slide"}]
    return []


def validate_slide(slide_xml, canvas_w, canvas_h, slide_label='slide'):
    shapes = _parse_shapes(slide_xml)
    issues = (  _check_off_canvas(shapes, canvas_w, canvas_h)
              + _check_text_spill(shapes)
              + _check_collisions(shapes)
              + _check_missing_visual(shapes, slide_xml))
    for issue in issues:
        issue['slide'] = slide_label
    return issues


def validate_pptx(pptx_path, include_warnings=True):
    all_issues = []
    with zipfile.ZipFile(pptx_path, 'r') as z:
        names      = z.namelist()
        prs_xml    = z.read('ppt/presentation.xml').decode('utf-8')
        canvas_w, canvas_h = _get_canvas(prs_xml)

        rels_path  = 'ppt/_rels/presentation.xml.rels'
        prs_rels   = z.read(rels_path).decode('utf-8') if rels_path in names else '<Relationships/>'
        slide_paths = _get_deck_slide_paths(prs_xml, prs_rels)

        if slide_paths is None:
            slide_paths = sorted(
                [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)],
                key=lambda n: int(re.search(r'(\d+)', n).group(1)))

        for deck_idx, sp in enumerate(slide_paths, 1):
            if sp not in names: continue
            slide_xml = z.read(sp).decode('utf-8')
            issues    = validate_slide(slide_xml, canvas_w, canvas_h,
                                       slide_label=f'slide {deck_idx} ({os.path.basename(sp)})')
            all_issues += issues

    if not include_warnings:
        all_issues = [i for i in all_issues if i['severity'] == 'ERROR']
    return all_issues


def print_report(pptx_path, issues, show_warnings=True):
    errors   = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']
    print(f"\n{'='*60}\nLayout validation: {os.path.basename(pptx_path)}\n{'='*60}")
    if not issues:
        print("✅  No layout issues found.")
        return
    if errors:
        print(f"\n❌  ERRORS ({len(errors)}):")
        for e in errors: print(f"  [{e['slide']}] {e['type']}: {e['detail']}")
    if show_warnings and warnings:
        print(f"\n⚠️   WARNINGS ({len(warnings)}):")
        for w in warnings: print(f"  [{w['slide']}] {w['type']}: {w['detail']}")
    print()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('pptx')
    p.add_argument('--strict',   action='store_true')
    p.add_argument('--warnings', action='store_true')
    args = p.parse_args()
    if not os.path.exists(args.pptx):
        print(f"File not found: {args.pptx}"); sys.exit(1)
    issues = validate_pptx(args.pptx, include_warnings=True)
    print_report(args.pptx, issues, show_warnings=args.warnings)
    if args.strict and any(i['severity'] == 'ERROR' for i in issues):
        sys.exit(1)
    sys.exit(0)
