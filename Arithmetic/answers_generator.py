from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Use landscape A4 — fits all answers on one page
W, H = landscape(A4)
LABEL = "TXWX"  # replaced by skill each week

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))

DARK_NAVY = rgb("1a3a5c")
MID_BLUE  = rgb("2e6fad")
BLACK     = (0,0,0)
WHITE     = (1,1,1)
GREEN     = (0, 0.5, 0)
GREY_RULE = (0.75, 0.75, 0.75)

ML   = 15*mm
MR   = 15*mm
MT   = 12*mm
ROW  = 7*mm
COLS = 5        # columns for 30-question arithmetic grid

# ── DATA — replaced by skill each week ────────────────────────────────────────

Y4_ARITH_ANS = [
    # SKILL_Y4_ARITH_ANS_PLACEHOLDER
]

Y4_REASON_ANS = [
    # SKILL_Y4_REASON_ANS_PLACEHOLDER
]

Y4_REASONING_TOTAL_MARKS = 0  # SKILL_Y4_REASONING_MARKS_PLACEHOLDER

AD_ARITH_ANS = [
    # SKILL_AD_ARITH_ANS_PLACEHOLDER
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def section_header(c, x, y, w, text):
    """Draw a dark navy section header bar."""
    c.setFillColorRGB(*DARK_NAVY)
    c.rect(x, y - 7*mm, w, 7*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 3*mm, y - 5*mm, text)
    return y - 7*mm  # returns bottom of header


def answer_grid(c, x, y, answers, cols, col_w):
    """
    Draw answers in a multi-column grid.
    Returns the y position below the last row.
    """
    for i, (qn, ans) in enumerate(answers):
        col = i % cols
        row = i // cols
        cx  = x + col * col_w
        cy  = y - row * ROW

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColorRGB(*DARK_NAVY)
        c.drawString(cx, cy, f"Q{qn}.")
        c.setFont("Helvetica", 8.5)
        c.setFillColorRGB(*GREEN)
        c.drawString(cx + 9*mm, cy, ans)

    rows = (len(answers) + cols - 1) // cols
    return y - rows * ROW


def divider_line(c, x, y, w):
    """Thin grey rule between sections."""
    c.setStrokeColorRGB(*GREY_RULE)
    c.setLineWidth(0.5)
    c.line(x, y, x + w, y)
    return y - 5*mm


# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────

def build_answers(c):
    content_w = W - ML - MR

    # ── Page header ──────────────────────────────────────────────────────────
    c.setFillColorRGB(*DARK_NAVY)
    c.rect(ML, H - MT - 10*mm, content_w, 10*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, H - MT - 6.5*mm, f"Answer Sheet  —  {LABEL}")

    y = H - MT - 10*mm - 6*mm  # starting y below header

    # ── Y4 section label ─────────────────────────────────────────────────────
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(ML, y, "Year 4")
    y -= 5*mm

    # ── Y4 Arithmetic ────────────────────────────────────────────────────────
    col_w = content_w / COLS
    y = section_header(c, ML, y, content_w,
                       f"Paper 1: Arithmetic  (30 marks)")
    y -= 6*mm
    y = answer_grid(c, ML, y, Y4_ARITH_ANS, COLS, col_w)
    y -= 6*mm

    # ── Y4 Reasoning ─────────────────────────────────────────────────────────
    reason_cols = 4
    reason_col_w = content_w / reason_cols
    y = section_header(c, ML, y, content_w,
                       f"Paper 2: Reasoning and Problem Solving  ({Y4_REASONING_TOTAL_MARKS} marks)")
    y -= 6*mm
    y = answer_grid(c, ML, y, Y4_REASON_ANS, reason_cols, reason_col_w)
    y -= 6*mm

    # ── Divider ───────────────────────────────────────────────────────────────
    y = divider_line(c, ML, y, content_w)

    # ── Adapted section label ─────────────────────────────────────────────────
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(ML, y, "Adapted")
    y -= 5*mm

    # ── Adapted Arithmetic ────────────────────────────────────────────────────
    y = section_header(c, ML, y, content_w,
                       "Paper 1: Arithmetic  (30 marks)")
    y -= 6*mm
    answer_grid(c, ML, y, AD_ARITH_ANS, COLS, col_w)

    c.showPage()


# ── RUN ───────────────────────────────────────────────────────────────────────

out = f"/mnt/user-data/outputs/Arithmetic and Reasoning - Answers - {LABEL}.pdf"
c   = canvas.Canvas(out, pagesize=landscape(A4))
build_answers(c)
c.save()
print("Done:", out)
