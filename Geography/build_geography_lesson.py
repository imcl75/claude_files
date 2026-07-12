#!/usr/bin/env python3
"""
build_geography_lesson.py — MTP-JSON-driven Geography enquiry lesson builder.

Architecture: clone-and-populate.
  • Standard slides: fresh_geo(layout_name) creates a slide referencing the
    correct layout, then _fill_ph() populates placeholders.  The layout
    supplies all visual design (background, decorations, typography).
  • Puzzle Pieces: clone_from_layout() copies the layout's shapes into the
    slide's spTree so groups can be hidden/modified directly.

Usage:
    python3 build_geography_lesson.py brazil_mtp.json \\
        --base-pptx /path/to/Geographer.pptx \\
        --out-dir ./Brazil_Lessons

    python3 build_geography_lesson.py brazil_mtp.json --lesson 1 \\
        --base-pptx /path/to/Geographer.pptx \\
        --out-pptx ./L1.pptx

Requires:
  lib_ooxml.py, geography_registry.py, lxml, Geographer.pptx
"""

import sys, os, json, argparse, glob, shutil, copy
from pathlib import Path

# ── Locate companion modules ──────────────────────────────────────────────────
_THIS = os.path.dirname(os.path.abspath(__file__))
for _p in [_THIS,
           os.path.join(_THIS, '..', 'EnquiryBuilder'),
           '/home/claude',
           '/tmp/EnquiryBuilder']:
    if _p not in sys.path and os.path.isdir(_p):
        sys.path.insert(0, _p)

from lib_ooxml import (
    P, A, R, PKG,
    unzip, rezip, clear_slides, build_layout_map,
    find_slide_by_anchor, clone,
    get_spTree, save,
    add_img, animate,
    xr, xw, xp, ex,
    SW, SH, next_sn,
    strip_orphaned_media,
)
import geography_registry as REG
from lxml import etree

# ── Sandbox path patch ────────────────────────────────────────────────────────
import lib_ooxml as _lo_mod
_lo_src_cache = {}

def _patched_src_dir(pptx, k=None):
    k = k or pptx
    if k not in _lo_src_cache:
        import tempfile
        base = os.environ.get('GEO_TMP', tempfile.gettempdir())
        dst = os.path.join(base, f'src_{os.getpid()}_{Path(pptx).stem}')
        _lo_mod.unzip(pptx, dst)
        _lo_src_cache[k] = dst
    return _lo_src_cache[k]

import zipfile as _zf
def _patched_rezip(src, dst):
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    with _zf.ZipFile(dst, 'w', _zf.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, src))
    shutil.rmtree(src, ignore_errors=True)

_lo_mod.src_dir = _patched_src_dir
_lo_mod.rezip   = _patched_rezip

# ── Relationship namespace shortcuts ─────────────────────────────────────────
R_EMBED = f'{{{R}}}embed'
R_LINK  = f'{{{R}}}link'


# ══════════════════════════════════════════════════════════════════════════════
#  Master-aware layout map
# ══════════════════════════════════════════════════════════════════════════════

_geo_layout_map = {}   # (master_idx, layout_name) → layout_filename


def build_geo_layout_map(work):
    """Build (master_idx, layout_name) → layout_filename for the template."""
    global _geo_layout_map
    _geo_layout_map = {}

    pres_rels = xr(f'{work}/ppt/_rels/presentation.xml.rels').getroot()
    master_rids = {}
    for rel in pres_rels:
        if 'slideMaster' in rel.get('Type', '') and 'slideLayout' not in rel.get('Target', ''):
            master_rids[rel.get('Id')] = os.path.basename(rel.get('Target', ''))

    pres_root = xr(f'{work}/ppt/presentation.xml').getroot()
    master_order = []
    lst = pres_root.find(f'.//{{{P}}}sldMasterIdLst')
    if lst is not None:
        for el in lst:
            rid = el.get(f'{{{R}}}id', '')
            if rid in master_rids:
                master_order.append(master_rids[rid])

    if not master_order:
        master_order = sorted(
            os.path.basename(f)
            for f in glob.glob(f'{work}/ppt/slideMasters/slideMaster*.xml')
        )

    for master_idx, master_file in enumerate(master_order):
        rels_path = f'{work}/ppt/slideMasters/_rels/{master_file}.rels'
        if not os.path.exists(rels_path):
            continue
        for rel in xr(rels_path).getroot():
            if 'slideLayout' not in rel.get('Type', ''):
                continue
            lf = os.path.basename(rel.get('Target', ''))
            lp = f'{work}/ppt/slideLayouts/{lf}'
            if not os.path.exists(lp):
                continue
            cSld = xr(lp).getroot().find(f'{{{P}}}cSld')
            name = cSld.get('name', '') if cSld is not None else ''
            if name:
                _geo_layout_map[(master_idx, name)] = lf


