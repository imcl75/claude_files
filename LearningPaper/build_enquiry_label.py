"""
WFA Learning Label — Enquiry / Maths variant.
Confirmed correct dimensions from LL tool DOCX builder.
Used on all subject LPs (enquiry, geography, history, science, computing,
maths, writing) as the top-right Avery 99mm label.

Usage:
    from build_enquiry_label import enquiry_label
    bottom_y = enquiry_label(c, kq=..., date=..., lf=...,
                             ican1=..., ican2=..., subject='geographer',
                             year='Y4', maths=False)
"""

import os, sys
sys.path.insert(0, '/home/claude')
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

W, H = A4
M = 35
CW = W - 2*M

# Shared constants (DXA→pt: divide by 20)
LL_OUTER_W = 280.8    # 5616 DXA — Avery 99mm
LL_PAD_LR  = 5.75    # 115 DXA
LL_PAD_TOP = 7.0     # 141 DXA
LL_INNER_W = 269.3   # 5386 DXA
LL_LEFT_W  = 219.3   # 4386 DXA
LL_RIGHT_W = 50.0    # 1000 DXA

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'll_assets')

SUBJECT_ICONS = {
    'historian':'icon_historian.png','geographer':'icon_geographer.png',
    'scientist':'icon_scientist.png','computer_scientist':'icon_computer_scientist.png',
    'mathematician':'icon_mathematician.png','writer':'icon_writer.png',
    'reader':'icon_reader.png','artist':'icon_artist.png',
    'musician':'icon_musician.png','designer':'icon_designer.png',
    'citizen':'icon_citizen.png','linguist':'icon_linguist.png','athlete':'icon_athlete.png',
}
SUBJECT_NAMES = {k: k.replace('_',' ') for k in SUBJECT_ICONS}

PHASE_LOGOS = {'EYFS':'phase_EYFS.png','Y1':'phase_Y1.png','Y2':'phase_Y2.png',
               'LKS2':'phase_LKS2.png','UKS2':'phase_UKS2.png'}
YEAR_PHASE = {'EYFS':'EYFS','Y1':'Y1','Y2':'Y2','Y3':'LKS2','Y4':'LKS2',
              'Y5':'UKS2','Y6':'UKS2'}

_BLK = (0.08, 0.08, 0.08)
_DGY = (0.35, 0.35, 0.35)


