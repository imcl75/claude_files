#!/usr/bin/env python3
"""
build_geography_lesson.py — MTP-JSON-driven Geography enquiry lesson builder.

Produces one PPTX per lesson from a geography MTP JSON file.

Usage:
    # Build all lessons:
    python3 build_geography_lesson.py brazil_mtp.json \
        --base-pptx /Users/innes/Downloads/Example\ Enquiry\ Slides/Geographer.pptx \
        --out-dir ./Brazil_Lessons

    # Build one lesson:
    python3 build_geography_lesson.py brazil_mtp.json --lesson 1 \
        --base-pptx /Users/innes/Downloads/Example\ Enquiry\ Slides/Geographer.pptx \
        --out-pptx ./L1.pptx

Requires:
  - lib_ooxml.py          (EnquiryBuilder/ in repo, or on sys.path)
  - geography_registry.py (same directory as this script)
  - Pillow                (pip install pillow --break-system-packages)
  - lxml                  (pip install lxml --break-system-packages)
  - Geographer.pptx       (template — lives at path passed to --base-pptx)

Key design decisions (locked in transfer file 2026-07-12):
  - Slide order every lesson:
      KQ Cover → Concepts & Skills → Progression → Puzzle Pieces →
      LO → KWL (L1) / Recap Quiz (L2+) → Key Vocabulary → [variable slides]
  - Colour / master changes PER LESSON (driven by substantive_concept),
    not per enquiry like history.
  - Puzzle pieces (not building blocks): EMF+ images, cumulative.
    Piece N is coloured by swapping r:embed rId to the EMF for that
    lesson's skill_focus.  Cannot be coloured via XML fill — must be rId swap.
  - Progression slide: cloned from Geographer.pptx (anchor search).
  - LO slides are inline (not delegated to lo-slides skill).
  - 15 puzzle pieces: 5 bottom row, 6 middle row, 4 top row.
"""

import sys, os, json, argparse, glob, re, shutil
from pathlib import Path

# ── Locate companion modules ─────────────────────────────────────────────────
_THIS = os.path.dirname(os.path.abspath(__file__))
for _p in [_THIS,
           os.path.join(_THIS, '..', 'EnquiryBuilder'),
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
import geography_registry as REG
from lxml import etree

# ── Sandbox path patch (same pattern as history builder) ─────────────────────
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
src_dir = _patched_src_dir
rezip   = _patched_rezip

# ── EMU constants ─────────────────────────────────────────────────────────────
BORDER_W  = 76200    # ~6pt stroke for slide border
MARGIN_X  = 228600   # 18pt left/right margin


# ══════════════════════════════════════════════════════════════════════════════
#  Master-aware layout map
# ══════════════════════════════════════════════════════════════════════════════

# Map: (master_idx, layout_name) → layout_filename  (e.g. slideLayout5.xml)
_geo_layout_map = {}

def build_geo_layout_map(work):
    """
    Build a two-key layout map: (master_idx, layout_name) → layout_filename.

    The Geographer.pptx has 5 slide masters.  Each master has its own set of
    layout files.  To pick the right layout we need to know which master a
    layout file belongs to, then look up by name within that master.

    master_idx is 0-based, ordered as PowerPoint lists them in
    ppt/presentation.xml (sldMasterIdLst order).
    """
    global _geo_layout_map
    _geo_layout_map = {}

    # 1. Determine master ordering from presentation.xml
    pres_rels = f'{work}/ppt/_rels/presentation.xml.rels'
    tree = xr(pres_rels); root = tree.getroot()
    # Collect slideMaster relationships in the order they appear
    master_rel_map = {}   # rId → slideMasterN.xml basename
    for rel in root:
        typ = rel.get('Type', '')
        tgt = rel.get('Target', '')
        if 'slideMaster' in typ and 'slideLayout' not in tgt:
            rid = rel.get('Id', '')
            master_rel_map[rid] = os.path.basename(tgt)

    pres_xml = f'{work}/ppt/presentation.xml'
    tree2 = xr(pres_xml); root2 = tree2.getroot()
    master_order = []   # ordered list of slideMasterN.xml basenames
    master_id_lst = root2.find(f'.//{{{P}}}sldMasterIdLst')
    if master_id_lst is not None:
        for el in master_id_lst:
            rid = el.get(f'{{{R}}}id', '')
            if rid in master_rel_map:
                master_order.append(master_rel_map[rid])

    # Fallback: sort numerically if presentation.xml lacks the list
    if not master_order:
        master_order = sorted(
            os.path.basename(f)
            for f in glob.glob(f'{work}/ppt/slideMasters/slideMaster*.xml')
        )

    # 2. For each master, find its layouts and read their names
    for master_idx, master_file in enumerate(master_order):
        master_rels = (f'{work}/ppt/slideMasters/_rels/'
                       f'{master_file}.rels')
        if not os.path.exists(master_rels):
            continue
        rel_tree = xr(master_rels); rel_root = rel_tree.getroot()
        for rel in rel_root:
            typ = rel.get('Type', '')
            tgt = rel.get('Target', '')
            if 'slideLayout' not in typ:
                continue
            layout_file = os.path.basename(tgt)
            layout_path = f'{work}/ppt/slideLayouts/{layout_file}'
            if not os.path.exists(layout_path):
                continue
            lt = xr(layout_path); lr = lt.getroot()
            cSld = lr.find(f'{{{P}}}cSld')
            name = cSld.get('name', '') if cSld is not None else ''
            if name:
                _geo_layout_map[(master_idx, name)] = layout_file


def _get_layout_file(layout_name, master_idx):
    """
    Look up the correct layout file for a (master_idx, layout_name) pair.

    Falls back to a flat name search if the master-indexed lookup fails,
    to handle templates where layout names are globally unique.
    """
    key = (master_idx, layout_name)
    if key in _geo_layout_map:
        return _geo_layout_map[key]
    # Try with the '1_' prefix convention for masters 3 and 4
    prefixed = REG.layout_name_for_master(layout_name, master_idx)
    key2 = (master_idx, prefixed)
    if key2 in _geo_layout_map:
        return _geo_layout_map[key2]
    # Flat fallback: any master
    for (mi, ln), lf in _geo_layout_map.items():
        if ln == layout_name or ln == prefixed:
            return lf
    # Last resort: delegate to lib_ooxml's flat map
    from lib_ooxml import _work_layouts
    if layout_name in _work_layouts:
        return _work_layouts[layout_name]
    if prefixed in _work_layouts:
        return _work_layouts[prefixed]
    raise KeyError(
        f"Layout '{layout_name}' (master_idx={master_idx}) not found. "
        f"Known geo keys: {sorted(_geo_layout_map.keys())}"
    )


def fresh_geo(work, layout_name, master_idx):
    """
    Create a fresh slide (like lib_ooxml.fresh) but pointing to the layout
    belonging to the specified master index.

    Returns (slide_path, rels_path) exactly like lib_ooxml.fresh().
    """
    from lib_ooxml import PKG, next_sn, reg_slide, xw as _xw
    lf = _get_layout_file(layout_name, master_idx)
    sn = next_sn(work)
    slide = (
        f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
        f"<p:sld xmlns:p=\"{P}\" xmlns:a=\"{A}\" xmlns:r=\"{R}\">\n"
        f"  <p:cSld><p:spTree>\n"
        f"    <p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n"
        f"    <p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
        f"<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>\n"
        f"  </p:spTree></p:cSld>\n"
        f"  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n"
        f"</p:sld>"
    )
    rels = (
        f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
        f"<Relationships xmlns=\"{PKG}\">\n"
        f"  <Relationship Id=\"rId1\" Type=\"{R}/slideLayout\" "
        f"Target=\"../slideLayouts/{lf}\"/>\n"
        f"</Relationships>"
    )
    sp = f'{work}/ppt/slides/slide{sn}.xml'
    rp = f'{work}/ppt/slides/_rels/slide{sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels', exist_ok=True)
    with open(sp, 'w', encoding='utf-8') as f: f.write(slide)
    with open(rp, 'w', encoding='utf-8') as f: f.write(rels)
    reg_slide(work, sn)
    return sp, rp


