"""
T6W6 Being a Reader — full build
New skill: one-line header, per-class day PDFs, all adapted pupils, single ZIP output.
"""
import sys, os, shutil, zipfile, random
sys.path.insert(0, '/home/claude')

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter

W, H = A4
MARGIN = 8 * mm
CW = W - 2 * MARGIN

BOX_BORDER = (0.173, 0.173, 0.424)
BOX_BG     = (0.941, 0.941, 0.973)
GREEN      = (0.102, 0.478, 0.102)
DARK       = (0.133, 0.133, 0.133)
GREY_LINE  = (0.6, 0.6, 0.6)
ICON_PATH  = "/home/claude/reader_icon_saved.png"

WORK   = "/home/claude/pdfs_v2"
OUT    = "/mnt/user-data/outputs"
os.makedirs(WORK, exist_ok=True)

from t6w6_v2_content import *

# ── Layout helpers ──────────────────────────────────────────────────────────

def wrap(c, text, font, size, max_w):
    words = text.split()
    lines, line = [], ''
    for w in words:
        test = (line + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines or ['']

def answer_lines(c, y, n, gap=6.5*mm):
    c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    for i in range(n):
        ly = y - (i+1)*gap
        c.line(MARGIN, ly, MARGIN+CW, ly)
    return y - n*gap - 2*mm

# ── Header (new one-line format) ────────────────────────────────────────────

def draw_header(c, lesson_type, date_str, key_q, lf, ican1, ican2, pupil_name=None):
    """
    Row 1: "Key Question" [icon] day date  — all left-to-right on one line.
    If pupil_name, shows "Key Question" [icon] "Name — LessonType" instead.
    """
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(*DARK)
    c.drawString(MARGIN, y - 5*mm, "Key Question")
    icon_x = MARGIN + 26*mm
    try:
        c.drawImage(ICON_PATH, icon_x, y - 7*mm, width=7*mm, height=7*mm,
                    mask='auto', preserveAspectRatio=True)
    except Exception:
        pass
    c.setFont("Helvetica", 8)
    if pupil_name:
        label = f"{pupil_name} \u2014 {lesson_type}"
    else:
        day, date = date_str
        label = f"{day} {date}"
    c.drawString(icon_x + 8*mm, y - 5*mm, label)
    y -= 7*mm

    c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.3)
    c.line(MARGIN, y, MARGIN+CW, y); y -= 1*mm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(*BOX_BORDER)
    c.drawString(MARGIN, y - 4*mm, key_q)
    kq_w = c.stringWidth(key_q, "Helvetica-Bold", 10)
    c.setLineWidth(0.5); c.setStrokeColorRGB(*BOX_BORDER)
    c.line(MARGIN, y - 5*mm, MARGIN + kq_w, y - 5*mm); y -= 6*mm

    c.setFont("Helvetica", 8); c.setFillColorRGB(*DARK)
    c.drawString(MARGIN, y - 3.5*mm, lf);  y -= 4.5*mm
    c.drawString(MARGIN, y - 3.5*mm, ican1); y -= 4*mm
    c.drawString(MARGIN, y - 3.5*mm, ican2); y -= 4.5*mm

    c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.5)
    c.line(MARGIN, y, MARGIN+CW, y); y -= 2*mm
    return y

def draw_text_box(c, text, y_top, font_size=10.5):
    lines = wrap(c, text, "Helvetica", font_size, CW - 6*mm)
    lh = font_size * 1.4
    bh = len(lines)*lh + 5*mm
    c.setFillColorRGB(*BOX_BG); c.setStrokeColorRGB(*BOX_BORDER); c.setLineWidth(0.8)
    c.roundRect(MARGIN, y_top - bh, CW, bh, 2*mm, fill=1, stroke=1)
    c.setFillColorRGB(*DARK); c.setFont("Helvetica", font_size)
    ty = y_top - 3*mm - font_size * 0.72
    for l in lines:
        c.drawString(MARGIN + 3*mm, ty, l); ty -= lh
    return y_top - bh - 3*mm

def draw_glossary(c, glossary, y_top):
    """Small glossary box at top of page (above text box)."""
    items = list(glossary.items())
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColorRGB(*DARK)
    bh = len(items) * 5*mm + 4*mm
    c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.roundRect(MARGIN, y_top - bh, CW, bh, 1*mm, fill=0, stroke=1)
    ty = y_top - 2*mm
    for word, defn in items:
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(MARGIN + 2*mm, ty - 3.5*mm, word + ":")
        wd = c.stringWidth(word + ": ", "Helvetica-Bold", 7.5)
        c.setFont("Helvetica", 7.5)
        c.drawString(MARGIN + 2*mm + wd, ty - 3.5*mm, defn)
        ty -= 5*mm
    return y_top - bh - 2*mm

# ── Question renderers ──────────────────────────────────────────────────────

