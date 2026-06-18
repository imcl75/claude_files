"""
T6W3 Boxing-Up — All Seven Skills Reference Sheet.
Compact read-only version for children to use as a planning support.
Same column layout as the blank/model but 7 skill rows, no intro/conclusion.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white

OUT = '/home/claude/T6W3_Boxing_Up_All7.pdf'
PAGE_W, PAGE_H = A4
MARGIN   = 1.3 * cm
BLUE     = HexColor('#1798d3')
MID_BLUE = HexColor('#2980B9')
MGREY    = HexColor('#CCCCCC')
DGREY    = HexColor('#333333')
LGREY    = HexColor('#888888')
INK      = HexColor('#1a3a5c')

ALL_SKILLS = [
    {
        "name": "Open Mind",
        "col1": ["Thinking in different ways."],
        "col2": ["Stay calm and look for new solutions."],
        "col3": ["Helps solve problems and adapt to new situations."],
    },
    {
        "name": "Awareness",
        "col1": ["Noticing everything around you."],
        "col2": ["Use your senses to gather information."],
        "col3": ["Helps spot danger before it arrives."],
    },
    {
        "name": "Hunting",
        "col1": ["Catching food and defending yourself."],
        "col2": ["Move quietly and strike at the right moment."],
        "col3": ["Helps find food and stay safe."],
    },
    {
        "name": "Slow-Time",
        "col1": ["Focusing your mind completely."],
        "col2": ["Everything seems to move more slowly."],
        "col3": ["Helps you react quickly and avoid danger."],
    },
    {
        "name": "Moving Circles",
        "col1": ["Fighting while staying in motion."],
        "col2": ["Keep moving around enemies."],
        "col3": ["Helps avoid attacks and escape being surrounded."],
    },
    {
        "name": "Shadow-Walking",
        "col1": ["Moving without being seen."],
        "col2": ["Stay silent and use shadows as cover."],
        "col3": ["Helps avoid enemies and sneak through the city."],
    },
    {
        "name": "Trust Yourself",
        "col1": ["Believing in yourself."],
        "col2": ["Trust your instincts and training."],
        "col3": ["Helps you stay brave and make good decisions."],
    },
]

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("T6W3 Boxing-Up — All Seven Skills Reference")

# Header
BAR = 0.90 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H-BAR, PAGE_W, BAR, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MARGIN, PAGE_H-BAR+0.25*cm,
             "Boxing-Up Plan  \u2014  All Seven Skills  \u2014  Reference")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W-MARGIN, PAGE_H-BAR+0.25*cm, "T6W3  |  Being a Writer  |  Year 4")

# Footer
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, 0.42*cm, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W/2, 0.13*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

# Instruction
note_y = PAGE_H - BAR - 0.52*cm
c.setFillColor(HexColor('#555555')); c.setFont('Helvetica', 8.2)
c.drawString(MARGIN, note_y,
    "Use this sheet to help you plan a skill your teacher has not modelled. "
    "Choose your skill, then write your own notes using these ideas.")

# Table
tbl_top    = note_y - 0.32*cm
tbl_bottom = 0.55*cm
tbl_w      = PAGE_W - 2*MARGIN
tbl_x      = MARGIN

col0_w = 0.72 * cm
data_w = (tbl_w - col0_w) / 3
col_xs = [tbl_x,
          tbl_x + col0_w,
          tbl_x + col0_w + data_w,
          tbl_x + col0_w + 2*data_w]

header_h  = 0.65 * cm
avail_h   = tbl_top - tbl_bottom - header_h
row_h     = avail_h / len(ALL_SKILLS)   # fills the page evenly

# Column headers
cy = tbl_top
c.setFillColor(BLUE)
c.rect(tbl_x, cy-header_h, tbl_w, header_h, fill=1, stroke=0)

# Col 0 header — rotated
c.saveState()
c.translate(col_xs[0]+col0_w/2, cy-header_h/2)
c.rotate(90)
c.setFillColor(white); c.setFont('Helvetica-Bold', 7)
c.drawCentredString(0, -0.09*cm, "Skill")
c.restoreState()

for i, lbl in enumerate(["Skill name  +  what the skill is",
                          "How it works",
                          "What happens as a result"], start=1):
    c.setFillColor(white); c.setFont('Helvetica-Bold', 7.8)
    c.drawCentredString(col_xs[i]+data_w/2, cy-header_h*0.57, lbl)

cy -= header_h

# Skill rows
for si, sk in enumerate(ALL_SKILLS):
    row_bottom = cy - row_h

    # White background
    c.setFillColor(white)
    c.rect(col_xs[1], row_bottom, tbl_w-col0_w, row_h, fill=1, stroke=0)

    # Col 0 blue band with rotated name
    c.setFillColor(MID_BLUE)
    c.rect(col_xs[0], row_bottom, col0_w, row_h, fill=1, stroke=0)
    c.saveState()
    c.translate(col_xs[0]+col0_w/2, row_bottom+row_h/2)
    c.rotate(90)
    sz = 7.5 if len(sk['name']) <= 10 else 6.5
    c.setFillColor(white); c.setFont('Helvetica-Bold', sz)
    c.drawCentredString(0, -0.10*cm, sk['name'])
    c.restoreState()

    # Content — skill name bold at top of col 1, then notes
    pad = 0.22 * cm
    # Col 1: skill name + what it is
    c.setFillColor(MID_BLUE); c.setFont('Helvetica-Bold', 8.5)
    c.drawString(col_xs[1]+0.18*cm, cy-0.38*cm, sk['name'])
    c.setFillColor(INK); c.setFont('Helvetica-Oblique', 8.5)
    for li, ln in enumerate(sk['col1']):
        c.drawString(col_xs[1]+0.18*cm, cy-0.72*cm-li*0.34*cm, ln)

    # Cols 2 & 3
    for ci, key in [(2,'col2'), (3,'col3')]:
        c.setFillColor(INK); c.setFont('Helvetica-Oblique', 8.5)
        for li, ln in enumerate(sk[key]):
            c.drawString(col_xs[ci]+0.18*cm, cy-0.38*cm-li*0.34*cm, ln)

    # Grid lines
    c.setStrokeColor(MGREY); c.setLineWidth(0.5)
    c.line(tbl_x, cy, tbl_x+tbl_w, cy)
    for ci in range(1, 4):
        c.line(col_xs[ci], row_bottom, col_xs[ci], cy)

    cy = row_bottom

# Bottom border + outer box
c.setStrokeColor(MGREY); c.setLineWidth(0.5)
c.line(tbl_x, cy, tbl_x+tbl_w, cy)
c.rect(tbl_x, cy, tbl_w, tbl_top-cy, fill=0, stroke=1)

c.save()
print(f"Saved: {OUT}")