# ══════════════════════════════════════════════════════════════════════════════
#  Low-level drawing helpers  (identical pattern to history builder)
# ══════════════════════════════════════════════════════════════════════════════

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
        f'<a:ln w="{BORDER_W}"><a:solidFill>'
        f'<a:srgbClr val="{border_hex}"/></a:solidFill></a:ln>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
    )


def _apply_concept_bg(sp, bg_hex, border_hex):
    """Insert BG fill into the slide's spTree immediately after grpSpPr."""
    t, st = get_spTree(sp)
    grp_idx = 1
    for i, child in enumerate(st):
        if child.tag.endswith('}grpSpPr'):
            grp_idx = i
            break
    st.insert(grp_idx + 1, _bg_fill_rect(990, bg_hex))
    save(t, sp)


def _append_border(sp, border_hex):
    """Append the border rectangle as the topmost shape."""
    t, st = get_spTree(sp)
    st.append(_border_rect(991, border_hex))
    save(t, sp)


def _styled_tbox(sid, text, x, y, cx, cy, sz=1800, bold=False,
                 color='1A3A5C', align='l', font=None, name=None,
                 underline=False):
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
        f'<p:txBody><a:bodyPr wrap="square"><a:normAutofit/></a:bodyPr>'
        f'<a:lstStyle/><a:p><a:pPr algn="{align}"/>'
        f'<a:r><a:rPr lang="en-GB" sz="{sz}"{b}{u} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{fn}</a:rPr>'
        f'<a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  Puzzle Pieces helpers
# ══════════════════════════════════════════════════════════════════════════════

def _build_emf_rId_map(sd, slide_num):
    """
    Read the source slide's rels and return a mapping:
        src_emf_basename → src_rId
    for all EMF relationships on that slide.
    """
    rp = f'{sd}/ppt/slides/_rels/slide{slide_num}.xml.rels'
    tree = xr(rp); root = tree.getroot()
    result = {}
    for rel in root:
        tgt = rel.get('Target', '')
        rid = rel.get('Id', '')
        if tgt.endswith('.emf'):
            result[os.path.basename(tgt)] = rid
    return result