def q_label(c, qnum, text, y):
    c.setFillColorRGB(*BOX_BORDER); c.setFont("Helvetica-Bold", 9)
    lbl = f"{qnum[1:]}. "
    lw = c.stringWidth(lbl, "Helvetica-Bold", 9)
    c.drawString(MARGIN, y, lbl)
    ls = wrap(c, text, "Helvetica-Bold", 9, CW - lw)
    for i, l in enumerate(ls):
        c.drawString(MARGIN + lw, y - i*(9*1.35), l)
    return y - len(ls)*(9*1.35) - 1*mm

def draw_mc_pupil(c, options, y):
    col_w = CW/2; rh = 6*mm
    for row in range(2):
        for col in range(2):
            idx = row*2+col
            if idx >= len(options): break
            x = MARGIN + col*col_w; ry = y - row*rh
            c.setFillColorRGB(1,1,1); c.setStrokeColorRGB(.7,.7,.7); c.setLineWidth(0.4)
            c.rect(x, ry-rh, col_w, rh, fill=1, stroke=1)
            c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
            c.drawString(x+2*mm, ry-rh+2*mm, options[idx])
    return y - 2*rh - 1.5*mm

def draw_mc_answer(c, options, correct, y):
    col_w = CW/2; rh = 6*mm
    for row in range(2):
        for col in range(2):
            idx = row*2+col
            if idx >= len(options): break
            x = MARGIN + col*col_w; ry = y - row*rh
            ok = options[idx] == correct
            c.setFillColorRGB(0.85,0.95,0.85) if ok else c.setFillColorRGB(1,1,1)
            c.setStrokeColorRGB(.7,.7,.7); c.setLineWidth(0.4)
            c.rect(x, ry-rh, col_w, rh, fill=1, stroke=1)
            if ok:
                c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 8.5)
                c.drawString(x+2*mm, ry-rh+2*mm, options[idx]+" \u2713")
            else:
                c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
                c.drawString(x+2*mm, ry-rh+2*mm, options[idx])
    return y - 2*rh - 1.5*mm

def draw_tick_v_pupil(c, options, y):
    """KS2-style vertical tick — square box on right side of each option."""
    rh = 7*mm
    for i, opt in enumerate(options):
        ry = y - i*rh
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 2*mm, ry - 4*mm, opt)
        c.setStrokeColorRGB(0.3,0.3,0.3); c.setLineWidth(0.5)
        c.rect(MARGIN + CW - 6*mm, ry - 6*mm, 5*mm, 5*mm, fill=0, stroke=1)
    return y - len(options)*rh - 1*mm

def draw_tick_v_answer(c, options, correct, y):
    rh = 7*mm
    correct_list = [correct] if isinstance(correct, str) else list(correct)
    for i, opt in enumerate(options):
        ry = y - i*rh
        ok = opt in correct_list
        if ok:
            c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColorRGB(*DARK); c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 2*mm, ry - 4*mm, opt)
        c.setStrokeColorRGB(0.3,0.3,0.3); c.setLineWidth(0.5)
        c.rect(MARGIN + CW - 6*mm, ry - 6*mm, 5*mm, 5*mm,
               fill=1 if ok else 0, stroke=1)
        if ok:
            c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 11)
            c.drawString(MARGIN + CW - 5.5*mm, ry - 5.5*mm, "\u2713")
    return y - len(options)*rh - 1*mm

def draw_fill(c, sentence, y, is_answer=False, answer=""):
    parts = sentence.split("______________")
    answers = [a.strip() for a in answer.split("/")] if answer else []
    x = MARGIN; BLANK_W = 28*mm
    c.setFont("Helvetica", 9); c.setFillColorRGB(*DARK)
    line_y = y - 4*mm
    for pi, part in enumerate(parts):
        for w in part.split():
            ww = c.stringWidth(w+" ", "Helvetica", 9)
            if x + ww > MARGIN+CW: line_y -= 5*mm; x = MARGIN
            c.drawString(x, line_y, w+" "); x += ww
        if pi < len(parts)-1:
            if x + BLANK_W > MARGIN+CW: line_y -= 5*mm; x = MARGIN
            if is_answer and pi < len(answers):
                c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 9)
                c.drawString(x+1*mm, line_y, answers[pi])
                c.setFillColorRGB(*DARK); c.setFont("Helvetica", 9)
            else:
                c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.5)
                c.line(x, line_y-1*mm, x+BLANK_W, line_y-1*mm)
            x += BLANK_W + 2*mm
    return line_y - 5*mm

