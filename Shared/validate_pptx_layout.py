#!/usr/bin/env python3
"""
validate_pptx_layout.py — Universal PPTX layout validator for WFA skills.

Checks every slide in a PPTX for three categories of error:
  1. OFF-CANVAS   — any shape extending beyond the slide boundary
  2. TEXT-SPILL   — text box too short to hold its content (no autofit set)
  3. COLLISION    — two sibling-level shapes overlapping (not intentional layering)

Usage as a script:
    python3 validate_pptx_layout.py file.pptx
    python3 validate_pptx_layout.py file.pptx --strict    # exit 1 on any issue
    python3 validate_pptx_layout.py file.pptx --warnings  # show warnings too

Usage as a module:
    from validate_pptx_layout import validate_pptx
    issues = validate_pptx('output.pptx')
    errors = [i for i in issues if i['severity'] == 'ERROR']
    if errors:
        raise RuntimeError(f"Layout errors: {errors}")
"""

import math
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

# XML namespaces
PML = 'http://schemas.openxmlformats.org/presentationml/2006/main'
DML = 'http://schemas.openxmlformats.org/drawingml/2006/main'

# Tolerances
OVERLAP_TOLERANCE_EMU   = 36000   # 0.1cm — ignore sub-pixel overlaps
SPILL_TOLERANCE_RATIO   = 0.20    # allow 20% over before flagging
LAYERING_THRESHOLD      = 0.88    # if overlap ≥ 88% of smaller shape, treat as intentional layering

# Char-width factor for height estimation (Aptos/Calibri, typical)
CHAR_WIDTH_FACTOR = 0.55   # avg char width = font_pt × 0.55 (in points)
LINE_SPACING      = 1.20   # line height = font_pt × 1.20


def _emu_cm(v):
    return round(v / 360000, 3)


def _get_canvas(prs_xml):
    """Return (width_emu, height_emu) from presentation.xml text."""
    root = ET.fromstring(prs_xml)
    sz = root.find(f'{{{PML}}}sldSz')
    if sz is None:
        # fallback: widescreen 16:9
        return 12192000, 6858000
    return int(sz.get('cx')), int(sz.get('cy'))


def _parse_shapes(slide_xml):
    """
    Parse all shapes from a slide XML string.
    Returns list of dicts with geometry, text content, and autofit status.
    Handles both <p:sp> and shapes inside <p:grpSp> groups (flattened).
    """
    root = ET.fromstring(slide_xml)
    shapes = []

    for sp in root.iter(f'{{{PML}}}sp'):
        # Name
        cnvpr = sp.find(f'.//{{{PML}}}cNvPr')
        name = cnvpr.get('name', '?') if cnvpr is not None else '?'

        # Geometry
        xfrm = sp.find(f'.//{{{DML}}}xfrm')
        if xfrm is None:
            continue
        off = xfrm.find(f'{{{DML}}}off')
        ext = xfrm.find(f'{{{DML}}}ext')
        if off is None or ext is None:
            continue

        x = int(off.get('x', 0))
        y = int(off.get('y', 0))
        w = int(ext.get('cx', 0))
        h = int(ext.get('cy', 0))

        if w == 0:
            continue  # invisible / zero-width

        # Body properties
        bodyPr = sp.find(f'.//{{{DML}}}bodyPr')
        autofit = 'none'
        lIns = rIns = 91440   # default 0.254cm
        tIns = bIns = 45720   # default 0.127cm

        if bodyPr is not None:
            if bodyPr.find(f'{{{DML}}}normAutofit') is not None:
                autofit = 'normAutofit'
            elif bodyPr.find(f'{{{DML}}}spAutoFit') is not None:
                autofit = 'spAutoFit'
            lIns = int(bodyPr.get('lIns', lIns))
            rIns = int(bodyPr.get('rIns', rIns))
            tIns = int(bodyPr.get('tIns', tIns))
            bIns = int(bodyPr.get('bIns', bIns))

        # Text paragraphs
        paras = []
        for p in sp.findall(f'.//{{{DML}}}p'):
            text = ''.join(t.text or '' for t in p.iter(f'{{{DML}}}t'))
            paras.append(text)

        # Font sizes (hundredths of a point → points)
        sizes = [int(r.get('sz')) / 100
                 for r in sp.iter(f'{{{DML}}}rPr')
                 if r.get('sz')]
        font_pt = min(sizes) if sizes else 11.0

        shapes.append({
            'name': name,
            'x': x, 'y': y, 'w': w, 'h': h,
            'autofit': autofit,
            'lIns': lIns, 'rIns': rIns,
            'tIns': tIns, 'bIns': bIns,
            'paras': paras,
            'font_pt': font_pt,
            'has_text': any(p.strip() for p in paras),
        })

    return shapes


