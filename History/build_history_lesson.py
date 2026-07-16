#!/usr/bin/env python3
"""
build_history_lesson.py - MTP-JSON-driven History enquiry lesson builder.

Produces one PPTX per lesson from an Ancient Egypt (or any history) MTP JSON.

Usage:
    # Build all lessons:
    python3 build_history_lesson.py egypt_mtp.json --base-pptx /path/to/science-example.pptx --out-dir ./Egypt_Lessons

    # Build one lesson:
    python3 build_history_lesson.py egypt_mtp.json --lesson 1 --base-pptx /path/to/science-example.pptx --out-pptx ./L1.pptx

Requires:
  - lib_ooxml.py      (in same directory or on sys.path)
  - history_registry.py (in same directory or on sys.path)
  - Pillow            (pip install pillow --break-system-packages)
  - lxml              (pip install lxml --break-system-packages)
  - A base PPTX that contains the named slide layouts (science-example.pptx works)
  - Image assets at the paths defined in history_registry.ASSETS_ROOT

Design decisions (locked in transfer file, 2026-07-12):
  - Fixed slide sequence per lesson: KQ / Concepts&Skills / ConceptCard /
    BuildingBlocks / LO / KWL-or-Quiz / KeyVocab / [variable slides]
  - KWL only in Lesson 1; Recap Quiz in all other lessons
  - Concept colour (bg + border) from the enquiry-level 'concept' field
  - Building Blocks: 14 bricks in 4/3/4/3 rows; all bricks up to lesson N animate in
  - Vocabulary: word clicks in → definition clicks in → next word…
  - Quiz: Q clicks in → A clicks in → Q2…
"""

import sys, os, json, argparse, subprocess
from pathlib import Path

# ── Locate companion modules ─────────────────────────────────────────────────
_THIS = os.path.dirname(os.path.abspath(__file__))
for _p in [_THIS,
           os.path.join(_THIS, 'EnquiryBuilder'),
           '/home/claude',
           '/tmp/EnquiryBuilder']:
    if _p not in sys.path and os.path.isdir(_p):
        sys.path.insert(0, _p)

from lib_ooxml import (
    P, A, R, unzip, rezip, clear_slides, build_layout_map, src_dir,
    find_slide_by_anchor, clone, fresh, get_spTree, save,
    title_sp, tbox, add_img, animate, xr, xw, xp, ex,
    SW, SH, next_sn, next_mn,
    strip_orphaned_media, get_shape_id_by_name,
)
import history_registry as REG
from lxml import etree

# ── Sandbox path patch (mirrors science builder) ──────────────────────────────
import lib_ooxml as _lo_mod
_lo_src_cache = {}

def _patched_src_dir(pptx, k=None):
    k = k or pptx
    if k not in _lo_src_cache:
        import tempfile
        base = os.environ.get('HISTORY_TMP', tempfile.gettempdir())
        dst = os.path.join(base, f'src_{os.getpid()}_{Path(pptx).stem}')
        _lo_mod.unzip(pptx, dst)
        _lo_src_cache[k] = dst
    return _lo_src_cache[k]

import zipfile as _zf, shutil as _sh
def _patched_rezip(src, dst):
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    with _zf.ZipFile(dst, 'w', _zf.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, src))
    _sh.rmtree(src, ignore_errors=True)

_lo_mod.src_dir = _patched_src_dir
_lo_mod.rezip   = _patched_rezip
src_dir = _patched_src_dir
rezip   = _patched_rezip

# ── EMU constants ─────────────────────────────────────────────────────────────
BORDER_W  = 76200    # ~6pt stroke for slide border
MARGIN_X  = 228600   # 18pt left/right margin


# ═══════════════════════════════════════════════════════════════════════════════
#  Low-level drawing helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _bg_fill_rect(sid, bg_hex):
    """Full-slide filled rectangle (background)."""
    return xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="BG"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SW}" cy="{SH}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{bg_hex}"/></a:solidFill>'
        f'<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )


def _border_rect(sid, border_hex):
    """Full-slide border rectangle (no fill, coloured stroke)."""
    return xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="Border"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SW}" cy="{SH}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'<a:ln w="{BORDER_W}"><a:solidFill><a:srgbClr val="{border_hex}"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )


def _apply_concept_bg(sp, bg_hex, border_hex):
    """Insert BG fill + border into the slide's spTree, before any other shapes."""
    t, st = get_spTree(sp)
    # The first child of spTree is always nvGrpSpPr, second is grpSpPr
    # Insert BG immediately after grpSpPr (index 2)
    grp_idx = 1
    for i, child in enumerate(st):
        if child.tag.endswith('}grpSpPr'):
            grp_idx = i
            break
    st.insert(grp_idx + 1, _bg_fill_rect(990, bg_hex))
    # Border goes last (drawn on top of everything)
    # We'll append it at the very end after all content is added
    save(t, sp)


def _append_border(sp, border_hex):
    """Append the border rectangle as the topmost shape (drawn last = on top)."""
    t, st = get_spTree(sp)
    st.append(_border_rect(991, border_hex))
    save(t, sp)


