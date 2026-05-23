from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

W, H = A4
LABEL = "TXWX"  # replaced by skill each week

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))

DARK_NAVY  = rgb("1a3a5c")
MID_BLUE   = rgb("2e6fad")
LIGHT_BLUE = rgb("c8dcf0")
GRID_LINE  = rgb("c0cfe0")
BLACK      = (0,0,0)
WHITE      = (1,1,1)
GREEN      = (0, 0.5, 0)

ML = 18*mm
MR = 18*mm
MT = 14*mm

# ── COVER ─────────────────────────────────────────────────────────────────────
# Identical to Y4 version except Paper 2 line is omitted

def draw_cover(c):
    # Black header bar
    c.setFillColorRGB(0.08, 0.08, 0.08)
    c.rect(ML, H - MT - 18*mm, W-ML-MR, 18*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(ML+6*mm, H - MT - 11*mm, "2026 Assessments")
    c.setFont("Helvetica", 9)
    c.drawRightString(W-MR-2*mm, H - MT - 11*mm, LABEL)

    # Blue Year 4 bar — identical to Y4
    c.setFillColorRGB(*MID_BLUE)
    c.rect(ML, H - MT - 40*mm, W-ML-MR, 22*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(ML+6*mm, H - MT - 30*mm, "Year 4")

    # Body text — Paper 1 only, no Paper 2 line
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(ML, H - MT - 60*mm, "Mathematics")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(ML, H - MT - 74*mm, "Paper 1:")
    c.setFont("Helvetica", 16)
    c.drawString(ML+38*mm, H - MT - 74*mm, "arithmetic")

    # Name line
    c.setFont("Helvetica", 11)
    c.drawString(ML, H - MT - 100*mm, "Name")
    c.setLineWidth(0.8)
    c.line(ML+14*mm, H - MT - 101*mm, W - MR - 40*mm, H - MT - 101*mm)

    c.showPage()

# ── ARITHMETIC BOX CONSTANTS ──────────────────────────────────────────────────

BOX_H      = 52*mm
TOP_H      = 16*mm
STRIP_W    = 18*mm
NUM_W      = 10*mm
ANS_W      = 40*mm
ANS_H      = 10*mm
MARK_BOX_W = 10*mm
MARK_BOX_H = 10*mm
GRID_CELL  = 7*mm

# ── ARITHMETIC BOX ────────────────────────────────────────────────────────────

def draw_arith_box(c, q_num, eq_text, marks, y,
                   show_working=False, frac=None):
    label_h    = 6*mm
    this_box_h = 80*mm if show_working else BOX_H

    if show_working:
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(W/2, y - 4*mm,
                            "You must show your working on this question")
        y -= label_h

    box_left   = ML
    box_right  = W - MR
    box_top    = y
    box_bottom = y - this_box_h
    box_w      = box_right - box_left

    # Outer border
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(0.8)
    c.setFillColorRGB(*WHITE)
    c.rect(box_left, box_bottom, box_w, this_box_h, fill=1, stroke=1)

    # Right-hand mark strip
    strip_x = box_right - STRIP_W
    c.setFillColorRGB(*LIGHT_BLUE)
    c.rect(strip_x, box_bottom, STRIP_W, this_box_h, fill=1, stroke=0)

    # Question number
    c.setFillColorRGB(*MID_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(box_left + 3*mm, box_top - TOP_H/2 - 2*mm, str(q_num))

    # Separator line
    sep_y = box_top - TOP_H
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(1.0)
    c.line(box_left, sep_y, strip_x, sep_y)

    # Grid
    c.setStrokeColorRGB(*GRID_LINE)
    c.setLineWidth(0.3)
    x = box_left
    while x <= strip_x + 0.1:
        c.line(x, box_bottom, x, sep_y)
        x += GRID_CELL
    yg = box_bottom
    while yg <= sep_y + 0.1:
        c.line(box_left, yg, strip_x, yg)
        yg += GRID_CELL

    # Mark box inside strip
    c.setStrokeColorRGB(*BLACK)
    c.setFillColorRGB(*WHITE)
    c.setLineWidth(0.8)
    mb_x = strip_x + (STRIP_W - MARK_BOX_W) / 2
    mb_y = box_bottom + 5*mm
    c.rect(mb_x, mb_y, MARK_BOX_W, MARK_BOX_H, fill=1, stroke=1)
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(strip_x + STRIP_W / 2, mb_y - 4*mm, f"{marks} mark")

    # Equation and answer box
    eq_x      = box_left + NUM_W + 4*mm
    eq_y      = box_top - TOP_H/2 - 3*mm
    ans_box_y = box_top - TOP_H/2 - ANS_H/2

    if '[BOX]' in eq_text:
        parts      = eq_text.split('[BOX]')
        left_text  = parts[0].rstrip()
        right_text = parts[1].lstrip() if len(parts) > 1 else ''
        left_w     = c.stringWidth(left_text, "Helvetica-Bold", 16) if left_text else 0

        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica-Bold", 16)
        if left_text:
            c.drawString(eq_x, eq_y, left_text)

        ibx = eq_x + left_w + (3*mm if left_text else 0)
        c.setStrokeColorRGB(*MID_BLUE)
        c.setFillColorRGB(*WHITE)
        c.setLineWidth(2)
        c.rect(ibx, ans_box_y, 28*mm, ANS_H, fill=1, stroke=1)
        c.setLineWidth(0.8)

        if right_text:
            c.setFillColorRGB(*BLACK)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(ibx + 28*mm + 3*mm, eq_y, right_text)
    else:
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(eq_x, eq_y, eq_text)
        ans_box_x = strip_x - ANS_W - 4*mm
        c.setStrokeColorRGB(*MID_BLUE)
        c.setFillColorRGB(*WHITE)
        c.setLineWidth(2)
        c.rect(ans_box_x, ans_box_y, ANS_W, ANS_H, fill=1, stroke=1)
        c.setLineWidth(0.8)

    return box_bottom - 5*mm

# ── ARITHMETIC QUESTIONS — REPLACED BY SKILL EACH WEEK ───────────────────────
# Tuple format: (display_text, marks, show_working)
# [BOX] in display_text = inline answer box

ARITH_QS = [
    # SKILL_ARITH_QS_PLACEHOLDER
]

def build_arithmetic(c):
    first_page = True
    page_num   = 1
    y = H - MT

    for i, (text, marks, work) in enumerate(ARITH_QS):
        q_num   = i + 1
        label_h = 6*mm if work else 0
        this_h  = 80*mm if work else BOX_H
        needed  = this_h + label_h + 5*mm

        if y - needed < MT + 10*mm:
            draw_page_num(c, page_num)
            c.showPage()
            first_page = False
            page_num  += 1
            y = H - MT

        if first_page and i == 0:
            c.setFillColorRGB(*BLACK)
            c.setFont("Helvetica", 10)
            c.drawRightString(W - MR, H - MT + 5*mm, "...........  /   30 marks")

        y = draw_arith_box(c, q_num, text, marks, y, show_working=work)

    draw_page_num(c, page_num)
    c.showPage()

def draw_page_num(c, num):
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, 9*mm, f"page {num}")


# ── RUN ───────────────────────────────────────────────────────────────────────

out = f"/mnt/user-data/outputs/Arithmetic and Reasoning - Adapted - {LABEL}.pdf"
c = canvas.Canvas(out, pagesize=A4)
draw_cover(c)
build_arithmetic(c)
c.save()
print("Done:", out)
