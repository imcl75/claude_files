#!/usr/bin/env python3
"""
validate_base_template.py — WFA base PPTX template structure validator.

Checks base template files for structural problems that bake into every lesson.
Run once after any template change and at session-start environment restore.

Checks:
  1. PLACEHOLDER-OVERFLOW  — text placeholder narrower than its visual container
  2. PLACEHOLDER-ORPHAN    — text placeholder has no matching visual container
  3. LAYOUT-DUPLICATE-IDX  — two placeholders with the same idx on one layout
  4. LAYOUT-MISSING-IDX    — layout missing an idx required by build scripts

Usage:
    python3 validate_base_template.py <template.pptx>
    python3 validate_base_template.py writing_lesson_base.pptx --layout 5
    python3 validate_base_template.py --all
"""

import os, re, sys, zipfile
import xml.etree.ElementTree as ET

PML = "http://schemas.openxmlformats.org/presentationml/2006/main"
DML = "http://schemas.openxmlformats.org/drawingml/2006/main"

WIDTH_TOLERANCE_EMU  = 182880
HEIGHT_TOLERANCE_EMU = 274320

EXPECTED_LAYOUT_IDX = {
    "Learning Focus": ["10", "13", "14"],
}

def emu_in(v): return round(int(v) / 914400, 3)


def _parse_shapes_from_xml(xml_str):
    if isinstance(xml_str, bytes): xml_str = xml_str.decode()
    root = ET.fromstring(xml_str); shapes = []
    for sp in root.iter(f"{{{PML}}}sp"):
        cnvpr    = sp.find(f".//{{{PML}}}cNvPr")
        name     = cnvpr.get("name", "?") if cnvpr is not None else "?"
        xfrm     = sp.find(f".//{{{DML}}}xfrm")
        if xfrm is None: continue
        off = xfrm.find(f"{{{DML}}}off"); ext = xfrm.find(f"{{{DML}}}ext")
        if off is None or ext is None: continue
        x = int(off.get("x", 0)); y = int(off.get("y", 0))
        w = int(ext.get("cx", 0)); h = int(ext.get("cy", 0))
        if w == 0: continue
        ph       = sp.find(f".//{{{PML}}}ph")
        ph_idx   = ph.get("idx") if ph is not None else None
        geom     = sp.find(f".//{{{DML}}}prstGeom")
        geom_name = geom.get("prst", "") if geom is not None else ""
        shapes.append({"name": name, "x": x, "y": y, "w": w, "h": h,
                        "ph_idx": ph_idx, "geom": geom_name,
                        "is_ph": ph is not None,
                        "right": x + w, "bottom": y + h})
    return shapes


def _find_container(placeholder, visual_shapes):
    px, py, pw, ph = placeholder["x"], placeholder["y"], placeholder["w"], placeholder["h"]
    best = None; best_area = float("inf")
    for vs in visual_shapes:
        if vs["is_ph"] or not vs["geom"]: continue
        overlap_x = min(vs["right"], px + pw) - max(vs["x"], px)
        if overlap_x < pw * 0.5: continue
        if vs["w"] < pw - WIDTH_TOLERANCE_EMU: continue
        if vs["h"] < ph - HEIGHT_TOLERANCE_EMU: continue
        area = vs["w"] * vs["h"]
        if area < best_area: best = vs; best_area = area
    return best


