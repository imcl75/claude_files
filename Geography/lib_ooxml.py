#!/usr/bin/env python3
"""
lib_ooxml.py - shared low-level PPTX/OOXML plumbing for the enquiry-lesson-builder.

This is the proven machinery from build_l1_final.py (T6W7 session), lifted out
and generalised so it can be reused by any subject's build script, plus fixes
for two bugs found on audit (11 July 2026):

  1. anim_body()/anim_shapes() used an explicit hide-at-start <p:par> block.
     SKILL.md's own CRITICAL RULES say this is forbidden - it produces
     "TRIGGER: UNNAMED" in PowerPoint's animation pane. Fixed to emit the
     clean <p:seq>-only pattern that SKILL.md documents as correct.
  2. Cloning was purely structural (rIds/media/layout) with no way to strip
     shapes or verify the source slide is what you think it is. Template
     files get renamed/renumbered between sessions (confirmed: this happened
     at least twice to the science templates) and a raw clone-by-index will
     silently pull in the wrong slide. Added anchor-text resolution and a
     delete_shapes() / replace_image() pair so overrides are explicit.
"""
import os, sys, shutil, zipfile, re, glob, subprocess
from pathlib import Path
from lxml import etree

# ── Font installation ─────────────────────────────────────────────────────────
# Twinkl Cursive Looped must be registered in fontconfig for LibreOffice renders
# to use it. The sandbox ~/.fonts directory is wiped on session restart, so this
# runs at import time and reinstalls from any known source it can find.
# The sandbox session path contains a UUID that changes each run, so we use
# glob patterns rather than hard-coded paths.
_TWINKL_FONT_GLOBS = [
    # Sandbox mount of the user's Geographer assets folder (session UUID varies)
    '/sessions/*/mnt/Geographer/fonts/TwinklCursive*.ttf',
    '/sessions/*/mnt/*/fonts/TwinklCursive*.ttf',
    # GitHub repo backup (if pulled by github-sync skill)
    '/home/claude/fonts/TwinklCursive*.ttf',
    # Direct macOS path (works if running outside the sandbox)
    '/Users/*/Pictures/PPTX Slide assets/*/fonts/TwinklCursive*.ttf',
]

def _ensure_fonts():
    """Install Twinkl Cursive Looped into ~/.fonts if not already registered."""
    try:
        result = subprocess.run(['fc-list'], capture_output=True, text=True)
        if 'Twinkl Cursive Looped' in result.stdout:
            return  # already registered
        font_dir = Path.home() / '.fonts'
        font_dir.mkdir(exist_ok=True)
        installed = False
        for pattern in _TWINKL_FONT_GLOBS:
            for src in glob.glob(pattern):
                shutil.copy(src, font_dir / Path(src).name)
                installed = True
        if installed:
            subprocess.run(['fc-cache', '-f', str(font_dir)],
                           capture_output=True)
    except Exception:
        pass  # never block a build over a missing font

_ensure_fonts()

A   = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P   = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R   = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
SLIDE_CT  = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
SLIDE_REL = f'{R}/slide'
IMG_REL   = f'{R}/image'
HD_REL    = 'http://schemas.microsoft.com/office/2007/relationships/hdphoto'

SW, SH = 12192000, 6858000  # slide width/height, EMU (16:9)