def _get_layout_file(layout_name, master_idx):
    """Return the layout filename for (master_idx, layout_name), with fallbacks."""
    # Direct lookup
    key = (master_idx, layout_name)
    if key in _geo_layout_map:
        return _geo_layout_map[key]

    # Try with 1_ prefix (for M3/M4)
    prefixed = REG.layout_name_for_master(layout_name, master_idx)
    key2 = (master_idx, prefixed)
    if key2 in _geo_layout_map:
        return _geo_layout_map[key2]

    # Try without 1_ prefix (in case caller passed prefixed name)
    unprefixed = layout_name.lstrip('1_')
    for mi in range(5):
        for name in (unprefixed, f'1_{unprefixed}'):
            k = (mi, name)
            if k in _geo_layout_map:
                print(f'  NOTE: layout "{layout_name}" M{master_idx} → using M{mi} "{name}"',
                      file=sys.stderr)
                return _geo_layout_map[k]

    # Absolute last resort
    for (mi, ln), lf in sorted(_geo_layout_map.items()):
        if mi == master_idx:
            print(f'  NOTE: layout "{layout_name}" not found — falling back to "{ln}"',
                  file=sys.stderr)
            return lf

    raise KeyError(
        f"Layout '{layout_name}' (master {master_idx}) not found. "
        f"Available: {sorted(_geo_layout_map.keys())}"
    )


def _reg_slide(work, sn):
    """Register slide{sn}.xml in ppt/presentation.xml and its .rels."""
    # Presentation rels
    pr_rels_path = f'{work}/ppt/_rels/presentation.xml.rels'
    pr_rels = xr(pr_rels_path)
    root = pr_rels.getroot()

    # Find highest existing rId
    max_id = 0
    for rel in root:
        rid = rel.get('Id', '')
        if rid.startswith('rId'):
            try:
                max_id = max(max_id, int(rid[3:]))
            except ValueError:
                pass
    new_rid = f'rId{max_id + 1}'

    rel_el = etree.SubElement(root, 'Relationship')
    rel_el.set('Id', new_rid)
    rel_el.set('Type', f'{R}/slide')
    rel_el.set('Target', f'slides/slide{sn}.xml')
    xw(pr_rels, pr_rels_path)

    # Presentation sldIdLst
    pres_path = f'{work}/ppt/presentation.xml'
    pres = xr(pres_path)
    pres_root = pres.getroot()
    sld_id_lst = pres_root.find(f'.//{{{P}}}sldIdLst')
    if sld_id_lst is not None:
        max_cid = 255
        for el in sld_id_lst:
            try:
                max_cid = max(max_cid, int(el.get('id', 255)))
            except ValueError:
                pass
        sld_el = etree.SubElement(sld_id_lst, f'{{{P}}}sldId')
        sld_el.set('id', str(max_cid + 1))
        sld_el.set(f'{{{R}}}id', new_rid)
    xw(pres, pres_path)

    # [Content_Types].xml
    ct_path = f'{work}/[Content_Types].xml'
    ct = xr(ct_path)
    ct_root = ct.getroot()
    CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
    override = etree.SubElement(ct_root, f'{{{CT_NS}}}Override')
    override.set('PartName', f'/ppt/slides/slide{sn}.xml')
    override.set('ContentType',
                 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
    xw(ct, ct_path)


def fresh_geo(work, layout_name, master_idx):
    """
    Create a blank slide referencing the correct layout for this master.
    The layout provides all visual design; callers populate placeholders.
    Returns (slide_path, rels_path).
    """
    lf = _get_layout_file(layout_name, master_idx)
    sn = _next_slide_num(work)

    slide_xml = (
        f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
        f"<p:sld xmlns:p='{P}' xmlns:a='{A}' xmlns:r='{R}'>"
        f"<p:cSld><p:spTree>"
        f"<p:nvGrpSpPr><p:cNvPr id='1' name=''/>"
        f"<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
        f"<p:grpSpPr><a:xfrm><a:off x='0' y='0'/><a:ext cx='0' cy='0'/>"
        f"<a:chOff x='0' y='0'/><a:chExt cx='0' cy='0'/></a:xfrm></p:grpSpPr>"
        f"</p:spTree></p:cSld>"
        f"<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>"
        f"</p:sld>"
    )
    rels_xml = (
        f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
        f"<Relationships xmlns='{PKG}'>"
        f"<Relationship Id='rId1' Type='{R}/slideLayout' "
        f"Target='../slideLayouts/{lf}'/>"
        f"</Relationships>"
    )

    sp = f'{work}/ppt/slides/slide{sn}.xml'
    rp = f'{work}/ppt/slides/_rels/slide{sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels', exist_ok=True)
    with open(sp, 'w', encoding='utf-8') as f: f.write(slide_xml)
    with open(rp, 'w', encoding='utf-8') as f: f.write(rels_xml)
    _reg_slide(work, sn)
    return sp, rp


