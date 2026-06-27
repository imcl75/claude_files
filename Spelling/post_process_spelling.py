"""
post_process_spelling.py
Applies post-build additions to a spelling deck:
  1. Slide 10: 2-click animation (syllable breaks on click 1, sound buttons on click 2)
     Uses Y-position to classify shapes, not text content.
  2. Independent Learning section slide (inserted after slide 10)

Usage: python3 post_process_spelling.py <code>
"""
import sys, os, zipfile, shutil, re, json
from lxml import etree
from copy import deepcopy

CODE = sys.argv[1] if len(sys.argv) > 1 else "OU"
SRC  = f"/home/claude/spelling_shed_slides_{CODE}.pptx"
TMP  = SRC + ".post_tmp"

with open("/home/claude/lesson.json") as f:
    LESSON = json.load(f)
WORDS_STR = ", ".join(LESSON["words"])
WORDMAP_WORDS = set(LESSON["wordMaps"]["words"])

P  = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A  = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'

with zipfile.ZipFile(SRC, 'r') as z:
    files = {n: z.read(n) for n in z.namelist()}

# ─── Part 1: Animate slide 10 ─────────────────────────────────────────────────
# Slide layout (Y in EMU, CONT_Y = 1079592):
#   Frame shapes:           y < 1100000
#   Word headings (pink):   y ≈ 1307592  → VISIBLE
#   "Syllable Breaks":      y ≈ 1993392  → VISIBLE
#   Syllable box (rect):    y ≈ 2295144  → CLICK 1
#   Syllable text:          y ≈ 2295144  → CLICK 1
#   Syllable count:         y ≈ 2788920  → CLICK 1
#   "Sound Buttons":        y ≈ 3090672  → VISIBLE
#   GraphicFrame (table):   y ≈ 3429000  → CLICK 2
#   Dots / Lines:           y ≈ 3856736  → CLICK 2
#   Legend:                 y ≈ 3941064  → CLICK 2

FRAME_MAX   = 1_100_000
CLICK1_MIN  = 2_200_000
CLICK1_MAX  = 2_900_000
CLICK2_MIN  = 3_150_000

def get_y(el):
    off = el.find('.//{%s}off' % A)
    if off is None:
        return None
    try:
        return int(off.get('y', '0'))
    except (ValueError, TypeError):
        return None

def build_click_timing(all_groups):
    """Build p:timing XML for N click groups. all_groups = [[spid,...], [spid,...]]"""
    NS_P = P
    groups_xml = []
    id_counter = [100]
    def nid(): v = id_counter[0]; id_counter[0] += 1; return v

    all_spids = [spid for g in all_groups for spid in g]

    for grp in all_groups:
        outer = nid(); inner = nid()
        parts = []
        for i, spid in enumerate(grp):
            eff = nid(); stt = nid()
            node = "clickEffect" if i == 0 else "withEffect"
            parts.append(
                f'<p:par><p:cTn id="{eff}" presetID="1" presetClass="entr" presetSubtype="0"'
                f' fill="hold" grpId="0" nodeType="{node}">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst><p:set><p:cBhvr>'
                f'<p:cTn id="{stt}" dur="1" fill="hold">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
                f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
                f'</p:childTnLst></p:cTn></p:par>'
            )
        groups_xml.append(
            f'<p:par><p:cTn id="{outer}" fill="hold">'
            f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            f'<p:childTnLst><p:par><p:cTn id="{inner}" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst>{"".join(parts)}</p:childTnLst>'
            f'</p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
        )

    bld = "".join(f'<p:bldP spid="{s}" grpId="0" animBg="1"/>' for s in all_spids)
    return (
        f'<p:timing xmlns:p="{NS_P}">'
        '<p:tnLst><p:par>'
        '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        '<p:childTnLst>'
        '<p:seq concurrent="1" nextAc="seek">'
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
        f'<p:childTnLst>{"".join(groups_xml)}</p:childTnLst>'
        '</p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        '</p:seq>'
        '</p:childTnLst></p:cTn>'
        '</p:par></p:tnLst>'
        f'<p:bldLst>{bld}</p:bldLst>'
        '</p:timing>'
    )

