#!/usr/bin/env python3
"""
validate_base_template.py — WFA base PPTX template structure validator.

Checks base template files (writing_lesson_base.pptx, template.pptx, etc.)
for structural problems that bake into every lesson built from them.
These are UPSTREAM errors that post-build validators cannot catch.

Checks:
  1. PLACEHOLDER-OVERFLOW  — text placeholder narrower than its visual container
  2. PLACEHOLDER-ORPHAN    — text placeholder has no matching visual container
  3. LAYOUT-DUPLICATE-IDX  — two placeholders with the same idx on one layout
  4. LAYOUT-MISSING-IDX    — a layout is missing an idx that the build script expects

Run this:
  - Once after any change to a base template file
  - As part of each skill's session-start environment restore
  - Before any build that uses that template

Usage:
    python3 validate_base_template.py <template.pptx>
    python3 validate_base_template.py writing_lesson_base.pptx --layout 5
    python3 validate_base_template.py --all   (checks all known WFA templates)

Exit 0 = clean. Exit 1 = errors found.
"""

import os, re, sys, zipfile
import xml.etree.ElementTree as ET

PML = 'http://schemas.openxmlformats.org/presentationml/2006/main'
DML = 'http://schemas.openxmlformats.org/drawingml/2006/main'

# Tolerance: a placeholder may be up to this many EMU narrower than its
# container before we flag it (allows for intentional inner padding).
WIDTH_TOLERANCE_EMU  = 182880   # 0.2 inches
HEIGHT_TOLERANCE_EMU = 274320   # 0.3 inches

# Known WFA templates and the build-script idx values they must provide
EXPECTED_LAYOUT_IDX = {
    # writing_lesson_base.pptx  Layout 5 (Learning Focus)
    'Learning Focus': ['10', '13', '14'],
    # More can be added as skills are audited
}

def emu_in(v): return round(int(v) / 914400, 3)


def _parse_shapes_from_xml(xml_str):
    """
    Return list of shape dicts from a layout or slide XML string.
    Each dict: name, x, y, w, h, ph_idx, geom
    """
    if isinstance(xml_str, bytes):
        xml_str = xml_str.decode()
    root   = ET.fromstring(xml_str)
    shapes = []

    for sp in root.iter(f'{{{PML}}}sp'):
        cnvpr = sp.find(f'.//{{{PML}}}cNvPr')
        name  = cnvpr.get('name', '?') if cnvpr is not None else '?'

        xfrm = sp.find(f'.//{{{DML}}}xfrm')
        if xfrm is None: continue
        off = xfrm.find(f'{{{DML}}}off')
        ext = xfrm.find(f'{{{DML}}}ext')
        if off is None or ext is None: continue

        x = int(off.get('x', 0)); y = int(off.get('y', 0))
        w = int(ext.get('cx', 0)); h = int(ext.get('cy', 0))
        if w == 0: continue

        ph    = sp.find(f'.//{{{PML}}}ph')
        ph_idx = ph.get('idx') if ph is not None else None

        geom  = sp.find(f'.//{{{DML}}}prstGeom')
        geom_name = geom.get('prst', '') if geom is not None else ''

        shapes.append({
            'name': name, 'x': x, 'y': y, 'w': w, 'h': h,
            'ph_idx': ph_idx, 'geom': geom_name,
            'is_ph': ph is not None,
            'right': x + w, 'bottom': y + h,
        })

    return shapes


def _find_container(placeholder, visual_shapes):
    """
    Find the visual container shape that best encloses the given placeholder.
    Returns the container shape dict, or None.
    A container must:
      - Be a visual (non-placeholder) shape with a geometry
      - Spatially contain the placeholder (with tolerance)
      - Have its centre within the placeholder's horizontal span
    """
    px, py, pw, ph = (placeholder['x'], placeholder['y'],
                      placeholder['w'], placeholder['h'])
    best = None
    best_area = float('inf')

    for vs in visual_shapes:
        if vs['is_ph']: continue
        if not vs['geom']: continue

        # Must horizontally overlap the placeholder significantly
        overlap_x = min(vs['right'], px + pw) - max(vs['x'], px)
        if overlap_x < pw * 0.5: continue  # less than 50% overlap

        # Container should be >= placeholder in both dimensions (with tolerance)
        if vs['w'] < pw - WIDTH_TOLERANCE_EMU:  continue
        if vs['h'] < ph - HEIGHT_TOLERANCE_EMU: continue

        # Prefer the smallest enclosing container
        area = vs['w'] * vs['h']
        if area < best_area:
            best      = vs
            best_area = area

    return best


