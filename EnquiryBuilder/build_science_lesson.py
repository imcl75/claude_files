#!/usr/bin/env python3
"""
build_science_lesson.py (v5) - MTP-JSON-driven Science enquiry lesson builder.

Unified MTP format: one JSON file per enquiry (lessons[] array), matching
History and Geography. Fixed slides 1-7 are auto-built; slides[] array in
the MTP contains only variable content slides.

Fixed slide sequence (auto-built, never listed in MTP slides[]):
  1. Key Question + challenge
  2. Being a Scientist
  3. Discipline (strand beaker)
  4. Building Blocks (atom model, 2-8-5 = 15 lessons)
  5. Learning Objective  (what / why / success)
  6. KWL (lesson 1) or Recap Quiz (lesson 2+)
  7. Key Vocabulary

Usage:
  python3 build_science_lesson.py <mtp_json> <templates_dir> <out_pptx> <manifest_out> [--lesson N]
"""
import sys, os, json, subprocess, argparse, math as _math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.path.isdir('/tmp/t6w7') and '/tmp/t6w7' not in sys.path:
    sys.path.insert(0, '/tmp/t6w7')
from lib_ooxml import (
    P, A, unzip, rezip, clear_slides, build_layout_map, src_dir,
    find_slide_by_anchor, clone, fresh, get_spTree, save,
    title_sp, body_sp, tbox, add_img, grid_geometry, animate,
    find_sp, get_sp_id, get_shape_id_by_name, set_text, delete_shapes_by_id, delete_shape_by_name,
    replace_image, find_pic_id_by_name, force_shrink_to_fit, strip_orphaned_media,
    clamp_callout_tail, strip_timing, extract_image_by_shape_name,
    xr, xw, xp, ex, SW, SH,
)
import science_registry as REG

# ── Sandbox compatibility patch ───────────────────────────────────────────────
import lib_ooxml as _lo_mod
from pathlib import Path as _Path
_SESSION_TMP = '/sessions/admiring-sleepy-wozniak'
_lo_src_cache = {}

def _patched_src_dir(pptx, k=None):
    k = k or pptx
    if k not in _lo_src_cache:
        dst = f'{_SESSION_TMP}/src_{os.getpid()}_{_Path(pptx).stem}'
        _lo_mod.unzip(pptx, dst)
        _lo_src_cache[k] = dst
    return _lo_src_cache[k]

_lo_mod.src_dir = _patched_src_dir
src_dir = _patched_src_dir

_orig_rezip = _lo_mod.rezip
def _patched_rezip(src, dst):
    import zipfile, shutil
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, src))
    shutil.rmtree(src, ignore_errors=True)
_lo_mod.rezip = _patched_rezip
rezip = _patched_rezip
# ─────────────────────────────────────────────────────────────────────────────

_MARGIN = 381000  # ~1cm side margin in EMU


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 1: Key Question + challenge
# ══════════════════════════════════════════════════════════════════════════════

