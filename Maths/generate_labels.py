"""
generate_labels.py — Mathematician label sheet for WFA maths LPs.

Produces an A4 PDF matching the Wallscourt Farm Academy learning-labels tool
(Avery 99×42 mm, 12 per sheet, 2 cols × 6 rows).

Usage:
    python3 generate_labels.py <lesson_num> [<lesson_num> ...]

Reads label data from labels_data.json (written by build_lp_v3.js).
Each lesson fills one full row (both columns identical).
4 lessons → 4 rows = half a sheet.
"""

import json, os, sys, base64
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io

# ─── Avery L7159 dimensions ──────────────────────────────────────────────────
PAGE_W, PAGE_H = A4               # 595.28 × 841.89 pt
LABEL_W = 99.1 * mm
LABEL_H = 42.3 * mm
COLS    = 2
ROWS    = 6
MARGIN_L = 6.35 * mm
MARGIN_T = 21.15 * mm
GAP_X   = 0
GAP_Y   = 0

# ─── Colours ─────────────────────────────────────────────────────────────────
BLUE  = colors.HexColor("#1798d3")   # Y4 / school colour
DARK  = colors.HexColor("#1F4E79")   # text
GREY  = colors.HexColor("#555555")   # secondary text
BLACK = colors.black

# ─── Paths ───────────────────────────────────────────────────────────────────
ASSETS    = "/home/claude/lp_assets"
ICON_PATH = os.path.join(ASSETS, "mathematician_icon.png")
DATA_PATH = "/home/claude/labels_data.json"

# ─── Load label data ──────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"No labels_data.json found at {DATA_PATH}. "
                            "Run build_lp_v3.js for each lesson first.")
with open(DATA_PATH) as f:
    all_labels = json.load(f)  # list of dicts, keyed by lesson number

# Filter to requested lessons (or all if no args)
if len(sys.argv) > 1:
    wanted = {int(x) for x in sys.argv[1:]}
    labels = [l for l in all_labels if l["lesson"] in wanted]
else:
    labels = all_labels

if not labels:
    print("No matching label data found.")
    sys.exit(1)

# ─── Determine output path ───────────────────────────────────────────────────
week = labels[0].get("week", "T6W3")
out_path = f"/home/claude/{week}_Labels.pdf"

# ─── Fonts ───────────────────────────────────────────────────────────────────
# Use built-in Helvetica — close enough to Calibri for label use
# (ReportLab doesn't bundle Calibri)
FONT_BOLD   = "Helvetica-Bold"
FONT_REG    = "Helvetica"
FONT_OBLIQ  = "Helvetica-Oblique"

# ─── Load icon ───────────────────────────────────────────────────────────────
icon_img = None
if os.path.exists(ICON_PATH):
    icon_img = ICON_PATH  # ReportLab drawImage accepts path

# ─── Draw one label ───────────────────────────────────────────────────────────
def draw_label(c, x, y, label):
    """
    x, y: bottom-left corner of label (ReportLab y-origin = bottom).
    Layout:
      [DATE top-left]               [ICON top-right]
      [TOPIC bold, coloured, underlined — constrained to text column]
      [LF line — full width]
      [I can 1]
      [I can 2]
    """
    # ── thin border ──────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#DDDDDD"))
    c.setLineWidth(0.3)
    c.rect(x, y, LABEL_W, LABEL_H, stroke=1, fill=0)

    PAD    = 3 * mm
    top    = y + LABEL_H          # top of label in pt coords
    ICON_W = 9 * mm
    ICON_H = 7.8 * mm             # 38:33 ratio ≈ matches tool dimensions
    ICON_X = x + LABEL_W - PAD - ICON_W
    ICON_TOP_Y = top - PAD - ICON_H  # bottom of icon in pt coords

    # Column widths: text left of icon vs text that can go full width
    TEXT_W_NARROW = LABEL_W - 2*PAD - ICON_W - 2*mm   # beside icon
    TEXT_W_FULL   = LABEL_W - 2*PAD                    # below icon

    cur_y = top - PAD  # current text position (descends)

    # ── Date ─────────────────────────────────────────────────────────────────
    date_str = label.get("date", "")
    c.setFont(FONT_REG, 6)
    c.setFillColor(GREY)
    c.drawString(x + PAD, cur_y - 6, date_str)
    cur_y -= 9

    # ── Icon ─────────────────────────────────────────────────────────────────
    if icon_img:
        c.drawImage(icon_img, ICON_X, ICON_TOP_Y,
                    width=ICON_W, height=ICON_H,
                    preserveAspectRatio=True, mask="auto")
        c.setFont(FONT_REG, 5)
        c.setFillColor(GREY)
        c.drawCentredString(ICON_X + ICON_W / 2, ICON_TOP_Y - 5, "Mathematician")

    # ── Topic (bold, coloured, underlined, constrained to text column) ────────
    topic = label.get("topic", "")
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(BLUE)
    c.drawString(x + PAD, cur_y - 8, topic)
    tw = c.stringWidth(topic, FONT_BOLD, 8.5)
    c.setStrokeColor(BLUE)
    c.setLineWidth(0.5)
    c.line(x + PAD, cur_y - 9, x + PAD + tw, cur_y - 9)
    cur_y -= 14

    # ── LF and I can lines — full width below topic ───────────────────────────
    c.setFont(FONT_REG, 7)
    c.setFillColor(DARK)

    def draw_wrapped(text, start_y, line_h=8.5):
        """Draw wrapped text. Narrow beside icon, full width below."""
        words = text.split()
        line = ""
        cy = start_y
        for w in words:
            # Use narrow width if alongside the icon, full width below it
            avail = TEXT_W_NARROW if cy > ICON_TOP_Y else TEXT_W_FULL
            test = (line + " " + w).strip()
            if c.stringWidth(test, FONT_REG, 7) < avail:
                line = test
            else:
                if line:
                    c.drawString(x + PAD, cy, line)
                    cy -= line_h
                line = w
        if line:
            c.drawString(x + PAD, cy, line)
            cy -= line_h
        return cy

    for text_key in ["lf", "ican1", "ican2"]:
        txt = label.get(text_key, "")
        if txt:
            cur_y = draw_wrapped(txt, cur_y)


# ─── Build PDF ────────────────────────────────────────────────────────────────
c = canvas.Canvas(out_path, pagesize=A4)
c.setTitle(f"{week} Maths Learning Labels")

# Fill 12 slots: each lesson fills one row (col 0 and col 1 identical).
slot = 0  # 0..11
for label in labels:
    row = slot // COLS
    col = slot % COLS
    if row >= ROWS:
        # Overflow onto next page
        c.showPage()
        row = 0
        col = 0
        slot = 0

    # Draw both columns for this lesson (same label)
    for c_idx in range(COLS):
        lx = MARGIN_L + c_idx * (LABEL_W + GAP_X)
        # ReportLab y=0 is bottom; label top is at MARGIN_T from top
        ly = PAGE_H - MARGIN_T - (row + 1) * LABEL_H
        draw_label(c, lx, ly, label)

    slot += COLS  # advance by one full row

c.save()
print(f"Labels saved: {out_path}  ({len(labels)} lesson{'s' if len(labels)!=1 else ''})")
