#!/usr/bin/env python3
"""
build_lp.py — Generic enquiry Learning Paper builder.

Entry point:
    build_lp(lesson_json_path_or_dict, out_path, resource_base='/tmp/t6w7')

Reads the 'lp' key from the lesson JSON and renders a 2-slide A4 portrait
PPTX (slide 1 = pupil task, slide 2 = marking station).

Section types supported:
    heading, instruction, write_lines, word_bank, reference_image,
    row_boxes, pair_boxes, table, graph_template, sentence_starter, spacer,
    sort_table, sort_table_answers, marking_station, answer_text

Called automatically from build_science_lesson.py after VERIFY: PASS.
"""

import os, sys, json

# When imported, add /tmp/t6w7 to path so label_builder etc. are found
# (this is the session resource base; overridden at call time via resource_base param)
_DEFAULT_RESOURCE_BASE = '/tmp/t6w7'
if _DEFAULT_RESOURCE_BASE not in sys.path:
    sys.path.insert(0, _DEFAULT_RESOURCE_BASE)

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree
from PIL import Image as _PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Slide dimensions (A4 portrait) ─────────────────────────────────────────
SW_IN, SH_IN = 7.5, 10.833
SW, SH = int(SW_IN * 914400), int(SH_IN * 914400)
MARGIN = 0.25
LBL_Y  = MARGIN
CONT_X = MARGIN
CONT_W = SW_IN - 2 * MARGIN

BLUE   = RGBColor(0x17, 0x98, 0xD3)
DARK   = RGBColor(0x1A, 0x1A, 0x1A)
GREEN  = RGBColor(0x4F, 0xAD, 0x5B)
ORANGE = RGBColor(0xE6, 0x7E, 0x22)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LGREY  = RGBColor(0xCC, 0xCC, 0xCC)
EXBOOK = RGBColor(0xBD, 0xD7, 0xEE)
CREAM  = RGBColor(0xFE, 0xF9, 0xE7)

FONT_BODY = 'Twinkl Cursive Looped'

# Sort table column setup (L1-specific but kept here for reuse)
_SORT_COL_LABELS  = ['Material', 'State?', 'Reason (use the particle model)']
_SORT_COL_RATIO   = [0.26, 0.14, 0.60]


# ══════════════════════════════════════════════════════════════════
# Low-level PPTX helpers
# ══════════════════════════════════════════════════════════════════

def _new_prs():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(SW), Emu(SH)
    blank = prs.slide_layouts[6]
    prs.slides.add_slide(blank)
    prs.slides.add_slide(blank)
    return prs


def _clear_slide(slide):
    sp_tree = slide.shapes._spTree
    for child in list(sp_tree):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('sp', 'pic', 'graphicFrame', 'grpSp', 'cxnSp'):
            sp_tree.remove(child)


def _i(v):
    return Inches(v)


def _add_textbox(slide, x, y, w, h):
    return slide.shapes.add_textbox(_i(x), _i(y), _i(w), _i(h))


def _set_para(para, text, bold=False, italic=False, size_pt=10,
              color=None, font=FONT_BODY, align=PP_ALIGN.LEFT, underline=False):
    para.alignment = align
    run = para.add_run()
    run.text = text
    rf = run.font
    rf.name = font
    rf.size = Pt(size_pt)
    rf.bold = bold
    rf.italic = italic
    rf.underline = underline
    if color:
        rf.color.rgb = color
    return run


def _add_line(slide, x, y, w, color=None, width_pt=1.0):
    c = color if color is not None else EXBOOK
    hex_col = f'{c[0]:02X}{c[1]:02X}{c[2]:02X}'
    lw = int(Pt(width_pt))
    sp_tree = slide.shapes._spTree
    uid = max((int(el.get('id', 0)) for el in sp_tree.iter()
               if el.get('id') and el.get('id').isdigit()), default=100) + 1
    xml = (
        f'<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
        f' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:nvSpPr><p:cNvPr id="{uid}" name="Line{uid}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{int(Inches(x))}" y="{int(Inches(y))}"/>'
        f'<a:ext cx="{int(Inches(w))}" cy="0"/></a:xfrm>'
        f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>'
        f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{hex_col}"/></a:solidFill></a:ln>'
        f'<a:effectLst/></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )
    sp_tree.append(etree.fromstring(xml))


def _add_rect(slide, x, y, w, h, fill_rgb=None, line_rgb=None, line_pt=0.75):
    shape = slide.shapes.add_shape(1, _i(x), _i(y), _i(w), _i(h))
    if fill_rgb:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_rgb
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_pt)
    else:
        shape.line.fill.background()
    return shape


