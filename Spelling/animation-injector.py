# SKILL VERSION: 2026-04-07-v4
"""
add_animation.py  — inject click animations into spelling_shed_slides_v2.pptx
Rebuilt from Innes's exact PowerPoint-generated timing XML structure.
"""
import zipfile, shutil, os, re

# ── File paths from lesson.json ───────────────────────────────────────────────
import json as _json
with open("/home/claude/lesson.json") as _f:
    _code = _json.load(_f).get("code", "XX")
SRC   = f"/home/claude/spelling_shed_slides_{_code}.pptx"
DEST  = f"/home/claude/spelling_shed_slides_{_code}_tmp.pptx"
_FINAL = SRC  # overwrite in place after processing

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'

# ── XML builders ──────────────────────────────────────────────────────────────

def make_timing(groups):
    """Build click-reveal timing XML matching the exact working format.
    
    Key structure (copied from confirmed working file):
    - ONE <p:seq nodeType="mainSeq"> wrapping ALL click groups
    - Each group = <p:par delay="indefinite"> with shape animations inside
    - First shape in group: nodeType="clickEffect"
    - Subsequent shapes in same group: nodeType="withEffect"  
    - <p:bldLst> at end with animBg="1" per shape — CRITICAL for initial hiding
    - nextCondLst uses evt="onNext" (not onClick)
    """
    id_gen = [3]
    def nid(): v = id_gen[0]; id_gen[0] += 1; return v

    all_spids = []
    click_groups = []

    for group_spids in groups:
        all_spids.extend(group_spids)
        outer_id = nid()
        inner_id = nid()
        shape_pars = []
        for i, spid in enumerate(group_spids):
            node_type = "clickEffect" if i == 0 else "withEffect"
            effect_id = nid()
            set_id    = nid()
            shape_pars.append(
                f'<p:par><p:cTn id="{effect_id}" presetID="1" presetClass="entr" ' +
                f'presetSubtype="0" fill="hold" grpId="0" nodeType="{node_type}">' +
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>' +
                f'<p:set><p:cBhvr>' +
                f'<p:cTn id="{set_id}" dur="1" fill="hold">' +
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>' +
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>' +
                f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>' +
                f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>' +
                f'</p:childTnLst></p:cTn></p:par>'
            )
        click_groups.append(
            f'<p:par><p:cTn id="{outer_id}" fill="hold">' +
            f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>' +
            f'<p:childTnLst><p:par>' +
            f'<p:cTn id="{inner_id}" fill="hold">' +
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>' +
            f'<p:childTnLst>{"".join(shape_pars)}</p:childTnLst>' +
            f'</p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
        )

    bld = "".join(f'<p:bldP spid="{s}" grpId="0" animBg="1"/>' for s in all_spids)

    return (
        '<p:timing><p:tnLst><p:par>' +
        '<p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">' +
        '<p:childTnLst>' +
        '<p:seq concurrent="1" nextAc="seek">' +
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq">' +
        f'<p:childTnLst>{"".join(click_groups)}</p:childTnLst>' +
        '</p:cTn>' +
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>' +
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>' +
        '</p:seq>' +
        '</p:childTnLst></p:cTn></p:par></p:tnLst>' +
        f'<p:bldLst>{bld}</p:bldLst>' +
        '</p:timing>'
    )


def inject_timing(slide_bytes, groups):
    """Inject click-reveal animation groups into a slide's XML."""
    xml = slide_bytes.decode('utf-8')
    xml = re.sub(r'<p:timing>.*?</p:timing>', '', xml, flags=re.DOTALL)
    timing = make_timing(groups)
    xml = xml.replace('</p:sld>', timing + '</p:sld>')
    return xml.encode('utf-8')


def spids_with_text(xml_bytes, texts):
    """Find spids whose shape contains any of `texts` as its complete text content."""
    results = []
    for sp_match in re.finditer(r'<p:sp\b.*?</p:sp>', xml_bytes.decode('utf-8'), re.DOTALL):
        sp = sp_match.group()
        id_m = re.search(r'<p:cNvPr[^>]*\bid="(\d+)"', sp)
        if not id_m:
            continue
        spid = int(id_m.group(1))
        text = ''.join(re.findall(r'<a:t>(.*?)</a:t>', sp))
        if text.strip() in texts:
            results.append(spid)
    return results

