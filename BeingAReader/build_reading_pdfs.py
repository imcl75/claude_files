"""
T5W2 PDF builder — matches T5W1 layout exactly.
Produces 12 individual PDFs then merges into 3.
"""
import sys
sys.path.insert(0, '/home/claude')
from t5w2_content import *

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
import os

W, H = A4
MARGIN = 8 * mm
CW = W - 2 * MARGIN  # content width

# Colours matching T5W1
BOX_BORDER = (0.173, 0.173, 0.424)   # #2c2c6c
BOX_BG     = (0.941, 0.941, 0.973)   # #f0f0f8
GREEN      = (0.102, 0.478, 0.102)   # #1a7a1a
DARK       = (0.133, 0.133, 0.133)
GREY_LINE  = (0.6, 0.6, 0.6)

ICON_PATH = "/home/claude/reader_icon_saved.png"
OUT_DIR   = "/home/claude/pdfs_individual"
os.makedirs(OUT_DIR, exist_ok=True)


def draw_header(c, lesson_type, date_str, key_q, lf, ican1, ican2, pupil_name=None):
    """
    Draw the learning label header using the unified enquiry_label() function.
    Returns y after header (first available content position).
    """
    from build_enquiry_label import enquiry_label

    day, date_val = date_str if isinstance(date_str, (list, tuple)) else (date_str, date_str)

    # Strip prefixes — enquiry_label() prepends them itself
    lf_clean  = lf.replace('LF: To ', '').replace('LF: to ', '').strip()
    ic1_clean = ican1.replace('I can ', '').replace('i can ', '').strip()
    ic2_clean = ican2.replace('I can ', '').replace('i can ', '').strip()

    y_start = H - MARGIN

    # Day + date in top-left (outside the label area)
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(*DARK)
    c.drawString(MARGIN, y_start - 5*mm, f"{day}  {date_val}")

    # Pupil name for adapted copies — below day/date on the left
    if pupil_name:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN, y_start - 9.5*mm, pupil_name)

    # Learning label — top-right using the unified confirmed function
    label_bottom = enquiry_label(
        c,
        kq=key_q,
        date=date_val,
        lf=lf_clean,
        ican1=ic1_clean,
        ican2=ic2_clean,
        subject='reader',
        year='Y4',
        maths=False,
        top_y=y_start,
    )

    # Thin divider across full content width below the label
    c.setStrokeColorRGB(*GREY_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, label_bottom - 1*mm, MARGIN + CW, label_bottom - 1*mm)

    return label_bottom - 3*mm



