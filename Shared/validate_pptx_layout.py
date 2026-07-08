#!/usr/bin/env python3
"""
validate_pptx_layout.py — Universal PPTX layout validator for WFA skills.

Checks every slide in a PPTX for five categories of error:
  1. OFF-CANVAS     — any shape extending beyond the slide boundary
  2. TEXT-SPILL     — text box too short to hold its content (no autofit set)
  3. COLLISION      — two sibling-level shapes overlapping
  4. MISSING-VISUAL — slide text references a chart/graph/diagram but no image present
  5. LAYOUT-MISMATCH— slide uses a layout whose name conflicts with its content

Usage:
    python3 validate_pptx_layout.py file.pptx
    python3 validate_pptx_layout.py file.pptx --strict    # exit 1 on any ERROR
    python3 validate_pptx_layout.py file.pptx --warnings  # show warnings too
    python3 validate_pptx_layout.py file.pptx --render    # pixel-level render check

As a module:
    from validate_pptx_layout import validate_pptx
    issues = validate_pptx('output.pptx')
    errors = [i for i in issues if i['severity'] == 'ERROR']
"""

import math, os, re, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

PML  = 'http://schemas.openxmlformats.org/presentationml/2006/main'
DML  = 'http://schemas.openxmlformats.org/drawingml/2006/main'

OVERLAP_TOLERANCE_EMU = 36000
SPILL_TOLERANCE_RATIO = 0.20
LAYERING_THRESHOLD    = 0.88
CHAR_WIDTH_FACTOR     = 0.55
LINE_SPACING          = 1.20

# Keywords that mean a visual should be on this slide
VISUAL_REF_RE = re.compile(
    r'\b(the|this)\s+(bar\s+|line\s+|double\s+bar\s+|double\s+)?'
    r'(chart|graph|pictogram|table|diagram|image|picture|photograph)\b'
    r'|looks?\s+at\s+the\b'
    r'|\busing\s+the\s+(chart|graph|data|table|diagram)\b'
    r'|\bfrom\s+the\s+(chart|graph|table|diagram)\b'
    r'|\bread\s+the\s+(chart|graph|table|diagram)\b',
    re.IGNORECASE
)

# Layout name fragment → XML content indicator → human description
LAYOUT_CONFLICTS = [
    ('learning review', '<p:pic',     'Photo slide on Learning Review layout — layout avatars will bleed through'),
    ('learning review', 'blipFill',   'Image fill on Learning Review layout — layout avatars will bleed through'),
]


def _emu_cm(v):
    return round(v / 360000, 3)


def _get_canvas(prs_xml):
    if isinstance(prs_xml, bytes):
        prs_xml = prs_xml.decode()
    root = ET.fromstring(prs_xml)
    sz = root.find(f'{{{PML}}}sldSz')
    if sz is None:
        return 12192000, 6858000
    return int(sz.get('cx')), int(sz.get('cy'))


def _get_layout_name(pptx_zip, slide_path):
    """Follow slide → slideLayout relationship and return the layout's cSld name."""
    parts    = slide_path.split('/')
    rels_path = '/'.join(parts[:-1] + ['_rels', parts[-1] + '.rels'])
    try:
        rels_xml = pptx_zip.read(rels_path).decode()
    except KeyError:
        return ''
    root = ET.fromstring(rels_xml)
    for rel in root:
        if 'slideLayout' in rel.get('Type', ''):
            target      = rel.get('Target', '')
            layout_path = 'ppt/slideLayouts/' + target.split('/')[-1]
            try:
                layout_xml = pptx_zip.read(layout_path).decode()
            except KeyError:
                return ''
            lroot = ET.fromstring(layout_xml)
            csld  = lroot.find(f'{{{PML}}}cSld')
            return csld.get('name', '') if csld is not None else ''
    return ''