def build_kq_challenge(work, templates, enquiry, lesson):
    pptx = templates[REG.COMPONENTS['kq_challenge']['template']]
    sn = find_slide_by_anchor(pptx, REG.KQ_CHALLENGE_ANCHOR, REG.KQ_CHALLENGE_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    delete_shapes_by_id(sp, REG.KQ_CHALLENGE_STRIP_IDS)
    delete_shape_by_name(sp, REG.KQ_CHALLENGE_STRIP_NAME)
    has_challenge = bool(enquiry.get('challenge'))
    if not has_challenge:
        delete_shape_by_name(sp, REG.KQ_CHALLENGE_TASK_SHAPE_NAME)
    tree = xr(sp)
    kq_shape = find_sp(tree, REG.KQ_CHALLENGE_KQ_SHAPE_NAME)
    if kq_shape is None:
        raise RuntimeError(f"kq_challenge: '{REG.KQ_CHALLENGE_KQ_SHAPE_NAME}' not found")
    set_text(kq_shape, enquiry['key_question'])
    if has_challenge:
        task_shape = find_sp(tree, REG.KQ_CHALLENGE_TASK_SHAPE_NAME)
        if task_shape is None:
            raise RuntimeError(f"kq_challenge: '{REG.KQ_CHALLENGE_TASK_SHAPE_NAME}' not found")
        set_text(task_shape, f"Our Challenge is: \n{enquiry['challenge']}")
    xw(tree, sp)
    print('  [1] key_question')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 2: Being a Scientist
# ══════════════════════════════════════════════════════════════════════════════

def build_being_a_scientist(work, templates):
    pptx = templates[REG.COMPONENTS['being_a_scientist']['template']]
    sn = find_slide_by_anchor(pptx, REG.BEING_A_SCIENTIST_ANCHOR, REG.BEING_A_SCIENTIST_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    print('  [2] being_a_scientist')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 3: Discipline / strand
# ══════════════════════════════════════════════════════════════════════════════

def build_discipline(work, templates, enquiry):
    strand = enquiry.get('strand', 'Biology')
    if strand not in REG.DISCIPLINE_ANCHORS:
        raise ValueError(f"Unknown strand '{strand}'. Must be one of {list(REG.DISCIPLINE_ANCHORS)}")
    pptx = templates[REG.COMPONENTS['discipline']['template']]
    sn = find_slide_by_anchor(pptx, REG.DISCIPLINE_ANCHORS[strand], REG.DISCIPLINE_HINTS[strand])
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    strip_timing(sp)
    steps = REG.DISCIPLINE_ANIMATION_SHAPE_NAMES.get(strand)
    if steps:
        tree = xr(sp)
        id_steps = []
        for step_names in steps:
            ids = []
            for name in step_names:
                sid = get_shape_id_by_name(tree, name)
                if sid is None:
                    raise RuntimeError(f"discipline ({strand}): shape '{name}' not found")
                ids.append(sid)
            id_steps.append(ids)
        animate(sp, id_steps)
    print('  [3] discipline')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 4: Building Blocks — atom model (2-8-5 shells, up to 15 lessons)
# ══════════════════════════════════════════════════════════════════════════════

def build_building_blocks_atom(work, enquiry, lesson, all_lessons):
    """
    Atom model: nucleus + 3 electron shells (Phosphorus: 2-8-5 = 15 electrons).
    Completed lessons: filled Y4 blue.
    Current lesson: filled Y4 blue, thick dark border.
    Future lessons: light grey, outline only.
    """
    lesson_num = lesson['lesson_number']
    topic = enquiry.get('topic', 'Science')

    sp, rp = fresh(work, 'I do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, f'Our Enquiry: {topic}', REG.TITLE_FONT))
    save(t, sp)

    # Atom geometry (EMU, slide = 12192000 × 6858000)
    CX, CY = 6096000, 3750000

    # (n_electrons, rx, ry) for each shell
    SHELLS = [
        (2, 900000,  760000),     # K shell — 2 electrons
        (8, 2050000, 1720000),    # L shell — 8 electrons
        (5, 3150000, 2450000),    # M shell — 5 electrons  (max = 15 = Phosphorus)
    ]

    NUCLEUS_RX   = 530000
    NUCLEUS_RY   = 440000
    ELECTRON_R   = 190000     # electron circle radius
    RING_W       = 19050      # orbital ring stroke (0.75 pt)
    DONE_W       = 19050      # completed electron border
    CURRENT_W    = 57150      # current lesson border (2.25 pt)

    WFA_BLUE     = '1798D3'
    DARK_BLUE    = '0A4A7A'
    RING_COL     = 'A8C8E0'
    EMPTY_FILL   = 'EBEBEB'
    EMPTY_STROKE = 'BBBBBB'

    sid = 10

    # Draw orbital rings (ellipses, back to front)
    for (n_e, rx, ry) in SHELLS:
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="Ring{rx}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm>'
            f'<a:off x="{CX - rx}" y="{CY - ry}"/>'
            f'<a:ext cx="{2*rx}" cy="{2*ry}"/></a:xfrm>'
            f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
            f'<a:noFill/>'
            f'<a:ln w="{RING_W}"><a:solidFill>'
            f'<a:srgbClr val="{RING_COL}"/></a:solidFill></a:ln>'
            f'</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>'
            f'</p:sp>'
        ))
        save(t2, sp); sid += 1

    # Nucleus
    t2, st2 = get_spTree(sp)
    st2.append(xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="Nucleus"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm>'
        f'<a:off x="{CX - NUCLEUS_RX}" y="{CY - NUCLEUS_RY}"/>'
        f'<a:ext cx="{2*NUCLEUS_RX}" cy="{2*NUCLEUS_RY}"/></a:xfrm>'
        f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{DARK_BLUE}"/></a:solidFill>'
        f'<a:ln w="0"><a:noFill/></a:ln>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr anchor="ctr" wrap="square"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="800" b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'<a:latin typeface="{REG.TITLE_FONT}"/></a:rPr>'
        f'<a:t>{ex(topic)}</a:t></a:r></a:p>'
        f'</p:txBody>'
        f'</p:sp>'
    ))
    save(t2, sp); sid += 1

    # Electrons (K first, then L, then M — numbered 1-15)
    electron_num = 0
    for (n_e, rx, ry) in SHELLS:
        for i in range(n_e):
            electron_num += 1
            angle = (2 * _math.pi * i / n_e) - _math.pi / 2  # start from 12 o'clock
            el_x = CX + int(rx * _math.cos(angle))
            el_y = CY + int(ry * _math.sin(angle))

            is_current = electron_num == lesson_num
            is_done    = electron_num < lesson_num
            is_future  = electron_num > lesson_num

            if is_future:
                fill_col, text_col, bdr_col, bdr_w = EMPTY_FILL, 'AAAAAA', EMPTY_STROKE, RING_W
            elif is_current:
                fill_col, text_col, bdr_col, bdr_w = WFA_BLUE, 'FFFFFF', DARK_BLUE, CURRENT_W
            else:  # done
                fill_col, text_col, bdr_col, bdr_w = WFA_BLUE, 'FFFFFF', WFA_BLUE, DONE_W

            t2, st2 = get_spTree(sp)
            st2.append(xp(
                f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
                f'<p:nvSpPr><p:cNvPr id="{sid}" name="Electron{electron_num}"/>'
                f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm>'
                f'<a:off x="{el_x - ELECTRON_R}" y="{el_y - ELECTRON_R}"/>'
                f'<a:ext cx="{2*ELECTRON_R}" cy="{2*ELECTRON_R}"/></a:xfrm>'
                f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{fill_col}"/></a:solidFill>'
                f'<a:ln w="{bdr_w}"><a:solidFill>'
                f'<a:srgbClr val="{bdr_col}"/></a:solidFill></a:ln>'
                f'</p:spPr>'
                f'<p:txBody>'
                f'<a:bodyPr anchor="ctr" wrap="square"/><a:lstStyle/>'
                f'<a:p><a:pPr algn="ctr"/>'
                f'<a:r><a:rPr lang="en-GB" sz="900" b="1" dirty="0">'
                f'<a:solidFill><a:srgbClr val="{text_col}"/></a:solidFill>'
                f'</a:rPr><a:t>{electron_num}</a:t></a:r></a:p>'
                f'</p:txBody>'
                f'</p:sp>'
            ))
            save(t2, sp); sid += 1

    # Current lesson label — bottom of slide
    current_lsn = next((l for l in all_lessons if l['lesson_number'] == lesson_num), lesson)
    bb_text = current_lsn.get('building_block_text', '')
    if bb_text:
        label = f'Lesson {lesson_num}: {bb_text}'
        t2, st2 = get_spTree(sp)
        st2.append(tbox(
            sid, label,
            _MARGIN, 6350000, SW - 2 * _MARGIN, 380000,
            sz=1600, bold=True, color='1A3A5C', align='ctr'
        ))
        save(t2, sp); sid += 1

    print('  [4] building_blocks_atom')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 5: Learning Objective  (what / why / success)
