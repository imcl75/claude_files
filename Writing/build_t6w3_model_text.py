"""
T6W3 Model Text — A4 landscape handout.
Explanation text: How to Survive in the City Using the Way of Jalal.
Left: full model text with subheadings. Right: annotation key + notes space.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black

OUT = '/home/claude/T6W3_Model_Text.pdf'

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
c.setTitle("How to Survive in the City — Model Explanation Text")

# ── Header bar ──────────────────────────────────────────────────────
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11.5)
c.drawString(MARGIN, PAGE_H - bar_h + 0.25 * cm,
             "How to Survive in the City Using the Way of Jalal  \u2014  Model Explanation Text")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.25 * cm,
                  "T6W3  |  Being a Writer  |  Year 4")

# ── Column layout ────────────────────────────────────────────────────
col_split = PAGE_W * 0.58
text_x    = MARGIN
text_w    = col_split - MARGIN - 0.5 * cm
key_x     = col_split + 0.3 * cm
key_w     = PAGE_W - key_x - MARGIN * 0.7
content_top = PAGE_H - bar_h - 0.4 * cm

# ── Annotation key ───────────────────────────────────────────────────
key_h = 4.4 * cm
key_y_top = content_top
c.setFillColor(LBLUE)
c.rect(key_x, key_y_top - key_h, key_w, key_h, fill=1, stroke=0)

c.setFillColor(DBLUE)
c.setFont('Helvetica-Bold', 8.5)
c.drawString(key_x + 0.22 * cm, key_y_top - 0.42 * cm,
             "Annotation key  \u2014  use four colours")

ann_items = [
    ("Colour 1", "Rhetorical question",
     "question that draws the reader in without needing an answer"),
    ("Colour 2", "Subheadings",
     "one-word label that organises each skill section"),
    ("Colour 3", "Causal connectives",
     "therefore, as a result, due to, since, which means"),
    ("Colour 4", "Fronted adverbials",
     "By [doing this]\u2026  /  As a result,\u2026  /  When this happens\u2026"),
]
ky = key_y_top - 1.0 * cm
for label, title, sub in ann_items:
    c.setFillColor(DGREY)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(key_x + 0.3 * cm, ky, f"{label}: {title}")
    c.setFillColor(MGREY)
    c.setFont('Helvetica', 7)
    c.drawString(key_x + 0.52 * cm, ky - 0.28 * cm, sub)
    ky -= 0.72 * cm

# ── Notes area ───────────────────────────────────────────────────────
notes_top    = key_y_top - key_h - 0.2 * cm
notes_bottom = 0.65 * cm
notes_h      = notes_top - notes_bottom

c.setFillColor(LGREY)
c.setStrokeColor(SMOKE)
c.setLineWidth(0.4)
c.rect(key_x, notes_bottom, key_w, notes_h, fill=1, stroke=1)

c.setFillColor(MGREY)
c.setFont('Helvetica', 7.5)
c.drawString(key_x + 0.28 * cm, notes_top - 0.38 * cm, "Annotation notes")

# ruled lines inside notes area
line_gap   = 0.58 * cm
line_count = int((notes_h - 0.7 * cm) / line_gap)
c.setStrokeColor(HexColor('#CCCCCC'))
c.setLineWidth(0.3)
for i in range(line_count):
    ly = notes_top - 0.7 * cm - i * line_gap
    if ly > notes_bottom + 0.1 * cm:
        c.line(key_x + 0.28 * cm, ly, key_x + key_w - 0.28 * cm, ly)

# ── Model text ───────────────────────────────────────────────────────
# Typeset the model text in the left column with subheadings

TITLE_SZ    = 11
INTRO_SZ    = 8.4
BODY_SZ     = 8.2
HEAD_SZ     = 9.5
LEAD        = 0.39 * cm   # line leading
PARA_GAP    = 0.14 * cm
HEAD_GAP    = 0.20 * cm   # extra space before a subheading

def wrap_text(text, font, size, max_w):
    """Split text into lines that fit within max_w."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

from reportlab.pdfbase.pdfmetrics import stringWidth

cy = content_top - 0.1 * cm   # current y (bottom of current text)

