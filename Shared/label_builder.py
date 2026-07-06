"""
WFA Learning Label — exact spec from label-spec.md (embedded PPTX Set 1 Enquiry).
"""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

CM          = 1 / 2.54
LABEL_SCALE = 0.72 * 0.85
LL_W        = 9.7  * CM * LABEL_SCALE   # 2.338"
LL_H        = 4.24 * CM * LABEL_SCALE   # 1.021"
PAD         = 0.04
ICO_W       = 0.26
ICO_H       = ICO_W * (118 / 120)       # ≈ 0.257"
NARROW_W    = LL_W - ICO_W - PAD * 3
FULL_W      = LL_W - PAD * 2
FONT        = 'Calibri'
DARK        = RGBColor(0x1A, 0x1A, 0x1A)

# Row heights
DATE_H  = 0.11
KQ_H    = 0.12    # "Key Question" label alone
Q_H     = 0.25    # question text — generous for one-line wrap
LF_H    = 0.22
ICAN_H  = 0.13

def _i(v): return Inches(v)

def _txt(slide, x, y, w, h, text, size, bold=False, underline=False, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(_i(x), _i(y), _i(w), _i(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.underline = underline
    r.font.color.rgb = DARK


def build_enquiry_label(slide, x, y,
                        date_str, key_q, lf, ican1, ican2,
                        icon_path):
    """
    Add WFA Set 1 Enquiry learning label.
    lf    — verb phrase WITHOUT leading 'to' (e.g. 'describe and compare land use')
    ican1 — verb phrase WITHOUT leading 'I can' (e.g. 'describe land use in Brazil')
    ican2 — verb phrase WITHOUT leading 'I can'
    Builder prepends 'LF: To ' and 'I can ' respectively.
    """

    # ── Right column: icon then 'geographer' caption ──────────────
    ico_x = x + LL_W - ICO_W - PAD
    ico_y = y + PAD
    slide.shapes.add_picture(icon_path, _i(ico_x), _i(ico_y), _i(ICO_W), _i(ICO_H))
    cap_tb = slide.shapes.add_textbox(
        _i(ico_x - 0.15), _i(ico_y + ICO_H + 0.01),
        _i(ICO_W + 0.30), _i(0.09))
    cap_tb.text_frame.word_wrap = False
    cap_p = cap_tb.text_frame.paragraphs[0]
    cap_p.alignment = PP_ALIGN.CENTER
    cap_r = cap_p.add_run()
    cap_r.text = 'geographer'
    cap_r.font.name = FONT
    cap_r.font.size = Pt(6.5)
    cap_r.font.color.rgb = DARK

    # ── Left column ───────────────────────────────────────────────
    tx = x + PAD
    ty = y + PAD

    # Date  (beside icon)
    _txt(slide, tx, ty, NARROW_W, DATE_H, date_str, 7)
    ty += DATE_H

    # "Key Question" (bold — full width, icon is small and above)
    _txt(slide, tx, ty, FULL_W, KQ_H, 'Key Question', 8, bold=True)
    ty += KQ_H

    # Question text (bold underline — full width)
    _txt(slide, tx, ty, FULL_W, Q_H, key_q, 9, bold=True, underline=True)
    ty += Q_H

    # LF (prepend 'LF: To ')
    _txt(slide, tx, ty, FULL_W, LF_H, f'LF: To {lf}', 7)
    ty += LF_H

    # I can statements
    _txt(slide, tx, ty, FULL_W, ICAN_H, f'I can {ican1}', 6.5)
    ty += ICAN_H
    _txt(slide, tx, ty, FULL_W, ICAN_H, f'I can {ican2}', 6.5)
