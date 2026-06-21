"""
T6W3 Seven Skills — all explanation paragraphs on one A4 page.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Skill_Paragraphs.pdf'
PAGE_W, PAGE_H = A4
MG = 1.3 * cm

BLUE  = HexColor('#1798d3')
DBLUE = HexColor('#154360')
DGREY = HexColor('#2C2C2C')

SKILLS = [
    {
        "head": "Open Mind",
        "body": (
            "The skill of Open Mind helps a cat to think in different ways. "
            "This essential skill gives a cat in the city the ability to stay calm while "
            "looking for solutions to the many challenges their new surroundings create for them. "
            "As a result, a cat can solve problems and adapt to the new and dangerous situations "
            "they will find themself in."
        ),
    },
    {
        "head": "Awareness",
        "body": (
            "The skill of Awareness helps a cat to notice everything that is happening around it. "
            "This essential skill gives a cat in the city the ability to use its senses to gather "
            "vital information about its surroundings at all times. "
            "Due to this, a cat can spot danger before it arrives and stay one step ahead of any threat."
        ),
    },
    {
        "head": "Hunting",
        "body": (
            "The skill of Hunting helps a cat to catch food and defend itself from danger. "
            "This essential skill gives a cat in the city the ability to move quietly and wait "
            "patiently for exactly the right moment to strike. "
            "It never rushes towards its prey, which means it can find the food it needs to survive "
            "and keep itself safe from harm."
        ),
    },
    {
        "head": "Slow-Time",
        "body": (
            "The skill of Slow-Time helps a cat to focus its mind completely in moments of danger. "
            "This essential skill gives a cat in the city the ability to slow its thoughts so that "
            "everything around it seems to move more slowly. "
            "When this happens, a cat has far more time to dodge attacks and avoid the many dangers "
            "of city life."
        ),
    },
    {
        "head": "Moving Circles",
        "body": (
            "The skill of Moving Circles helps a cat to fight back while keeping itself in constant "
            "motion. "
            "This essential skill gives a cat in the city the ability to keep moving around its "
            "enemies so that they cannot predict where it will be next. "
            "A cat in constant motion is far harder to surround, so enemies struggle to land a "
            "successful attack."
        ),
    },
    {
        "head": "Shadow-Walking",
        "body": (
            "The skill of Shadow-Walking helps a cat to travel through the city without being seen. "
            "This essential skill gives a cat in the city the ability to stay completely silent and "
            "use the darkness of shadows as cover. "
            "By moving in this way, a cat can avoid enemies entirely and pass through even the most "
            "dangerous parts of the city undetected."
        ),
    },
    {
        "head": "Trust Yourself",
        "body": (
            "The skill of Trust Yourself helps a cat to believe in its own abilities, even when "
            "fear takes hold. "
            "This essential skill gives a cat in the city the ability to rely on its instincts and "
            "the training it has received from Jalal. "
            "It is the most difficult skill to master, which is why a cat that truly trusts itself "
            "can face any danger and make the decisions that will keep it alive."
        ),
    },
]

def wrap(text, font, size, max_w):
    words = text.split()
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

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("The Seven Skills — Explanation Paragraphs")

# Header
BAR = 0.88 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H-BAR, PAGE_W, BAR, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MG, PAGE_H-BAR+0.25*cm,
             "The Seven Skills of the Way of Jalal  \u2014  Explanation Text")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W-MG, PAGE_H-BAR+0.25*cm, "T6W3  |  Being a Writer  |  Year 4")

# Footer
FOOT = 0.40 * cm
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, FOOT, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W/2, 0.12*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

CW   = PAGE_W - 2*MG
HEAD_SZ = 14
BODY_SZ = 13
LEAD    = 0.520 * cm
HEAD_GAP = 1.10 * cm
PARA_GAP = 0.16 * cm

cy = PAGE_H - BAR - 0.30*cm

for i, sk in enumerate(SKILLS):
    # Subheading
    cy -= HEAD_GAP
    cy -= HEAD_SZ / 72 * 2.54 * cm * 1.2
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', HEAD_SZ)
    c.drawString(MG, cy, sk['head'])
    lw = stringWidth(sk['head'], 'Helvetica-Bold', HEAD_SZ)
    c.setStrokeColor(BLUE); c.setLineWidth(0.5)
    c.line(MG, cy-1.5, MG+lw, cy-1.5)

    # Body text
    cy -= PARA_GAP
    lines = wrap(sk['body'], 'Helvetica', BODY_SZ, CW)
    for ln in lines:
        cy -= LEAD
        c.setFillColor(DGREY); c.setFont('Helvetica', BODY_SZ)
        c.drawString(MG, cy, ln)

c.save()
# Report bottom of last element vs footer
print(f"Saved: {OUT}")
print(f"Bottom of content: {cy/cm:.2f}cm from bottom  (footer needs ~0.8cm)")