def _check_off_canvas(shapes, canvas_w, canvas_h):
    issues = []
    for s in shapes:
        right = s['x'] + s['w']
        bottom = s['y'] + s['h']
        if right > canvas_w + OVERLAP_TOLERANCE_EMU:
            issues.append({
                'severity': 'ERROR',
                'type': 'OFF-CANVAS-RIGHT',
                'detail': (f"Shape '{s['name']}' right edge {_emu_cm(right)}cm "
                           f"exceeds canvas {_emu_cm(canvas_w)}cm "
                           f"(overflow {_emu_cm(right - canvas_w)}cm)")
            })
        if bottom > canvas_h + OVERLAP_TOLERANCE_EMU:
            issues.append({
                'severity': 'ERROR',
                'type': 'OFF-CANVAS-BOTTOM',
                'detail': (f"Shape '{s['name']}' bottom {_emu_cm(bottom)}cm "
                           f"exceeds canvas {_emu_cm(canvas_h)}cm "
                           f"(overflow {_emu_cm(bottom - canvas_h)}cm)")
            })
    return issues


def _estimate_lines(paras, font_pt, usable_w_emu):
    """Estimate total lines of text needed for the given paragraphs."""
    if usable_w_emu <= 0:
        return len(paras)
    # Convert usable width to points (1 EMU = 1/914400 inch = 1/72 pt / 914400 * 72)
    usable_w_pt = usable_w_emu / 12700
    char_w_pt = font_pt * CHAR_WIDTH_FACTOR
    chars_per_line = max(1, usable_w_pt / char_w_pt)
    total = 0
    for para in paras:
        total += max(1, math.ceil(len(para) / chars_per_line))
    return total


def _check_text_spill(shapes):
    issues = []
    for s in shapes:
        # Only check shapes with text that have no autofit
        if not s['has_text']:
            continue
        if s['autofit'] != 'none':
            continue
        if s['h'] == 0:
            continue

        usable_w = s['w'] - s['lIns'] - s['rIns']
        usable_h = s['h'] - s['tIns'] - s['bIns']
        if usable_h <= 0:
            continue

        total_lines = _estimate_lines(s['paras'], s['font_pt'], usable_w)
        line_h_emu = s['font_pt'] * LINE_SPACING * 12700
        required_h = total_lines * line_h_emu

        overflow_ratio = (required_h - usable_h) / usable_h

        if overflow_ratio > SPILL_TOLERANCE_RATIO:
            severity = 'ERROR' if overflow_ratio > 0.5 else 'WARNING'
            text_preview = ''.join(s['paras'])[:50]
            issues.append({
                'severity': severity,
                'type': 'TEXT-SPILL',
                'detail': (f"Shape '{s['name']}' box {_emu_cm(s['h'])}cm tall, "
                           f"needs ~{_emu_cm(int(required_h + s['tIns'] + s['bIns']))}cm "
                           f"for {total_lines} line(s) at {s['font_pt']:.0f}pt "
                           f"[{text_preview!r}]")
            })
    return issues


