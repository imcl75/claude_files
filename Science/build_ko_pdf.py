#!/usr/bin/env python3
"""
build_ko_pdf.py — WFA Knowledge Organiser PDF builder
Produces a single print-ready A4 PDF from a JSON config file.

Usage:
    python3 build_ko_pdf.py <config.json>

Config keys:
    year_group      "Y3" | "Y4" | "Y5" | "Y6"
    subject         "science" | "history" | "geography" | "computing" | "art" |
                    "music" | "dt" | "pe" | "mfl" | "citizenship"
    key_question    string
    key_facts       list of strings  (6–10 recommended)
    key_skills      list of strings  (4–6 recommended)
    vocabulary      list of ["word", "definition"]  (10–16 recommended)
    icon_path       absolute path to state-of-being .png (auto-resolved if omitted)
    strip_image     absolute path to wide-format image for the panorama strip
    notes_image     absolute path to landscape/square image for notes column
    output          absolute path for the PDF to write
"""
import json, sys, os
from pathlib import Path
from PIL import Image
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white

# ── Page geometry ──────────────────────────────────────────────────────────────
W, H   = A4            # 595.28 × 841.89 pt
MARGIN = 18
CW     = W - 2*MARGIN  # ≈ 559 pt
GAP    = 6             # gap between sections
AVAIL  = H - 2*MARGIN  # ≈ 806 pt

# ── Section constants ──────────────────────────────────────────────────────────
LBL_H  = 20   # label bar
V_ROW  = 14   # row height in facts / skills boxes (set dynamically below)
V_PAD  = 6    # padding inside those boxes
VRH    = 14   # vocab table row height
VHDR_H = 18   # vocab column header height
HDR_H  = 40   # header — reduced from 54
WC     = 130  # vocab word-column width
N_BLANK = 0   # no "add your own" blank rows

# ── School colour map ──────────────────────────────────────────────────────────
YG_COLOUR = {
    'Y3': '#c0157b',
    'Y4': '#1798d3',
    'Y5': '#e57d24',
    'Y6': '#2bae62',
}