def _build_cloned_rId_map(work, cloned_sp_path):
    """
    After clone(), read the cloned slide's rels to build:
        old_emf_basename → new_rId_in_cloned_slide

    We infer the original basename from the new media filename because
    clone() renames media files to imageN.emf but we track the order in
    which the source rels were processed via the src_emf name in the
    PUZZLE_PIECE_EMF table.

    Returns: dict mapping src_emf_basename → rId_in_cloned_slide
    """
    rp = cloned_sp_path.replace('.xml', '.xml.rels').replace(
        '/slides/', '/slides/_rels/')
    # Already formed correctly if cloned_sp_path is in _rels; adjust if not
    sp_dir = os.path.dirname(cloned_sp_path)
    rels_path = os.path.join(sp_dir, '_rels',
                             os.path.basename(cloned_sp_path) + '.rels')
    if not os.path.exists(rels_path):
        rels_path = cloned_sp_path.replace('/slides/slide', '/slides/_rels/slide') + '.rels'

    tree = xr(rels_path); root = tree.getroot()
    # Build: rId → new_media_name  (in work dir)
    rid_to_media = {}
    for rel in root:
        tgt = rel.get('Target', '')
        rid = rel.get('Id', '')
        if '../media/' in tgt:
            rid_to_media[rid] = os.path.basename(tgt)
    return rid_to_media   # rId → new_media_name


def _swap_piece_emf(sp_path, rels_path, work, piece_shape_name,
                    skill_focus, src_pptx, src_slide_num):
    """
    Swap the EMF image of a puzzle piece shape to the correct skill_focus EMF.

    Strategy:
      1. Find the <p:pic> with cNvPr name == piece_shape_name in the cloned slide.
      2. Get its current r:embed rId.
      3. Remove that rId's relationship and add a new one pointing to the
         correct EMF file (copied from the source PPTX's media directory).
      4. Update r:embed on the blip.

    If the EMF file already exists in the work media dir under the correct
    src_emf name (from the original PPTX), reuse it instead of re-copying.
    """
    emf_info = REG.PUZZLE_PIECE_EMF.get(skill_focus)
    if emf_info is None:
        print(f'  WARNING: unknown skill_focus "{skill_focus}" for piece '
              f'"{piece_shape_name}" — leaving unchanged', file=sys.stderr)
        return

    # Locate the target EMF in the source PPTX's unpacked media
    sd = src_dir(src_pptx)
    src_emf_name = emf_info['src_emf']   # e.g. 'image12.emf'
    src_emf_path = os.path.join(sd, 'ppt', 'media', src_emf_name)
    if not os.path.exists(src_emf_path):
        # Fallback: look for the file by EMF extension
        candidates = glob.glob(os.path.join(sd, 'ppt', 'media', '*.emf'))
        if not candidates:
            print(f'  WARNING: EMF file {src_emf_name} not found in template — '
                  f'skill_focus "{skill_focus}" piece will not be swapped',
                  file=sys.stderr)
            return
        # Guess by position (the rId ordering is 6,8,10,12,15 → index 0,1,2,3,4)
        skill_order = list(REG.PUZZLE_PIECE_EMF.keys())
        idx = skill_order.index(skill_focus) if skill_focus in skill_order else 0
        src_emf_path = sorted(candidates)[min(idx, len(candidates)-1)]

    # Copy EMF into work media if not already there under a stable name
    media_dir = os.path.join(work, 'ppt', 'media')
    # Use a stable name keyed to the skill so we only copy once per lesson build
    stable_name = f'geo_piece_{skill_focus}.emf'
    dest_emf = os.path.join(media_dir, stable_name)
    if not os.path.exists(dest_emf):
        shutil.copy(src_emf_path, dest_emf)

    # Find the pic shape in the cloned slide
    tree = xr(sp_path); root = tree.getroot()
    target_pic = None
    for pic in root.iter(f'{{{P}}}pic'):
        cNvPr = pic.find(f'.//{{{P}}}cNvPr')
        if cNvPr is not None and cNvPr.get('name') == piece_shape_name:
            target_pic = pic
            break

    if target_pic is None:
        print(f'  WARNING: puzzle piece shape "{piece_shape_name}" not found '
              f'in cloned slide — skipping', file=sys.stderr)
        return

    blip = target_pic.find(f'.//{{{A}}}blip')
    if blip is None:
        print(f'  WARNING: no blip in piece shape "{piece_shape_name}"',
              file=sys.stderr)
        return
    old_rid = blip.get(f'{{{R}}}embed', '')

    # Add a new relationship for the skill EMF
    rt = xr(rels_path); rr = rt.getroot()
    ex_rids = {int(m.group(1)) for el in rr
               for m in [re.match(r'rId(\d+)', el.get('Id', ''))] if m}
    new_rn = max(ex_rids, default=0) + 1
    new_rid = f'rId{new_rn}'
    etree.SubElement(rr, 'Relationship', {
        'Id': new_rid,
        'Type': f'{R}/image',
        'Target': f'../media/{stable_name}',
    })
    xw(rt, rels_path)

    # Update the blip's r:embed
    blip.set(f'{{{R}}}embed', new_rid)
    xw(tree, sp_path)


# ══════════════════════════════════════════════════════════════════════════════
#  Fixed slide builders
# ══════════════════════════════════════════════════════════════════════════════