def draw_match_pupil(c, pairs, y):
    lw = CW*0.28; rw = CW*0.48; gap = CW - lw - rw
    rh = 7*mm
    c.setStrokeColorRGB(0.7,0.7,0.7); c.setLineWidth(0.4)
    rights = [r for _,r in pairs]
    scrambled = rights[1:] + rights[:1]
    for i,(left,_) in enumerate(pairs):
        ry = y - i*rh
        c.setFillColorRGB(1,1,1)
        c.roundRect(MARGIN, ry-rh+1*mm, lw, rh-2*mm, 1*mm, fill=1, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8)
        c.drawString(MARGIN+2*mm, ry-rh+3*mm, left)
        rx = MARGIN+lw+gap
        c.setFillColorRGB(1,1,1)
        c.roundRect(rx, ry-rh+1*mm, rw, rh-2*mm, 1*mm, fill=1, stroke=1)
        c.setFillColorRGB(*DARK)
        dlines = wrap(c, scrambled[i], "Helvetica", 8, rw-4*mm)
        c.drawString(rx+2*mm, ry-rh+3*mm, dlines[0] if dlines else "")
    return y - len(pairs)*rh - 1.5*mm

def draw_match_answer(c, pairs, y):
    lw = CW*0.28; rw = CW*0.48; gap = CW - lw - rw; rh = 7*mm
    c.setStrokeColorRGB(0.7,0.7,0.7); c.setLineWidth(0.4)
    rights = [r for _,r in pairs]
    scrambled = rights[1:] + rights[:1]
    for i,(left,right) in enumerate(pairs):
        ry = y - i*rh
        c.setFillColorRGB(1,1,1)
        c.roundRect(MARGIN, ry-rh+1*mm, lw, rh-2*mm, 1*mm, fill=1, stroke=1)
        c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 8)
        c.drawString(MARGIN+2*mm, ry-rh+3*mm, left)
        # Connector
        c.setStrokeColorRGB(*GREEN); c.setLineWidth(1.2)
        mx = MARGIN+lw+gap/2
        c.line(MARGIN+lw+1*mm, ry-rh+rh/2, MARGIN+lw+gap-1*mm, ry-rh+rh/2)
        rx = MARGIN+lw+gap
        c.setFillColorRGB(0.9,1.0,0.9)
        c.roundRect(rx, ry-rh+1*mm, rw, rh-2*mm, 1*mm, fill=1, stroke=1)
        c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Oblique", 8)
        dlines = wrap(c, right, "Helvetica-Oblique", 8, rw-4*mm)
        c.drawString(rx+2*mm, ry-rh+3*mm, dlines[0] if dlines else "")
    return y - len(pairs)*rh - 1.5*mm

def draw_short(c, y, n_lines=1, is_answer=False, answer=None):
    if is_answer and answer:
        c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Oblique", 8.5)
        ls = wrap(c, answer, "Helvetica-Oblique", 8.5, CW)
        for l in ls:
            c.drawString(MARGIN, y, l); y -= 8.5*1.4
        return y - 2*mm
    return answer_lines(c, y, n_lines)

def draw_short2(c, y, n_lines=2, is_answer=False, answer=None):
    return draw_short(c, y, n_lines, is_answer, answer)

def draw_quote_pupil(c, y):
    bh = 12*mm
    c.setFillColorRGB(0.94,0.94,0.94); c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.roundRect(MARGIN, y-bh, CW, bh, 2*mm, fill=1, stroke=1)
    c.setFillColorRGB(0.6,0.6,0.6); c.setFont("Helvetica-Oblique", 8)
    c.drawString(MARGIN+3*mm, y-bh+3*mm, "Find and copy the phrase from the text...")
    return y - bh - 2*mm

def draw_quote_answer(c, answer, y):
    bh = 12*mm
    c.setFillColorRGB(0.88,0.96,0.88); c.setStrokeColorRGB(*GREEN); c.setLineWidth(0.6)
    c.roundRect(MARGIN, y-bh, CW, bh, 2*mm, fill=1, stroke=1)
    c.setFillColorRGB(*GREEN); c.setFont("Helvetica-BoldOblique", 9)
    ls = wrap(c, f"\u201c{answer}\u201d", "Helvetica-BoldOblique", 9, CW-6*mm)
    ty = y - bh/2 + (len(ls)*9*1.2)/2 - 9*0.6
    for l in ls:
        c.drawString(MARGIN+3*mm, ty, l); ty -= 9*1.3
    return y - bh - 2*mm

def draw_true_false_pupil(c, y):
    for lbl in ["True", "False"]:
        c.setStrokeColorRGB(0.4,0.4,0.4); c.setLineWidth(0.5)
        c.circle(MARGIN+5*mm, y-3*mm, 3*mm, fill=0, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 9)
        c.drawString(MARGIN+10*mm, y-4.5*mm, lbl)
        y -= 8*mm
    return y

