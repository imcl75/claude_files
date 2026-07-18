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
_SESSION_TMP = '/tmp/bsl_work'
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
        # TextBox 17 has spAutoFit — the box grows to fit and overlaps the
        # student images below. force_shrink_to_fit computes an explicit sz
        # on each rPr so the text stays inside the fixed box in both
        # LibreOffice and real PowerPoint (normAutofit alone doesn't work
        # in LibreOffice — it ignores the instruction and renders at default
        # size, confirmed by visual QA on v2_slide_1.png).
        force_shrink_to_fit(task_shape)
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
    steps = REG.DISCIPLINE_ANIMATION_SHAPE_NAMES.get(strand)
    if steps:
        # Only strip+rebuild timing for strands where we have confirmed shape names.
        # For all other strands, keep the template's own animations intact.
        strip_timing(sp)
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
    # else: template animations cloned as-is — do NOT strip them
    print('  [3] discipline')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide 4: Building Blocks — atom model (programmatic, animated)
#  All positions in EMU, derived from Group 205 in atom-IM.pptx.
#  No external template file required.
# ══════════════════════════════════════════════════════════════════════════════

# ── Coordinate transform constants (Group 205 in atom-IM.pptx) ────────────────
# Slide coords = GRP_OX + (child_x − CH_OX) * SX,  similarly for Y.
_ATOM_GRP_OX = 3264196
_ATOM_GRP_OY = 464046
_ATOM_SX = 8452884 / 6371657   # ~1.3266
_ATOM_SY = 6166392 / 5090000   # ~1.2115
_ATOM_CH_OX = 2910171
_ATOM_CH_OY = 1110000
_ATOM_ELECTRON_R = 190000       # half-radius in child coords

# Nucleus (child centre 6096000, 3750000 → slide)
_ATOM_NUC_X  = int(_ATOM_GRP_OX + (6096000 - _ATOM_CH_OX) * _ATOM_SX)
_ATOM_NUC_Y  = int(_ATOM_GRP_OY + (3750000 - _ATOM_CH_OY) * _ATOM_SY)
_ATOM_NUC_RX = int(530000 * _ATOM_SX)
_ATOM_NUC_RY = int(440000 * _ATOM_SY)

# Orbital ring semi-axes in slide coords (child radii scaled)
_ATOM_RING_PARAMS = [
    (int(900000  * _ATOM_SX), int(760000  * _ATOM_SY)),   # K shell
    (int(2050000 * _ATOM_SX), int(1720000 * _ATOM_SY)),   # L shell
    (int(3150000 * _ATOM_SX), int(2450000 * _ATOM_SY)),   # M shell
]

# Electron centres in child coords (14 active lessons)
_ATOM_CHILD_CENTRES = [
    (6096000, 2990000), (6096000, 4510000),
    (6096000, 2030000), (7545568, 2533776),
    (8146000, 3750000), (7545568, 4966223),
    (6096000, 5470000), (4646431, 4966223),
    (4046000, 3750000), (4646431, 2533776),
    (6096000, 1300000), (9091828, 2992908),
    (7947523, 5732091), (4244476, 5732091),
]

_ATOM_LESSON_NAMES = [
    "The Universe", "Our Solar System", "Sizes and Distances",
    "Day, Night and the Seasons", "The Moon", "Planet Conditions",
    "Relative Clauses", "Parenthesis", "Planning",
    "Writing 1", "Writing 2", "Writing 3", "Editing", "Sharing",
]

# Label positions (slide coords, hand-tuned by teacher on atom-IM.pptx slide 4)
_ATOM_LABEL_POS = [
    (7208270,  2226344, 1162498, 307777),
    (6874683,  4812456, 1527982, 307777),
    (6719341,  1069430, 1704313, 307777),
    (8521921,  1449189, 1726888, 523220),
    (9769736,  3093923,  939680, 307777),
    (8783924,  4648576, 1547218, 307777),
    (6927582,  5963340, 1422184, 307777),
    (5027247,  4577164, 1064715, 307777),
    (4344495,  3106286,  875560, 307777),
    (5113635,  1667649,  878767, 307777),
    (7038427,   151511,  904415, 307777),
    (10849956, 2194282,  899605, 307777),
    (9641910,  6293759,  728083, 307777),
    (4606235,  6267824,  780983, 307777),
]

