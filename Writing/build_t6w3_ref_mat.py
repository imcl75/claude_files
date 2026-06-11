"""
T6W3 Explanation Text Reference Mat — A4 portrait desk card.
Sections: causal connectives | fronted adverbials | useful verbs | register check + structure reminder.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Reference_Mat.pdf'
PAGE_W, PAGE_H = A4
MARGIN = 1.0 * cm

BLUE   = HexColor('#1798d3')
DBLUE  = HexColor('#154360')
LBLUE  = HexColor('#D6EAF8')
MID    = HexColor('#2980B9')
GREEN  = HexColor('#1E8449')
LGREEN = HexColor('#D5F5E3')
AMBER  = HexColor('#B7770D')
LAMBER = HexColor('#FEF9E7')
LGREY  = HexColor('#F5F5F5')
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

bar_h = 0.85 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 11)
c.drawString(MARGIN, PAGE_H - bar_h + 0.24*cm, "Explanation Text Reference Mat")
c.setFont('Helvetica', 9)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.24*cm,
                  "T6W3  |  Being a Writer  |  Year 4")

foot_h = 0.38 * cm
c.setFillColor(BLUE)
c.rect(0, 0, PAGE_W, foot_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica', 7)
c.drawCentredString(PAGE_W/2, 0.12*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

CT = PAGE_H - bar_h - 0.28*cm
CB = foot_h + 0.18*cm
CW = PAGE_W - 2*MARGIN
CX = MARGIN
GAP   = 0.30*cm
BAND  = 0.60*cm
COLG  = 0.38*cm
COL_W = (CW - COLG) / 2
LX    = CX
RX    = CX + COL_W + COLG

# ── Section 1: Connectives (two columns) ────────────────────────────
conn = [
    ("therefore",      "The cat kept moving; therefore, enemies could not surround it."),
    ("so",             "Danger appeared, so the cat used Slow-Time immediately."),
    ("which means",    "It focused completely, which means danger seemed to slow down."),
    ("which is why",   "Trust comes from inside, which is why this skill is the hardest."),
    ("and as a result","It stayed alert, and as a result it spotted the enemy first."),
]
fron = [
    ("As a result,",      "As a result, the cat spotted danger before it arrived."),
    ("Due to this,",      "Due to this, enemies struggled to track its movements."),
    ("Because of this,",  "Because of this, the cat reached safety undetected."),
    ("By [doing this],",  "By calming the mind, everything seemed to move more slowly."),
    ("When this happens,","When this happens, the cat has more time to react."),
    ("In this way,",      "In this way, the cat escapes without being seen."),
]

ENTRY = 1.22*cm
PAD   = 0.18*cm
rows  = max(len(conn), len(fron))
body1 = rows * ENTRY + PAD
SEC1  = BAND + body1

cy = CT
# Bands
for bx, bc, label in [
    (LX, MID,   "Causal connectives  \u2014  use mid-sentence"),
    (RX, GREEN, "Fronted adverbials  \u2014  use to start a sentence"),
]:
    c.setFillColor(bc)
    c.rect(bx, cy-BAND, COL_W, BAND, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(bx+0.22*cm, cy-BAND*0.68, label)

cy -= BAND
# Bodies
for bx, bf in [(LX, LBLUE), (RX, LGREEN)]:
    c.setFillColor(bf)
    c.setStrokeColor(MGREY)
    c.setLineWidth(0.3)
    c.rect(bx, cy-body1, COL_W, body1, fill=1, stroke=1)

def col_entries(entries, bx, top, accent):
    ey = top - PAD
    for word, ex in entries:
        c.setFillColor(accent)
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(bx+PAD, ey-0.26*cm, word)
        c.setFillColor(DGREY)
        c.setFont('Helvetica-Oblique', 7.2)
        for li, ln in enumerate(wrap(ex, 'Helvetica-Oblique', 7.2, COL_W-PAD*2)[:2]):
            c.drawString(bx+PAD+0.10*cm, ey-0.54*cm-li*0.27*cm, ln)
        ey -= ENTRY
        if ey > top-body1+0.05*cm:
            c.setStrokeColor(MGREY); c.setLineWidth(0.22)
            c.line(bx+PAD, ey+0.06*cm, bx+COL_W-PAD, ey+0.06*cm)

col_entries(conn, LX, cy, MID)
col_entries(fron, RX, cy, GREEN)
cy -= body1 + GAP

# ── Section 2: Useful verbs ──────────────────────────────────────────
verbs = [
    ("allows",     "Slow-Time allows a cat to react more quickly."),
    ("enables",    "This enables the cat to dodge attacks."),
    ("prevents",   "Moving Circles prevents encirclement."),
    ("requires",   "Hunting requires patience and silence."),
    ("results in", "Open Mind results in better decisions."),
    ("leads to",   "Awareness leads to earlier warnings of danger."),
    ("helps",      "Trust Yourself helps every other skill work."),
    ("means that", "This means that danger seems to move more slowly."),
    ("keeps",      "This keeps the cat one step ahead of its enemies."),
]
N_VC    = 3
vc_w    = CW / N_VC
v_rows  = (len(verbs) + N_VC - 1) // N_VC
vbody   = v_rows * 0.70*cm + 0.22*cm
SEC2    = BAND + vbody

c.setFillColor(AMBER)
c.rect(CX, cy-BAND, CW, BAND, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 8.5)
c.drawString(CX+0.22*cm, cy-BAND*0.68, "Useful verbs for explanation")
cy -= BAND

c.setFillColor(LAMBER)
c.setStrokeColor(MGREY); c.setLineWidth(0.3)
c.rect(CX, cy-vbody, CW, vbody, fill=1, stroke=1)

vy0 = cy - 0.26*cm
for i, (verb, ex) in enumerate(verbs):
    col = i % N_VC
    row = i // N_VC
    vx  = CX + 0.18*cm + col*vc_w
    vy  = vy0 - row*0.70*cm
    c.setFillColor(AMBER); c.setFont('Helvetica-Bold', 8.2)
    c.drawString(vx, vy, verb)
    c.setFillColor(DGREY); c.setFont('Helvetica-Oblique', 7.0)
    exs = ex
    while exs and stringWidth(exs, 'Helvetica-Oblique', 7.0) > vc_w-0.32*cm:
        exs = exs.rsplit(' ',1)[0]
    if exs != ex: exs += '\u2026'
    c.drawString(vx, vy-0.27*cm, exs)

cy -= vbody + GAP

# ── Sections 3 & 4: Register check (left) | Structure reminder (right) ─
remaining = cy - CB
HW = (CW - COLG) / 2   # half width

# --- 3: Register check ---
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
# Band
c.setFillColor(DBLUE)
c.rect(LX, cy-BAND, HW, BAND, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 8.5)
c.drawString(LX+0.22*cm, cy-BAND*0.68,
             "Register check  \u2014  explanation or instructions?")

rc_top = cy - BAND
rc_body = remaining - BAND
half_rc = HW / 2

# Green sub-box
SUBB = 0.50*cm
c.setFillColor(LGREEN); c.setStrokeColor(GREEN); c.setLineWidth(0.4)
c.rect(LX, rc_top-rc_body, half_rc, rc_body, fill=1, stroke=1)
c.setFillColor(GREEN)
c.rect(LX, rc_top-SUBB, half_rc, SUBB, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 7.5)
c.drawString(LX+0.18*cm, rc_top-SUBB*0.70, "\u2713  Explanation")

# Red sub-box
c.setFillColor(LRED); c.setStrokeColor(RED); c.setLineWidth(0.4)
c.rect(LX+half_rc, rc_top-rc_body, half_rc, rc_body, fill=1, stroke=1)
c.setFillColor(RED)
c.rect(LX+half_rc, rc_top-SUBB, half_rc, SUBB, fill=1, stroke=0)
c.setFillColor(white)
c.drawString(LX+half_rc+0.18*cm, rc_top-SUBB*0.70, "\u2717  Instructions  \u2014  avoid")

ex_row_h = (rc_body - SUBB - 0.10*cm) / len(rc_examples)
for gi, (good, bad) in enumerate(rc_examples):
    gy = rc_top - SUBB - 0.26*cm - gi*ex_row_h
    for col_x, text, color in [
        (LX,         good, GREEN),
        (LX+half_rc, bad,  RED),
    ]:
        c.setFillColor(color); c.setFont('Helvetica-Oblique', 7.2)
        for li, ln in enumerate(wrap(text, 'Helvetica-Oblique', 7.2, half_rc-0.32*cm)[:2]):
            c.drawString(col_x+0.18*cm, gy-li*0.26*cm, ln)

# --- 4: Structure reminder ---
c.setFillColor(PURPLE)
c.rect(RX, cy-BAND, HW, BAND, fill=1, stroke=0)
c.setFillColor(white); c.setFont('Helvetica-Bold', 8.5)
c.drawString(RX+0.22*cm, cy-BAND*0.68,
             "Structure of each skill section")

sr_top  = cy - BAND
sr_body = remaining - BAND
c.setFillColor(LPURP); c.setStrokeColor(PURPLE); c.setLineWidth(0.4)
c.rect(RX, sr_top-sr_body, HW, sr_body, fill=1, stroke=1)

parts = [
    ("1  Subheading", "One word: the name of the skill.",
     "e.g.  Open Mind"),
    ("2  What it is", "A sentence explaining what the skill involves.",
     "e.g.  Open Mind is the ability to change your approach\n       when things do not go as planned."),
    ("3  How it works", "Explain the process using a fronted adverbial.",
     "e.g.  By looking at problems in different ways,\n       a cat can find solutions others would miss."),
    ("4  What happens as a result", "Use a causal connective to show the outcome.",
     "e.g.  As a result, the cat avoids danger\n       and stays one step ahead."),
]

py = sr_top - 0.26*cm
for label, desc, ex in parts:
    c.setFillColor(PURPLE); c.setFont('Helvetica-Bold', 8.0)
    c.drawString(RX+0.22*cm, py, label)
    c.setFillColor(DGREY); c.setFont('Helvetica', 7.4)
    c.drawString(RX+0.22*cm, py-0.28*cm, desc)
    c.setFillColor(HexColor('#555555')); c.setFont('Helvetica-Oblique', 7.0)
    for li, ln in enumerate(ex.split('\n')):
        c.drawString(RX+0.32*cm, py-0.52*cm-li*0.24*cm, ln)
    py -= 1.90*cm
    if py < sr_top - sr_body + 0.1*cm:
        break

c.save()
print(f"Saved: {OUT}")