def draw_true_false_answer(c, correct, y):
    for lbl in ["True", "False"]:
        ok = lbl == correct
        if ok:
            c.setFillColorRGB(0.85,0.95,0.85)
            c.circle(MARGIN+5*mm, y-3*mm, 3*mm, fill=1, stroke=1)
            c.setStrokeColorRGB(*GREEN); c.setLineWidth(1.2)
            c.circle(MARGIN+5*mm, y-3*mm, 3*mm, fill=0, stroke=1)
            c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColorRGB(1,1,1)
            c.setStrokeColorRGB(0.4,0.4,0.4); c.setLineWidth(0.5)
            c.circle(MARGIN+5*mm, y-3*mm, 3*mm, fill=0, stroke=1)
            c.setFillColorRGB(*DARK); c.setFont("Helvetica", 9)
        c.drawString(MARGIN+10*mm, y-4.5*mm, lbl + (" \u2713" if ok else ""))
        y -= 8*mm
    return y

def draw_select_pupil(c, options, y):
    rh = 6*mm
    for i, opt in enumerate(options):
        ry = y - i*rh
        c.setStrokeColorRGB(0.4,0.4,0.4); c.setLineWidth(0.5)
        c.rect(MARGIN+1*mm, ry-4*mm, 4*mm, 4*mm, fill=0, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN+7*mm, ry-3.5*mm, opt)
    return y - len(options)*rh - 2*mm

def draw_select_answer(c, options, correct, y):
    rh = 6*mm
    for i, opt in enumerate(options):
        ry = y - i*rh
        ok = opt in correct
        if ok:
            c.setFillColorRGB(0.85,0.95,0.85)
            c.setStrokeColorRGB(*GREEN); c.setLineWidth(0.8)
        else:
            c.setFillColorRGB(1,1,1)
            c.setStrokeColorRGB(0.4,0.4,0.4); c.setLineWidth(0.5)
        c.rect(MARGIN+1*mm, ry-4*mm, 4*mm, 4*mm, fill=1, stroke=1)
        if ok:
            c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 10)
            c.drawString(MARGIN+1.5*mm, ry-4.5*mm, "\u2713")
            c.setFont("Helvetica-Bold", 8.5)
        else:
            c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN+7*mm, ry-3.5*mm, opt + (" \u2713" if ok else ""))
    return y - len(options)*rh - 2*mm

def draw_tf_table_pupil(c, stmts, y):
    hdr_h = 7*mm; row_h = 9*mm; col_t = CW*0.62; col_t_x = MARGIN+col_t
    col_w = (CW - col_t) / 2
    # Header
    c.setFillColorRGB(0.88,0.88,0.95); c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN, y-hdr_h, col_t, hdr_h, fill=1, stroke=1)
    c.rect(col_t_x, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
    c.rect(col_t_x+col_w, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN+2*mm, y-hdr_h+2*mm, "Statement")
    c.drawCentredString(col_t_x+col_w/2, y-hdr_h+2*mm, "True")
    c.drawCentredString(col_t_x+col_w+col_w/2, y-hdr_h+2*mm, "False")
    y -= hdr_h
    for stmt in stmts:
        c.setFillColorRGB(1,1,1)
        c.rect(MARGIN, y-row_h, col_t, row_h, fill=1, stroke=1)
        c.rect(col_t_x, y-row_h, col_w, row_h, fill=1, stroke=1)
        c.rect(col_t_x+col_w, y-row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8)
        ls = wrap(c, stmt, "Helvetica", 8, col_t-4*mm)
        ty = y - row_h/2 + len(ls)*8*1.2/2 - 8*0.6
        for l in ls:
            c.drawString(MARGIN+2*mm, ty, l); ty -= 8*1.3
        y -= row_h
    return y - 2*mm

def draw_tf_table_answer(c, stmts, correct, y):
    hdr_h = 7*mm; row_h = 9*mm; col_t = CW*0.62; col_t_x = MARGIN+col_t
    col_w = (CW - col_t) / 2
    c.setFillColorRGB(0.88,0.88,0.95); c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN, y-hdr_h, col_t, hdr_h, fill=1, stroke=1)
    c.rect(col_t_x, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
    c.rect(col_t_x+col_w, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
    c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN+2*mm, y-hdr_h+2*mm, "Statement")
    c.drawCentredString(col_t_x+col_w/2, y-hdr_h+2*mm, "True")
    c.drawCentredString(col_t_x+col_w+col_w/2, y-hdr_h+2*mm, "False")
    y -= hdr_h
    for i, stmt in enumerate(stmts):
        ans = correct[i] if i < len(correct) else "True"
        c.setFillColorRGB(1,1,1)
        c.rect(MARGIN, y-row_h, col_t, row_h, fill=1, stroke=1)
        for j, col_ans in enumerate(["True","False"]):
            cx = col_t_x + j*col_w
            ok = (ans == col_ans)
            c.setFillColorRGB(0.85,0.95,0.85) if ok else c.setFillColorRGB(1,1,1)
            c.rect(cx, y-row_h, col_w, row_h, fill=1, stroke=1)
            if ok:
                c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(cx+col_w/2, y-row_h+2*mm, "\u2713")
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8)
        ls = wrap(c, stmt, "Helvetica", 8, col_t-4*mm)
        ty = y - row_h/2 + len(ls)*8*1.2/2 - 8*0.6
        for l in ls:
            c.drawString(MARGIN+2*mm, ty, l); ty -= 8*1.3
        y -= row_h
    return y - 2*mm