_ATOM_ABBREV = [
    "1", "2",
    "Size", "D/N", "Moon", "Cond", "Rel", "Par", "Plan", "Wrt1",
    "Wrt2", "Wrt3", "Edit", "Shr",
]

_ATOM_ORANGE_ID = 1000
_ATOM_LABEL_ID  = 1001


# ── Coordinate helpers ─────────────────────────────────────────────────────────

def _atom_child_to_slide(cx, cy):
    return (
        int(_ATOM_GRP_OX + (cx - _ATOM_CH_OX) * _ATOM_SX),
        int(_ATOM_GRP_OY + (cy - _ATOM_CH_OY) * _ATOM_SY),
    )

def _atom_electron_rect(ccx, ccy):
    r = _ATOM_ELECTRON_R
    tl_x, tl_y = _atom_child_to_slide(ccx - r, ccy - r)
    br_x, br_y = _atom_child_to_slide(ccx + r, ccy + r)
    return tl_x, tl_y, br_x - tl_x, br_y - tl_y


# ── XML factories (use P and A from lib_ooxml) ────────────────────────────────

def _atom_ring_xml(sid, rx, ry):
    nx, ny = _ATOM_NUC_X, _ATOM_NUC_Y
    return (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="Ring{sid}"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{nx-rx}" y="{ny-ry}"/>'
        f'<a:ext cx="{2*rx}" cy="{2*ry}"/></a:xfrm>'
        f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'<a:ln w="19050"><a:solidFill><a:srgbClr val="A8C8E0"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>'
        f'</p:sp>'
    )

def _atom_nucleus_xml(sid, topic):
    nx, ny = _ATOM_NUC_X, _ATOM_NUC_Y
    rx, ry = _ATOM_NUC_RX, _ATOM_NUC_RY
    return (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="Nucleus"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{nx-rx}" y="{ny-ry}"/>'
        f'<a:ext cx="{2*rx}" cy="{2*ry}"/></a:xfrm>'
        f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="0A3D62"/></a:solidFill>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr anchor="ctr" wrap="square"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="800" b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'<a:latin typeface="Aptos"/></a:rPr>'
        f'<a:t>{topic}</a:t></a:r></a:p>'
        f'</p:txBody>'
        f'</p:sp>'
    )

def _atom_electron_xml(sid, left, top, ecx, ecy, fill, border, bw, text, tcol):
    return (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="El{sid}"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{left}" y="{top}"/><a:ext cx="{ecx}" cy="{ecy}"/></a:xfrm>'
        f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
        f'<a:ln w="{bw}"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{tcol}"/></a:solidFill>'
        f'</a:rPr><a:t>{text}</a:t></a:r></a:p>'
        f'</p:txBody>'
        f'</p:sp>'
    )

def _atom_orange_overlay_xml(shape_id, left, top, cx, cy, num):
    """Hidden orange electron for current lesson, revealed on click."""
    return (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{shape_id}" name="OrangeEl{num}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{left}" y="{top}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="E57D24"/></a:solidFill>'
        f'<a:ln w="19050"><a:solidFill><a:srgbClr val="A35610"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'</a:rPr><a:t>{num}</a:t></a:r></a:p>'
        f'</p:txBody>'
        f'</p:sp>'
    )

def _atom_label_xml(shape_id, text, left, top, w, h):
    return (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{shape_id}" name="LessonLabel"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{int(left)}" y="{int(top)}"/>'
        f'<a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/></p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr wrap="none" rtlCol="0"><a:spAutoFit/></a:bodyPr>'
        f'<a:lstStyle/>'
        f'<a:p><a:r>'
        f'<a:rPr lang="en-US" sz="1400" b="1" dirty="0">'
        f'<a:latin typeface="Twinkl Cursive Looped" pitchFamily="2" charset="77"/>'
        f'</a:rPr>'
        f'<a:t>{text}</a:t>'
        f'</a:r></a:p>'
        f'</p:txBody></p:sp>'
    )