def _styled_tbox(sid, text, x, y, cx, cy, sz=1800, bold=False,
                 color='1A3A5C', align='l', font=None, name=None,
                 underline=False):
    """Text box with optional font override and underline."""
    b  = ' b="1"' if bold else ''
    u  = ' u="sng"' if underline else ''
    nm = name or f'TextBox {sid}'
    fn = (f'<a:latin typeface="{font}" panose="02000000000000000000" '
          f'pitchFamily="2" charset="77"/>'
          if font else '')
    return xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="{ex(nm)}"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" anchor="t"/>'
        f'<a:lstStyle/><a:p><a:pPr algn="{align}"/>'
        f'<a:r><a:rPr lang="en-GB" sz="{sz}"{b}{u} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{fn}</a:rPr>'
        f'<a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>'
    )


def _phase_badge(sid, phase_num, x, y):
    """Small coloured phase badge (e.g. 'Phase 1: Discover')."""
    colours = {1: ('FFE6CC', '7D4000'), 2: ('DAE8FC', '0D3D91'), 3: ('D5E8D4', '1A5C1A')}
    bg, fg = colours.get(phase_num, ('EEEEEE', '333333'))
    label = f'Phase {phase_num}: {REG.PHASE_NAMES.get(phase_num, "")}'
    return xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="PhaseBadge"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="1800000" cy="320000"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{bg}"/></a:solidFill>'
        f'<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="1200" b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{fg}"/></a:solidFill></a:rPr>'
        f'<a:t>{ex(label)}</a:t></a:r></a:p></p:txBody></p:sp>'
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixed slide builders
# ═══════════════════════════════════════════════════════════════════════════════