def build_key_question(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 1: Key Question

    Layout:
      - Concept colour BG + border
      - Cloud callout (upper centre) with KQ text (underlined) + challenge
      - 4-children PNG centred on slide
      - 21C-skills PNG top right
      - geo-icon PNG + 'Being a Geographer' label — bottom centre
      - Day label — bottom left, large bold
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    # Day label — bottom left
    st.append(_styled_tbox(
        sid, lesson.get('day_label', ''),
        MARGIN_X, SH - 700000, 2000000, 650000,
        sz=3200, bold=True, color='1A3A5C',
        font=REG.TITLE_FONT, name='DayLabel'
    ))
    sid += 1

    # 'Being a Geographer' label — bottom centre
    st.append(_styled_tbox(
        sid, 'Being a Geographer',
        SW // 2 - 1200000, SH - 680000, 2400000, 550000,
        sz=2000, bold=True, color='1A3A5C',
        font=REG.TITLE_FONT, name='BeingAGeographerLabel', align='ctr'
    ))
    sid += 1

    # Cloud callout with KQ + challenge
    cloud_x, cloud_y = 380000, 180000
    cloud_w, cloud_h = SW - 760000, 2500000
    kq_text        = enquiry['key_question']
    challenge_text = enquiry.get('challenge', '')

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
        f'<a:bodyPr anchor="ctr"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="2200" b="1" u="sng" dirty="0">'
        f'<a:solidFill><a:srgbClr val="1A3A5C"/></a:solidFill>'
        f'<a:latin typeface="{REG.TITLE_FONT}" panose="02000000000000000000" '
        f'pitchFamily="2" charset="77"/></a:rPr>'
        f'<a:t>{ex(kq_text)}</a:t></a:r></a:p>'
        + (f'<a:p><a:pPr algn="ctr"/>'
           f'<a:r><a:rPr lang="en-GB" sz="1600" dirty="0">'
           f'<a:solidFill><a:srgbClr val="1A3A5C"/></a:solidFill></a:rPr>'
           f'<a:t>{ex(challenge_text)}</a:t></a:r></a:p>'
           if challenge_text else '') +
        f'</p:txBody></p:sp>'
    ))
    sid += 1
    save(t, sp)

    def _try_add(path, x, y, mw, mh):
        nonlocal sid
        if os.path.exists(path):
            add_img(sp, rp, work, path, x, y, mw, mh, sid)
            sid += 1
        else:
            print(f'  WARNING: asset not found, skipping: {path}', file=sys.stderr)

    # 4-children PNG — centred horizontally, lower half
    _try_add(REG.STATIC_ASSETS['children_kq'],
             SW // 2 - 3000000, 2700000, 6000000, 3600000)
    # 21C-skills PNG — top right
    _try_add(REG.STATIC_ASSETS['skills_21c'],
             SW - 2200000, 100000, 2000000, 1400000)
    # geo-icon — bottom centre (left of the label)
    _try_add(REG.STATIC_ASSETS['geo_icon'],
             SW // 2 - 1800000, SH - 700000, 500000, 500000)

    _append_border(sp, bd)
    return sp


def build_concepts_skills(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 2: Concepts & Skills

    Two images side by side — geo sub-concepts wheel (left) and geo skills
    wheel (right).  Each clicks in separately.
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    half_w = SW // 2 - MARGIN_X - 100000
    img_y  = 600000
    img_h  = SH - 800000

    left_path  = REG.STATIC_ASSETS['sub_concepts']
    right_path = REG.STATIC_ASSETS['skill']

    sid = 10
    ids_left, ids_right = [], []

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
        animate(sp, [s for s in [ids_left, ids_right] if s])

    _append_border(sp, bd)
    return sp


def build_progression(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 3: Progression

    Cloned from the Geographer.pptx template (anchor search).
    If the template slide cannot be found, falls back to displaying the
    progression PNG asset as a full-slide image.
    """
    # Try to clone from the template
    try:
        slide_num = find_slide_by_anchor(
            base_pptx, REG.PROGRESSION_SLIDE_ANCHOR)
        sp, rp = clone(work, base_pptx, slide_num)
        print(f'  [3] progression — cloned from template slide {slide_num}')
        return sp
    except (RuntimeError, Exception) as e:
        print(f'  [3] progression — template clone failed ({e}); '
              f'building from asset', file=sys.stderr)

    # Fallback: full-slide progression PNG
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    prog_path = REG.STATIC_ASSETS['progression']
    if os.path.exists(prog_path):
        add_img(sp, rp, work, prog_path, MARGIN_X, 300000,
                SW - 2 * MARGIN_X, SH - 500000, 10)
    else:
        t, st = get_spTree(sp)
        st.append(_styled_tbox(
            10, 'Geographer Progression',
            MARGIN_X, SH // 2 - 400000, SW - 2 * MARGIN_X, 800000,
            sz=3200, bold=True, color='1A3A5C', align='ctr',
            font=REG.TITLE_FONT, name='ProgressionFallback'
        ))
        save(t, sp)

    _append_border(sp, bd)
    return sp


def build_puzzle_pieces(work, base_pptx, lesson, enquiry, all_lessons, colours, master_idx):
    """
    Slide 4: Puzzle Pieces

    15 pieces arranged in rows (5 bottom / 6 middle / 4 top).
    Pieces 1..lesson_number are 'filled' by swapping their EMF rId to the
    EMF for that lesson's skill_focus.  Remaining pieces keep the template's
    default (empty) state.

    Clone strategy:
      1. Find the puzzle-pieces slide in the Geographer.pptx template.
      2. Clone it into the work directory.
      3. For each lesson ≤ current_lesson, swap the piece's EMF to the
         correct skill_focus EMF.

    Shape naming:
      The pieces must be named 'Piece1'…'Piece15' in the template (or
      whatever names are stored in PUZZLE_PIECE_SHAPE_NAMES).  If the
      shape is NOT found by name, the swap is skipped with a warning so
      the build still completes.
    """
    lesson_num = lesson['lesson_number']

    # Locate the puzzle-pieces slide in the template
    try:
        pp_slide_num = find_slide_by_anchor(
            base_pptx, REG.PUZZLE_PIECES_SLIDE_ANCHOR)
    except RuntimeError as e:
        print(f'  WARNING: cannot find puzzle pieces slide in template ({e}); '
              f'building a plain fallback slide', file=sys.stderr)
        return _build_puzzle_pieces_fallback(
            work, lesson, all_lessons, colours, master_idx)

    sp, rp = clone(work, base_pptx, pp_slide_num)

    # For each piece up to the current lesson, swap the EMF
    for idx, lsn in enumerate(all_lessons):
        if lsn['lesson_number'] > lesson_num:
            break
        piece_idx = idx   # 0-based
        if piece_idx >= len(REG.PUZZLE_PIECE_SHAPE_NAMES):
            print(f'  WARNING: lesson {lsn["lesson_number"]} has no matching '
                  f'piece shape name (only {len(REG.PUZZLE_PIECE_SHAPE_NAMES)} '
                  f'names defined)', file=sys.stderr)
            continue
        shape_name = REG.PUZZLE_PIECE_SHAPE_NAMES[piece_idx]
        skill      = lsn.get('skill_focus', 'questioning_predicting')
        _swap_piece_emf(sp, rp, work, shape_name, skill,
                        base_pptx, pp_slide_num)

    print(f'  [4] puzzle_pieces — {lesson_num} piece(s) filled')
    return sp


def _build_puzzle_pieces_fallback(work, lesson, all_lessons, colours, master_idx):
    """
    Fallback puzzle pieces slide when the template slide cannot be cloned.
    Draws a simple text-based representation so the build does not fail.
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10
    lesson_num = lesson['lesson_number']

    st.append(_styled_tbox(
        sid, 'Our Enquiry…',
        MARGIN_X, 120000, SW - 2 * MARGIN_X, 480000,
        sz=2800, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='PuzzleTitle'
    ))
    sid += 1
    save(t, sp)

    rows      = REG.PUZZLE_PIECE_ROWS  # [5, 6, 4]
    wall_top  = 700000
    wall_bot  = SH - 200000
    wall_h    = wall_bot - wall_top
    n_rows    = len(rows)
    row_h     = wall_h // n_rows
    piece_gap = 20000

    skill_colours = {
        'questioning_predicting':   'F4A460',
        'observing_recording':      'FFD966',
        'field_work':               'B19CD9',
        'map_skills':               '90EE90',
        'concluding_communicating': '87CEEB',
    }

    piece_global_idx = 0
    steps = []
    for row_i, n_pieces in enumerate(rows):
        row_y    = wall_bot - (row_i + 1) * row_h + 15000
        piece_w  = (SW - 2 * MARGIN_X - (n_pieces - 1) * piece_gap) // n_pieces
        piece_h  = row_h - 30000

        for col_i in range(n_pieces):
            lsn = all_lessons[piece_global_idx] if piece_global_idx < len(all_lessons) else None
            px  = MARGIN_X + col_i * (piece_w + piece_gap)

            if lsn and lsn['lesson_number'] <= lesson_num:
                skill = lsn.get('skill_focus', 'questioning_predicting')
                fill  = skill_colours.get(skill, 'DDDDDD')
                text  = lsn.get('building_block_text',
                                 lsn.get('lesson_title', str(lsn['lesson_number'])))
            else:
                fill = 'EEEEEE'
                text = ''

            t2, st2 = get_spTree(sp)
            st2.append(xp(
                f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
                f'<p:nvSpPr><p:cNvPr id="{sid}" name="Piece{piece_global_idx+1}BG"/>'
                f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{px}" y="{row_y}"/>'
                f'<a:ext cx="{piece_w}" cy="{piece_h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                f'<a:ln w="19050"><a:solidFill>'
                f'<a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>'
                f'</p:spPr>'
                f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
            ))
            save(t2, sp)
            bg_id = sid; sid += 1

            if text:
                t2, st2 = get_spTree(sp)
                st2.append(_styled_tbox(
                    sid, text,
                    px + 10000, row_y + 10000,
                    piece_w - 20000, piece_h - 20000,
                    sz=max(900, 1200 - len(text) * 5),
                    bold=True, color='1A3A5C', align='ctr',
                    name=f'PieceText{piece_global_idx+1}'
                ))
                save(t2, sp)
                if lsn and lsn['lesson_number'] <= lesson_num:
                    steps.append([bg_id, sid])
                sid += 1
            elif lsn and lsn['lesson_number'] <= lesson_num:
                steps.append([bg_id])

            piece_global_idx += 1

    if steps:
        animate(sp, steps)

    _append_border(sp, bd)
    return sp


def build_lo(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 5: Learning Objective

    Three panels (What / Why / How), each clicking in.
    Title = enquiry key question.

    LO placeholder indices (from Geographer.pptx, confirmed 2026-07-12):
      Date: ph0   WALT: lo10   TIB: lo13   ISB: lo14
    (These are the same as the history builder's LO slide.)
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    st.append(_styled_tbox(
        sid, enquiry['key_question'],
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 560000,
        sz=2200, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='LOTitle'
    ))
    sid += 1
    save(t, sp)

    panel_top = 700000
    panel_h   = SH - panel_top - 180000
    gap       = 80000
    panel_w   = (SW - 2 * MARGIN_X - 2 * gap) // 3

    panels = [
        ('I am learning…',           lesson.get('what', ''),    '1F3864', 'F2F9FF'),
        ('This is so…',              lesson.get('why', ''),     '1A5C2A', 'F0FFF4'),
        ('I will be successful by…', lesson.get('success', ''), '7D2200', 'FFF9F0'),
    ]

    steps = []
    for i, (header, body, text_col, fill_col) in enumerate(panels):
        px = MARGIN_X + i * (panel_w + gap)

        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="Panel{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{px}" y="{panel_top}"/>'
            f'<a:ext cx="{panel_w}" cy="{panel_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect">'
            f'<a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill_col}"/></a:solidFill>'
            f'<a:ln w="38100"><a:solidFill>'
            f'<a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp)
        bg_id = sid; sid += 1

        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, header,
            px + 40000, panel_top + 40000, panel_w - 80000, 500000,
            sz=1800, bold=True, color=text_col, align='ctr',
            font=REG.TITLE_FONT, name=f'Panel{i}Header'
        ))
        save(t2, sp)
        header_id = sid; sid += 1

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


def build_kwl(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 6 (Lesson 1 only): KWL Grid

    'We Do' layout.
    2-column table: 'Prior Knowledge and Skill' | 'I am curious about…'
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

    st.append(_styled_tbox(
        sid,
        'What knowledge am I bringing to this enquiry?\n'
        'What would I like to find out?',
        MARGIN_X, 80000, SW - 2 * MARGIN_X, 680000,
        sz=2400, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='ctr', name='KWLTitle'
    ))
    sid += 1

    st.append(_styled_tbox(
        sid, 'We Do', SW - MARGIN_X - 1000000, 80000, 900000, 400000,
        sz=1800, bold=True, color='FFFFFF', align='ctr', name='WeDoLabel'
    ))
    sid += 1
    save(t, sp)

    tbl_x, tbl_y = MARGIN_X, 820000
    tbl_w = SW - 2 * MARGIN_X
    tbl_h = SH - tbl_y - 200000
    col_w = tbl_w // 2
    row_h = tbl_h // 4

    headers = ['Prior Knowledge and Skill', 'I am curious about…']
    for ci, hdr in enumerate(headers):
        cx = tbl_x + ci * col_w
        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="TblH{ci}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{cx}" y="{tbl_y}"/>'
            f'<a:ext cx="{col_w}" cy="{row_h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="1F3864"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill>'
            f'<a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
        ))
        save(t2, sp); sid += 1
        t2, st2 = get_spTree(sp)
        st2.append(_styled_tbox(
            sid, hdr, cx + 30000, tbl_y + 20000, col_w - 60000, row_h - 40000,
            sz=1800, bold=True, color='FFFFFF', align='ctr', name=f'TblH{ci}Txt'
        ))
        save(t2, sp); sid += 1

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
                f'<a:solidFill><a:srgbClr val='
                f'{"F2F2F2" if ri % 2 == 0 else "FFFFFF"}"/></a:solidFill>'
                f'<a:ln w="19050"><a:solidFill>'
                f'<a:srgbClr val="AAAAAA"/></a:solidFill></a:ln>'
                f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'
            ))
            save(t2, sp); sid += 1

    _append_border(sp, bd)
    return sp


def build_recap_quiz(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 6 (Lessons 2+): Recap Quiz

    Up to 5 Q+A pairs.  Q clicks in → A clicks in → next Q…
    Paragraph-level animation on a single text box (same pattern as history).
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
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

    _A_NS = A; _P_NS = P

    def _q_para(text, num):
        p = etree.Element(f'{{{_A_NS}}}p')
        pPr = etree.SubElement(p, f'{{{_A_NS}}}pPr')
        pPr.set('marL', '514350'); pPr.set('indent', '-514350')
        buFont = etree.SubElement(pPr, f'{{{_A_NS}}}buFont')
        buFont.set('typeface', '+mj-lt')
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
        clr  = etree.SubElement(fill, f'{{{_A_NS}}}srgbClr')
        clr.set('val', '1A5C2A')
        t_ = etree.SubElement(r, f'{{{_A_NS}}}t'); t_.text = '→ ' + text
        return p

    content_sp_xml = (
        f'<p:sp xmlns:p="{_P_NS}" xmlns:a="{_A_NS}">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="QuizContent"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="680000"/>'
        f'<a:ext cx="{SW - 2 * MARGIN_X}" cy="{SH - 900000}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square"><a:normAutofit/></a:bodyPr>'
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
            endPr.set('lang', 'en-GB'); endPr.set('dirty', '0')
            txBody.append(spacer)

    content_sp_id = sid
    t2, st2 = get_spTree(sp)
    st2.append(content_el)
    save(t2, sp)
    sid += 1

    animated_para_indices = []
    for i in range(len(qna)):
        animated_para_indices.append(i * 3)
        animated_para_indices.append(i * 3 + 1)

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
            f'<p:cTn id="{behav}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
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
        f'<p:tnLst><p:par><p:cTn id="{root_id}" dur="indefinite" restart="never" '
        f'nodeType="tmRoot">'
        f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="{seq_id}" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'<p:bldLst><p:bldP spid="{content_sp_id}" grpId="0" build="p"/>'
        f'</p:bldLst></p:timing>'
    )

    tree = xr(sp); root = tree.getroot()
    existing = root.find(f'{{{_P_NS}}}timing')
    if existing is not None: root.remove(existing)
    root.append(etree.fromstring(timing_xml))
    xw(tree, sp)

    _append_border(sp, bd)
    return sp


def build_key_vocabulary(work, base_pptx, lesson, enquiry, colours, master_idx):
    """
    Slide 7: Key Vocabulary

    Up to 5 word/definition pairs.
    Animation: Word 1 → Definition 1 → Word 2 → …
    Each pair in a visually distinct card (word left, definition right).
    """
    sp, rp = fresh_geo(work, 'Blank', master_idx)
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
    word_colours = ['DAE3F3', 'FFE6CC', 'D5E8D4', 'F8CECC', 'E1D5E7']

    for i, item in enumerate(vocab):
        cy        = card_top + i * (card_h + card_gap)
        word_fill = word_colours[i % len(word_colours)]

        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="WordCard{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="{cy}"/>'
            f'<a:ext cx="{word_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect">'
            f'<a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{word_fill}"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill>'
            f'<a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
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

        t2, st2 = get_spTree(sp)
        st2.append(xp(
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr><p:cNvPr id="{sid}" name="DefCard{i}BG"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{MARGIN_X + word_w + 20000}" y="{cy}"/>'
            f'<a:ext cx="{def_w}" cy="{card_h}"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect">'
            f'<a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'<a:ln w="19050"><a:solidFill>'
            f'<a:srgbClr val="{bd}"/></a:solidFill></a:ln>'
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


# ══════════════════════════════════════════════════════════════════════════════
#  Variable slide builders
# ══════════════════════════════════════════════════════════════════════════════

def _build_content_slide(work, layout_name, slide_spec, lesson,
                         colours, badge_label, master_idx):
    """
    Generic builder for I Do / We Do / You Do / You Do Trio slides.

    Title from slide_spec['title'].
    Content from slide_spec['content'] split into sentences, each animated in.
    Concept colour BG + border.
    """
    sp, rp = fresh_geo(work, layout_name, master_idx)
    bg, bd = colours['bg'], colours['border']
    _apply_concept_bg(sp, bg, bd)

    t, st = get_spTree(sp)
    sid = 10

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
        f'<a:prstGeom prst="roundRect">'
        f'<a:avLst><a:gd name="adj" fmla="val 16667"/></a:avLst></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{bfill}"/></a:solidFill>'
        f'<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="ctr"/>'
        f'<a:r><a:rPr lang="en-GB" sz="1600" b="1" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{btext}"/></a:solidFill></a:rPr>'
        f'<a:t>{ex(badge_label)}</a:t></a:r></a:p></p:txBody></p:sp>'
    ))
    sid += 1

    st.append(_styled_tbox(
        sid, slide_spec.get('title', ''),
        MARGIN_X, 80000, SW - 2 * MARGIN_X - 1700000, 520000,
        sz=2800, bold=True, color='1A3A5C', font=REG.TITLE_FONT,
        align='l', name='SlideTitle'
    ))
    sid += 1
    save(t, sp)

    content = slide_spec.get('content', '')
    sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', content) if s.strip()]
    if not sentences:
        sentences = [content] if content else []

    groups = []
    for i, sentence in enumerate(sentences):
        by = 680000 + i * 1100000
        if by + 900000 > SH - 150000:
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


def build_i_do(work, slide_spec, lesson, enquiry, colours, master_idx):
    return _build_content_slide(work, 'I do', slide_spec, lesson,
                                colours, 'I Do', master_idx)

def build_we_do(work, slide_spec, lesson, enquiry, colours, master_idx):
    return _build_content_slide(work, 'We do', slide_spec, lesson,
                                colours, 'We Do', master_idx)

def build_you_do(work, slide_spec, lesson, enquiry, colours, master_idx):
    return _build_content_slide(work, 'You do Ind', slide_spec, lesson,
                                colours, 'You Do', master_idx)

def build_you_do_trio(work, slide_spec, lesson, enquiry, colours, master_idx):
    return _build_content_slide(work, 'You Do Trio', slide_spec, lesson,
                                colours, 'You Do (Trio)', master_idx)


# ══════════════════════════════════════════════════════════════════════════════
#  Main orchestrator
# ══════════════════════════════════════════════════════════════════════════════

VARIABLE_DISPATCH = {
    'i_do':       build_i_do,
    'we_do':      build_we_do,
    'you_do':     build_you_do,
    'you_do_trio':build_you_do_trio,
}


def build_one_lesson(mtp, lesson_num, base_pptx, out_pptx):
    """Build a single lesson PPTX from the MTP dict."""
    lesson_data = next(
        (l for l in mtp['lessons'] if l['lesson_number'] == lesson_num), None
    )
    if lesson_data is None:
        raise ValueError(f'Lesson {lesson_num} not found in MTP')

    # Per-lesson master / colours from substantive_concept
    sc = lesson_data.get(
        'substantive_concept',
        mtp.get('default_substantive_concept', REG.DEFAULT_SUBSTANTIVE_CONCEPT)
    )
    master_idx = REG.MASTER_INDICES.get(sc, 0)
    colours    = REG.MASTER_COLOURS.get(sc, REG.MASTER_COLOURS[REG.DEFAULT_SUBSTANTIVE_CONCEPT])
    all_lessons = mtp['lessons']

    import tempfile
    tmp_base = os.environ.get('GEO_TMP', tempfile.gettempdir())
    work = os.path.join(tmp_base, f'geo_{os.getpid()}_L{lesson_num}_work')

    lesson_title = lesson_data.get('lesson_title', lesson_data.get('building_block_text', ''))
    print(f'\nLesson {lesson_num}: {lesson_title}  [{sc} / master {master_idx}]')

    unzip(base_pptx, work)
    clear_slides(work)
    build_layout_map(work)       # flat map (lib_ooxml default)
    build_geo_layout_map(work)   # two-key map (master_idx, name)

    src_dir(base_pptx)   # warm the source cache

    # ── Fixed slides ──────────────────────────────────────────────────────────
    print('  [1] key_question')
    build_key_question(work, base_pptx, lesson_data, mtp, colours, master_idx)

    print('  [2] concepts_skills')
    build_concepts_skills(work, base_pptx, lesson_data, mtp, colours, master_idx)

    print('  [3] progression')
    build_progression(work, base_pptx, lesson_data, mtp, colours, master_idx)

    print('  [4] puzzle_pieces')
    build_puzzle_pieces(work, base_pptx, lesson_data, mtp, all_lessons,
                        colours, master_idx)

    print('  [5] lo')
    build_lo(work, base_pptx, lesson_data, mtp, colours, master_idx)

    if lesson_num == 1:
        print('  [6] kwl')
        build_kwl(work, base_pptx, lesson_data, mtp, colours, master_idx)
    else:
        print('  [6] recap_quiz')
        build_recap_quiz(work, base_pptx, lesson_data, mtp, colours, master_idx)

    print('  [7] key_vocabulary')
    build_key_vocabulary(work, base_pptx, lesson_data, mtp, colours, master_idx)

    # ── Variable slides ───────────────────────────────────────────────────────
    for i, slide_spec in enumerate(lesson_data.get('slides', []), start=8):
        stype = slide_spec['type']
        if stype not in VARIABLE_DISPATCH:
            print(f'  [{i}] WARNING: unknown slide type "{stype}", skipping',
                  file=sys.stderr)
            continue
        print(f'  [{i}] {stype}: {slide_spec.get("title", "")}')
        VARIABLE_DISPATCH[stype](work, slide_spec, lesson_data, mtp,
                                 colours, master_idx)

    # ── Finalise ──────────────────────────────────────────────────────────────
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
    topic = mtp.get('topic', 'Geography').replace(' ', '_')
    built = []

    for lesson in mtp['lessons']:
        n     = lesson['lesson_number']
        title = (lesson.get('lesson_title') or
                 lesson.get('building_block_text') or
                 f'Lesson_{n}')
        label = title.replace(' ', '_').replace('?', '')[:40]
        fname = f'L{n:02d}_{label}.pptx'
        out_path = os.path.join(out_dir, fname)
        build_one_lesson(mtp, n, base_pptx, out_path)
        built.append(out_path)

    print(f'\nDone — {len(built)} PPTXs written to {out_dir}')
    return built


def main():
    parser = argparse.ArgumentParser(description='Geography lesson PPTX builder')
    parser.add_argument('mtp_json',    help='Path to the enquiry MTP JSON file')
    parser.add_argument('--base-pptx', required=True,
                        help='Geographer.pptx template')
    parser.add_argument('--out-dir',   default='./Geography_Lessons',
                        help='Output directory for all lesson PPTXs')
    parser.add_argument('--lesson',    type=int, default=None,
                        help='Build only this lesson number (omit to build all)')
    parser.add_argument('--out-pptx',  default=None,
                        help='Output path for single lesson (only with --lesson)')
    args = parser.parse_args()

    if not os.path.exists(args.mtp_json):
        sys.exit(f'MTP JSON not found: {args.mtp_json}')
    if not os.path.exists(args.base_pptx):
        sys.exit(f'Base PPTX not found: {args.base_pptx}')

    if args.lesson:
        out = (args.out_pptx or
               os.path.join(args.out_dir, f'L{args.lesson:02d}.pptx'))
        with open(args.mtp_json) as f:
            mtp = json.load(f)
        build_one_lesson(mtp, args.lesson, args.base_pptx, out)
    else:
        build_all_lessons(args.mtp_json, args.base_pptx, args.out_dir)


if __name__ == '__main__':
    main()
