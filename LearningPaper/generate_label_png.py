"""
generate_label_png.py
WFA — canonical label PNG generator.

Renders the confirmed enquiry_label() or etiw_label() to a cropped PNG
suitable for embedding in any LP format (PPTX via python-pptx or pptxgenjs,
ReportLab PDF via direct canvas call).

Usage:
    from generate_label_png import enquiry_label_png, etiw_label_png

    # Enquiry / maths label → PNG at dest_path
    height_pt = enquiry_label_png(
        dest='/home/claude/lp_label.png',
        kq='Are England and Brazil different?',
        date='07/07/2025',
        lf='describe and compare human geography',
        ican1='identify features of human geography',
        ican2='compare human geography using key vocabulary',
        subject='geographer',   # key from SUBJECT_ICONS dict
        year='Y4',
        maths=False,            # True → mathematician mode (no KQ header)
        dpi=216,                # 3× 72pt base; increase for sharper PPTX embed
    )
    # height_pt is the label height in points — use to position content below it

    # ETIW Writer label → PNG at dest_path
    height_pt = etiw_label_png(
        dest='/home/claude/etiw_label.png',
        kq='How do writers create atmosphere?',
        lf='use expanded noun phrases to describe setting',
        date='07/07/2025',
        year='Y4',
        code='S3',              # session code — pass None to omit
        page_width_pt=None,     # defaults to A4 content width (CW)
        dpi=216,
    )

Returns:
    float — label height in points (crop height on the rendered canvas).
    Callers use this to position the first content element below the label.
"""

import os, sys, tempfile
sys.path.insert(0, '/home/claude')

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

from build_enquiry_label import (
    enquiry_label, LL_OUTER_W, LL_PAD_TOP, W as _W, H as _H, M as _M
)

# ── constants shared by both functions ───────────────────────────────────────
_A4_W, _A4_H = A4   # 595.28, 841.89 pt
_MARGIN = _M        # 35 pt


def enquiry_label_png(dest, kq, date, lf, ican1, ican2,
                      subject='geographer', year='Y4', maths=False, dpi=216):
    """
    Render enquiry_label() to a cropped PNG and save to dest.

    Parameters
    ----------
    dest       : str   — output file path (.png)
    kq         : str   — key question / maths topic text
    date       : str   — date string, e.g. '07/07/2025'
    lf         : str   — verb phrase WITHOUT leading 'to' (builder prepends it)
    ican1      : str   — verb phrase WITHOUT leading 'I can'
    ican2      : str   — verb phrase WITHOUT leading 'I can'
    subject    : str   — icon key, e.g. 'geographer', 'mathematician', 'scientist'
    year       : str   — 'Y3'–'Y6' (selects phase logo if used)
    maths      : bool  — True → mathematician mode (no 'Key Question' header)
    dpi        : int   — render resolution; 216 = 3× (good for PPTX embed)

    Returns
    -------
    float — label height in points
    """
    scale = dpi / 72.0
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp.close()

    try:
        # Render full A4 page
        c = rl_canvas.Canvas(tmp.name, pagesize=A4)
        bottom_y = enquiry_label(
            c, kq=kq, date=date, lf=lf, ican1=ican1, ican2=ican2,
            subject=subject, year=year, maths=maths,
            top_y=_A4_H - _MARGIN
        )
        c.save()

        label_height_pt = (_A4_H - _MARGIN) - bottom_y

        # Crop to label bounding box (fitz uses top-left origin, pt units)
        doc = fitz.open(tmp.name)
        page = doc[0]

        x0 = _A4_W - _MARGIN - LL_OUTER_W
        x1 = _A4_W - _MARGIN
        # PDF bottom-left → fitz top-left
        y0 = _MARGIN                              # fitz top of label
        y1 = _MARGIN + label_height_pt            # fitz bottom of label

        rect = fitz.Rect(x0, y0, x1, y1)
        mat  = fitz.Matrix(scale, scale)
        pix  = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        pix.save(dest)
        doc.close()

        # Write sidecar JSON for JS consumers (build_lp_v3.js reads this)
        meta_path = dest.replace('.png', '_meta.json')
        import json
        with open(meta_path, 'w') as f:
            json.dump({
                'png_path': os.path.abspath(dest),
                'width_in': LL_OUTER_W / 72.0,
                'height_in': label_height_pt / 72.0,
                'width_pt': LL_OUTER_W,
                'height_pt': label_height_pt,
            }, f, indent=2)

        return label_height_pt

    finally:
        os.unlink(tmp.name)