def _wrap_line_count(text, width_in, size_pt):
    """Estimate wrapped line count. Calibrated to Twinkl Cursive Looped at 0.46 chars/pt/width."""
    usable_w_pt = width_in * 72
    chars_per_line = max(1, int(usable_w_pt / (size_pt * 0.46)))
    words = text.split()
    lines, cur = 1, ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if len(test) <= chars_per_line:
            cur = test
        else:
            lines += 1
            cur = w
    return max(1, lines)


def _resolve_path(path, resource_base):
    """Return absolute path: try as-is first, then relative to resource_base."""
    if os.path.isabs(path) and os.path.exists(path):
        return path
    candidate = os.path.join(resource_base, path)
    if os.path.exists(candidate):
        return candidate
    raise FileNotFoundError(
        f"LP resource not found: '{path}' (also tried '{candidate}')")


# ══════════════════════════════════════════════════════════════════
# Section renderers
# ══════════════════════════════════════════════════════════════════

def _render_heading(slide, y, sec):
    text = sec['text']
    size_pt = sec.get('size_pt', 12)
    w = sec.get('w', CONT_W)
    n = _wrap_line_count(text, w, size_pt)
    h = (size_pt / 12) * 0.24 * n
    tb = _add_textbox(slide, CONT_X, y, w, h)
    tb.text_frame.word_wrap = True
    _set_para(tb.text_frame.paragraphs[0], text, bold=True, size_pt=size_pt, color=BLUE)
    return y + h + 0.06


def _render_instruction(slide, y, sec):
    text = sec['text']
    size_pt = sec.get('size_pt', 12)
    w = sec.get('w', CONT_W)
    n = _wrap_line_count(text, w, size_pt)
    h = (size_pt / 9.5) * 0.19 * n
    tb = _add_textbox(slide, CONT_X, y, w, h)
    tb.text_frame.word_wrap = True
    _set_para(tb.text_frame.paragraphs[0], text, size_pt=size_pt, color=DARK)
    return y + h + 0.08


def _render_write_lines(slide, y, sec):
    n = sec.get('n', 3)
    gap = sec.get('gap_in', 0.315)
    w = sec.get('w', CONT_W)
    x = sec.get('x', CONT_X)
    for _ in range(n):
        _add_line(slide, x, y, w)
        y += gap
    return y + 0.10


def _render_word_bank(slide, y, sec):
    words = sec['words']
    size_pt = sec.get('size_pt', 12)
    w = sec.get('w', CONT_W)
    n = _wrap_line_count('Word bank: ' + words, w - 0.1, size_pt)
    box_h = (size_pt / 9) * 0.20 * n + 0.14
    _add_rect(slide, CONT_X, y, w, box_h, fill_rgb=CREAM, line_rgb=ORANGE, line_pt=1.0)
    tb = _add_textbox(slide, CONT_X + 0.05, y + 0.05, w - 0.1, box_h - 0.08)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r1 = p.add_run()
    r1.text = 'Word bank: '
    r1.font.name = FONT_BODY
    r1.font.bold = True
    r1.font.size = Pt(size_pt)
    r1.font.color.rgb = ORANGE
    r2 = p.add_run()
    r2.text = words
    r2.font.name = FONT_BODY
    r2.font.size = Pt(size_pt)
    r2.font.color.rgb = DARK
    return y + box_h + 0.06