def _next_slide_num(work):
    """Return the next available slide number."""
    existing = glob.glob(f'{work}/ppt/slides/slide*.xml')
    nums = []
    for p in existing:
        m = __import__('re').search(r'slide(\d+)\.xml$', p)
        if m:
            nums.append(int(m.group(1)))
    return max(nums, default=0) + 1


# ══════════════════════════════════════════════════════════════════════════════
#  clone_from_layout — copies layout shapes into the slide for direct editing
# ══════════════════════════════════════════════════════════════════════════════

def clone_from_layout(work, layout_name, master_idx):
    """
    Create a slide whose spTree is pre-populated with the layout's shapes.
    This allows the caller to hide groups, update TextBox content, and
    swap image rIds — operations not possible on inherited layout shapes.

    Returns (slide_path, rels_path, rId_map) where rId_map maps
    layout rId strings → new slide rId strings.
    """
    lf = _get_layout_file(layout_name, master_idx)
    layout_path      = f'{work}/ppt/slideLayouts/{lf}'
    layout_rels_path = f'{work}/ppt/slideLayouts/_rels/{lf}.rels'

    # 1. Build rId mapping: layout rId → slide rId
    rId_map = {}
    slide_rels_entries = [
        f'<Relationship Id="rId1" Type="{R}/slideLayout"'
        f' Target="../slideLayouts/{lf}"/>'
    ]
    counter = 2

    if os.path.exists(layout_rels_path):
        for rel in xr(layout_rels_path).getroot():
            typ = rel.get('Type', '')
            tgt = rel.get('Target', '')
            lid = rel.get('Id', '')
            if 'slideMaster' in tgt or 'slideLayout' in tgt:
                continue
            new_rid = f'rId{counter}'
            counter += 1
            rId_map[lid] = new_rid
            slide_rels_entries.append(
                f'<Relationship Id="{new_rid}" Type="{typ}" Target="{tgt}"/>'
            )

    # 2. Deep-copy the layout's spTree and remap rIds
    layout_root = xr(layout_path).getroot()
    layout_spTree = layout_root.find(f'.//{{{P}}}spTree')

    if layout_spTree is not None:
        spTree_el = copy.deepcopy(layout_spTree)
        for el in spTree_el.iter():
            if R_EMBED in el.attrib and el.attrib[R_EMBED] in rId_map:
                el.attrib[R_EMBED] = rId_map[el.attrib[R_EMBED]]
            if R_LINK in el.attrib and el.attrib[R_LINK] in rId_map:
                el.attrib[R_LINK] = rId_map[el.attrib[R_LINK]]
    else:
        spTree_el = etree.fromstring(
            f'<p:spTree xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
            f'<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            f'<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
            f'</a:xfrm></p:grpSpPr></p:spTree>'
        )

    # 3. Build slide XML around the copied spTree
    sn = _next_slide_num(work)
    sp_path = f'{work}/ppt/slides/slide{sn}.xml'
    rp_path = f'{work}/ppt/slides/_rels/slide{sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels', exist_ok=True)

    rels_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{PKG}">'
        + ''.join(slide_rels_entries) +
        '</Relationships>'
    )
    with open(rp_path, 'w', encoding='utf-8') as f:
        f.write(rels_xml)

    slide_root = etree.Element(f'{{{P}}}sld',
                               nsmap={'p': P, 'a': A, 'r': R})
    cSld = etree.SubElement(slide_root, f'{{{P}}}cSld')
    cSld.append(spTree_el)
    clrOvr = etree.SubElement(slide_root, f'{{{P}}}clrMapOvr')
    etree.SubElement(clrOvr, f'{{{A}}}masterClrMapping')

    etree.ElementTree(slide_root).write(
        sp_path, xml_declaration=True, encoding='UTF-8', standalone=True
    )

    _reg_slide(work, sn)
    return sp_path, rp_path, rId_map


