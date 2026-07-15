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
    IMG_REL,
    unzip, rezip, clear_slides, build_layout_map,
    find_slide_by_anchor, clone,
    get_spTree, save,
    add_img, animate,
    xr, xw, xp, ex,
    SW, SH, next_sn, next_mn,
    strip_orphaned_media,
    embed_fonts,
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

    Universal overflow prevention (two-layer):
      Layer 1 — explicit font cap:
        When no sz is given, cap based on the longest line's character count
        so text is never written at a size that guarantees overflow.
        Thresholds are conservative for Twinkl Cursive Looped which runs
        ~20% wider than screen-render fonts.
          ≤35 chars → inherit from layout/master (no cap)
          36–55 chars → 1800 (18 pt)
          >55 chars  → 1600 (16 pt)

      Layer 2 — normAutofit:
        Applied in the bodyPr so PowerPoint will shrink any remaining
        overflow at render time regardless of font or layout size.

    bodyPr strategy:
      ph_idx == 0 (title): standard margins, wrap, normAutofit.
      ph_idx 1–9  (std body): standard margins, wrap, normAutofit.
      ph_idx ≥10  (custom layout PHs — LR speech bubbles, KQ callout, etc.):
        zero internal margins to match the layout placeholder definition,
        wrap, top-anchor, normAutofit.  These layouts define bodyPr with
        lIns=tIns=rIns=bIns=0 so our slide-level override must match to
        avoid adding unexpected padding that reduces the effective text area.
    """
    # ── Layer 1: font cap (idx >= 10 only) ──────────────────────────────────
    # Only small custom-layout PHs (LR speech bubbles etc.) need a hard cap.
    # Standard title/body PHs are large enough that normAutofit handles them.
    # Threshold is based on the LR bubble dimensions (3370263 × 1096962 EMU,
    # ≈3.69" × 1.20") with Twinkl Cursive Looped running ~20% wider than
    # screen fonts.  At 24pt, roughly 22 chars fit per line; 3 lines = 1.15"
    # which just fits.  4 lines = 1.53" → overflows.  Cap only fires when the
    # longest line suggests 4+ lines would result at 24pt (i.e. > ~65 chars).
    _eff_sz = sz
    if not _eff_sz and ph_idx >= 10:
        _max_ch = max(len(l) for l in str(text).split('\n')) if text else 0
        if _max_ch > 80:
            _eff_sz = '1600'   # 16pt — very long text, 4+ lines even at 20pt
        elif _max_ch > 65:
            _eff_sz = '2000'   # 20pt — borderline; 4 lines at 24pt overflows

    # Run properties
    rpr_parts = ['lang="en-GB" dirty="0"']
    if _eff_sz:
        rpr_parts.append(f'sz="{_eff_sz}"')
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

    # ── Layer 2: bodyPr with normAutofit ─────────────────────────────────────
    # ph element — title uses type="title"; body must include type="body" so
    # PowerPoint matches the layout PH exactly.
    if ph_idx == 0:
        ph_xml  = '<p:ph type="title"/>'
        body_pr = '<a:bodyPr wrap="square" anchor="t"><a:normAutofit/></a:bodyPr>'
    elif ph_idx >= 10:
        # Custom-indexed layout PHs (LR speech bubbles, KQ callout, etc.).
        # Layout defines these with zero internal margins — mirror that so our
        # override doesn't shrink the effective text area.
        ph_xml  = f'<p:ph type="body" idx="{ph_idx}"/>'
        body_pr = (
            '<a:bodyPr spcFirstLastPara="1" wrap="square" '
            'lIns="0" tIns="0" rIns="0" bIns="0" anchor="t" anchorCtr="0">'
            '<a:normAutofit/></a:bodyPr>'
        )
    else:
        ph_xml  = f'<p:ph type="body" idx="{ph_idx}"/>'
        body_pr = '<a:bodyPr wrap="square" anchor="t"><a:normAutofit/></a:bodyPr>'

    sp_xml = (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{ph_idx + 100}" name="ph{ph_idx}"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr>{ph_xml}</p:nvPr>'
        f'</p:nvSpPr>'
        f'<p:spPr/>'
        f'<p:txBody>{body_pr}<a:lstStyle/>'
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


def _add_strip_img(sp, rp, work, img_path, x, y, w, h, sid):
    """Place a strip image filling EXACTLY (x, y, w, h) — no aspect-ratio preservation.
    Uses <a:stretch><a:fillRect/></a:stretch> so PowerPoint stretches the bitmap
    to fill the box, matching the w×h dimensions set on the xfrm ext element."""
    import re as _re
    n = next_mn(work)
    extn = Path(img_path).suffix.lower()
    nm = f'image{n}{extn}'
    md = Path(work) / 'ppt' / 'media'
    md.mkdir(exist_ok=True)
    shutil.copy(img_path, md / nm)

    rt = xr(rp); rr = rt.getroot()
    ex_rids = {int(m.group(1)) for el in rr
               for m in [_re.match(r'rId(\d+)', el.get('Id', ''))] if m}
    rn = max(ex_rids, default=0) + 1
    rid = f'rId{rn}'
    etree.SubElement(rr, 'Relationship',
                     {'Id': rid, 'Type': IMG_REL, 'Target': f'../media/{nm}'})
    rt.write(rp, xml_declaration=True, encoding='UTF-8', standalone=True)

    st = xr(sp)
    spTree = st.getroot().find(f'.//{{{P}}}spTree')
    spTree.append(xp(
        f'<p:pic xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
        f'<p:nvPicPr>'
        f'<p:cNvPr id="{sid}" name="Strip{sid}"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="0"/></p:cNvPicPr>'
        f'<p:nvPr/>'
        f'</p:nvPicPr>'
        f'<p:blipFill>'
        f'<a:blip r:embed="{rid}"/>'
        f'<a:stretch><a:fillRect/></a:stretch>'
        f'</p:blipFill>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'</p:spPr>'
        f'</p:pic>'
    ))
    st.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)


def build_progression(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 3: Progression — animated, one strip per year group (Y1–Y6).

    Layout: Revisit (provides themed background + globe icon top-left).

    Left panel (static, always visible):
      • Concept title text box
      • Concept icon(s) + definition text — one icon per row, placed below
        the globe using the PNG assets from ASSETS_ROOT.

    Right panel (animated):
      • 6 strip images placed in a vertical column.
      • Each strip appears on click (Y1 first → Y6 last).
      • Strips that are missing from disk are silently skipped.

    To add strips: drop geo-prog-{concept}-y{N}.png into ASSETS_ROOT.
    No code change required.
    """
    sc = lesson.get('substantive_concept', REG.DEFAULT_SUBSTANTIVE_CONCEPT)
    sp, rp = fresh_geo(work, 'Revisit', master_idx)

    # ── Slide geometry ────────────────────────────────────────────────────────
    # Widescreen 16:9 — 12192000 × 6858000 EMU
    # Left panel: ~28% of width (icons + text), right panel: strips
    # The Revisit layout's globe + "Revisit" title occupies the top ~950 000 EMU.
    # All content must start below that to avoid overlap.
    LEFT_W   = 3200000   # left panel width (~2.6 in)
    MARGIN_T = 1050000   # top margin — below the Revisit header
    MARGIN_B = 200000    # bottom margin
    STRIP_X  = LEFT_W + 200000   # strips start after left panel + gap
    STRIP_W  = SW - STRIP_X - 150000
    USABLE_H = SH - MARGIN_T - MARGIN_B
    STRIP_H  = USABLE_H // 6    # height per strip

    # ── Left panel — concept title ────────────────────────────────────────────
    title_text = REG.CONCEPT_TITLES.get(sc, sc.replace('_', ' ').title())
    title_xml = (
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="300" name="ProgTitle"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/>'
        f'</p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="120000" y="{MARGIN_T}"/>'
        f'<a:ext cx="{LEFT_W - 120000}" cy="500000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square"><a:normAutofit/></a:bodyPr>'
        f'<a:lstStyle/>'
        f'<a:p><a:r>'
        f'<a:rPr lang="en-GB" sz="1800" b="1" dirty="0">'
        f'<a:latin typeface="Twinkl Cursive Looped"/>'
        f'</a:rPr>'
        f'<a:t>{ex(title_text)}</a:t>'
        f'</a:r></a:p>'
        f'</p:txBody>'
        f'</p:sp>'
    )
    t, st = get_spTree(sp)
    st.append(etree.fromstring(title_xml))
    save(t, sp)

    # ── Left panel — concept icons + definition text ──────────────────────────
    icon_data  = REG.CONCEPT_ICON_DATA.get(sc, [])
    icon_y     = MARGIN_T + 560000   # start below title
    icon_size  = 650000              # icon image square size
    text_x     = 120000 + icon_size + 80000
    text_w     = LEFT_W - text_x - 60000

    shape_id = 310
    for icon_file, definition in icon_data:
        icon_path = REG.ensure_asset(icon_file)
        if icon_path and os.path.exists(icon_path):
            add_img(sp, rp, work, icon_path,
                    120000, icon_y, icon_size, icon_size, shape_id)
            shape_id += 1

        # Definition text box alongside the icon
        def_xml = (
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr>'
            f'<p:cNvPr id="{shape_id}" name="DefText{shape_id}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/>'
            f'</p:nvSpPr>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{text_x}" y="{icon_y}"/>'
            f'<a:ext cx="{text_w}" cy="{icon_size}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/>'
            f'</p:spPr>'
            f'<p:txBody>'
            f'<a:bodyPr wrap="square" anchor="t"><a:normAutofit/></a:bodyPr>'
            f'<a:lstStyle/>'
            f'<a:p><a:r>'
            f'<a:rPr lang="en-GB" sz="1000" dirty="0">'
            f'<a:latin typeface="Aptos"/>'
            f'</a:rPr>'
            f'<a:t>{ex(definition)}</a:t>'
            f'</a:r></a:p>'
            f'</p:txBody>'
            f'</p:sp>'
        )
        t, st = get_spTree(sp)
        st.append(etree.fromstring(def_xml))
        save(t, sp)
        shape_id += 1

        icon_y += icon_size + 60000   # gap between icon rows

    # ── Right panel — 6 year-group strips ────────────────────────────────────
    # Visual layout: Y6 at top, Y5 below, ..., Y1 at bottom.
    # Animation order: Y1 reveals first (bottom), Y6 reveals last (top).
    # So we place Y6→Y1 top-to-bottom, then animate in reverse (Y1 first).
    strip_shape_ids = []   # index 0 = Y1, index 5 = Y6 (matches year group)
    strip_id = 400

    for yr in range(1, 7):
        strip_path = REG.progression_strip_path(sc, yr)
        if not strip_path or not os.path.exists(strip_path):
            print(f'  NOTE: progression strip missing for Y{yr} ({sc})',
                  file=sys.stderr)
            strip_shape_ids.append(None)
            strip_id += 1
            continue

        # Y6 sits at MARGIN_T, Y1 sits at bottom: y = MARGIN_T + (6-yr)*STRIP_H
        y_pos = MARGIN_T + (6 - yr) * STRIP_H
        _add_strip_img(sp, rp, work, strip_path,
                       STRIP_X, y_pos, STRIP_W, STRIP_H, strip_id)
        strip_shape_ids.append(strip_id)
        strip_id += 1

    # ── Animation — reveal bottom-to-top (Y1 first, Y6 last) ─────────────────
    # strip_shape_ids[0] = Y1 (bottom), strip_shape_ids[5] = Y6 (top)
    visible_strips = [(i, sid) for i, sid in enumerate(strip_shape_ids)
                      if sid is not None]
    # Animate in ascending order (Y1→Y6) so bottom strip appears first
    visible_strips_anim = sorted(visible_strips, key=lambda x: x[0])

    if visible_strips_anim:
        nid = [1]
        def _nid(): v = nid[0]; nid[0] += 1; return str(v)

        root_id = _nid(); seq_id = _nid()
        blocks = []
        for _, sid in visible_strips_anim:
            b, inn, clk, bhv = _nid(), _nid(), _nid(), _nid()
            blocks.append(
                f'<p:par xmlns:p="{P}"><p:cTn id="{b}" fill="hold">'
                f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                f'<p:childTnLst><p:par><p:cTn id="{inn}" fill="hold">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst><p:par>'
                f'<p:cTn id="{clk}" presetID="1" presetClass="entr" '
                f'presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst><p:set><p:cBhvr>'
                f'<p:cTn id="{bhv}" dur="1" fill="hold">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
                f'<p:attrNameLst>'
                f'<p:attrName>style.visibility</p:attrName>'
                f'</p:attrNameLst>'
                f'</p:cBhvr>'
                f'<p:to><p:strVal val="visible"/></p:to>'
                f'</p:set></p:childTnLst></p:cTn>'
                f'</p:par></p:childTnLst></p:cTn></p:par>'
                f'</p:childTnLst></p:cTn></p:par>'
            )

        timing_xml = (
            f'<p:timing xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:tnLst><p:par><p:cTn id="{root_id}" dur="indefinite" '
            f'restart="never" nodeType="tmRoot"><p:childTnLst>'
            f'<p:seq concurrent="1" nextAc="seek">'
            f'<p:cTn id="{seq_id}" dur="indefinite" nodeType="mainSeq">'
            f'<p:childTnLst>{"".join(blocks)}</p:childTnLst></p:cTn>'
            f'<p:prevCondLst><p:cond evt="onPrev" delay="0">'
            f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0">'
            f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
            f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
            f'<p:bldLst>'
            + ''.join(
                f'<p:bldP spid="{sid}" grpId="0" build="p"/>'
                for _, sid in visible_strips_anim
            )
            + f'</p:bldLst></p:timing>'
        )

        tree = xr(sp)
        sld_root = tree.getroot()
        existing = sld_root.find(f'{{{P}}}timing')
        if existing is not None:
            sld_root.remove(existing)
        sld_root.append(etree.fromstring(timing_xml))
        xw(tree, sp)

    found = sum(1 for sid in strip_shape_ids if sid is not None)
    print(f'  [3] progression — {found}/6 strips for "{sc}"')
    return sp


