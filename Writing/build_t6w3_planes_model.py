"""
T6W3 Planes Model Text — A4 landscape handout.
Same format as Varjak model text. Three sections: Wings, Engines, The Tail.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Planes_Model_Text.pdf'

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 1.5 * cm

BLUE   = HexColor('#1798d3')
LBLUE  = HexColor('#D6EAF8')
DBLUE  = HexColor('#154360')
DGREY  = HexColor('#2C2C2C')
MGREY  = HexColor('#AAAAAA')
LGREY  = HexColor('#F5F5F5')
SMOKE  = HexColor('#EEEEEE')

c = canvas.Canvas(OUT, pagesize=landscape(A4))
c.setTitle("How a Plane Gets Into the Sky and Stays There — Model Explanation Text")

# Header
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11.5)
c.drawString(MARGIN, PAGE_H - bar_h + 0.25*cm,
             "How a Plane Gets Into the Sky and Stays There  \u2014  Model Explanation Text")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.25*cm,
                  "T6W3  |  Being a Writer  |  Year 4")

# Footer
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, 0.42*cm, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W/2, 0.13*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

# Column layout
col_split  = PAGE_W * 0.58
text_x     = MARGIN
text_w     = col_split - MARGIN - 0.5*cm
key_x      = col_split + 0.3*cm
key_w      = PAGE_W - key_x - MARGIN * 0.7
content_top = PAGE_H - bar_h - 0.4*cm

# Annotation key
key_h = 4.4 * cm
key_y_top = content_top
c.setFillColor(LBLUE)
c.rect(key_x, key_y_top - key_h, key_w, key_h, fill=1, stroke=0)
c.setFillColor(DBLUE); c.setFont('Helvetica-Bold', 8.5)
c.drawString(key_x + 0.22*cm, key_y_top - 0.42*cm,
             "Annotation key  \u2014  use four colours")

ann_items = [
    ("Colour 1", "Rhetorical question",
     "question that draws the reader in without needing an answer"),
    ("Colour 2", "Subheadings",
     "one-word label that organises each section"),
    ("Colour 3", "Causal connectives",
     "therefore, as a result, due to, since, which means"),
    ("Colour 4", "Fronted adverbials",
     "By [doing this]\u2026  /  As a result,\u2026  /  When this happens\u2026"),
]
ky = key_y_top - 1.0*cm
for label, title, sub in ann_items:
    c.setFillColor(DGREY); c.setFont('Helvetica-Bold', 7.5)
    c.drawString(key_x + 0.3*cm, ky, f"{label}: {title}")
    c.setFillColor(MGREY); c.setFont('Helvetica', 7)
    c.drawString(key_x + 0.52*cm, ky - 0.28*cm, sub)
    ky -= 0.72*cm

# Notes area
notes_top    = key_y_top - key_h - 0.2*cm
notes_bottom = 0.65*cm
notes_h      = notes_top - notes_bottom
c.setFillColor(LGREY); c.setStrokeColor(SMOKE); c.setLineWidth(0.4)
c.rect(key_x, notes_bottom, key_w, notes_h, fill=1, stroke=1)
c.setFillColor(MGREY); c.setFont('Helvetica', 7.5)
c.drawString(key_x + 0.28*cm, notes_top - 0.38*cm, "Annotation notes")
line_gap   = 0.58*cm
line_count = int((notes_h - 0.7*cm) / line_gap)
c.setStrokeColor(HexColor('#CCCCCC')); c.setLineWidth(0.3)
for i in range(line_count):
    ly = notes_top - 0.7*cm - i*line_gap
    if ly > notes_bottom + 0.1*cm:
        c.line(key_x + 0.28*cm, ly, key_x + key_w - 0.28*cm, ly)

# Text helpers
TITLE_SZ = 11
INTRO_SZ = 8.8
BODY_SZ  = 8.5
HEAD_SZ  = 9.5
LEAD     = 0.39*cm
PARA_GAP = 0.14*cm
HEAD_GAP = 0.20*cm

def wrap_text(text, font, size, max_w):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

cy = content_top - 0.1*cm

def draw_para(text, font='Helvetica', size=BODY_SZ, gap_before=PARA_GAP, color=DGREY):
    global cy
    cy -= gap_before
    for ln in wrap_text(text, font, size, text_w):
        cy -= LEAD
        c.setFillColor(color); c.setFont(font, size)
        c.drawString(text_x, cy, ln)

def draw_head(text):
    global cy
    cy -= HEAD_GAP
    cy -= LEAD * 1.2
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', HEAD_SZ)
    c.drawString(text_x, cy, text)
    lw = stringWidth(text, 'Helvetica-Bold', HEAD_SZ)
    c.setStrokeColor(BLUE); c.setLineWidth(0.5)
    c.line(text_x, cy - 1.5, text_x + lw, cy - 1.5)
    cy -= 0.08*cm

# Title
draw_para("How a Plane Gets Into the Sky and Stays There",
          font='Helvetica-Bold', size=TITLE_SZ, gap_before=0.0*cm, color=DBLUE)
cy -= 0.1*cm

# Introduction
draw_para(
    "Have you ever watched a plane disappear into the clouds and wondered how something so heavy "
    "can fly? A jumbo jet can weigh over 400 tonnes, yet it climbs into the sky with ease. "
    "Planes are extraordinary machines, and the science behind them is fascinating. "
    "Read on to discover how three key parts work together to lift a plane off the ground "
    "and keep it soaring.",
    font='Helvetica', size=INTRO_SZ, gap_before=0.28*cm, color=DGREY
)

# Section 1: Wings
draw_head("Wings")
draw_para(
    "A plane's wings are its most important feature. As the engines push the plane forward, air "
    "flows over and under each wing. Due to the special curved shape of the wing, air moves "
    "faster over the top than underneath. As a result, this difference in air pressure creates "
    "a powerful upward force called lift, which pushes the plane into the sky.",
    font='Helvetica', size=BODY_SZ, gap_before=0.10*cm, color=DGREY
)

# Section 2: Engines
draw_head("Engines")
draw_para(
    "Without thrust, a plane cannot move fast enough to take off. Jet engines work by sucking "
    "in air at the front, mixing it with fuel and burning it. By doing this, the engine produces "
    "a powerful blast of hot gas that shoots backwards. As a result, the plane is pushed forwards "
    "at tremendous speed, which gives the wings enough airflow to generate lift.",
    font='Helvetica', size=BODY_SZ, gap_before=0.10*cm, color=DGREY
)

# Section 3: The Tail
draw_head("The Tail")
draw_para(
    "Once a plane is in the air, the pilot needs to control its direction. The tail contains "
    "moveable surfaces called rudders and elevators. By adjusting these surfaces, the pilot can "
    "steer left or right and climb or descend. Therefore, the tail is what allows the pilot to "
    "navigate safely through the sky and bring the plane in to land.",
    font='Helvetica', size=BODY_SZ, gap_before=0.10*cm, color=DGREY
)

# Conclusion
draw_para(
    "Planes are remarkable machines. However, by working together, the wings, engines and tail "
    "make flight possible. Whether you are watching from the ground or sitting in a window seat, "
    "these three parts are working constantly to keep the plane safe in the sky.",
    font='Helvetica', size=BODY_SZ, gap_before=PARA_GAP * 1.5, color=DGREY
)

c.save()
print(f"Saved: {OUT}")