def _render_reference_image(slide, y, sec, resource_base):
    path = _resolve_path(sec['path'], resource_base)
    max_h = sec.get('max_h', 1.35)
    max_w = sec.get('max_w', CONT_W)
    iw, ih = _PILImage.open(path).size
    ratio = iw / ih
    h = max_h
    w = h * ratio
    if w > max_w:
        w = max_w
        h = w / ratio
    x = CONT_X + (CONT_W - w) / 2
    slide.shapes.add_picture(path, _i(x), _i(y), width=_i(w), height=_i(h))
    return y + h + 0.10


def _render_row_boxes(slide, y, sec):
    """Row of N equal-width boxes with text labels (e.g. L2 state labels)."""
    items = sec['items']
    box_h = sec.get('height', 0.36)
    size_pt = sec.get('size_pt', 10)
    n = len(items)
    gap = 0.10
    box_w = (CONT_W - gap * (n - 1)) / n
    x = CONT_X
    for label in items:
        _add_rect(slide, x, y, box_w, box_h, line_rgb=BLUE, line_pt=1.0)
        tb = _add_textbox(slide, x + 0.05, y + 0.06, box_w - 0.14, box_h - 0.12)
        _set_para(tb.text_frame.paragraphs[0], label, size_pt=size_pt, color=DARK)
        x += box_w + gap
    return y + box_h + 0.08


def _render_pair_boxes(slide, y, sec):
    """Two half-width boxes (e.g. L2 temperature fill-ins)."""
    items = sec['items']
    box_h = sec.get('height', 0.36)
    size_pt = sec.get('size_pt', 11)
    half_w = CONT_W / 2 - 0.1
    x = CONT_X
    for label in items[:2]:
        _add_rect(slide, x, y, half_w, box_h, line_rgb=BLUE, line_pt=1.0)
        tb = _add_textbox(slide, x + 0.06, y + 0.06, half_w - 0.12, box_h - 0.12)
        _set_para(tb.text_frame.paragraphs[0], label, size_pt=size_pt, color=DARK)
        x += half_w + 0.20
        y_next = y + box_h + 0.08
        y = y  # keep same y for second box
    return y_next


def _render_table(slide, y, sec):
    """Generic data table: coloured header + alternating data rows."""
    headers = sec['headers']   # [{text, frac, align?}]
    rows    = sec.get('rows', [])
    row_h   = sec.get('row_height', 0.38)
    hdr_col = sec.get('header_color', BLUE)
    body_size = sec.get('body_size_pt', 10)

    col_ws = [CONT_W * h['frac'] for h in headers]
    # header row
    x = CONT_X
    hdr_h = 0.30
    for hdr, cw in zip(headers, col_ws):
        al = PP_ALIGN.CENTER if hdr.get('align') == 'center' else PP_ALIGN.LEFT
        _add_rect(slide, x, y, cw - 0.02, hdr_h, fill_rgb=hdr_col)
        tb = _add_textbox(slide, x + 0.04, y + 0.04, cw - 0.10, hdr_h - 0.06)
        _set_para(tb.text_frame.paragraphs[0], hdr['text'],
                  bold=True, size_pt=10, color=WHITE, align=al)
        x += cw
    y += hdr_h

    # data rows
    for i, row in enumerate(rows):
        fill = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
        x = CONT_X
        for j, (cell, cw) in enumerate(zip(row, col_ws)):
            # auto-grow row height if text wraps
            al = PP_ALIGN.CENTER if headers[j].get('align') == 'center' else PP_ALIGN.LEFT
            nlines = _wrap_line_count(cell, cw - 0.08, body_size) if cell else 1
            this_h = max(row_h, 0.08 + nlines * (body_size * 1.35 / 72))
            _add_rect(slide, x, y, cw - 0.02, this_h,
                      fill_rgb=fill, line_rgb=LGREY, line_pt=0.5)
            if cell:
                tb = _add_textbox(slide, x + 0.04, y + 0.06, cw - 0.10, this_h - 0.08)
                tb.text_frame.word_wrap = True
                _set_para(tb.text_frame.paragraphs[0], cell,
                          size_pt=body_size, color=DARK, align=al)
            x += cw
        y += this_h
    return y