def check_layout(layout_xml, layout_name, layout_num):
    """
    Check one slide layout for placeholder/container mismatches.
    Returns list of issue dicts.
    """
    issues  = []
    shapes  = _parse_shapes_from_xml(layout_xml)
    ph_list = [s for s in shapes if s['is_ph'] and s['ph_idx'] is not None]
    visuals = [s for s in shapes if not s['is_ph'] and s['geom']]

    # 1. Placeholder narrower than its container
    for ph in ph_list:
        container = _find_container(ph, visuals)
        if container is None:
            issues.append({
                'severity': 'WARNING',
                'type':     'PLACEHOLDER-ORPHAN',
                'detail':   (f"Layout {layout_num} ('{layout_name}') idx={ph['ph_idx']}: "
                             f"no visual container found for placeholder "
                             f"(x={emu_in(ph['x'])}\", w={emu_in(ph['w'])}\"). "
                             f"Placeholder position may be free-floating.")
            })
            continue

        width_gap  = container['w'] - ph['w']
        height_gap = container['h'] - ph['h']

        if width_gap > WIDTH_TOLERANCE_EMU + 91440:   # > 0.3" narrower than container
            issues.append({
                'severity': 'ERROR',
                'type':     'PLACEHOLDER-OVERFLOW',
                'detail':   (f"Layout {layout_num} ('{layout_name}') idx={ph['ph_idx']}: "
                             f"placeholder w={emu_in(ph['w']):.3f}\" but container "
                             f"'{container['name']}' w={emu_in(container['w']):.3f}\" "
                             f"({emu_in(width_gap):.3f}\" narrower). "
                             f"Long text will wrap early and overflow the box. "
                             f"Fix: widen placeholder to {emu_in(container['w']):.3f}\" "
                             f"(cx={container['w']} EMU).")
            })

    # 2. Duplicate idx values
    seen_idx = {}
    for ph in ph_list:
        idx = ph['ph_idx']
        if idx in seen_idx:
            issues.append({
                'severity': 'ERROR',
                'type':     'LAYOUT-DUPLICATE-IDX',
                'detail':   (f"Layout {layout_num} ('{layout_name}'): "
                             f"idx={idx} appears on both '{seen_idx[idx]}' and '{ph['name']}'. "
                             f"Only the last one will be used by build scripts.")
            })
        seen_idx[idx] = ph['name']

    # 3. Check expected idx values are present
    if layout_name in EXPECTED_LAYOUT_IDX:
        for req_idx in EXPECTED_LAYOUT_IDX[layout_name]:
            if req_idx not in seen_idx:
                issues.append({
                    'severity': 'ERROR',
                    'type':     'LAYOUT-MISSING-IDX',
                    'detail':   (f"Layout {layout_num} ('{layout_name}'): "
                                 f"expected placeholder idx={req_idx} (required by build scripts) "
                                 f"but it is not present. Build will fail or produce blank content.")
                })

    return issues


def _check_slides_off_canvas(z, canvas_w, canvas_h):
    """Check all slide files in zip for OFF-CANVAS shapes."""
    import re as _re
    PML2 = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    DML2 = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    issues = []
    slide_files = sorted(
        [n for n in z.namelist() if _re.match(r'ppt/slides/slide\d+\.xml$', n)],
        key=lambda n: int(_re.search(r'(\d+)', n).group(1)))
    for sf in slide_files:
        root = ET.fromstring(z.read(sf).decode())
        lbl  = os.path.basename(sf)
        for sp in root.iter(f'{{{PML2}}}sp'):
            xfrm = sp.find(f'.//{{{DML2}}}xfrm')
            if xfrm is None: continue
            off = xfrm.find(f'{{{DML2}}}off'); ext = xfrm.find(f'{{{DML2}}}ext')
            if off is None or ext is None: continue
            x  = int(off.get('x', 0)); cx = int(ext.get('cx', 0))
            y  = int(off.get('y', 0)); cy = int(ext.get('cy', 0))
            nm = sp.find(f'.//{{{PML2}}}cNvPr')
            name = nm.get('name','?') if nm is not None else '?'
            if x + cx > canvas_w + 36000:
                issues.append({'severity':'ERROR','type':'OFF-CANVAS-RIGHT',
                    'detail': f"[{lbl}] '{name}' right {round((x+cx)/360000,3)}cm > canvas {round(canvas_w/360000,3)}cm"})
            if y + cy > canvas_h + 36000:
                issues.append({'severity':'ERROR','type':'OFF-CANVAS-BOTTOM',
                    'detail': f"[{lbl}] '{name}' bottom {round((y+cy)/360000,3)}cm > canvas {round(canvas_h/360000,3)}cm"})
    return issues


