"""
build_hl_pdf.py — WFA Home Learning standard PDF builder (A5, 2 pages)
Page 1: Maths (10x10 grid + 5 questions)
Page 2: Reading (passage + 4 questions with icons)

Edit WEEK_REF, maths questions and reading content each week, then run:
    python3 /home/claude/build_hl_pdf.py

Both pages must print OK (not OVERFLOW).
"""

import sys
import os
sys.path.insert(0, '/home/claude')

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

W, H = A5          # 419.53 x 595.28 pt
M    = 10 * mm     # margin
UW   = W - 2 * M  # usable width ≈ 363pt

ICO_SIZE = 8 * mm
ICO_GAP  = 2 * mm
Q_W      = UW - ICO_SIZE - ICO_GAP
GW = GH  = 185     # grid image size in points

# Colours
NAVY   = (14/255, 40/255, 65/255)
BLUE   = (0.18, 0.38, 0.68)
BLACK  = (0, 0, 0)
GREY   = (0.55, 0.55, 0.55)
LGREY  = (0.88, 0.88, 0.88)

WEEK_REF = 'TxWy'   # <<< UPDATE EACH WEEK

# Icon paths
ICO_RET = '/home/claude/ico_ret.png'
ICO_VOC = '/home/claude/ico_voc.png'
ICO_INF = '/home/claude/ico_inf.png'


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def heading(c, x, y, text, size=9):
    """Draw a section heading. Returns y below baseline."""
    c.setFont('Helvetica-Bold', size)
    c.setFillColorRGB(*NAVY)
    bl = y - size * 0.85
    c.drawString(x, bl, text)
    return bl - size * 0.15


def rule(c, y, col=LGREY, lw=0.5):
    c.setStrokeColorRGB(*col)
    c.setLineWidth(lw)
    c.line(M, y, M + UW, y)


def answer_lines(c, top_y, n_lines, gap=7*mm):
    """Draw n_lines answer lines starting at top_y. Returns y below last line."""
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.5)
    y = top_y
    for _ in range(n_lines):
        c.line(M, y, M + UW, y)
        y -= gap
    return y


def question_block(c, top_y, icon_path, q_text, n_ans_lines):
    """
    Draw one reading question with icon + text + answer lines.
    Returns y below the last answer line.
    """
    # Question text (wraps if needed)
    lines = simpleSplit(q_text, 'Helvetica-Bold', 10, Q_W)
    q_text_h = len(lines) * 10 * 1.30
    q_top = top_y

    # Icon — centred vertically against question text
    ico_top = q_top - (q_text_h / 2) + (ICO_SIZE / 2)
    try:
        c.drawImage(icon_path, M, ico_top - ICO_SIZE,
                    width=ICO_SIZE, height=ICO_SIZE,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        pass  # graceful if icon missing

    # Question text
    c.setFont('Helvetica-Bold', 10)
    c.setFillColorRGB(*BLACK)
    tx_x = M + ICO_SIZE + ICO_GAP
    bl = q_top - 10 * 0.85
    for line in lines:
        c.drawString(tx_x, bl, line)
        bl -= 10 * 1.30

    content_bottom = min(ico_top - ICO_SIZE, q_top - q_text_h)
    content_bottom -= 2 * mm

    # Answer lines
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.5)
    y = content_bottom
    for _ in range(n_ans_lines):
        c.line(M, y, M + UW, y)
        y -= 7 * mm

    return y - 2 * mm


# ─── PAGE 1: MATHS ───────────────────────────────────────────────────────────

