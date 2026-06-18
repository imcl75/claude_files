"""
T6W3 Boxing-Up Plan — A4 portrait, blank version for children.
- 3 skill rows only (no Skill 4)
- Col 0 narrow (0.72cm) with rotated label text
- Cols 1, 2, 3 equal width
- Col 1 skill rows: "Skill name:" prompt at top, then ruled lines
- All writing areas pure white
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black

OUT = '/home/claude/T6W3_Boxing_Up.pdf'
PAGE_W, PAGE_H = A4
MARGIN = 1.3 * cm
BLUE     = HexColor('#1798d3')
MID_BLUE = HexColor('#2980B9')
DBLUE    = HexColor('#154360')
MGREY    = HexColor('#CCCCCC')
LGREY    = HexColor('#888888')
DGREY    = HexColor('#333333')

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("T6W3 Boxing-Up Plan — Explanation Text")

# ── Header ──────────────────────────────────────────────────────────
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MARGIN, PAGE_H - bar_h + 0.25*cm, "Boxing-Up Plan  \u2014  Explanation Text")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.25*cm, "T6W3  |  Being a Writer  |  Year 4")

# ── Name line ─────────────────────────────────────────────────────
name_y = PAGE_H - bar_h - 0.60*cm
c.setFillColor(DGREY); c.setFont('Helvetica', 9)
c.drawString(MARGIN, name_y, "Name:")
c.setStrokeColor(MGREY); c.setLineWidth(0.5)
c.line(MARGIN + 1.5*cm, name_y - 0.05*cm, MARGIN + 8*cm, name_y - 0.05*cm)
c.drawString(MARGIN + 9*cm, name_y, "Class:")
c.line(MARGIN + 10.5*cm, name_y - 0.05*cm, PAGE_W - MARGIN, name_y - 0.05*cm)

# ── Instruction ─────────────────────────────────────────────────────
note_y = name_y - 0.55*cm
c.setFont('Helvetica', 8.2); c.setFillColor(HexColor('#555555'))
c.drawString(MARGIN, note_y,
    "Choose three skills from the Seven Skills. "
    "Complete a row for each one. Write notes, not full sentences.")

# ── Table dimensions ────────────────────────────────────────────────
tbl_top    = note_y - 0.35*cm
tbl_bottom = 0.85*cm
tbl_w      = PAGE_W - 2*MARGIN
tbl_x      = MARGIN

# Col 0 narrow; cols 1,2,3 equal
col0_w  = 0.72 * cm
data_w  = (tbl_w - col0_w) / 3
col_xs  = [tbl_x,
           tbl_x + col0_w,
           tbl_x + col0_w + data_w,
           tbl_x + col0_w + 2*data_w]
col_ws  = [col0_w, data_w, data_w, data_w]

# Column header labels (col 0 handled separately — rotated)
col_labels = [
    "",
    "Skill name  +  what the skill is",
    "How it works",
    "What happens as a result",
]

# Rows: (label, raw_height_cm)
rows = [
    ("Introduction", 2.4),
    ("Skill 1",      3.2),
    ("Skill 2",      3.2),
    ("Skill 3",      3.2),
    ("Conclusion",   2.4),
]

# Scale rows to fill available height
header_h   = 0.70 * cm
avail_h    = tbl_top - tbl_bottom
data_h     = avail_h - header_h
raw_total  = sum(r[1] for r in rows) * cm
scale      = data_h / raw_total
row_hs     = [r[1] * cm * scale for r in rows]

# ── Column header row ───────────────────────────────────────────────
cy = tbl_top
c.setFillColor(BLUE)
c.rect(tbl_x, cy - header_h, tbl_w, header_h, fill=1, stroke=0)

# Col 0 header — rotated "Section"
c.saveState()
hcx = col_xs[0] + col0_w / 2
hcy = cy - header_h / 2
c.translate(hcx, hcy)
c.rotate(90)
c.setFillColor(white); c.setFont('Helvetica-Bold', 7)
c.drawCentredString(0, -0.09*cm, "Section")
c.restoreState()

# Cols 1-3 headers
for i in range(1, 4):
    c.setFillColor(white); c.setFont('Helvetica-Bold', 7.8)
    lbl = col_labels[i]
    c.drawCentredString(col_xs[i] + col_ws[i] / 2,
                        cy - header_h * 0.57, lbl)

cy -= header_h

# ── Data rows ───────────────────────────────────────────────────────
SKILL_NAME_H = 0.52 * cm   # height reserved for skill name prompt in col 1

for (row_lbl, _), rh in zip(rows, row_hs):
    row_bottom = cy - rh
    is_skill   = row_lbl.startswith('Skill')
    is_merged  = row_lbl in ("Introduction", "Conclusion")

    # White background for ALL cells (col 0 blue band drawn separately)
    c.setFillColor(white)
    c.rect(col_xs[1], row_bottom, tbl_w - col0_w, rh, fill=1, stroke=0)

    # Col 0: blue band with rotated label
    c.setFillColor(MID_BLUE)
    c.rect(col_xs[0], row_bottom, col0_w, rh, fill=1, stroke=0)
    c.saveState()
    c.translate(col_xs[0] + col0_w / 2, row_bottom + rh / 2)
    c.rotate(90)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 8)
    c.drawCentredString(0, -0.10*cm, row_lbl)
    c.restoreState()

    # Introduction / Conclusion: merged cols 1-3 with prompts
    if is_merged:
        merged_x = col_xs[1]
        merged_w = tbl_w - col0_w
        c.setFillColor(HexColor('#888888'))
        c.setFont('Helvetica', 7.5)
        if row_lbl == "Introduction":
            c.drawString(merged_x + 0.20*cm, cy - 0.36*cm,
                         "Rhetorical question:                                        Framing sentence:")
        else:
            c.drawString(merged_x + 0.20*cm, cy - 0.36*cm,
                         "Link the skills together:                                   Final message to the reader:")
        # Ruled lines
        c.setStrokeColor(MGREY); c.setLineWidth(0.3)
        lg = 0.46 * cm
        n  = int((rh - 0.55*cm) / lg)
        for li in range(n):
            ly = cy - 0.55*cm - li * lg
            if ly > row_bottom + 0.05*cm:
                c.line(merged_x + 0.20*cm, ly, merged_x + merged_w - 0.20*cm, ly)

    # Skill rows
    else:
        c.setStrokeColor(MGREY); c.setLineWidth(0.3)
        lg = 0.44 * cm

        for ci in range(1, 4):
            cx2 = col_xs[ci]
            cw2 = col_ws[ci]

            if ci == 1:
                # Skill name prompt at top of col 1
                c.setFillColor(LGREY)
                c.setFont('Helvetica', 7.2)
                c.drawString(cx2 + 0.16*cm, cy - 0.30*cm, "Skill name:")
                c.setStrokeColor(MGREY); c.setLineWidth(0.4)
                c.line(cx2 + 1.6*cm, cy - 0.32*cm, cx2 + cw2 - 0.16*cm, cy - 0.32*cm)
                # Ruled lines below skill name prompt
                n = int((rh - SKILL_NAME_H - 0.18*cm) / lg)
                for li in range(n):
                    ly = cy - SKILL_NAME_H - 0.18*cm - li * lg
                    if ly > row_bottom + 0.05*cm:
                        c.line(cx2 + 0.16*cm, ly, cx2 + cw2 - 0.16*cm, ly)
            else:
                # Cols 2 & 3: ruled lines from top
                n = int((rh - 0.28*cm) / lg)
                for li in range(n):
                    ly = cy - 0.28*cm - li * lg
                    if ly > row_bottom + 0.05*cm:
                        c.setStrokeColor(MGREY); c.setLineWidth(0.3)
                        c.line(cx2 + 0.16*cm, ly, cx2 + cw2 - 0.16*cm, ly)

    # Grid lines
    c.setStrokeColor(MGREY); c.setLineWidth(0.5)
    c.line(tbl_x, cy, tbl_x + tbl_w, cy)
    for ci in range(1, 4):
        c.line(col_xs[ci], row_bottom, col_xs[ci], cy)

    cy = row_bottom

# Bottom border + outer box
c.setStrokeColor(MGREY); c.setLineWidth(0.5)
c.line(tbl_x, cy, tbl_x + tbl_w, cy)
c.rect(tbl_x, cy, tbl_w, tbl_top - cy, fill=0, stroke=1)

# ── Footer ──────────────────────────────────────────────────────────
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, 0.42*cm, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W / 2, 0.13*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

c.save()
print(f"Saved: {OUT}")