def _parse_shapes(slide_xml):
    if isinstance(slide_xml, bytes):
        slide_xml = slide_xml.decode()
    root   = ET.fromstring(slide_xml)
    shapes = []
    for sp in root.iter(f'{{{PML}}}sp'):
        cnvpr = sp.find(f'.//{{{PML}}}cNvPr')
        name  = cnvpr.get('name', '?') if cnvpr is not None else '?'
        xfrm  = sp.find(f'.//{{{DML}}}xfrm')
        if xfrm is None:
            continue
        off = xfrm.find(f'{{{DML}}}off')
        ext = xfrm.find(f'{{{DML}}}ext')
        if off is None or ext is None:
            continue
        x = int(off.get('x', 0)); y = int(off.get('y', 0))
        w = int(ext.get('cx', 0)); h = int(ext.get('cy', 0))
        if w == 0:
            continue
        bodyPr  = sp.find(f'.//{{{DML}}}bodyPr')
        autofit = 'none'
        lIns = rIns = 91440; tIns = bIns = 45720
        if bodyPr is not None:
            if bodyPr.find(f'{{{DML}}}normAutofit') is not None:
                autofit = 'normAutofit'
            elif bodyPr.find(f'{{{DML}}}spAutoFit') is not None:
                autofit = 'spAutoFit'
            lIns = int(bodyPr.get('lIns', lIns)); rIns = int(bodyPr.get('rIns', rIns))
            tIns = int(bodyPr.get('tIns', tIns)); bIns = int(bodyPr.get('bIns', bIns))
        paras = [''.join(t.text or '' for t in p.iter(f'{{{DML}}}t'))
                 for p in sp.findall(f'.//{{{DML}}}p')]
        sizes = [int(r.get('sz')) / 100 for r in sp.iter(f'{{{DML}}}rPr') if r.get('sz')]
        shapes.append({
            'name': name, 'x': x, 'y': y, 'w': w, 'h': h,
            'autofit': autofit,
            'lIns': lIns, 'rIns': rIns, 'tIns': tIns, 'bIns': bIns,
            'paras': paras, 'font_pt': min(sizes) if sizes else 11.0,
            'has_text': any(p.strip() for p in paras),
        })
    return shapes


def _slide_has_image(slide_xml):
    if isinstance(slide_xml, bytes):
        slide_xml = slide_xml.decode()
    return f'{{{PML}}}pic' in slide_xml or f'{{{DML}}}blipFill' in slide_xml


def _full_text(shapes):
    return ' '.join(' '.join(s['paras']) for s in shapes).lower()


# ── Check functions ──────────────────────────────────────────────────────────

def _check_off_canvas(shapes, cw, ch):
    issues = []
    for s in shapes:
        r = s['x'] + s['w']; b = s['y'] + s['h']
        if r > cw + OVERLAP_TOLERANCE_EMU:
            issues.append({'severity': 'ERROR', 'type': 'OFF-CANVAS-RIGHT',
                'detail': f"Shape '{s['name']}' right {_emu_cm(r)}cm > canvas {_emu_cm(cw)}cm"})
        if b > ch + OVERLAP_TOLERANCE_EMU:
            issues.append({'severity': 'ERROR', 'type': 'OFF-CANVAS-BOTTOM',
                'detail': f"Shape '{s['name']}' bottom {_emu_cm(b)}cm > canvas {_emu_cm(ch)}cm"})
    return issues


def _check_text_spill(shapes):
    issues = []
    for s in shapes:
        if not s['has_text'] or s['autofit'] != 'none' or s['h'] == 0:
            continue
        usable_w = s['w'] - s['lIns'] - s['rIns']
        usable_h = s['h'] - s['tIns'] - s['bIns']
        if usable_h <= 0:
            continue
        usable_w_pt     = usable_w / 12700
        chars_per_line  = max(1, usable_w_pt / (s['font_pt'] * CHAR_WIDTH_FACTOR))
        total_lines     = sum(max(1, math.ceil(len(p) / chars_per_line)) for p in s['paras'])
        required_h      = total_lines * s['font_pt'] * LINE_SPACING * 12700
        overflow_ratio  = (required_h - usable_h) / usable_h
        if overflow_ratio > SPILL_TOLERANCE_RATIO:
            sev = 'ERROR' if overflow_ratio > 0.5 else 'WARNING'
            issues.append({'severity': sev, 'type': 'TEXT-SPILL',
                'detail': (f"Shape '{s['name']}' {_emu_cm(s['h'])}cm tall, "
                           f"needs ~{_emu_cm(int(required_h + s['tIns'] + s['bIns']))}cm "
                           f"for {total_lines} lines at {s['font_pt']:.0f}pt "
                           f"[{''.join(s['paras'])[:50]!r}]")})
    return issues