def draw_para(text, font='Helvetica', size=BODY_SZ, gap_before=PARA_GAP,
              color=DGREY, indent=0):
    global cy
    cy -= gap_before
    lines = wrap_text(text, font, size, text_w - indent)
    for ln in lines:
        cy -= LEAD
        c.setFillColor(color)
        c.setFont(font, size)
        c.drawString(text_x + indent, cy, ln)

def draw_head(text):
    global cy
    cy -= HEAD_GAP
    cy -= LEAD * 1.2
    c.setFillColor(BLUE)
    c.setFont('Helvetica-Bold', HEAD_SZ)
    c.drawString(text_x, cy, text)
    # thin underline
    c.setStrokeColor(BLUE)
    c.setLineWidth(0.5)
    lw = stringWidth(text, 'Helvetica-Bold', HEAD_SZ)
    c.line(text_x, cy - 1.5, text_x + lw, cy - 1.5)
    cy -= 0.08 * cm

# Title
draw_para("How to Survive in the City Using the Way of Jalal",
          font='Helvetica-Bold', size=TITLE_SZ, gap_before=0.0 * cm, color=DBLUE)
cy -= 0.1 * cm

# Intro para
intro = ("Have you ever imagined leaving the safety of your home and stepping into the city "
         "for the very first time? Would you know what to do if danger appeared from the "
         "shadows? The city is full of noisy roads, strange creatures and hidden enemies. "
         "Fortunately, the ancient Way of Jalal teaches seven special skills that can help "
         "a cat survive. Read on to discover how each skill can keep you safe.")
draw_para(intro, font='Helvetica', size=INTRO_SZ, gap_before=0.28 * cm, color=DGREY)

# Skills
skills = [
    ("Open Mind",
     "When you enter a new place, things may not happen as you expect. Therefore, you need "
     "to keep an open mind. If one plan does not work, you must be ready to think of another. "
     "By looking at problems in different ways, you can find solutions and avoid danger."),
    ("Awareness",
     "The city is full of sights, sounds and smells. As danger can appear at any moment, you "
     "must pay attention to everything around you. Listen carefully, watch closely and trust "
     "your senses. Due to this skill, you may spot trouble before it reaches you."),
    ("Hunting",
     "Finding food is important if you want to survive. To hunt successfully, you need to "
     "move quietly and patiently. If you rush, your prey may escape. A skilled hunter waits "
     "for the perfect moment before striking."),
    ("Slow-Time",
     "Sometimes danger moves very quickly. When this happens, Slow-Time can help. By calming "
     "your mind and focusing completely, everything seems to move more slowly. As a result, "
     "you will have more time to dodge attacks and make good decisions."),
    ("Moving Circles",
     "You may face more than one enemy at a time. Since standing still makes you an easy "
     "target, you should keep moving. The skill of Moving Circles allows you to stay in "
     "motion while watching every direction. It is much harder for enemies to surround you."),
    ("Shadow-Walking",
     "There are times when fighting is not the best choice. If danger is too great, it is "
     "often safer to avoid being seen. By staying silent and moving through dark places, you "
     "can travel unnoticed. In this way, you can escape trouble without anyone knowing you "
     "were there."),
    ("Trust Yourself",
     "The final skill is the most challenging because it comes from inside you. Even when you "
     "feel afraid, you must believe in yourself. If you trust your training and your instincts, "
     "you will be able to face challenges with confidence. This skill helps you use all the "
     "others successfully."),
]

for head, body in skills:
    draw_head(head)
    draw_para(body, font='Helvetica', size=BODY_SZ, gap_before=0.10 * cm, color=DGREY)

# Conclusion
draw_para("The city can be a dangerous and unpredictable place. However, by using the seven "
          "skills of the Way of Jalal, a cat can stay safe and overcome many challenges. "
          "These skills will help you survive and find your way through the Outside.",
          font='Helvetica', size=BODY_SZ, gap_before=PARA_GAP * 1.5, color=DGREY)

# ── Footer ───────────────────────────────────────────────────────────
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, 0.42 * cm, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W / 2, 0.13 * cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

c.save()
print(f"Saved: {OUT}")