def wrap_text(c, text, font, size, max_w):
    """Wrap text to lines fitting max_w. Returns list of lines."""
    words = text.split()
    lines, line = [], ''
    for w in words:
        test = (line + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or ['']


def draw_text_box(c, text, y_top, font_size=10.5):
    """Draw the reading text box. Returns y after box."""
    lines = wrap_text(c, text, "Helvetica", font_size, CW - 6*mm)
    line_h = font_size * 1.4
    box_h = len(lines) * line_h + 5*mm

    # Box
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*BOX_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(MARGIN, y_top - box_h, CW, box_h, 2*mm, fill=1, stroke=1)

    # Text
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica", font_size)
    ty = y_top - 3*mm - font_size * 0.72
    for line in lines:
        c.drawString(MARGIN + 3*mm, ty, line)
        ty -= line_h

    return y_top - box_h - 3*mm


def answer_lines(c, y, n, gap=6.5*mm):
    """Draw n solid answer lines. Returns y after lines."""
    c.setStrokeColorRGB(*GREY_LINE)
    c.setLineWidth(0.4)
    for i in range(n):
        ly = y - (i + 1) * gap
        c.line(MARGIN, ly, MARGIN + CW, ly)
    return y - n * gap - 2*mm


def draw_quote_pupil(c, y):
    """Single underline for 'find and copy' answer."""
    ly = y - 6.5*mm
    c.setStrokeColorRGB(*GREY_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, ly, MARGIN + CW, ly)
    return y - 8*mm


def draw_quote_answer(c, answer, y):
    """Find-and-copy answer: green text above a line."""
    c.setFillColorRGB(*GREEN)
    c.setFont("Helvetica-BoldOblique", 9)
    c.drawString(MARGIN + 1*mm, y - 4.5*mm, f'"{answer}"')
    ly = y - 6.5*mm
    c.setStrokeColorRGB(*GREY_LINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, ly, MARGIN + CW, ly)
    return y - 8*mm


def draw_true_false_pupil(c, y):
    """True / False with circular radio buttons."""
    half = CW / 2
    c.setLineWidth(0.5)
    for i, label in enumerate(["True", "False"]):
        x = MARGIN + i * half
        cx = x + 3.5*mm
        cy = y - 3.5*mm
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.circle(cx, cy, 2.8*mm, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 10)
        c.drawString(cx + 4*mm, y - 5*mm, label)
    return y - 8*mm


def draw_true_false_answer(c, correct, y):
    """True / False — correct option filled."""
    half = CW / 2
    c.setLineWidth(0.5)
    for i, label in enumerate(["True", "False"]):
        x = MARGIN + i * half
        cx = x + 3.5*mm
        cy = y - 3.5*mm
        if label == correct:
            c.setFillColorRGB(*BOX_BORDER)
            c.setStrokeColorRGB(*BOX_BORDER)
            c.circle(cx, cy, 2.8*mm, fill=1, stroke=1)
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.circle(cx, cy, 2.8*mm, fill=1, stroke=1)
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica", 10)
        c.drawString(cx + 4*mm, y - 5*mm, label)
    return y - 8*mm


def draw_select_pupil(c, options, y):
    """Tick ALL that apply — square checkboxes, 2-column layout."""
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    note = "(Tick all that apply — there may be more than one correct answer)"
    c.drawString(MARGIN, y, note)
    y -= 5.5*mm
    col_w = CW / 2
    box_s = 3.5*mm
    row_h = 6*mm
    rows = (len(options) + 1) // 2
    c.setLineWidth(0.5)
    for i, opt in enumerate(options):
        row = i // 2
        col = i % 2
        x = MARGIN + col * col_w
        ry = y - row * row_h
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.rect(x, ry - box_s, box_s, box_s, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        c.drawString(x + box_s + 2*mm, ry - box_s + 1*mm, opt)
    return y - rows * row_h - 2*mm


def draw_select_answer(c, options, correct_list, y):
    """Tick ALL that apply — correct boxes ticked in accent colour."""
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    note = "(Tick all that apply — there may be more than one correct answer)"
    c.drawString(MARGIN, y, note)
    y -= 5.5*mm
    col_w = CW / 2
    box_s = 3.5*mm
    row_h = 6*mm
    rows = (len(options) + 1) // 2
    c.setLineWidth(0.5)
    for i, opt in enumerate(options):
        row = i // 2
        col = i % 2
        x = MARGIN + col * col_w
        ry = y - row * row_h
        is_correct = opt in correct_list
        if is_correct:
            c.setFillColorRGB(*BOX_BG)
            c.setStrokeColorRGB(*BOX_BORDER)
        else:
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.rect(x, ry - box_s, box_s, box_s, fill=1, stroke=1)
        if is_correct:
            # Tick mark
            c.setStrokeColorRGB(*BOX_BORDER)
            c.setLineWidth(1)
            c.line(x + 0.6*mm, ry - box_s + 1.8*mm, x + 1.4*mm, ry - box_s + 0.8*mm)
            c.line(x + 1.4*mm, ry - box_s + 0.8*mm, x + 3.1*mm, ry - box_s + 2.8*mm)
            c.setLineWidth(0.5)
            c.setFillColorRGB(*BOX_BORDER)
            c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica", 9)
        c.drawString(x + box_s + 2*mm, ry - box_s + 1*mm, opt)
    return y - rows * row_h - 2*mm



def draw_tick_v_pupil(c, options, correct, y):
    """KS2-style vertical tick list. Instruction is drawn by render_question inline with question text."""
    c.setFont("Helvetica", 9)
    max_w = max(c.stringWidth(o, "Helvetica", 9) for o in options)
    box_s = 3.5*mm
    box_x = MARGIN + 2*mm + max_w + 4*mm  # just after longest option
    row_h = 7*mm
    c.setLineWidth(0.5)
    for opt in options:
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.rect(box_x, y - box_s, box_s, box_s, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN + 2*mm, y - box_s + 1*mm, opt)
        y -= row_h
    return y - 1*mm


def draw_tick_v_answer(c, options, correct, y):
    """KS2-style vertical tick list — correct answer(s) ticked. Instruction drawn by render_question."""
    c.setFont("Helvetica", 9)
    max_w = max(c.stringWidth(o, "Helvetica", 9) for o in options)
    correct_list = [correct] if isinstance(correct, str) else list(correct)
    box_s = 3.5*mm
    box_x = MARGIN + 2*mm + max_w + 4*mm
    row_h = 7*mm
    c.setLineWidth(0.5)
    for opt in options:
        is_correct = opt in correct_list
        bx = box_x
        if is_correct:
            c.setFillColorRGB(*BOX_BG)
            c.setStrokeColorRGB(*BOX_BORDER)
        else:
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.rect(bx, y - box_s, box_s, box_s, fill=1, stroke=1)
        if is_correct:
            c.setStrokeColorRGB(*BOX_BORDER)
            c.setLineWidth(1)
            c.line(bx + 0.5*mm, y - box_s + 1.8*mm, bx + 1.3*mm, y - box_s + 0.7*mm)
            c.line(bx + 1.3*mm, y - box_s + 0.7*mm, bx + 3*mm, y - box_s + 2.8*mm)
            c.setLineWidth(0.5)
            c.setFillColorRGB(*BOX_BORDER)
            c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 2*mm, y - box_s + 1*mm, opt)
        y -= row_h
    return y - 1*mm


def draw_impr_evidence_pupil(c, n_rows, y):
    """Impression/Evidence 2-column write-in table (KS2 Q38 style)."""
    hdr_h = 9*mm
    row_h = 34*mm
    col_i = CW * 0.40
    col_e = CW * 0.60
    gap_l = 7*mm
    c.setLineWidth(0.5)
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN,         y - hdr_h, col_i, hdr_h, fill=1, stroke=1)
    c.rect(MARGIN + col_i, y - hdr_h, col_e, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(MARGIN + col_i / 2,         y - hdr_h + 3*mm, "Impression")
    c.drawCentredString(MARGIN + col_i + col_e / 2, y - hdr_h + 3*mm, "Evidence")
    y -= hdr_h
    for _ in range(n_rows):
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN,         y - row_h, col_i, row_h, fill=1, stroke=1)
        c.rect(MARGIN + col_i, y - row_h, col_e, row_h, fill=1, stroke=1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.setLineWidth(0.4)
        ly_i = y - row_h + 9*mm
        c.line(MARGIN + 3*mm, ly_i, MARGIN + col_i - 3*mm, ly_i)
        for k in range(3):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.line(MARGIN + col_i + 3*mm, ly_e, MARGIN + CW - 3*mm, ly_e)
        y -= row_h
    return y - 2*mm


def draw_impr_evidence_answer(c, pairs, y):
    """Impression/Evidence table with answer text."""
    hdr_h = 9*mm
    row_h = 34*mm
    col_i = CW * 0.40
    col_e = CW * 0.60
    gap_l = 7*mm
    c.setLineWidth(0.5)
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN,         y - hdr_h, col_i, hdr_h, fill=1, stroke=1)
    c.rect(MARGIN + col_i, y - hdr_h, col_e, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(MARGIN + col_i / 2,         y - hdr_h + 3*mm, "Impression")
    c.drawCentredString(MARGIN + col_i + col_e / 2, y - hdr_h + 3*mm, "Evidence")
    y -= hdr_h
    for impr, evid in pairs:
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN,         y - row_h, col_i, row_h, fill=1, stroke=1)
        c.rect(MARGIN + col_i, y - row_h, col_e, row_h, fill=1, stroke=1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.setLineWidth(0.4)
        ly_i = y - row_h + 9*mm
        c.line(MARGIN + 3*mm, ly_i, MARGIN + col_i - 3*mm, ly_i)
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        for k, il in enumerate(wrap_text(c, impr, "Helvetica-Oblique", 8.5, col_i - 6*mm)[:2]):
            c.drawString(MARGIN + 3*mm, ly_i + 1*mm + k * 5*mm, il)
        for k in range(3):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.setStrokeColorRGB(*GREY_LINE)
            c.line(MARGIN + col_i + 3*mm, ly_e, MARGIN + CW - 3*mm, ly_e)
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        for k, el in enumerate(wrap_text(c, evid, "Helvetica-Oblique", 8.5, col_e - 6*mm)[:3]):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.drawString(MARGIN + col_i + 3*mm, ly_e + 1*mm, el)
        y -= row_h
    return y - 2*mm



def draw_attrib_table_pupil(c, options, y):
    """Attribution table — tick one column per row. KS2 Q8 (James/Mandy) style.
    options[0] = list of column header strings; options[1:] = statement rows."""
    headers = options[0]
    rows    = options[1:]
    col_stmt = CW * 0.62
    n_cols   = len(headers)
    col_w    = (CW - col_stmt) / n_cols
    hdr_h    = 8*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    # Draw header cells (right side only — left cell blank)
    for i, hdr in enumerate(headers):
        hx = MARGIN + col_stmt + i * col_w
        c.setFillColorRGB(*BOX_BG)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(hx, y - hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(hx + col_w / 2, y - hdr_h + 2.5*mm, hdr)
    y -= hdr_h
    for i, stmt in enumerate(rows):
        fill = (0.96, 0.96, 0.96) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        for j in range(n_cols):
            c.rect(MARGIN + col_stmt + j * col_w, y - row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 9, col_stmt - 4*mm)
        for k, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - k * 4.5*mm, sl)
        for j in range(n_cols):
            bx = MARGIN + col_stmt + j * col_w + (col_w - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
        y -= row_h
    return y - 2*mm


def draw_attrib_table_answer(c, options, correct_list, y):
    """Attribution table with correct column ticked."""
    headers = options[0]
    rows    = options[1:]
    col_stmt = CW * 0.62
    n_cols   = len(headers)
    col_w    = (CW - col_stmt) / n_cols
    hdr_h    = 8*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    for i, hdr in enumerate(headers):
        hx = MARGIN + col_stmt + i * col_w
        c.setFillColorRGB(*BOX_BG)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(hx, y - hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(hx + col_w / 2, y - hdr_h + 2.5*mm, hdr)
    y -= hdr_h
    for i, (stmt, correct_hdr) in enumerate(zip(rows, correct_list)):
        fill = (0.96, 0.96, 0.96) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        for j in range(n_cols):
            c.rect(MARGIN + col_stmt + j * col_w, y - row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 9, col_stmt - 4*mm)
        for k, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - k * 4.5*mm, sl)
        for j, hdr in enumerate(headers):
            bx = MARGIN + col_stmt + j * col_w + (col_w - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            is_correct = (hdr == correct_hdr)
            if is_correct:
                c.setFillColorRGB(*BOX_BG); c.setStrokeColorRGB(*BOX_BORDER)
            else:
                c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
            if is_correct:
                c.setStrokeColorRGB(*BOX_BORDER); c.setLineWidth(1)
                c.line(bx+0.4*mm, by+1.6*mm, bx+1.1*mm, by+0.6*mm)
                c.line(bx+1.1*mm, by+0.6*mm, bx+2.7*mm, by+2.4*mm)
                c.setLineWidth(0.5)
        y -= row_h
    return y - 2*mm


def draw_impr_evidence_pupil(c, n_rows, y):
    """Impression/Evidence 2-column write-in table (KS2 Q38 style)."""
    hdr_h = 9*mm
    row_h = 34*mm
    col_i = CW * 0.40
    col_e = CW * 0.60
    gap_l = 7*mm
    c.setLineWidth(0.5)
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN,         y - hdr_h, col_i, hdr_h, fill=1, stroke=1)
    c.rect(MARGIN + col_i, y - hdr_h, col_e, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(MARGIN + col_i / 2,         y - hdr_h + 3*mm, "Impression")
    c.drawCentredString(MARGIN + col_i + col_e / 2, y - hdr_h + 3*mm, "Evidence")
    y -= hdr_h
    for _ in range(n_rows):
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN,         y - row_h, col_i, row_h, fill=1, stroke=1)
        c.rect(MARGIN + col_i, y - row_h, col_e, row_h, fill=1, stroke=1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.setLineWidth(0.4)
        ly_i = y - row_h + 9*mm
        c.line(MARGIN + 3*mm, ly_i, MARGIN + col_i - 3*mm, ly_i)
        for k in range(3):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.line(MARGIN + col_i + 3*mm, ly_e, MARGIN + CW - 3*mm, ly_e)
        y -= row_h
    return y - 2*mm


def draw_impr_evidence_answer(c, pairs, y):
    """Impression/Evidence table with answer text."""
    hdr_h = 9*mm
    row_h = 34*mm
    col_i = CW * 0.40
    col_e = CW * 0.60
    gap_l = 7*mm
    c.setLineWidth(0.5)
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN,         y - hdr_h, col_i, hdr_h, fill=1, stroke=1)
    c.rect(MARGIN + col_i, y - hdr_h, col_e, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(MARGIN + col_i / 2,         y - hdr_h + 3*mm, "Impression")
    c.drawCentredString(MARGIN + col_i + col_e / 2, y - hdr_h + 3*mm, "Evidence")
    y -= hdr_h
    for impr, evid in pairs:
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN,         y - row_h, col_i, row_h, fill=1, stroke=1)
        c.rect(MARGIN + col_i, y - row_h, col_e, row_h, fill=1, stroke=1)
        c.setStrokeColorRGB(*GREY_LINE)
        c.setLineWidth(0.4)
        ly_i = y - row_h + 9*mm
        c.line(MARGIN + 3*mm, ly_i, MARGIN + col_i - 3*mm, ly_i)
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        for k, il in enumerate(wrap_text(c, impr, "Helvetica-Oblique", 8.5, col_i - 6*mm)[:2]):
            c.drawString(MARGIN + 3*mm, ly_i + 1*mm + k * 5*mm, il)
        for k in range(3):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.setStrokeColorRGB(*GREY_LINE)
            c.line(MARGIN + col_i + 3*mm, ly_e, MARGIN + CW - 3*mm, ly_e)
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        for k, el in enumerate(wrap_text(c, evid, "Helvetica-Oblique", 8.5, col_e - 6*mm)[:3]):
            ly_e = y - row_h + 9*mm + k * gap_l
            c.drawString(MARGIN + col_i + 3*mm, ly_e + 1*mm, el)
        y -= row_h
    return y - 2*mm



def draw_attrib_table_pupil(c, options, y):
    """Attribution table — tick one column per row. KS2 Q8 (James/Mandy) style.
    options[0] = list of column header strings; options[1:] = statement rows."""
    headers = options[0]
    rows    = options[1:]
    col_stmt = CW * 0.62
    n_cols   = len(headers)
    col_w    = (CW - col_stmt) / n_cols
    hdr_h    = 8*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    # Draw header cells (right side only — left cell blank)
    for i, hdr in enumerate(headers):
        hx = MARGIN + col_stmt + i * col_w
        c.setFillColorRGB(*BOX_BG)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(hx, y - hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(hx + col_w / 2, y - hdr_h + 2.5*mm, hdr)
    y -= hdr_h
    for i, stmt in enumerate(rows):
        fill = (0.96, 0.96, 0.96) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        for j in range(n_cols):
            c.rect(MARGIN + col_stmt + j * col_w, y - row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 9, col_stmt - 4*mm)
        for k, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - k * 4.5*mm, sl)
        for j in range(n_cols):
            bx = MARGIN + col_stmt + j * col_w + (col_w - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
        y -= row_h
    return y - 2*mm


def draw_attrib_table_answer(c, options, correct_list, y):
    """Attribution table with correct column ticked."""
    headers = options[0]
    rows    = options[1:]
    col_stmt = CW * 0.62
    n_cols   = len(headers)
    col_w    = (CW - col_stmt) / n_cols
    hdr_h    = 8*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    for i, hdr in enumerate(headers):
        hx = MARGIN + col_stmt + i * col_w
        c.setFillColorRGB(*BOX_BG)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(hx, y - hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(hx + col_w / 2, y - hdr_h + 2.5*mm, hdr)
    y -= hdr_h
    for i, (stmt, correct_hdr) in enumerate(zip(rows, correct_list)):
        fill = (0.96, 0.96, 0.96) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        for j in range(n_cols):
            c.rect(MARGIN + col_stmt + j * col_w, y - row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 9, col_stmt - 4*mm)
        for k, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - k * 4.5*mm, sl)
        for j, hdr in enumerate(headers):
            bx = MARGIN + col_stmt + j * col_w + (col_w - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            is_correct = (hdr == correct_hdr)
            if is_correct:
                c.setFillColorRGB(*BOX_BG); c.setStrokeColorRGB(*BOX_BORDER)
            else:
                c.setFillColorRGB(1, 1, 1); c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
            if is_correct:
                c.setStrokeColorRGB(*BOX_BORDER); c.setLineWidth(1)
                c.line(bx+0.4*mm, by+1.6*mm, bx+1.1*mm, by+0.6*mm)
                c.line(bx+1.1*mm, by+0.6*mm, bx+2.7*mm, by+2.4*mm)
                c.setLineWidth(0.5)
        y -= row_h
    return y - 2*mm


def draw_tf_table_pupil(c, statements, y):
    """True/False multi-statement table — KS2 Q20 style."""
    col_stmt = CW * 0.72
    col_tf   = CW * 0.14
    hdr_h    = 7*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    # Header
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN + col_stmt, y - hdr_h, col_tf * 2, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(MARGIN + col_stmt + col_tf / 2,        y - hdr_h + 2.5*mm, "True")
    c.drawCentredString(MARGIN + col_stmt + col_tf * 1.5,      y - hdr_h + 2.5*mm, "False")
    y -= hdr_h
    for i, stmt in enumerate(statements):
        fill_bg = (0.97, 0.97, 0.97) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill_bg)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        c.rect(MARGIN + col_stmt, y - row_h, col_tf * 2, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 8.5)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 8.5, col_stmt - 4*mm)
        for j, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - j * 4.5*mm, sl)
        for k in range(2):
            bx = MARGIN + col_stmt + k * col_tf + (col_tf - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
        y -= row_h
    return y - 2*mm


def draw_tf_table_answer(c, statements, correct_list, y):
    """True/False table — correct boxes ticked."""
    col_stmt = CW * 0.72
    col_tf   = CW * 0.14
    hdr_h    = 7*mm
    row_h    = 9*mm
    box_s    = 3*mm
    c.setLineWidth(0.5)
    c.setFillColorRGB(*BOX_BG)
    c.setStrokeColorRGB(*GREY_LINE)
    c.rect(MARGIN + col_stmt, y - hdr_h, col_tf * 2, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(MARGIN + col_stmt + col_tf / 2,   y - hdr_h + 2.5*mm, "True")
    c.drawCentredString(MARGIN + col_stmt + col_tf * 1.5, y - hdr_h + 2.5*mm, "False")
    y -= hdr_h
    for i, (stmt, ans) in enumerate(zip(statements, correct_list)):
        fill_bg = (0.97, 0.97, 0.97) if i % 2 == 0 else (1, 1, 1)
        c.setFillColorRGB(*fill_bg)
        c.setStrokeColorRGB(*GREY_LINE)
        c.rect(MARGIN, y - row_h, col_stmt, row_h, fill=1, stroke=1)
        c.setFillColorRGB(1, 1, 1)
        c.rect(MARGIN + col_stmt, y - row_h, col_tf * 2, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 8.5)
        stmt_lines = wrap_text(c, stmt, "Helvetica", 8.5, col_stmt - 4*mm)
        for j, sl in enumerate(stmt_lines[:2]):
            c.drawString(MARGIN + 2*mm, y - 3.5*mm - j * 4.5*mm, sl)
        for k, tf in enumerate(["True", "False"]):
            bx = MARGIN + col_stmt + k * col_tf + (col_tf - box_s) / 2
            by = y - row_h / 2 - box_s / 2
            is_ans = (ans == tf)
            if is_ans:
                c.setFillColorRGB(*BOX_BG)
                c.setStrokeColorRGB(*BOX_BORDER)
            else:
                c.setFillColorRGB(1, 1, 1)
                c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.rect(bx, by, box_s, box_s, fill=1, stroke=1)
            if is_ans:
                c.setStrokeColorRGB(*BOX_BORDER)
                c.setLineWidth(1)
                c.line(bx + 0.4*mm, by + 1.6*mm, bx + 1.1*mm, by + 0.6*mm)
                c.line(bx + 1.1*mm, by + 0.6*mm, bx + 2.7*mm, by + 2.4*mm)
                c.setLineWidth(0.5)
        y -= row_h
    return y - 2*mm


def draw_evidence_pupil(c, n_items, y, lines_per_item=1):
    """Numbered evidence list — KS2 Q4/Q9 style."""
    gap = 6.5*mm
    c.setLineWidth(0.4)
    for i in range(n_items):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN, y, f"{i + 1}.")
        for j in range(lines_per_item):
            ly = y - (j + 1) * gap
            c.setStrokeColorRGB(*GREY_LINE)
            c.line(MARGIN + 5*mm, ly, MARGIN + CW, ly)
        y -= lines_per_item * gap + 4*mm
    return y


def draw_evidence_answer(c, answers, y, lines_per_item=1):
    """Numbered evidence list with answers in green."""
    gap = 6.5*mm
    for i, ans in enumerate(answers):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN, y, f"{i + 1}.")
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawString(MARGIN + 5*mm, y - gap + 2*mm, ans)
        y -= lines_per_item * gap + 4*mm
    return y



def q_label(c, qnum, text, y, is_answer=False, ans_colour=False):
    """Draw question label. Returns y after text."""
    colour = GREEN if ans_colour else DARK
    c.setFillColorRGB(*colour)
    c.setFont("Helvetica-Bold", 9)
    label = f"{qnum[1:]}. "
    lw = c.stringWidth(label, "Helvetica-Bold", 9)
    c.drawString(MARGIN, y, label)
    lines = wrap_text(c, text, "Helvetica-Bold", 9, CW - lw)
    for i, line in enumerate(lines):
        c.drawString(MARGIN + lw, y - i * (9 * 1.35), line)
    return y - len(lines) * (9 * 1.35) - 1*mm


def draw_mc_pupil(c, options, y):
    """4-cell MC table, no highlight."""
    col_w = CW / 2
    row_h = 6*mm
    # Two rows of 2
    for row in range(2):
        for col in range(2):
            idx = row * 2 + col
            if idx >= len(options):
                break
            x = MARGIN + col * col_w
            ry = y - row * row_h
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.setLineWidth(0.4)
            c.rect(x, ry - row_h, col_w, row_h, fill=1, stroke=1)
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica", 8.5)
            c.drawString(x + 2*mm, ry - row_h + 2*mm, options[idx])
    return y - 2 * row_h - 1.5*mm


def draw_mc_answer(c, options, correct, y):
    """4-cell MC table, correct cell highlighted green."""
    col_w = CW / 2
    row_h = 6*mm
    for row in range(2):
        for col in range(2):
            idx = row * 2 + col
            if idx >= len(options):
                break
            x = MARGIN + col * col_w
            ry = y - row * row_h
            is_correct = options[idx] == correct
            if is_correct:
                c.setFillColorRGB(0.85, 0.95, 0.85)
            else:
                c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.setLineWidth(0.4)
            c.rect(x, ry - row_h, col_w, row_h, fill=1, stroke=1)
            if is_correct:
                c.setFillColorRGB(*GREEN)
                c.setFont("Helvetica-Bold", 8.5)
                c.drawString(x + 2*mm, ry - row_h + 2*mm, options[idx] + " \u2713")
            else:
                c.setFillColorRGB(*DARK)
                c.setFont("Helvetica", 8.5)
                c.drawString(x + 2*mm, ry - row_h + 2*mm, options[idx])
    return y - 2 * row_h - 1.5*mm


def draw_match_pupil(c, pairs, y):
    """Match — circles at column edges; pupil draws connecting lines."""
    lw  = CW * 0.30
    rw  = CW * 0.48
    gap = CW - lw - rw
    row_h = 9*mm
    r     = 2.5*mm
    rights    = [right for _, right in pairs]
    scrambled = rights[1:] + rights[:1]
    c.setLineWidth(0.4)
    for i, (left, _) in enumerate(pairs):
        ry    = y - i * row_h
        mid_y = ry - row_h / 2
        c.setFillColorRGB(0.96, 0.96, 0.96)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(MARGIN, ry - row_h, lw, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 2*mm, mid_y - 2*mm, left)
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.circle(MARGIN + lw, mid_y, r, fill=1, stroke=1)
        rx = MARGIN + lw + gap
        c.setFillColorRGB(0.96, 0.96, 0.96)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(rx, ry - row_h, rw, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        c.setFont("Helvetica", 9)
        c.drawString(rx + r * 2 + 2*mm, mid_y - 2*mm, scrambled[i])
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.circle(rx, mid_y, r, fill=1, stroke=1)
    return y - len(pairs) * row_h - 1.5*mm


def draw_match_answer(c, pairs, y):
    """Match — filled circles with lines connecting correct pairs."""
    lw  = CW * 0.30
    rw  = CW * 0.48
    gap = CW - lw - rw
    row_h = 9*mm
    r     = 2.5*mm
    n     = len(pairs)
    rights    = [right for _, right in pairs]
    scrambled = rights[1:] + rights[:1]
    lx       = MARGIN + lw
    rx_circ  = MARGIN + lw + gap
    left_cy  = [y - i * row_h - row_h / 2 for i in range(n)]
    right_cy = [y - i * row_h - row_h / 2 for i in range(n)]
    c.setLineWidth(0.4)
    for i, (left, _) in enumerate(pairs):
        ry    = y - i * row_h
        mid_y = ry - row_h / 2
        c.setFillColorRGB(0.96, 0.96, 0.96)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(MARGIN, ry - row_h, lw, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*BOX_BORDER)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 2*mm, mid_y - 2*mm, left)
        c.setFillColorRGB(*BOX_BORDER)
        c.setStrokeColorRGB(*BOX_BORDER)
        c.circle(lx, mid_y, r, fill=1, stroke=0)
        rx = MARGIN + lw + gap
        c.setFillColorRGB(0.96, 0.96, 0.96)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(rx, ry - row_h, rw, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*BOX_BORDER)
        c.setFont("Helvetica-BoldOblique", 9)
        c.drawString(rx + r * 2 + 2*mm, mid_y - 2*mm, scrambled[i])
        c.setFillColorRGB(*BOX_BORDER)
        c.setStrokeColorRGB(*BOX_BORDER)
        c.circle(rx_circ, mid_y, r, fill=1, stroke=0)
    c.setStrokeColorRGB(*BOX_BORDER)
    c.setLineWidth(1.5)
    for i in range(n):
        j = (i - 1) % n
        c.line(lx + r, left_cy[i], rx_circ - r, right_cy[j])
    return y - n * row_h - 1.5*mm



def draw_fill(c, sentence, y, is_answer=False, answer=""):
    """Draw fill-in-blank sentence with underline blanks or green answers."""
    parts = sentence.split("______________")
    blanks_needed = len(parts) - 1
    answers = [a.strip() for a in answer.split("/")] if answer else []
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*DARK)
    x = MARGIN
    blank_w = 28*mm
    for pi, part in enumerate(parts):
        # Measure and draw the text part
        pw = c.stringWidth(part, "Helvetica", 9)
        c.drawString(x, y, part)
        x += pw
        if pi < blanks_needed:
            if is_answer and pi < len(answers):
                c.setFillColorRGB(*GREEN)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(x + 1*mm, y, answers[pi])
                x += blank_w
                c.setFillColorRGB(*DARK)
                c.setFont("Helvetica", 9)
            else:
                c.setStrokeColorRGB(*GREY_LINE)
                c.setLineWidth(0.5)
                c.line(x, y - 1*mm, x + blank_w, y - 1*mm)
                x += blank_w
    return y - 5.5*mm