def animate_slide10():
    key = 'ppt/slides/slide10.xml'
    if key not in files:
        print("  slide10.xml not found — skipping"); return

    tree = etree.fromstring(files[key])

    # ── Step 1: deduplicate graphicFrame IDs (pptxgenjs reuses sp IDs) ──────
    used_ids = set()
    next_free_id = [200]
    def new_id():
        while str(next_free_id[0]) in used_ids:
            next_free_id[0] += 1
        r = str(next_free_id[0]); next_free_id[0] += 1; return r

    # Collect all existing IDs
    for el in tree.findall('.//{%s}cNvPr' % P):
        used_ids.add(el.get('id', ''))
    for el in tree.findall('.//{%s}cNvPr' % A):
        used_ids.add(el.get('id', ''))

    # For graphicFrames: if their ID is already used by an sp, renumber
    gf_id_map = {}  # old_id → new_id for graphicFrames
    for gf in tree.findall('.//{%s}graphicFrame' % P):
        nvpr = gf.find('{%s}nvGraphicFramePr' % P)
        if nvpr is None: continue
        cnv = nvpr.find('{%s}cNvPr' % P)
        if cnv is None: continue
        old = cnv.get('id', '')
        # Count how many elements share this ID
        all_with_id = [e for e in tree.findall('.//{%s}cNvPr' % P) if e.get('id') == old]
        if len(all_with_id) > 1:
            nw = new_id()
            used_ids.add(nw)
            gf_id_map[old] = nw
            cnv.set('id', nw)
            cnv.set('name', f'tbl_{nw}')

    if gf_id_map:
        print(f"  Renumbered {len(gf_id_map)} duplicate graphicFrame IDs: {gf_id_map}")

    # ── Step 2: classify shapes by Y position ──────────────────────────────
    click1_ids = []; click2_ids = []

    # sp elements
    for sp in tree.findall('.//{%s}sp' % P):
        cnv = sp.find('.//{%s}cNvPr' % P)
        if cnv is None: continue
        spid = cnv.get('id', '')
        y = get_y(sp)
        if y is None: continue
        if y < FRAME_MAX: continue  # frame shape — leave alone
        # Get text for visible-label check
        text = ''.join(t.text or '' for t in sp.findall('.//{%s}t' % A)).strip()
        if text in ('Syllable Breaks', 'Sound Buttons') or text in WORDMAP_WORDS:
            continue  # always visible
        if CLICK1_MIN <= y <= CLICK1_MAX:
            click1_ids.append(spid)
        elif y >= CLICK2_MIN:
            click2_ids.append(spid)

    # graphicFrame elements (tables built by drawSoundButtons)
    for gf in tree.findall('.//{%s}graphicFrame' % P):
        nvpr = gf.find('{%s}nvGraphicFramePr' % P)
        if nvpr is None: continue
        cnv = nvpr.find('{%s}cNvPr' % P)
        if cnv is None: continue
        spid = cnv.get('id', '')
        y = get_y(gf)
        if y is not None and y >= CLICK2_MIN:
            click2_ids.append(spid)

    print(f"  Slide 10: click-1 = {len(click1_ids)} shapes {click1_ids}")
    print(f"  Slide 10: click-2 = {len(click2_ids)} shapes {click2_ids}")

    if not click1_ids and not click2_ids:
        print("  Nothing to animate — skipping"); return

    # Remove existing timing
    existing = tree.find('{%s}timing' % P)
    if existing is not None: tree.remove(existing)

    timing_xml = build_click_timing([click1_ids, click2_ids])
    tree.append(etree.fromstring(timing_xml))
    files[key] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    print("  Slide 10 animated ✓")

animate_slide10()

# ─── Part 2: Insert Independent Learning section slide after slide 10 ─────────
YOU_DO_IMG = '/home/claude/you_do_image.png'

