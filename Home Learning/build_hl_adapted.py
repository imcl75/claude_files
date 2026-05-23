"""
build_hl_adapted.py — WFA Home Learning ADAPTED PDF builder (A5, 2 pages)
Pitched at Y1/Y2 level. Same format as standard but:
  Page 1: 6x6 grid, word bank, 4 scaffolded maths questions
  Page 2: shorter passage (~120 words), same 4 question types but simpler

Edit WEEK_REF and all content sections, then run:
    python3 /home/claude/build_hl_adapted.py

Both pages must print OK.
"""

import sys
import os
sys.path.insert(0, '/home/claude')

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

W, H = A5
M    = 10 * mm
UW   = W - 2 * M

ICO_SIZE = 8 * mm
ICO_GAP  = 2 * mm
Q_W      = UW - ICO_SIZE - ICO_GAP
GW = GH  = 185

NAVY   = (14/255, 40/255, 65/255)
BLACK  = (0, 0, 0)
GREY   = (0.55, 0.55, 0.55)
LGREY  = (0.88, 0.88, 0.88)
BLUE   = (0.18, 0.38, 0.68)

WEEK_REF = 'TxWy-Adapted'   # <<< UPDATE EACH WEEK

ICO_RET = '/home/claude/ico_ret.png'
ICO_VOC = '/home/claude/ico_voc.png'
ICO_INF = '/home/claude/ico_inf.png'


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def heading(c, x, y, text, size=10):
    c.setFont('Helvetica-Bold', size)
    c.setFillColorRGB(*NAVY)
    bl = y - size * 0.85
    c.drawString(x, bl, text)
    return bl - size * 0.15


def rule(c, y):
    c.setStrokeColorRGB(*LGREY)
    c.setLineWidth(0.5)
    c.line(M, y, M + UW, y)


def draw_options(c, top_y, opts, label_prefix=''):
    """
    Draw selectable options evenly spaced across UW.
    Used for circle-the-answer and true/false questions.
    Returns y below the options row.
    """
    slot_w = UW / len(opts)
    c.setFont('Helvetica', 10)
    c.setFillColorRGB(*BLACK)
    row_h = 14
    bl = top_y - 10 * 0.85
    for i, opt in enumerate(opts):
        x = M + i * slot_w + slot_w / 2
        c.drawCentredString(x, bl, str(opt))
        # Circle placeholder
        c.setStrokeColorRGB(*BLUE)
        c.setLineWidth(0.8)
        c.circle(x, bl + 4, 9, stroke=1, fill=0)
        c.setFillColorRGB(*BLACK)
    return top_y - row_h - 4 * mm


def answer_line(c, y, label=None):
    """Draw a single answer line with optional label. Returns y below."""
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.5)
    lx = M
    if label:
        c.setFont('Helvetica', 9)
        c.setFillColorRGB(*GREY)
        c.drawString(M, y - 9 * 0.85, label)
        lx = M + 40
    c.line(lx, y, M + UW, y)
    return y - 7 * mm


def question_block(c, top_y, icon_path, q_text, n_ans_lines):
    """Reading question with icon, text, and answer lines. Returns y below."""
    lines = simpleSplit(q_text, 'Helvetica-Bold', 10, Q_W)
    q_text_h = len(lines) * 10 * 1.30
    ico_top = top_y - (q_text_h / 2) + (ICO_SIZE / 2)
    try:
        c.drawImage(icon_path, M, ico_top - ICO_SIZE,
                    width=ICO_SIZE, height=ICO_SIZE,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        pass
    c.setFont('Helvetica-Bold', 10)
    c.setFillColorRGB(*BLACK)
    tx_x = M + ICO_SIZE + ICO_GAP
    bl = top_y - 10 * 0.85
    for line in lines:
        c.drawString(tx_x, bl, line)
        bl -= 10 * 1.30
    content_bottom = min(ico_top - ICO_SIZE, top_y - q_text_h) - 2 * mm
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.5)
    y = content_bottom
    for _ in range(n_ans_lines):
        c.line(M, y, M + UW, y)
        y -= 7 * mm
    return y - 2 * mm


def generate_adapted_grid():
    """
    Build a 6x6 grid image using grid_gen.py with GRID_SIZE=6.
    Edit the ELEMENTS list here each week, then this function generates it.
    """
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location(
        'grid_gen', '/home/claude/grid_gen.py')
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)

    # ~~~ ADAPTED GRID ELEMENTS: REPLACE EACH WEEK ~~~
    elements = [
        ('point', (1, 2), 'A', '#1a3c8e'),
        ('star',  (5, 2), 'S', '#e67e22'),
        ('arrow', (1, 5), (3, 5), None, '#c0392b'),
    ]
    # ~~~ END ADAPTED GRID ELEMENTS ~~~

    gm.ELEMENTS   = elements
    gm.GRID_SIZE  = 6
    gm.OUTPUT     = '/home/claude/grid_a5_adapted.png'
    gm.draw_grid(elements, 6)


# ─── PAGE 1: MATHS ───────────────────────────────────────────────────────────