def draw_tick_pupil(c, options, y):
    """Tick options with square bullets."""
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*DARK)
    # 2 or 3 per row depending on count
    # Choose columns based on option length
    max_len = max(len(o) for o in options)
    if max_len > 25:
        per_row = 2  # long options: 2 per row
    elif len(options) == 5:
        per_row = 5  # 5 short options: all on one row
    else:
        per_row = 4
    col_w = CW / per_row
    rows = (len(options) + per_row - 1) // per_row
    row_h = 5.5*mm
    for i, opt in enumerate(options):
        row = i // per_row
        col = i % per_row
        c.drawString(MARGIN + col * col_w, y - row * row_h, opt)
    return y - rows * row_h - 3*mm


def draw_tick_answer(c, options, correct, y):
    """Tick options with correct ones in bold green."""
    max_len = max(len(o) for o in options)
    if max_len > 25:
        per_row = 2
    elif len(options) == 5:
        per_row = 5
    else:
        per_row = 4
    col_w = CW / per_row
    rows = (len(options) + per_row - 1) // per_row
    row_h = 5.5*mm
    for i, opt in enumerate(options):
        row = i // per_row
        col = i % per_row
        if opt in correct:
            c.setFillColorRGB(*GREEN)
            c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColorRGB(*DARK)
            c.setFont("Helvetica", 9)
        c.drawString(MARGIN + col * col_w, y - row * row_h, opt)
    return y - rows * row_h - 3*mm


