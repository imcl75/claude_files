"""
ETIW (Writer) learning label for ReportLab LP builder.

Assets (per year group) stored in /home/claude/etiw_assets/:
  ETIW-Y1.png, ETIW-Y2.png, ETIW-LKS2-Y3-Y4.png, ETIW-UKS2-Y5-Y6.png
  logo-Y1.png … logo-Y6.png
  writer-icon.png

Label structure:
  ┌─────────┬──────────────────────────────────────┬──────────────────┐
  │  LOGO   │  Key Question:  [text]  ← underlined  │  [S1]  [icon]    │
  │  Y4     │  Learning Focus: [text]  ← plain bold  │       Writer     │
  │ 07/... │                                        │                  │
  ├─────────┴──────────────────────────────────────┴──────────────────┤
  │  [strip: 7 icon circles, full width, pre-built PNG]              │
  └──────────────────────────────────────────────────────────────────┘

Returns label_bottom_y — content must start at or below this value.
"""

import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

# ── Page geometry ──────────────────────────────────────────────────────────
W, H = A4           # 595.28 × 841.89 pt
M    = 35.0         # margin (pt)
CW   = W - 2 * M   # content width = 525.28 pt

# ── Column widths ──────────────────────────────────────────────────────────
# Logo column: from DOCX (1350 DXA at 10771 DXA content width), scaled to CW
_DXA      = CW / 10771
LOGO_COL  = round(1350 * _DXA, 1)   # ≈ 65.8 pt

# Writer column: needs 1.25cm icon (35.6pt) + gap (4pt) + code "S1" max (22pt)
# = ~62pt. Use 65pt to keep a margin.
WRITER_COL = 65.0

# Text column: remainder
TEXT_COL   = CW - LOGO_COL - WRITER_COL   # ≈ 394.5 pt

# Within writer column — icon always at 1.25cm, code to its left
ICON_H     = 1.25 / 2.54 * 72   # 35.4 pt  (1.25 cm exactly)
_wi_src    = PILImage.open('/home/claude/etiw_assets/writer-icon.png')
_wi_ratio  = _wi_src.size[0] / _wi_src.size[1]
ICON_W     = round(ICON_H * _wi_ratio, 1)  # ≈ 35.6 pt

# Logo display size — from DOCX: LOGO_PX_W=54, LOGO_PX_H=60 at 96 dpi → pt
LOGO_DISP_W = 54 / 96 * 72   # 40.5 pt
LOGO_DISP_H = 60 / 96 * 72   # 45.0 pt

# ── Asset paths ────────────────────────────────────────────────────────────
ASSETS = '/home/claude/etiw_assets'

STRIP_MAP = {
    'Y1': 'ETIW-Y1.png',
    'Y2': 'ETIW-Y2.png',
    'Y3': 'ETIW-LKS2-Y3-Y4.png',
    'Y4': 'ETIW-LKS2-Y3-Y4.png',
    'Y5': 'ETIW-UKS2-Y5-Y6.png',
    'Y6': 'ETIW-UKS2-Y5-Y6.png',
}
LOGO_MAP = {f'Y{n}': f'logo-Y{n}.png' for n in range(1, 7)}

# ── Colours ────────────────────────────────────────────────────────────────
_BLACK   = (0.08, 0.08, 0.08)
_GREY    = (0.35, 0.35, 0.35)
_LGREY   = (0.75, 0.75, 0.75)   # light grey for borders / separator