def check_layout(layout_xml, layout_name, layout_num):
    issues  = []
    shapes  = _parse_shapes_from_xml(layout_xml)
    ph_list = [s for s in shapes if s["is_ph"] and s["ph_idx"] is not None]
    visuals = [s for s in shapes if not s["is_ph"] and s["geom"]]
    for ph in ph_list:
        container = _find_container(ph, visuals)
        if container is None:
            issues.append({"severity": "WARNING", "type": "PLACEHOLDER-ORPHAN",
                "detail": (f"Layout {layout_num} ('{layout_name}') idx={ph['ph_idx']}: "
                           f"no visual container found.")})
            continue
        width_gap = container["w"] - ph["w"]
        if width_gap > WIDTH_TOLERANCE_EMU + 91440:
            issues.append({"severity": "ERROR", "type": "PLACEHOLDER-OVERFLOW",
                "detail": (f"Layout {layout_num} ('{layout_name}') idx={ph['ph_idx']}: "
                           f"placeholder w={emu_in(ph['w']):.3f}\" but container "
                           f"'{container['name']}' w={emu_in(container['w']):.3f}\" "
                           f"({emu_in(width_gap):.3f}\" narrower). "
                           f"Fix: set cx={container['w']} EMU.")})
    seen_idx = {}
    for ph in ph_list:
        idx = ph["ph_idx"]
        if idx in seen_idx:
            issues.append({"severity": "ERROR", "type": "LAYOUT-DUPLICATE-IDX",
                "detail": f"Layout {layout_num} ('{layout_name}'): idx={idx} appears twice."})
        seen_idx[idx] = ph["name"]
    if layout_name in EXPECTED_LAYOUT_IDX:
        for req_idx in EXPECTED_LAYOUT_IDX[layout_name]:
            if req_idx not in seen_idx:
                issues.append({"severity": "ERROR", "type": "LAYOUT-MISSING-IDX",
                    "detail": (f"Layout {layout_num} ('{layout_name}'): "
                               f"expected placeholder idx={req_idx} not present.")})
    return issues


def validate_template(pptx_path, layout_filter=None):
    all_issues = []
    with zipfile.ZipFile(pptx_path, "r") as z:
        names = z.namelist()
        layout_files = sorted(
            [n for n in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml", n)],
            key=lambda n: int(re.search(r"(\d+)", n).group(1))
        )
        for lf in layout_files:
            num = int(re.search(r"(\d+)", lf).group(1))
            if layout_filter is not None and num != layout_filter: continue
            xml_str  = z.read(lf).decode()
            root     = ET.fromstring(xml_str)
            csld     = root.find(f"{{{PML}}}cSld")
            lay_name = csld.get("name", f"Layout{num}") if csld is not None else f"Layout{num}"
            all_issues += check_layout(xml_str, lay_name, num)
    return all_issues


def print_report(pptx_path, issues):
    errors   = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]
    print(f"\n{'='*65}")
    print(f"WFA Base Template Validator  —  {os.path.basename(pptx_path)}")
    print(f"{'='*65}")
    if not issues: print("✅  No structural issues found."); return
    if errors:
        print(f"\n❌  ERRORS ({len(errors)}) — fix before building:\n")
        for e in errors: print(f"  {e['type']}: {e['detail']}\n")
    if warnings:
        print(f"\n⚠️   WARNINGS ({len(warnings)}):\n")
        for w in warnings: print(f"  {w['type']}: {w['detail']}\n")


KNOWN_TEMPLATES = [
    "/tmp/claude_work/template.pptx",
    "/mnt/skills/user/writing-lesson-pptx/assets/writing_lesson_base.pptx",
    "/mnt/skills/user/working-memory-starters/assets/Working_Memory_Template.pptx",
    "/mnt/skills/user/etiw-dictation/assets/easter_etiw.pptx",
]


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="WFA base PPTX template validator")
    p.add_argument("pptx", nargs="?")
    p.add_argument("--layout", type=int, default=None)
    p.add_argument("--all",    action="store_true")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()
    targets = ([t for t in KNOWN_TEMPLATES if os.path.exists(t)] if args.all
               else [args.pptx] if args.pptx else [])
    if not targets: p.print_help(); sys.exit(1)
    all_errors = []
    for pptx in targets:
        if not os.path.exists(pptx): print(f"Not found: {pptx}"); continue
        issues = validate_template(pptx, layout_filter=args.layout)
        print_report(pptx, issues)
        all_errors += [i for i in issues if i["severity"] == "ERROR"]
    sys.exit(1 if args.strict and all_errors else 0)