def draw_evidence2_pupil(c, y, n_lines=1):
    for i in range(2):
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y - 4*mm, f"{i+1}.")
        y = answer_lines(c, y - 4*mm, n_lines)
        y -= 2*mm
    return y

def draw_evidence2_answer(c, answers, y, n_lines=1):
    for i, ans in enumerate(answers[:2]):
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y - 4*mm, f"{i+1}.")
        c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Oblique", 8.5)
        ls = wrap(c, ans, "Helvetica-Oblique", 8.5, CW - 6*mm)
        for j, l in enumerate(ls):
            c.drawString(MARGIN+6*mm, y-4*mm - j*8.5*1.3, l)
        y -= 4*mm + len(ls)*8.5*1.3 + 3*mm
    return y

def draw_evidence2_ext_pupil(c, y, n_lines=2):
    for i in range(2):
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y - 4*mm, f"{i+1}.")
        y = answer_lines(c, y - 4*mm, n_lines); y -= 3*mm
    return y

def draw_evidence2_ext_answer(c, answers, y):
    return draw_evidence2_answer(c, answers, y, n_lines=2)

def draw_evidence3_pupil(c, y, n_lines=1):
    for i in range(3):
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y-4*mm, f"{i+1}.")
        y = answer_lines(c, y-4*mm, n_lines); y -= 2*mm
    return y

def draw_order_pupil(c, events, y):
    rh = 6*mm
    for ev in events:
        c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
        c.rect(MARGIN+CW-8*mm, y-rh+1*mm, 7*mm, rh-2*mm, fill=0, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN+2*mm, y-4*mm, ev)
        y -= rh
    return y - 2*mm

def draw_order_answer(c, events, correct_order, y):
    rh = 6*mm; nums = correct_order.split(",")
    for i, ev in enumerate(events):
        c.setFillColorRGB(0.88,0.96,0.88); c.setStrokeColorRGB(*GREEN); c.setLineWidth(0.5)
        c.rect(MARGIN+CW-8*mm, y-rh+1*mm, 7*mm, rh-2*mm, fill=1, stroke=1)
        c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 9)
        num = nums[i] if i < len(nums) else "?"
        c.drawCentredString(MARGIN+CW-4.5*mm, y-rh+2*mm, num)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN+2*mm, y-4*mm, ev)
        y -= rh
    return y - 2*mm

def draw_attrib_table_pupil(c, options, y):
    headers = options[0]; rows = options[1:]
    n_cols = len(headers); hdr_h = 7*mm; row_h = 9*mm
    stat_w = CW * 0.55; col_w = (CW - stat_w) / n_cols
    c.setFillColorRGB(0.88,0.88,0.95); c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN, y-hdr_h, stat_w, hdr_h, fill=1, stroke=1)
    for j, hdr in enumerate(headers):
        cx = MARGIN + stat_w + j*col_w
        c.rect(cx, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx+col_w/2, y-hdr_h+2*mm, hdr)
    y -= hdr_h
    for row in rows:
        c.setFillColorRGB(1,1,1)
        c.rect(MARGIN, y-row_h, stat_w, row_h, fill=1, stroke=1)
        for j in range(n_cols):
            cx = MARGIN + stat_w + j*col_w
            c.rect(cx, y-row_h, col_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8)
        ls = wrap(c, row, "Helvetica", 8, stat_w-4*mm)
        ty = y - row_h/2 + len(ls)*8*1.2/2 - 8*0.6
        for l in ls:
            c.drawString(MARGIN+2*mm, ty, l); ty -= 8*1.3
        y -= row_h
    return y - 2*mm