def build_key_question(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 1: Key Question

    Layout:
      - Concept colour BG + border
      - Cloud callout shape (upper centre) containing the enquiry KQ (underlined)
        and challenge text below it inside the cloud
      - 4-children PNG centred on slide
      - 21C-skills PNG top right
      - hist-icon PNG + 'Being an Historian' text — bottom centre
      - Day label — bottom left, large bold
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    # Day label — bottom left
    st.append(_styled_tbox(
        sid, lesson['day_label'],
        MARGIN_X, SH - 700000, 2000000, 650000,
        sz=3200, bold=True, color='1A3A5C',
        font=REG.TITLE_FONT, name='DayLabel'
    ))
    sid += 1

    # 'Being an Historian' label — bottom centre
    st.append(_styled_tbox(
        sid, 'Being an Historian',
        SW // 2 - 1200000, SH - 680000, 2400000, 550000,
        sz=2000, bold=True, color='1A3A5C',
        font=REG.TITLE_FONT, name='BeingAnHistorianLabel', align='ctr'
    ))
    sid += 1

    # Cloud callout with KQ + challenge (upper area of slide)
    cloud_x, cloud_y = 380000, 180000
    cloud_w, cloud_h = SW - 760000, 2500000
    kq_text = enquiry['key_question']
    challenge_text = enquiry.get('challenge', '')
    full_cloud_text = kq_text + ('\n\n' + challenge_text if challenge_text else '')

    st.append(xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="CloudKQ"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{cloud_x}" y="{cloud_y}"/>'
        f'<a:ext cx="{cloud_w}" cy="{cloud_h}"/></a:xfrm>'
        f'<a:prstGeom prst="cloud"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'<a:ln w="38100"><a:solidFill><a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody>'
        f'<a:bodyPr anchor="ctr"/>'
        f'<a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="2200" b="1" u="sng" dirty="0">'
        f'<a:solidFill><a:srgbClr val="1A3A5C"/></a:solidFill>'
        f'<a:latin typeface="{REG.TITLE_FONT}" panose="02000000000000000000" pitchFamily="2" charset="77"/>'
        f'</a:rPr><a:t>{ex(kq_text)}</a:t></a:r></a:p>'
        + (f'<a:p><a:pPr algn="ctr"/>'
           f'<a:r><a:rPr lang="en-GB" sz="1600" dirty="0">'
           f'<a:solidFill><a:srgbClr val="1A3A5C"/></a:solidFill></a:rPr>'
           f'<a:t>{ex(challenge_text)}</a:t></a:r></a:p>'
           if challenge_text else '') +
        f'</p:txBody></p:sp>'
    ))
    sid += 1
    save(t, sp)

    # Images — only add if files exist (fail gracefully with warning)
    def _try_add(path, x, y, mw, mh):
        nonlocal sid
        if os.path.exists(path):
            add_img(sp, rp, work, path, x, y, mw, mh, sid)
            sid += 1
        else:
            print(f'  WARNING: asset not found, skipping: {path}', file=sys.stderr)

    # 4-children PNG — centred horizontally, lower half of slide
    _try_add(REG.STATIC_ASSETS['children_kq'],
             SW // 2 - 3000000, 2700000, 6000000, 3600000)

    # 21C-skills PNG — top right
    _try_add(REG.STATIC_ASSETS['skills_21c'],
             SW - 2200000, 100000, 2000000, 1400000)

    # hist-icon — bottom centre (left of the label)
    _try_add(REG.STATIC_ASSETS['hist_icon'],
             SW // 2 - 1800000, SH - 700000, 500000, 500000)

    _append_border(sp, bd)
    return sp


def build_concepts_skills(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 2: Concepts & Skills

    Two images side by side:
      Left:  hist-sub-concepts.png  (concepts wheel)
      Right: Hist-skill.png         (skills wheel)
    Each clicks in separately.
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    half_w = SW // 2 - MARGIN_X - 100000
    img_y  = 600000
    img_h  = SH - 800000

    ids_left, ids_right = [], []

    left_path  = REG.STATIC_ASSETS['sub_concepts']
    right_path = REG.STATIC_ASSETS['skill']

    sid = 10
    if os.path.exists(left_path):
        add_img(sp, rp, work, left_path, MARGIN_X, img_y, half_w, img_h, sid)
        ids_left.append(sid); sid += 1
    else:
        print(f'  WARNING: {left_path} not found', file=sys.stderr)

    if os.path.exists(right_path):
        add_img(sp, rp, work, right_path, SW // 2 + 100000, img_y, half_w, img_h, sid)
        ids_right.append(sid); sid += 1
    else:
        print(f'  WARNING: {right_path} not found', file=sys.stderr)

    if ids_left or ids_right:
        steps = [s for s in [ids_left, ids_right] if s]
        animate(sp, steps)

    _append_border(sp, bd)
    return sp


def build_concept_card(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 3: Concept Card

    Stacks 6 images (Y1 bottom → Y6 top), each appearing on its own click.
    Images path: ASSETS_ROOT/[ConceptFolder]/[prefix]-Y1.png … -Y6.png
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    concept = enquiry.get('concept', 'civilisation').lower()
    if concept not in REG.CONCEPT_CARD_SPECS:
        print(f'  WARNING: unknown concept "{concept}", skipping concept card images', file=sys.stderr)
        _append_border(sp, bd)
        return sp

    folder, prefix = REG.CONCEPT_CARD_SPECS[concept]
    row_h = (SH - 400000) // 6
    img_h = row_h - 40000
    img_w = SW - 2 * MARGIN_X

    steps = []
    sid = 10
    for year in range(1, 7):
        img_path = os.path.join(REG.ASSETS_ROOT, folder, f'{prefix}-Y{year}.png')
        y_pos = SH - 200000 - year * row_h  # Y1 at bottom, Y6 at top
        if os.path.exists(img_path):
            add_img(sp, rp, work, img_path, MARGIN_X, y_pos, img_w, img_h, sid)
            steps.append([sid])
            sid += 1
        else:
            print(f'  WARNING: concept card image not found: {img_path}', file=sys.stderr)

    if steps:
        animate(sp, steps)

    _append_border(sp, bd)
    return sp


def build_building_blocks(work, rp_dummy, lesson, enquiry, all_lessons, colours):
    """
    Slide 4: Building Blocks (brick wall)

    14 bricks in 4/3/4/3 layout (bottom to top).
    In lesson N, bricks 1..N animate in, one at a time.
    Each brick = coloured PNG + text label overlay.

    Brick PNG selected by skill_focus of that lesson.
    Text = building_block_text of that lesson.
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    # Title
    st.append(_styled_tbox(
        sid, 'Our Enquiry…', MARGIN_X, 120000, SW - 2 * MARGIN_X, 480000,
        sz=2800, bold=True, color='1A3A5C', font=REG.TITLE_FONT, align='ctr', name='BBTitle'
    ))
    sid += 1
    save(t, sp)

    # Compute brick positions
    rows      = REG.BRICK_WALL_ROWS   # [4, 3, 4, 3]
    total_bricks = sum(rows)
    wall_top  = 650000
    wall_bot  = SH - 200000
    wall_h    = wall_bot - wall_top
    n_rows    = len(rows)
    row_h     = wall_h // n_rows
    brick_h   = row_h - 30000
    gap_x     = 30000

    lesson_num = lesson['lesson_number']

    # Map brick index (0-based) → lesson in order
    # Bricks are ordered bottom-row-left-to-right, then next row up, etc.
    brick_to_lesson = {}
    brick_idx = 0
    for row_i, n_bricks in enumerate(rows):   # row 0 = bottom
        for col_i in range(n_bricks):
            brick_to_lesson[brick_idx] = all_lessons[brick_idx] if brick_idx < len(all_lessons) else None
            brick_idx += 1

    steps = []
    brick_idx = 0
    for row_i, n_bricks in enumerate(rows):
        row_y  = wall_bot - (row_i + 1) * row_h + 15000
        brick_w = (SW - 2 * MARGIN_X - (n_bricks - 1) * gap_x) // n_bricks
        # Stagger even rows slightly for brick-wall effect
        x_start = MARGIN_X + (brick_w // 4 if row_i % 2 == 1 else 0)

        for col_i in range(n_bricks):
            lsn = brick_to_lesson.get(brick_idx)
            if lsn is None:
                brick_idx += 1
                continue

            bx = x_start + col_i * (brick_w + gap_x)
            skill  = lsn.get('skill_focus', 'questioning')
            bb_txt = lsn.get('building_block_text', '')
            png    = REG.BUILDING_BLOCK_PNGS.get(skill, REG.BUILDING_BLOCK_PNGS['questioning'])

            group_ids = []

            # Brick image
            if os.path.exists(png):
                add_img(sp, rp, work, png, bx, row_y, brick_w, brick_h, sid)
                group_ids.append(sid); sid += 1
            else:
                # Fallback: plain coloured rectangle
                skill_colours = {
                    'questioning':     'FFD966',
                    'chronology':      'F4B183',
                    'sources':         'F4AFBA',
                    'interpretations': '9DC3E6',
                }
                fill = skill_colours.get(skill, 'DDDDDD')
                t2, st2 = get_spTree(sp)
                st2.append(xp(
                    f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
                    f'<p:nvSpPr><p:cNvPr id="{sid}" name="Brick{brick_idx}"/>'
                    f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                    f'<p:spPr><a:xfrm><a:off x="{bx}" y="{row_y}"/>'
                    f'<a:ext cx="{brick_w}" cy="{brick_h}"/></a:xfrm>'
                    f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                    f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                    f'<a:ln w="19050"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>'
                    f'</p:spPr>'
                    f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
                ))
                save(t2, sp)
                group_ids.append(sid); sid += 1

            # Text overlay on the brick
            t2, st2 = get_spTree(sp)
            st2.append(_styled_tbox(
                sid, bb_txt,
                bx + 20000, row_y + 20000,
                brick_w - 40000, brick_h - 40000,
                sz=max(900, 1400 - len(bb_txt) * 8),
                bold=True, color='1A3A5C', align='ctr',
                name=f'BrickText{brick_idx}'
            ))
            save(t2, sp)
            group_ids.append(sid); sid += 1

            # Lesson number badge (small, top-left of brick)
            t2, st2 = get_spTree(sp)
            st2.append(_styled_tbox(
                sid, str(lsn['lesson_number']),
                bx + 8000, row_y + 8000, 200000, 200000,
                sz=900, bold=True, color='1A3A5C',
                name=f'BrickNum{brick_idx}'
            ))
            save(t2, sp)
            group_ids.append(sid); sid += 1

            # Only animate bricks up to the current lesson
            if lsn['lesson_number'] <= lesson_num:
                steps.append(group_ids)

            brick_idx += 1

    if steps:
        animate(sp, steps)

    _append_border(sp, bd)
    return sp


def build_lo(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 5: Learning Objective (What / Why / How)

    Three panels left/centre/right.
    Enquiry question as title.
    Panels: 'I am learning… [what]' / 'This is so… [why]' / 'I will be successful by… [success]'
    Each panel clicks in.
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    # Title: enquiry key question
    st.append(_styled_tbox(
        sid, enquiry['key_question'],
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 560000,
        sz=2200, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='LOTitle'
    ))
    sid += 1
    save(t, sp)

    panel_top  = 700000
    panel_h    = SH - panel_top - 180000
    gap        = 80000
    panel_w    = (SW - 2 * MARGIN_X - 2 * gap) // 3

    panels = [
        ('I am learning…',           lesson.get('what', ''),    '1F3864', 'F2F9FF'),
        ('This is so…',              lesson.get('why', ''),     '1A5C2A', 'F0FFF4'),
        ('I will be successful by…', lesson.get('success', ''), '7D2200', 'FFF9F0'),
    ]

    steps = []
    for i, (header, body, text_col, fill_col) in enumerate(panels):
        px = MARGIN_X + i * (panel_w + gap)

        # Panel background
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="Panel{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{px}" y="{panel_top}"/>'
            f'<a:ext cx="{panel_w}" cy="{panel_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill_col}"/></a:solidFill>'
            f'<a:ln w="38100"><a:solidFill><a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
            f'</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        bg_id = sid; sid += 1

        # Header text
        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, header,
            px + 40000, panel_top + 40000, panel_w - 80000, 500000,
            sz=1800, bold=True, color=text_col, align='ctr',
            font=REG.TITLE_FONT, name=f'Panel{i}Header'
        ))
        save(t2, sp)
        header_id = sid; sid += 1

        # Body text
        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, body,
            px + 40000, panel_top + 580000, panel_w - 80000, panel_h - 640000,
            sz=1600, color='222222', align='ctr',
            name=f'Panel{i}Body'
        ))
        save(t2, sp)
        body_id = sid; sid += 1

        steps.append([bg_id, header_id, body_id])

    animate(sp, steps)
    _append_border(sp, bd)
    return sp


def build_kwl(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 6 (Lesson 1 only): KWL Grid

    'We Do' layout.
    Title: "What knowledge am I bringing to this enquiry? What would I like to find out?"
    2-column table: 'Prior Knowledge and Skill' | 'I am curious about…'
    (Teacher fills in live on the interactive whiteboard.)
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    st.append(_styled_tbox(
        sid,
        'What knowledge am I bringing to this enquiry?\nWhat would I like to find out?',
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 680000,
        sz=2400, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='KWLTitle'
    ))
    sid += 1

    # 'We Do' badge
    st.append(_styled_tbox(
        sid, 'We Do', SW - MARGIN_X - 1000000, 80000, 900000, 400000,
        sz=1800, bold=True, color='FFFFFF', align='ctr', name='WeDoLabel'
    ))
    sid += 1
    save(t, sp)

    # Table (drawn as rectangles + text)
    tbl_x, tbl_y = MARGIN_X, 820000
    tbl_w = SW - 2 * MARGIN_X
    tbl_h = SH - tbl_y - 200000
    col_w = tbl_w // 2
    row_h = tbl_h // 4  # header + 3 data rows

    headers = ['Prior Knowledge and Skill', 'I am curious about…']
    for ci, hdr in enumerate(headers):
        cx = tbl_x + ci * col_w
        # Header cell BG
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="TblH{ci}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{cx}" y="{tbl_y}"/>'
            f'<a:ext cx="{col_w}" cy="{row_h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="1F3864"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp); sid += 1
        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, hdr, cx + 30000, tbl_y + 20000, col_w - 60000, row_h - 40000,
            sz=1800, bold=True, color='FFFFFF', align='ctr', name=f'TblH{ci}Txt'
        ))
        save(t2, sp); sid += 1

    # Data rows (empty, teacher fills in)
    for ri in range(3):
        ry = tbl_y + (ri + 1) * row_h
        for ci in range(2):
            cx = tbl_x + ci * col_w
            t2, st2 = get_spTree(sp)
            st2.append(xp(
                f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
                f'<p:nvSpPr><p:cNvPr id="{sid}" name="TblR{ri}C{ci}"/>'
                f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{cx}" y="{ry}"/>'
                f'<a:ext cx="{col_w}" cy="{row_h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{"F2F2F2" if ri % 2 == 0 else "FFFFFF"}"/></a:solidFill>'
                f'<a:ln w="19050"><a:solidFill><a:srgbClr val="AAAAAA"/></a:solidFill></a:ln>'
                f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
            ))
            save(t2, sp); sid += 1

    _append_border(sp, bd)
    return sp


def build_recap_quiz(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 6 (Lessons 2+): Recap Quiz

    Up to 5 Q+A pairs.
    Animation: Q1 clicks in → A1 clicks in → Q2 → A2 → …
    Uses paragraph-level animation on a single text box.
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    st.append(_styled_tbox(
        sid, 'Recap Quiz',
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 520000,
        sz=3200, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='QuizTitle'
    ))
    sid += 1
    save(t, sp)

    qna = lesson.get('quiz', [])[:5]
    if not qna:
        _append_border(sp, bd)
        return sp

    # Build paragraphs: Q numbered → A in green bold → spacer
    _A_NS = A
    _P_NS = P

    def _q_para(text, num):
        p = etree.Element(f'{{{_A_NS}}}p')
        pPr = etree.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '514350'); pPr.set('indent', '-514350')
        buFont = etree.SubElement(pPr, f'{{{_A_NS}}}buFont'); buFont.set('typeface', '+mj-lt')
        buAutoNum = etree.SubElement(pPr, f'{{{_A_NS}}}buAutoNum')
        buAutoNum.set('type', 'arabicPeriod')
        if num > 1: buAutoNum.set('startAt', str(num))
        r = etree.SubElement(p, f'{{{_A_NS}}}r')
        rPr = etree.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '2000'); rPr.set('dirty', '0')
        t_ = etree.SubElement(r, f'{{{_A_NS}}}t'); t_.text = text
        return p

    def _a_para(text):
        p = etree.Element(f'{{{_A_NS}}}p')
        pPr = etree.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '514350'); pPr.set('indent', '0')
        etree.SubElement(pPr, f'{{{_A_NS}}}buNone')
        r = etree.SubElement(p, f'{{{_A_NS}}}r')
        rPr = etree.SubElement(r, f'{{{_A_NS}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '1900')
        rPr.set('b', '1'); rPr.set('dirty', '0')
        fill = etree.SubElement(rPr, f'{{{_A_NS}}}solidFill')
        clr  = etree.SubElement(fill, f'{{{_A_NS}}}srgbClr'); clr.set('val', '1A5C2A')
        t_ = etree.SubElement(r, f'{{{_A_NS}}}t'); t_.text = '→ ' + text
        return p

    # Content placeholder for Q+A
    content_sp_xml = (
        f'<p:sp xmlns:p="{_P_NS}" xmlns:a="{_A_NS}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="QuizContent"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="680000"/>'
        f'<a:ext cx="{SW - 2 * MARGIN_X}" cy="{SH - 900000}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" anchor="t"/>'
        f'<a:lstStyle/></p:txBody></p:sp>'
    )
    content_el = etree.fromstring(content_sp_xml)
    txBody = content_el.find(f'.//{{{_P_NS}}}txBody')

    for i, item in enumerate(qna):
        txBody.append(_q_para(item['question'], i + 1))
        txBody.append(_a_para(item['answer']))
        if i < len(qna) - 1:
            spacer = etree.Element(f'{{{_A_NS}}}p')
            endPr  = etree.SubElement(spacer, f'{{{_A_NS}}}endParaRPr')
            endPr.set('lang', 'en-GB'); endPr.set('sz', '600'); endPr.set('dirty', '0')
            txBody.append(spacer)

    content_sp_id = sid
    t2, st2 = get_spTree(sp)
    st2.append(content_el)
    save(t2, sp)
    sid += 1

    # Para-level animation: Q(0)→A(1)→Q(3)→A(4)→… (spacers at 2,5,8,…)
    animated_para_indices = []
    for i in range(len(qna)):
        animated_para_indices.append(i * 3)      # Q
        animated_para_indices.append(i * 3 + 1)  # A

    # Build paragraph-level timing XML (same pattern as science builder's quiz)
    id_n = [1]
    def nid(): v = id_n[0]; id_n[0] += 1; return str(v)
    root_id = nid(); seq_id = nid()
    blocks = []
    for para_idx in animated_para_indices:
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
            f'<p:cTn id="{behav}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{content_sp_id}"><p:txEl>'
            f'<p:pRg st="{para_idx}" end="{para_idx}"/></p:txEl></p:spTgt></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
        )

    timing_xml = (
        f'<p:timing xmlns:p="{_P_NS}" xmlns:a="{_A_NS}">'
        f'<p:tnLst><p:par><p:cTn id="{root_id}" dur="indefinite" restart="never" nodeType="tmRoot">'
        f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="{seq_id}" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst><p:bldP spid="{content_sp_id}" grpId="0" build="p"/></p:bldLst></p:timing>'
    )

    tree = xr(sp); root = tree.getroot()
    existing = root.find(f'{{{_P_NS}}}timing')
    if existing is not None: root.remove(existing)
    root.append(etree.fromstring(timing_xml))
    xw(tree, sp)

    _append_border(sp, bd)
    return sp


def build_key_vocabulary(work, rp_dummy, lesson, enquiry, colours):
    """
    Slide 7: Key Vocabulary

    Up to 5 word/definition pairs.
    Animation: Word 1 clicks in → Definition 1 clicks in → Word 2 → …
    Each pair in a visually distinct card.
    """
    sp, rp = fresh(work, 'Blank')
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    st.append(_styled_tbox(
        sid, 'Key Vocabulary',
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 520000,
        sz=3200, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='VocabTitle'
    ))
    sid += 1
    save(t, sp)

    vocab = lesson.get('vocabulary', [])[:5]
    n = len(vocab)
    if n == 0:
        _append_border(sp, bd)
        return sp

    card_top = 680000
    card_gap = 50000
    card_h   = (SH - card_top - 200000 - (n - 1) * card_gap) // n
    card_w   = SW - 2 * MARGIN_X
    word_w   = int(card_w * 0.28)
    def_w    = card_w - word_w - 20000

    steps = []
    for i, item in enumerate(vocab):
        cy = card_top + i * (card_h + card_gap)

        # Word card (coloured left panel)
        t2, st2 = get_spTree(sp)
        word_colours = ['DAE3F3', 'FFE6CC', 'D5E8D4', 'F8CECC', 'E1D5E7']
        word_fill = word_colours[i % len(word_colours)]
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="WordCard{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="{cy}"/>'
            f'<a:ext cx="{word_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{word_fill}"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        bg_id = sid; sid += 1

        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, item['word'],
            MARGIN_X + 20000, cy + 20000, word_w - 40000, card_h - 40000,
            sz=max(1400, 2000 - len(item['word']) * 20),
            bold=True, color='1A3A5C', align='ctr',
            font=REG.TITLE_FONT, name=f'Word{i}Text'
        ))
        save(t2, sp)
        word_id = sid; sid += 1

        steps.append([bg_id, word_id])

        # Definition card (white right panel) — clicks in separately
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="DefCard{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{MARGIN_X + word_w + 20000}" y="{cy}"/>'
            f'<a:ext cx="{def_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        def_bg_id = sid; sid += 1

        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, item['definition'],
            MARGIN_X + word_w + 40000, cy + 20000, def_w - 40000, card_h - 40000,
            sz=1600, color='222222', align='l',
            name=f'Def{i}Text'
        ))
        save(t2, sp)
        def_id = sid; sid += 1

        steps.append([def_bg_id, def_id])

    animate(sp, steps)
    _append_border(sp, bd)
    return sp


# ═══════════════════════════════════════════════════════════════════════════════
#  Variable slide builders
# ═══════════════════════════════════════════════════════════════════════════════

def _build_content_slide(work, layout_name, slide_spec, lesson, colours, badge_label):
    """
    Generic builder for I Do / We Do / You Do / You Do Trio slides.

    Title from slide_spec['title'].
    Content from slide_spec['content'] — split by '. ' into bullets and animated in.
    Concept colour BG + border.
    """
    sp, rp = fresh(work, layout_name)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    # Slide type badge
    badge_colours = {
        'I Do':         ('1F3864', 'FFFFFF'),
        'We Do':        ('1A5C2A', 'FFFFFF'),
        'You Do':       ('7D2200', 'FFFFFF'),
        'You Do (Trio)':('4B0082', 'FFFFFF'),
    }
    bfill, btext = badge_colours.get(badge_label, ('333333', 'FFFFFF'))
    st.append(xp(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="TypeBadge"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{SW - MARGIN_X - 1600000}" y="80000"/>'
        f'<a:ext cx="1500000" cy="380000"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{bfill}"/></a:solidFill>'
        f'<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="1600" b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{btext}"/></a:solidFill></a:rPr>'
        f'<a:t>{ex(badge_label)}</a:t></a:r></a:p></p:txBody></p:sp>'
    ))
    sid += 1

    # Title
    st.append(_styled_tbox(
        sid, slide_spec.get('title', ''),
        MARGIN_X, 80000, SW - 2 * MARGIN_X - 1700000, 520000,
        sz=2800, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='l', name='SlideTitle'
    ))
    sid += 1
    save(t, sp)

    # Content — split into sentences and animate each
    content = slide_spec.get('content', '')
    # Split on '. ' but keep sentence-ending punctuation
    import re
    sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', content) if s.strip()]
    if not sentences:
        sentences = [content] if content else []

    groups = []
    for i, sentence in enumerate(sentences):
        by = 680000 + i * 1100000
        if by + 900000 > SH - 150000:
            # Remaining sentences in one block if we run out of vertical space
            remainder = ' '.join(sentences[i:])
            t2, st2 = get_spTree(sp)
            st2.append(_styled_tbox(
                sid, remainder,
                MARGIN_X, by, SW - 2 * MARGIN_X, SH - by - 150000,
                sz=1800, color='1A3A5C', align='l', name=f'Content{i}'
            ))
            save(t2, sp)
            groups.append([sid]); sid += 1
            break
        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, sentence,
            MARGIN_X, by, SW - 2 * MARGIN_X, 1000000,
            sz=1900, color='1A3A5C', align='l', name=f'Content{i}'
        ))
        save(t2, sp)
        groups.append([sid]); sid += 1

    if groups:
        animate(sp, groups)

    _append_border(sp, bd)
    return sp


def build_i_do(work, slide_spec, lesson, enquiry, colours):
    return _build_content_slide(work, 'I do', slide_spec, lesson, colours, 'I Do')

def build_we_do(work, slide_spec, lesson, enquiry, colours):
    return _build_content_slide(work, 'We do', slide_spec, lesson, colours, 'We Do')

def build_you_do(work, slide_spec, lesson, enquiry, colours):
    return _build_content_slide(work, 'You do Ind', slide_spec, lesson, colours, 'You Do')

def build_you_do_trio(work, slide_spec, lesson, enquiry, colours):
    return _build_content_slide(work, 'You Do Trio', slide_spec, lesson, colours, 'You Do (Trio)')


# ═══════════════════════════════════════════════════════════════════════════════
#  Main orchestrator
# ═══════════════════════════════════════════════════════════════════════════════



def build_concept_cartoon(work, slide_spec, lesson_data, mtp, colours):
    """
    Variable slide: Concept Cartoon.

    Clones the concept cartoon slide from Being_a_Scientist_slide_deck.pptx.
    Requires:
      slide_spec['title']              — optional override for the title box
      slide_spec['learners']           — list of 3 dicts with 'statement' key
      slide_spec['image_path']         — path to the central image PNG (required)
      mtp['concept_cartoon_pptx']      — path to Being_a_Scientist_slide_deck.pptx
                                         OR standard fallback paths are tried

    Raises RuntimeError if the PPTX cannot be found or the central image is missing.
    """
    import os as _os

    # Locate the template PPTX
    cc_pptx = mtp.get('concept_cartoon_pptx')
    if cc_pptx and not _os.path.exists(cc_pptx):
        cc_pptx = None
    if not cc_pptx:
        _this = _os.path.dirname(_os.path.abspath(__file__))
        candidates = [
            _os.path.join(_this, '..', 'EnquiryBuilder', 'Being_a_Scientist_slide_deck.pptx'),
            _os.path.join(_this, 'Being_a_Scientist_slide_deck.pptx'),
            '/tmp/t6w7/Being_a_Scientist_slide_deck.pptx',
        ]
        cc_pptx = next((p for p in candidates if _os.path.exists(p)), None)
    if not cc_pptx:
        raise RuntimeError(
            "concept_cartoon: Being_a_Scientist_slide_deck.pptx not found. "
            "Set mtp['concept_cartoon_pptx'] to its path."
        )

    src_dir(cc_pptx)
    sn = find_slide_by_anchor(cc_pptx, REG.CONCEPT_CARTOON_ANCHOR, REG.CONCEPT_CARTOON_HINT)
    sp, rp = clone(work, cc_pptx, sn, copy_hdphoto=True)

    # Title
    tree = xr(sp)
    title_s = find_sp(tree, REG.CONCEPT_CARTOON_TITLE_SHAPE_NAME)
    if title_s is not None and slide_spec.get('title'):
        set_text(title_s, slide_spec['title'])

    # Learner speech bubbles
    learners = slide_spec.get('learners', [])
    if len(learners) != 3:
        raise ValueError("concept_cartoon requires exactly 3 learners (A/B/C)")
    for bubble_name, learner in zip(REG.CONCEPT_CARTOON_BUBBLE_NAMES, learners):
        s = find_sp(tree, bubble_name)
        if s is None:
            raise RuntimeError(f"concept_cartoon: bubble '{bubble_name}' not found — template drift")
        set_text(s, learner['statement'])
        force_shrink_to_fit(s)
    xw(tree, sp)

    for bubble_name in REG.CONCEPT_CARTOON_BUBBLE_NAMES:
        clamp_callout_tail(sp, bubble_name)

    # Central image
    img_path = slide_spec.get('image_path', '')
    if not img_path or not _os.path.exists(img_path):
        raise RuntimeError(
            f"concept_cartoon: image_path '{img_path}' is missing — "
            "refusing to deliver a slide with the default cat/light template image"
        )
    tree = xr(sp)
    pic_id = find_pic_id_by_name(tree, REG.CONCEPT_CARTOON_CENTRAL_IMAGE_SHAPE_NAME)
    if pic_id is None:
        raise RuntimeError("concept_cartoon: central image shape not found")
    replace_image(sp, rp, work, pic_id, img_path)

    # Animation
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

VARIABLE_DISPATCH = {
    'i_do':         build_i_do,
    'we_do':        build_we_do,
    'you_do':       build_you_do,
    'you_do_trio':  build_you_do_trio,
    'concept_cartoon': build_concept_cartoon,
}


def build_one_lesson(mtp, lesson_num, base_pptx, out_pptx):
    """Build a single lesson PPTX from the MTP dict."""
    lesson_data = next(
        (l for l in mtp['lessons'] if l['lesson_number'] == lesson_num), None
    )
    if lesson_data is None:
        raise ValueError(f'Lesson {lesson_num} not found in MTP')

    concept   = mtp.get('concept', 'civilisation').lower()
    colours   = REG.CONCEPT_COLOURS.get(concept, REG.CONCEPT_COLOURS['civilisation'])
    all_lessons = mtp['lessons']  # for building-blocks context

    import tempfile
    tmp_base = os.environ.get('HISTORY_TMP', tempfile.gettempdir())
    work = os.path.join(tmp_base, f'hist_{os.getpid()}_L{lesson_num}_work')

    print(f'\nLesson {lesson_num}: {lesson_data.get("building_block_text", "")}')

    unzip(base_pptx, work)
    clear_slides(work)
    build_layout_map(work)

    # Pre-extract all source templates
    src_dir(base_pptx)

    # ── Fixed slides ───────────────────────────────────────────────────────────
    print('  [1] key_question')
    build_key_question(work, None, lesson_data, mtp, colours)

    print('  [2] concepts_skills')
    build_concepts_skills(work, None, lesson_data, mtp, colours)

    print('  [3] concept_card')
    build_concept_card(work, None, lesson_data, mtp, colours)

    print('  [4] building_blocks')
    build_building_blocks(work, None, lesson_data, mtp, all_lessons, colours)

    print('  [5] lo')
    build_lo(work, None, lesson_data, mtp, colours)

    if lesson_num == 1:
        print('  [6] kwl')
        build_kwl(work, None, lesson_data, mtp, colours)
    else:
        print('  [6] recap_quiz')
        build_recap_quiz(work, None, lesson_data, mtp, colours)

    print('  [7] key_vocabulary')
    build_key_vocabulary(work, None, lesson_data, mtp, colours)

    # ── Variable slides ────────────────────────────────────────────────────────
    for i, slide_spec in enumerate(lesson_data.get('slides', []), start=8):
        stype = slide_spec['type']
        if stype not in VARIABLE_DISPATCH:
            print(f'  [{i}] WARNING: unknown slide type "{stype}", skipping', file=sys.stderr)
            continue
        print(f'  [{i}] {stype}: {slide_spec.get("title", "")}')
        VARIABLE_DISPATCH[stype](work, slide_spec, lesson_data, mtp, colours)

    # ── Finalise ───────────────────────────────────────────────────────────────
    removed = strip_orphaned_media(work)
    if removed:
        print(f'  stripped {len(removed)} orphaned media file(s)')

    os.makedirs(os.path.dirname(out_pptx) or '.', exist_ok=True)
    rezip(work, out_pptx)
    print(f'  → {out_pptx} ({os.path.getsize(out_pptx):,} bytes)')
    return out_pptx


def build_all_lessons(mtp_path, base_pptx, out_dir):
    """Build one PPTX per lesson, saving to out_dir."""
    with open(mtp_path) as f:
        mtp = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    topic = mtp.get('topic', 'History').replace(' ', '_')
    built = []

    for lesson in mtp['lessons']:
        n = lesson['lesson_number']
        label = lesson.get('building_block_text', f'Lesson {n}').replace(' ', '_').replace('?', '')
        fname = f'L{n:02d}_{label[:40]}.pptx'
        out_path = os.path.join(out_dir, fname)
        build_one_lesson(mtp, n, base_pptx, out_path)
        built.append(out_path)

    print(f'\nDone — {len(built)} PPTXs written to {out_dir}')
    return built


def main():
    parser = argparse.ArgumentParser(description='History lesson PPTX builder')
    parser.add_argument('mtp_json',   help='Path to the enquiry MTP JSON file')
    parser.add_argument('--base-pptx', required=True,
                        help='Base PPTX containing the slide layouts (science-example.pptx works)')
    parser.add_argument('--out-dir',  default='./History_Lessons',
                        help='Output directory for all lesson PPTXs (default: ./History_Lessons)')
    parser.add_argument('--lesson',   type=int, default=None,
                        help='Build only this lesson number (omit to build all)')
    parser.add_argument('--out-pptx', default=None,
                        help='Output path for single lesson (only with --lesson)')
    args = parser.parse_args()

    if not os.path.exists(args.mtp_json):
        sys.exit(f'MTP JSON not found: {args.mtp_json}')
    if not os.path.exists(args.base_pptx):
        sys.exit(f'Base PPTX not found: {args.base_pptx}')

    if args.lesson:
        out = args.out_pptx or os.path.join(args.out_dir, f'L{args.lesson:02d}.pptx')
        with open(args.mtp_json) as f:
            mtp = json.load(f)
        build_one_lesson(mtp, args.lesson, args.base_pptx, out)
    else:
        build_all_lessons(args.mtp_json, args.base_pptx, args.out_dir)


if __name__ == '__main__':
    main()