def _check_collisions(shapes):
    issues     = []
    candidates = [s for s in shapes if s['h'] > 0]
    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            ox = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
            oy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
            if ox <= OVERLAP_TOLERANCE_EMU or oy <= OVERLAP_TOLERANCE_EMU:
                continue
            smaller = min(a['w'] * a['h'], b['w'] * b['h'])
            if smaller and (ox * oy) / smaller >= LAYERING_THRESHOLD:
                continue
            # Intentional design: emoji/icon shapes overlapping adjacent fact cards
            # in picture_scene slides — the icon sits at the left edge of the card
            import re as _re
            if (_re.search(r'^Icon\s*\d+$', a['name'], _re.I) and
                    _re.search(r'^Fact\s*\d+$', b['name'], _re.I)):
                continue
            if (_re.search(r'^Icon\s*\d+$', b['name'], _re.I) and
                    _re.search(r'^Fact\s*\d+$', a['name'], _re.I)):
                continue
            sev = 'ERROR' if (ox > 360000 and oy > 180000) else 'WARNING'
            issues.append({'severity': sev, 'type': 'COLLISION',
                'detail': (f"'{a['name']}' and '{b['name']}' overlap "
                           f"{_emu_cm(ox)}cm × {_emu_cm(oy)}cm")})
    return issues


def _check_visual_reference(shapes, slide_xml):
    """
    Slide text mentions a chart/graph/diagram/table/image → image must be present.
    Catches the 'Spot the mistake — looks at the Bristol/Manaus chart' bug where
    the chart was referenced in text but never embedded on the slide.
    """
    text  = _full_text(shapes)
    match = VISUAL_REF_RE.search(text)
    if not match:
        return []
    if _slide_has_image(slide_xml):
        return []
    snippet = text[max(0, match.start() - 10): match.end() + 40].strip()
    return [{'severity': 'ERROR', 'type': 'MISSING-VISUAL',
             'detail': (f"Text references a visual ('{match.group().strip()}') "
                        f"but no image is on this slide. Context: '...{snippet}...' "
                        f"— embed the chart/diagram before delivering.")}]


def _check_layout_mismatch(layout_name, slide_xml):
    """
    Detect known bad layout assignments — e.g. photo slides on Learning Review
    layout, which has child avatars baked into the layout that bleed through.
    """
    if not layout_name:
        return []
    ll = layout_name.lower()
    if isinstance(slide_xml, bytes):
        slide_xml = slide_xml.decode()
    issues = []
    for fragment, xml_marker, description in LAYOUT_CONFLICTS:
        if fragment in ll and xml_marker in slide_xml:
            issues.append({'severity': 'ERROR', 'type': 'LAYOUT-MISMATCH',
                           'detail': f"Layout '{layout_name}': {description}"})
    return issues


# ── Render check (optional) ──────────────────────────────────────────────────