def draw_attrib_table_answer(c, options, correct, y):
    headers = options[0]; rows = options[1:]
    n_cols = len(headers); hdr_h = 7*mm; row_h = 9*mm
    stat_w = CW * 0.55; col_w = (CW - stat_w) / n_cols
    c.setFillColorRGB(0.88,0.88,0.95); c.setStrokeColorRGB(*GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN, y-hdr_h, stat_w, hdr_h, fill=1, stroke=1)
    for j, hdr in enumerate(headers):
        cx = MARGIN + stat_w + j*col_w
        c.rect(cx, y-hdr_h, col_w, hdr_h, fill=1, stroke=1)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx+col_w/2, y-hdr_h+2*mm, hdr)
    y -= hdr_h
    for ri, row in enumerate(rows):
        c.setFillColorRGB(1,1,1)
        c.rect(MARGIN, y-row_h, stat_w, row_h, fill=1, stroke=1)
        ans = correct[ri] if ri < len(correct) else headers[0]
        for j, hdr in enumerate(headers):
            cx = MARGIN + stat_w + j*col_w
            ok = hdr == ans
            c.setFillColorRGB(0.85,0.95,0.85) if ok else c.setFillColorRGB(1,1,1)
            c.rect(cx, y-row_h, col_w, row_h, fill=1, stroke=1)
            if ok:
                c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 11)
                c.drawCentredString(cx+col_w/2, y-row_h+2*mm, "\u2713")
        c.setFillColorRGB(*DARK); c.setFont("Helvetica", 8)
        ls = wrap(c, row, "Helvetica", 8, stat_w-4*mm)
        ty = y - row_h/2 + len(ls)*8*1.2/2 - 8*0.6
        for l in ls:
            c.drawString(MARGIN+2*mm, ty, l); ty -= 8*1.3
        y -= row_h
    return y - 2*mm

def draw_written_pupil(c, y, n_lines=3):
    return answer_lines(c, y, n_lines)

def draw_written_answer(c, answer, y):
    c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Oblique", 8.5)
    ls = wrap(c, answer, "Helvetica-Oblique", 8.5, CW)
    for l in ls:
        c.drawString(MARGIN, y, l); y -= 8.5*1.4
    return y - 2*mm

# ── Height estimates ────────────────────────────────────────────────────────

def est_height(c, q, n_lines):
    qnum, qtype, qtext, options, correct = q
    q_lines = qtext.split('\n')
    lh = len(wrap(c, q_lines[0], "Helvetica-Bold", 9, CW - 8*mm)) * 12 + 4
    ex = 0
    if qtype == "mc":             ex = 14*mm
    elif qtype == "match":        ex = len(options) * 7*mm
    elif qtype == "fill":         ex = 6*mm
    elif qtype == "order":        ex = len(options) * 6*mm
    elif qtype == "written":      ex = n_lines * 5.5*mm
    elif qtype == "short":        ex = 5.5*mm
    elif qtype == "short2":       ex = 11*mm
    elif qtype == "quote":        ex = 14*mm
    elif qtype == "true_false":   ex = 16*mm
    elif qtype == "select":       ex = 5.5*mm + len(options) * 6*mm
    elif qtype == "tick_v":       ex = len(options) * 7*mm
    elif qtype == "tf_table":     ex = 7*mm + len(options) * 9*mm
    elif qtype == "evidence2":    ex = 2*(6.5*mm + 4*mm) + 4*mm
    elif qtype == "evidence2_ext":ex = 2*(2*6.5*mm + 4*mm) + 6*mm
    elif qtype == "evidence3":    ex = 3*(6.5*mm + 4*mm)
    elif qtype == "attrib_table": ex = 7*mm + (len(options)-1) * 9*mm
    return lh + ex + 3*mm

# ── render_question ─────────────────────────────────────────────────────────

def render_question(c, q, y, is_answer=False, n_lines=3, min_y=20*mm):
    qnum, qtype, qtext, options, correct = q
    q_lines = qtext.split('\n')

    # Append [Tick one.] / [Tick two.] inline for tick_v
    label_text = q_lines[0]
    if qtype == "tick_v":
        n_c = 1 if isinstance(correct, str) else len(correct)
        label_text += f"  [Tick {'one' if n_c == 1 else 'two'}.]"

    if y - est_height(c, q, n_lines) < min_y:
        return None

    y = q_label(c, qnum, label_text, y)

    if qtype == "mc":
        y = draw_mc_answer(c, options, correct, y) if is_answer else draw_mc_pupil(c, options, y)
        y -= 1*mm
    elif qtype == "match":
        y = draw_match_answer(c, options, y) if is_answer else draw_match_pupil(c, options, y)
        y -= 1*mm
    elif qtype == "fill":
        fs = q_lines[-1] if len(q_lines) > 1 else qtext
        y = draw_fill(c, fs, y, is_answer=is_answer, answer=correct or "")
    elif qtype == "order":
        y = draw_order_answer(c, options, correct, y) if is_answer else draw_order_pupil(c, options, y)
    elif qtype == "written":
        y = draw_written_answer(c, correct, y) if is_answer else draw_written_pupil(c, y, n_lines)
    elif qtype == "short":
        y = draw_short(c, y, 1, is_answer, correct)
    elif qtype == "short2":
        y = draw_short2(c, y, 2, is_answer, correct)
    elif qtype == "quote":
        y = draw_quote_answer(c, correct, y) if is_answer else draw_quote_pupil(c, y)
    elif qtype == "true_false":
        y = draw_true_false_answer(c, correct, y) if is_answer else draw_true_false_pupil(c, y)
    elif qtype == "select":
        y = draw_select_answer(c, options, correct, y) if is_answer else draw_select_pupil(c, options, y)
    elif qtype == "tick_v":
        y = draw_tick_v_answer(c, options, correct, y) if is_answer else draw_tick_v_pupil(c, options, y)
    elif qtype == "tf_table":
        y = draw_tf_table_answer(c, options, correct, y) if is_answer else draw_tf_table_pupil(c, options, y)
    elif qtype == "evidence2":
        y = draw_evidence2_answer(c, correct, y) if is_answer else draw_evidence2_pupil(c, y, 1)
    elif qtype == "evidence2_ext":
        y = draw_evidence2_ext_answer(c, correct, y) if is_answer else draw_evidence2_ext_pupil(c, y, 2)
    elif qtype == "evidence3":
        if is_answer and correct:
            for i, ans in enumerate(correct[:3]):
                c.setFont("Helvetica-Bold",9); c.setFillColorRGB(*DARK)
                c.drawString(MARGIN, y-4*mm, f"{i+1}.")
                c.setFont("Helvetica-Oblique",8.5); c.setFillColorRGB(*GREEN)
                c.drawString(MARGIN+6*mm, y-4*mm, ans)
                y -= 8.5*1.4+4*mm
        else:
            y = draw_evidence3_pupil(c, y)
    elif qtype == "attrib_table":
        y = draw_attrib_table_answer(c, options, correct, y) if is_answer else draw_attrib_table_pupil(c, options, y)

    return y - 3*mm