def _check_collisions(shapes):
    issues = []
    # Only consider shapes with non-zero height for collision purposes
    candidates = [s for s in shapes if s['h'] > 0]

    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            # Bounding box overlap
            ox = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
            oy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])

            if ox <= OVERLAP_TOLERANCE_EMU or oy <= OVERLAP_TOLERANCE_EMU:
                continue  # no meaningful overlap

            overlap_area = ox * oy
            a_area = a['w'] * a['h']
            b_area = b['w'] * b['h']
            smaller_area = min(a_area, b_area)

            if smaller_area == 0:
                continue

            containment = overlap_area / smaller_area

            if containment >= LAYERING_THRESHOLD:
                # One shape is mostly inside the other — intentional layering, skip
                continue

            # Partial sibling collision
            # Classify severity: large overlap = ERROR, small = WARNING
            severity = 'ERROR' if (ox > 360000 and oy > 180000) else 'WARNING'

            issues.append({
                'severity': severity,
                'type': 'COLLISION',
                'detail': (f"'{a['name']}' (y={_emu_cm(a['y'])}-{_emu_cm(a['y']+a['h'])}cm) "
                           f"and '{b['name']}' (y={_emu_cm(b['y'])}-{_emu_cm(b['y']+b['h'])}cm) "
                           f"overlap {_emu_cm(ox)}cm × {_emu_cm(oy)}cm")
            })

    return issues


def validate_slide(slide_xml, canvas_w, canvas_h, slide_label='slide'):
    """
    Validate a single slide.
    Returns list of issue dicts: {severity, type, detail, slide}.
    """
    shapes = _parse_shapes(slide_xml)
    issues = []
    issues += _check_off_canvas(shapes, canvas_w, canvas_h)
    issues += _check_text_spill(shapes)
    issues += _check_collisions(shapes)
    for issue in issues:
        issue['slide'] = slide_label
    return issues


def validate_pptx(pptx_path, include_warnings=True):
    """
    Validate all slides in a PPTX file.
    Returns list of issue dicts sorted by slide then severity.
    """
    all_issues = []

    with zipfile.ZipFile(pptx_path, 'r') as z:
        names = z.namelist()

        # Read canvas dimensions
        prs_xml = z.read('ppt/presentation.xml')
        canvas_w, canvas_h = _get_canvas(prs_xml)

        # Find all slide XML files (not layouts or masters)
        slide_files = sorted(
            [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)],
            key=lambda n: int(re.search(r'(\d+)', n).group(1))
        )

        for slide_path in slide_files:
            slide_num = re.search(r'(\d+)', slide_path).group(1)
            slide_xml = z.read(slide_path).decode('utf-8')
            issues = validate_slide(slide_xml, canvas_w, canvas_h,
                                    slide_label=f'slide {slide_num}')
            all_issues += issues

    if not include_warnings:
        all_issues = [i for i in all_issues if i['severity'] == 'ERROR']

    return all_issues


def print_report(pptx_path, issues, show_warnings=True):
    errors   = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']

    print(f"\n{'='*60}")
    print(f"Layout validation: {os.path.basename(pptx_path)}")
    print(f"{'='*60}")

    if not issues:
        print("✅  No layout issues found.")
        return

    if errors:
        print(f"\n❌  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  [{e['slide']}] {e['type']}: {e['detail']}")

    if show_warnings and warnings:
        print(f"\n⚠️   WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  [{w['slide']}] {w['type']}: {w['detail']}")

    print()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate PPTX layout')
    parser.add_argument('pptx', help='Path to .pptx file')
    parser.add_argument('--strict',   action='store_true',
                        help='Exit code 1 if any errors found')
    parser.add_argument('--warnings', action='store_true',
                        help='Show warnings as well as errors')
    args = parser.parse_args()

    if not os.path.exists(args.pptx):
        print(f"File not found: {args.pptx}")
        sys.exit(1)

    issues = validate_pptx(args.pptx, include_warnings=True)
    print_report(args.pptx, issues, show_warnings=args.warnings)

    errors = [i for i in issues if i['severity'] == 'ERROR']
    if args.strict and errors:
        sys.exit(1)
    sys.exit(0)