def _wrap(c, text, font, size, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines or ['']


# ── 1 & 2: Enquiry / Maths label (same DOCX dimensions) ─────────────────────
def enquiry_label(c, kq, date, lf, ican1, ican2, subject,
                  year='Y4', maths=False, top_y=None):
    """
    Enquiry or Maths LP label.
    maths=True omits 'Key Question' header, shows topic (kq) bold+underline only.
    Returns label_bottom_y.
    """
    if top_y is None:
        top_y = H - M

    tx   = W - M - LL_OUTER_W + LL_PAD_LR     # text left
    ty   = top_y - LL_PAD_TOP                   # text top
    rx   = W - M - LL_RIGHT_W                   # right col left edge
    rr   = W - M - LL_PAD_LR                    # right col right edge
    left_w = LL_LEFT_W

    # ── Right column: icon + name ──────────────────────────────────────────
    icon_key  = subject.lower().replace(' ','_')
    icon_path = os.path.join(ASSETS, SUBJECT_ICONS.get(icon_key, 'icon_geographer.png'))
    subj_name = SUBJECT_NAMES.get(icon_key, icon_key.replace('_',' '))

    ICON_SZ = 36
    if os.path.exists(icon_path):
        ix = rr - ICON_SZ
        iy = ty - ICON_SZ
        c.drawImage(ImageReader(icon_path), ix, iy, width=ICON_SZ, height=ICON_SZ,
                    preserveAspectRatio=True, mask='auto')

    c.setFont('Helvetica', 6.5)
    c.setFillColorRGB(*_DGY)
    nw = c.stringWidth(subj_name, 'Helvetica', 6.5)
    c.drawString(rr - nw, ty - ICON_SZ - 8, subj_name)

    # ── Left column ─────────────────────────────────────────────────────────
    y = ty

    # Date (8pt regular)
    c.setFont('Helvetica', 8)
    c.setFillColorRGB(*_DGY)
    c.drawString(tx, y - 8, date)
    y -= 8 * 1.35

    if not maths:
        # 'Key Question' header (8pt bold)
        c.setFont('Helvetica-Bold', 8)
        c.setFillColorRGB(*_BLK)
        c.drawString(tx, y - 8, 'Key Question')
        y -= 8 * 1.35

    # KQ / topic text (10pt bold + underline)
    c.setFont('Helvetica-Bold', 10)
    c.setFillColorRGB(*_BLK)
    for line in _wrap(c, kq, 'Helvetica-Bold', 10, left_w):
        lw = c.stringWidth(line, 'Helvetica-Bold', 10)
        c.setStrokeColorRGB(*_BLK); c.setLineWidth(0.6)
        c.line(tx, y - 10 - 1.5, tx + lw, y - 10 - 1.5)
        c.drawString(tx, y - 10, line)
        y -= 10 * 1.35
    y -= 2

    # LF: To … (9pt regular)
    c.setFont('Helvetica', 9); c.setFillColorRGB(*_BLK)
    lf_full = 'LF: To ' + (lf or '\u2026')
    for line in _wrap(c, lf_full, 'Helvetica', 9, left_w):
        c.drawString(tx, y - 9, line); y -= 9 * 1.25

    # I can … x2 (8pt regular)
    c.setFont('Helvetica', 8)
    for ican in [ican1, ican2]:
        ic_full = 'I can ' + (ican or '\u2026')
        for line in _wrap(c, ic_full, 'Helvetica', 8, left_w):
            c.drawString(tx, y - 8, line); y -= 8 * 1.25

    return y - 4


# ── 3: ETIW Writer label (full A4 width, UKS2) ──────────────────────────────
# ETIW dimensions (from DOCX builder, DXA→pt):
# PAGE_W=11905, MARGIN=567 each side → CONTENT_W=10771 DXA → 538.55pt
# But our LP has M=35 → CW=525.28pt — we scale proportionally.
# LOGO_COL=1350 → 1350/10771 × 525.28 = 65.8pt
# WRITER_COL=900 → 900/10771 × 525.28 = 43.9pt
# TEXT_COL = CW - LOGO_COL - WRITER_COL = 415.6pt
#
# LOGO: UKS2 phase logo 54×60pt (LOGO_PX_W × LOGO_PX_H) centred in LOGO_COL; date below
# TEXT: 'Key Question:  [kq]' (12pt bold) / 'Learning Focus:  [lf]' (12pt bold+underline)
# WRITER: 'S1' code (18pt bold) + writer icon (44×43pt) + 'Writer' (7pt)
# STRIP: row of 7 icons across full width below top row

ETIW_SCALE = 525.28 / 10771.0  # scale DXA→pt at CW width
ETIW_LOGO_W  = int(1350 * ETIW_SCALE)   # ≈ 65.8pt
ETIW_WRITER_W= int(900  * ETIW_SCALE)   # ≈ 43.9pt
ETIW_TEXT_W  = int(CW - ETIW_LOGO_W - ETIW_WRITER_W)

ETIW_LOGO_PX_W = 54    # display size of phase logo in label
ETIW_LOGO_PX_H = 60
ETIW_ICON_PX_W = 44    # writer icon display size
ETIW_ICON_PX_H = 43

# UKS2 strip icons (filename → label)
UKS2_ICONS = [
    ('segment-ks2.png',        'segment'),
    ('spelling-rules-ks2.png', 'spelling rules'),
    ('cursive-ks2.png',        'cursive'),
    ('missing-word-Y2-ks2.png','missing word'),
    ('tense-ks2.png',          'tense'),
    ('punctuation-uks2.png',   'punctuation'),
    ('re-read-all.png',        're-read'),
]