# ══════════════════════════════════════════════════════════════════════════════

def build_lo(work, templates, enquiry, lesson):
    pptx = templates[REG.COMPONENTS['lo']['template']]
    sn = find_slide_by_anchor(pptx, REG.COMPONENTS['lo']['anchor'], REG.COMPONENTS['lo']['hint'])
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    delete_shapes_by_id(sp, REG.LO_STALE_GROUP_IDS)
    tree = xr(sp)
    # TextBox 38 = what (I am learning…)
    # TextBox 39 = why  (This is because…)
    # TextBox 40 = success (I will show this by…)
    for shape_name, field in [
        ('Title 27',  'key_question'),
        ('TextBox 38', 'what'),
        ('TextBox 39', 'why'),
        ('TextBox 40', 'success'),
    ]:
        val = enquiry.get(field) if field == 'key_question' else lesson.get(field, '')
        s = find_sp(tree, shape_name)
        if s is not None:
            set_text(s, val or '')
        else:
            raise RuntimeError(f"LO slide: shape '{shape_name}' not found — template drift")
    xw(tree, sp)
    tree = xr(sp)
    ids = [get_sp_id(tree, n) for n in ('TextBox 38', 'TextBox 39', 'TextBox 40')]
    if not all(ids):
        raise RuntimeError("LO slide: could not resolve shape IDs for animation")
    animate(sp, [[i] for i in ids])
    print('  [5] lo')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 6a: KWL (lesson 1 only)
# ══════════════════════════════════════════════════════════════════════════════

def build_kwl(work, enquiry):
    """
    Two-column KWL grid: Prior Knowledge | I am curious about...
    Teacher fills in live on the whiteboard.
    """
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(
        2,
        'What knowledge am I bringing to this enquiry?\nWhat would I like to find out?',
        REG.TITLE_FONT,
    ))
    save(t, sp)

    tbl_x = _MARGIN
    tbl_y = 1300000      # clear the title
    tbl_w = SW - 2 * _MARGIN
    tbl_h = SH - tbl_y - 200000
    col_w = tbl_w // 2
    hdr_h = 500000
    body_h = tbl_h - hdr_h

    headers = ['Prior Knowledge and Skill', 'I am curious about…']
    sid = 10

    for ci, hdr in enumerate(headers):
        cx = tbl_x + ci * col_w
        # Header background
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="KWLHdrBG{ci}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{cx}" y="{tbl_y}"/>'
            f'<a:ext cx="{col_w}" cy="{hdr_h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="1798D3"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp); sid += 1
        t2, st2 = get_spTree(sp)
        st2.append(tbox(
            sid, hdr, cx + 30000, tbl_y + 20000, col_w - 60000, hdr_h - 40000,
            sz=1800, bold=True, color='FFFFFF', align='ctr'
        ))
        save(t2, sp); sid += 1

    # Body rows (3 empty rows for teacher to fill)
    row_h = body_h // 3
    for ri in range(3):
        ry = tbl_y + hdr_h + ri * row_h
        fill = 'F5F5F5' if ri % 2 == 0 else 'FFFFFF'
        for ci in range(2):
            cx = tbl_x + ci * col_w
            t2, st2 = get_spTree(sp)
            st2.append(xp(
                f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
                f'<p:nvSpPr><p:cNvPr id="{sid}" name="KWLCell{ri}{ci}"/>'
                f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{cx}" y="{ry}"/>'
                f'<a:ext cx="{col_w}" cy="{row_h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                f'<a:ln w="19050"><a:solidFill><a:srgbClr val="AAAAAA"/></a:solidFill></a:ln>'
                f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
            ))
            save(t2, sp); sid += 1

    print('  [6] kwl')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 6b: Recap Quiz (lessons 2+)