def etiw_label_png(dest, kq, lf, date, year='Y4', code=None,
                   page_width_pt=None, dpi=216):
    """
    Render etiw_label() to a cropped PNG and save to dest.

    Parameters
    ----------
    dest           : str   — output file path (.png)
    kq             : str   — key question text
    lf             : str   — learning focus verb phrase (WITHOUT leading 'to')
    date           : str   — date string
    year           : str   — 'Y1'–'Y6'
    code           : str|None — session code, e.g. 'S3' (None to omit)
    page_width_pt  : float|None — content width in pt; defaults to A4 CW
    dpi            : int   — render resolution

    Returns
    -------
    float — label height in points
    """
    from build_etiw_label import etiw_label, CW as _CW

    if page_width_pt is None:
        page_width_pt = _CW  # A4 content width

    scale = dpi / 72.0
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp.close()

    try:
        c = rl_canvas.Canvas(tmp.name, pagesize=A4)
        bottom_y = etiw_label(
            c, kq=kq, lf=lf, date=date, year=year, code=code,
            top_y=_A4_H - _MARGIN
        )
        c.save()

        label_height_pt = (_A4_H - _MARGIN) - bottom_y

        doc = fitz.open(tmp.name)
        page = doc[0]

        x0 = _MARGIN
        x1 = _A4_W - _MARGIN
        y0 = _MARGIN
        y1 = _MARGIN + label_height_pt

        rect = fitz.Rect(x0, y0, x1, y1)
        mat  = fitz.Matrix(scale, scale)
        pix  = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        pix.save(dest)
        doc.close()

        return label_height_pt

    finally:
        os.unlink(tmp.name)


# ── PPTX embed helpers ────────────────────────────────────────────────────────

def embed_label_pptx(slide, png_path, x_in, y_in, w_in, h_in):
    """
    Embed a label PNG into a python-pptx slide at the given position (inches).
    Replaces whatever label drawing was done before — no border, no background.

    Parameters
    ----------
    slide    : pptx.slide.Slide
    png_path : str    — path to PNG produced by enquiry_label_png() / etiw_label_png()
    x_in     : float  — left edge in inches
    y_in     : float  — top edge in inches
    w_in     : float  — width in inches  (= LL_W constant from label_builder.py)
    h_in     : float  — height in inches (= actual label height / 72.0)
    """
    from pptx.util import Inches
    slide.shapes.add_picture(png_path, Inches(x_in), Inches(y_in),
                             width=Inches(w_in), height=Inches(h_in))


# ── Constants for callers ─────────────────────────────────────────────────────

# Enquiry label width in inches (matches LL_OUTER_W in pt / 72)
ENQUIRY_LABEL_W_IN = LL_OUTER_W / 72.0   # ≈ 3.9"

# Maths PPTX label dimensions (from build_lp_v3.js)
# These are the slots carved out in the PPTX — the PNG will fill them exactly.
MATHS_LP_LABEL_W_IN = 9.7 / 2.54 * 0.72 * 0.85   # ≈ 2.338"
MATHS_LP_LABEL_H_IN = 4.24 / 2.54 * 0.72 * 0.85  # ≈ 1.021"


if __name__ == '__main__':
    # Quick smoke test
    h = enquiry_label_png(
        '/tmp/smoke_enquiry.png',
        kq='Are England and Brazil different?',
        date='07/07/2025',
        lf='describe and compare human geography',
        ican1='identify features of human geography',
        ican2='compare human geography using key vocabulary',
        subject='geographer', year='Y4', maths=False
    )
    print(f'Enquiry label height: {h:.1f}pt  →  /tmp/smoke_enquiry.png')

    h2 = enquiry_label_png(
        '/tmp/smoke_maths.png',
        kq='Statistics and Data',
        date='07/07/2025',
        lf='read and interpret bar charts',
        ican1='read values from a bar chart',
        ican2='use bar chart data to answer questions',
        subject='mathematician', year='Y4', maths=True
    )
    print(f'Maths label height:   {h2:.1f}pt  →  /tmp/smoke_maths.png')
