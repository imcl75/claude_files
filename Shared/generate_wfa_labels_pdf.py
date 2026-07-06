#!/usr/bin/env python3
"""
generate_wfa_labels_pdf.py
Generates 12 Avery-style learning labels (2 col × 6 row, 99mm × 42mm) as a PDF.
Uses ReportLab for exact, renderer-independent output.

Usage:
  python3 generate_wfa_labels_pdf.py --mode geographer \
      --date "07/07/2026" \
      --question "Are England and Brazil different?" \
      --lf "compare human geography features of two countries." \
      --ican1 "identify human geography features of two countries." \
      --ican2 "compare two countries using geography vocabulary." \
      --out labels.pdf
"""

import argparse
import os
import sys
import re
import urllib.request

# ── Avery 99×42mm layout on A4 ──────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
pt = 1.0  # 1 point = 1 ReportLab unit
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# Label geometry (physical Avery label)
LABEL_W  = 99.0 * mm   # label width
LABEL_H  = 42.0 * mm   # label height
N_COLS   = 2
N_ROWS   = 6

PAGE_W, PAGE_H = A4   # 595.28 × 841.89 pt

# Compute margins so 2 labels + gap fit centred on page
GAP_W    = 3.0 * mm
TOTAL_W  = N_COLS * LABEL_W + GAP_W
LEFT_M   = (PAGE_W - TOTAL_W) / 2   # ~2.8mm

TOP_M    = 1215 / 1440 * 25.4 * mm  # LL tool top margin
TOTAL_H  = N_ROWS * LABEL_H
BOT_M    = PAGE_H - TOP_M - TOTAL_H

# Cell padding (from LL tool)
PAD_TOP  = 141 / 1440 * 25.4 * mm
PAD_LR   = 115 / 1440 * 25.4 * mm

# Font sizes (from LL tool, enquiry mode)
SZ_DATE  = 8   * pt
SZ_KQLBL = 8   * pt
SZ_KQ    = 10  * pt
SZ_LF    = 9   * pt
SZ_ICAN  = 8   * pt
SZ_CAP   = 6.5 * pt

LINE_H_NORMAL = 11 * pt  # ~280/1440×25.4 ≈ 4.94mm; use 11pt for legibility
LINE_H_ICON   = 720 / 1440 * 25.4 * mm  # exact icon line spacing

# Icon pixel dimensions → points at 96 dpi
ICON_DIMS = {
    "geographer":         (38, 37),
    "historian":          (38, 26),
    "scientist":          (38, 27),
    "mathematician":      (38, 33),
    "writer":             (38, 37),
    "reader":             (32, 38),
    "computer_scientist": (38, 35),
    "artist":             (38, 37),
    "musician":           (38, 36),
    "athlete":            (37, 38),
    "linguist":           (38, 37),
    "Designer":           (38, 35),
    "Citizen":            (38, 38),
}

ICON_CACHE = {}

def get_icon(subject, ll_icons_dir='/home/claude/ll_icons'):
    if subject in ICON_CACHE:
        return ICON_CACHE[subject]
    path = os.path.join(ll_icons_dir, f'{subject}.png')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            img = ImageReader(io.BytesIO(f.read()))
        ICON_CACHE[subject] = img
        return img
    return None


def register_fonts():
    """Use Helvetica (built-in) — no install needed."""
    pass   # Helvetica, Helvetica-Bold are always available in ReportLab