# ══════════════════════════════════════════════════════════════════════════════

def build_recap_quiz(work, quiz_template_pptx, lesson):
    """
    Clone the quiz recap template slide, populate Q/A, rebuild animation.
    Reads lesson['quiz']: list of {question: str, answer: str}
    """
    from lxml import etree as _et

    _A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    _P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'

    def _q_para(text, num):
        p = _et.Element(f'{{{_A_NS}}}p')
        pPr = _et.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '514350'); pPr.set('indent', '-514350')
        buFont = _et.SubElement(pPr, f'{{{_A_NS}}}buFont'); buFont.set('typeface', '+mj-lt')
        buAutoNum = _et.SubElement(pPr, f'{{{_A_NS}}}buAutoNum'); buAutoNum.set('type', 'arabicPeriod')
        if num > 1:
            buAutoNum.set('startAt', str(num))
        r = _et.SubElement(p, f'{{{_A_NS}}}r')
        rPr = _et.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('dirty', '0')
        t_ = _et.SubElement(r, f'{{{_A_NS}}}t'); t_.text = text
        return p

    def _a_para(text):
        p = _et.Element(f'{{{_A_NS}}}p')
        pPr = _et.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '0'); pPr.set('indent', '0')
        _et.SubElement(pPr, f'{{{_A_NS}}}buNone')
        r = _et.SubElement(p, f'{{{_A_NS}}}r')
        rPr = _et.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('b', '1'); rPr.set('dirty', '0')
        fill = _et.SubElement(rPr, f'{{{_A_NS}}}solidFill')
        clr = _et.SubElement(fill, f'{{{_A_NS}}}srgbClr'); clr.set('val', '00B050')
        sym = _et.SubElement(rPr, f'{{{_A_NS}}}sym')
        sym.set('typeface', 'Wingdings'); sym.set('pitchFamily', '2'); sym.set('charset', '2')
        t_ = _et.SubElement(r, f'{{{_A_NS}}}t'); t_.text = ' ' + text
        return p

    def _spacer_para():
        p = _et.Element(f'{{{_A_NS}}}p')
        pPr = _et.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '0'); pPr.set('indent', '0')
        _et.SubElement(pPr, f'{{{_A_NS}}}buNone')
        endPr = _et.SubElement(p, f'{{{_A_NS}}}endParaRPr')
        endPr.set('lang', 'en-GB'); endPr.set('sz', '600'); endPr.set('dirty', '0')
        sym = _et.SubElement(endPr, f'{{{_A_NS}}}sym')
        sym.set('typeface', 'Wingdings'); sym.set('pitchFamily', '2'); sym.set('charset', '2')
        return p

    sp, rp = clone(work, quiz_template_pptx, 1, copy_hdphoto=True)
    title_text = lesson.get('quiz_title', 'Recap – Quiz Time')
    tree = xr(sp)
    title_shape = find_sp(tree, 'Title 2')
    if title_shape is not None:
        set_text(title_shape, title_text)
    xw(tree, sp)

    tree = xr(sp)
    content_sp_el = find_sp(tree, 'Content Placeholder 2')
    if content_sp_el is None:
        raise RuntimeError("quiz_recap: 'Content Placeholder 2' not found — template drift")
    content_spid = int(content_sp_el.get('id', '3'))

    _P_NS2 = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    txBody = content_sp_el.find(f'{{{_P_NS2}}}txBody')
    if txBody is None:
        raise RuntimeError("quiz_recap: no txBody in content placeholder")
    for p_el in txBody.findall(f'{{{_A_NS}}}p'):
        txBody.remove(p_el)
    bodyPr = txBody.find(f'{{{_A_NS}}}bodyPr')
    if bodyPr is not None:
        for _bf in list(bodyPr):
            bodyPr.remove(_bf)
        bodyPr.set('wrap', 'square'); bodyPr.set('anchor', 't')

    qna = lesson.get('quiz', [])
    if not qna:
        print('  [6] recap_quiz (empty)')
        xw(tree, sp)
        return sp

    for i, item in enumerate(qna):
        txBody.append(_q_para(item['question'], i + 1))
        txBody.append(_a_para(item['answer']))
        if i < len(qna) - 1:
            txBody.append(_spacer_para())
    xw(tree, sp)

    animated = []
    for i in range(len(qna)):
        animated.append(i * 3); animated.append(i * 3 + 1)

    id_n = [1]
    def nid(): v = id_n[0]; id_n[0] += 1; return str(v)

    root_id = nid(); seq_id = nid()
    blocks = []
    for para_idx in animated:
        b, inner, click, behav = nid(), nid(), nid(), nid()
        blocks.append(
            f'<p:par xmlns:p="{_P_NS}"><p:cTn id="{b}" fill="hold">'
            f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{inner}" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{click}" presetID="1" presetClass="entr" '
            f'presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst><p:set><p:cBhvr>'
            f'<p:cTn id="{behav}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{content_spid}"><p:txEl>'
            f'<p:pRg st="{para_idx}" end="{para_idx}"/></p:txEl></p:spTgt></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
        )

    timing_xml = (
        f'<p:timing xmlns:p="{_P_NS}" xmlns:a="{A}">'
        f'<p:tnLst><p:par><p:cTn id="{root_id}" dur="indefinite" restart="never" '
        f'nodeType="tmRoot"><p:childTnLst>'
        f'<p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="{seq_id}" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst><p:bldP spid="{content_spid}" grpId="0" build="p"/></p:bldLst>'
        f'</p:timing>'
    )

    from lxml import etree as _et2
    tree = xr(sp)
    root = tree.getroot()
    existing = root.find(f'{{{_P_NS}}}timing')
    if existing is not None:
        root.remove(existing)
    root.append(_et2.fromstring(timing_xml))
    xw(tree, sp)

    print(f'  [6] recap_quiz — {len(qna)} question(s)')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 7: Key Vocabulary
