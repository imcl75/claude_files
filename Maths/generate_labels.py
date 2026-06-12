"""
generate_labels.py  — WFA Mathematician label sheet generator.

Produces one DOCX per lesson: 12 identical labels per sheet (2 col × 6 row Avery layout).
Uses the school's reference DOCX as an exact byte-level template — only the five text
strings are replaced. No XML re-serialisation, so fonts and formatting are preserved
exactly as the Flask label tool produces them.

Usage:
    python3 generate_labels.py <lesson_num> [<lesson_num> ...]
    python3 generate_labels.py 9 10 11 12   →  T6W3_L9_Mon_Labels.docx  × 4

Reads content from /home/claude/labels_data.json (written by build_lp_v3.js).
Template file: /home/claude/WFA_Labels_template.docx  (backed up to repo)
"""

import json, os, sys, zipfile

# ─── Paths ────────────────────────────────────────────────────────────────────
TEMPLATE  = "/home/claude/WFA_Labels_template.docx"
if not os.path.exists(TEMPLATE):
    TEMPLATE = "/home/claude/WFA_Labels_mathematician_15-06-2026.docx"
DATA_PATH = "/home/claude/labels_data.json"

# ─── Template placeholder strings (exact text in the reference DOCX) ─────────
T_DATE  = "15/06/2026"
T_TOPIC = "Calculation"
T_LF    = "LF: To identify which operation is required to solve a problem."
T_IC1   = "I can identify the operation and clauclate using a suitable method"
T_IC2   = "I can solve problems involving the four operations"

# ─── Load label data ──────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"labels_data.json not found at {DATA_PATH}")
with open(DATA_PATH) as f:
    all_labels = json.load(f)

if len(sys.argv) > 1:
    wanted = {int(x) for x in sys.argv[1:]}
    labels = [l for l in all_labels if l["lesson"] in wanted]
else:
    labels = all_labels

if not labels:
    print("No matching label data.")
    sys.exit(1)

# ─── Read template into memory once ──────────────────────────────────────────
with zipfile.ZipFile(TEMPLATE, "r") as z:
    template_files = {name: z.read(name) for name in z.namelist()}

template_xml = template_files["word/document.xml"].decode("utf-8")

# ─── Generate one sheet per lesson ───────────────────────────────────────────
for label in labels:
    week    = label["week"]
    day     = label["day"][:3]
    lesson  = label["lesson"]
    out_path = f"/home/claude/{week}_L{lesson}_{day}_Labels.docx"

    # Replace all 12 occurrences of each placeholder with this lesson's content
    xml = template_xml
    xml = xml.replace(T_DATE,  label["date"])
    xml = xml.replace(T_TOPIC, label["topic"])
    xml = xml.replace(T_LF,    label["lf"])
    xml = xml.replace(T_IC1,   label["ican1"])
    xml = xml.replace(T_IC2,   label["ican2"])

    # Write new DOCX — identical to template except document.xml
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in template_files.items():
            if name == "word/document.xml":
                zout.writestr(name, xml.encode("utf-8"))
            else:
                zout.writestr(name, data)

    print(f"Saved: {out_path}  ({label['topic']})")