def validate_template(pptx_path, layout_filter=None):
    """
    Validate all slide layouts in a template PPTX, plus slide OFF-CANVAS check.
    layout_filter: if set, only check that layout number (int).
    Returns list of issue dicts.
    """
    all_issues = []

    with zipfile.ZipFile(pptx_path, 'r') as z:
        names = z.namelist()
        # Check canvas size from presentation.xml
        if 'ppt/presentation.xml' in names:
            prs_xml = z.read('ppt/presentation.xml').decode()
            prs_root = ET.fromstring(prs_xml)
            PML3 = 'http://schemas.openxmlformats.org/presentationml/2006/main'
            sz = prs_root.find(f'{{{PML3}}}sldSz')
            canvas_w = int(sz.get('cx')) if sz is not None else 12192000
            canvas_h = int(sz.get('cy')) if sz is not None else 6858000
        else:
            canvas_w, canvas_h = 12192000, 6858000
        all_issues += _check_slides_off_canvas(z, canvas_w, canvas_h)
        layout_files = sorted(
            [n for n in names if re.match(r'ppt/slideLayouts/slideLayout\d+\.xml', n)],
            key=lambda n: int(re.search(r'(\d+)', n).group(1))
        )

        for lf in layout_files:
            num = int(re.search(r'(\d+)', lf).group(1))
            if layout_filter is not None and num != layout_filter:
                continue

            xml_str   = z.read(lf).decode()
            # Get layout name
            root      = ET.fromstring(xml_str)
            csld      = root.find(f'{{{PML}}}cSld')
            lay_name  = csld.get('name', f'Layout{num}') if csld is not None else f'Layout{num}'

            issues = check_layout(xml_str, lay_name, num)
            all_issues += issues

    return all_issues


def print_report(pptx_path, issues):
    errors   = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']

    print(f"\n{'='*65}")
    print(f"WFA Base Template Validator  —  {os.path.basename(pptx_path)}")
    print(f"{'='*65}")

    if not issues:
        print("✅  No structural issues found in template layouts.")
        return

    if errors:
        print(f"\n❌  ERRORS ({len(errors)}) — fix before building any lessons:\n")
        for e in errors:
            print(f"  {e['type']}: {e['detail']}\n")

    if warnings:
        print(f"\n⚠️   WARNINGS ({len(warnings)}):\n")
        for w in warnings:
            print(f"  {w['type']}: {w['detail']}\n")


# ---------------------------------------------------------------------------
# Known WFA templates to check under --all
# ---------------------------------------------------------------------------
KNOWN_TEMPLATES = [
    # Path relative to /tmp/claude_work/ (runtime) or skill assets
    '/tmp/claude_work/template.pptx',
    '/tmp/claude_work/assets/writing_lesson_base.pptx',
    '/mnt/skills/user/writing-lesson-pptx/assets/writing_lesson_base.pptx',
    '/mnt/skills/user/working-memory-starters/assets/Working_Memory_Template.pptx',
    '/mnt/skills/user/etiw-dictation/assets/easter_etiw.pptx',
]


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='WFA base PPTX template validator')
    p.add_argument('pptx', nargs='?', help='Path to template .pptx')
    p.add_argument('--layout', type=int, default=None, help='Only check this layout number')
    p.add_argument('--all',    action='store_true',   help='Check all known WFA templates')
    p.add_argument('--strict', action='store_true',   help='Exit 1 on any ERROR')
    args = p.parse_args()

    targets = []
    if args.all:
        targets = [t for t in KNOWN_TEMPLATES if os.path.exists(t)]
        if not targets:
            print("No known template files found.")
            sys.exit(1)
    elif args.pptx:
        targets = [args.pptx]
    else:
        p.print_help()
        sys.exit(1)

    all_errors = []
    for pptx in targets:
        if not os.path.exists(pptx):
            print(f"File not found: {pptx}")
            continue
        issues = validate_template(pptx, layout_filter=args.layout)
        print_report(pptx, issues)
        all_errors += [i for i in issues if i['severity'] == 'ERROR']

    sys.exit(1 if args.strict and all_errors else 0)
