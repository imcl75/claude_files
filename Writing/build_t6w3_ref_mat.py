"""
T6W3 Explanation Text Reference Mat — A4 portrait.
14pt keywords, 12pt examples. Page nearly full.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Reference_Mat.pdf'
PAGE_W, PAGE_H = A4
MG = 1.0 * cm

BLUE   = HexColor('#1798d3')
DBLUE  = HexColor('#154360')
LBLUE  = HexColor('#D6EAF8')
MID    = HexColor('#2980B9')
GREEN  = HexColor('#1E8449')
LGREEN = HexColor('#D5F5E3')
AMBER  = HexColor('#B7770D')
LAMBER = HexColor('#FEF9E7')
MGREY  = HexColor('#CCCCCC')
DGREY  = HexColor('#2C2C2C')
RED    = HexColor('#922B21')
LRED   = HexColor('#FADBD8')
PURPLE = HexColor('#6C3483')
LPURP  = HexColor('#F5EEF8')

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
c.setTitle("T6W3 Explanation Text Reference Mat")

# Header
BAR = 1.0 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H-BAR, PAGE_W, BAR, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 13)
c.drawString(MG, PAGE_H-BAR+0.28*cm, "Explanation Text Reference Mat")
c.setFont('Helvetica', 10)
c.drawRightString(PAGE_W-MG, PAGE_H-BAR+0.28*cm, "T6W3  |  Being a Writer  |  Year 4")

# Footer
FOOT = 0.45 * cm
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, FOOT, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica', 8)
c.drawCentredString(PAGE_W/2, 0.14*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

CW   = PAGE_W - 2*MG
CX   = MG
cy   = PAGE_H - BAR - 0.32*cm
BAND = 0.72 * cm
GAP  = 0.45 * cm
COLG = 0.40 * cm
HW   = (CW - COLG) / 2

# ── Section 1: connectives ────────────────────────────────────────────
conn = [
    ("therefore",       "The cat kept moving; therefore, enemies could not surround it."),
    ("so",              "Danger appeared, so the cat used Slow-Time immediately."),
    ("which means",     "It focused completely, which means danger seemed to slow down."),
    ("which is why",    "Trust comes from inside, which is why this skill is the hardest."),
    ("and as a result", "It stayed alert, and as a result it spotted the enemy first."),
]
fron = [
    ("As a result,",       "As a result, the cat spotted danger before it arrived."),
    ("Due to this,",       "Due to this, enemies struggled to track its movements."),
    ("Because of this,",   "Because of this, the cat reached safety undetected."),
    ("By [doing this],",   "By calming the mind, everything seemed to move more slowly."),
    ("When this happens,", "When this happens, the cat has more time to react."),
    ("In this way,",       "In this way, the cat escapes without being seen."),
]

ENTRY = 1.80 * cm
PAD   = 0.18 * cm
body1 = max(len(conn), len(fron)) * ENTRY + PAD
LX = CX
RX = CX + HW + COLG

for bx, bc, lbl in [
    (LX, MID,   "Causal connectives  \u2014  use mid-sentence"),
    (RX, GREEN, "Fronted adverbials  \u2014  use to start a sentence"),
]:
    c.setFillColor(bc)
    c.rect(bx, cy-BAND, HW, BAND, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(bx+0.26*cm, cy-BAND*0.68, lbl)

cy -= BAND

for bx, bf in [(LX, LBLUE), (RX, LGREEN)]:
    c.setFillColor(bf)
    c.setStrokeColor(MGREY); c.setLineWidth(0.35)
    c.rect(bx, cy-body1, HW, body1, fill=1, stroke=1)

def col_entries(entries, bx, top, accent):
    ey = top - PAD
    for word, ex in entries:
        c.setFillColor(accent)
        c.setFont('Helvetica-Bold', 13)
        c.drawString(bx+0.26*cm, ey-0.32*cm, word)
        c.setFillColor(DGREY)
        c.setFont('Helvetica-Oblique', 11)
        for li, ln in enumerate(wrap(ex, 'Helvetica-Oblique', 11, HW-0.48*cm)[:2]):
            c.drawString(bx+0.38*cm, ey-0.68*cm-li*0.38*cm, ln)
        ey -= ENTRY
        if ey > top-body1+0.08*cm:
            c.setStrokeColor(MGREY); c.setLineWidth(0.28)
            c.line(bx+0.26*cm, ey+0.08*cm, bx+HW-0.26*cm, ey+0.08*cm)

col_entries(conn, LX, cy, MID)
col_entries(fron, RX, cy, GREEN)
cy -= body1 + GAP

# ── Section 2: verbs ──────────────────────────────────────────────────
verbs = [
    ("allows",     "allows a cat to pass unseen"),
    ("enables",    "enables the cat to react faster"),
    ("prevents",   "prevents enemies surrounding it"),
    ("requires",   "requires patience and silence"),
    ("results in", "results in better decisions"),
    ("leads to",   "leads to earlier warnings"),
    ("helps",      "helps every other skill work"),
    ("means that", "means that danger seems slower"),
    ("keeps",      "keeps the cat one step ahead"),
]
N_VC   = 3
vcw    = CW / N_VC
v_rows = (len(verbs) + N_VC - 1) // N_VC
vbody  = v_rows * 1.10*cm + 0.22*cm

c.setFillColor(AMBER)
c.rect(CX, cy-BAND, CW, BAND, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 10)
c.drawString(CX+0.26*cm, cy-BAND*0.68, "Useful verbs for explanation")
cy -= BAND

c.setFillColor(LAMBER); c.setStrokeColor(MGREY); c.setLineWidth(0.35)
c.rect(CX, cy-vbody, CW, vbody, fill=1, stroke=1)

vy0 = cy - 0.28*cm
for i, (verb, ex) in enumerate(verbs):
    col = i % N_VC; row = i // N_VC
    vx  = CX + 0.24*cm + col*vcw
    vy  = vy0 - row*1.10*cm
    c.setFillColor(AMBER); c.setFont('Helvetica-Bold', 13)
    c.drawString(vx, vy, verb)
    c.setFillColor(DGREY); c.setFont('Helvetica-Oblique', 11)
    exs = ex
    while exs and stringWidth(exs, 'Helvetica-Oblique', 11) > vcw-0.40*cm:
        exs = exs.rsplit(' ', 1)[0]
    if exs != ex: exs += '\u2026'
    c.drawString(vx, vy-0.34*cm, exs)

cy -= vbody + GAP

# ── Sections 3 & 4: register + structure, content-height ─────────────
SUBB = 0.58 * cm

rc_examples = [
    ("\u201cSlow-Time allows a cat to slow its reactions.\u201d",
     "\u201cYou should calm your mind and focus.\u201d"),
    ("\u201cThis skill enables the cat to dodge attacks.\u201d",
     "\u201cNext, move quietly through the shadows.\u201d"),
    ("\u201cAwareness leads to earlier warnings of danger.\u201d",
     "\u201cAlways pay attention to your surroundings.\u201d"),
    ("\u201cBy staying silent, the cat travels unnoticed.\u201d",
     "\u201cRemember to trust yourself at all times.\u201d"),
]
RC_EX_H = 1.80 * cm
rc_body  = SUBB + len(rc_examples)*RC_EX_H + 0.18*cm

sr_parts = [
    ("1  Subheading",
     "One word: the name of the skill.",
     "e.g.  Open Mind"),
    ("2  What it is",
     "A sentence explaining what the skill involves.",
     "e.g.  Open Mind is the ability to change your\n       approach when things do not go as planned."),
    ("3  How it works",
     "Explain the process using a fronted adverbial.",
     "e.g.  By looking at problems in different ways,\n       a cat can find solutions others would miss."),
    ("4  What happens as a result",
     "Use a causal connective to show the outcome.",
     "e.g.  As a result, the cat avoids danger\n       and stays one step ahead."),
]
SR_STEP_H = 2.20 * cm
sr_body   = SUBB + 0.15*cm + len(sr_parts)*SR_STEP_H + 0.18*cm

SEC34_BODY = max(rc_body, sr_body)

# Bands
c.setFillColor(DBLUE)
c.rect(LX, cy-BAND, HW, BAND, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 10)
c.drawString(LX+0.26*cm, cy-BAND*0.68, "Explanation or instructions?")

c.setFillColor(PURPLE)
c.rect(RX, cy-BAND, HW, BAND, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 10)
c.drawString(RX+0.26*cm, cy-BAND*0.68, "Structure of each skill section")

cy -= BAND
half_rc = HW / 2

# Register boxes
for bx2, bf2, bc2, lbl2 in [
    (LX,          LGREEN, GREEN, "\u2713  Explanation"),
    (LX+half_rc,  LRED,   RED,   "\u2717  Instructions  \u2014  avoid"),
]:
    c.setFillColor(bf2); c.setStrokeColor(bc2); c.setLineWidth(0.5)
    c.rect(bx2, cy-SEC34_BODY, half_rc, SEC34_BODY, fill=1, stroke=1)
    c.setFillColor(bc2)
    c.rect(bx2, cy-SUBB, half_rc, SUBB, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 10)
    c.drawString(bx2+0.20*cm, cy-SUBB*0.70, lbl2)

ey = cy - SUBB - 0.26*cm
for good, bad in rc_examples:
    for col_x, text, col in [(LX, good, GREEN), (LX+half_rc, bad, RED)]:
        c.setFillColor(col); c.setFont('Helvetica-Oblique', 11)
        for li, ln in enumerate(wrap(text, 'Helvetica-Oblique', 11, half_rc-0.36*cm)[:2]):
            c.drawString(col_x+0.20*cm, ey-li*0.38*cm, ln)
    ey -= RC_EX_H

# Structure box
c.setFillColor(LPURP); c.setStrokeColor(PURPLE); c.setLineWidth(0.5)
c.rect(RX, cy-SEC34_BODY, HW, SEC34_BODY, fill=1, stroke=1)

# Top clearance: align with register content start (after SUBB)
py = cy - SUBB - 0.15*cm
for label, desc, ex in sr_parts:
    c.setFillColor(PURPLE); c.setFont('Helvetica-Bold', 13)
    c.drawString(RX+0.26*cm, py, label)
    c.setFillColor(DGREY); c.setFont('Helvetica', 11)
    c.drawString(RX+0.26*cm, py-0.38*cm, desc)
    c.setFillColor(HexColor('#555555')); c.setFont('Helvetica-Oblique', 10)
    for li, ln in enumerate(ex.split('\n')):
        c.drawString(RX+0.38*cm, py-0.72*cm-li*0.33*cm, ln)
    py -= SR_STEP_H

c.save()
used = (PAGE_H - BAR - 0.32*cm) - (cy - SEC34_BODY)
total = PAGE_H - BAR - 0.32*cm - FOOT - 0.18*cm
print(f"Saved: {OUT}")
print(f"Content: {used/28.35:.1f}cm of {total/28.35:.1f}cm — {27.9-(used/28.35):.1f}cm blank at bottom")
