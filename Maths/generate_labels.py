"""
generate_labels.py  — WFA Mathematician label sheet generator.

Uses the school's reference DOCX as an exact template. Replaces text content
only — all formatting, fonts, table structure, page margins and embedded images
are taken directly from the template so the output is pixel-for-pixel consistent
with the Flask label tool.

Usage:
    python3 generate_labels.py [lesson_num ...]
    python3 generate_labels.py 9 10 11 12   → T6W3_Labels.docx

Reads label content from /home/claude/labels_data.json (written by build_lp_v3.js).
Each lesson fills one full row (both columns identical). Up to 6 lessons per sheet.
Rows with no lesson data are cleared to blank.
"""

import json, os, sys, shutil, zipfile
import xml.etree.ElementTree as ET

# ─── Paths ────────────────────────────────────────────────────────────────────
TEMPLATE  = "/home/claude/WFA_Labels_mathematician_15-06-2026.docx"
DATA_PATH = "/home/claude/labels_data.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Register all namespaces found in the document so ET preserves them
NSMAP = {
    "wpc":    "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "mc":     "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o":      "urn:schemas-microsoft-com:office:office",
    "r":      "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m":      "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v":      "urn:schemas-microsoft-com:vml",
    "wp14":   "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp":     "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10":    "urn:schemas-microsoft-com:office:word",
    "w":      "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14":    "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15":    "http://schemas.microsoft.com/office/word/2012/wordml",
    "wpg":    "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi":    "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne":    "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps":    "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "a":      "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic":    "http://schemas.openxmlformats.org/drawingml/2006/picture",
}
for prefix, uri in NSMAP.items():
    ET.register_namespace(prefix, uri)

# ─── Load label data ──────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"labels_data.json not found at {DATA_PATH}")
with open(DATA_PATH) as f:
    all_labels = json.load(f)

# Filter to requested lessons
if len(sys.argv) > 1:
    wanted = {int(x) for x in sys.argv[1:]}
    labels = [l for l in all_labels if l["lesson"] in wanted]
else:
    labels = all_labels

if not labels:
    print("No matching label data.")
    sys.exit(1)

week     = labels[0].get("week", "T6W3")
out_path = f"/home/claude/{week}_Labels.docx"

# ─── Unpack template into memory ──────────────────────────────────────────────
tmp_dir = "/home/claude/_labels_tmp"
if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)
os.makedirs(tmp_dir)
with zipfile.ZipFile(TEMPLATE, "r") as z:
    z.extractall(tmp_dir)

# ─── Parse and modify document.xml ───────────────────────────────────────────
doc_path = os.path.join(tmp_dir, "word", "document.xml")
tree = ET.parse(doc_path)
root = tree.getroot()

body      = root.find(f"{{{W}}}body")
outer_tbl = body.find(f"{{{W}}}tbl")
rows      = outer_tbl.findall(f"{{{W}}}tr")  # 6 rows

def set_label_content(outer_cell, label):
    """Replace the 5 text nodes in the label's content column."""
    nested_tbl  = outer_cell.find(f"{{{W}}}tbl")
    nested_row  = nested_tbl.find(f"{{{W}}}tr")
    ncells      = nested_row.findall(f"{{{W}}}tc")
    left_cell   = ncells[0]  # content column
    right_cell  = ncells[1]  # icon + name column
    t_nodes     = left_cell.findall(f".//{{{W}}}t")

    if label is None:
        # Clear text and remove the icon drawing from the right column
        for t in t_nodes:
            t.text = ""
        # Remove drawing elements from right cell so blank rows show nothing
        for p in right_cell.findall(f"{{{W}}}p"):
            for r in p.findall(f"{{{W}}}r"):
                drawing = r.find(f"{{{W}}}drawing")
                if drawing is not None:
                    p.remove(r)
        # Clear "mathematician" text node too
        for t in right_cell.findall(f".//{{{W}}}t"):
            t.text = ""
    else:
        values = [
            label["date"],
            label["topic"],
            label["lf"],
            label["ican1"],
            label["ican2"],
        ]
        for i, t in enumerate(t_nodes):
            t.text = values[i] if i < len(values) else ""

# Apply label data to each row. Column 0 = left label, column 2 = right label.
# (Column 1 is the gap spacer — skip it.)
for row_idx, row in enumerate(rows):
    outer_cells = row.findall(f"{{{W}}}tc")
    label_data  = labels[row_idx] if row_idx < len(labels) else None
    set_label_content(outer_cells[0], label_data)  # left label
    set_label_content(outer_cells[2], label_data)  # right label (identical)

# ─── Write modified document.xml ─────────────────────────────────────────────
ET.indent(tree, space="  ")
tree.write(doc_path, encoding="UTF-8", xml_declaration=True)

# ─── Repack into DOCX ─────────────────────────────────────────────────────────
if os.path.exists(out_path):
    os.remove(out_path)
with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
    for dirpath, dirnames, filenames in os.walk(tmp_dir):
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            arcname = os.path.relpath(full, tmp_dir)
            zout.write(full, arcname)

shutil.rmtree(tmp_dir)
print(f"Labels saved: {out_path}  ({len(labels)} lesson{'s' if len(labels)!=1 else ''}, "
      f"{6 - len(labels)} blank row{'s' if 6-len(labels)!=1 else ''})")