def build_maths_page(c):
    c.setPageSize(A5)
    cy = H - M

    # Header
    cy = heading(c, M, cy, f'Maths  —  {WEEK_REF}', size=10)
    cy -= 3 * mm

    # Grid image (if it exists)
    grid_path = '/home/claude/grid_a5.png'
    if os.path.exists(grid_path):
        c.drawImage(grid_path, M, cy - GH, width=GW, height=GH,
                    preserveAspectRatio=True, mask='auto')
        cy -= GH + 4 * mm
    else:
        # Placeholder box if no grid generated
        c.setStrokeColorRGB(*LGREY)
        c.setLineWidth(0.5)
        c.rect(M, cy - 80, GW, 80)
        c.setFont('Helvetica-Oblique', 8)
        c.setFillColorRGB(*GREY)
        c.drawString(M + 4, cy - 44, '[run grid_gen.py first]')
        cy -= 84 + 4 * mm

    # ~~~ MATHS QUESTIONS: REPLACE BELOW EACH WEEK ~~~
    maths_qs = [
        # (question_text, n_answer_lines)
        ('Q1. [Question using grid]', 2),
        ('Q2. [Question using grid]', 2),
        ('Q3. [Question using grid]', 2),
        ('Q4. [Second skill question — no grid]', 3),
        ('Q5. [Problem solving or misconception challenge]', 3),
    ]
    # ~~~ END MATHS QUESTIONS ~~~

    for i, (q, n) in enumerate(maths_qs):
        c.setFont('Helvetica-Bold', 9)
        c.setFillColorRGB(*NAVY)
        bl = cy - 9 * 0.85
        c.drawString(M, bl, q)
        cy = bl - 9 * 0.15 - 2 * mm
        c.setStrokeColorRGB(*GREY)
        c.setLineWidth(0.5)
        for _ in range(n):
            c.line(M, cy, M + UW, cy)
            cy -= 7 * mm
        cy -= 2 * mm

    status = 'OK' if cy > M else 'OVERFLOW'
    print(f'Maths page bottom: {cy:.0f}pt  margin: {M:.0f}pt  {status}')
    c.showPage()


# ─── PAGE 2: READING ─────────────────────────────────────────────────────────

def build_reading_page(c):
    c.setPageSize(A5)
    cy = H - M

    # Header
    cy = heading(c, M, cy, f'Reading  —  {WEEK_REF}', size=10)
    cy -= 3 * mm

    # ~~~ READING CONTENT: REPLACE BELOW EACH WEEK ~~~
    passage = (
        '[Reading passage: 170–190 words, single flowing paragraph, narrative '
        'prose. Replace this placeholder with the week\'s passage. Must be a '
        'single string with no embedded newlines. Use \\u2019 for apostrophes '
        'and \\u201c \\u201d for speech marks.]'
    )

    questions = [
        # (icon_path, question_text, n_answer_lines)
        (ICO_RET, 'Q1. [Retrieval question — factual, directly stated in the text.]', 2),
        (ICO_RET, 'Q2. [Retrieval question — factual, directly stated in the text.]', 2),
        (ICO_VOC, 'Q3. Find and copy a word that means [definition].', 2),
        (ICO_INF, 'Q4. [Inference question — use clues from the text to explain.]', 3),
    ]
    # ~~~ END READING CONTENT ~~~

    # Passage
    c.setFont('Helvetica-Oblique', 11)
    c.setFillColorRGB(*BLACK)
    lines = simpleSplit(passage, 'Helvetica-Oblique', 11, UW)
    for line in lines:
        bl = cy - 11 * 0.85
        c.drawString(M, bl, line)
        cy = bl - 11 * 0.15 - 11 * 0.25   # 1.25 leading

    cy -= 3 * mm
    rule(c, cy)
    cy -= 3 * mm

    # Questions
    for icon, q_text, n_lines in questions:
        cy = question_block(c, cy, icon, q_text, n_lines)

    status = 'OK' if cy > M else 'OVERFLOW'
    print(f'Reading page bottom: {cy:.0f}pt  margin: {M:.0f}pt  {status}')
    c.showPage()


# ─── FITTING CHECK (run before building) ─────────────────────────────────────

def check_fit(passage, questions):
    """
    Quick pre-check. Call this with your actual content before building.
    Returns True if both pages will fit.
    """
    # Reading page check
    plines = simpleSplit(passage, 'Helvetica-Oblique', 11, UW)
    total = len(plines) * 11 * 1.25 + 3 * mm  # passage
    total += 3 * mm  # rule gap
    for _, q, n in questions:
        qlines = simpleSplit(q, 'Helvetica-Bold', 10, Q_W)
        total += len(qlines) * 10 * 1.30 + 2 * mm + n * 7 * mm + 2 * mm
    avail = H - 2 * M - 10 * 0.85 - 0.15 - 3 * mm  # below heading
    fit = total < avail
    print(f'Reading fit check: {total:.0f} / {avail:.0f}pt  {"OK" if fit else "OVERFLOW"}')
    return fit


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    out = f'/home/claude/HL_{WEEK_REF}.pdf'
    c = canvas.Canvas(out, pagesize=A5)
    build_maths_page(c)
    build_reading_page(c)
    c.save()
    print(f'Saved {out}')