# ══════════════════════════════════════════════════════════════════════════════
#  Placeholder helpers
# ══════════════════════════════════════════════════════════════════════════════

def _fill_ph(sp_path, ph_idx, text, sz=None, bold=False, color=None):
    """
    Append a placeholder-filling <p:sp> to the slide's spTree.
    The shape inherits all formatting from the layout's matching placeholder.
    Newlines in text become separate paragraphs.
    """
    # Run properties
    rpr_parts = ['lang="en-GB" dirty="0"']
    if sz:
        rpr_parts.append(f'sz="{sz}"')
    if bold:
        rpr_parts.append('b="1"')
    rpr_attrs = ' '.join(rpr_parts)

    fill_xml = ''
    if color:
        fill_xml = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'

    # Paragraph(s)
    lines = str(text).split('\n') if '\n' in str(text) else [str(text)]
    paras_xml = ''
    for line in lines:
        if line.strip():
            paras_xml += (
                f'<a:p><a:r>'
                f'<a:rPr {rpr_attrs}>{fill_xml}</a:rPr>'
                f'<a:t>{ex(line)}</a:t>'
                f'</a:r></a:p>'
            )
        else:
            paras_xml += f'<a:p><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'
    if not paras_xml:
        paras_xml = f'<a:p><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'

    # ph element — title uses type="title", body uses idx only
    if ph_idx == 0:
        ph_xml = '<p:ph type="title"/>'
    else:
        ph_xml = f'<p:ph idx="{ph_idx}"/>'

    sp_xml = (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{ph_idx + 100}" name="ph{ph_idx}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr>{ph_xml}</p:nvPr>'
        f'</p:nvSpPr>'
        f'<p:spPr/>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/>'
        f'{paras_xml}'
        f'</p:txBody>'
        f'</p:sp>'
    )
    sp_el = etree.fromstring(sp_xml)
    t, st = get_spTree(sp_path)
    st.append(sp_el)
    save(t, sp_path)


def _set_group_textbox_text(group_el, text):
    """Replace text in the first TextBox (<p:sp>) found in a puzzle piece group."""
    for sp_el in group_el.findall(f'{{{P}}}sp'):
        txBody = sp_el.find(f'{{{P}}}txBody')
        if txBody is None:
            continue
        paras = txBody.findall(f'{{{A}}}p')
        if not paras:
            continue
        first_para = paras[0]
        runs = first_para.findall(f'{{{A}}}r')
        if runs:
            t_el = runs[0].find(f'{{{A}}}t')
            if t_el is not None:
                t_el.text = text
            for r in runs[1:]:
                first_para.remove(r)
        for p in paras[1:]:
            txBody.remove(p)
        return


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide builders
# ══════════════════════════════════════════════════════════════════════════════

