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
            "In a city full of hidden dangers, this skill allows a cat to use all of its senses "
            "to gather information about what is lurking nearby. "
            "Due to this, a cat can spot danger before it arrives and stay one step ahead "
            "of any threat."
        ),
    },
    {
        "head": "Hunting",
        "body": (
            "The skill of Hunting helps a cat to catch food and protect itself from danger. "
            "For a cat in the city, this skill provides the means to move quietly and to strike "
            "at exactly the right moment. "
            "It never rushes towards its prey, which means it can find the food it needs "
            "and keep itself safe from harm."
        ),
    },
    {
        "head": "Slow-Time",
        "body": (
            "The skill of Slow-Time helps a cat to focus its mind completely when danger is near. "
            "Using this skill, a cat in the city can slow its thoughts until everything around it "
            "seems to move more slowly. "
            "When this happens, it has far more time to react and dodge even the quickest attacks."
        ),
    },
    {
        "head": "Moving Circles",
        "body": (
            "The skill of Moving Circles helps a cat to keep fighting while staying in "
            "constant motion. "
            "This skill gives a cat in the city the ability to circle its enemies continuously, "
            "making it almost impossible to predict where it will move next. "
            "A cat that never stands still is far harder to surround, so even several enemies "
            "at once can be dealt with."
        ),
    },
    {
        "head": "Shadow-Walking",
        "body": (
            "The skill of Shadow-Walking helps a cat to move through the city without being seen. "
            "This skill teaches a cat in the city to stay completely silent and use the cover "
            "of shadows to travel undetected. "
            "By moving in this way, it can avoid confrontation entirely and pass through even "
            "the most dangerous streets safely."
        ),
    },
    {
        "head": "Trust Yourself",
        "body": (
            "The skill of Trust Yourself helps a cat to believe in its own abilities, "
            "even when fear takes hold. "
            "This skill gives a cat in the city the confidence to rely on its instincts "
            "and trust the training it has received. "
            "It is the most challenging skill of all, which is why a cat that has truly "
            "found it can face any danger and make the right decisions."
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