# ── slide-specific click groups ───────────────────────────────────────────────

def groups_slide3():
    """6 pairs (ans+rule) + rule box = 7 click groups."""
    groups = [[9 + i*3 + 1, 9 + i*3 + 2] for i in range(6)]
    groups.append([27, 28])
    print(f"  Slide 3: {len(groups)} click groups → {groups}")
    return groups

def groups_slide4():
    """2 click groups: box0=ID29, box1=ID30"""
    groups = [[29], [30]]
    print(f"  Slide 4: {len(groups)} click groups → {groups}")
    return groups

def groups_slide5():
    """6 click groups for etymology slide."""
    groups = [
        [10, 11],
        [12, 13],
        [14, 15],
        [9],
        [16, 17, 18, 19],
        [20, 21],
    ]
    print(f"  Slide 5: {len(groups)} click groups → {groups}")
    return groups

def groups_slide6(xml_bytes):
    """All syllable count shapes in one click (found by text content)."""
    target = {"1", "2", "3", "4", "5", "6", "syllable", "syllables"}
    spids = sorted(spids_with_text(xml_bytes, target))
    print(f"  Slide 6: found {len(spids)} shapes → {spids}")
    return [spids]

# ── bezier arc injection ──────────────────────────────────────────────────────

def inject_bezier_arcs(src_path, arc_data):
    """Add split-digraph bezier arcs to slides before animation pass."""
    if not arc_data:
        return
    P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    EMU  = 914400

    from lxml import etree
    arcs_by_slide = {}
    for arc in arc_data:
        arcs_by_slide.setdefault(arc['slide'], []).append(arc)

    with zipfile.ZipFile(src_path, 'r') as zin:
        files = {n: zin.read(n) for n in zin.namelist()}

    for slide_num, arcs in arcs_by_slide.items():
        key = f'ppt/slides/slide{slide_num}.xml'
        if key not in files:
            continue
        tree = etree.fromstring(files[key])
        spTree = tree.find(f'.//{{{P_NS}}}cSld/{{{P_NS}}}spTree') or \
                 tree.find(f'.//{{{A_NS}}}spTree')
        if spTree is None:
            continue
        for arc in arcs:
            x1, y1, x2, y2 = [int(v * EMU) for v in [arc['x1'], arc['y1'], arc['x2'], arc['y2']]]
            bx, by = min(x1, x2), min(y1, y2)
            bw, bh = abs(x2 - x1), abs(y2 - y1)
            flipH = (x2 < x1) != (y2 < y1)
            sp = etree.SubElement(spTree, f'{{{P_NS}}}sp')
            nvSpPr = etree.SubElement(sp, f'{{{P_NS}}}nvSpPr')
            cNvPr  = etree.SubElement(nvSpPr, f'{{{P_NS}}}cNvPr')
            cNvPr.set('id', str(arc.get('id', 999)))
            cNvPr.set('name', f"Arc_{arc.get('id', 999)}")
            cNvSpPr = etree.SubElement(nvSpPr, f'{{{P_NS}}}cNvSpPr')
            spLocks = etree.SubElement(cNvSpPr, f'{{{A_NS}}}spLocks')
            spLocks.set('noGrp', '1')
            etree.SubElement(nvSpPr, f'{{{P_NS}}}nvPr')
            spPr = etree.SubElement(sp, f'{{{P_NS}}}spPr')
            xfrm = etree.SubElement(spPr, f'{{{A_NS}}}xfrm')
            if flipH:
                xfrm.set('flipH', '1')
            off = etree.SubElement(xfrm, f'{{{A_NS}}}off')
            off.set('x', str(bx)); off.set('y', str(by))
            ext = etree.SubElement(xfrm, f'{{{A_NS}}}ext')
            ext.set('cx', str(max(bw, 1))); ext.set('cy', str(max(bh, 1)))
            prstGeom = etree.SubElement(spPr, f'{{{A_NS}}}prstGeom')
            prstGeom.set('prst', 'arc')
            etree.SubElement(prstGeom, f'{{{A_NS}}}avLst')
            ln = etree.SubElement(spPr, f'{{{A_NS}}}ln')
            ln.set('w', '25400')
            solidFill = etree.SubElement(ln, f'{{{A_NS}}}solidFill')
            srgbClr = etree.SubElement(solidFill, f'{{{A_NS}}}srgbClr')
            srgbClr.set('val', '1A1A1A')
        files[key] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)

    tmp = src_path + '.arc_tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item, data in files.items():
            if not item.endswith('/'):
                zout.writestr(item, data)
    os.replace(tmp, src_path)