def draw_order_pupil(c, events, y):
    """KS2-style sequencing — text left, number box just after longest item."""
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*DARK)
    box_s = 6*mm
    row_h = 10*mm
    max_w = max(c.stringWidth(ev, "Helvetica", 9) for ev in events)
    box_x = MARGIN + 2*mm + max_w + 4*mm
    c.setLineWidth(0.5)
    for ev in events:
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN + 2*mm, y - row_h + 3*mm, ev)
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.rect(box_x, y - row_h + 2*mm, box_s, box_s - 1*mm, fill=1, stroke=1)
        y -= row_h + 2*mm
    return y - 1*mm



def draw_order_answer(c, events, correct_order, y):
    """KS2-style sequencing — number box just after longest item."""
    c.setFont("Helvetica", 9)
    box_s = 6*mm
    row_h = 10*mm
    max_w = max(c.stringWidth(ev, "Helvetica", 9) for ev in events)
    box_x = MARGIN + 2*mm + max_w + 4*mm
    c.setLineWidth(0.5)
    nums = [n.strip() for n in str(correct_order).split(",")]
    for i, (ev, num) in enumerate(zip(events, nums)):
        c.setFillColorRGB(*DARK)
        c.drawString(MARGIN + 2*mm, y - row_h + 3*mm, ev)
        c.setFillColorRGB(*BOX_BG)
        c.setStrokeColorRGB(*BOX_BORDER)
        c.rect(box_x, y - row_h + 2*mm, box_s, box_s - 1*mm, fill=1, stroke=1)
        c.setFillColorRGB(*BOX_BORDER)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(box_x + box_s/2, y - row_h + 4*mm, num)
        c.setFont("Helvetica", 9)
        y -= row_h + 2*mm
    return y - 1*mm