def _render_check(pptx_path):
    """
    Convert to PDF via LibreOffice, rasterise at 96dpi, and flag slides
    whose bottom half is almost entirely blank (suggests an empty chart placeholder).
    Requires Pillow.
    """
    try:
        from PIL import Image
    except ImportError:
        return [{'severity': 'WARNING', 'type': 'RENDER-SKIP', 'slide': 'all',
                 'detail': 'Pillow not installed — pixel render check skipped'}]

    soffice = '/mnt/skills/public/pptx/scripts/office/soffice.py'
    issues  = []
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(
            ['python3', soffice, '--headless', '--convert-to', 'pdf', '--outdir', tmp, pptx_path],
            capture_output=True, timeout=120
        )
        base     = os.path.splitext(os.path.basename(pptx_path))[0]
        pdf_path = os.path.join(tmp, base + '.pdf')
        if not os.path.exists(pdf_path):
            return [{'severity': 'WARNING', 'type': 'RENDER-SKIP', 'slide': 'all',
                     'detail': 'LibreOffice PDF conversion failed'}]

        subprocess.run(['pdftoppm', '-jpeg', '-r', '96', pdf_path, os.path.join(tmp, 'pg')],
                       capture_output=True, timeout=60)
        pages = sorted(f for f in os.listdir(tmp) if f.startswith('pg') and f.endswith('.jpg'))

        for i, page in enumerate(pages, 1):
            img  = Image.open(os.path.join(tmp, page)).convert('RGB')
            w, h = img.size
            bh   = img.crop((0, h // 2, w, h))
            px   = list(bh.getdata())
            near_white = sum(1 for r, g, b in px if r > 245 and g > 245 and b > 245)
            ratio = near_white / len(px)
            if ratio > 0.65:
                issues.append({'severity': 'WARNING', 'type': 'RENDER-BLANK-BOTTOM',
                               'slide': f'slide {i}',
                               'detail': f'{ratio:.0%} of bottom half is near-white — possible empty chart placeholder'})
    return issues


# ── Main ─────────────────────────────────────────────────────────────────────

def validate_pptx(pptx_path, include_warnings=True, render=False):
    """
    Validate slides referenced in presentation.xml only.
    Orphaned slide XML files left in the zip by build scripts (e.g. working
    memory template slides that are removed from sldIdLst but not from the zip)
    are ignored — they are never shown by PowerPoint.
    """
    all_issues = []
    with zipfile.ZipFile(pptx_path, 'r') as z:
        names = z.namelist()
        canvas_w, canvas_h = _get_canvas(z.read('ppt/presentation.xml'))

        # Build the set of referenced slide files from sldIdLst in presentation.xml
        # This is the AUTHORITATIVE list of what PowerPoint actually shows.
        # The presentation rels file lists ALL slides ever added (including ones
        # removed from sldIdLst by build scripts), so we don't use it here.
        referenced = set()
        try:
            prs_xml_str = z.read('ppt/presentation.xml').decode()
            prs_rels    = z.read('ppt/_rels/presentation.xml.rels').decode()

            # Build rId → slide filename map from rels
            rid_to_slide = {}
            for m in re.finditer(
                r'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', prs_rels
            ):
                rid_to_slide[m.group(1)] = f'ppt/slides/{m.group(2)}'

            # sldIdLst lists the rIds of slides that are actually in the deck
            # <p:sldId id="..." r:id="rId5"/>
            for m in re.finditer(r'r:id="(rId\d+)"', prs_xml_str):
                rid = m.group(1)
                if rid in rid_to_slide:
                    referenced.add(rid_to_slide[rid])
        except KeyError:
            pass

        if not referenced:
            referenced = {n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)}

        slide_files = sorted(
            [n for n in referenced if n in names],
            key=lambda n: int(re.search(r'(\d+)', n).group(1))
        )

        for sp in slide_files:
            num        = re.search(r'(\d+)', sp).group(1)
            slide_xml  = z.read(sp).decode()
            layout     = _get_layout_name(z, sp)
            shapes     = _parse_shapes(slide_xml)
            label      = f'slide {num}'
            issues     = []
            issues    += _check_off_canvas(shapes, canvas_w, canvas_h)
            issues    += _check_text_spill(shapes)
            issues    += _check_collisions(shapes)
            issues    += _check_visual_reference(shapes, slide_xml)
            issues    += _check_layout_mismatch(layout, slide_xml)
            for issue in issues:
                issue['slide'] = label
            all_issues += issues

    if render:
        for ri in _render_check(pptx_path):
            if 'slide' not in ri:
                ri['slide'] = 'all'
            all_issues.append(ri)

    if not include_warnings:
        all_issues = [i for i in all_issues if i['severity'] == 'ERROR']
    return all_issues


def print_report(pptx_path, issues, show_warnings=True):
    errors   = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']
    print(f"\n{'='*65}")
    print(f"WFA PPTX Validator  —  {os.path.basename(pptx_path)}")
    print(f"{'='*65}")
    if not issues:
        print('✅  No layout issues found.')
        return
    if errors:
        print(f'\n❌  ERRORS ({len(errors)}):')
        for e in errors:
            print(f"  [{e['slide']}] {e['type']}: {e['detail']}")
    if show_warnings and warnings:
        print(f'\n⚠️   WARNINGS ({len(warnings)}):')
        for w in warnings:
            print(f"  [{w['slide']}] {w['type']}: {w['detail']}")
    print()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='WFA PPTX layout validator')
    p.add_argument('pptx')
    p.add_argument('--strict',   action='store_true', help='Exit 1 on any ERROR')
    p.add_argument('--warnings', action='store_true', help='Show warnings')
    p.add_argument('--render',   action='store_true', help='Pixel render check')
    args = p.parse_args()
    if not os.path.exists(args.pptx):
        print(f'File not found: {args.pptx}'); sys.exit(1)
    issues = validate_pptx(args.pptx, include_warnings=True, render=args.render)
    print_report(args.pptx, issues, show_warnings=args.warnings)
    sys.exit(1 if args.strict and any(i['severity'] == 'ERROR' for i in issues) else 0)