# ── Structural fixes for pptxgenjs output ─────────────────────────────────────

def clean_and_fix(zip_path):
    """Minimal fix: only strip phantom slideMaster CT entries pptxgenjs generates.
    Do NOT touch XML formatting, notes, rels ordering, or anything else — 
    every extra change risks triggering PowerPoint's repair dialog.
    """
    CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
    from lxml import etree as _et
    import zipfile as _zf

    with _zf.ZipFile(zip_path, 'r') as z:
        files = {n: z.read(n) for n in z.namelist()}

    names = set(files.keys())
    tree = _et.fromstring(files['[Content_Types].xml'])
    removed = 0
    for el in list(tree.findall(f'{{{CT_NS}}}Override')):
        part = el.get('PartName', '').lstrip('/')
        if part and part not in names:
            tree.remove(el)
            removed += 1

    if removed:
        files['[Content_Types].xml'] = _et.tostring(
            tree, xml_declaration=True, encoding='UTF-8', standalone=True
        ).replace(
            b"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>",
            b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        )

    tmp = zip_path + '.fix_tmp'
    with _zf.ZipFile(tmp, 'w', _zf.ZIP_DEFLATED) as oz:
        for name, data in files.items():
            if not name.endswith('/'):
                oz.writestr(name, data)
    import os as _os
    _os.replace(tmp, zip_path)
    print(f"  Stripped {removed} phantom CT entries → {zip_path.split('/')[-1]}")


# ── Main pipeline ─────────────────────────────────────────────────────────────

# Fix both slides and worksheets
clean_and_fix(SRC)
_ws_path = f"/home/claude/spelling_worksheets_{_code}.pptx"
if os.path.exists(_ws_path):
    clean_and_fix(_ws_path)

# Arc injection (if any)
_arc_json = '/home/claude/sb_arc_data.json'
_arc_data = _json.load(open(_arc_json)) if os.path.exists(_arc_json) else []
if _arc_data:
    print(f"Injecting {len(_arc_data)} bezier arc(s) into {SRC}...")
    inject_bezier_arcs(SRC, _arc_data)
else:
    print("No arcs to inject")

# Animation injection — key spelling slide is already slide 1,
# so animated content slides sit at positions 4-7
with zipfile.ZipFile(SRC, 'r') as zf:
    raw = {n: zf.read(f'ppt/slides/slide{n}.xml') for n in [4, 5, 6, 7]}

animated = {
    'ppt/slides/slide4.xml': inject_timing(raw[4], groups_slide3()),
    'ppt/slides/slide5.xml': inject_timing(raw[5], groups_slide4()),
    'ppt/slides/slide6.xml': inject_timing(raw[6], groups_slide5()),
    'ppt/slides/slide7.xml': inject_timing(raw[7], groups_slide6(raw[7])),
}

shutil.copy(SRC, DEST)
tmp = DEST + '.tmp'
with zipfile.ZipFile(DEST, 'r') as zin:
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            if item.endswith('/'):
                continue
            data = animated.get(item, zin.read(item))
            zout.writestr(item, data)
os.replace(tmp, DEST)
import os as _os
_os.replace(DEST, _FINAL)
print(f"Saved: {_FINAL}")