# ══════════════════════════════════════════════════════════════════════════════

def build_key_vocabulary(work, lesson):
    """
    Word cards: coloured word panel (left) + definition panel (right).
    Each word+definition pair clicks in separately.
    Up to 5 words from lesson['vocabulary'].
    """
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, 'Key Vocabulary', REG.TITLE_FONT))
    save(t, sp)

    vocab = lesson.get('vocabulary', [])[:5]
    n = len(vocab)
    if n == 0:
        print('  [7] vocabulary (empty)')
        return sp

    card_top = 1200000
    card_gap = 50000
    card_h   = (SH - card_top - 200000 - (n - 1) * card_gap) // n
    card_w   = SW - 2 * _MARGIN
    word_w   = int(card_w * 0.28)
    def_x    = _MARGIN + word_w + 20000
    def_w    = card_w - word_w - 20000

    WORD_FILLS = ['DAE3F3', 'FFE6CC', 'D5E8D4', 'F8CECC', 'E1D5E7']

    sid = 10
    steps = []

    for i, item in enumerate(vocab):
        cy = card_top + i * (card_h + card_gap)
        fill = WORD_FILLS[i % len(WORD_FILLS)]

        # Word panel (coloured, left)
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="WordBG{i}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{_MARGIN}" y="{cy}"/>'
            f'<a:ext cx="{word_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect">'
            f'<a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="1798D3"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        wbg_id = sid; sid += 1

        t2, st2 = get_spTree(sp)
        word_sz = max(1400, 2000 - len(item.get('word', '')) * 20)
        st2.append(tbox(
            sid, item.get('word', ''),
            _MARGIN + 20000, cy + 20000, word_w - 40000, card_h - 40000,
            sz=word_sz, bold=True, color='1A3A5C', align='ctr'
        ))
        save(t2, sp)
        wtxt_id = sid; sid += 1

        steps.append([wbg_id, wtxt_id])  # word clicks in first

        # Definition panel (white, right)
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="DefBG{i}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{def_x}" y="{cy}"/>'
            f'<a:ext cx="{def_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect">'
            f'<a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="1798D3"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        dbg_id = sid; sid += 1

        t2, st2 = get_spTree(sp)
        st2.append(tbox(
            sid, item.get('definition', ''),
            def_x + 20000, cy + 20000, def_w - 40000, card_h - 40000,
            sz=1600, color='222222', align='l'
        ))
        save(t2, sp)
        dtxt_id = sid; sid += 1

        steps.append([dbg_id, dtxt_id])  # definition clicks in second

    animate(sp, steps)
    print('  [7] vocabulary (animated)')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Variable content slide builders
# ══════════════════════════════════════════════════════════════════════════════

def _build_wedo_hook(work, spec):
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1750000 + i * 1350000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 700000, by, SW - 1400000, 1250000, sz=2200, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp

def _build_wedo_grid(work, spec):
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    items = spec['items']
    n = len(items)
    cols = 4 if n > 4 else n
    rows = -(-n // cols)
    cells = grid_geometry(cols, rows)
    sid = 10
    for (cx, cy, cw, ch, iw, ih, lh), item in zip(cells, items):
        img_path = item['image_path']
        if not os.path.exists(img_path):
            raise RuntimeError(f"wedo_grid: image_path '{img_path}' missing")
        add_img(sp, rp, work, img_path, cx + 40000, cy + 20000, iw, ih, sid); sid += 1
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, item['label'], cx, cy + ih + 40000, cw, lh,
                        sz=1600, bold=True, color='1A3A5C', align='ctr'))
        save(t2, sp); sid += 1
    return sp

def _build_ido_diagram(work, spec):
    sp, rp = fresh(work, 'I do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT, bold=True))
    save(t, sp)
    if spec.get('image_path'):
        if not os.path.exists(spec['image_path']):
            raise RuntimeError(f"ido_diagram: image_path '{spec['image_path']}' missing")
        add_img(sp, rp, work, spec['image_path'], 5400000, 1600000, 6500000, 4800000, 3)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1550000 + i * 1540000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 180000, by, 5000000, 1500000, sz=1900, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp

def _build_youdo_provocation(work, spec):
    sp, rp = fresh(work, 'You do Ind')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    if not os.path.exists(spec['image_path']):
        raise RuntimeError(f"youdo_provocation: image_path '{spec['image_path']}' missing")
    add_img(sp, rp, work, spec['image_path'], 838200, 1700000, 10515600, 4900000, 3)
    return sp

def _build_youdo_task(work, spec):
    sp, rp = fresh(work, 'You do Ind')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1750000 + i * 1150000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 700000, by, SW - 1400000, 1050000, sz=2000, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp

def _build_concept_cartoon(work, templates, spec):
    pptx = templates[REG.COMPONENTS['concept_cartoon']['template']]
    sn = find_slide_by_anchor(pptx, REG.CONCEPT_CARTOON_ANCHOR, REG.CONCEPT_CARTOON_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    tree = xr(sp)
    title_shape = find_sp(tree, REG.CONCEPT_CARTOON_TITLE_SHAPE_NAME)
    if title_shape is not None and spec.get('title'):
        set_text(title_shape, spec['title'])
    learners = spec['learners']
    if len(learners) != 3:
        raise ValueError("concept_cartoon requires exactly 3 learners (A/B/C)")
    for bubble_name, learner in zip(REG.CONCEPT_CARTOON_BUBBLE_NAMES, learners):
        s = find_sp(tree, bubble_name)
        if s is None:
            raise RuntimeError(f"concept_cartoon: bubble '{bubble_name}' not found")
        set_text(s, learner['statement'])
        force_shrink_to_fit(s)
    xw(tree, sp)
    for bubble_name in REG.CONCEPT_CARTOON_BUBBLE_NAMES:
        clamp_callout_tail(sp, bubble_name)
    tree = xr(sp)
    pic_id = find_pic_id_by_name(tree, REG.CONCEPT_CARTOON_CENTRAL_IMAGE_SHAPE_NAME)
    if pic_id is None:
        raise RuntimeError("concept_cartoon: central image shape not found")
    if not spec.get('image_path') or not os.path.exists(spec['image_path']):
        raise RuntimeError(f"concept_cartoon: image_path missing — refusing to deliver cat/light template")
    replace_image(sp, rp, work, pic_id, spec['image_path'])
    tree = xr(sp)
    id_steps = []
    for step_names in REG.CONCEPT_CARTOON_ANIMATION_STEPS:
        ids = []
        for name in step_names:
            sid = get_shape_id_by_name(tree, name)
            if sid is None:
                raise RuntimeError(f"concept_cartoon: animated shape '{name}' not found")
            ids.append(sid)
        id_steps.append(ids)
    animate(sp, id_steps)
    return sp

def _build_learning_review(work, templates, spec):
    pptx = templates[REG.COMPONENTS['learning_review']['template']]
    sn = find_slide_by_anchor(pptx, REG.LEARNING_REVIEW_ANCHOR, REG.LEARNING_REVIEW_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    tree = xr(sp)
    starters = spec['starters']
    bmap = {'Bubble1': 0, 'Bubble2': 1, 'Bubble3': 2}
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            nm = el.get('name', '')
            if nm in bmap:
                set_text(s, starters[bmap[nm]]); break
    xw(tree, sp)
    return sp


# Variable slide dispatch — content slides ONLY (not infrastructure)
DISPATCH = {
    'wedo_hook':         lambda work, templates, spec: _build_wedo_hook(work, spec),
    'wedo_grid':         lambda work, templates, spec: _build_wedo_grid(work, spec),
    'ido_diagram':       lambda work, templates, spec: _build_ido_diagram(work, spec),
    'youdo_provocation': lambda work, templates, spec: _build_youdo_provocation(work, spec),
    'youdo_task':        lambda work, templates, spec: _build_youdo_task(work, spec),
    'concept_cartoon':   lambda work, templates, spec: _build_concept_cartoon(work, templates, spec),
    'learning_review':   lambda work, templates, spec: _build_learning_review(work, templates, spec),
}

CONTENT_SLIDE_TYPES = set(DISPATCH.keys())

# ══════════════════════════════════════════════════════════════════════════════
#  Orchestrator
# ══════════════════════════════════════════════════════════════════════════════

def build_lesson(mtp_path, templates_dir, out_path, manifest_path, lesson_num=1):
    with open(mtp_path) as f:
        mtp = json.load(f)

    # Support both unified (lessons[]) and legacy (lesson{}) formats
    if 'lessons' in mtp:
        lesson = next((l for l in mtp['lessons'] if l['lesson_number'] == lesson_num), None)
        if lesson is None:
            raise ValueError(f'Lesson {lesson_num} not found in MTP (available: '
                             f'{[l["lesson_number"] for l in mtp["lessons"]]})')
        all_lessons = mtp['lessons']
        # enquiry-level fields live at top level of unified MTP
        enquiry = {
            'key_question': mtp.get('key_question', ''),
            'challenge':    mtp.get('challenge', ''),
            'strand':       mtp.get('strand', 'Biology'),
            'topic':        mtp.get('topic', ''),
            'subject':      mtp.get('subject', 'science'),
            'year_group':   mtp.get('year_group', 'Y4'),
        }
    else:
        # Legacy single-lesson format (backwards compat)
        lesson_raw = mtp['lesson']
        lesson = {
            'lesson_number': lesson_raw.get('number', 1),
            'day_label':     lesson_raw.get('day', ''),
            'what':          lesson_raw.get('lo', ''),
            'why':           lesson_raw.get('tib', ''),
            'success':       lesson_raw.get('isb', ''),
            'vocabulary':    lesson_raw.get('vocabulary', []),
            'quiz':          lesson_raw.get('quiz', []),
            'slides':        lesson_raw.get('slides', []),
            'lp':            lesson_raw.get('lp'),
            'building_block_text': lesson_raw.get('building_block_text', ''),
            'skill_focus':   lesson_raw.get('skill_focus', 'questioning'),
        }
        all_lessons = [lesson]
        enq = mtp.get('enquiry', {})
        enquiry = {
            'key_question': lesson_raw.get('key_question', enq.get('key_question', '')),
            'challenge':    mtp.get('challenge', ''),
            'strand':       enq.get('science_strand', 'Biology'),
            'topic':        enq.get('topic', ''),
            'subject':      'science',
            'year_group':   enq.get('year_group', 'Y4'),
        }

    slides_spec = lesson.get('slides', [])

    # Validate content slide types
    for entry in slides_spec:
        t = entry.get('type')
        if t not in CONTENT_SLIDE_TYPES:
            if t in ('kq_challenge', 'being_a_scientist', 'discipline', 'lo'):
                raise ValueError(
                    f"Slide type '{t}' is auto-built in v5 — remove it from the slides[] array. "
                    f"Infrastructure slides are added automatically."
                )
            raise ValueError(f"Unknown slide type '{t}'. Known types: {sorted(CONTENT_SLIDE_TYPES)}")

    templates = {k: os.path.join(templates_dir, v) for k, v in REG.TEMPLATE_FILES.items()}
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _quiz_template = next(
        (p for p in [
            os.path.join(_this_dir, 'quiz_recap_template.pptx'),
            '/tmp/t6w7/quiz_recap_template.pptx',
        ] if os.path.exists(p)), None
    )
    for k, p in templates.items():
        if p and not os.path.exists(p):
            raise FileNotFoundError(f"Template '{k}' not found at {p}")

    work = f'{_SESSION_TMP}/bsl_{os.getpid()}_L{lesson_num}_work'
    unzip(templates['science_example'], work)
    clear_slides(work)
    build_layout_map(work)
    import lib_ooxml as _lib
    for k, v in REG.CONTENT_LAYOUTS.items():
        if v not in _lib._work_layouts:
            raise RuntimeError(f"Layout '{v}' not found in work presentation")
    for k in templates.values():
        if k:
            src_dir(k)

    print(f'\nLesson {lesson_num}: {lesson.get("building_block_text", "")}')

    manifest = []

    # ── Fixed slides 1-7 ─────────────────────────────────────────────────────
    build_kq_challenge(work, templates, enquiry, lesson)
    manifest.append({'output_index': 1, 'type': 'kq_challenge'})

    build_being_a_scientist(work, templates)
    manifest.append({'output_index': 2, 'type': 'being_a_scientist'})

    build_discipline(work, templates, enquiry)
    manifest.append({'output_index': 3, 'type': 'discipline'})

    build_building_blocks_atom(work, enquiry, lesson, all_lessons)
    manifest.append({'output_index': 4, 'type': 'building_blocks_atom'})

    build_lo(work, templates, enquiry, lesson)
    manifest.append({'output_index': 5, 'type': 'lo'})

    if lesson_num == 1:
        build_kwl(work, enquiry)
        manifest.append({'output_index': 6, 'type': 'kwl'})
    else:
        if _quiz_template is None:
            raise FileNotFoundError("quiz_recap_template.pptx not found — place it alongside this script")
        build_recap_quiz(work, _quiz_template, lesson)
        manifest.append({'output_index': 6, 'type': 'recap_quiz'})

    build_key_vocabulary(work, lesson)
    manifest.append({'output_index': 7, 'type': 'key_vocabulary'})

    # ── Variable content slides (8+) ──────────────────────────────────────────
    for i, entry in enumerate(slides_spec, start=8):
        t = entry['type']
        print(f"  [{i}] {t}: {entry.get('title', '')}")
        sp = DISPATCH[t](work, templates, entry)
        manifest.append({'output_index': i, 'type': t,
                         'slide_xml': os.path.basename(sp)})

    # ── Finalise ──────────────────────────────────────────────────────────────
    r = subprocess.run(['python3', '/mnt/skills/public/pptx/scripts/clean.py', work],
                      capture_output=True, text=True)
    if r.returncode != 0 and r.stderr.strip():
        print(f"  clean.py warning: {r.stderr.strip()[:300]}")

    removed = strip_orphaned_media(work)
    if removed:
        print(f"  stripped {len(removed)} orphaned media file(s)")

    rezip(work, out_path)
    with open(manifest_path, 'w') as f:
        json.dump({'mtp': mtp_path, 'lesson': lesson_num, 'slides': manifest}, f, indent=2)
    print(f"\n→ {out_path} ({os.path.getsize(out_path):,} bytes)")

    # ── Fix OOXML ─────────────────────────────────────────────────────────────
    fix_script = next(
        (p for p in [
            os.path.join(_this_dir, 'fix_pptx_ooxml.py'),
            '/tmp/t6w7/fix_pptx_ooxml.py',
        ] if os.path.exists(p)), None
    )
    if fix_script:
        r_fix = subprocess.run(['python3', fix_script, out_path], capture_output=True, text=True)
        if r_fix.returncode != 0:
            print(f'  fix_pptx_ooxml warning: {r_fix.stderr.strip()[:200]}')
        else:
            print('  fix_pptx_ooxml: OK')
    else:
        print('  fix_pptx_ooxml.py not found — skipping')

    # ── Verify ────────────────────────────────────────────────────────────────
    verify_script = next(
        (p for p in [
            os.path.join(_this_dir, 'verify_lesson.py'),
            '/tmp/t6w7/verify_lesson.py',
        ] if os.path.exists(p)), None
    )
    if verify_script:
        r_ver = subprocess.run(
            ['python3', verify_script, out_path, mtp_path, manifest_path],
            capture_output=True, text=True
        )
        print(r_ver.stdout.strip())
        if r_ver.returncode != 0:
            print('VERIFY FAILED — LP not built.')
            sys.exit(1)
    else:
        print('  verify_lesson.py not found — skipping')

    # ── Build LP ──────────────────────────────────────────────────────────────
    lp_spec = lesson.get('lp')
    if lp_spec is None:
        print("  No 'lp' key in lesson — skipping LP build")
    else:
        lp_path = os.path.splitext(out_path)[0] + ' LP.pptx'
        build_lp_script = next(
            (p for p in [
                os.path.join(_this_dir, 'build_lp.py'),
                f'{_SESSION_TMP}/mnt/outputs/build_lp.py',
                '/tmp/t6w7/build_lp.py',
            ] if os.path.exists(p)), None
        )
        if build_lp_script is None:
            print('  build_lp.py not found — skipping LP')
        else:
            lp_mod_dir = os.path.dirname(build_lp_script)
            if lp_mod_dir not in sys.path:
                sys.path.insert(0, lp_mod_dir)
            _rb_candidates = [os.path.dirname(os.path.abspath(mtp_path)), _this_dir, '/tmp/t6w7']
            resource_base = next(
                (c for c in _rb_candidates if os.path.isdir(os.path.join(c, 'll_assets'))),
                '/tmp/t6w7'
            )
            from build_lp import build_lp
            build_lp(mtp_path, lp_path, resource_base=resource_base)

    return out_path, manifest_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Science enquiry lesson builder v5')
    parser.add_argument('mtp_json')
    parser.add_argument('templates_dir')
    parser.add_argument('out_pptx')
    parser.add_argument('manifest_out')
    parser.add_argument('--lesson', type=int, default=1, help='Lesson number to build (default: 1)')
    args = parser.parse_args()
    build_lesson(args.mtp_json, args.templates_dir, args.out_pptx, args.manifest_out, args.lesson)