def draw_label(c, lx, ly, mode, date, question, lf, ican1, ican2, subject):
    """
    Draw one label.
    lx, ly = bottom-left corner of label in pt (ReportLab coordinates, y up).
    """
    # Icon column width (from LL tool icon region ≈ 1000 DXA)
    icon_col_w = 1000 / 1440 * 25.4 * mm  # ~17.6mm
    text_col_w = LABEL_W - PAD_LR - icon_col_w - PAD_LR

    # Text region top
    label_top = ly + LABEL_H
    ty = label_top - PAD_TOP   # start y (descending)

    # ── Text column ──────────────────────────────────────────────
    tx = lx + PAD_LR

    def draw_line(text, size, bold=False, underline=False):
        nonlocal ty
        font = 'Helvetica-Bold' if bold else 'Helvetica'
        ty -= size * 0.72   # ascender
        c.setFont(font, size)
        c.drawString(tx, ty, text)
        if underline:
            w = c.stringWidth(text, font, size)
            c.setLineWidth(0.4)
            c.line(tx, ty - size * 0.12, tx + w, ty - size * 0.12)
        ty -= size * 0.28   # descender + a touch of gap
        ty -= 1.2 * pt       # line gap

    if mode == 'mathematician':
        draw_line(date,     SZ_DATE,  bold=False)
        draw_line(question, SZ_KQ,    bold=True,  underline=True)
        draw_line(f'LF: {lf}', SZ_LF)
        draw_line(f'I can {ican1}', SZ_ICAN)
        draw_line(f'I can {ican2}', SZ_ICAN)
    else:
        draw_line(date,          SZ_DATE,  bold=False)
        draw_line('Key Question', SZ_KQLBL, bold=True)
        draw_line(question,      SZ_KQ,    bold=True,  underline=True)
        draw_line(f'LF: {lf}', SZ_LF)
        draw_line(f'I can {ican1}', SZ_ICAN)
        draw_line(f'I can {ican2}', SZ_ICAN)

    # ── Icon column ──────────────────────────────────────────────
    icon_x = lx + LABEL_W - icon_col_w
    icon_img = get_icon(subject)
    if icon_img:
        pw, ph = ICON_DIMS.get(subject, (38, 37))
        iw = pw / 96 * 72   # px → pt at 96 dpi
        ih = ph / 96 * 72
        # Centre icon horizontally in icon column, place at top
        ix = icon_x + (icon_col_w - iw) / 2
        iy = label_top - PAD_TOP - ih   # top of icon aligns with top of text
        c.drawImage(icon_img, ix, iy, width=iw, height=ih, mask='auto')
        # Caption below icon
        cap_text = subject.replace('_', ' ')
        c.setFont('Helvetica', SZ_CAP)
        cap_w = c.stringWidth(cap_text, 'Helvetica', SZ_CAP)
        cx = icon_x + (icon_col_w - cap_w) / 2
        c.drawString(cx, iy - SZ_CAP * 0.84, cap_text)


def build_pdf(mode, subject, date, question, lf, ican1, ican2, out_path):
    register_fonts()

    # Strip common prefixes if caller passed full strings
    lf    = re.sub(r'^(LF:|To\s)', '', lf.strip(), flags=re.I).strip()
    ican1 = re.sub(r'^I can\s+', '', ican1.strip(), flags=re.I).strip()
    ican2 = re.sub(r'^I can\s+', '', ican2.strip(), flags=re.I).strip()

    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle(f'Learning Labels — {subject}')

    for row in range(N_ROWS):
        for col in range(N_COLS):
            lx = LEFT_M + col * (LABEL_W + GAP_W)
            # ReportLab y=0 at bottom; row 0 is at top of page
            ly = PAGE_H - TOP_M - (row + 1) * LABEL_H
            draw_label(c, lx, ly, mode, date, question, lf, ican1, ican2, subject)

    c.save()
    print(f'✓ {out_path}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Generate WFA learning labels as PDF')
    p.add_argument('--mode', default='enquiry',
                   help='enquiry or mathematician')
    p.add_argument('--date', required=True)
    p.add_argument('--question', required=True)
    p.add_argument('--lf', required=True)
    p.add_argument('--ican1', required=True)
    p.add_argument('--ican2', required=True)
    p.add_argument('--out', default='labels.pdf')
    # Subject inferred from mode or passed explicitly
    p.add_argument('--subject', default=None,
                   help='Icon subject key (e.g. geographer, historian). Defaults to mode.')
    args = p.parse_args()

    subject = args.subject or args.mode
    mode    = 'mathematician' if subject == 'mathematician' else 'enquiry'
    build_pdf(mode, subject, args.date, args.question, args.lf, args.ican1, args.ican2, args.out)