# ── Subject → icon filename ───────────────────────────────────────────────────
ICON_DIR = (
    '/Users/innes/Desktop/Claude Assets/'
    'States of Being Icons/enquiry-reading-maths-writer-images'
)
SUBJECT_ICON = {
    'science':     'scientist.png',
    'history':     'historian.png',
    'geography':   'geographer.png',
    'computing':   'computer_scientist.png',
    'art':         'artist.png',
    'music':       'musician.png',
    'dt':          'Designer.png',
    'design':      'Designer.png',
    'pe':          'athlete.png',
    'sport':       'athlete.png',
    'mfl':         'linguist.png',
    'languages':   'linguist.png',
    'citizenship': 'Citizen.png',
    'pshe':        'Citizen.png',
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lighten(hex_colour, factor):
    """Mix hex_colour toward white. factor=0 → original, 1 → white."""
    r, g, b = hex_to_rgb(hex_colour)
    return '#{:02x}{:02x}{:02x}'.format(
        int(r + (255 - r) * factor),
        int(g + (255 - g) * factor),
        int(b + (255 - b) * factor),
    )

def composite_icon(icon_path, colour_hex, out_path):
    """White silhouette on coloured background — uses the PNG alpha channel."""
    img = Image.open(icon_path).convert('RGBA')
    arr = np.array(img)
    has_ink = arr[:, :, 3] > 0
    r, g, b = hex_to_rgb(colour_hex)
    result = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    result[:, :] = [r, g, b]
    result[has_ink] = [255, 255, 255]
    Image.fromarray(result, 'RGB').save(out_path)
    return out_path

def crop_strip_to_ratio(img_path, strip_h_pt, cw_pt, out_path):
    """Crop image centre-vertically so its pixel ratio matches strip_h_pt/cw_pt."""
    img = Image.open(img_path)
    iw, ih = img.size
    crop_h = round(strip_h_pt * iw / cw_pt)
    crop_h = min(crop_h, ih)
    top = (ih - crop_h) // 2
    img.crop((0, top, iw, top + crop_h)).save(out_path)
    return out_path

def label_bar(c, col, x, top, w, text):
    """Orange label bar at the top of a section box."""
    bar_bot = top - LBL_H
    c.setFillColor(col)
    c.rect(x, bar_bot, w, LBL_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(x + 10, bar_bot + int(LBL_H * 0.33), text)

# ── Main draw routine ──────────────────────────────────────────────────────────
def build(c, cfg, colour, col, col_light, col_mid, icon_comp, strip_crop, tmp_dir):
    facts  = cfg['key_facts']
    skills = cfg['key_skills']
    vocab  = cfg['vocabulary']
    key_q  = cfg['key_question']

    import textwrap as _tw

    # Pre-wrap facts and skills to fit column widths (approx 5.5pt/char at 8.5pt)
    FACT_W_EST = int(CW * 0.585) - 20     # inner text width for facts column
    SK_W_EST   = CW - int(CW * 0.585) - 8 - 20   # inner text width for skills column
    CHARS_FACT = max(int(FACT_W_EST / 4.8), 30)
    CHARS_SK   = max(int(SK_W_EST / 4.8), 22)

    facts_wrapped  = [_tw.wrap(f, width=CHARS_FACT) or [f] for f in facts]
    skills_wrapped = [_tw.wrap(s, width=CHARS_SK) or [s] for s in skills]

    facts_lines  = sum(len(w) for w in facts_wrapped)
    skills_lines = sum(len(w) for w in skills_wrapped)
    max_lines    = max(facts_lines, skills_lines)

    FONT_SZ = 8.5
    LINE_H  = FONT_SZ * 1.4   # ≈12pt leading
    TWO_H   = int(LBL_H + V_PAD + max_lines * LINE_H + V_PAD)
    VTBL_H  = LBL_H + VHDR_H + (len(vocab) + N_BLANK) * VRH

    # Strip is a fixed visual accent — 65pt (~2.3cm), not dynamic
    STRIP_H = 65
    NOTES_H = int(AVAIL - HDR_H - TWO_H - VTBL_H - STRIP_H - 4 * GAP)

    DRK = HexColor('#111111')
    GRY = HexColor('#666666')
    LN  = HexColor('#c8c8c8')

    cur_top = H - MARGIN

    # ── 1. Header ──────────────────────────────────────────────────────────────
    hdr_bot = cur_top - HDR_H
    c.setFillColor(col)
    c.rect(MARGIN, hdr_bot, CW, HDR_H, fill=1, stroke=0)

    # White icon (pre-composited on same colour as header → seamless)
    # ICON_SZ is the rendered size in pts; icon_comp is at native resolution
    ICON_SZ = 32
    icon_y  = hdr_bot + (HDR_H - ICON_SZ) / 2
    c.drawImage(icon_comp, MARGIN + 6, icon_y, ICON_SZ, ICON_SZ,
                preserveAspectRatio=True, anchor='c')

    # Key question
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 12)
    q_base = hdr_bot + (HDR_H / 2) - (12 * 0.72 / 2)
    c.drawString(MARGIN + 6 + ICON_SZ + 10, q_base, key_q)

    cur_top = hdr_bot - GAP

    # ── 2. Key facts | Key skills ──────────────────────────────────────────────
    # Single unified box with an internal dividing line — no gap between columns
    FACT_W = int(CW * 0.585)
    SK_W   = CW - FACT_W
    sx     = MARGIN + FACT_W
    two_bot = cur_top - TWO_H

    # Single background fill for the combined area
    c.setFillColor(col_light)
    c.rect(MARGIN, two_bot, CW, TWO_H, fill=1, stroke=0)

    # Facts label bar + text
    label_bar(c, col, MARGIN, cur_top, FACT_W, 'Key facts')
    c.setFillColor(DRK)
    ty = cur_top - LBL_H - V_PAD - int(FONT_SZ * 0.72)
    for wrapped_lines in facts_wrapped:
        for i, line in enumerate(wrapped_lines):
            c.setFont('Helvetica', FONT_SZ)
            prefix = '•  ' if i == 0 else '    '
            c.drawString(MARGIN + 10, ty, prefix + line)
            ty -= LINE_H

    # Skills label bar + text
    label_bar(c, col, sx, cur_top, SK_W, 'Key skills')
    c.setFillColor(DRK)
    ty2 = cur_top - LBL_H - V_PAD - int(FONT_SZ * 0.72)
    for wrapped_lines in skills_wrapped:
        for i, line in enumerate(wrapped_lines):
            c.setFont('Helvetica', FONT_SZ)
            prefix = '•  ' if i == 0 else '    '
            c.drawString(sx + 10, ty2, prefix + line)
            ty2 -= LINE_H

    # Outer border for the combined box, then internal dividing line
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(MARGIN, two_bot, CW, TWO_H, fill=0, stroke=1)
    c.line(sx, two_bot, sx, cur_top)

    cur_top = two_bot - GAP

    # ── 3. Image strip ─────────────────────────────────────────────────────────
    strip_bot = cur_top - STRIP_H
    if strip_crop and Path(strip_crop).exists():
        c.drawImage(strip_crop, MARGIN, strip_bot, CW, STRIP_H,
                    preserveAspectRatio=False)
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(MARGIN, strip_bot, CW, STRIP_H, fill=0, stroke=1)

    cur_top = strip_bot - GAP

    # ── 4. Vocabulary table ────────────────────────────────────────────────────
    vocab_bot = cur_top - VTBL_H
    c.setFillColor(white); c.rect(MARGIN, vocab_bot, CW, VTBL_H, fill=1, stroke=0)
    label_bar(c, col, MARGIN, cur_top, CW, 'Vocabulary')

    chdr_top = cur_top - LBL_H
    chdr_bot = chdr_top - VHDR_H
    c.setFillColor(col_mid); c.rect(MARGIN, chdr_bot, CW, VHDR_H, fill=1, stroke=0)
    c.setFillColor(DRK); c.setFont('Helvetica-Bold', 9)
    chdr_base = chdr_bot + int(VHDR_H * 0.33)
    c.drawString(MARGIN + 8, chdr_base, 'Word')
    c.drawString(MARGIN + WC + 8, chdr_base, 'Definition')

    row_top = chdr_bot
    col_alt = HexColor(lighten(colour, 0.94))
    for i, (word, defn) in enumerate(vocab):
        row_bot = row_top - VRH
        if i % 2 == 0:
            c.setFillColor(col_alt); c.rect(MARGIN, row_bot, CW, VRH, fill=1, stroke=0)
        base = row_bot + int(VRH * 0.33)
        c.setFillColor(col); c.setFont('Helvetica-Bold', 8.5)
        c.drawString(MARGIN + 6, base, word)
        c.setFillColor(DRK); c.setFont('Helvetica', 8.5)
        c.drawString(MARGIN + WC + 6, base, defn)
        c.setStrokeColor(LN); c.setLineWidth(0.3)
        c.line(MARGIN, row_bot, MARGIN + CW, row_bot)
        row_top = row_bot

    # Blank rows (only if N_BLANK > 0)
    if N_BLANK > 0:
        c.setFillColor(GRY); c.setFont('Helvetica-Oblique', 6.5)
        c.drawString(MARGIN + 6, row_top - int(VRH * 0.68), 'add your own…')
    for i in range(N_BLANK):
        row_bot = row_top - VRH
        bi = len(vocab) + i
        if bi % 2 == 0:
            c.setFillColor(col_alt); c.rect(MARGIN, row_bot, CW, VRH, fill=1, stroke=0)
        base = row_bot + int(VRH * 0.33)
        c.setStrokeColor(HexColor('#d0d0d0')); c.setLineWidth(0.5); c.setDash([3, 3], 0)
        c.line(MARGIN + 6, base, MARGIN + WC - 6, base)
        c.line(MARGIN + WC + 6, base, MARGIN + CW - 6, base)
        c.setDash([])
        c.setStrokeColor(LN); c.setLineWidth(0.3)
        c.line(MARGIN, row_bot, MARGIN + CW, row_bot)
        row_top = row_bot

    c.setStrokeColor(LN); c.setLineWidth(0.5)
    c.line(MARGIN + WC, vocab_bot, MARGIN + WC, chdr_bot)
    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(MARGIN, vocab_bot, CW, VTBL_H, fill=0, stroke=1)

    cur_top = vocab_bot - GAP

    # ── 5. My notes ────────────────────────────────────────────────────────────
    notes_bot = MARGIN
    notes_h   = cur_top - notes_bot
    c.setFillColor(white); c.rect(MARGIN, notes_bot, CW, notes_h, fill=1, stroke=0)
    label_bar(c, col, MARGIN, cur_top, CW, 'My notes')

    inner_top = cur_top - LBL_H
    inner_bot = notes_bot + 4
    inner_h   = inner_top - inner_bot

    notes_img_path = cfg.get('notes_image')
    if notes_img_path and Path(notes_img_path).exists():
        # 3:2 image scaled to fit inner height
        IMG_H = int(inner_h)
        IMG_W = int(IMG_H * 1.5)
        if IMG_W > CW * 0.45:   # cap at 45% of width so lines have space
            IMG_W = int(CW * 0.45)
            IMG_H = int(IMG_W / 1.5)
        img_x = MARGIN + CW - IMG_W - 4
        img_y = inner_bot + (inner_h - IMG_H) / 2
        c.drawImage(notes_img_path, img_x, img_y, IMG_W, IMG_H,
                    preserveAspectRatio=True)
        line_w = CW - IMG_W - 14
    else:
        line_w = CW - 20

    # Writing lines
    lines_x = MARGIN + 10
    LINE_SP  = 20
    line_y   = inner_top - LINE_SP
    c.setStrokeColor(LN); c.setLineWidth(0.6)
    while line_y > notes_bot + 12:
        c.line(lines_x, line_y, lines_x + line_w, line_y)
        line_y -= LINE_SP

    c.setStrokeColor(col); c.setLineWidth(0.8)
    c.rect(MARGIN, notes_bot, CW, notes_h, fill=0, stroke=1)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 build_ko_pdf.py <config.json>')
        sys.exit(1)

    cfg_path = sys.argv[1]
    with open(cfg_path) as f:
        cfg = json.load(f)

    yg      = cfg.get('year_group', 'Y4')
    subject = cfg.get('subject', 'science').lower()
    colour  = cfg.get('colour', YG_COLOUR.get(yg, '#1798d3'))

    col      = HexColor(colour)
    col_light = HexColor(lighten(colour, 0.88))
    col_mid   = HexColor(lighten(colour, 0.72))

    # Resolve icon path
    icon_path = cfg.get('icon_path') or os.path.join(
        ICON_DIR, SUBJECT_ICON.get(subject, 'scientist.png')
    )

    # Temp dir for pre-processed images
    tmp_dir = Path(cfg_path).parent / '_ko_tmp'
    tmp_dir.mkdir(exist_ok=True)

    # Composite icon
    icon_comp = str(tmp_dir / 'icon_comp.png')
    composite_icon(icon_path, colour, icon_comp)

    # Crop strip image to match layout ratio
    strip_crop = None
    if cfg.get('strip_image') and Path(cfg['strip_image']).exists():
        strip_crop = str(tmp_dir / 'strip_crop.png')
        # We need to know STRIP_H first — calculate it with the same wrapping logic
        facts  = cfg['key_facts']
        skills = cfg.get('key_skills', [])
        vocab  = cfg['vocabulary']
        import textwrap as _tw2
        FACT_W_EST2 = int(CW * 0.585) - 20
        SK_W_EST2   = CW - int(CW * 0.585) - 8 - 20
        fw2 = [_tw2.wrap(f, width=max(int(FACT_W_EST2 / 4.8), 30)) or [f] for f in facts]
        sw2 = [_tw2.wrap(s, width=max(int(SK_W_EST2 / 4.8), 22)) or [s] for s in skills]
        ml2 = max(sum(len(w) for w in fw2), sum(len(w) for w in sw2))
        STRIP_H_calc = 65   # fixed to match build() constant
        crop_strip_to_ratio(cfg['strip_image'], STRIP_H_calc, CW, strip_crop)

    # Build PDF
    out = cfg.get('output', str(Path(cfg_path).parent / 'KO_output.pdf'))
    cv  = canvas.Canvas(out, pagesize=A4)
    cv.setTitle(f"Knowledge Organiser — {cfg.get('key_question', '')[:40]}")
    build(cv, cfg, colour, col, col_light, col_mid, icon_comp, strip_crop, tmp_dir)
    cv.save()
    print(f'Saved: {out}')


main()