def _render_graph_template(slide, y, sec, resource_base):
    """Generate a blank axes matplotlib figure and embed it."""
    filename = sec['filename']
    # If filename is an absolute path use it; otherwise put in resource_base/images/
    if os.path.isabs(filename):
        graph_path = filename
    else:
        graph_path = os.path.join(resource_base, 'images', filename)

    # Only regenerate if the file doesn't already exist
    if not os.path.exists(graph_path):
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.set_xlim(*sec.get('xlim', [0, 10]))
        ax.set_ylim(*sec.get('ylim', [0, 100]))
        ax.set_xlabel(sec.get('xlabel', ''), fontsize=11)
        ax.set_ylabel(sec.get('ylabel', ''), fontsize=11)
        ax.set_title(sec.get('title', ''), fontsize=12, fontweight='bold')
        if 'xticks' in sec:
            ax.set_xticks(sec['xticks'])
        if 'yticks' in sec:
            ax.set_yticks(sec['yticks'])
        ax.grid(True, alpha=0.4, linestyle='--')
        for spine in ax.spines.values():
            spine.set_color('#1A3A5C')
        plt.tight_layout()
        plt.savefig(graph_path, dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()

    max_h = sec.get('max_h', 2.0)
    iw, ih = _PILImage.open(graph_path).size
    ratio = iw / ih
    h = max_h
    w = min(h * ratio, CONT_W)
    if w == CONT_W:
        h = w / ratio
    x = CONT_X + (CONT_W - w) / 2
    slide.shapes.add_picture(graph_path, _i(x), _i(y), width=_i(w), height=_i(h))
    return y + h + 0.10


def _render_sentence_starter(slide, y, sec):
    """Blue-tinted box with italic sentence starter."""
    text = sec['text']
    size_pt = sec.get('size_pt', 12)
    box_h = 0.38
    _add_rect(slide, CONT_X, y, CONT_W, box_h,
              fill_rgb=RGBColor(0xDE, 0xEC, 0xF8), line_rgb=BLUE, line_pt=1.5)
    tb = _add_textbox(slide, CONT_X + 0.08, y + 0.07, CONT_W - 0.16, box_h - 0.14)
    _set_para(tb.text_frame.paragraphs[0], text, italic=True,
              size_pt=size_pt, color=DARK)
    return y + box_h + 0.08


def _render_sort_table(slide, y, sec):
    """L1 sort table: 3-column header + blank rows for each material."""
    materials = sec['materials']
    size_pt   = sec.get('size_pt', 10)
    row_h     = sec.get('row_height', 0.36)
    col_ws    = [CONT_W * r for r in _SORT_COL_RATIO]

    # header
    hdr_h = max(0.28, 0.08 + (size_pt * 1.35 / 72))
    x = CONT_X
    for lbl, cw in zip(_SORT_COL_LABELS, col_ws):
        _add_rect(slide, x, y, cw, hdr_h, fill_rgb=BLUE)
        tb = _add_textbox(slide, x + 0.04, y + 0.03, cw - 0.08, hdr_h - 0.06)
        tb.text_frame.word_wrap = True
        _set_para(tb.text_frame.paragraphs[0], lbl, bold=True, size_pt=size_pt, color=WHITE)
        x += cw
    y += hdr_h

    # blank rows with material name pre-filled
    for i, mat in enumerate(materials):
        n = _wrap_line_count(mat, col_ws[0] - 0.08, size_pt)
        this_h = max(row_h, 0.08 + n * (size_pt * 1.3 / 72))
        fill = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
        x = CONT_X
        for j, cw in enumerate(col_ws):
            _add_rect(slide, x, y, cw, this_h, fill_rgb=fill, line_rgb=LGREY, line_pt=0.5)
            if j == 0:
                tb = _add_textbox(slide, x + 0.04, y + 0.04, cw - 0.08, this_h - 0.08)
                tb.text_frame.word_wrap = True
                _set_para(tb.text_frame.paragraphs[0], mat, size_pt=size_pt, color=DARK)
            x += cw
        y += this_h
    return y


def _render_sort_table_answers(slide, y, sec):
    """L1 marking: sort table with all three cells filled in green."""
    answers  = sec['answers']   # [[material, state, reason], ...]
    size_pt  = sec.get('size_pt', 8)
    col_ws   = [CONT_W * r for r in _SORT_COL_RATIO]

    for row in answers:
        n = max(_wrap_line_count(c, cw - 0.08, size_pt)
                for c, cw in zip(row, col_ws))
        row_h = max(0.26, 0.10 + n * (size_pt * 1.35 / 72))
        x = CONT_X
        for cell, cw in zip(row, col_ws):
            tb = _add_textbox(slide, x + 0.04, y + 0.02, cw - 0.08, row_h - 0.04)
            tb.text_frame.word_wrap = True
            _set_para(tb.text_frame.paragraphs[0], cell, size_pt=size_pt, color=GREEN)
            x += cw
        y += row_h
    return y


def _render_marking_station(slide, y, sec):
    title = sec.get('title', 'Marking Station')
    tb = _add_textbox(slide, CONT_X, y, CONT_W, 0.40)
    _set_para(tb.text_frame.paragraphs[0], title, bold=True, size_pt=16, color=GREEN)
    return y + 0.45


def _render_answer_text(slide, y, sec):
    text = sec['text']
    bold = sec.get('bold', False)
    size_pt = sec.get('size_pt', 9.5)
    w = sec.get('w', CONT_W)
    n = _wrap_line_count(text, w, size_pt)
    h = 0.19 * n
    tb = _add_textbox(slide, CONT_X, y, w, h)
    tb.text_frame.word_wrap = True
    _set_para(tb.text_frame.paragraphs[0], text, bold=bold, size_pt=size_pt, color=GREEN)
    return y + h + 0.06


# ── dispatch ────────────────────────────────────────────────────────────────
_SECTION_RENDERERS = {
    'heading':            lambda slide, y, sec, rb: _render_heading(slide, y, sec),
    'instruction':        lambda slide, y, sec, rb: _render_instruction(slide, y, sec),
    'write_lines':        lambda slide, y, sec, rb: _render_write_lines(slide, y, sec),
    'word_bank':          lambda slide, y, sec, rb: _render_word_bank(slide, y, sec),
    'reference_image':    _render_reference_image,
    'row_boxes':          lambda slide, y, sec, rb: _render_row_boxes(slide, y, sec),
    'pair_boxes':         lambda slide, y, sec, rb: _render_pair_boxes(slide, y, sec),
    'table':              lambda slide, y, sec, rb: _render_table(slide, y, sec),
    'graph_template':     _render_graph_template,
    'sentence_starter':   lambda slide, y, sec, rb: _render_sentence_starter(slide, y, sec),
    'spacer':             lambda slide, y, sec, rb: y + sec.get('h', 0.1),
    'sort_table':         lambda slide, y, sec, rb: _render_sort_table(slide, y, sec),
    'sort_table_answers': lambda slide, y, sec, rb: _render_sort_table_answers(slide, y, sec),
    'marking_station':    lambda slide, y, sec, rb: _render_marking_station(slide, y, sec),
    'answer_text':        lambda slide, y, sec, rb: _render_answer_text(slide, y, sec),
}


def _render_section(slide, sec, y, resource_base):
    t = sec['type']
    renderer = _SECTION_RENDERERS.get(t)
    if renderer is None:
        raise ValueError(f"Unknown LP section type: '{t}'")
    return renderer(slide, y, sec, resource_base)


# ══════════════════════════════════════════════════════════════════
# Label builder
# ══════════════════════════════════════════════════════════════════

def _add_label(slide, lp_spec, lesson, resource_base, png_dest):
    """Place the WFA enquiry label and return the y position below it."""
    # Import here so the path patch is applied first by the caller
    from label_builder import build_enquiry_label, LL_W

    lf = lp_spec.get('lf') or lesson.get('lo', '')
    label_h = build_enquiry_label(
        slide,
        SW_IN - LL_W - MARGIN,
        LBL_Y,
        date_str=lp_spec.get('date', ''),
        key_q=lesson.get('key_question', ''),
        lf=lf,
        ican1=lp_spec.get('ican1', ''),
        ican2=lp_spec.get('ican2', ''),
        icon_path=None,
        subject='scientist',
        year='Y4',
        png_dest=png_dest,
    )
    LABEL_SCALE = 0.707
    label_pic = slide.shapes[-1]
    new_w = LL_W * LABEL_SCALE
    new_h = label_h * LABEL_SCALE
    label_pic.left = _i(SW_IN - new_w - MARGIN)
    label_pic.top  = _i(LBL_Y)
    label_pic.width  = _i(new_w)
    label_pic.height = _i(new_h)
    return LBL_Y + new_h + 0.15


# ══════════════════════════════════════════════════════════════════
# Public entry point
# ══════════════════════════════════════════════════════════════════

def build_lp(lesson_json_or_path, out_path, resource_base=None):
    """
    Build the LP PPTX for a single lesson.

    Args:
        lesson_json_or_path: path to lesson JSON file, or an already-loaded dict.
        out_path:            where to write the output PPTX.
        resource_base:       directory containing ll_assets/, images/, etc.
                             Defaults to dirname of lesson_json_or_path (if path),
                             or /tmp/t6w7 (if dict).
    Returns:
        out_path on success.
    """
    # Load JSON
    if isinstance(lesson_json_or_path, (str, os.PathLike)):
        json_path = str(lesson_json_or_path)
        with open(json_path) as f:
            lesson_data = json.load(f)
        if resource_base is None:
            resource_base = os.path.dirname(os.path.abspath(json_path))
    else:
        lesson_data = lesson_json_or_path
        if resource_base is None:
            resource_base = _DEFAULT_RESOURCE_BASE

    lesson  = lesson_data['lesson']
    lp_spec = lesson.get('lp')
    if lp_spec is None:
        raise ValueError(
            "Lesson JSON has no 'lp' key — add an 'lp' spec before calling build_lp()")

    # Patch assets path for the label builder
    if resource_base not in sys.path:
        sys.path.insert(0, resource_base)
    import build_enquiry_label as _bel
    _bel.ASSETS = os.path.join(resource_base, 'll_assets')

    prs = _new_prs()
    s1, s2 = prs.slides[0], prs.slides[1]
    _clear_slide(s1)
    _clear_slide(s2)

    # Label on slide 1; returns y-start for content
    # PNG must be on a real filesystem (not FUSE) because PyMuPDF does
    # a remove-before-write internally. Use /sessions/ (ext4) as temp.
    _tmp_dir = '/sessions/admiring-sleepy-wozniak'
    if not os.path.isdir(_tmp_dir):
        _tmp_dir = os.path.dirname(os.path.abspath(out_path))
    png_dest = os.path.join(_tmp_dir, f'_lp_label_{os.getpid()}.png')
    y1 = _add_label(s1, lp_spec, lesson, resource_base, png_dest)

    # Split sections at the first 'marking_station' — everything before → slide 1
    all_sections = lp_spec.get('sections', [])
    try:
        split_at = next(i for i, s in enumerate(all_sections) if s['type'] == 'marking_station')
    except StopIteration:
        split_at = len(all_sections)

    s1_sections = all_sections[:split_at]
    s2_sections = all_sections[split_at:]   # includes the marking_station entry

    for sec in s1_sections:
        y1 = _render_section(s1, sec, y1, resource_base)

    y2 = 0.30
    for sec in s2_sections:
        y2 = _render_section(s2, sec, y2, resource_base)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    prs.save(out_path)

    # Clean up the temp label PNG (ignore errors on FUSE mounts)
    try:
        if os.path.exists(png_dest):
            os.remove(png_dest)
    except OSError:
        pass

    size_kb = os.path.getsize(out_path) // 1024
    print(f"  LP -> {out_path} ({size_kb} KB)")
    return out_path


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Build an enquiry LP from a lesson JSON.')
    ap.add_argument('lesson_json')
    ap.add_argument('out_pptx')
    ap.add_argument('--resource-base', default=None)
    args = ap.parse_args()
    build_lp(args.lesson_json, args.out_pptx, resource_base=args.resource_base)
