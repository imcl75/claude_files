"""
T6W3 Boxing-Up Planning Frame — A4 portrait.
Introduction / Skill 1-4 / Conclusion rows with 4 columns each.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black

OUT = '/home/claude/T6W3_Boxing_Up.pdf'

PAGE_W, PAGE_H = A4
MARGIN   = 1.3 * cm
BLUE     = HexColor('#1798d3')
DBLUE    = HexColor('#154360')
LBLUE    = HexColor('#D6EAF8')
MID_BLUE = HexColor('#2980B9')
LGREY    = HexColor('#F7F7F7')
MGREY    = HexColor('#CCCCCC')
DGREY    = HexColor('#333333')

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("T6W3 Boxing-Up Plan — Explanation Text")

# ── Header bar ──────────────────────────────────────────────────────
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MARGIN, PAGE_H - bar_h + 0.25 * cm, "Boxing-Up Plan  \u2014  Explanation Text")
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

# Column widths (proportional)
col_props  = [0.14, 0.22, 0.32, 0.32]
col_labels = ["Subheading\n(skill name)", "What the skill is",
              "How it works", "What happens as a result"]
col_ws     = [tbl_w * p for p in col_props]
col_xs     = [tbl_x + sum(col_ws[:i]) for i in range(4)]

# Row definitions: (label, height_cm, is_header, fill_color)
rows = [
    ("Introduction", 2.4, False, LBLUE),
    ("Skill 1",      3.0, False, LGREY),
    ("Skill 2",      3.0, False, white),
    ("Skill 3",      3.0, False, LGREY),
    ("Skill 4\n(optional)", 3.0, False, white),
    ("Conclusion",   2.4, False, LBLUE),
]

# Scale rows to fit available height
avail_h = tbl_top - tbl_bottom
header_h = 0.7 * cm
data_h   = avail_h - header_h
raw_total = sum(r[1] for r in rows) * cm
scale    = data_h / raw_total
row_hs   = [r[1] * cm * scale for r in rows]

# Draw column header row
cy = tbl_top
c.setFillColor(BLUE)
c.rect(tbl_x, cy - header_h, tbl_w, header_h, fill=1, stroke=0)
for i, (lbl, cx) in enumerate(zip(col_labels, col_xs)):
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7.5)
    # centre text in column
    parts = lbl.split('\n')
    if len(parts) == 2:
        c.drawCentredString(cx + col_ws[i] / 2,
                            cy - header_h * 0.35, parts[0])
        c.setFont('Helvetica', 6.5)
        c.drawCentredString(cx + col_ws[i] / 2,
                            cy - header_h * 0.72, parts[1])
    else:
        c.drawCentredString(cx + col_ws[i] / 2, cy - header_h * 0.52, lbl)

cy -= header_h

# Draw data rows
for (row_lbl, _, _, fill), rh in zip(rows, row_hs):
    row_bottom = cy - rh

    # Row background alternation
    c.setFillColor(fill)
    c.rect(tbl_x, row_bottom, tbl_w, rh, fill=1, stroke=0)

    # Row label (col 0 — dark blue band on very first column)
    c.setFillColor(MID_BLUE)
    c.rect(col_xs[0], row_bottom, col_ws[0], rh, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 8)
    for k, part in enumerate(row_lbl.split('\n')):
        label_y = cy - rh / 2 + (0.22 if len(row_lbl.split('\n')) == 2 else 0) * cm
        if len(row_lbl.split('\n')) == 2:
            label_y = cy - rh / 2 + (0.18 - k * 0.36) * cm
        else:
            label_y = cy - rh / 2 - 0.12 * cm
        c.drawCentredString(col_xs[0] + col_ws[0] / 2, label_y, part)

    # Introduction and Conclusion: merge cols 1-3 into writing space with a prompt
    if row_lbl in ("Introduction", "Conclusion"):
        merged_x = col_xs[1]
        merged_w = sum(col_ws[1:])
        c.setFillColor(fill)
        c.rect(merged_x, row_bottom, merged_w, rh, fill=1, stroke=0)
        c.setFillColor(HexColor('#888888'))
        c.setFont('Helvetica', 7.5)
        if row_lbl == "Introduction":
            prompt = "Rhetorical question:                                       Framing sentence:"
        else:
            prompt = "Link the skills together:                                  Final message to the reader:"
        c.drawString(merged_x + 0.2 * cm,
                     cy - 0.42 * cm, prompt)
        # grid lines for writing
        c.setStrokeColor(MGREY)
        c.setLineWidth(0.3)
        line_gap = 0.46 * cm
        n_lines  = int((rh - 0.6 * cm) / line_gap)
        for li in range(n_lines):
            ly = cy - 0.65 * cm - li * line_gap
            if ly > row_bottom + 0.05 * cm:
                c.line(merged_x + 0.2 * cm, ly,
                       merged_x + merged_w - 0.2 * cm, ly)
    else:
        # Skill sections: ruled lines in cols 1, 2, 3
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

    # Grid lines (column borders and row border)
    c.setStrokeColor(MGREY)
    c.setLineWidth(0.5)
    # row border top
    c.line(tbl_x, cy, tbl_x + tbl_w, cy)
    # column dividers
    for ci in range(1, 4):
        c.line(col_xs[ci], row_bottom, col_xs[ci], cy)

    cy = row_bottom

# Bottom row border + outer box
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