# ── build_page ──────────────────────────────────────────────────────────────

def build_page(path, lesson_type, text, questions, date_str, is_answer,
               n_lines=3, pupil_name=None, glossary=None):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFillColorRGB(*DARK)
    y = draw_header(c, lesson_type, date_str, KEY_Q,
                    LF[lesson_type], ICAN[lesson_type][0], ICAN[lesson_type][1],
                    pupil_name=pupil_name)
    if glossary:
        y = draw_glossary(c, glossary, y)
    y = draw_text_box(c, text, y)
    for q in questions:
        r = render_question(c, q, y, is_answer=is_answer, n_lines=n_lines, min_y=12*mm)
        if r is None: break
        y = r
    c.save()

def check_pages(path):
    return len(PdfReader(path).pages)

def merge(files, out):
    w = PdfWriter()
    for f in files:
        for pg in PdfReader(f).pages:
            w.add_page(pg)
    with open(out, "wb") as fh:
        w.write(fh)

# ── Level data lookup ───────────────────────────────────────────────────────

LEVEL_DATA = {
    "Y4-standard": {
        "Vocabulary": (STD_VOC, STD_VOC_QS, 3),
        "Retrieval":  (STD_RET, STD_RET_QS, 3),
        "Inference":  (STD_INF, STD_INF_QS, 3),
    },
    "Y4-adapted": {
        "Vocabulary": (ADP_VOC, ADP_VOC_QS, 2),
        "Retrieval":  (ADP_RET, ADP_RET_QS, 2),
        "Inference":  (ADP_INF, ADP_INF_QS, 2),
    },
    "Y3": {
        "Vocabulary": (Y3_VOC_TEXT, Y3_VOC_QS, 2),
        "Retrieval":  (Y3_RET_TEXT, Y3_RET_QS, 2),
        "Inference":  (Y3_INF_TEXT, Y3_INF_QS, 2),
    },
    "Y2": {
        "Vocabulary": (Y2_VOC_TEXT, Y2_VOC_QS, 1),
        "Retrieval":  (Y2_RET_TEXT, Y2_RET_QS, 1),
        "Inference":  (Y2_INF_TEXT, Y2_INF_QS, 1),
    },
    "Y1": {
        "Vocabulary": (Y1_VOC_TEXT, Y1_VOC_QS, 1),
        "Retrieval":  (Y1_RET_TEXT, Y1_RET_QS, 1),
        "Inference":  (Y1_INF_TEXT, Y1_INF_QS, 1),
    },
    "Ph2": {
        "Vocabulary": (PH2_VOC_TEXT, PH2_VOC_QS, 0),
        "Retrieval":  (PH2_RET_TEXT, PH2_RET_QS, 0),
        "Inference":  (PH2_INF_TEXT, PH2_INF_QS, 0),
    },
}

def get_glossary(level, lesson):
    if level == "Ph2":
        return PH2_GLOSSARY.get(lesson)
    return None

# ── Build all individual pages ──────────────────────────────────────────────

LESSONS = ["Vocabulary", "Retrieval", "Inference"]

print("Building standard pages...")
std_pupil_pages = []
std_ans_pages   = []
for lesson in LESSONS:
    text, qs, nl = LEVEL_DATA["Y4-standard"][lesson]
    date = DATES[lesson]
    p = f"{WORK}/std_{lesson}_pupil.pdf"
    build_page(p, lesson, text, qs, date, False, nl)
    std_pupil_pages.append(p)
    a = f"{WORK}/std_{lesson}_ans.pdf"
    build_page(a, lesson, text, qs, date, True, nl)
    std_ans_pages.append(a)
    print(f"  {lesson}: {check_pages(p)}p pupil, {check_pages(a)}p ans")

