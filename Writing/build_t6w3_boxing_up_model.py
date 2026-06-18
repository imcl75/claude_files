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

OUT = '/home/claude/T6W3_Boxing_Up_Model.pdf'
PAGE_W, PAGE_H = A4
MARGIN = 1.3 * cm
BLUE     = HexColor('#1798d3')
MID_BLUE = HexColor('#2980B9')
DBLUE    = HexColor('#154360')
MGREY    = HexColor('#CCCCCC')
LGREY    = HexColor('#888888')
DGREY    = HexColor('#333333')
INK      = HexColor('#1a3a5c')   # model note colour


# ── Model content ────────────────────────────────────────────────────
INTRO_CONTENT = {
    "Rhetorical question":    "Have you ever imagined stepping\ninto the city for the first time?",
    "Framing sentence":       "The city is full of dangers a\nhouse cat has never faced.",
    "Encouragement sentence": "Fortunately, the Way of Jalal\nteaches skills to help any cat.\nRead on to discover how each\nskill can keep you safe.",
}
SKILL_DATA = [
    {
        "name":   "Open Mind",
        "col1":   ["Thinking in different ways."],
        "col2":   ["Stay calm and look for", "new solutions."],
        "col3":   ["Helps solve problems and", "adapt to new situations."],
    },
    {
        "name":   "Awareness",
        "col1":   ["Noticing everything around you."],
        "col2":   ["Use your senses to", "gather information."],
        "col3":   ["Helps spot danger", "before it arrives."],
    },
    {
        "name":   "Hunting",
        "col1":   ["Catching food and", "defending yourself."],
        "col2":   ["Move quietly and strike", "at the right moment."],
        "col3":   ["Helps find food", "and stay safe."],
    },
]
CONC_CONTENT = {
    "Link the skills together":   ["Use all skills together", "to stay safe in the city.", "The skills work best combined."],
    "Final message to the reader":["Any cat can survive", "the Outside with", "the Way of Jalal."],
}

def draw_notes(lines, x, y_top, max_w, size=8.0):
    """Draw italic model notes from y_top downward."""
    c.setFillColor(INK); c.setFont('Helvetica-Oblique', size)
    for i, ln in enumerate(lines):
        c.drawString(x + 0.18*cm, y_top - 0.38*cm - i * 0.36*cm, ln)

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("T6W3 Boxing-Up Plan — Explanation Text — MODEL")

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
c.setFillColor(INK); c.setFont('Helvetica-Oblique', 9)
c.drawString(MARGIN + 1.7*cm, name_y, 'Class model')


# ── Instruction ─────────────────────────────────────────────────────
note_y = name_y - 0.55*cm
c.setFont('Helvetica', 8.2); c.setFillColor(HexColor('#555555'))
c.drawString(MARGIN, note_y,
    "Choose three skills from the Seven Skills.")

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
SKILL_NAME_H = 0.80 * cm   # height reserved for skill name prompt in col 1

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

    # Introduction / Conclusion: merged cols 1-3, subdivided
    if is_merged:
        merged_x = col_xs[1]
        merged_w = tbl_w - col0_w
        lg = 0.46 * cm

        if row_lbl == "Introduction":
            # 3 equal sub-boxes: Rhet Q / Framing sent / Encouragement sent
            sub_labels = [
                "Rhetorical question",
                "Framing sentence",
                "Encouragement sentence",
            ]
            n_subs  = 3
            sub_w   = merged_w / n_subs
            for si, lbl in enumerate(sub_labels):
                sx = merged_x + si * sub_w
                # thin divider (not before first)
                if si > 0:
                    c.setStrokeColor(MGREY); c.setLineWidth(0.4)
                    c.line(sx, row_bottom, sx, cy)
                # label
                c.setFillColor(HexColor('#888888')); c.setFont('Helvetica', 7.2)
                c.drawString(sx + 0.18*cm, cy - 0.34*cm, lbl)
                # model notes
                note_lines = INTRO_CONTENT.get(lbl, [])
                if isinstance(note_lines, str):
                    note_lines = note_lines.split('\n')
                draw_notes(note_lines, sx, cy - 0.52*cm, sub_w)

        else:  # Conclusion — 2 equal sub-boxes
            sub_labels = [
                "Link the skills together",
                "Final message to the reader",
            ]
            n_subs = 2
            sub_w  = merged_w / n_subs
            for si, lbl in enumerate(sub_labels):
                sx = merged_x + si * sub_w
                if si > 0:
                    c.setStrokeColor(MGREY); c.setLineWidth(0.4)
                    c.line(sx, row_bottom, sx, cy)
                c.setFillColor(HexColor('#888888')); c.setFont('Helvetica', 7.2)
                c.drawString(sx + 0.18*cm, cy - 0.34*cm, lbl)
                note_lines = CONC_CONTENT.get(lbl, [])
                draw_notes(note_lines, sx, cy - 0.52*cm, sub_w)

    # Skill rows
    else:
        c.setStrokeColor(MGREY); c.setLineWidth(0.3)
        lg = 0.44 * cm

        for ci in range(1, 4):
            cx2 = col_xs[ci]
            cw2 = col_ws[ci]

            if ci == 1:
                # Skill name prompt + model content
                sk_idx = int(row_lbl[-1]) - 1
                sk = SKILL_DATA[sk_idx] if sk_idx < len(SKILL_DATA) else {}
                c.setFillColor(LGREY); c.setFont('Helvetica', 7.2)
                c.drawString(cx2 + 0.16*cm, cy - 0.56*cm, "Skill name:")
                c.setStrokeColor(MGREY); c.setLineWidth(0.4)
                c.line(cx2 + 1.6*cm, cy - 0.60*cm, cx2 + cw2 - 0.16*cm, cy - 0.60*cm)
                # Model skill name on the line
                c.setFillColor(INK); c.setFont('Helvetica-Oblique', 9)
                c.drawString(cx2 + 1.7*cm, cy - 0.56*cm, sk.get('name', ''))
                # Model notes below
                draw_notes(sk.get('col1', []), cx2, cy - SKILL_NAME_H - 0.02*cm, cw2)
            else:
                # Cols 2 & 3: model notes
                sk_idx = int(row_lbl[-1]) - 1
                sk = SKILL_DATA[sk_idx] if sk_idx < len(SKILL_DATA) else {}
                col_key = 'col2' if ci == 2 else 'col3'
                draw_notes(sk.get(col_key, []), cx2, cy - 0.28*cm, cw2)

    # Grid lines
    c.setStrokeColor(MGREY); c.setLineWidth(0.5)
    c.line(tbl_x, cy, tbl_x + tbl_w, cy)
    if is_merged:
        # Only the blue-band border; sub-dividers drawn inside is_merged block
        c.line(col_xs[1], row_bottom, col_xs[1], cy)
    else:
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
