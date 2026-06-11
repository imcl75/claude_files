"""
T6W3 Explanation Text Reference Mat.
A4 landscape — two A5 portrait instances side by side, cut to share.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W3_Reference_Mat.pdf'

PW, PH = landscape(A4)   # 841.9 × 595.3 pt

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

c = canvas.Canvas(OUT, pagesize=landscape(A4))
c.setTitle("T6W3 Explanation Text Reference Mat")

# ── Cut line down centre ──────────────────────────────────────────────
c.setStrokeColor(MGREY)
c.setLineWidth(0.5)
c.setDash(4, 4)
c.line(PW/2, 0, PW/2, PH)
c.setDash()

# ── Draw one A5 unit ─────────────────────────────────────────────────
def draw_unit(ox):
    """ox = x-offset for this A5 unit (0 or PW/2)"""
    UW  = PW / 2       # unit width  ≈ 420.9 pt ≈ 14.84 cm
    UH  = PH           # unit height ≈ 595.3 pt ≈ 21.0 cm
    mg  = 0.72 * cm
    cw  = UW - 2*mg    # content width
    cx  = ox + mg
    
    bar_h  = 0.78 * cm
    foot_h = 0.34 * cm
    CT = UH - bar_h - 0.24*cm
    CB = foot_h + 0.16*cm

    # Header
    c.setFillColor(BLUE)
    c.rect(ox, UH-bar_h, UW, bar_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(cx, UH-bar_h+0.20*cm, "Explanation Text Reference Mat")
    c.setFont('Helvetica', 7.5)
    c.drawRightString(ox+UW-mg, UH-bar_h+0.20*cm, "T6W3  |  Y4")

    # Footer
    c.setFillColor(BLUE)
    c.rect(ox, 0, UW, foot_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica', 6)
    c.drawCentredString(ox+UW/2, 0.10*cm, "Wallscourt Farm Academy  |  Year 4  |  Term 6")

    BAND  = 0.54*cm
    GAP   = 0.24*cm
    COLG  = 0.30*cm
    HCW   = (cw - COLG) / 2   # half content width
    LX    = cx
    RX    = cx + HCW + COLG

    # ── Section 1: Connectives ────────────────────────────────────────
    conn = [
        ("therefore",       "The cat kept moving; therefore, enemies could not surround it."),
        ("so",              "Danger appeared, so the cat used Slow-Time immediately."),
        ("which means",     "It focused completely, which means danger seemed to slow down."),
        ("which is why",    "Trust comes from inside, which is why this is the hardest skill."),
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

    ENTRY  = 1.08*cm
    PAD    = 0.14*cm
    n_rows = max(len(conn), len(fron))
    body1  = n_rows * ENTRY + PAD

    cy = CT
    # Bands
    for bx, bc, lbl in [
        (LX, MID,   "Causal connectives  \u2014  use mid-sentence"),
        (RX, GREEN, "Fronted adverbials  \u2014  use to start a sentence"),
    ]:
        c.setFillColor(bc)
        c.rect(bx, cy-BAND, HCW, BAND, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 7.5)
        c.drawString(bx+0.18*cm, cy-BAND*0.70, lbl)

    cy -= BAND
    for bx, bf in [(LX, LBLUE), (RX, LGREEN)]:
        c.setFillColor(bf)
        c.setStrokeColor(MGREY); c.setLineWidth(0.3)
        c.rect(bx, cy-body1, HCW, body1, fill=1, stroke=1)

    def col_entries(entries, bx, top, accent):
        ey = top - PAD
        for word, ex in entries:
            c.setFillColor(accent); c.setFont('Helvetica-Bold', 7.8)
            c.drawString(bx+PAD, ey-0.24*cm, word)
            c.setFillColor(DGREY); c.setFont('Helvetica-Oblique', 6.5)
            for li, ln in enumerate(wrap(ex,'Helvetica-Oblique',6.5,HCW-PAD*2)[:2]):
                c.drawString(bx+PAD+0.08*cm, ey-0.48*cm-li*0.24*cm, ln)
            ey -= ENTRY
            if ey > top-body1+0.04*cm:
                c.setStrokeColor(MGREY); c.setLineWidth(0.2)
                c.line(bx+PAD, ey+0.05*cm, bx+HCW-PAD, ey+0.05*cm)

    col_entries(conn, LX, cy, MID)
    col_entries(fron, RX, cy, GREEN)
    cy -= body1 + GAP

    # ── Section 2: Useful verbs ───────────────────────────────────────
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
    vcw    = cw / N_VC
    v_rows = (len(verbs) + N_VC - 1) // N_VC
    vbody  = v_rows * 0.64*cm + 0.18*cm

    c.setFillColor(AMBER)
    c.rect(cx, cy-BAND, cw, BAND, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 7.5)
    c.drawString(cx+0.18*cm, cy-BAND*0.70, "Useful verbs for explanation")
    cy -= BAND

    c.setFillColor(LAMBER); c.setStrokeColor(MGREY); c.setLineWidth(0.3)
    c.rect(cx, cy-vbody, cw, vbody, fill=1, stroke=1)

    vy0 = cy - 0.22*cm
    for i, (verb, ex) in enumerate(verbs):
        col = i % N_VC; row = i // N_VC
        vx  = cx + 0.14*cm + col*vcw
        vy  = vy0 - row*0.64*cm
        c.setFillColor(AMBER); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(vx, vy, verb)
        c.setFillColor(DGREY); c.setFont('Helvetica-Oblique', 6.5)
        exs = ex
        while exs and stringWidth(exs,'Helvetica-Oblique',6.5) > vcw-0.28*cm:
            exs = exs.rsplit(' ',1)[0]
        if exs != ex: exs += '\u2026'
        c.drawString(vx, vy-0.25*cm, exs)

    cy -= vbody + GAP

    # ── Sections 3 & 4: Register / Structure ─────────────────────────
    remaining = cy - CB
    SUBB = 0.46*cm

    # -- Register check (left) --
    c.setFillColor(DBLUE)
    c.rect(LX, cy-BAND, HCW, BAND, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 7.0)
    c.drawString(LX+0.18*cm, cy-BAND*0.70,
                 "Which sounds like explanation?")
    # Second line of header (tight)
    c.setFont('Helvetica', 6.5)
    c.drawString(LX+0.18*cm, cy-BAND*0.70-0.26*cm,
                 "Which sounds like instructions?")

    rc_top  = cy - BAND
    rc_body = remaining - BAND
    half_rc = HCW / 2

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

    for bx2, bf2, bc2, sub_lbl in [
        (LX,           LGREEN, GREEN, "\u2713  Explanation"),
        (LX+half_rc,   LRED,   RED,   "\u2717  Instructions \u2014 avoid"),
    ]:
        c.setFillColor(bf2); c.setStrokeColor(bc2); c.setLineWidth(0.4)
        c.rect(bx2, rc_top-rc_body, half_rc, rc_body, fill=1, stroke=1)
        c.setFillColor(bc2)
        c.rect(bx2, rc_top-SUBB, half_rc, SUBB, fill=1, stroke=0)
        c.setFillColor(white); c.setFont('Helvetica-Bold', 7.0)
        c.drawString(bx2+0.15*cm, rc_top-SUBB*0.72, sub_lbl)

    ex_row_h = (rc_body - SUBB - 0.08*cm) / len(rc_examples)
    for gi, (good, bad) in enumerate(rc_examples):
        gy = rc_top - SUBB - 0.24*cm - gi*ex_row_h
        for col_x, text, col in [(LX, good, GREEN), (LX+half_rc, bad, RED)]:
            c.setFillColor(col); c.setFont('Helvetica-Oblique', 6.8)
            for li, ln in enumerate(wrap(text,'Helvetica-Oblique',6.8,half_rc-0.28*cm)[:2]):
                c.drawString(col_x+0.15*cm, gy-li*0.24*cm, ln)

    # -- Structure reminder (right) --
    c.setFillColor(PURPLE)
    c.rect(RX, cy-BAND, HCW, BAND, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 7.5)
    c.drawString(RX+0.18*cm, cy-BAND*0.70, "Structure of each skill section")

    sr_top  = cy - BAND
    sr_body = remaining - BAND
    c.setFillColor(LPURP); c.setStrokeColor(PURPLE); c.setLineWidth(0.4)
    c.rect(RX, sr_top-sr_body, HCW, sr_body, fill=1, stroke=1)

    parts = [
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

    py = sr_top - 0.22*cm
    step_h = sr_body / len(parts)
    for label, desc, ex in parts:
        c.setFillColor(PURPLE); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(RX+0.18*cm, py, label)
        c.setFillColor(DGREY); c.setFont('Helvetica', 7.0)
        c.drawString(RX+0.18*cm, py-0.26*cm, desc)
        c.setFillColor(HexColor('#555555')); c.setFont('Helvetica-Oblique', 6.5)
        for li, ln in enumerate(ex.split('\n')):
            c.drawString(RX+0.28*cm, py-0.48*cm-li*0.22*cm, ln)
        py -= step_h

# Draw both units
draw_unit(0)
draw_unit(PW/2)

c.save()
print(f"Saved: {OUT}")