print("Building adapted pages...")
adapted_pupil_pages = {}   # {name: [voc, ret, inf]}
adapted_ans_pages   = {}

all_adapted = LMES_ADAPTED + IM_ADAPTED
for pupil in all_adapted:
    name  = pupil["name"]
    level = pupil["level"]
    pages_p = []; pages_a = []
    for lesson in LESSONS:
        if level not in LEVEL_DATA:
            print(f"  WARNING: unknown level {level} for {name}")
            continue
        text, qs, nl = LEVEL_DATA[level][lesson]
        date = DATES[lesson]
        gloss = get_glossary(level, lesson)
        p = f"{WORK}/{name}_{lesson}_pupil.pdf"
        build_page(p, lesson, text, qs, date, False, nl,
                   pupil_name=name, glossary=gloss)
        pages_p.append(p)
        a = f"{WORK}/{name}_{lesson}_ans.pdf"
        build_page(a, lesson, text, qs, date, True, nl,
                   pupil_name=name, glossary=gloss)
        pages_a.append(a)
    adapted_pupil_pages[name] = pages_p
    adapted_ans_pages[name]   = pages_a
    print(f"  {name} ({level}): built {len(pages_p)} pupil pages")

# ── Build standard 3-page pupil PDF (used as template for standard copies)
merge(std_pupil_pages, f"{WORK}/T6W6_Standard.pdf")

# ── Build per-lesson day documents ──────────────────────────────────────────

print("Building day/class PDFs...")
for lesson in LESSONS:
    lesson_idx = LESSONS.index(lesson)
    date_str   = DATES[lesson]
    day_name   = date_str[0]  # Monday / Wednesday / Friday

    for cls, adapted_list, std_list in [
        ("LMES", LMES_ADAPTED, LMES_STANDARD),
        ("IM",   IM_ADAPTED,   IM_STANDARD),
    ]:
        pages = []
        # 1. Adapted pupils (sorted lowest → highest already in content)
        for pupil in adapted_list:
            n = pupil["name"]
            if n in adapted_pupil_pages:
                pages.append(adapted_pupil_pages[n][lesson_idx])
        # 2. One standard copy per standard pupil (all identical)
        std_p = f"{WORK}/std_{lesson}_pupil.pdf"
        for _ in std_list:
            pages.append(std_p)
        out = f"{WORK}/{day_name}_{cls}.pdf"
        merge(pages, out)
        total = check_pages(out)
        print(f"  {day_name} {cls}: {total} pages ({len(adapted_list)} adapted + {len(std_list)} std)")

# ── Build All Answers PDF ───────────────────────────────────────────────────

print("Building All Answers PDF...")
ans_pages = []
for lesson in LESSONS:
    ans_pages.append(f"{WORK}/std_{lesson}_ans.pdf")
    for pupil in (LMES_ADAPTED + IM_ADAPTED):
        n = pupil["name"]
        idx = LESSONS.index(lesson)
        if n in adapted_ans_pages and idx < len(adapted_ans_pages[n]):
            ans_pages.append(adapted_ans_pages[n][idx])
merge(ans_pages, f"{WORK}/T6W6_ReaderAnswers.pdf")
print(f"  Answers: {check_pages(f'{WORK}/T6W6_ReaderAnswers.pdf')} pages")

# ── Copy PPTX ───────────────────────────────────────────────────────────────
# Reuse the already-built PPTX (content is correct, We Do Qs will match)
import shutil
shutil.copy("/mnt/user-data/outputs/T6W6_Being_a_Reader.pptx",
            f"{WORK}/T6W6_ReaderTeaching.pptx")

# ── Package ZIP ─────────────────────────────────────────────────────────────

print("Packaging ZIP...")
ZIP_PATH = f"{OUT}/T6W6 - Being a Reader.zip"

files = {
    "T6W6 - ReaderTeaching.pptx": f"{WORK}/T6W6_ReaderTeaching.pptx",
    "T6W6 - ReaderAnswers.pdf":   f"{WORK}/T6W6_ReaderAnswers.pdf",
}
for lesson in LESSONS:
    day = DATES[lesson][0]
    for cls in ("LMES", "IM"):
        arc = f"{day}/T6W6 - {day} - {cls}.pdf"
        src = f"{WORK}/{day}_{cls}.pdf"
        files[arc] = src

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
    for arc_name, src_path in files.items():
        zf.write(src_path, arc_name)
        print(f"  + {arc_name}")

shutil.rmtree(WORK)
print(f"\nDone → {ZIP_PATH}")