def xp(s): return etree.fromstring(s.encode())
def ex(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
def xr(p): return etree.parse(str(p))
def xw(t, p): t.write(str(p), xml_declaration=True, encoding='UTF-8', standalone=True)

def unzip(src, dst):
    shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
    with zipfile.ZipFile(src) as z: z.extractall(dst)

def rezip(src, dst):
    os.makedirs(Path(dst).parent, exist_ok=True)
    if os.path.exists(dst): os.remove(dst)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                full = os.path.join(root, f); z.write(full, os.path.relpath(full, src))

def next_sn(work):
    existing = {int(m.group(1)) for f in os.listdir(f'{work}/ppt/slides')
                for m in [re.match(r'slide(\d+)\.xml$', f)] if m}
    n = 1
    while n in existing: n += 1
    return n

def next_mn(work):
    md = f'{work}/ppt/media'; os.makedirs(md, exist_ok=True)
    existing = set()
    for f in os.listdir(md):
        m = re.match(r'(?:image|hdphoto)(\d+)', f.split('.')[0])
        if m: existing.add(int(m.group(1)))
    n = 1
    while n in existing: n += 1
    return n

# -- Layout name resolver -----------------------------------------------------
_work_layouts = {}

def build_layout_map(work):
    global _work_layouts; _work_layouts = {}
    for lf in glob.glob(f'{work}/ppt/slideLayouts/slideLayout*.xml'):
        t = xr(lf); r = t.getroot()
        cSld = r.find(f'{{{P}}}cSld')
        name = cSld.get('name', '') if cSld is not None else ''
        if name: _work_layouts[name] = os.path.basename(lf)

def _src_layout_name(src_dir, layout_filename):
    lp = f'{src_dir}/ppt/slideLayouts/{layout_filename}'
    if not os.path.exists(lp): return None
    t = xr(lp); r = t.getroot()
    cSld = r.find(f'{{{P}}}cSld')
    return cSld.get('name', '') if cSld is not None else None

def resolve_layout(src_dir, src_layout_file):
    """Map a source layout filename to the correct layout in the work dir, BY NAME."""
    name = _src_layout_name(src_dir, src_layout_file)
    if name and name in _work_layouts: return _work_layouts[name]
    return src_layout_file  # fallback

# -- Atomic rId replacement (single regex pass - no cascading corruption) ---
def remap_xml(xml, o2n):
    def sub(m):
        attr, rid = m.group(1), m.group(2)
        return f'{attr}="{o2n.get(rid, rid)}"'
    return re.sub(r'(r:(?:embed|id|link))="([^"]+)"', sub, xml)

# -- Slide bookkeeping --------------------------------------------------------
def clear_slides(work):
    for f in glob.glob(f'{work}/ppt/slides/slide*.xml'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/slides/_rels/slide*.xml.rels'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/notesSlides/notesSlide*.xml'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/notesSlides/_rels/notesSlide*.xml.rels'): os.remove(f)
    layout_media = set()
    for lf in glob.glob(f'{work}/ppt/slideLayouts/_rels/slideLayout*.xml.rels'):
        t = xr(lf)
        for rel in t.getroot():
            tgt = rel.get('Target', '')
            if '../media/' in tgt: layout_media.add(tgt.split('/')[-1])
    for f in glob.glob(f'{work}/ppt/media/*'):
        if os.path.basename(f) not in layout_media: os.remove(f)
    t = xr(f'{work}/ppt/presentation.xml'); r = t.getroot()
    lst = r.find(f'{{{P}}}sldIdLst')
    if lst is not None:
        for c in list(lst): lst.remove(c)
    xw(t, f'{work}/ppt/presentation.xml')
    t = xr(f'{work}/ppt/_rels/presentation.xml.rels'); r = t.getroot()
    for rel in list(r):
        typ = rel.get('Type', '')
        if 'slide' in typ.lower() and 'Layout' not in typ and 'Master' not in typ: r.remove(rel)
    xw(t, f'{work}/ppt/_rels/presentation.xml.rels')
    t = xr(f'{work}/[Content_Types].xml'); r = t.getroot()
    for el in list(r):
        pn = el.get('PartName', ''); ct = el.get('ContentType', '')
        if ct == SLIDE_CT or 'notesSlide' in pn: r.remove(el)
    xw(t, f'{work}/[Content_Types].xml')

def reg_slide(work, sn):
    prels = f'{work}/ppt/_rels/presentation.xml.rels'
    t = xr(prels); r = t.getroot()
    existing = {int(m.group(1)) for el in r for m in [re.match(r'rId(\d+)', el.get('Id', ''))] if m}
    rid_n = max(existing, default=0) + 1; new_rid = f'rId{rid_n}'
    etree.SubElement(r, 'Relationship', {'Id': new_rid, 'Type': SLIDE_REL, 'Target': f'slides/slide{sn}.xml'})
    xw(t, prels)
    pres = f'{work}/ppt/presentation.xml'; t = xr(pres); r = t.getroot()
    lst = r.find(f'{{{P}}}sldIdLst')
    if lst is None: lst = etree.SubElement(r, f'{{{P}}}sldIdLst')
    ex_ids = {int(el.get('id', 256)) for el in lst}
    new_id = max(ex_ids, default=255) + 1
    etree.SubElement(lst, f'{{{P}}}sldId', {'id': str(new_id), f'{{{R}}}id': new_rid})
    xw(t, pres)
    t = xr(f'{work}/[Content_Types].xml'); r = t.getroot()
    pname = f'/ppt/slides/slide{sn}.xml'
    if not any(el.get('PartName') == pname for el in r):
        etree.SubElement(r, f'{{{CT_NS}}}Override', {'PartName': pname, 'ContentType': SLIDE_CT})
    xw(t, f'{work}/[Content_Types].xml')

# -- Source cache --------------------------------------------------------------
_cache = {}
def src_dir(pptx):
    k = str(pptx)
    if k not in _cache:
        dst = f'/tmp/src_{os.getpid()}_{Path(pptx).stem}'; unzip(pptx, dst); _cache[k] = dst
    return _cache[k]

def _slide_text(sd, sn):
    sp = f'{sd}/ppt/slides/slide{sn}.xml'
    if not os.path.exists(sp): return ''
    with open(sp, encoding='utf-8') as f: xml = f.read()
    return ' '.join(re.findall(r'<a:t>(.*?)</a:t>', xml, re.S))

def find_slide_by_anchor(pptx, anchor_text, hint=None):
    """
    Resolve a slide number by searching for anchor_text in the source deck's
    slide text, rather than trusting a hardcoded index. Template files have
    already drifted (renamed/renumbered) at least twice - this is the defence.
    Tries hint first (fast path); if it doesn't contain the anchor, searches
    every slide and warns loudly if the hint was wrong or nothing matched.
    """
    sd = src_dir(pptx)
    n_slides = len(glob.glob(f'{sd}/ppt/slides/slide*.xml'))
    if hint and anchor_text.lower() in _slide_text(sd, hint).lower():
        return hint
    for n in range(1, n_slides + 1):
        if anchor_text.lower() in _slide_text(sd, n).lower():
            if hint and n != hint:
                print(f"    WARNING: template drift in {Path(pptx).name} - "
                      f"anchor '{anchor_text[:40]}' expected at slide {hint}, found at slide {n}. "
                      f"Using {n}.", file=sys.stderr)
            return n
    raise RuntimeError(f"Anchor text '{anchor_text[:60]}' not found in any slide of {pptx}")

# -- Clone (atomic rId remap + name-based layout resolution) ----------------
def clone(work, pptx, sn, copy_hdphoto=True):
    sd = src_dir(pptx)
    slide_path = f'{sd}/ppt/slides/slide{sn}.xml'
    rels_path  = f'{sd}/ppt/slides/_rels/slide{sn}.xml.rels'
    with open(slide_path, encoding='utf-8') as f: slide_xml = f.read()
    rt = xr(rels_path); rr = rt.getroot()
    md = Path(work) / 'ppt' / 'media'; md.mkdir(exist_ok=True)
    os.makedirs(f'{work}/ppt/diagrams', exist_ok=True)
    os.makedirs(f'{work}/ppt/notesSlides/_rels', exist_ok=True)
    new_sn = next_sn(work); o2n = {}; entries = []; rn = 1

    for rel in rr:
        typ = rel.get('Type', ''); tgt = rel.get('Target', ''); oid = rel.get('Id', '')
        if f'{R}/slideLayout' in typ:
            lf = tgt.split('/')[-1]
            resolved = resolve_layout(sd, lf)
            entries.append((f'rId{rn}', typ, f'../slideLayouts/{resolved}'))
            o2n[oid] = f'rId{rn}'; rn += 1
        elif f'{R}/image' in typ or (HD_REL in typ and copy_hdphoto):
            for c in [f'{sd}/ppt/slides/{tgt}', f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    extn = Path(c).suffix.lower(); n = next_mn(work)
                    pfx = 'hdphoto' if extn == '.wdp' else 'image'
                    nm = f'{pfx}{n}{extn}'; shutil.copy(c, md / nm)
                    entries.append((f'rId{rn}', typ, f'../media/{nm}'))
                    o2n[oid] = f'rId{rn}'; rn += 1; break
        elif any(dt in typ for dt in ['diagramData', 'diagramLayout', 'diagramColors', 'diagramQuickStyle', 'diagramDrawing']):
            for c in [f'{sd}/ppt/slides/{tgt}', f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    orig = Path(c).name; dst = f'{work}/ppt/diagrams/{orig}'
                    if not os.path.exists(dst): shutil.copy(c, dst)
                    ct = xr(f'{work}/[Content_Types].xml'); cr = ct.getroot()
                    pn = f'/ppt/diagrams/{orig}'
                    if not any(el.get('PartName') == pn for el in cr):
                        cm = {'data': 'diagramData+xml', 'layout': 'diagramLayout+xml', 'colors': 'diagramColors+xml',
                              'quickStyle': 'diagramStyle+xml', 'drawing': 'diagramDrawing+xml'}
                        sfx = next((v for k, v in cm.items() if k in orig), 'xml')
                        base = 'application/vnd.openxmlformats-officedocument.drawingml.'
                        etree.SubElement(cr, f'{{{CT_NS}}}Override', {'PartName': pn, 'ContentType': base + sfx})
                    xw(ct, f'{work}/[Content_Types].xml')
                    entries.append((f'rId{rn}', typ, f'../diagrams/{orig}'))
                    o2n[oid] = f'rId{rn}'; rn += 1; break
        elif f'{R}/notesSlide' in typ:
            for c in [f'{sd}/ppt/slides/{tgt}', f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    nn = f'notesSlide{new_sn}.xml'
                    shutil.copy(c, f'{work}/ppt/notesSlides/{nn}')
                    nr = (f'''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n'''
                          f'''<Relationships xmlns="{PKG}">\n'''
                          f'''  <Relationship Id="rId1" Type="{R}/slide" Target="../slides/slide{new_sn}.xml"/>\n'''
                          f'''  <Relationship Id="rId2" Type="{R}/notesMaster" Target="../notesMasters/notesMaster1.xml"/>\n'''
                          f'''</Relationships>''')
                    with open(f'{work}/ppt/notesSlides/_rels/{nn}.rels', 'w') as f2: f2.write(nr)
                    ct = xr(f'{work}/[Content_Types].xml'); cr = ct.getroot()
                    pn = f'/ppt/notesSlides/{nn}'
                    ns_ct = 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
                    if not any(el.get('PartName') == pn for el in cr):
                        etree.SubElement(cr, f'{{{CT_NS}}}Override', {'PartName': pn, 'ContentType': ns_ct})
                    xw(ct, f'{work}/[Content_Types].xml')
                    entries.append((f'rId{rn}', typ, f'../notesSlides/{nn}'))
                    o2n[oid] = f'rId{rn}'; rn += 1; break

    rels_xml = f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<Relationships xmlns=\"{PKG}\">"
    for rid, typ2, tgt2 in entries:
        rels_xml += f'\n  <Relationship Id="{rid}" Type="{typ2}" Target="{tgt2}"/>'
    rels_xml += '\n</Relationships>'

    slide_xml = remap_xml(slide_xml, o2n)  # ATOMIC - single regex pass

    sp = f'{work}/ppt/slides/slide{new_sn}.xml'
    rp = f'{work}/ppt/slides/_rels/slide{new_sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels', exist_ok=True)
    with open(sp, 'w', encoding='utf-8') as f: f.write(slide_xml)
    with open(rp, 'w', encoding='utf-8') as f: f.write(rels_xml)
    reg_slide(work, new_sn)
    return sp, rp

def fresh(work, layout_name):
    # Round 11 (11 Jul 2026): the clrMapOvr below used to write
    # <a:masterClr/>, which is not a real OOXML element - the correct
    # empty element for "use the master's own colour map" is
    # <a:masterClrMapping/> (confirmed correct by its use, unmodified,
    # in every slideLayout and notesSlide in this same package). Found
    # via a normalised diff against Innes's own PowerPoint-repaired
    # file on wedo_hook/youdo_task/ido_diagram slides (every slide this
    # function builds), which showed PowerPoint's repair silently
    # rewriting <a:masterClr/> to <a:masterClrMapping/> on every one -
    # a strong sign PowerPoint's schema validation was rejecting the
    # original element outright, not just disagreeing with a value.
    if layout_name not in _work_layouts:
        raise KeyError(f"Layout '{layout_name}' not found in work presentation. "
                        f"Known layouts: {sorted(_work_layouts)}")
    lf = _work_layouts[layout_name]; sn = next_sn(work)
    slide = (f'''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n'''
             f'''<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">\n'''
             f'''  <p:cSld><p:spTree>\n'''
             f'''    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'''
             f'''    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n'''
             f'''  </p:spTree></p:cSld>\n'''
             f'''  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n'''
             f'''</p:sld>''')
    rels = (f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<Relationships xmlns=\"{PKG}\">\n"
            f"  <Relationship Id=\"rId1\" Type=\"{R}/slideLayout\" Target=\"../slideLayouts/{lf}\"/>\n</Relationships>")
    sp = f'{work}/ppt/slides/slide{sn}.xml'; rp = f'{work}/ppt/slides/_rels/slide{sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels', exist_ok=True)
    with open(sp, 'w', encoding='utf-8') as f: f.write(slide)
    with open(rp, 'w', encoding='utf-8') as f: f.write(rels)
    reg_slide(work, sn)
    return sp, rp

def get_spTree(sp):
    t = xr(sp); st = t.getroot().find(f'.//{{{P}}}spTree'); return t, st

def save(t, sp): xw(t, sp)

# -- Content builders (fixed geometry passed in explicitly) -----------------
def title_sp(sid, text, font, bold=False):
    b = ' b="1"' if bold else ''
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="Title {sid}"/>'
              f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
              f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-GB"{b} dirty="0">'
              f'<a:latin typeface="{font}" panose="02000000000000000000" pitchFamily="2" charset="77"/></a:rPr>'
              f'<a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>')

def body_sp(sid, bullets, sz=2200):
    paras = ''.join(f'<a:p><a:r><a:rPr lang="en-GB" sz="{sz}" dirty="0"/><a:t>{ex(b)}</a:t></a:r></a:p>' for b in bullets)
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="Content Placeholder {sid}"/>'
              f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph idx="1"/></p:nvPr></p:nvSpPr>'
              f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>')

def tbox(sid, text, x, y, cx, cy, sz=1800, bold=False, color='1A3A5C', align='l', name=None):
    # Round 11 (11 Jul 2026): bodyPr used to carry an attribute
    # autofit="normAutofit" - there is no such attribute in the OOXML
    # schema for CT_TextBodyProperties; autofit is only ever expressed
    # via a child element (<a:normAutofit/>, <a:noAutofit/> or
    # <a:spAutoFit/>). Found the same way as the masterClr bug above -
    # PowerPoint's own repair silently stripped the attribute entirely
    # on every affected slide rather than reinterpreting it.
    b = ' b="1"' if bold else ''
    nm = name or f'TextBox {sid}'
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="{ex(nm)}"/>'
              f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
              f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
              f'<p:txBody><a:bodyPr wrap="square"><a:normAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="{align}"/>'
              f'<a:r><a:rPr lang="en-GB" sz="{sz}"{b} dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr>'
              f'<a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>')

def add_img(sp, rp, work, img_path, x, y, mw, mh, sid):
    """Place an image inside box (x,y,mw,mh), preserving aspect ratio and centring."""
    from PIL import Image as PILImage
    img = PILImage.open(img_path); iw, ih = img.size
    sc = min(mw / iw, mh / ih); w = int(iw * sc); h = int(ih * sc)
    cx = x + (mw - w) // 2; cy = y + (mh - h) // 2
    n = next_mn(work); extn = Path(img_path).suffix.lower(); nm = f'image{n}{extn}'
    md = Path(work) / 'ppt' / 'media'; md.mkdir(exist_ok=True); shutil.copy(img_path, md / nm)
    rt = xr(rp); rr = rt.getroot()
    ex_rids = {int(m.group(1)) for el in rr for m in [re.match(r'rId(\d+)', el.get('Id', ''))] if m}
    rn = max(ex_rids, default=0) + 1; rid = f'rId{rn}'
    etree.SubElement(rr, 'Relationship', {'Id': rid, 'Type': IMG_REL, 'Target': f'../media/{nm}'})
    rt.write(rp, xml_declaration=True, encoding='UTF-8', standalone=True)
    st = xr(sp); spTree = st.getroot().find(f'.//{{{P}}}spTree')
    spTree.append(xp(f'<p:pic xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:nvPicPr>'
                      f'<p:cNvPr id="{sid}" name="Picture {sid}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
                      f'<p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
                      f'<p:spPr><a:xfrm><a:off x="{cx}" y="{cy}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
                      f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'))
    st.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)

def grid_geometry(n_cols, n_rows, margin_x=150000, top_y=1750000, label_h=400000, bottom_pad=80000):
    """Return list of (cell_x, cell_y, cell_w, cell_h, image_w, image_h, label_h)
    for an n_cols x n_rows grid inside the slide, non-overlapping by construction."""
    tw = SW - 2 * margin_x; th = SH - top_y - bottom_pad
    cw = tw // n_cols; ch = th // n_rows
    iw = cw - 80000; ih = ch - label_h - 60000
    cells = []
    for i in range(n_cols * n_rows):
        row, col = divmod(i, n_cols)
        cx = margin_x + col * cw; cy = top_y + row * ch
        cells.append((cx, cy, cw, ch, iw, ih, label_h))
    return cells

# -- Animation (matches native PowerPoint output exactly - see Round 7) -----
def _anim_timing_xml(steps):
    """
    steps: list of lists of shape ids that should appear together on one
    click. Within a step, the FIRST shape id is the one that triggers the
    click (nodeType="clickEffect"); any further shape ids in the same step
    ride along simultaneously without needing their own click
    (nodeType="withEffect") - this is PowerPoint's own "Start: With
    Previous" behaviour applied to a second/third shape in the same build
    step, e.g. a speech bubble and a "Learner A" label appearing together
    with the avatar picture that triggers them.

    Round 7 (11 Jul 2026) rewrote this against ground truth for the simple
    single-shape-per-step case and confirmed a byte-exact match. Round 8
    extended it to multi-shape steps after discovering (again from ground
    truth, this time checked exhaustively with .findall() instead of
    .find() - the earlier single-shape check silently missed that half of
    real animated slides use this) that several slides pair a withEffect
    shape with the clickEffect one. Structurally a multi-shape step was
    already nested correctly by this function before this change (all
    shapes in one step already shared one middle wrapper, so timing/click
    grouping was already right) - the only fix needed was tagging shapes
    after the first as nodeType="withEffect" instead of "clickEffect", to
    match what PowerPoint itself writes.
    """
    c = 3; outer_pars = ''; bld_entries = ''
    for step in steps:
        outer_id = c; c += 1
        middle_id = c; c += 1
        inner = ''
        for idx, sid in enumerate(step):
            node_type = 'clickEffect' if idx == 0 else 'withEffect'
            click_id, cbhvr_id = c, c + 1
            inner += (f'<p:par><p:cTn id="{click_id}" presetID="1" presetClass="entr" presetSubtype="0" '
                      f'fill="hold" grpId="0" nodeType="{node_type}"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                      f'<p:childTnLst><p:set><p:cBhvr><p:cTn id="{cbhvr_id}" dur="1" fill="hold">'
                      f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                      f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
                      f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                      f'<p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par>')
            bld_entries += f'<p:bldP spid="{sid}" grpId="0"/>'
            c += 2
        middle = (f'<p:par><p:cTn id="{middle_id}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                  f'<p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>')
        outer_pars += (f'<p:par><p:cTn id="{outer_id}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
                        f'</p:stCondLst><p:childTnLst>{middle}</p:childTnLst></p:cTn></p:par>')
    return (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" '
            f'nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek">'
            f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{outer_pars}</p:childTnLst></p:cTn>'
            f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
            f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
            f'<p:bldLst>{bld_entries}</p:bldLst></p:timing>')

def animate(sp, steps):
    """steps: list of lists of shape-ids, one list per click."""
    st = xr(sp); root = st.getroot()
    for el in list(root):
        if el.tag == f'{{{P}}}timing': root.remove(el)
    root.append(xp(_anim_timing_xml(steps)))
    xw(st, sp)

# -- Shape lookup / text editing / deletion ----------------------------------
def find_sp(tree, name):
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            if el.get('name') == name: return s
    return None

def find_all_sp(tree, name):
    out = []
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            if el.get('name') == name: out.append(s); break
    return out

def get_sp_id(tree, name):
    s = find_sp(tree, name)
    if s is None: return None
    c = s.find(f'.//{{{P}}}cNvPr'); return int(c.get('id', 0)) if c is not None else None

def get_shape_id_by_name(tree, name):
    """Resolve a cNvPr id by shape name across ANY container type (sp, pic,
    grpSp, graphicFrame) - get_sp_id()/find_sp() only search <p:sp> and miss
    grouped shapes entirely, which matters for e.g. the discipline wheel's
    <p:grpSp> elements (Round 8, 11 Jul 2026)."""
    root = tree.getroot()
    for el in root.iter():
        tag = etree.QName(el).localname
        if tag not in ('sp', 'pic', 'grpSp', 'graphicFrame'): continue
        for nv_path in (f'{{{P}}}nvSpPr/{{{P}}}cNvPr', f'{{{P}}}nvPicPr/{{{P}}}cNvPr',
                         f'{{{P}}}nvGrpSpPr/{{{P}}}cNvPr', f'{{{P}}}nvGraphicFramePr/{{{P}}}cNvPr'):
            nv = el.find(nv_path)
            if nv is not None:
                if nv.get('name') == name: return int(nv.get('id'))
                break
    return None

def set_text(s, text):
    tb = None
    for ns in [P, A]:
        tb = s.find(f'.//{{{ns}}}txBody')
        if tb is not None: break
    if tb is None: return
    paras = tb.findall(f'{{{A}}}p')
    if not paras: return
    fp = paras[0]; runs = fp.findall(f'{{{A}}}r')
    rpr = runs[0].find(f'{{{A}}}rPr') if runs else None
    for r in list(fp.findall(f'{{{A}}}r')): fp.remove(r)
    for br in list(fp.findall(f'{{{A}}}br')): fp.remove(br)
    for pp in paras[1:]: tb.remove(pp)
    for i, line in enumerate(text.split('\n')):
        p = fp if i == 0 else etree.SubElement(tb, f'{{{A}}}p')
        if i > 0 and rpr is not None:
            pp2 = fp.find(f'{{{A}}}pPr')
            if pp2 is not None: p.append(etree.fromstring(etree.tostring(pp2)))
        nr = etree.SubElement(p, f'{{{A}}}r')
        if rpr is not None: nr.append(etree.fromstring(etree.tostring(rpr)))
        t = etree.SubElement(nr, f'{{{A}}}t'); t.text = line

def delete_shapes_by_id(sp, ids_to_remove):
    """Remove shapes (by cNvPr id) from a cloned slide. Used to strip stale
    duplicate content - e.g. the LO slide carries two complete, pixel-identical
    overlapping panels; only one should survive into a delivered lesson."""
    t = xr(sp); root = t.getroot()
    removed = 0
    for el in list(root.iter()):
        if el.tag.endswith('}cNvPr') and int(el.get('id', -1)) in ids_to_remove:
            node = el
            while node is not None and node.tag not in (f'{{{P}}}sp', f'{{{P}}}pic', f'{{{P}}}grpSp', f'{{{P}}}graphicFrame'):
                node = node.getparent()
            if node is not None and node.getparent() is not None:
                node.getparent().remove(node); removed += 1
    xw(t, sp)
    return removed

def replace_image(sp, rp, work, pic_shape_id, new_image_path):
    """Swap the embedded image of an existing <p:pic> (by shape id) for a new
    file, keeping its position/size."""
    t = xr(sp); root = t.getroot()
    target_pic = None
    for pic in root.iter(f'{{{P}}}pic'):
        cNvPr = pic.find(f'.//{{{P}}}cNvPr')
        if cNvPr is not None and int(cNvPr.get('id', -1)) == pic_shape_id:
            target_pic = pic; break
    if target_pic is None:
        raise RuntimeError(f'replace_image: no <p:pic> with id={pic_shape_id} on {sp}')
    blip = target_pic.find(f'.//{{{A}}}blip')
    old_rid = blip.get(f'{{{R}}}embed')
    n = next_mn(work); extn = Path(new_image_path).suffix.lower(); nm = f'image{n}{extn}'
    md = Path(work) / 'ppt' / 'media'; md.mkdir(exist_ok=True); shutil.copy(new_image_path, md / nm)
    rt = xr(rp); rr = rt.getroot()
    for rel in rr:
        if rel.get('Id') == old_rid:
            rel.set('Target', f'../media/{nm}')
    xw(rt, rp)
    xw(t, sp)

def delete_shape_by_name(sp, name):
    """Remove a shape by its cNvPr name (e.g. a stray editor note left in a
    template, such as 'Insert any other states of being icons for the whole
    enquiry' found on the Being a Scientist slide)."""
    t = xr(sp); root = t.getroot()
    removed = 0
    for el in list(root.iter()):
        if el.tag.endswith('}cNvPr') and el.get('name') == name:
            node = el
            while node is not None and node.tag not in (f'{{{P}}}sp', f'{{{P}}}pic', f'{{{P}}}grpSp', f'{{{P}}}graphicFrame'):
                node = node.getparent()
            if node is not None and node.getparent() is not None:
                node.getparent().remove(node); removed += 1
    xw(t, sp)
    return removed

def find_pic_id_by_name(tree, name):
    for pic in tree.iter(f'{{{P}}}pic'):
        cNvPr = pic.find(f'.//{{{P}}}cNvPr')
        if cNvPr is not None and cNvPr.get('name') == name:
            return int(cNvPr.get('id'))
    return None

def _wrap_line_count(text, chars_per_line):
    """Word-wrap text at chars_per_line and return the number of lines -
    used to estimate whether a given font size will fit a box, without a
    real text-measurement engine."""
    words = text.split()
    if not words: return 1
    lines = 1; cur = 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur + add > chars_per_line and cur > 0:
            lines += 1; cur = len(w)
        else:
            cur += add
    return lines

def force_shrink_to_fit(s, min_sz=1400, step=100):
    """Shrink text to actually fit its box, computed directly rather than
    left for PowerPoint to resolve at open time.
    Found via the T6W7 crash-fix session: an earlier version of this
    function only added an empty <a:normAutofit/> with no fontScale set,
    which asks PowerPoint to auto-shrink but supplies no computed shrink
    percentage - LibreOffice happened to lay it out without visible overflow
    when rendered for QA, but real PowerPoint trusts the stored (absent)
    scale and left the text overflowing the box edges, confirmed by a
    screenshot of the concept cartoon slide with text spilling across
    neighbouring shapes. Fixed by computing an explicit font size here
    (word-wrap heuristic against the shape's actual box width/height) and
    writing it onto every run directly, so the fit does not depend on the
    renderer recalculating anything. normAutofit is left present (empty,
    no fontScale) purely so PowerPoint's own live-editing auto-shrink can
    still kick in if Innes later retypes the text by hand.

    Round 11 (11 Jul 2026) correction: this function used to also set
    fontScale on the normAutofit element, computed as sz/start_sz. That
    was wrong - rPr/sz above is already the final, fitting size, and
    PowerPoint renders text at sz * fontScale, not sz alone. Setting both
    meant the shrink was applied twice: a shape whose fitting size was
    correctly computed as 18pt (down from a 28pt template default) was
    ALSO scaled by the 18/28 ratio again at render time, displaying at
    ~11.5pt (PowerPoint's UI rounds this to size 12) even though the box
    had visible room for something closer to 20pt. Confirmed on all three
    concept-cartoon speech bubbles in T6W7 L1, all showing sz=1800 with
    fontScale=64286 (=1800/2800), i.e. the same double shrink on every
    one. Fix: never set fontScale - rPr/sz alone carries the computed
    size, and an unscaled normAutofit is enough to enable live-editing
    autofit without re-applying a shrink that's already baked in."""
    spPr = s.find(f'{{{P}}}spPr')
    xfrm = spPr.find(f'{{{A}}}xfrm') if spPr is not None else None
    ext = xfrm.find(f'{{{A}}}ext') if xfrm is not None else None
    if ext is None: return  # no geometry to compute against - leave as-is
    box_w_emu = int(ext.get('cx')); box_h_emu = int(ext.get('cy'))
    EMU_PER_PT = 12700
    inset_pt = 14  # PowerPoint's default text box inset is 0.1in each side ~= 7.2pt; use a slightly
                   # more conservative figure since speech-bubble shapes carry extra internal padding
    usable_w_pt = max(10, box_w_emu / EMU_PER_PT - 2 * inset_pt)
    usable_h_pt = max(10, box_h_emu / EMU_PER_PT - 2 * inset_pt)

    tb = None
    for ns in [P, A]:
        tb = s.find(f'.//{{{ns}}}txBody')
        if tb is not None: break
    if tb is None: return
    runs = tb.findall(f'.//{{{A}}}r')
    if not runs: return
    text = ''.join(r.find(f'{{{A}}}t').text or '' for r in runs if r.find(f'{{{A}}}t') is not None)
    first_rpr = runs[0].find(f'{{{A}}}rPr')
    start_sz = int(first_rpr.get('sz', '1800')) if first_rpr is not None else 1800

    sz = start_sz
    while sz > min_sz:
        font_pt = sz / 100
        chars_per_line = max(1, int(usable_w_pt / (font_pt * 0.52)))
        lines = _wrap_line_count(text, chars_per_line)
        line_height_pt = font_pt * 1.2
        if lines * line_height_pt <= usable_h_pt:
            break
        sz -= step
    sz = max(sz, min_sz)

    for r in runs:
        rpr = r.find(f'{{{A}}}rPr')
        if rpr is not None:
            rpr.set('sz', str(sz))

    bodyPr = None
    for ns in [P, A]:
        bodyPr = s.find(f'.//{{{ns}}}bodyPr')
        if bodyPr is not None: break
    if bodyPr is not None:
        for child_tag in ('spAutoFit', 'noAutofit', 'normAutofit'):
            el = bodyPr.find(f'{{{A}}}{child_tag}')
            if el is not None: bodyPr.remove(el)
        etree.SubElement(bodyPr, f'{{{A}}}normAutofit')
        # No fontScale here - rPr/sz (set above) already IS the fitting
        # size. Setting fontScale too would scale that already-fitting
        # size down again at render time. See Round 11 note above.

def strip_orphaned_media(work):
    """Remove any file in ppt/media/ that no relationship anywhere in the
    package actually points to. Found via the T6W7 repair investigation:
    replace_image() swaps a <p:pic>'s embedded image by re-pointing its
    relationship Target at a new file, but never deleted the old one - so a
    replaced template image (in one case, the exact banned concept-cartoon
    cat photo) was still physically sitting in the delivered file, just
    unreferenced. Harmless to PowerPoint on its own, but it's dead weight
    and, worse, means content that was supposed to be fully replaced is
    still technically present in the archive. Run this as the last step
    before rezip."""
    referenced = set()
    for root_dir, _, files in os.walk(work):
        for f in files:
            if not f.endswith('.rels'): continue
            path = os.path.join(root_dir, f)
            with open(path, encoding='utf-8') as fh:
                content = fh.read()
            for m in re.finditer(r'Target="([^"]+)"', content):
                tgt = m.group(1)
                if tgt.startswith('http') or tgt.startswith('#'): continue
                # resolve relative to the part's own directory (parent of _rels/)
                part_dir = os.path.dirname(os.path.dirname(path))
                resolved = os.path.normpath(os.path.join(part_dir, tgt))
                referenced.add(resolved)
    media_dir = os.path.join(work, 'ppt', 'media')
    removed = []
    if os.path.isdir(media_dir):
        for f in os.listdir(media_dir):
            full = os.path.normpath(os.path.join(media_dir, f))
            if full not in referenced:
                os.remove(full)
                removed.append(f)
    return removed

def clamp_callout_tail(sp, shape_name, max_abs=30000):
    """wedgeRoundRectCallout shapes (speech bubbles) point their tail via
    adj1/adj2 (roughly -100000..100000, permille of shape width/height from
    centre). The concept cartoon template's bubbles were authored with very
    large adj1 offsets (confirmed: -56873, -3351, -65727 across the three
    bubbles) so the tail reaches a long way across the bubble toward its
    character - on the two bubbles with large offsets, that reach is long
    enough to visually cross the text in some renderers. Never touched by
    set_text(), so this is template geometry, not build-introduced - but
    clamping the reach is a cheap defensive fix that removes the risk
    regardless of which renderer is displaying it."""
    t = xr(sp); root = t.getroot()
    for s in root.iter(f'{{{P}}}sp'):
        cNvPr = s.find(f'.//{{{P}}}cNvPr')
        if cNvPr is None or cNvPr.get('name') != shape_name: continue
        for gd in s.iter(f'{{{A}}}gd'):
            if gd.get('name') != 'adj1': continue
            m = re.match(r'val (-?\d+)', gd.get('fmla', ''))
            if not m: continue
            v = int(m.group(1))
            clamped = max(-max_abs, min(max_abs, v))
            if clamped != v:
                gd.set('fmla', f'val {clamped}')
    xw(t, sp)

def strip_timing(sp):
    """Remove any pre-existing <p:timing> from a cloned slide. Found via the
    T6W7 investigation: the discipline slides in Being_a_Scientist_slide_
    deck.pptx carry a pre-existing animation with 11 clickEffect blocks
    against 37 spTgt targets - a mismatch that was already broken in the
    source artwork, independent of anything this skill builds. A malformed
    animation is worse than no animation, so clone_discipline (and any other
    clone_verbatim source found to have the same problem) strips it rather
    than deliver broken click behaviour."""
    t = xr(sp); root = t.getroot()
    removed = False
    for el in list(root):
        if el.tag == f'{{{P}}}timing':
            root.remove(el); removed = True
    if removed:
        xw(t, sp)
    return removed

def extract_image_by_shape_name(pptx_path, slide_number, shape_name, dest_path):
    """Pull a single embedded image out of a specific slide by shape name and
    write it to dest_path. Used to reuse a generic icon (e.g. the scientist
    magnifying-glass icon) that lives on one template slide onto a
    differently-sourced slide, without cloning the whole donor slide."""
    sd = src_dir(pptx_path)
    sp = f'{sd}/ppt/slides/slide{slide_number}.xml'
    rp = f'{sd}/ppt/slides/_rels/slide{slide_number}.xml.rels'
    tree = xr(sp); root = tree.getroot()
    rels = xr(rp).getroot()
    rid_to_target = {rel.get('Id'): rel.get('Target') for rel in rels}
    for pic in root.iter(f'{{{P}}}pic'):
        cNvPr = pic.find(f'.//{{{P}}}cNvPr')
        if cNvPr is None or cNvPr.get('name') != shape_name: continue
        blip = pic.find(f'.//{{{A}}}blip')
        rid = blip.get(f'{{{R}}}embed')
        target = rid_to_target[rid]
        src_media = os.path.normpath(os.path.join(sd, 'ppt', 'slides', target))
        shutil.copy(src_media, dest_path)
        return dest_path
    raise RuntimeError(f"extract_image_by_shape_name: shape '{shape_name}' not found on slide {slide_number} of {pptx_path}")


# ── Font embedding ─────────────────────────────────────────────────────────────

FONT_REL = f'{R}/font'
_ODTTF_CT = 'application/vnd.openxmlformats-officedocument.obfuscatedFont'

def _guid_to_key(guid_str):
    """Convert a GUID like '{37D0410B-CB06-4AF0-9B29-5C09E60A5021}' to a 16-byte
    obfuscation key following the OOXML mixed-endian (COM GUID) byte order."""
    import struct, uuid as _uuid
    clean = guid_str.strip('{}').replace('-', '')
    u = _uuid.UUID(clean)
    # COM/Windows GUID byte order: first three fields are little-endian,
    # last two fields are big-endian.
    key = struct.pack('<IHH', u.time_low, u.time_mid, u.time_hi_version) + u.bytes[8:]
    return key


def _obfuscate_font(font_data, key):
    """XOR the first 32 bytes of font_data with key (16 bytes), repeated twice."""
    ba = bytearray(font_data)
    for i in range(min(32, len(ba))):
        ba[i] ^= key[i % 16]
    return bytes(ba)


def embed_fonts(work, font_files):
    """Embed fonts into an unpacked PPTX working directory.

    font_files: list of (typeface_name, font_path) tuples.
    Embeds each font with OOXML obfuscation (ECMA-376 §22.5).
    Call this after all slides are built, before rezip().
    """
    import uuid as _uuid
    pres_path      = Path(work) / 'ppt' / 'presentation.xml'
    pres_rels_path = Path(work) / 'ppt' / '_rels' / 'presentation.xml.rels'
    ct_path        = Path(work) / '[Content_Types].xml'
    fonts_dir      = Path(work) / 'ppt' / 'fonts'
    fonts_dir.mkdir(exist_ok=True)

    # -- presentation.xml.rels ------------------------------------------------
    rels_tree = xr(pres_rels_path)
    rels_root = rels_tree.getroot()
    max_rid = max(
        (int(m.group(1)) for el in rels_root
         for m in [re.match(r'rId(\d+)', el.get('Id', ''))] if m),
        default=0
    )

    # -- presentation.xml: find or create <p:embeddedFontLst> -----------------
    pres_tree = xr(pres_path)
    pres_root = pres_tree.getroot()
    efl = pres_root.find(f'{{{P}}}embeddedFontLst')
    if efl is None:
        # Insert before <p:extLst> if present, otherwise append
        extlst = pres_root.find(f'{{{P}}}extLst')
        if extlst is not None:
            idx = list(pres_root).index(extlst)
            efl = etree.Element(f'{{{P}}}embeddedFontLst')
            pres_root.insert(idx, efl)
        else:
            efl = etree.SubElement(pres_root, f'{{{P}}}embeddedFontLst')

    # -- [Content_Types].xml: add odttf default if absent ---------------------
    ct_tree = xr(ct_path)
    ct_root = ct_tree.getroot()
    if not any(el.get('Extension') == 'odttf' for el in ct_root):
        etree.SubElement(ct_root, f'{{{CT_NS}}}Default',
                         {'Extension': 'odttf', 'ContentType': _ODTTF_CT})
    xw(ct_tree, ct_path)

    # -- Embed each font ------------------------------------------------------
    for i, (typeface, font_path) in enumerate(font_files):
        font_path = Path(font_path)
        if not font_path.exists():
            print(f'  WARNING: font not found, skipping: {font_path}', file=sys.stderr)
            continue

        font_data = font_path.read_bytes()
        guid = '{' + str(_uuid.uuid4()).upper() + '}'
        key  = _guid_to_key(guid)
        obf  = _obfuscate_font(font_data, key)

        out_name = f'font{i + 1}.odttf'
        (fonts_dir / out_name).write_bytes(obf)

        rid = f'rId{max_rid + 1 + i}'
        etree.SubElement(rels_root, 'Relationship', {
            'Id': rid,
            'Type': FONT_REL,
            'Target': f'fonts/{out_name}',
        })

        ef_xml = (
            f'<p:embeddedFont xmlns:p="{P}" xmlns:r="{R}">'
            f'<p:font typeface="{ex(typeface)}" panose="020B0502050000060200"'
            f' pitchFamily="34" charset="0"/>'
            f'<p:regular r:id="{rid}"/>'
            f'</p:embeddedFont>'
        )
        efl.append(etree.fromstring(ef_xml))
        print(f'  [font] embedded "{typeface}" → {out_name} ({len(obf):,} bytes)')

    xw(rels_tree, pres_rels_path)
    xw(pres_tree,  pres_path)