def _atom_timing_xml(orange_id, label_id):
    """Confirmed-working one-click timing XML (mirrors geo jigsaw pattern)."""
    return (
        f'<p:timing xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        f'<p:childTnLst>'
        f'<p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>'
        f'<p:par><p:cTn id="3" fill="hold">'
        f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
        f'<p:childTnLst><p:par><p:cTn id="4" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f'<p:childTnLst>'
        f'<p:par><p:cTn id="5" presetID="1" presetClass="entr" presetSubtype="0"'
        f' fill="hold" nodeType="clickEffect">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f'<p:childTnLst><p:set><p:cBhvr>'
        f'<p:cTn id="6" dur="1" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{orange_id}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
        f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to>'
        f'</p:set></p:childTnLst></p:cTn></p:par>'
        f'<p:par><p:cTn id="7" presetID="1" presetClass="entr" presetSubtype="0"'
        f' fill="hold" nodeType="withEffect">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
        f'<p:childTnLst><p:set><p:cBhvr>'
        f'<p:cTn id="8" dur="1" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{label_id}"/></p:tgtEl>'
        f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
        f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to>'
        f'</p:set></p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq>'
        f'</p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst>'
        f'<p:bldP spid="{orange_id}" grpId="0" build="p"/>'
        f'<p:bldP spid="{label_id}" grpId="0" build="p"/>'
        f'</p:bldLst>'
        f'</p:timing>'
    )