# ── Helpers ────────────────────────────────────────────────────────────────
def _wrap(c, text, font, size, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or ['']


def _img_h(path, display_w):
    img = PILImage.open(path)
    pw, ph = img.size
    return display_w * ph / pw


def _flat(path):
    """Open image, flatten onto white (removes alpha), return ImageReader."""
    img = PILImage.open(path).convert('RGBA')
    bg  = PILImage.new('RGBA', img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img)
    rgb = bg.convert('RGB')
    import io
    buf = io.BytesIO()
    rgb.save(buf, format='PNG')
    buf.seek(0)
    return ImageReader(buf)


# ── Main function ──────────────────────────────────────────────────────────
def etiw_label(c, kq, date, lf, year='Y4', code=None, top_y=None):
    """
    Draw an ETIW Writer learning label.

    Parameters
    ----------
    c      : ReportLab canvas
    kq     : Key Question text (without prefix)
    date   : e.g. '07/07/2026'
    lf     : Learning Focus text (without prefix)
    year   : 'Y1'–'Y6'
    code   : session code e.g. 'S1', or None to omit
    top_y  : y of label top edge (default H − M)

    Returns
    -------
    label_bottom_y : float
    """
    if top_y is None:
        top_y = H - M

    year = str(year).upper()

    strip_path = os.path.join(ASSETS, STRIP_MAP.get(year, 'ETIW-LKS2-Y3-Y4.png'))
    logo_path  = os.path.join(ASSETS, LOGO_MAP.get(year, 'logo-Y4.png'))

    strip_h = _img_h(strip_path, CW)

    # ── Measure text blocks ────────────────────────────────────────────────
    SIZE_TEXT = 12          # pt (DOCX size:24 = 12pt)
    LEAD      = SIZE_TEXT * 1.35
    GAP       = 4           # gap between KQ and LF blocks
    SIZE_DATE = 8
    SIZE_WRIT = 7

    kq_full = 'Key Question:  ' + (kq or '\u2026')
    lf_full = 'Learning Focus:  ' + (lf or '\u2026')

    kq_lines = _wrap(c, kq_full, 'Helvetica-Bold', SIZE_TEXT, TEXT_COL - 6)
    lf_lines = _wrap(c, lf_full, 'Helvetica-Bold', SIZE_TEXT, TEXT_COL - 6)

    text_h = (len(kq_lines) + len(lf_lines)) * LEAD + GAP

    # ── Row heights per column ─────────────────────────────────────────────
    logo_h  = LOGO_DISP_H + 3 + SIZE_DATE   # logo + gap + date
    writ_h  = ICON_H + 2 + SIZE_WRIT        # icon + gap + "Writer"
    if code:
        writ_h = max(writ_h, 18 + 4 + ICON_H)  # code above icon

    ROW_H = max(50.0, logo_h, text_h, writ_h) + 10.0

    row_top    = top_y
    row_bottom = row_top - ROW_H

    # ─────────────────────────────────────────────────────────────────────
    # LOGO COLUMN
    # ─────────────────────────────────────────────────────────────────────
    logo_cx = M + LOGO_COL / 2                      # horizontal centre
    logo_x  = logo_cx - LOGO_DISP_W / 2
    # Vertically centre logo block in row
    blk_top = (row_top + row_bottom) / 2 + logo_h / 2
    logo_y  = blk_top - LOGO_DISP_H

    if os.path.exists(logo_path):
        c.drawImage(
            _flat(logo_path),
            logo_x, logo_y,
            width=LOGO_DISP_W, height=LOGO_DISP_H,
            preserveAspectRatio=True
        )

    # Date centred below logo
    date_y = logo_y - 3 - SIZE_DATE
    c.setFont('Helvetica', SIZE_DATE)
    c.setFillColorRGB(*_GREY)
    dw = c.stringWidth(date, 'Helvetica', SIZE_DATE)
    c.drawString(logo_cx - dw / 2, date_y, date)

    # ─────────────────────────────────────────────────────────────────────
    # TEXT COLUMN
    # ─────────────────────────────────────────────────────────────────────
    tx = M + LOGO_COL + 3

    # Vertically centre text block in row
    ty = (row_top + row_bottom) / 2 + text_h / 2

    # Key Question — bold + UNDERLINED
    c.setFont('Helvetica-Bold', SIZE_TEXT)
    c.setFillColorRGB(*_BLACK)
    for line in kq_lines:
        ty -= LEAD
        lw = c.stringWidth(line, 'Helvetica-Bold', SIZE_TEXT)
        c.setStrokeColorRGB(*_BLACK)
        c.setLineWidth(0.7)
        c.line(tx, ty - 1.5, tx + lw, ty - 1.5)
        c.drawString(tx, ty, line)

    ty -= GAP

    # Learning Focus — bold, NO underline
    c.setFont('Helvetica-Bold', SIZE_TEXT)
    c.setFillColorRGB(*_BLACK)
    for line in lf_lines:
        ty -= LEAD
        c.drawString(tx, ty, line)

    # ─────────────────────────────────────────────────────────────────────
    # WRITER COLUMN
    # ─────────────────────────────────────────────────────────────────────
    wc_left  = W - M - WRITER_COL
    wc_right = W - M - 4      # 4pt inset: prevents right-edge clipping at PDF crop boundary

    # Icon: right-aligned within column, 1.25cm tall
    icon_x = wc_right - ICON_W - 2   # 2pt right padding
    row_mid = (row_top + row_bottom) / 2

    if code:
        # Code above icon, both centred in column
        total_h  = 18 + 4 + ICON_H + 2 + SIZE_WRIT
        block_top = row_mid + total_h / 2
        # Code
        c.setFont('Helvetica-Bold', 18)
        c.setFillColorRGB(*_BLACK)
        cw_ = c.stringWidth(code, 'Helvetica-Bold', 18)
        c.drawString(wc_left + (WRITER_COL - cw_) / 2, block_top - 18, code)
        icon_y = block_top - 18 - 4 - ICON_H
    else:
        # Icon centred vertically, "Writer" below
        total_h  = ICON_H + 2 + SIZE_WRIT
        block_top = row_mid + total_h / 2
        icon_y = block_top - ICON_H

    # Always centre icon horizontally
    icon_x = wc_left + (WRITER_COL - ICON_W) / 2

    writer_path = '/home/claude/etiw_assets/writer-icon.png'
    if os.path.exists(writer_path):
        c.drawImage(
            _flat(writer_path),
            icon_x, icon_y,
            width=ICON_W, height=ICON_H,
            preserveAspectRatio=True
        )

    # "Writer" label
    c.setFont('Helvetica', SIZE_WRIT)
    c.setFillColorRGB(*_GREY)
    wlw = c.stringWidth('Writer', 'Helvetica', SIZE_WRIT)
    c.drawString(wc_left + (WRITER_COL - wlw) / 2, icon_y - 2 - SIZE_WRIT, 'Writer')

    # ─────────────────────────────────────────────────────────────────────
    # ICON STRIP — drawn at 97% of CW, centred, to avoid edge clipping
    # (source PNG has zero padding on both sides)
    # ─────────────────────────────────────────────────────────────────────
    STRIP_SCALE = 0.97
    strip_w   = CW * STRIP_SCALE
    strip_x   = M + (CW - strip_w) / 2
    strip_y   = row_bottom - strip_h
    if os.path.exists(strip_path):
        c.drawImage(
            ImageReader(strip_path),
            strip_x, strip_y,
            width=strip_w, height=strip_h,
            preserveAspectRatio=False, mask='auto'
        )

    return strip_y - 4


# ── Test ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    out = '/home/claude/etiw_label_test.pdf'
    c = rl_canvas.Canvas(out, pagesize=A4)

    c.setFont('Helvetica', 7); c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(M, H - M + 8, 'Test 1: Y4 / LKS2 with code S1')

    b1 = etiw_label(c,
        kq="How do writers use dialogue to reveal character?",
        date="07/07/2026",
        lf="use dialogue to reveal character and advance plot",
        year='Y4', code='S1')

    c.setFont('Helvetica', 7); c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(M, b1 - 16, 'Test 2: Y5 / UKS2 — no code')

    b2 = etiw_label(c,
        kq="Are England and Brazil different?",
        date="08/07/2026",
        lf="compare and contrast two contrasting countries",
        year='Y5', code=None, top_y=b1 - 24)

    c.save()
    print(f'Saved {out}')
    print(f'Y4 bottom: {b1:.1f}pt  |  Y5 bottom: {b2:.1f}pt')
