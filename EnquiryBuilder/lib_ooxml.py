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
import os, sys, shutil, zipfile, re, glob
from pathlib import Path
from lxml import etree

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
        dst = f'/tmp/src_{Path(pptx).stem}'; unzip(pptx, dst); _cache[k] = dst
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
             f'''  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>\n'''
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
    b = ' b="1"' if bold else ''
    nm = name or f'TextBox {sid}'
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="{ex(nm)}"/>'
              f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
              f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
              f'<p:txBody><a:bodyPr wrap="square" autofit="normAutofit"/><a:lstStyle/><a:p><a:pPr algn="{align}"/>'
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

# -- Animation (FIXED: clean <p:seq> only, no hide-at-start pars) -----------
def _anim_timing_xml(steps):
    """
    steps: list of lists of shape ids that should appear together on one click.
    Produces the pattern documented in SKILL.md as correct: clean p:seq,
    restart="never", no explicit hide-at-start block.
    """
    c = 3; par_blocks = ''
    for step in steps:
        inner = ''
        for sid in step:
            c1, c2 = c, c + 1
            inner += (f'<p:par><p:cTn id="{c1}" presetID="1" presetClass="entr" presetSubtype="0" '
                      f'fill="hold" grpId="0" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                      f'<p:childTnLst><p:set><p:cBhvr><p:cTn id="{c2}" dur="1" fill="hold"/>'
                      f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
                      f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                      f'<p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par>')
            c += 3
        oid = c; c += 1
        par_blocks += (f'<p:par><p:cTn id="{oid}" fill="hold"><p:stCondLst><p:cond evt="onBegin" delay="indefinite"/>'
                        f'</p:stCondLst><p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>')
    bld_targets = [sid for step in steps for sid in step]
    bld = ''.join(f'<p:bldP spid="{sid}" grpId="0" build="p"/>' for sid in bld_targets)
    return (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" '
            f'nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek">'
            f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{par_blocks}</p:childTnLst></p:cTn>'
            f'<p:prevCondLst><p:cond evt="onPrevClick" delay="0"/></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNextClick" delay="0"/></p:nextCondLst></p:seq></p:childTnLst></p:cTn>'
            f'</p:par></p:tnLst><p:bldLst>{bld}</p:bldLst></p:timing>')

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

def force_shrink_to_fit(s):
    """Force PowerPoint to shrink text to fit its box (normAutofit) rather
    than overflow it. Used when overriding cloned template text with content
    of unknown length going into a fixed-size template shape (e.g. concept
    cartoon speech bubbles) - the template box size is fixed and was sized
    for its own original text, not for whatever the current lesson's
    statement is."""
    bodyPr = None
    for ns in [P, A]:
        bodyPr = s.find(f'.//{{{ns}}}bodyPr')
        if bodyPr is not None: break
    if bodyPr is None: return
    for child_tag in ('spAutoFit', 'noAutofit', 'normAutofit'):
        el = bodyPr.find(f'{{{A}}}{child_tag}')
        if el is not None: bodyPr.remove(el)
    etree.SubElement(bodyPr, f'{{{A}}}normAutofit')

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