def insert_section_slide():
    if not os.path.exists(YOU_DO_IMG):
        print("  you_do_image.png not found"); return

    with open(YOU_DO_IMG, 'rb') as f:
        img_data = f.read()

    max_img = max((int(re.search(r'(\d+)', os.path.basename(n)).group(1))
                   for n in files if re.match(r'ppt/media/image\d+', n)), default=0)
    new_img_num = max_img + 1
    files[f'ppt/media/image{new_img_num}.png'] = img_data

    # Renumber slides 11+ → 12+ to make room for new slide 11
    renames = {}
    for k in list(files.keys()):
        m = re.match(r'ppt/slides/(slide(\d+)\.xml)', k)
        if m and int(m.group(2)) > 10:
            renames[k] = f'ppt/slides/slide{int(m.group(2))+1}.xml'
        m2 = re.match(r'ppt/slides/_rels/(slide(\d+)\.xml\.rels)', k)
        if m2 and int(m2.group(2)) > 10:
            renames[k] = f'ppt/slides/_rels/slide{int(m2.group(2))+1}.xml.rels'

    for old, new in renames.items():
        files[new] = files.pop(old)

    # FIX: also update presentation.xml.rels so renamed slide targets stay correct.
    # Without this, rId11 still targets slides/slide11.xml after slide11 is renamed
    # to slide12 — then the new section slide11.xml causes a duplicate reference.
    prs_rels_bytes = files['ppt/_rels/presentation.xml.rels']
    slide_renames = {
        old.replace('ppt/', ''): new.replace('ppt/', '')
        for old, new in renames.items()
        if re.match(r'ppt/slides/slide\d+\.xml$', old)
    }
    # Sort descending by number to avoid slide1 matching inside slide10, slide11 etc.
    for old_rel, new_rel in sorted(slide_renames.items(),
                                    key=lambda x: int(re.search(r'\d+', x[0]).group()),
                                    reverse=True):
        prs_rels_bytes = prs_rels_bytes.replace(
            f'Target="{old_rel}"'.encode(),
            f'Target="{new_rel}"'.encode()
        )
    files['ppt/_rels/presentation.xml.rels'] = prs_rels_bytes

    # Build section slide XML
    W, H = 9144000, 5143500  # 10" x 5.625" in EMU
    def cm(v): return int(v * 360000)
    img_rId = 'rId99'
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        f'<Relationship Id="{img_rId}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image{new_img_num}.png"/>'
        '</Relationships>'
    )
    files['ppt/slides/_rels/slide11.xml.rels'] = rels.encode('utf-8')

    def rect(id_, x, y, w, h, fill):
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id_}" name="r{id_}"/>'
                f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                f'<a:ln><a:noFill/></a:ln></p:spPr>'
                f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

    def txt(id_, x, y, w, h, text, sz, bold, color, align='ctr'):
        b = '1' if bold else '0'
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id_}" name="t{id_}"/>'
                f'<p:cNvSpPr txBox="1"><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="square" anchorCtr="1"/><a:lstStyle/>'
                f'<a:p><a:pPr algn="{align}"/>'
                f'<a:r><a:rPr lang="en-GB" sz="{sz}" b="{b}" dirty="0">'
                f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr>'
                f'<a:t>{text}</a:t></a:r></a:p>'
                f'</p:txBody></p:sp>')

    img_sp = (
        f'<p:pic><p:nvPicPr><p:cNvPr id="99" name="img"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{img_rId}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
        f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="{cm(8.18)}" y="{cm(4.41)}"/>'
        f'<a:ext cx="{cm(8.4)}" cy="{cm(3.49)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
    )

    words_safe = WORDS_STR.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    slide_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:cSld><p:spTree>'
        f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{W}" cy="{H}"/>'
        f'<a:chOff x="0" y="0"/><a:chExt cx="{W}" cy="{H}"/></a:xfrm></p:grpSpPr>'
        + rect(10, 0, 0, W, cm(9.14), '87CEEB')
        + rect(11, 0, cm(8.38), W, cm(5.91), 'FFFFFF')
        + rect(12, 0, cm(13.72), W, cm(0.57), '57A657')
        + txt(13, cm(0.4), cm(0.38), cm(24.55), cm(3.56), 'Independent Learning', 6400, True, 'F4C430')
        + img_sp
        + txt(20, cm(8.0), cm(8.5), cm(9.4), cm(0.9), 'Learning Paper', 1800, False, '1A1A1A')
        + txt(21, cm(1.27), cm(10.5), cm(22.86), cm(1.9),
              f'Today\u2019s words:  {words_safe}', 1700, False, '1A1A1A')
        + '</p:spTree></p:cSld></p:sld>'
    )
    files['ppt/slides/slide11.xml'] = slide_xml.encode('utf-8')

    # Update presentation.xml — insert sldId for slide11 after slide10
    prs_tree = etree.fromstring(files['ppt/presentation.xml'])
    sldIdLst = prs_tree.find('{%s}sldIdLst' % P)
    existing_ids = [int(el.get('id', '0')) for el in sldIdLst]
    new_sld_id = max(existing_ids) + 1

    prs_rels = etree.fromstring(files['ppt/_rels/presentation.xml.rels'])
    slide_rId_map = {el.get('Target'): el.get('Id') for el in prs_rels
                     if 'slide' in el.get('Target','') and 'Layout' not in el.get('Target','')}
    rids = [v for v in slide_rId_map.values() if re.search(r'\d+', v)]
    max_rid = max(int(re.search(r'(\d+)', r).group(1)) for r in rids)
    new_rid = f'rId{max_rid + 1}'

    new_rel = etree.SubElement(prs_rels, '{%s}Relationship' % NS_REL)
    new_rel.set('Id', new_rid)
    new_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')
    new_rel.set('Target', 'slides/slide11.xml')
    files['ppt/_rels/presentation.xml.rels'] = etree.tostring(
        prs_rels, xml_declaration=True, encoding='UTF-8', standalone=True)

    # Find sldId for slide10 and insert after it
    slide10_rid = slide_rId_map.get('slides/slide10.xml','')
    R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    insert_after = None
    for el in sldIdLst:
        if el.get(f'{{{R_NS}}}id') == slide10_rid:
            insert_after = el; break

    new_sld_el = etree.Element(f'{{{P}}}sldId')
    new_sld_el.set('id', str(new_sld_id))
    new_sld_el.set(f'{{{R_NS}}}id', new_rid)
    idx = list(sldIdLst).index(insert_after) if insert_after is not None else len(list(sldIdLst))-1
    sldIdLst.insert(idx + 1, new_sld_el)
    files['ppt/presentation.xml'] = etree.tostring(
        prs_tree, xml_declaration=True, encoding='UTF-8', standalone=True)

    # Update [Content_Types].xml
    ct = etree.fromstring(files['[Content_Types].xml'])
    CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
    ov = etree.SubElement(ct, f'{{{CT_NS}}}Override')
    ov.set('PartName', '/ppt/slides/slide11.xml')
    ov.set('ContentType', 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
    if not any(el.get('Extension') == 'png' for el in ct):
        d = etree.SubElement(ct, f'{{{CT_NS}}}Default')
        d.set('Extension', 'png'); d.set('ContentType', 'image/png')
    files['[Content_Types].xml'] = etree.tostring(
        ct, xml_declaration=True, encoding='UTF-8', standalone=True)

    print(f"  Section slide inserted as slide 11 ✓")

insert_section_slide()

# ─── Write output ─────────────────────────────────────────────────────────────
with zipfile.ZipFile(TMP, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in files.items():
        if not name.endswith('/'):
            zout.writestr(name, data)
os.replace(TMP, SRC)
print(f"Saved: {SRC}")


# ─── Part 3: Fix OOXML issues that cause PowerPoint repair prompts ─────────────
# After slide renaming and section slide insertion, several structural issues
# remain that PowerPoint flags on open:
#  1. notesSlide back-refs still point to old slide numbers (post rename)
#  2. Empty <a:r> runs in all notesSlides (pptxgenjs quirk)
#  3. notesMaster1.xml.rels references theme1.xml instead of theme2.xml
#  4. theme2.xml is missing from the ZIP

def fix_ooxml_issues():
    # 1. Fix notesSlide back-refs ─────────────────────────────────────────────
    # Build map: notesSlideN → slideN (from slide _rels)
    ns_to_slide = {}
    for name, data in files.items():
        if not re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels$', name):
            continue
        s_num = int(re.search(r'slide(\d+)', name).group(1))
        for m in re.finditer(r'notesSlide(\d+)\.xml', data.decode('utf-8', errors='ignore')):
            ns_to_slide[int(m.group(1))] = s_num

    for name in list(files.keys()):
        if not re.match(r'ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels$', name):
            continue
        ns_num = int(re.search(r'notesSlide(\d+)', name).group(1))
        if ns_num not in ns_to_slide:
            continue
        correct_slide = ns_to_slide[ns_num]
        rels = files[name].decode('utf-8')
        m = re.search(r'Target="\.\./slides/(slide\d+\.xml)"', rels)
        if m and m.group(1) != f'slide{correct_slide}.xml':
            files[name] = rels.replace(
                m.group(1), f'slide{correct_slide}.xml'
            ).encode('utf-8')

    # 2. Remove empty <a:r> runs from all notesSlide XML ─────────────────────
    # pptxgenjs emits <a:r><a:rPr .../><a:t></a:t></a:r> — PowerPoint removes these
    empty_run_pat = re.compile(
        r'<a:r>\s*<a:rPr[^/]*/>\s*<a:t>\s*</a:t>\s*</a:r>'
    )
    for name in list(files.keys()):
        if not re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', name):
            continue
        content = files[name].decode('utf-8')
        fixed = empty_run_pat.sub('', content)
        if fixed != content:
            files[name] = fixed.encode('utf-8')

    # 3. Fix notesMaster rels: theme1.xml → theme2.xml ────────────────────────
    nm_rels_key = 'ppt/notesMasters/_rels/notesMaster1.xml.rels'
    if nm_rels_key in files:
        nm_rels = files[nm_rels_key].decode('utf-8')
        if 'theme/theme1.xml' in nm_rels:
            files[nm_rels_key] = nm_rels.replace(
                'theme/theme1.xml', 'theme/theme2.xml'
            ).encode('utf-8')

    # 4. Add theme2.xml if missing ────────────────────────────────────────────
    if 'ppt/theme/theme1.xml' in files and 'ppt/theme/theme2.xml' not in files:
        files['ppt/theme/theme2.xml'] = files['ppt/theme/theme1.xml']
        # Declare it in Content_Types
        ct = files['[Content_Types].xml'].decode('utf-8')
        if 'theme2.xml' not in ct:
            ct = ct.replace(
                '<Override PartName="/ppt/theme/theme1.xml"',
                '<Override PartName="/ppt/theme/theme2.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
                '<Override PartName="/ppt/theme/theme1.xml"'
            )
            files['[Content_Types].xml'] = ct.encode('utf-8')

    print("  OOXML issues fixed ✓")

fix_ooxml_issues()