def build_puzzle_pieces(work, base_pptx, lesson, enquiry, all_lessons, master_idx):
    """
    Slide 4: Puzzle Pieces (jigsaw).

    For lesson N in the enquiry sequence:
      - Slot  1       : always visible on slide load — no animation entry
      - Slots 2..N    : each gets one click-reveal animation (p:set style.visibility → visible)
      - Slots N+1..15 : not added to slide at all

    Each slot is a p:grpSp built from scratch:
      - p:pic  : skill-coloured PNG from ASSETS_ROOT/Jigsaw Pieces/
      - p:sp   : TextBox with lesson_title (11pt Twinkl Cursive Looped)

    Positions come from REG.JIGSAW_PIECE_POSITIONS (EMU coords extracted from
    jigsaw-animated.pptx 2026-07-14). Slide references 'Revisit' layout which
    gives the WFA master background without the KQ cloud callout — no double-
    rendering possible because pieces are built into the slide's own spTree.
    """
    lesson_num  = lesson['lesson_number']
    positions   = REG.JIGSAW_PIECE_POSITIONS          # list of (x, y, cx, cy)

    # Jigsaw PNGs are resolved per-piece via REG.ensure_asset so they are
    # fetched from the GitHub repo automatically when not found locally.
    # jigsaw_dir is kept as a fallback for any legacy path references.
    jigsaw_dir = os.path.join(REG.ASSETS_ROOT, 'Jigsaw Pieces')

    # Use 'Puzzle Pieces' layout — provides the "Connections" header, WFA
    # background and globe icon for this slide type.  The layout contains NO
    # actual puzzle-piece shapes (only decorative text + images), so building
    # groups into the slide's own spTree causes no double-rendering.
    sp, rp = fresh_geo(work, 'Puzzle Pieces', master_idx)

    # ── Load slide XML ────────────────────────────────────────────────────────
    tree   = xr(sp)
    root   = tree.getroot()
    cSld   = root.find(f'{{{P}}}cSld')
    spTree = cSld.find(f'{{{P}}}spTree')

    # ── Load rels to append PNG image relationships ───────────────────────────
    rels_tree = xr(rp)
    rels_root = rels_tree.getroot()

    # Find the highest existing rId number so we can start above it
    def _max_rid(rels_el):
        hi = 1
        for r in rels_el:
            rid = r.get('Id', 'rId0')
            try:
                hi = max(hi, int(rid.replace('rId', '')))
            except ValueError:
                pass
        return hi

    next_rid     = _max_rid(rels_root) + 1
    png_rid_map  = {}   # skill_focus → rId (deduplicate same PNG)

    def _add_png_rel(skill):
        """Copy PNG to media dir and add a relationship. Returns rId or None."""
        nonlocal next_rid
        if skill in png_rid_map:
            return png_rid_map[skill]
        fname = REG.SKILL_JIGSAW_PNG.get(skill)
        if not fname:
            fname = REG.SKILL_JIGSAW_PNG.get('questioning_predicting')
        # Use ensure_asset so the PNG is fetched from GitHub if not local
        src = REG.ensure_asset(f'Jigsaw Pieces/{fname}')
        if not src or not os.path.exists(src):
            print(f'  WARNING: jigsaw PNG not available: Jigsaw Pieces/{fname}', file=sys.stderr)
            return None
        media_dir  = f'{work}/ppt/media'
        tgt_name   = f'jig_{skill}.png'
        tgt_path   = f'{media_dir}/{tgt_name}'
        if not os.path.exists(tgt_path):
            import shutil as _sh
            _sh.copy2(src, tgt_path)
        rid = f'rId{next_rid}'
        next_rid  += 1
        rel_el = etree.SubElement(rels_root, 'Relationship')
        rel_el.set('Id',     rid)
        rel_el.set('Type',   'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
        rel_el.set('Target', f'../media/{tgt_name}')
        png_rid_map[skill] = rid
        return rid

    # ── Build piece groups ────────────────────────────────────────────────────
    # spids: group=200+i*3, pic=201+i*3, txt=202+i*3  (i=0-indexed slot)
    BASE_SPID = 200
    animated_spids = []   # group spids for pieces 2..N (click-revealed)

    for i, lsn in enumerate(all_lessons[:lesson_num]):
        if i >= len(positions):
            break

        off_x, off_y, cx, cy = positions[i]
        skill  = lsn.get('skill_focus', 'questioning_predicting')
        txt    = (lsn.get('puzzle_piece_text') or
                  lsn.get('lesson_title') or
                  f'Lesson {i + 1}')
        rid    = _add_png_rel(skill)
        if rid is None:
            continue

        grp_spid = BASE_SPID + i * 3
        pic_spid = grp_spid + 1
        sp_spid  = grp_spid + 2
        if i > 0:                    # piece 1 (i=0) is always visible; 2..N animate
            animated_spids.append(grp_spid)

        # TextBox sits in the safe body zone of the piece.
        # Margins hand-tuned by Innes McLean 2026-07-15 from jig_v9_colour_L5.pptx.
        # 30% side margins (≈ 40% wide), 31% from top, 38% tall.
        # Child coords map 1-to-1 to slide coords (chOff = off_x, off_y).
        tb_margin = int(cx * 0.30)
        tb_x      = off_x + tb_margin
        tb_y      = off_y + int(cy * 0.31)
        tb_cx     = cx - 2 * tb_margin
        tb_cy     = int(cy * 0.38)

        grp_xml = (
            f'<p:grpSp xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
              f'<p:nvGrpSpPr>'
                f'<p:cNvPr id="{grp_spid}" name="JigsawPiece_{i+1}"/>'
                f'<p:cNvGrpSpPr/>'
                f'<p:nvPr/>'
              f'</p:nvGrpSpPr>'
              f'<p:grpSpPr>'
                f'<a:xfrm>'
                  f'<a:off x="{off_x}" y="{off_y}"/>'
                  f'<a:ext cx="{cx}" cy="{cy}"/>'
                  f'<a:chOff x="{off_x}" y="{off_y}"/>'
                  f'<a:chExt cx="{cx}" cy="{cy}"/>'
                f'</a:xfrm>'
              f'</p:grpSpPr>'
              # Image — fills the whole group (child coords = slide coords when chOff=off)
              f'<p:pic>'
                f'<p:nvPicPr>'
                  f'<p:cNvPr id="{pic_spid}" name="JigsawImg_{i+1}"/>'
                  f'<p:cNvPicPr/>'
                  f'<p:nvPr/>'
                f'</p:nvPicPr>'
                f'<p:blipFill>'
                  f'<a:blip r:embed="{rid}"/>'
                  f'<a:stretch><a:fillRect/></a:stretch>'
                f'</p:blipFill>'
                f'<p:spPr>'
                  f'<a:xfrm>'
                    f'<a:off x="{off_x}" y="{off_y}"/>'
                    f'<a:ext cx="{cx}" cy="{cy}"/>'
                  f'</a:xfrm>'
                  f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'</p:spPr>'
              f'</p:pic>'
              # TextBox — lesson title centred in piece body
              f'<p:sp>'
                f'<p:nvSpPr>'
                  f'<p:cNvPr id="{sp_spid}" name="JigsawTxt_{i+1}"/>'
                  f'<p:cNvSpPr txBox="1"/>'
                  f'<p:nvPr/>'
                f'</p:nvSpPr>'
                f'<p:spPr>'
                  f'<a:xfrm>'
                    f'<a:off x="{tb_x}" y="{tb_y}"/>'
                    f'<a:ext cx="{tb_cx}" cy="{tb_cy}"/>'
                  f'</a:xfrm>'
                  f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                  f'<a:noFill/>'
                f'</p:spPr>'
                f'<p:txBody>'
                  f'<a:bodyPr wrap="square" rtlCol="0" anchor="ctr">'
                    f'<a:normAutofit/>'
                  f'</a:bodyPr>'
                  f'<a:lstStyle/>'
                  f'<a:p>'
                    f'<a:pPr algn="ctr"/>'
                    f'<a:r>'
                      f'<a:rPr lang="en-GB" sz="1000" b="1" dirty="0">'
                        f'<a:latin typeface="Twinkl Cursive Looped"'
                        f' panose="02000000000000000000"'
                        f' pitchFamily="2" charset="77"/>'
                        f'<a:solidFill><a:srgbClr val="1C1C1C"/></a:solidFill>'
                      f'</a:rPr>'
                      f'<a:t>{ex(txt)}</a:t>'
                    f'</a:r>'
                  f'</a:p>'
                f'</p:txBody>'
              f'</p:sp>'
            f'</p:grpSp>'
        )
        spTree.append(etree.fromstring(grp_xml))

    # ── Save slide XML ────────────────────────────────────────────────────────
    xw(tree, sp)

    # ── Save updated rels ─────────────────────────────────────────────────────
    xw(rels_tree, rp)

    # ── Build timing: one click-reveal par block per animated piece ───────────
    # Piece 1 (i=0) has no timing entry → always visible on slide load.
    # Pieces 2..N each get one <p:par> in mainSeq that fires on click.
    # Lesson 1 has only piece 1 → no animations → skip timing entirely
    # (empty childTnLst / bldLst causes PowerPoint to repair-and-strip the slide).
    # cTn IDs: each block uses 4 IDs (outer, inner, clickEffect, set).
    # Structure confirmed from Innes's jig_v6_L15.pptx edit (2026-07-15).
    # prevCondLst/nextCondLst use evt="onPrev"/"onNext"; tgtEl is direct child
    # of cond — no <p:tn> wrapper.
    if not animated_spids:
        # No animations needed — remove any existing timing and exit
        existing = root.find(f'{{{P}}}timing')
        if existing is not None:
            root.remove(existing)
        xw(tree, sp)
        print(f'  [4] puzzle_pieces — {lesson_num}/{len(positions)} pieces  (no animations)')
        return sp

    inner_pars = ''
    ctn_id = 3
    for anim_spid in animated_spids:
        inner_pars += (
            f'<p:par>'
              f'<p:cTn id="{ctn_id}" fill="hold">'
                f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                f'<p:childTnLst>'
                  f'<p:par>'
                    f'<p:cTn id="{ctn_id+1}" fill="hold">'
                      f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                      f'<p:childTnLst>'
                        f'<p:par>'
                          f'<p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr"'
                          f' presetSubtype="0" fill="hold" nodeType="clickEffect">'
                            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                            f'<p:childTnLst>'
                              f'<p:set>'
                                f'<p:cBhvr>'
                                  f'<p:cTn id="{ctn_id+3}" dur="1" fill="hold">'
                                    f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                                  f'</p:cTn>'
                                  f'<p:tgtEl><p:spTgt spid="{anim_spid}"/></p:tgtEl>'
                                  f'<p:attrNameLst>'
                                    f'<p:attrName>style.visibility</p:attrName>'
                                  f'</p:attrNameLst>'
                                f'</p:cBhvr>'
                                f'<p:to><p:strVal val="visible"/></p:to>'
                              f'</p:set>'
                            f'</p:childTnLst>'
                          f'</p:cTn>'
                        f'</p:par>'
                      f'</p:childTnLst>'
                    f'</p:cTn>'
                  f'</p:par>'
                f'</p:childTnLst>'
              f'</p:cTn>'
            f'</p:par>'
        )
        ctn_id += 4

    timing_xml = (
        f'<p:timing xmlns:p="{P}" xmlns:a="{A}">'
          f'<p:tnLst>'
            f'<p:par>'
              f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
                f'<p:childTnLst>'
                  f'<p:seq concurrent="1" nextAc="seek">'
                    f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
                      f'<p:childTnLst>'
                        f'{inner_pars}'
                      f'</p:childTnLst>'
                    f'</p:cTn>'
                    f'<p:prevCondLst>'
                      f'<p:cond evt="onPrev" delay="0">'
                        f'<p:tgtEl><p:sldTgt/></p:tgtEl>'
                      f'</p:cond>'
                    f'</p:prevCondLst>'
                    f'<p:nextCondLst>'
                      f'<p:cond evt="onNext" delay="0">'
                        f'<p:tgtEl><p:sldTgt/></p:tgtEl>'
                      f'</p:cond>'
                    f'</p:nextCondLst>'
                  f'</p:seq>'
                f'</p:childTnLst>'
              f'</p:cTn>'
            f'</p:par>'
          f'</p:tnLst>'
          f'<p:bldLst>'
            + ''.join(
                f'<p:bldP spid="{s}" grpId="0" build="p"/>'
                for s in animated_spids
              ) +
          f'</p:bldLst>'
        f'</p:timing>'
    )

    timing_el = etree.fromstring(timing_xml)
    existing  = root.find(f'{{{P}}}timing')
    if existing is not None:
        root.remove(existing)
    root.append(timing_el)
    xw(tree, sp)

    anim_count = len(animated_spids)
    print(f'  [4] puzzle_pieces — {lesson_num}/{len(positions)} pieces'
          f'  ({anim_count} click-reveal animation{"s" if anim_count != 1 else ""})')
    return sp


def build_lo(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 5: Learning Objective (KS2 What, Why, How)
    Layout provides: three cloud callouts, rounded-rectangle panels, and
    static labels 'I am learning to...', 'This is so...', 'I will be successful by...'.
    Content written as explicit text boxes below each label.
    Positions from user-confirmed PPTX edit (2026-07-13).
    Font: Twinkl Cursive Looped 14pt + normAutofit.
    """
    lo_layout = REG.lo_layout_name(master_idx)
    sp, rp = fresh_geo(work, lo_layout, master_idx)

    ll    = lesson.get('learning_label', {})
    date  = lesson.get('date', lesson.get('day', ''))
    walt  = ll.get('lf', lesson.get('what', ''))
    tib   = lesson.get('why', ll.get('sc1', ''))
    isb   = lesson.get('success', ll.get('sc2', ''))

    # Strip "I am learning to " prefix -- the layout label already provides it.
    # Also strip a bare leading 'to ' when MTP what field starts 'to [verb]'.
    import re as _re_lo
    for pfx in ('I am learning to ', 'I am learning to '):
        if walt.lower().startswith(pfx.lower()):
            walt = walt[len(pfx):]
            break
    walt = _re_lo.sub(r'^to\s+', '', walt, flags=_re_lo.IGNORECASE)
    walt = walt[0].upper() + walt[1:] if walt else walt

    _fill_ph(sp, 0, date)

    # ── Explicit content text boxes below each panel label ────────────────────
    # y=4 719 286 sits below the static labels in each rounded-rectangle panel.
    # sz=1400 (14 pt) + normAutofit handles Twinkl Cursive Looped which runs
    # ~20% wider than screen render fonts, preventing bottom overflow.
    LO_BOXES = [
        (698500,   4719286, 2559050, 1698625, walt),  # panel 1 - WALT
        (4877594,  4719287, 2559050, 1698625, tib),   # panel 2 - TIB
        (9056688,  4719287, 2559050, 1698625, isb),   # panel 3 - ISB
    ]

    t, st = get_spTree(sp)
    for box_id, (bx, by, bcx, bcy, txt) in enumerate(LO_BOXES, start=501):
        sp_xml = (
            f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
            f'<p:nvSpPr>'
            f'<p:cNvPr id="{box_id}" name="LOContent{box_id}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/>'
            f'</p:nvSpPr>'
            f'<p:spPr>'
            f'<a:xfrm><a:off x="{bx}" y="{by}"/><a:ext cx="{bcx}" cy="{bcy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/>'
            f'</p:spPr>'
            f'<p:txBody>'
            f'<a:bodyPr wrap="square" anchor="t"><a:normAutofit/></a:bodyPr>'
            f'<a:lstStyle/>'
            f'<a:p><a:r>'
            f'<a:rPr lang="en-GB" sz="1400" dirty="0">'
            f'<a:latin typeface="Twinkl Cursive Looped"/>'
            f'</a:rPr>'
            f'<a:t>{ex(txt)}</a:t>'
            f'</a:r></a:p>'
            f'</p:txBody>'
            f'</p:sp>'
        )
        st.append(etree.fromstring(sp_xml))
    save(t, sp)

    # ── Animate LO boxes 501, 502, 503 on clicks 1, 2, 3 ────────────────────
    # The layout's timing (if any) only targets layout-level shapes.
    # The three content text boxes (IDs 501–503) are slide-level shapes and
    # need explicit slide timing using the same visibility-toggle pattern as
    # recap_quiz / key_vocabulary.
    lo_box_ids = [501, 502, 503]
    nid_counter = [1]
    def _nid(): v = nid_counter[0]; nid_counter[0] += 1; return str(v)

    root_id = _nid(); seq_id = _nid()
    lo_blocks = []
    for lo_bid in lo_box_ids:
        b, inn, clk, bhv = _nid(), _nid(), _nid(), _nid()
        lo_blocks.append(
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
            f'<p:tgtEl><p:spTgt spid="{lo_bid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par>'
        )

    lo_timing_xml = (
        f'<p:timing xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:tnLst><p:par><p:cTn id="{root_id}" dur="indefinite" restart="never" '
        f'nodeType="tmRoot"><p:childTnLst>'
        f'<p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="{seq_id}" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(lo_blocks)}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0">'
        f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
        f'</p:timing>'
    )

    lo_anim_tree = xr(sp)
    lo_root = lo_anim_tree.getroot()
    existing_timing = lo_root.find(f'{{{P}}}timing')
    if existing_timing is not None:
        lo_root.remove(existing_timing)
    lo_root.append(etree.fromstring(lo_timing_xml))
    xw(lo_anim_tree, sp)

    print('  [5] lo (animated)')
    return sp

def build_kwl(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 6 (Lesson 1 only): KWL — What do we know? Want to know?
    Matches the historians KWL setup: title question + 2-column table
    drawn as a native PPTX table (a:tbl).
    Layout: You Do Trio (shows activity badge, title PH + themed background).
    """
    TBL_URI = 'http://schemas.openxmlformats.org/drawingml/2006/table'

    layout_name = REG.teaching_layout('you_do_trio', master_idx)
    sp, rp = fresh_geo(work, layout_name, master_idx)

    _fill_ph(sp, 0,
             'What knowledge am I bringing to this enquiry? '
             'What would I like to find out?')

    # 2-column table dimensions (EMU, 12192000 × 6858000 slide)
    # tbl_y must clear the Hook layout's title placeholder, which renders the
    # two-line question at the layout's native font size (~2000 EMU per point).
    # 2 200 000 EMU ≈ 1.75 in gives comfortable clearance below the title.
    tbl_x  = 457200      # ~0.5 in from left
    tbl_y  = 2200000     # below title area (increased from 1 600 000)
    tbl_cx = 11277600    # ~12.4 in wide (slide width minus margins)
    tbl_cy = SH - tbl_y - 200000   # fill remaining height with a small bottom margin
    col_w  = tbl_cx // 2
    hdr_h  = 500000      # header row
    body_h = tbl_cy - hdr_h

    def _hdr_cell(text):
        return (
            f'<a:tc xmlns:a="{A}">'
            f'<a:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:r>'
            f'<a:rPr lang="en-GB" sz="2000" b="1" dirty="0">'
            f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'</a:rPr>'
            f'<a:t>{ex(text)}</a:t>'
            f'</a:r></a:p>'
            f'</a:txBody>'
            f'<a:tcPr marL="91440" marT="45720">'
            f'<a:solidFill><a:srgbClr val="1798D3"/></a:solidFill>'
            f'</a:tcPr>'
            f'</a:tc>'
        )

    def _body_cell():
        return (
            f'<a:tc xmlns:a="{A}">'
            f'<a:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'
            f'</a:txBody>'
            f'<a:tcPr marL="91440" marT="45720">'
            f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'</a:tcPr>'
            f'</a:tc>'
        )

    tbl_xml = (
        f'<p:graphicFrame xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvGraphicFramePr>'
        f'<p:cNvPr id="200" name="KWL Table"/>'
        f'<p:cNvGraphicFramePr>'
        f'<a:graphicFrameLocks noGrp="1"/>'
        f'</p:cNvGraphicFramePr>'
        f'<p:nvPr/>'
        f'</p:nvGraphicFramePr>'
        f'<p:xfrm>'
        f'<a:off x="{tbl_x}" y="{tbl_y}"/>'
        f'<a:ext cx="{tbl_cx}" cy="{tbl_cy}"/>'
        f'</p:xfrm>'
        f'<a:graphic>'
        f'<a:graphicData uri="{TBL_URI}">'
        f'<a:tbl>'
        f'<a:tblPr firstRow="1"/>'
        f'<a:tblGrid>'
        f'<a:gridCol w="{col_w}"/>'
        f'<a:gridCol w="{col_w}"/>'
        f'</a:tblGrid>'
        f'<a:tr h="{hdr_h}">'
        f'{_hdr_cell("Prior Knowledge and Skill")}'
        f'{_hdr_cell("I am curious about...")}'
        f'</a:tr>'
        f'<a:tr h="{body_h}">'
        f'{_body_cell()}'
        f'{_body_cell()}'
        f'</a:tr>'
        f'</a:tbl>'
        f'</a:graphicData>'
        f'</a:graphic>'
        f'</p:graphicFrame>'
    )

    t, st = get_spTree(sp)
    st.append(etree.fromstring(tbl_xml))
    save(t, sp)

    print('  [6] kwl')
    return sp


def build_recap_quiz(work, base_pptx, lesson, enquiry, master_idx):
    """
    Slide 6 (Lessons 2+): Recap Quiz — Q clicks in, A clicks in.
    Layout: You Do (shows activity badge, title PH idx=0 + body PH idx=1).
    Animation: each question paragraph then each answer paragraph fires on click.
    """
    layout_name = REG.teaching_layout('you_do', master_idx)
    sp, rp = fresh_geo(work, layout_name, master_idx)

    _fill_ph(sp, 0, 'Recap Quiz')

    qna = lesson.get('quiz') or []
    if not qna:
        print('  [6] recap_quiz (empty)')
        return sp

    # Build a single content shape with Q/A paragraphs and paragraph animation.
    # Each Q paragraph and each A paragraph fires on a separate click.
    content_id = 200   # fixed shape ID for the quiz content box

    # Explicit font sizes based on item count — no normAutofit.
    item_count = len(qna[:5])
    if item_count <= 4:
        qn_sz = '2000'   # 20 pt
        an_sz = '1600'   # 16 pt
    else:
        qn_sz = '1600'   # 16 pt  (5 items)
        an_sz = '1400'   # 14 pt

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
        rPr.set('lang', 'en-GB'); rPr.set('sz', qn_sz); rPr.set('dirty', '0')
        t_ = etree.SubElement(r, f'{{{A}}}t'); t_.text = text
        return p

    def _a_para(text):
        p = etree.Element(f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('marL', '457200')
        etree.SubElement(pPr, f'{{{A}}}buNone')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', an_sz)
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
        f'<p:spPr>'
        f'<a:xfrm><a:off x="246888" y="1826167"/>'
        f'<a:ext cx="11684402" cy="4900000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" anchor="t"/><a:lstStyle/></p:txBody>'
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
            endPr = etree.SubElement(spacer, f'{{{A}}}endParaRPr')
            endPr.set('lang', 'en-GB')
            endPr.set('sz', '600')   # 6pt — stops spacer inheriting 24pt master default
            endPr.set('dirty', '0')
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
    Layout: We Do (shows activity badge; PH idx=0 = title, PH idx=1 = body).
    Animation: click → word 1, click → definition 1, click → word 2, etc.
    Each word and each definition is a separate paragraph; all start hidden
    and reveal one per click using the same style.visibility pattern as
    the recap quiz.
    """
    layout_name = REG.teaching_layout('we_do', master_idx)
    sp, rp = fresh_geo(work, layout_name, master_idx)

    _fill_ph(sp, 0, 'Key Vocabulary')

    vocab = lesson.get('vocabulary', [])[:5]
    if not vocab:
        print('  [7] vocabulary (empty)')
        return sp

    content_id = 201  # fixed shape ID for the vocabulary content box

    # Explicit font sizes based on item count — more reliable than normAutofit.
    # Twinkl Cursive Looped runs ~20% wider than screen fonts; at 5 items the
    # natural height exceeds the box even with normAutofit, so we size down.
    item_count = len(vocab)
    if item_count <= 4:
        word_sz = '1800'   # 18 pt
        def_sz  = '1400'   # 14 pt
    else:
        word_sz = '1400'   # 14 pt  (5 items)
        def_sz  = '1200'   # 12 pt

    def _word_para(word):
        p = etree.Element(f'{{{A}}}p')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', word_sz); rPr.set('b', '1')
        rPr.set('dirty', '0')
        t_ = etree.SubElement(r, f'{{{A}}}t'); t_.text = word
        return p

    def _def_para(definition):
        p = etree.Element(f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('marL', '457200')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB'); rPr.set('sz', def_sz); rPr.set('dirty', '0')
        fill = etree.SubElement(rPr, f'{{{A}}}solidFill')
        clr  = etree.SubElement(fill, f'{{{A}}}srgbClr')
        clr.set('val', '1A5C2A')
        t_ = etree.SubElement(r, f'{{{A}}}t'); t_.text = definition
        return p

    sp_el = etree.fromstring(
        f'<p:sp xmlns:p="{P}" xmlns:a="{A}">'
        f'<p:nvSpPr>'
        f'<p:cNvPr id="{content_id}" name="VocabContent"/>'
        f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'<p:nvPr><p:ph idx="1"/></p:nvPr>'
        f'</p:nvSpPr>'
        f'<p:spPr>'
        f'<a:xfrm><a:off x="246888" y="1826167"/>'
        f'<a:ext cx="11684402" cy="4900000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:noFill/>'
        f'</p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" anchor="t"/><a:lstStyle/></p:txBody>'
        f'</p:sp>'
    )
    txBody = sp_el.find(f'.//{{{P}}}txBody')

    animated_para_idxs = []
    para_global = 0

    for i, item in enumerate(vocab):
        txBody.append(_word_para(item.get('word', '')))
        animated_para_idxs.append(para_global); para_global += 1
        txBody.append(_def_para(item.get('definition', '')))
        animated_para_idxs.append(para_global); para_global += 1
        if i < len(vocab) - 1:
            spacer = etree.Element(f'{{{A}}}p')
            endPr = etree.SubElement(spacer, f'{{{A}}}endParaRPr')
            endPr.set('lang', 'en-GB')
            endPr.set('sz', '600')   # 6pt — stops spacer inheriting 24pt master default
            endPr.set('dirty', '0')
            txBody.append(spacer)
            para_global += 1

    t, st = get_spTree(sp)
    st.append(sp_el)
    save(t, sp)

    # Paragraph-level click animation — same pattern as recap quiz
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

    print('  [7] vocabulary (animated)')
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

    # Embed Twinkl Cursive Looped so the PPTX carries its own font copy and
    # renders correctly on machines without the font installed.
    _twinkl_fonts = []
    for pattern in [
        '/sessions/*/mnt/Geographer/fonts/TwinklCursiveLooped-Regular.ttf',
        '/sessions/*/mnt/*/fonts/TwinklCursiveLooped-Regular.ttf',
        '/home/claude/fonts/TwinklCursiveLooped-Regular.ttf',
    ]:
        matches = glob.glob(pattern)
        if matches:
            _twinkl_fonts.append(('Twinkl Cursive Looped', matches[0]))
            break
    if _twinkl_fonts:
        embed_fonts(work, _twinkl_fonts)
    else:
        print('  NOTE: Twinkl font not found — skipping font embedding', file=sys.stderr)

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