def build_building_blocks_atom(work, templates, enquiry, lesson, all_lessons):
    """
    Atom model building-blocks slide — fully programmatic, no external file.

    Draws orbital rings, nucleus and all 14 electrons in slide-space coordinates
    derived from the atom-IM.pptx group transform (hardcoded constants above).
    Done electrons (< lesson_num) are orange and immediately visible.
    Current lesson is grey with a hidden orange overlay + label that appears
    on one mouse click.
    """
    from lxml import etree

    lesson_num = lesson['lesson_number']
    topic = enquiry.get('topic', 'Science')

    sp, rp = fresh(work, 'I do')
    t, st = get_spTree(sp)
    # Use an explicit tbox positioned in the top-left corner, clear of the orbit.
    # The outermost orbit left-edge is at ~x=3,300,000 so x=300,000–3,000,000
    # is safe. The orbit's top is at ~y=694,000 so y=120,000–680,000 is clear
    # of all electrons. Do NOT use title_sp (layout placeholder) — it puts the
    # title in the slide's default title area which overlaps the top orbit arc.
    st.append(tbox(
        2, f'Building Blocks: {topic}',
        300000, 120000, 2900000, 580000,
        sz=2000, bold=False, color='1A3A5C', align='l',
        name='Title 2',
    ))
    save(t, sp)

    tree    = xr(sp)
    root    = tree.getroot()
    sp_tree = root.find(f'{{{P}}}cSld').find(f'{{{P}}}spTree')

    sid = 50   # start above layout shape IDs

    # Orbital rings — draw M first (back), then L, then K (front)
    for rx, ry in reversed(_ATOM_RING_PARAMS):
        sp_tree.append(etree.fromstring(_atom_ring_xml(sid, rx, ry)))
        sid += 1

    # Nucleus
    sp_tree.append(etree.fromstring(_atom_nucleus_xml(sid, ex(topic))))
    sid += 1

    # Base electrons (grey or orange depending on state)
    for i, (ccx, ccy) in enumerate(_ATOM_CHILD_CENTRES):
        les = i + 1
        left, top, ecx, ecy = _atom_electron_rect(ccx, ccy)
        if les < lesson_num:    # done — orange, lesson number
            sp_tree.append(etree.fromstring(
                _atom_electron_xml(sid, left, top, ecx, ecy,
                                   'E57D24', 'A35610', 19050, str(les), 'FFFFFF')
            ))
        else:                   # current or future — grey, no text (clean circles)
            sp_tree.append(etree.fromstring(
                _atom_electron_xml(sid, left, top, ecx, ecy,
                                   'EBEBEB', 'BBBBBB', 19050, '', 'AAAAAA')
            ))
        sid += 1

    # Static labels for completed lessons (immediately visible)
    for i in range(lesson_num - 1):
        lx, ly, lw, lh = _ATOM_LABEL_POS[i]
        sp_tree.append(etree.fromstring(
            _atom_label_xml(2000 + i, _ATOM_LESSON_NAMES[i], lx, ly, lw, lh)
        ))

    # Orange overlay + label for current lesson (hidden until click)
    ci = lesson_num - 1
    ccx, ccy = _ATOM_CHILD_CENTRES[ci]
    left, top, ecx, ecy = _atom_electron_rect(ccx, ccy)
    sp_tree.append(etree.fromstring(
        _atom_orange_overlay_xml(_ATOM_ORANGE_ID, left, top, ecx, ecy, lesson_num)
    ))
    lx, ly, lw, lh = _ATOM_LABEL_POS[ci]
    sp_tree.append(etree.fromstring(
        _atom_label_xml(_ATOM_LABEL_ID, _ATOM_LESSON_NAMES[ci], lx, ly, lw, lh)
    ))

    # Attach one-click animation timing
    for old in root.findall(f'{{{P}}}timing'):
        root.remove(old)
    root.append(etree.fromstring(_atom_timing_xml(_ATOM_ORANGE_ID, _ATOM_LABEL_ID)))

    xw(tree, sp)
    print(f'  [4] building_blocks_atom (L{lesson_num} animated)')
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
            if shape_name == 'Title 27':
                # KQ_LO.pptx Title 27 has anchor="b" — long key questions grow
                # upward off the top of the slide. Fix: change anchor to "t" so
                # text flows down from the top of the box, then force_shrink_to_fit
                # writes an explicit sz on each run so the text stays within the box
                # in both LibreOffice and real PowerPoint.
                # NOTE: txBody in a p:sp shape is in the PML namespace (p:txBody),
                # NOT the DrawingML namespace — using A_NS here silently finds nothing.
                _P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
                _A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
                txBody = s.find(f'{{{_P_NS}}}txBody')
                if txBody is not None:
                    bodyPr = txBody.find(f'{{{_A_NS}}}bodyPr')
                    if bodyPr is not None:
                        bodyPr.set('anchor', 't')
                force_shrink_to_fit(s)
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
        pPr.set('marL', '457200'); pPr.set('indent', '-457200')
        buFont = _et.SubElement(pPr, f'{{{_A_NS}}}buFont'); buFont.set('typeface', '+mj-lt')
        buAutoNum = _et.SubElement(pPr, f'{{{_A_NS}}}buAutoNum'); buAutoNum.set('type', 'arabicPeriod')
        if num > 1:
            buAutoNum.set('startAt', str(num))
        r = _et.SubElement(p, f'{{{_A_NS}}}r')
        rPr = _et.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '2000'); rPr.set('dirty', '0')
        t_ = _et.SubElement(r, f'{{{_A_NS}}}t'); t_.text = text
        return p

    def _a_para(text):
        # Answer paragraph: dark green, bold, → prefix, indented, sz=1600
        p = _et.Element(f'{{{_A_NS}}}p')
        pPr = _et.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '457200')
        _et.SubElement(pPr, f'{{{_A_NS}}}buNone')
        r = _et.SubElement(p, f'{{{_A_NS}}}r')
        rPr = _et.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '1600'); rPr.set('b', '1'); rPr.set('dirty', '0')
        fill = _et.SubElement(rPr, f'{{{_A_NS}}}solidFill')
        clr = _et.SubElement(fill, f'{{{_A_NS}}}srgbClr'); clr.set('val', '1A5C2A')
        t_ = _et.SubElement(r, f'{{{_A_NS}}}t'); t_.text = '→ ' + text
        return p

    def _spacer_para():
        p = _et.Element(f'{{{_A_NS}}}p')
        endPr = _et.SubElement(p, f'{{{_A_NS}}}endParaRPr')
        endPr.set('lang', 'en-GB'); endPr.set('sz', '600'); endPr.set('dirty', '0')
        return p

    sp, rp = clone(work, quiz_template_pptx, 1, copy_hdphoto=True)
    title_text = lesson.get('quiz_title', 'Recap Quiz')
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
    Vocabulary slide matching the shared enquiry deck format:
    bold term (sz=1400) + indented dark-green definition (sz=1200, colour 1A5C2A).
    Term and definition reveal on separate clicks, spacer paragraphs between words.
    Up to 5 words from lesson['vocabulary'].
    """
    from lxml import etree as _et

    _A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    _P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'

    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, 'Key Vocabulary', REG.TITLE_FONT))
    save(t, sp)

    vocab = lesson.get('vocabulary', [])[:5]
    n = len(vocab)
    if n == 0:
        print('  [7] vocabulary (empty)')
        return sp

    # Build paragraphs matching the reference format exactly
    # Structure per word: term para, definition para, spacer (except after last word)
    paras_xml = []
    for i, item in enumerate(vocab):
        word = item.get('word', '')
        defn = item.get('definition', '')

        # Term paragraph: bold, sz=1400, black (no fill = inherits)
        term_p = _et.Element(f'{{{_A_NS}}}p')
        r = _et.SubElement(term_p, f'{{{_A_NS}}}r')
        rPr = _et.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '1400'); rPr.set('b', '1'); rPr.set('dirty', '0')
        _et.SubElement(r, f'{{{_A_NS}}}t').text = word
        paras_xml.append(term_p)

        # Definition paragraph: sz=1200, dark green 1A5C2A, indented
        def_p = _et.Element(f'{{{_A_NS}}}p')
        pPr = _et.SubElement(def_p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '457200')
        r2 = _et.SubElement(def_p, f'{{{_A_NS}}}r')
        rPr2 = _et.SubElement(r2, f'{{{_A_NS}}}rPr')
        rPr2.set('lang', 'en-GB'); rPr2.set('sz', '1200'); rPr2.set('dirty', '0')
        fill = _et.SubElement(rPr2, f'{{{_A_NS}}}solidFill')
        _et.SubElement(fill, f'{{{_A_NS}}}srgbClr').set('val', '1A5C2A')
        _et.SubElement(r2, f'{{{_A_NS}}}t').text = defn
        paras_xml.append(def_p)

        # Spacer paragraph between words (not after last)
        if i < n - 1:
            sp_p = _et.Element(f'{{{_A_NS}}}p')
            endPr = _et.SubElement(sp_p, f'{{{_A_NS}}}endParaRPr')
            endPr.set('lang', 'en-GB'); endPr.set('sz', '600'); endPr.set('dirty', '0')
            paras_xml.append(sp_p)

    # Content shape — same position as VocabContent in reference
    content_sid = 10
    content_xml = (
        f'<p:sp xmlns:p="{_P_NS}" xmlns:a="{_A_NS}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{content_sid}" name="VocabContent"/>'
        f'<p:cNvSpPr/><p:nvPr/>'
        f'</p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="246888" y="1826167"/><a:ext cx="11684402" cy="4900000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr wrap="square" anchor="t"/>'
        f'<a:lstStyle/>'
        f'</p:txBody>'
        f'</p:sp>'
    )
    t2, st2 = get_spTree(sp)
    content_el = xp(content_xml)
    st2.append(content_el)
    save(t2, sp)

    # Insert paragraphs into the txBody
    tree = xr(sp)
    vocab_sp = find_sp(tree, 'VocabContent')
    txBody = vocab_sp.find(f'{{{_P_NS}}}txBody')
    for p in paras_xml:
        txBody.append(p)
    xw(tree, sp)

    # Animate: term on one click, definition on next click
    # Para indices: term=i*3, def=i*3+1, spacer=i*3+2 (except last word has no spacer)
    # Step size: 3 for words 0..n-2, 2 for last word
    animated = []
    for i in range(n):
        step = 3 if i < n - 1 else 2
        base = i * 3
        animated.append(base)       # term
        animated.append(base + 1)   # definition

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
            f'<p:tgtEl><p:spTgt spid="{content_sid}"><p:txEl>'
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
        f'<p:bldLst><p:bldP spid="{content_sid}" grpId="0" build="p"/></p:bldLst>'
        f'</p:timing>'
    )

    tree = xr(sp)
    root = tree.getroot()
    existing = root.find(f'{{{_P_NS}}}timing')
    if existing is not None:
        root.remove(existing)
    root.append(_et.fromstring(timing_xml))
    xw(tree, sp)

    print(f'  [7] vocabulary ({n} words, animated)')
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
        # Larger image: starts further left (4600000) and is wider (7400000)
        # so diagram labels are readable at the back of the classroom.
        add_img(sp, rp, work, spec['image_path'], 4600000, 1400000, 7400000, 5200000, 3)
    sid = 10; groups = []
    n_bullets = max(len(spec['bullets']), 1)
    # Bullet column runs from y=1550000 to y=6700000 (5150000 EMU available).
    # Step is capped at 1540000 so ≤3 bullets keep the original generous spacing;
    # 4+ bullets divide the available height equally so nothing overflows the slide.
    _BULLET_TOP  = 1550000
    _BULLET_BOT  = 6700000
    _avail       = _BULLET_BOT - _BULLET_TOP
    step         = min(1540000, _avail // n_bullets)
    box_h        = step - 40000   # 40000 EMU gap between boxes
    for i, bullet in enumerate(spec['bullets']):
        by = _BULLET_TOP + i * step
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 180000, by, 4200000, box_h, sz=1800, color='1A3A5C', align='l'))
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

    build_building_blocks_atom(work, templates, enquiry, lesson, all_lessons)
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