def draw_written_answer(c, answer, y, n_lines=3):
    """Written answer: answer lines (pupil) or green italic text (answers)."""
    if answer:
        c.setFillColorRGB(*GREEN)
        c.setFont("Helvetica-Oblique", 8.5)
        lines = wrap_text(c, answer, "Helvetica-Oblique", 8.5, CW)
        for i, line in enumerate(lines):
            c.drawString(MARGIN, y - (i + 0.25) * 5*mm, line)
        return y - (len(lines) - 0.75) * 5*mm - 4*mm
    else:
        return answer_lines(c, y + 3*mm, n_lines)


def render_question(c, q, y, is_answer=False, n_lines=3, min_y=20*mm):
    """Render a single question. Returns new y, or None if no room."""
    qnum, qtype, qtext, options, correct = q

    # Estimate height
    label_h = len(wrap_text(c, qtext.split('\n')[0], "Helvetica-Bold", 9, CW - 8*mm)) * 12 + 4
    extra = 0
    if qtype == "mc":             extra = 14*mm
    elif qtype == "match":        extra = len(options) * 7*mm
    elif qtype in ("tick2","tick3"): extra = (len(options) // 3 + 1) * 6*mm
    elif qtype == "fill":         extra = 6*mm
    elif qtype == "order":        extra = len(options) * 6*mm
    elif qtype == "written":      extra = n_lines * 5.5*mm
    elif qtype == "short":        extra = 5.5*mm
    elif qtype == "short2":       extra = 11*mm
    elif qtype == "quote":        extra = 8*mm
    elif qtype == "true_false":   extra = 8*mm
    elif qtype == "select":       extra = 5.5*mm + ((len(options)+1)//2) * 6*mm + 2*mm
    elif qtype == "tick_v":        extra = len(options) * 7*mm + 1*mm
    elif qtype == "tf_table":      extra = 7*mm + len(options) * 9*mm + 2*mm
    elif qtype == "evidence2":     extra = 2 * (6.5*mm + 4*mm)
    elif qtype == "evidence2_ext": extra = 2 * (2 * 6.5*mm + 4*mm)
    elif qtype == "evidence3":     extra = 3 * (6.5*mm + 4*mm)
    elif qtype == "attrib_table":  extra = 8*mm + (len(options)-1) * 9*mm + 2*mm
    elif qtype == "impr_evidence": extra = 9*mm + (options if isinstance(options, int) else 2) * 34*mm + 2*mm
    total_est = label_h + extra + 8*mm

    if y - total_est < min_y:
        return None  # no room

    y -= 5*mm  # pre-question gap — visually groups label with its answer, not previous content

    # Draw question text
    c.setFillColorRGB(*DARK)
    c.setFont("Helvetica-Bold", 9)
    label = f"{qnum[1:]}. "
    lw = c.stringWidth(label, "Helvetica-Bold", 9)
    c.drawString(MARGIN, y, label)
    q_lines_all = qtext.split('\n')
    # For tick_v: draw "Tick one." / "Tick two." right-aligned on the same line as the question
    if qtype == "tick_v":
        n_correct = 1 if isinstance(correct, str) else len(correct)
        instr = f"Tick {'one' if n_correct == 1 else 'two'}."
        iw = c.stringWidth(instr, "Helvetica-Bold", 9)
        c.drawString(MARGIN + CW - iw, y, instr)
    # For fill-in-blank with a separate sentence line, only show the prompt as the label
    label_lines_text = q_lines_all[0]
    first_lines = wrap_text(c, label_lines_text, "Helvetica-Bold", 9, CW - lw)
    for i, line in enumerate(first_lines):
        c.drawString(MARGIN + lw, y - i * (9 * 1.35), line)
    y -= len(first_lines) * (9 * 1.35)
    # For non-fill types with additional lines (not used currently), draw them
    if qtype != "fill":
        for extra_line in q_lines_all[1:]:
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(*DARK)
            c.drawString(MARGIN, y, extra_line)
            y -= 9 * 1.35
    if qtype == "mc":
        if is_answer:
            y = draw_mc_answer(c, options, correct, y)
        else:
            y = draw_mc_pupil(c, options, y)
        y -= 1*mm  # extra gap after MC table

    elif qtype == "match":
        if is_answer:
            y = draw_match_answer(c, options, y)
        else:
            y = draw_match_pupil(c, options, y)
        y -= 1*mm  # extra gap after match table

    elif qtype in ("tick2", "tick3"):
        if is_answer:
            y = draw_tick_answer(c, options, correct, y)
        else:
            y = draw_tick_pupil(c, options, y)

    elif qtype == "fill":
        # The fill sentence is the last element of q_lines_all (or qtext if no \n)
        fill_sentence = q_lines_all[-1] if len(q_lines_all) > 1 else qtext
        y = draw_fill(c, fill_sentence, y, is_answer=is_answer, answer=correct or "")

    elif qtype == "order":
        if is_answer:
            y = draw_order_answer(c, options, correct, y)
        else:
            y = draw_order_pupil(c, options, y)

    elif qtype == "written":
        y = draw_written_answer(c, correct if is_answer else None, y, n_lines=n_lines)

    elif qtype == "short":
        y = draw_written_answer(c, correct if is_answer else None, y, n_lines=1)

    elif qtype == "short2":
        y = draw_written_answer(c, correct if is_answer else None, y, n_lines=2)

    elif qtype == "quote":
        if is_answer:
            y = draw_quote_answer(c, correct or "", y)
        else:
            y = draw_quote_pupil(c, y)

    elif qtype == "true_false":
        if is_answer:
            y = draw_true_false_answer(c, correct or "True", y)
        else:
            y = draw_true_false_pupil(c, y)

    elif qtype == "select":
        if is_answer:
            y = draw_select_answer(c, options, correct if isinstance(correct, list) else [correct], y)
        else:
            y = draw_select_pupil(c, options, y)

    elif qtype == "tick_v":
        if is_answer:
            y = draw_tick_v_answer(c, options, correct, y)
        else:
            y = draw_tick_v_pupil(c, options, correct, y)

    elif qtype == "tf_table":
        if is_answer:
            y = draw_tf_table_answer(c, options, correct, y)
        else:
            y = draw_tf_table_pupil(c, options, y)

    elif qtype == "evidence2":
        if is_answer:
            y = draw_evidence_answer(c, correct, y, lines_per_item=1)
        else:
            y = draw_evidence_pupil(c, 2, y, lines_per_item=1)

    elif qtype == "evidence2_ext":
        if is_answer:
            y = draw_evidence_answer(c, correct, y, lines_per_item=2)
        else:
            y = draw_evidence_pupil(c, 2, y, lines_per_item=2)

    elif qtype == "evidence3":
        if is_answer:
            y = draw_evidence_answer(c, correct, y, lines_per_item=1)
        else:
            y = draw_evidence_pupil(c, 3, y, lines_per_item=1)

    elif qtype == "attrib_table":
        if is_answer:
            y = draw_attrib_table_answer(c, options, correct, y)
        else:
            y = draw_attrib_table_pupil(c, options, y)

    elif qtype == "impr_evidence":
        n_rows = options if isinstance(options, int) else len(correct) if correct else 2
        if is_answer:
            y = draw_impr_evidence_answer(c, correct, y)
        else:
            y = draw_impr_evidence_pupil(c, n_rows, y)

    return y - 1*mm


def build_page(path, lesson_type, text, questions, date_str, is_answer, n_lines):
    """Build a single-page PDF."""
    c = canvas.Canvas(path, pagesize=A4)
    c.setFillColorRGB(*DARK)

    y = draw_header(c, lesson_type, date_str, KEY_Q,
                    LF[lesson_type], ICAN[lesson_type][0], ICAN[lesson_type][1])

    y = draw_text_box(c, text, y)

    min_y = 12*mm
    for q in questions:
        result = render_question(c, q, y, is_answer=is_answer,
                                 n_lines=n_lines, min_y=min_y)
        if result is None:
            # Drop Q7 if no room (last question in list)
            break
        y = result

    c.save()
    return path


def check_page_count(path):
    reader = PdfReader(path)
    return len(reader.pages)


def merge_pdfs(file_list, output_path):
    writer = PdfWriter()
    for f in file_list:
        for page in PdfReader(f).pages:
            writer.add_page(page)
    with open(output_path, "wb") as fh:
        writer.write(fh)


# ── Build all 12 individual PDFs ─────────────────────────────────────────────

lessons = [
    ("Vocabulary", STD_VOC, SUP_VOC, STD_VOC_QS, SUP_VOC_QS, DATES["Vocabulary"]),
    ("Retrieval",  STD_RET, SUP_RET, STD_RET_QS, SUP_RET_QS, DATES["Retrieval"]),
    ("Inference",  STD_INF, SUP_INF, STD_INF_QS, SUP_INF_QS, DATES["Inference"]),
]

built = {
    "std_pupil": [], "sup_pupil": [],
    "std_ans": [], "sup_ans": [],
}

for lesson_type, std_text, sup_text, std_qs, sup_qs, date_str in lessons:
    lt = lesson_type
    print(f"Building {lt}...")

    # Standard pupil
    p = f"{OUT_DIR}/{lt}_Standard_Pupil.pdf"
    build_page(p, lt, std_text, std_qs, date_str, is_answer=False, n_lines=3)
    pages = check_page_count(p)
    if pages > 1:
        print(f"  WARNING: {lt} Standard overflows ({pages} pages) — dropping Q7")
        build_page(p, lt, std_text, std_qs[:-1], date_str, is_answer=False, n_lines=3)
    print(f"  Standard Pupil: {check_page_count(p)} page(s)")
    built["std_pupil"].append(p)

    # Supported pupil
    p = f"{OUT_DIR}/{lt}_Supported_Pupil.pdf"
    build_page(p, lt, sup_text, sup_qs, date_str, is_answer=False, n_lines=2)
    pages = check_page_count(p)
    if pages > 1:
        print(f"  WARNING: {lt} Supported overflows ({pages} pages) — dropping Q5")
        build_page(p, lt, sup_text, sup_qs[:-1], date_str, is_answer=False, n_lines=2)
    print(f"  Supported Pupil: {check_page_count(p)} page(s)")
    built["sup_pupil"].append(p)

    # Standard answers
    p = f"{OUT_DIR}/{lt}_Standard_Answers.pdf"
    build_page(p, lt, std_text, std_qs, date_str, is_answer=True, n_lines=3)
    print(f"  Standard Answers: {check_page_count(p)} page(s)")
    built["std_ans"].append(p)

    # Supported answers
    p = f"{OUT_DIR}/{lt}_Supported_Answers.pdf"
    build_page(p, lt, sup_text, sup_qs, date_str, is_answer=True, n_lines=2)
    print(f"  Supported Answers: {check_page_count(p)} page(s)")
    built["sup_ans"].append(p)

print("\nMerging...")

# Standard Pupil: Voc + Ret + Inf
merge_pdfs(built["std_pupil"],
           "/mnt/user-data/outputs/T5W2_Standard_Pupil.pdf")

# Supported Pupil: Voc + Ret + Inf
merge_pdfs(built["sup_pupil"],
           "/mnt/user-data/outputs/T5W2_Supported_Pupil.pdf")

# All Answers: Voc Std, Voc Sup, Ret Std, Ret Sup, Inf Std, Inf Sup
ans_order = []
for i in range(3):
    ans_order.append(built["std_ans"][i])
    ans_order.append(built["sup_ans"][i])
merge_pdfs(ans_order,
           "/mnt/user-data/outputs/T5W2_All_Answers.pdf")

# Clean up individual files
import shutil
shutil.rmtree(OUT_DIR)

print("Done.")
print("  T5W2_Standard_Pupil.pdf:", PdfReader("/mnt/user-data/outputs/T5W2_Standard_Pupil.pdf").pages.__len__(), "pages")
print("  T5W2_Supported_Pupil.pdf:", PdfReader("/mnt/user-data/outputs/T5W2_Supported_Pupil.pdf").pages.__len__(), "pages")
print("  T5W2_All_Answers.pdf:", PdfReader("/mnt/user-data/outputs/T5W2_All_Answers.pdf").pages.__len__(), "pages")