def build_key_question(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 1: Our Key Question is
    Layout provides: cloud callout, children image, 'Being a Geographer' footer.
    Slide populates: PH idx=10 with the key question text.
    Optional: full-bleed background image (from lesson['images']).
    """
    sp, rp = fresh_geo(work, 'Our Key Question is', master_idx)

    # Background image — if the MTP provides one for this lesson
    images = lesson.get('images', [])
    bg_img = next(
        (img for img in images if img.get('use') == 'key_question_bg'), None
    )
    if bg_img and bg_img.get('local_path') and os.path.exists(bg_img['local_path']):
        add_img(sp, rp, work, bg_img['local_path'], 0, 0, SW, SH, 10)

    _fill_ph(sp, 10, enquiry.get('key_question', ''))
    print('  [1] key_question')
    return sp


def build_concepts_skills(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 2: Concepts & Skills
    The layout contains the full design (concept wheel, skill wheel).
    No editable content is added to the slide — everything comes from the layout.
    """
    sp, rp = fresh_geo(work, 'Concepts & Skills', master_idx)
    print('  [2] concepts_skills')
    return sp


def build_progression(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 3: Progression
    No Progression layout exists in the template.  Falls back to displaying
    the geo-progression.png static asset full-bleed on a Revisit slide.
    """
    sp, rp = fresh_geo(work, 'Revisit', master_idx)

    prog_path = REG.STATIC_ASSETS.get('progression', '')
    if prog_path and os.path.exists(prog_path):
        add_img(sp, rp, work, prog_path, 0, 0, SW, SH, 10)
    else:
        _fill_ph(sp, 10, 'Geographer Progression')
        print(f'  NOTE: progression image not found at {prog_path}', file=sys.stderr)

    print('  [3] progression')
    return sp


def build_puzzle_pieces(work, base_pptx, lesson, enquiry, all_lessons, master_idx):
    """
    Slide 4: Puzzle Pieces
    Clones the Puzzle Pieces layout into the slide so groups can be
    hidden (sp:hidden) and their TextBox/EMF updated directly.

    Piece positions 1..N are shown; positions N+1..15 are hidden.
    Each visible piece swaps its EMF rId to the lesson's skill_focus colour.
    """
    lesson_num = lesson['lesson_number']
    sp, rp, rId_map = clone_from_layout(work, 'Puzzle Pieces', master_idx)

    # Build skill → slide rId lookup (from layout rIds → new slide rIds)
    skill_to_slide_rid = {
        skill: rId_map.get(layout_rid)
        for skill, layout_rid in REG.SKILL_EMF_LAYOUT_RID.items()
        if rId_map.get(layout_rid)
    }

    tree = xr(sp)
    root = tree.getroot()
    spTree = root.find(f'.//{{{P}}}spTree')

    for pos_idx, group_name in enumerate(REG.PUZZLE_PIECE_GROUPS):
        position = pos_idx + 1  # 1-based

        # Locate the group element by name
        group_el = None
        for child in spTree:
            if child.tag.split('}')[-1] != 'grpSp':
                continue
            cNvPr = child.find(f'{{{P}}}nvGrpSpPr/{{{P}}}cNvPr')
            if cNvPr is not None and cNvPr.get('name') == group_name:
                group_el = child
                break

        if group_el is None:
            print(f'  WARNING: puzzle piece group "{group_name}" not found',
                  file=sys.stderr)
            continue

        if position > lesson_num:
            # Hide this piece — set hidden="1" on the group's cNvPr
            cNvPr = group_el.find(f'{{{P}}}nvGrpSpPr/{{{P}}}cNvPr')
            if cNvPr is not None:
                cNvPr.set('hidden', '1')
        else:
            # Visible piece — update EMF colour and TextBox text
            lsn = all_lessons[pos_idx] if pos_idx < len(all_lessons) else None
            if lsn is not None:
                skill     = lsn.get('skill_focus', 'questioning_predicting')
                piece_txt = (lsn.get('puzzle_piece_text') or
                             lsn.get('building_block_text') or
                             str(lsn['lesson_number']))

                # Swap the first <p:pic> (EMF) rId to the correct skill colour
                target_rid = skill_to_slide_rid.get(skill)
                if target_rid:
                    for sub in group_el:
                        if sub.tag.split('}')[-1] == 'pic':
                            blip = sub.find(f'.//{{{A}}}blip')
                            if blip is not None:
                                blip.set(R_EMBED, target_rid)
                            break

                # Update TextBox text
                _set_group_textbox_text(group_el, piece_txt)

    xw(tree, sp)
    print(f'  [4] puzzle_pieces — {lesson_num}/{len(REG.PUZZLE_PIECE_GROUPS)} pieces')
    return sp


def build_lo(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 5: Learning Objective (KS2 What, Why, How)
    Layout provides: three cloud callouts, rounded-rectangle panels,
    'I am learning to…', 'This is so…', 'I will show this by…' labels.
    Slide populates: PH idx=0 (date), 10 (WALT), 13 (TIB), 14 (ISB).
    """
    lo_layout = REG.lo_layout_name(master_idx)
    sp, rp = fresh_geo(work, lo_layout, master_idx)

    ll    = lesson.get('learning_label', {})
    date  = lesson.get('date', lesson.get('day', ''))
    walt  = ll.get('lf', lesson.get('what', ''))
    tib   = lesson.get('why', ll.get('sc1', ''))
    isb   = lesson.get('success', ll.get('sc2', ''))

    _fill_ph(sp, 0,  date)
    _fill_ph(sp, 10, walt)
    _fill_ph(sp, 13, tib)
    _fill_ph(sp, 14, isb)

    print('  [5] lo')
    return sp


def build_kwl(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 6 (Lesson 1 only): KWL — What do we know? Want to know?
    No dedicated KWL layout exists; uses Hook as the base (title + content).
    """
    sp, rp = fresh_geo(work, 'Hook', master_idx)

    _fill_ph(sp, 0, 'What do I know? What do I want to find out?')
    _fill_ph(
        sp, 1,
        'What do I already know about this topic?\n'
        '\n'
        'What would I like to find out?'
    )

    print('  [6] kwl')
    return sp


def build_recap_quiz(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 6 (Lessons 2+): Recap Quiz — Q clicks in, A clicks in.
    No dedicated Quiz layout; uses Hook as the base.
    Animation: each question paragraph then each answer paragraph fires on click.
    """
    sp, rp = fresh_geo(work, 'Hook', master_idx)

    _fill_ph(sp, 0, 'Recap Quiz')

    qna = lesson.get('quiz') or []
    if not qna:
        print('  [6] recap_quiz (empty)')
        return sp

    # Build a single content shape with Q/A paragraphs and paragraph animation.
    # Each Q paragraph and each A paragraph fires on a separate click.
    content_id = 200   # fixed shape ID for the quiz content box

    def _q_para(text, num):
        p = etree.Element(f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('marL', '457200'); pPr.set('indent', '-457200')
        buFont = etree.SubElement(pPr, f'{{{A}}}buFont')
        buFont.set('typeface', '+mj-lt')
        buNum = etree.SubElement(pPr, f'{{{A}}}buAutoNum')
        buNum.set('type', 'arabicPeriod')
        if num > 1:
            buNum.set('startAt', str(num))
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '2000'); rPr.set('dirty', '0')
        t_ = etree.SubElement(r, f'{{{A}}}t'); t_.text = text
        return p

    def _a_para(text):
        p = etree.Element(f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('marL', '457200')
        etree.SubElement(pPr, f'{{{A}}}buNone')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', '1800')
        rPr.set('b', '1'); rPr.set('dirty', '0')
        fill = etree.SubElement(rPr, f'{{{A}}}solidFill')
        clr  = etree.SubElement(fill, f'{{{A}}}srgbClr')
        clr.set('val', '1A5C2A')
        t_ = etree.SubElement(r, f'{{{A}}}t'); t_.text = '→ ' + text
        return p

    sp_el = etree.fromstring(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{content_id}" name="QuizContent"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr><p:ph idx="1"/></p:nvPr>'
        f'</p:nvSpPr>'
        f'<p:spPr/>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/></p:txBody>'
        f'</p:sp>'
    )
    txBody = sp_el.find(f'.//{{{P}}}txBody')

    animated_para_idxs = []
    para_global = 0

    for i, item in enumerate(qna[:5]):
        txBody.append(_q_para(item.get('question', ''), i + 1))
        animated_para_idxs.append(para_global); para_global += 1
        txBody.append(_a_para(item.get('answer', '')))
        animated_para_idxs.append(para_global); para_global += 1
        if i < len(qna) - 1:
            spacer = etree.Element(f'{{{A}}}p')
            etree.SubElement(spacer, f'{{{A}}}endParaRPr').set('lang', 'en-GB')
            txBody.append(spacer)
            para_global += 1

    t, st = get_spTree(sp)
    st.append(sp_el)
    save(t, sp)

    # Paragraph-level click animation
    nid_counter = [1]
    def nid(): v = nid_counter[0]; nid_counter[0] += 1; return str(v)

    root_id = nid(); seq_id = nid()
    blocks  = []
    for pi in animated_para_idxs:
        b, inn, clk, bhv = nid(), nid(), nid(), nid()
        blocks.append(
            f'<p:par xmlns:p="{P}"><p:cTn id="{b}" fill="hold">'
            f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{inn}" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{clk}" presetID="1" presetClass="entr" '
            f'presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst><p:set><p:cBhvr>'
            f'<p:cTn id="{bhv}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{content_id}"><p:txEl>'
            f'<p:pRg st="{pi}" end="{pi}"/></p:txEl></p:spTgt></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
        )

    timing_xml = (
        f'<p:timing xmlns:p="{P}" xmlns:a="{A}">'
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
        f'<p:bldLst>'
        f'<p:bldP spid="{content_id}" grpId="0" build="p"/>'
        f'</p:bldLst></p:timing>'
    )

    tree = xr(sp)
    sld_root = tree.getroot()
    existing = sld_root.find(f'{{{P}}}timing')
    if existing is not None:
        sld_root.remove(existing)
    sld_root.append(etree.fromstring(timing_xml))
    xw(tree, sp)

    print(f'  [6] recap_quiz — {len(qna)} question(s)')
    return sp


def build_key_vocabulary(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 7: Key Vocabulary
    Layout provides: 'Vocabulary' header, decorative group.
    Slide populates: PH idx=10 with word / definition pairs.
    """
    sp, rp = fresh_geo(work, 'Vocabulary', master_idx)

    vocab = lesson.get('vocabulary', [])[:5]
    if vocab:
        lines = []
        for item in vocab:
            lines.append(f"{item.get('word', '')}: {item.get('definition', '')}")
        _fill_ph(sp, 10, '\n'.join(lines))

    print('  [7] vocabulary')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Variable slide builders
# ══════════════════════════════════════════════════════════════════════════════

def _build_content_slide(work, slide_type, slide_spec, lesson, master_idx, slide_num):
    """
    Generic builder for I Do / We Do / You Do / You Do Trio.
    Layout provides: header badge, decorative images.
    Slide populates: PH idx=0 (title) and PH idx=1 (content body).
    """
    layout_name = REG.teaching_layout(slide_type, master_idx)
    sp, rp = fresh_geo(work, layout_name, master_idx)

    title   = slide_spec.get('title', '')
    content = slide_spec.get('content', '')

    _fill_ph(sp, 0, title)
    if content:
        _fill_ph(sp, 1, content)

    print(f'  [{slide_num}] {slide_type}: {title}')
    return sp


def build_learning_review(work, slide_spec, lesson, enquiry, master_idx, slide_num):
    """
    Learning Review — always the final slide.
    Layout provides: 'Learning Review' header, decorative scoring elements.
    Slide populates: PH idx=10, 11, 12 with the 3 reflection questions.
    """
    sp, rp = fresh_geo(work, 'Learning Review Editable', master_idx)

    questions = (slide_spec.get('questions') or
                 lesson.get('learning_review', []))

    for i, q in enumerate(questions[:3]):
        _fill_ph(sp, 10 + i, q)

    print(f'  [{slide_num}] learning_review')
    return sp


# ══════════════════════════════════════════════════════════════════════════════
#  Main orchestrator
# ══════════════════════════════════════════════════════════════════════════════

VARIABLE_DISPATCH = {
    'i_do':            lambda work, spec, lsn, enq, mi, n:
                           _build_content_slide(work, 'i_do',       spec, lsn, mi, n),
    'we_do':           lambda work, spec, lsn, enq, mi, n:
                           _build_content_slide(work, 'we_do',      spec, lsn, mi, n),
    'you_do_trio':     lambda work, spec, lsn, enq, mi, n:
                           _build_content_slide(work, 'you_do_trio',spec, lsn, mi, n),
    'you_do':          lambda work, spec, lsn, enq, mi, n:
                           _build_content_slide(work, 'you_do',     spec, lsn, mi, n),
    'learning_review': lambda work, spec, lsn, enq, mi, n:
                           build_learning_review(work, spec, lsn, enq, mi, n),
}


def build_one_lesson(mtp, lesson_num, base_pptx, out_pptx):
    """Build one lesson PPTX from the MTP dict."""
    lesson_data = next(
        (l for l in mtp['lessons'] if l['lesson_number'] == lesson_num), None
    )
    if lesson_data is None:
        raise ValueError(f'Lesson {lesson_num} not found in MTP')

    sc = lesson_data.get(
        'substantive_concept',
        mtp.get('default_substantive_concept', REG.DEFAULT_SUBSTANTIVE_CONCEPT)
    )
    master_idx  = REG.MASTER_INDICES.get(sc, 0)
    all_lessons = mtp['lessons']

    import tempfile
    tmp_base = os.environ.get('GEO_TMP', tempfile.gettempdir())
    work = os.path.join(tmp_base, f'geo_{os.getpid()}_L{lesson_num}')

    title = (lesson_data.get('lesson_title') or
             lesson_data.get('building_block_text') or
             lesson_data.get('puzzle_piece_text') or
             f'Lesson {lesson_num}')
    print(f'\nLesson {lesson_num}: {title}  [{sc} / master {master_idx}]')

    unzip(base_pptx, work)
    clear_slides(work)
    build_layout_map(work)
    build_geo_layout_map(work)

    # ── Fixed slides ──────────────────────────────────────────────────────────
    build_key_question (work, base_pptx, lesson_data, mtp, master_idx)
    build_concepts_skills(work, base_pptx, lesson_data, mtp, master_idx)
    build_progression  (work, base_pptx, lesson_data, mtp, master_idx)
    build_puzzle_pieces(work, base_pptx, lesson_data, mtp, all_lessons, master_idx)
    build_lo           (work, base_pptx, lesson_data, mtp, master_idx)

    if lesson_num == 1:
        build_kwl        (work, base_pptx, lesson_data, mtp, master_idx)
    else:
        build_recap_quiz (work, base_pptx, lesson_data, mtp, master_idx)

    build_key_vocabulary(work, base_pptx, lesson_data, mtp, master_idx)

    # ── Variable slides ───────────────────────────────────────────────────────
    for i, slide_spec in enumerate(lesson_data.get('slides', []), start=8):
        stype = slide_spec.get('type', '')
        if stype not in VARIABLE_DISPATCH:
            print(f'  [{i}] WARNING: unknown slide type "{stype}", skipping',
                  file=sys.stderr)
            continue
        VARIABLE_DISPATCH[stype](work, slide_spec, lesson_data, mtp, master_idx, i)

    # ── Finalise ──────────────────────────────────────────────────────────────
    removed = strip_orphaned_media(work)
    if removed:
        print(f'  stripped {len(removed)} orphaned media file(s)')

    os.makedirs(os.path.dirname(out_pptx) or '.', exist_ok=True)
    _patched_rezip(work, out_pptx)
    print(f'  → {out_pptx} ({os.path.getsize(out_pptx):,} bytes)')
    return out_pptx


def build_all_lessons(mtp_path, base_pptx, out_dir):
    with open(mtp_path) as f:
        mtp = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    built = []
    for lesson in mtp['lessons']:
        n     = lesson['lesson_number']
        title = (lesson.get('lesson_title') or
                 lesson.get('puzzle_piece_text') or
                 lesson.get('building_block_text') or
                 f'Lesson_{n}')
        label = title.replace(' ', '_').replace('?', '').replace('/', '-')[:40]
        out_path = os.path.join(out_dir, f'L{n:02d}_{label}.pptx')
        build_one_lesson(mtp, n, base_pptx, out_path)
        built.append(out_path)

    print(f'\nDone — {len(built)} PPTX(s) written to {out_dir}')
    return built


def main():
    parser = argparse.ArgumentParser(description='Geography lesson PPTX builder')
    parser.add_argument('mtp_json',    help='Path to the MTP JSON file')
    parser.add_argument('--base-pptx', required=True,
                        help='Path to Geographer.pptx template')
    parser.add_argument('--out-dir',   default='./Geography_Lessons',
                        help='Output directory (all lessons)')
    parser.add_argument('--lesson',    type=int, default=None,
                        help='Build only this lesson number')
    parser.add_argument('--out-pptx',  default=None,
                        help='Output path (only with --lesson)')
    args = parser.parse_args()

    for path, label in [(args.mtp_json, 'MTP JSON'), (args.base_pptx, 'base PPTX')]:
        if not os.path.exists(path):
            sys.exit(f'{label} not found: {path}')

    if args.lesson:
        out = (args.out_pptx or
               os.path.join(args.out_dir, f'L{args.lesson:02d}.pptx'))
        with open(args.mtp_json) as f:
            mtp = json.load(f)
        build_one_lesson(mtp, args.lesson, args.base_pptx, out)
        # Run fix_pptx_ooxml if available
        fix_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'Shared', 'fix_pptx_ooxml.py'
        )
        if os.path.exists(fix_script):
            import subprocess
            subprocess.run([sys.executable, fix_script, out], check=False)
    else:
        build_all_lessons(args.mtp_json, args.base_pptx, args.out_dir)


if __name__ == '__main__':
    main()