def build_maths_page(c):
    c.setPageSize(A5)
    cy = H - M

    cy = heading(c, M, cy, f'Maths  —  {WEEK_REF}')
    cy -= 2 * mm

    # Word bank
    # ~~~ WORD BANK: REPLACE EACH WEEK ~~~
    word_bank = ['word1', 'word2', 'word3', 'word4', 'word5']
    # ~~~ END WORD BANK ~~~

    c.setFont('Helvetica-Bold', 8)
    c.setFillColorRGB(*NAVY)
    c.drawString(M, cy - 8 * 0.85, 'Word bank:')
    wb_x = M + 45
    c.setFont('Helvetica', 8)
    c.setFillColorRGB(*BLACK)
    for w in word_bank:
        c.drawString(wb_x, cy - 8 * 0.85, w)
        wb_x += c.stringWidth(w, 'Helvetica', 8) + 8
    cy -= 8 + 4 * mm

    # Grid
    grid_path = '/home/claude/grid_a5_adapted.png'
    if os.path.exists(grid_path):
        c.drawImage(grid_path, M, cy - GH, width=GW, height=GH,
                    preserveAspectRatio=True, mask='auto')
        cy -= GH + 3 * mm
    else:
        c.setStrokeColorRGB(*LGREY)
        c.rect(M, cy - 80, GW, 80)
        cy -= 84 + 3 * mm

    # ~~~ ADAPTED MATHS QUESTIONS: REPLACE EACH WEEK ~~~
    # Order is always: 1=circle-answer, 2=fill-in-count, 3=sentence-frame, 4=true/false

    # Q1 — circle the answer
    c.setFont('Helvetica-Bold', 9)
    c.setFillColorRGB(*NAVY)
    c.drawString(M, cy - 9 * 0.85, 'Q1. Circle the answer.')
    cy -= 9 + 2 * mm
    cy = draw_options(c, cy, ['(2,3)', '(3,2)', '(1,4)', '(4,1)'])

    # Q2 — fill in the count
    c.setFont('Helvetica-Bold', 9)
    c.setFillColorRGB(*NAVY)
    c.drawString(M, cy - 9 * 0.85, 'Q2. How many squares does the shape move?  ______')
    cy -= 9 + 4 * mm

    # Q3 — sentence frame
    c.setFont('Helvetica-Bold', 9)
    c.setFillColorRGB(*NAVY)
    c.drawString(M, cy - 9 * 0.85, 'Q3. Complete the sentence.')
    cy -= 9 + 1 * mm
    c.setFont('Helvetica', 9)
    c.setFillColorRGB(*BLACK)
    c.drawString(M, cy - 9 * 0.85, 'Point A is at (_____, _____).')
    cy -= 9 + 3 * mm

    # Q4 — true / false
    c.setFont('Helvetica-Bold', 9)
    c.setFillColorRGB(*NAVY)
    c.drawString(M, cy - 9 * 0.85, 'Q4. True or false?  The star is at (5, 2).')
    cy -= 9 + 2 * mm
    cy = draw_options(c, cy, ['True', 'False'])
    # ~~~ END ADAPTED MATHS QUESTIONS ~~~

    status = 'OK' if cy > M else 'OVERFLOW'
    print(f'Adapted maths page bottom: {cy:.0f}pt  margin: {M:.0f}pt  {status}')
    c.showPage()


# ─── PAGE 2: READING ─────────────────────────────────────────────────────────

def build_reading_page(c):
    c.setPageSize(A5)
    cy = H - M

    cy = heading(c, M, cy, f'Reading  —  {WEEK_REF}')
    cy -= 3 * mm

    # ~~~ ADAPTED READING CONTENT: REPLACE EACH WEEK ~~~
    # ~120 words. Short sentences (8-12 words). High-frequency vocabulary only.
    passage = (
        '[Adapted passage: 110–130 words. Short sentences, simple vocabulary. '
        'Replace this placeholder. Must be a single string, no newlines.]'
    )

    questions = [
        (ICO_RET, 'Q1. [Simple retrieval — who, what, where.]', 2),
        (ICO_RET, 'Q2. [Simple retrieval — factual detail from the text.]', 2),
        (ICO_VOC, 'Q3. Find and copy a word that means [simple definition].', 2),
        (ICO_INF, 'Q4. Why do you think [character] did [action]?', 3),
    ]
    # ~~~ END ADAPTED READING CONTENT ~~~

    c.setFont('Helvetica-Oblique', 11)
    c.setFillColorRGB(*BLACK)
    lines = simpleSplit(passage, 'Helvetica-Oblique', 11, UW)
    for line in lines:
        bl = cy - 11 * 0.85
        c.drawString(M, bl, line)
        cy = bl - 11 * 0.15 - 11 * 0.25

    cy -= 3 * mm
    rule(c, cy)
    cy -= 3 * mm

    for icon, q_text, n_lines in questions:
        cy = question_block(c, cy, icon, q_text, n_lines)

    status = 'OK' if cy > M else 'OVERFLOW'
    print(f'Adapted reading page bottom: {cy:.0f}pt  margin: {M:.0f}pt  {status}')
    c.showPage()


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    generate_adapted_grid()
    out = f'/home/claude/HL_{WEEK_REF}.pdf'
    c = canvas.Canvas(out, pagesize=A5)
    build_maths_page(c)
    build_reading_page(c)
    c.save()
    print(f'Saved {out}')
