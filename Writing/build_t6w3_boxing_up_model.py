"""
T6W3 Boxing-Up Plan — MODEL VERSION (teacher/class example).
Shows three completed skills: Open Mind, Slow-Time, Shadow-Walking.
Skill 4 left blank (optional). Notes style throughout, not full sentences.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Boxing_Up_Model.pdf'

PAGE_W, PAGE_H = A4
MARGIN   = 1.3 * cm
BLUE     = HexColor('#1798d3')
DBLUE    = HexColor('#154360')
LBLUE    = HexColor('#D6EAF8')
MID_BLUE = HexColor('#2980B9')
LGREY    = HexColor('#F7F7F7')
MGREY    = HexColor('#CCCCCC')
DGREY    = HexColor('#333333')
INK      = HexColor('#1a3a5c')   # "handwritten" note colour

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("T6W3 Boxing-Up Plan — Model Version")

# ── Header bar ──────────────────────────────────────────────────────
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MARGIN, PAGE_H - bar_h + 0.25 * cm,
             "Boxing-Up Plan  \u2014  Explanation Text  \u2014  MODEL")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.25 * cm,
                  "T6W3  |  Being a Writer  |  Year 4")

# ── Name line ───────────────────────────────────────────────────────
name_y = PAGE_H - bar_h - 0.6 * cm
c.setFillColor(DGREY)
c.setFont('Helvetica', 9)
c.drawString(MARGIN, name_y, "Name:")
c.setStrokeColor(MGREY)
c.setLineWidth(0.5)
c.line(MARGIN + 1.5 * cm, name_y - 0.05 * cm, MARGIN + 8 * cm, name_y - 0.05 * cm)
c.setFont('Helvetica-Oblique', 9)
c.setFillColor(INK)
c.drawString(MARGIN + 1.7 * cm, name_y, "Class model")
c.setFillColor(DGREY)
c.setFont('Helvetica', 9)
c.drawString(MARGIN + 9 * cm, name_y, "Class:")
c.line(MARGIN + 10.5 * cm, name_y - 0.05 * cm, PAGE_W - MARGIN, name_y - 0.05 * cm)

# ── Instruction note ────────────────────────────────────────────────
note_y = name_y - 0.55 * cm
c.setFont('Helvetica', 8.2)
c.setFillColor(HexColor('#555555'))
c.drawString(MARGIN, note_y,
             "Choose three or four skills from the Seven Skills. "
             "Complete a row for each one. Write notes, not full sentences.")

# ── Table setup ─────────────────────────────────────────────────────
tbl_top    = note_y - 0.35 * cm
tbl_bottom = 0.85 * cm
tbl_w      = PAGE_W - 2 * MARGIN
tbl_x      = MARGIN

col_props  = [0.14, 0.22, 0.32, 0.32]
col_labels = ["Subheading\n(skill name)", "What the skill is",
              "How it works", "What happens as a result"]
col_ws     = [tbl_w * p for p in col_props]
col_xs     = [tbl_x + sum(col_ws[:i]) for i in range(4)]

rows = [
    ("Introduction",      2.4, LBLUE),
    ("Skill 1",           3.0, LGREY),
    ("Skill 2",           3.0, white),
    ("Skill 3",           3.0, LGREY),
    ("Skill 4\n(optional)", 3.0, white),
    ("Conclusion",        2.4, LBLUE),
]

avail_h  = tbl_top - tbl_bottom
header_h = 0.7 * cm
data_h   = avail_h - header_h
raw_total = sum(r[1] for r in rows) * cm
scale    = data_h / raw_total
row_hs   = [r[1] * cm * scale for r in rows]

# ── Model content ───────────────────────────────────────────────────
# Each entry: list of (col_index, lines_of_notes)
# col 0 = label col (handled separately), cols 1-3 = data cols

def note_lines(text_list, cx, cy_top, cw, rh, size=7.4):
    """Draw a list of note strings in a column, top-justified with small gap."""
    c.setFillColor(INK)
    c.setFont('Helvetica-Oblique', size)
    line_h = size * 1.45
    pad    = 0.18 * cm
    y      = cy_top - pad - size * 0.72
    for ln in text_list:
        if y < cy_top - rh + 0.08 * cm:
            break
        c.drawString(cx + 0.18 * cm, y, ln)
        y -= line_h

# Introduction row content (cols 1-3 merged)
intro_content = {
    'q':  "Have you ever imagined stepping into the city for the first time?",
    'fr': "The city is full of dangers a house cat has never faced.",
    'pur':"The Way of Jalal teaches skills that can help any cat survive.",
}

# Skill rows: (row_label, col1_notes, col2_notes, col3_notes)
skill_data = [
    ("Open Mind",
     ["ready to change plan", "new place = unexpected", "think differently"],
     ["if one plan fails, try another", "look at problem from", "different angles"],
     ["find solutions", "avoid danger", "stay adaptable"]),
    ("Slow-Time",
     ["calm the mind", "focus completely", "danger moves fast"],
     ["slow breathing", "everything seems", "to move more slowly"],
     ["more time to dodge", "better decisions", "space to react"]),
    ("Shadow-Walking",
     ["avoid being seen", "sometimes fighting", "is not the answer"],
     ["stay silent", "move through dark", "places unnoticed"],
     ["escape trouble", "no one knows", "you were there"]),
    None,  # Skill 4 blank
]

# Conclusion content (cols 1-3 merged)
conclusion_content = [
    "Use all skills together to stay safe in the city.",
    "The skills work best when combined.",
    "Any cat can survive the Outside with the Way of Jalal.",
]

# ── Draw column header row ───────────────────────────────────────────
cy = tbl_top
c.setFillColor(BLUE)
c.rect(tbl_x, cy - header_h, tbl_w, header_h, fill=1, stroke=0)
for i, (lbl, cx) in enumerate(zip(col_labels, col_xs)):
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7.5)
    parts = lbl.split('\n')
    if len(parts) == 2:
        c.drawCentredString(cx + col_ws[i] / 2, cy - header_h * 0.35, parts[0])
        c.setFont('Helvetica', 6.5)
        c.drawCentredString(cx + col_ws[i] / 2, cy - header_h * 0.72, parts[1])
    else:
        c.drawCentredString(cx + col_ws[i] / 2, cy - header_h * 0.52, lbl)
cy -= header_h

# ── Draw data rows ───────────────────────────────────────────────────
skill_idx = 0

for row_i, ((row_lbl, _, fill), rh) in enumerate(zip(rows, row_hs)):
    row_bottom = cy - rh

    # Background
    c.setFillColor(fill)
    c.rect(tbl_x, row_bottom, tbl_w, rh, fill=1, stroke=0)

    # Label column (blue band)
    c.setFillColor(MID_BLUE)
    c.rect(col_xs[0], row_bottom, col_ws[0], rh, fill=1, stroke=0)
    c.setFillColor(white)
    # For skill rows with model data, show skill name; otherwise use row label
    sd_peek = skill_data[skill_idx] if row_lbl.startswith('Skill') and skill_idx < len(skill_data) else None
    skill_name = sd_peek[0] if sd_peek else None
    if skill_name:
        parts = row_lbl.split('\n')
        c.setFont('Helvetica', 6.5)
        c.drawCentredString(col_xs[0] + col_ws[0] / 2, cy - rh * 0.30, parts[0])
        sz = 8 if stringWidth(skill_name, 'Helvetica-Bold', 8) < col_ws[0] - 0.12*cm else 6.5
        c.setFont('Helvetica-Bold', sz)
        c.drawCentredString(col_xs[0] + col_ws[0] / 2, cy - rh * 0.54, skill_name)
    else:
        c.setFont('Helvetica-Bold', 8)
        parts = row_lbl.split('\n')
        for k, part in enumerate(parts):
            if len(parts) == 2:
                label_y = cy - rh / 2 + (0.18 - k * 0.36) * cm
            else:
                label_y = cy - rh / 2 - 0.12 * cm
            c.drawCentredString(col_xs[0] + col_ws[0] / 2, label_y, part)

    # Introduction row
    if row_lbl == "Introduction":
        merged_x = col_xs[1]
        merged_w = sum(col_ws[1:])
        c.setFillColor(fill)
        c.rect(merged_x, row_bottom, merged_w, rh, fill=1, stroke=0)
        # grey prompt labels
        c.setFillColor(HexColor('#888888'))
        c.setFont('Helvetica', 7.5)
        c.drawString(merged_x + 0.2 * cm, cy - 0.42 * cm,
                     "Rhetorical question:                                       Framing sentence:")
        # model notes
        c.setFillColor(INK)
        c.setFont('Helvetica-Oblique', 7.4)
        c.drawString(merged_x + 0.2 * cm, cy - 0.80 * cm, intro_content['q'])
        c.drawString(merged_x + 0.2 * cm, cy - 1.12 * cm, intro_content['fr'])
        c.drawString(merged_x + 0.2 * cm, cy - 1.44 * cm, intro_content['pur'])

    # Conclusion row
    elif row_lbl == "Conclusion":
        merged_x = col_xs[1]
        merged_w = sum(col_ws[1:])
        c.setFillColor(fill)
        c.rect(merged_x, row_bottom, merged_w, rh, fill=1, stroke=0)
        c.setFillColor(HexColor('#888888'))
        c.setFont('Helvetica', 7.5)
        c.drawString(merged_x + 0.2 * cm, cy - 0.42 * cm,
                     "Link the skills together:                                  Final message to the reader:")
        c.setFillColor(INK)
        c.setFont('Helvetica-Oblique', 7.4)
        line_h = 7.4 * 1.45
        for li, ln in enumerate(conclusion_content):
            c.drawString(merged_x + 0.2 * cm, cy - 0.80 * cm - li * line_h, ln)

    # Skill rows
    else:
        sd = skill_data[skill_idx] if skill_idx < len(skill_data) else None
        skill_idx += 1

        if sd is None:
            # Blank skill 4 — just ruled lines
            c.setStrokeColor(MGREY)
            c.setLineWidth(0.3)
            line_gap = 0.44 * cm
            for ci in range(1, 4):
                n_lines = int((rh - 0.28 * cm) / line_gap)
                for li in range(n_lines):
                    ly = cy - 0.38 * cm - li * line_gap
                    if ly > row_bottom + 0.05 * cm:
                        c.line(col_xs[ci] + 0.15 * cm, ly,
                               col_xs[ci] + col_ws[ci] - 0.15 * cm, ly)
        else:
            sk_name, col1, col2, col3 = sd
            for ci, notes in enumerate([col1, col2, col3], start=1):
                note_lines(notes, col_xs[ci], cy, col_ws[ci], rh)

    # Grid lines
    c.setStrokeColor(MGREY)
    c.setLineWidth(0.5)
    c.line(tbl_x, cy, tbl_x + tbl_w, cy)
    for ci in range(1, 4):
        c.line(col_xs[ci], row_bottom, col_xs[ci], cy)

    cy = row_bottom

# Bottom border and outer box
c.setStrokeColor(MGREY)
c.setLineWidth(0.5)
c.line(tbl_x, cy, tbl_x + tbl_w, cy)
c.rect(tbl_x, cy, tbl_w, tbl_top - cy, fill=0, stroke=1)

# ── Footer ───────────────────────────────────────────────────────────
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, 0.42 * cm, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W / 2, 0.13 * cm,
                    "Wallscourt Farm Academy  |  Year 4  |  Term 6")

c.save()
print(f"Saved: {OUT}")
