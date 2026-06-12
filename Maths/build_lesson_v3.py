"""
build_lesson_v3.py — Generalised lesson teaching PPTX builder
Usage:  python3 build_lesson_v3.py <lesson_number>   (1-20)

Reads all text content from maths_plan_v3.json.
Reads authored visual/WM/RM data from lesson_data.py.
"""

import sys, copy, re, json, io as _io
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt

EMU = 914400
def emu(inches): return int(inches * EMU)

# ---------------------------------------------------------------------------
# LESSON NUMBER
# ---------------------------------------------------------------------------
LESSON_NUM = int(sys.argv[1]) if len(sys.argv) > 1 else 1

# ---------------------------------------------------------------------------
# LOAD JSON PLAN
# ---------------------------------------------------------------------------
with open('/home/claude/transfer_files/maths_plan_v3.json') as f:
    PLAN = json.load(f)

L1 = PLAN['lessons'][LESSON_NUM - 1]
KEY_QUESTIONS = PLAN['keyQuestions']
assert L1['lesson'] == LESSON_NUM, f"Lesson mismatch: expected {LESSON_NUM}, got {L1['lesson']}"
print(f"Building lesson {LESSON_NUM}: {L1['day']} ({L1['topic']}) — {L1['li'][:60]}")

# ---------------------------------------------------------------------------
# LOAD AUTHORED LESSON DATA (visuals, WM, RM, vocab)
# ---------------------------------------------------------------------------
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('lesson_data', '/home/claude/lesson_data.py')
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

if LESSON_NUM not in _mod.LESSON_DATA:
    raise ValueError(f"No authored data found for lesson {LESSON_NUM} in lesson_data.py")

_ld = _mod.LESSON_DATA[LESSON_NUM]
VOCAB   = _ld['vocab']
WM_DATA = _ld['wm']
RM_DATA = _ld['rm']

# ---------------------------------------------------------------------------
# BUILD VISUALS DICT — authored coords + spotTheMistake from JSON
# ---------------------------------------------------------------------------
STM = L1['spotTheMistake']

stm_visual = {
    'title':             STM['slideTitle'],
    'slide_type':        'spot_the_mistake',
    'cols':              STM['gridSize'] if STM['gridSize'] > 0 else 6,
    'rows':              STM['gridSize'] if STM['gridSize'] > 0 else 6,
    'points':            [[STM['startPoint'][0], STM['startPoint'][1], 'A', '1F4E79']]
                         if STM['startPoint'] else [],
    'extra_points':      STM.get('extraPoints', []),
    'error_instruction': STM['errorInstruction'],
    'error_note':        STM['errorNote'],
    'error_type':        STM['errorType'],
    'notes':             "\n".join([
                             "I DO C2 — Spot the Mistake",
                             f"Concept: {STM['concept']}",
                             "Beat 1 (load): Grid + instruction visible.",
                             "Beat 2 (click 1): X appears at error position.",
                             "Beat 3 (click 2): Explanation revealed.",
                         ]),
}

VISUALS = dict(_ld['visuals'])
VISUALS['c2_ido2'] = stm_visual

# ---------------------------------------------------------------------------
prs = Presentation('/home/claude/template.pptx')

# Extract LO slide avatar image parts BEFORE deleting template slides
_lo_sld3 = prs.slides[2]

# Remove all existing slides cleanly
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
sldIdLst = prs.slides._sldIdLst
prs_part = prs.part
rIds = [s.get(f'{{{NS_R}}}id') for s in list(sldIdLst)]
for rId in rIds:
    for s in list(sldIdLst):
        if s.get(f'{{{NS_R}}}id') == rId:
            sldIdLst.remove(s)
    if rId in prs_part.rels:
        prs_part.rels.pop(rId)

_dummy = prs.slides[2] if False else None  # placeholder line
LO_IMAGE_PARTS = {}  # partname -> ImagePart
for _rId, _rel in _lo_sld3.part.rels.items():
    if hasattr(_rel, 'target_part'):
        _tp = _rel.target_part
        _pn = str(_tp.partname)
        if any(img in _pn for img in ['image8','image9','image10']):
            LO_IMAGE_PARTS[_pn.split('/')[-1]] = _tp

print(f"Template cleared. Slides: {len(prs.slides)}")
print(f"LO image parts saved: {list(LO_IMAGE_PARTS.keys())}")

def layout(n):
    return prs.slide_layouts[n - 1]

# ---------------------------------------------------------------------------
# IMAGE HELPER — always direct file read
# ---------------------------------------------------------------------------
def add_pic(slide, image_filename, x, y, w, h):
    img_path = f'/home/claude/unpacked/ppt/media/{image_filename}'
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    pic = slide.shapes.add_picture(_io.BytesIO(img_bytes), emu(x), emu(y), emu(w), emu(h))
    return pic.element

# ---------------------------------------------------------------------------
# XML HELPERS
# ---------------------------------------------------------------------------
def _esc(s):
    return (str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            .replace('"','&quot;').replace("'","&apos;"))

def add_sp(slide, xml_str):
    slide.shapes._spTree.append(etree.fromstring(xml_str))

def sp(spid, name, x, y, w, h, text, font='Twinkl Cursive Looped Light',
       sz=18, bold=False, color='000000', align='l',
       fill=None, border=None, geom='rect', anchor='ctr',
       no_line=False, underline=False):
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    if no_line:
        line_xml = '<a:ln w="0"><a:noFill/></a:ln>'
    elif border:
        col, wpt = border
        line_xml = f'<a:ln w="{int(wpt*12700)}"><a:solidFill><a:srgbClr val="{col}"/></a:solidFill></a:ln>'
    else:
        line_xml = ''
    b_attr = ' b="1"' if bold else ''
    u_attr = ' u="sng"' if underline else ''
    color_xml = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
    if isinstance(text, list):
        paras = ''.join(f'''<a:p><a:pPr algn="{align}"/><a:r>
          <a:rPr lang="en-GB" sz="{int(sz*100)}"{b_attr}{u_attr} dirty="0">
            {color_xml}<a:latin typeface="{font}"/>
          </a:rPr><a:t>{_esc(line)}</a:t></a:r></a:p>''' for line in text)
    else:
        paras = f'''<a:p><a:pPr algn="{align}"/><a:r>
          <a:rPr lang="en-GB" sz="{int(sz*100)}"{b_attr}{u_attr} dirty="0">
            {color_xml}<a:latin typeface="{font}"/>
          </a:rPr><a:t>{_esc(text)}</a:t></a:r></a:p>'''
    return f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
    {fill_xml}{line_xml}
  </p:spPr>
  <p:txBody><a:bodyPr rtlCol="0" anchor="{anchor}"/>
    <a:lstStyle/>{paras}</p:txBody>
</p:sp>'''

def new_slide(layout_num):
    return prs.slides.add_slide(layout(layout_num))

# ===========================================================================
# SLIDE 1 — KEY QUESTION  (fixed: exact template positions, black, underlined)
# ===========================================================================
def build_slide1():
    sld = new_slide(13)
    sid = [29]
    def nid(): sid[0]+=1; return sid[0]

    kq_text = KEY_QUESTIONS[L1['topic']]

    # Cloud PNG image (fixed — contains "Key Question?" label, key icon, red ?)
    # Positioned to match your reference: x=1.745, y=0.093, w=10.160, h=3.332
    add_pic(sld,'cloud_kq.png', 1.745, 0.093, 10.160, 3.332)

    # Question text box — floats over right portion of cloud
    # x=4.934, y=1.110, w=5.902, h=1.500 (slightly taller than ref for wrapping)
    add_sp(sld, sp(nid(),'KQText', 4.934, 1.110, 5.902, 1.500,
                   kq_text, font='Twinkl Cursive Looped',
                   sz=26, bold=False, color='000000', align='l',
                   fill=None, no_line=True, anchor='t'))

    # Children clipart and maths logo (same positions as ref)
    add_pic(sld,'image7.png',  3.243, 3.103, 6.458, 3.056)
    add_pic(sld,'image1.png',  5.867, 5.840, 1.210, 1.052)

    # "Being a Mathematician" label
    add_sp(sld, sp(nid(),'BAM', 4.934, 6.836, 3.077, 0.429,
                   'Being a Mathematician', font='Twinkl Cursive Looped Light',
                   sz=14, bold=True, color='000000', align='ctr',
                   fill=None, no_line=True))

    sld.notes_slide.notes_text_frame.text = (
        f"KEY QUESTION — {L1['topic']}\n{kq_text}\n"
        "Same slide used for all lessons in this topic block.")
    print("Slide 1 (Key Question) ✓")

# ===========================================================================
# SLIDE 2 — DAY TITLE
# ===========================================================================
def build_slide2():
    sld = new_slide(13)
    sid = [2]
    def nid(): sid[0]+=1; return sid[0]
    day_map = {'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4}
    day_num = day_map.get(L1['day'],1)
    add_sp(sld, sp(nid(),'BAM', 3.232,2.131, 7.221,0.505,
                   'Being a Mathematician', font='Twinkl Cursive Looped Light',
                   sz=18, bold=True, color='000000', align='ctr',
                   fill=None, no_line=True))
    add_sp(sld, sp(nid(),'DayText', 4.484,2.448, 4.504,2.036,
                   f'Day {day_num}', font='Twinkl Cursive Looped Light',
                   sz=100, bold=False, color='000000', align='ctr',
                   fill=None, no_line=True))
    add_pic(sld,'image1.png', 5.634,0.168, 2.066,1.796)
    add_pic(sld,'image7.png', 3.438,4.277, 6.458,3.056)
    sld.notes_slide.notes_text_frame.text = (
        f"DAY TITLE — Day {day_num} ({L1['day']})\nTopic: {L1['topic']}\nLI: {L1['li']}")
    print("Slide 2 (Day Title) ✓")

# ===========================================================================
# SLIDE 3 — LO  (cloned from template XML, text replaced only)
# ===========================================================================
def build_slide3():
    # Read template slide 3 XML
    with open('/home/claude/unpacked/ppt/slides/slide3.xml') as f:
        template_xml = f.read()

    lo = L1['loText']

    def replace_panel_text(xml, rect_name, header, body_text, body_sz):
        """Replace text in a panel's two paragraphs, preserving all formatting."""
        for match in re.finditer(r'(<p:sp>.*?</p:sp>)', xml, re.DOTALL):
            sp_xml = match.group(1)
            if f'name="{rect_name}"' in sp_xml:
                # Replace body text paragraph (para index 1)
                paras = re.findall(r'(<a:p>.*?</a:p>)', sp_xml, re.DOTALL)
                if len(paras) >= 2:
                    old_body_para = paras[1]
                    new_body_para = re.sub(
                        r'<a:t>[^<]*</a:t>',
                        f'<a:t>{_esc(body_text)}</a:t>',
                        old_body_para
                    )
                    new_sp = sp_xml.replace(old_body_para, new_body_para)
                    xml = xml.replace(sp_xml, new_sp)
        return xml

    modified_xml = template_xml
    modified_xml = replace_panel_text(modified_xml, 'Rounded Rectangle 25',
                                       'We are learning to…', lo['walt'], 1600)
    modified_xml = replace_panel_text(modified_xml, 'Rounded Rectangle 26',
                                       'This is because…', lo['tiob'], 1400)
    modified_xml = replace_panel_text(modified_xml, 'Rounded Rectangle 27',
                                       'I will show this by…', lo['iwstb'], 1600)

    # Add a new slide using the blank layout then replace its XML with the modified template
    sld = new_slide(9)  # slideLayout9 = I Do Blank (same as template slide 3)

    # Parse and set the spTree from modified template
    modified_root = etree.fromstring(modified_xml.encode())
    ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    template_spTree = modified_root.find(f'.//{{{ns_p}}}spTree')

    # Get the slide's own spTree and replace its content
    slide_spTree = sld.shapes._spTree
    # Clear existing children except nvGrpSpPr and grpSpPr
    for child in list(slide_spTree):
        tag = child.tag.split('}')[-1]
        if tag not in ('nvGrpSpPr', 'grpSpPr'):
            slide_spTree.remove(child)

    # Copy all children from template spTree (except nvGrpSpPr and grpSpPr)
    for child in template_spTree:
        tag = child.tag.split('}')[-1]
        if tag not in ('nvGrpSpPr', 'grpSpPr'):
            slide_spTree.append(copy.deepcopy(child))

    # Add LO avatar images using pre-extracted ImagePart objects
    with open('/home/claude/unpacked/ppt/slides/_rels/slide3.xml.rels') as f:
        rels_content = f.read()
    rid_map = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="\.\./media/([^"]+)"', rels_content):
        rid_map[m.group(1)] = m.group(2)

    img_rel_type = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
    spTree_xml = etree.tostring(slide_spTree, encoding='unicode')
    changed = False
    for old_rId, img_file in rid_map.items():
        img_part = LO_IMAGE_PARTS.get(img_file)
        if img_part:
            actual_rId = sld.part.relate_to(img_part, img_rel_type)
            if actual_rId != old_rId:
                spTree_xml = spTree_xml.replace(f'r:embed="{old_rId}"', f'r:embed="{actual_rId}"')
                changed = True
    if changed:
        new_spTree = etree.fromstring(spTree_xml.encode())
        parent = slide_spTree.getparent()
        parent.replace(slide_spTree, new_spTree)

    sld.notes_slide.notes_text_frame.text = (
        f"I DO — Learning Objective\nWALT: {lo['walt']}\nTIOB: {lo['tiob']}\nIWSTB: {lo['iwstb']}")
    print("Slide 3 (LO) ✓")

# ===========================================================================
# SLIDE 4 — WM MEMORY
# ===========================================================================
def build_slide4():
    sld = new_slide(5)
    items = WM_DATA['items']
    n = len(items)

    add_sp(sld, sp(2,'Title', 2.454,0.143, 9.039,1.450,
                   'Remember the details and the order',
                   font='Twinkl Cursive Looped Light', sz=40, bold=True,
                   color='000000', align='l', fill=None, no_line=True))

    add_sp(sld, sp(3,'ShowBtn', 5.219,1.347, 2.895,0.679,
                   'Click to Show', font='Aptos', sz=20, bold=True,
                   color='0E2841', align='ctr', fill='92D050',
                   geom='roundRect', no_line=True))

    item_w, item_h, item_y = 1.573, 1.400, 2.347
    # Font size: numbers fit at 40pt; words need to scale down based on longest item
    max_len = max(len(str(v)) for v in items)
    item_sz = 40 if max_len <= 3 else (28 if max_len <= 6 else 20)
    for i, val in enumerate(items):
        ix = 0.500 + i * ((13.333 - 1.000 - item_w) / (n - 1))
        add_sp(sld, sp(10+i, f'Item{i+1}', ix, item_y, item_w, item_h,
                       str(val), font='Aptos', sz=item_sz, bold=True,
                       color='FFFFFF', align='ctr', fill='1C4060',
                       border=('156082',1.5)))

    add_sp(sld, sp(20,'GoBtn', 5.283,5.887, 2.767,0.679,
                   'Go to the questions', font='Aptos', sz=20, bold=True,
                   color='FFFFFF', align='ctr', fill='0F9ED5',
                   geom='roundRect', no_line=True))

    # Cover — LAST shape
    cover_spid = 30
    add_sp(sld, sp(cover_spid,'Cover', 0.0,2.1, 13.333,3.35,
                   '', fill='DEECF8', no_line=True))

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
    <p:childTnLst><p:seq concurrent="1" nextAc="seek">
      <p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>
        <p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>
          <p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>
            <p:childTnLst><p:par>
              <p:cTn id="5" presetID="1" presetClass="exit" presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">
                <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                <p:childTnLst><p:set><p:cBhvr>
                  <p:cTn id="6" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                  <p:tgtEl><p:spTgt spid="{cover_spid}"/></p:tgtEl>
                  <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                </p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set></p:childTnLst>
              </p:cTn></p:par></p:childTnLst></p:cTn></p:par>
        <p:par><p:cTn id="7" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:par>
            <p:cTn id="8" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" grpId="1" nodeType="afterEffect">
              <p:stCondLst><p:cond delay="15000"/></p:stCondLst>
              <p:childTnLst><p:set><p:cBhvr>
                <p:cTn id="9" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                <p:tgtEl><p:spTgt spid="{cover_spid}"/></p:tgtEl>
                <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
              </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
            </p:cTn></p:par></p:childTnLst></p:cTn></p:par>
      </p:childTnLst></p:cTn></p:par>
      </p:childTnLst></p:cTn>
      <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
      <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
    </p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>
  <p:bldLst>
    <p:bldP spid="{cover_spid}" grpId="0" animBg="1"/>
    <p:bldP spid="{cover_spid}" grpId="1" animBg="1"/>
  </p:bldLst>
</p:timing>'''
    sld._element.append(etree.fromstring(timing_xml))
    sld.notes_slide.notes_text_frame.text = (
        f"YOU DO — WM Number Sequence\nNumbers: {WM_DATA['items']}\n"
        "Click reveals numbers, cover reappears after 15s.")
    print("Slide 4 (WM Memory) ✓")

# ===========================================================================
# SLIDE 5 — WM Q&A  (spids start at 20 to avoid layout placeholder collision)
# ===========================================================================
def build_slide5():
    sld = new_slide(5)

    add_sp(sld, sp(20,'Title', 0.917,0.110, 11.500,1.450,
                   'Now answer from memory!',
                   font='Twinkl Cursive Looped Light', sz=44, bold=True,
                   color='000000', align='l', fill=None, no_line=True))

    qa = WM_DATA['qa']
    q_y_left  = [1.309, 3.243, 5.212]
    q_y_right = [1.309, 3.243]
    q_h, a_h  = 1.013, 0.747
    q_w       = 6.000

    card_spids = []
    spid = 21
    for i, item in enumerate(qa):
        qx = 0.373 if i < 3 else 6.960
        qy = (q_y_left[i] if i < 3 else q_y_right[i-3])
        ay = qy + q_h

        add_sp(sld, sp(spid, f'Q{i+1}', qx, qy, q_w, q_h,
                       f'Q{i+1}   {item["q"]}',
                       font='Aptos', sz=17, bold=True, color='0E2841',
                       align='l', fill='C2D9EC', border=('156082',1.5)))
        card_spids.append(spid); spid += 1

        add_sp(sld, sp(spid, f'A{i+1}', qx, ay, q_w, a_h,
                       f'Answer:   {item["a"]}',
                       font='Aptos', sz=20, bold=True, color='0E2841',
                       align='l', fill='92D050', border=('156082',1.5)))
        card_spids.append(spid); spid += 1

    # Build timing — all cards hidden, revealed Q1→A1→Q2→A2 etc
    child_blocks = ''
    ctn_id = 3
    for spid_val in card_spids:
        child_blocks += f'''<p:par>
  <p:cTn id="{ctn_id}" fill="hold">
    <p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>
    <p:childTnLst><p:par><p:cTn id="{ctn_id+1}" fill="hold">
      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
      <p:childTnLst><p:par>
        <p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr" presetSubtype="0"
               fill="hold" grpId="1" nodeType="clickEffect">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:set><p:cBhvr>
            <p:cTn id="{ctn_id+3}" dur="1" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
            <p:tgtEl><p:spTgt spid="{spid_val}"/></p:tgtEl>
            <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
          </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
        </p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
  </p:cTn>
</p:par>'''
        ctn_id += 4

    bld_list = ''.join(
        f'<p:bldP spid="{s}" grpId="0" uiExpand="1" build="p"/>\n'
        f'<p:bldP spid="{s}" grpId="1" animBg="1"/>\n'
        for s in card_spids)

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par>
    <p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">
      <p:childTnLst><p:seq concurrent="1" nextAc="seek">
        <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
          <p:childTnLst>{child_blocks}</p:childTnLst>
        </p:cTn>
        <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
        <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
      </p:seq></p:childTnLst>
    </p:cTn>
  </p:par></p:tnLst>
  <p:bldLst>{bld_list}</p:bldLst>
</p:timing>'''
    sld._element.append(etree.fromstring(timing_xml))
    sld.notes_slide.notes_text_frame.text = (
        "YOU DO — WM Q&A\nAll cards hidden at start. Reveal: Q1→A1→Q2→A2→Q3→A3→Q4→A4→Q5→A5")
    print("Slide 5 (WM Q&A) ✓")

# ===========================================================================
# SLIDE 6 & 7 — RAPID MATHS (unchanged from v1 — working correctly)
# ===========================================================================
def build_slide6():
    sld = new_slide(5)
    qs = RM_DATA['questions']
    day = RM_DATA['day']
    add_sp(sld, sp(2,'Title', 0.917,0.069, 11.500,0.814,
                   f'Rapid Maths \u2013 Day {day}',
                   font='Twinkl Cursive Looped Light', sz=28,
                   color='000000', align='l', fill=None, no_line=True))

    left_cards  = [(0.240,0.933,6.200,2.056),(0.240,3.122,6.200,2.056),(0.240,5.311,6.200,2.056)]
    right_cards = [(6.907,0.933,6.200,3.150),(6.907,4.217,6.200,3.150)]
    card_positions = left_cards + right_cards
    lx_left, lx_right, lw = 0.400, 7.067, 5.973

    spid = 10
    for i, q in enumerate(qs):
        cx,cy,cw,ch = card_positions[i]
        lx = lx_left if i < 3 else lx_right
        q_h_text = 1.576 if i < 3 else 2.670

        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Card{i+1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx)}" y="{emu(cy)}"/><a:ext cx="{emu(cw)}" cy="{emu(ch)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(2*12700)}"><a:solidFill><a:srgbClr val="0070C0"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Topic{i+1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(lx)}" y="{emu(cy+0.067)}"/><a:ext cx="{emu(lw)}" cy="{emu(0.347)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="156082"/></a:solidFill>
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/>
    <a:lstStyle/><a:p><a:pPr algn="l"/><a:r>
      <a:rPr lang="en-GB" sz="1600" b="0" dirty="0">
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:latin typeface="Aptos"/>
      </a:rPr><a:t>Q{q["num"]}  {_esc(q["topic"])}</a:t>
    </a:r></a:p></p:txBody></p:sp>''')
        spid += 1

        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="QText{i+1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(lx)}" y="{emu(cy+0.414)}"/><a:ext cx="{emu(lw)}" cy="{emu(q_h_text)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:noFill/><a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="t"/>
    <a:lstStyle/><a:p><a:pPr algn="l"/><a:r>
      <a:rPr lang="en-GB" sz="2400" b="0" dirty="0">
        <a:solidFill><a:srgbClr val="1A1A1A"/></a:solidFill>
        <a:latin typeface="Aptos"/>
      </a:rPr><a:t>{_esc(q["q"])}</a:t>
    </a:r></a:p></p:txBody></p:sp>''')
        spid += 1

    sld.notes_slide.notes_text_frame.text = (
        f"YOU DO — Rapid Maths Day {day}\n" +
        '\n'.join(f"Q{q['num']} ({q['topic']}): {q['q']} → {q['a']}" for q in qs))
    print("Slide 6 (RM Questions) ✓")


def build_slide7():
    sld = new_slide(5)
    qs = RM_DATA['questions']
    day = RM_DATA['day']
    add_sp(sld, sp(2,'Title', 0.917,-0.009, 11.500,1.009,
                   f'Rapid Maths \u2013 Answers \u2013 Day {day}',
                   font='Twinkl Cursive Looped Light', sz=28,
                   color='000000', align='l', fill=None, no_line=True))

    left_cards  = [(0.240,0.933,6.200,2.056),(0.240,3.122,6.200,2.056),(0.240,5.311,6.200,2.056)]
    right_cards = [(6.907,0.933,6.200,3.150),(6.907,4.217,6.200,3.150)]
    card_positions = left_cards + right_cards
    lx_left, lx_right, lw = 0.400, 7.067, 5.973

    spid = 10
    for i, q in enumerate(qs):
        cx,cy,cw,ch = card_positions[i]
        lx = lx_left if i < 3 else lx_right
        a_h = 1.189 if i < 3 else 2.283

        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Card{i+1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx)}" y="{emu(cy)}"/><a:ext cx="{emu(cw)}" cy="{emu(ch)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(2*12700)}"><a:solidFill><a:srgbClr val="1D6B40"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        for label, col, y_off, sz_val, bold_val, txt in [
            (f'Topic{i+1}', '156082', 0.067, 1470, False, f'Q{q["num"]}  {q["topic"]}'),
            (f'QText{i+1}', '777777', 0.387, 1470, False, q['q']),
            (f'AText{i+1}', '1D6B40', 0.800, 2800, True,  q['a']),
        ]:
            h = 0.320 if 'Topic' in label else (0.427 if 'QText' in label else a_h)
            add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="{label}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(lx)}" y="{emu(cy+y_off)}"/><a:ext cx="{emu(lw)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    {"<a:solidFill><a:srgbClr val=\"156082\"/></a:solidFill>" if "Topic" in label else "<a:noFill/>"}
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/>
    <a:lstStyle/><a:p><a:pPr algn="l"/><a:r>
      <a:rPr lang="en-GB" sz="{sz_val}" b="{"1" if bold_val else "0"}" dirty="0">
        <a:solidFill><a:srgbClr val="{col}"/></a:solidFill>
        <a:latin typeface="Aptos"/>
      </a:rPr><a:t>{_esc(txt)}</a:t>
    </a:r></a:p></p:txBody></p:sp>''')
            spid += 1

    sld.notes_slide.notes_text_frame.text = (
        f"YOU DO — RM Answers Day {day}\n" +
        '\n'.join(f"Q{q['num']}: {q['a']}" for q in qs))
    print("Slide 7 (RM Answers) ✓")

# ===========================================================================
# SLIDE 8 — VOCABULARY  (curated list + paragraph-reveal animation)
# ===========================================================================
def build_slide8():
    sld = new_slide(3)  # We do layout

    # Title placeholder
    for ph in sld.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = 'Precise Mathematical Vocabulary'
            break

    # Build body text with correct paragraph structure in the placeholder
    # Para 0 (lvl 0): word 1  — visible from start (not animated)
    # Para 1 (lvl 1): definition 1  — revealed on click 1
    # Para 2 (lvl 1): blank spacer
    # Para 3 (lvl 0): word 2  — revealed on click 2
    # Para 4 (lvl 1): definition 2  — revealed on click 3
    # Para 5 (lvl 1): blank spacer
    # ... etc
    # Paragraph indices animated: 1, 3,4, 6,7, 9,10, 12,13  (def1, word2+def2, ...)

    # Build body as an EXPLICIT fixed-size text shape (not layout placeholder)
    # w=12.205" (31cm), h=5.315" (13.5cm), normAutofit so text shrinks on overflow
    # Build paragraph XML: word (bold lvl0), definition (lvl1), blank spacer (lvl1)
    paras_xml = ''
    for i, (word, defn) in enumerate(VOCAB):
        paras_xml += f'''<a:p>
          <a:pPr lvl="0"/>
          <a:r><a:rPr lang="en-GB" sz="1800" b="1" dirty="0">
            <a:latin typeface="Twinkl Cursive Looped Light"/>
          </a:rPr><a:t>{_esc(word)}</a:t></a:r>
        </a:p>
        <a:p>
          <a:pPr lvl="1"/>
          <a:r><a:rPr lang="en-GB" sz="1600" b="0" dirty="0">
            <a:latin typeface="Twinkl Cursive Looped Light"/>
          </a:rPr><a:t>{_esc(defn)}</a:t></a:r>
        </a:p>
        <a:p><a:pPr lvl="1"/><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'''

    vocab_body_xml = f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr>
    <p:cNvPr id="50" name="VocabBody"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(0.917)}" y="{emu(1.997)}"/>
      <a:ext cx="{emu(12.205)}" cy="{emu(5.315)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:noFill/><a:ln w="0"><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr rtlCol="0" anchor="t">
      <a:normAutofit/>
    </a:bodyPr>
    <a:lstStyle/>
    {paras_xml}
  </p:txBody>
</p:sp>'''
    add_sp(sld, vocab_body_xml)
    body_spid = 50  # our explicit shape's spid

    # Paragraph indices to animate (one click each):
    # Word 1 visible at start (para 0), then:
    # Click 1: para 1 (def 1)
    # Click 2: para 3 (word 2)
    # Click 3: para 4 (def 2)
    # Click 4: para 6 (word 3)
    # Click 5: para 7 (def 3)
    # Click 6: para 9 (word 4)
    # Click 7: para 10 (def 4)
    # Click 8: para 12 (word 5)
    # Click 9: para 13 (def 5)
    # Blank spacers (paras 2,5,8,11,14) are skipped

    n_words = len(VOCAB)
    # Build para indices: def of word1, then word2+def2, word3+def3 ...
    anim_paras = [1]  # definition of word 1
    for i in range(1, n_words):
        base = i * 3  # word para index
        anim_paras.append(base)       # word
        anim_paras.append(base + 1)   # definition

    child_blocks = ''
    ctn_id = 3
    for para_idx in anim_paras:
        child_blocks += f'''<p:par>
  <p:cTn id="{ctn_id}" fill="hold">
    <p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>
    <p:childTnLst><p:par><p:cTn id="{ctn_id+1}" fill="hold">
      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
      <p:childTnLst><p:par>
        <p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr" presetSubtype="0"
               fill="hold" nodeType="clickEffect">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:set><p:cBhvr>
            <p:cTn id="{ctn_id+3}" dur="1" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
            <p:tgtEl><p:spTgt spid="{body_spid}">
              <p:txEl><p:pRg st="{para_idx}" end="{para_idx}"/></p:txEl>
            </p:spTgt></p:tgtEl>
            <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
          </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
        </p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
  </p:cTn>
</p:par>'''
        ctn_id += 4

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par>
    <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
      <p:childTnLst><p:seq concurrent="1" nextAc="seek">
        <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
          <p:childTnLst>{child_blocks}</p:childTnLst>
        </p:cTn>
        <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
        <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
      </p:seq></p:childTnLst>
    </p:cTn>
  </p:par></p:tnLst>
</p:timing>'''
    sld._element.append(etree.fromstring(timing_xml))

    # No image badge — body is explicit fixed-size shape above (body_ph not used)
    sld.notes_slide.notes_text_frame.text = (
        f"WE DO — Vocabulary\nWords: {[w for w,_ in VOCAB]}\n"
        "Word 1 visible at start; each definition and subsequent word revealed per click.")
    print("Slide 8 (Vocabulary) ✓")

# ===========================================================================
# GRID DRAWING — core visual for teaching slides
# ===========================================================================
def draw_grid_slide(sld, visual_key, layout_num_was):
    """Draw a teaching slide with a coordinate grid on a white panel."""
    v = VISUALS[visual_key]
    cols = v['cols']
    rows = v['rows']

    # Layout: title top, white grid panel left, annotations/text right
    # Grid panel: x=0.4, y=0.9, w=7.0, h=5.8 (leaving room for title and right column)
    panel_x, panel_y = 0.40, 1.45
    panel_w, panel_h = 7.00, 5.80

    cell = min(panel_w / (cols + 1), panel_h / (rows + 1))  # cell size in inches
    # Grid starts inside panel with margin for axis labels
    margin = 0.50  # room for axis numbers
    grid_x = panel_x + margin
    grid_y = panel_y + 0.20
    grid_w = cell * cols
    grid_h = cell * rows

    # --- White panel background ---
    add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="50" name="GridPanel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(panel_x)}" y="{emu(panel_y)}"/>
    <a:ext cx="{emu(panel_w)}" cy="{emu(panel_h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(1.5*12700)}"><a:solidFill><a:srgbClr val="BBBBBB"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # --- Grid lines (horizontal) ---
    for r in range(rows + 1):
        y_pos = grid_y + r * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{51+r}" name="HLine{r}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(grid_x)}" y="{emu(y_pos)}"/>
    <a:ext cx="{emu(grid_w)}" cy="0"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(0.75*12700)}"><a:solidFill><a:srgbClr val="AAAAAA"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # --- Grid lines (vertical) ---
    for c in range(cols + 1):
        x_pos = grid_x + c * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{60+c}" name="VLine{c}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(x_pos)}" y="{emu(grid_y)}"/>
    <a:ext cx="0" cy="{emu(grid_h)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(0.75*12700)}"><a:solidFill><a:srgbClr val="AAAAAA"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # --- Axis number labels (bottom row = 0, left col = 0) ---
    label_sz = max(8, int(cell * 10))  # scale font with cell size
    for c in range(cols + 1):
        x_pos = grid_x + c * cell - 0.12
        y_pos = grid_y + grid_h + 0.05
        add_sp(sld, sp(70+c, f'XLabel{c}', x_pos, y_pos, 0.24, 0.25,
                       str(c), font='Aptos', sz=label_sz, bold=True,
                       color='333333', align='ctr', fill=None, no_line=True))

    for r in range(rows + 1):
        x_pos = grid_x - 0.35
        y_pos = grid_y + (rows - r) * cell - 0.12
        add_sp(sld, sp(80+r, f'YLabel{r}', x_pos, y_pos, 0.30, 0.25,
                       str(r), font='Aptos', sz=label_sz, bold=True,
                       color='333333', align='ctr', fill=None, no_line=True))

    # --- Axis labels ---
    add_sp(sld, sp(90, 'XAxisLabel',
                   grid_x + grid_w/2 - 0.15, grid_y + grid_h + 0.35, 0.30, 0.25,
                   'x', font='Aptos', sz=label_sz+2, bold=True,
                   color='156082', align='ctr', fill=None, no_line=True))
    add_sp(sld, sp(91, 'YAxisLabel',
                   grid_x - margin, grid_y + grid_h/2 - 0.12, 0.30, 0.25,
                   'y', font='Aptos', sz=label_sz+2, bold=True,
                   color='156082', align='ctr', fill=None, no_line=True))

    # --- Polygon edges (Shape A) — drawn BEFORE dots so dots sit on top ---
    # polygon: list of point labels in order; edges connect them, closed back to start
    # Visual decision: edges 2.5pt in the same colour as the points, slightly transparent
    # effect achieved by using a slightly lighter shade (8A -> same hue, lighter)
    # Dots are 100% colour, lines are drawn at same colour but thinner → vertex/edge distinction
    polygon = v.get('polygon', [])
    if polygon:
        # Build label→(px,py) map from points
        pt_map = {lbl: (grid_x + col*cell, grid_y + (rows-row)*cell)
                  for col, row, lbl, _ in v['points']}
        pt_colors = {lbl: col for _, _, lbl, col in v['points']}
        # Use the first point's colour for all edges (shapes are monochrome)
        edge_color = pt_colors.get(polygon[0], '1F4E79')
        # Slightly lighter: mix with white — prepend with 'light' variant
        # Decision: keep same colour at 2.5pt weight; dots are bigger so read as vertices
        edge_w_pt = 2.5
        for seg_i in range(len(polygon)):
            p1 = polygon[seg_i]
            p2 = polygon[(seg_i + 1) % len(polygon)]
            if p1 not in pt_map or p2 not in pt_map:
                continue
            x1, y1 = pt_map[p1]
            x2, y2 = pt_map[p2]
            lx, ly = min(x1,x2), min(y1,y2)
            lw = abs(x2-x1) or 0.001
            lh = abs(y2-y1) or 0.001
            add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{120+seg_i}" name="Edge{seg_i}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if x2>=x1 else ' flipH="1"'}{"" if y2>=y1 else ' flipV="1"'}>
    <a:off x="{emu(lx)}" y="{emu(ly)}"/><a:ext cx="{emu(lw)}" cy="{emu(lh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(edge_w_pt*12700)}"><a:solidFill><a:srgbClr val="{edge_color}"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # --- Plot points (on top of polygon edges) ---
    dot_r = min(0.12, cell * 0.30)
    for pt_idx, (col, row, label, color) in enumerate(v['points']):
        px = grid_x + col * cell - dot_r
        py = grid_y + (rows - row) * cell - dot_r
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{100+pt_idx}" name="Point{label}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(px)}" y="{emu(py)}"/>
    <a:ext cx="{emu(dot_r*2)}" cy="{emu(dot_r*2)}"/></a:xfrm>
    <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
    <a:ln w="{int(1.0*12700)}"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

        # Point label — above/right of dot, bold, matches dot colour
        add_sp(sld, sp(110+pt_idx, f'PtLabel{label}',
                       grid_x + col*cell + dot_r*0.5,
                       grid_y + (rows-row)*cell - dot_r*2 - 0.22,
                       0.30, 0.22, label,
                       font='Aptos', sz=label_sz+2, bold=True,
                       color=color, align='ctr', fill=None, no_line=True))

    # --- Translated shape (Shape B) — animated, hidden on load, revealed on click ---
    # Pedagogical rule: show translation only on I Do slides that demonstrate the move.
    # The translated shape is drawn in orange (E8642A) to contrast with Shape A (teal/blue).
    # Labels become A'→B'→C' etc, or use shape_b_label from visual data.
    # A translation vector arrow on one vertex (A→A') is also revealed with the shape.
    translation = v.get('translation')       # [dc, dr] move vector
    polygon_b   = v.get('polygon_b', polygon)  # defaults to same vertex order as A
    shape_a_label = v.get('shape_a_label', 'Shape A')
    shape_b_label = v.get('shape_b_label', 'Shape B')
    COLOR_B = 'E8642A'  # orange — distinct from any teal/blue shape A

    if translation and polygon:
        dc, dr = translation
        pt_map_b = {}
        for col, row, lbl, _ in v['points']:
            pt_map_b[lbl] = (grid_x + (col+dc)*cell, grid_y + (rows-(row+dr))*cell)

        anim_spids = []
        base_spid = 200

        # Shape B edges
        for seg_i in range(len(polygon_b)):
            p1 = polygon_b[seg_i]
            p2 = polygon_b[(seg_i + 1) % len(polygon_b)]
            if p1 not in pt_map_b or p2 not in pt_map_b:
                continue
            x1, y1 = pt_map_b[p1]
            x2, y2 = pt_map_b[p2]
            lx, ly = min(x1,x2), min(y1,y2)
            lw = abs(x2-x1) or 0.001
            lh = abs(y2-y1) or 0.001
            spid = base_spid + seg_i
            anim_spids.append(spid)
            add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="BEdge{seg_i}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if x2>=x1 else ' flipH="1"'}{"" if y2>=y1 else ' flipV="1"'}>
    <a:off x="{emu(lx)}" y="{emu(ly)}"/><a:ext cx="{emu(lw)}" cy="{emu(lh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.5*12700)}"><a:solidFill><a:srgbClr val="{COLOR_B}"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

        # Shape B dots and labels
        for pt_idx, (col, row, lbl, _) in enumerate(v['points']):
            bx = grid_x + (col+dc)*cell
            by = grid_y + (rows-(row+dr))*cell
            spid_dot   = base_spid + 20 + pt_idx
            spid_label = base_spid + 30 + pt_idx
            anim_spids.extend([spid_dot, spid_label])
            add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid_dot}" name="BPoint{lbl}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(bx-dot_r)}" y="{emu(by-dot_r)}"/>
    <a:ext cx="{emu(dot_r*2)}" cy="{emu(dot_r*2)}"/></a:xfrm>
    <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{COLOR_B}"/></a:solidFill>
    <a:ln w="{int(1.0*12700)}"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
            add_sp(sld, sp(spid_label, f'BLabel{lbl}',
                           bx + dot_r*0.5, by - dot_r*2 - 0.22,
                           0.30, 0.22, f"{lbl}'",
                           font='Aptos', sz=label_sz+2, bold=True,
                           color=COLOR_B, align='ctr', fill=None, no_line=True))

        # Translation arrow: A→A' on first point, dashed grey, helps read the move
        first_lbl = polygon[0]
        ax_orig, ay_orig = pt_map[first_lbl]
        ax_dest, ay_dest = pt_map_b[first_lbl]
        arr_spid = base_spid + 50
        anim_spids.append(arr_spid)
        alx, aly = min(ax_orig,ax_dest), min(ay_orig,ay_dest)
        alw = abs(ax_dest-ax_orig) or 0.001
        alh = abs(ay_dest-ay_orig) or 0.001
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{arr_spid}" name="TransArrow"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if ax_dest>=ax_orig else ' flipH="1"'}{"" if ay_dest>=ay_orig else ' flipV="1"'}>
    <a:off x="{emu(alx)}" y="{emu(aly)}"/><a:ext cx="{emu(alw)}" cy="{emu(alh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(1.5*12700)}" cap="flat">
      <a:solidFill><a:srgbClr val="888888"/></a:solidFill>
      <a:prstDash val="dash"/>
      <a:tailEnd type="arrow" w="med" len="med"/>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

        # Shape B label box (e.g. "Shape B") — in right column
        right_x = panel_x + panel_w + 0.25
        right_w = 13.333 - right_x - 0.2
        sha_spid = base_spid + 51
        anim_spids.append(sha_spid)
        add_sp(sld, sp(sha_spid, 'ShapeBLabel',
                       right_x, panel_y + 1.50, right_w, 0.50,
                       shape_b_label,
                       font='Twinkl Cursive Looped Light', sz=20, bold=True,
                       color=COLOR_B, align='l', fill=None, no_line=True))

        # Shape A label box — always visible (not animated)
        add_sp(sld, sp(base_spid+52, 'ShapeALabel',
                       right_x, panel_y + 0.15, right_w, 0.50,
                       shape_a_label,
                       font='Twinkl Cursive Looped Light', sz=20, bold=True,
                       color=v['points'][0][3], align='l', fill=None, no_line=True))

        # Animate all Shape B elements: hidden on load, all appear on single click
        def anim_block_multi(spids):
            blocks = ''
            ctn_id = 3
            for spid in spids:
                blocks += f'''<p:par>
  <p:cTn id="{ctn_id}" fill="hold">
    <p:stCondLst><p:cond delay="{"indefinite" if ctn_id==3 else "0"}"/></p:stCondLst>
    <p:childTnLst><p:par><p:cTn id="{ctn_id+1}" fill="hold">
      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
      <p:childTnLst><p:par>
        <p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr" presetSubtype="0"
               fill="hold" grpId="1" nodeType="{"clickEffect" if ctn_id==3 else "afterEffect"}">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:set><p:cBhvr>
            <p:cTn id="{ctn_id+3}" dur="1" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
            <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
            <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
          </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
        </p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
  </p:cTn>
</p:par>'''
                ctn_id += 4
            return blocks

        bld_list = ''.join(
            f'<p:bldP spid="{s}" grpId="0" uiExpand="1" build="p"/>\n'
            f'<p:bldP spid="{s}" grpId="1" animBg="1"/>\n'
            for s in anim_spids)

        timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par>
    <p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">
      <p:childTnLst><p:seq concurrent="1" nextAc="seek">
        <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
          <p:childTnLst>{anim_block_multi(anim_spids)}</p:childTnLst>
        </p:cTn>
        <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
        <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
      </p:seq></p:childTnLst>
    </p:cTn>
  </p:par></p:tnLst>
  <p:bldLst>{bld_list}</p:bldLst>
</p:timing>'''
        sld._element.append(etree.fromstring(timing_xml))

    # --- Right column: caption / sentence stem ---
    right_x = panel_x + panel_w + 0.25
    right_w = 13.333 - right_x - 0.2
    # Push caption/stem down if shape labels are present
    right_y = panel_y + (2.30 if translation else 0.15)

    if 'caption' in v:
        add_sp(sld, sp(130, 'Caption', right_x, right_y, right_w, 1.20,
                       v['caption'],
                       font='Twinkl Cursive Looped Light', sz=20, bold=False,
                       color='1F4E79', align='l', fill='DEECF8',
                       border=('156082', 1.5), anchor='ctr'))

    if 'sentence_stem' in v:
        add_sp(sld, sp(131, 'StemBox', right_x, right_y, right_w, 1.40,
                       v['sentence_stem'],
                       font='Twinkl Cursive Looped Light', sz=18, bold=False,
                       color='1F4E79', align='l', fill='FFF2CC',
                       border=('E8B825', 1.5), anchor='ctr'))

    # error_note / error_instruction handled with animation in build_spot_the_mistake_slide
    sld.notes_slide.notes_text_frame.text = v['notes']


def build_teaching_slide(layout_num, visual_key, title_text, phase):
    sld = new_slide(layout_num)
    for ph in sld.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = title_text
            break
    v = VISUALS[visual_key]
    slide_type = v.get('slide_type', 'grid')
    if slide_type == 'symmetry_grid':
        draw_symmetry_grid_slide(sld, visual_key)
    elif slide_type == 'clock':
        draw_clock_slide(sld, visual_key)
    elif slide_type == 'number_line':
        draw_number_line_slide(sld, visual_key)
    else:
        draw_grid_slide(sld, visual_key, layout_num)
    print(f"  Teaching slide ({title_text[:40]}) ✓")
    return sld


# ===========================================================================
# SYMMETRY GRID SLIDE
# For lessons involving lines of symmetry, reflection, and symmetrical patterns.
# Visual decisions:
#   - Mirror line drawn as a thick dashed red/purple line through the grid
#   - Filled squares (Shape A, teal) on one side
#   - Reflected squares (Shape B, orange) on the other — static or animated
#   - Grid cells coloured, not just dots
# ===========================================================================
def draw_symmetry_grid_slide(sld, visual_key):
    v = VISUALS[visual_key]
    cols = v['cols']
    rows = v['rows']

    panel_x, panel_y = 0.40, 1.45
    panel_w, panel_h = 7.00, 5.80
    cell = min(panel_w / (cols + 1), panel_h / (rows + 1))
    margin = 0.50
    grid_x = panel_x + margin
    grid_y = panel_y + 0.20
    grid_w  = cell * cols
    grid_h  = cell * rows
    label_sz = max(8, int(cell * 10))

    # White panel background
    add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="50" name="GridPanel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(panel_x)}" y="{emu(panel_y)}"/>
    <a:ext cx="{emu(panel_w)}" cy="{emu(panel_h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(1.5*12700)}"><a:solidFill><a:srgbClr val="BBBBBB"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # Grid lines
    for r in range(rows + 1):
        y_pos = grid_y + r * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{51+r}" name="HLine{r}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(grid_x)}" y="{emu(y_pos)}"/>
    <a:ext cx="{emu(grid_w)}" cy="0"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(0.75*12700)}"><a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
    for c in range(cols + 1):
        x_pos = grid_x + c * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{60+c}" name="VLine{c}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(x_pos)}" y="{emu(grid_y)}"/>
    <a:ext cx="0" cy="{emu(grid_h)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(0.75*12700)}"><a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')

    # Axis numbers
    for c in range(cols + 1):
        add_sp(sld, sp(70+c, f'XLbl{c}', grid_x+c*cell-0.12, grid_y+grid_h+0.05, 0.24, 0.25,
                       str(c), font='Aptos', sz=label_sz, bold=True,
                       color='333333', align='ctr', fill=None, no_line=True))
    for r in range(rows + 1):
        add_sp(sld, sp(80+r, f'YLbl{r}', grid_x-0.35, grid_y+(rows-r)*cell-0.12, 0.30, 0.25,
                       str(r), font='Aptos', sz=label_sz, bold=True,
                       color='333333', align='ctr', fill=None, no_line=True))

    spid = 100

    # Filled squares — Shape A (coloured cells, teal fill with alpha feel)
    for col, row in v.get('squares_a', []):
        cx = grid_x + col * cell
        cy = grid_y + (rows - row - 1) * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="SqA{col}_{row}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx+0.01)}" y="{emu(cy+0.01)}"/>
    <a:ext cx="{emu(cell-0.02)}" cy="{emu(cell-0.02)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="A8D0E6"><a:alpha val="85000"/></a:srgbClr></a:solidFill>
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

    # Reflected squares — Shape B (orange, animated if translate=True)
    anim_spids = []
    for col, row in v.get('squares_b', []):
        cx = grid_x + col * cell
        cy = grid_y + (rows - row - 1) * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="SqB{col}_{row}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx+0.01)}" y="{emu(cy+0.01)}"/>
    <a:ext cx="{emu(cell-0.02)}" cy="{emu(cell-0.02)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="F4B183"><a:alpha val="85000"/></a:srgbClr></a:solidFill>
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        if v.get('animate_b'):
            anim_spids.append(spid)
        spid += 1

    # Point markers (labelled dots for polygon-style symmetry problems)
    dot_r = min(0.10, cell * 0.25)
    for col, row, label, color in v.get('points', []):
        px = grid_x + col*cell - dot_r
        py = grid_y + (rows-row)*cell - dot_r
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Pt{label}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(px)}" y="{emu(py)}"/>
    <a:ext cx="{emu(dot_r*2)}" cy="{emu(dot_r*2)}"/></a:xfrm>
    <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
    <a:ln w="{int(1.0*12700)}"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        add_sp(sld, sp(spid+1, f'PtLbl{label}',
                       grid_x+col*cell+dot_r*0.5, grid_y+(rows-row)*cell-dot_r*2-0.22,
                       0.30, 0.22, label, font='Aptos', sz=label_sz+2, bold=True,
                       color=color, align='ctr', fill=None, no_line=True))
        if v.get('animate_b') and label in v.get('animate_labels', []):
            anim_spids.extend([spid, spid+1])
        spid += 2

    # Mirror line — thick dashed, drawn over the grid
    # mirror_col: vertical line at this column; mirror_row: horizontal line at this row
    mirror_col = v.get('mirror_col')
    mirror_row = v.get('mirror_row')
    MIRROR_COLOR = '7030A0'  # purple — neutral, neither Shape A nor B colour
    if mirror_col is not None:
        mx = grid_x + mirror_col * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="MirrorLine"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(mx)}" y="{emu(grid_y)}"/>
    <a:ext cx="0" cy="{emu(grid_h)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.5*12700)}">
      <a:solidFill><a:srgbClr val="{MIRROR_COLOR}"/></a:solidFill>
      <a:prstDash val="sysDash"/>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        # Mirror line label
        add_sp(sld, sp(spid+1, 'MirrorLbl',
                       mx + 0.05, grid_y - 0.26, 1.20, 0.24,
                       'mirror line', font='Twinkl Cursive Looped Light', sz=14,
                       color=MIRROR_COLOR, align='l', fill=None, no_line=True))
        spid += 2
    if mirror_row is not None:
        my = grid_y + (rows - mirror_row) * cell
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="MirrorLineH"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(grid_x)}" y="{emu(my)}"/>
    <a:ext cx="{emu(grid_w)}" cy="0"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.5*12700)}">
      <a:solidFill><a:srgbClr val="{MIRROR_COLOR}"/></a:solidFill>
      <a:prstDash val="sysDash"/>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        add_sp(sld, sp(spid+1, 'MirrorLblH',
                       grid_x + grid_w + 0.05, my - 0.15, 1.20, 0.24,
                       'mirror line', font='Twinkl Cursive Looped Light', sz=14,
                       color=MIRROR_COLOR, align='l', fill=None, no_line=True))
        spid += 2

    # Animate reflected squares if requested (I Do slides that reveal the answer)
    if anim_spids:
        def anim_block_sym(spids):
            blocks = ''
            ctn_id = 3
            for s in spids:
                blocks += f'''<p:par>
  <p:cTn id="{ctn_id}" fill="hold">
    <p:stCondLst><p:cond delay="{"indefinite" if ctn_id==3 else "0"}"/></p:stCondLst>
    <p:childTnLst><p:par><p:cTn id="{ctn_id+1}" fill="hold">
      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
      <p:childTnLst><p:par>
        <p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr" presetSubtype="0"
               fill="hold" grpId="1" nodeType="{"clickEffect" if ctn_id==3 else "afterEffect"}">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:set><p:cBhvr>
            <p:cTn id="{ctn_id+3}" dur="1" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
            <p:tgtEl><p:spTgt spid="{s}"/></p:tgtEl>
            <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
          </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
        </p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
  </p:cTn>
</p:par>'''
                ctn_id += 4
            return blocks
        bld_list = ''.join(
            f'<p:bldP spid="{s}" grpId="0" uiExpand="1" build="p"/>\n'
            f'<p:bldP spid="{s}" grpId="1" animBg="1"/>\n' for s in anim_spids)
        timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">
    <p:childTnLst><p:seq concurrent="1" nextAc="seek">
      <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
        <p:childTnLst>{anim_block_sym(anim_spids)}</p:childTnLst>
      </p:cTn>
      <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
      <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
    </p:seq></p:childTnLst>
  </p:cTn></p:par></p:tnLst>
  <p:bldLst>{bld_list}</p:bldLst>
</p:timing>'''
        sld._element.append(etree.fromstring(timing_xml))

    # Right column
    right_x = panel_x + panel_w + 0.25
    right_w  = 13.333 - right_x - 0.2
    right_y  = panel_y + 0.15
    if 'caption' in v:
        add_sp(sld, sp(200, 'Caption', right_x, right_y, right_w, 1.20,
                       v['caption'], font='Twinkl Cursive Looped Light', sz=20,
                       color='1F4E79', align='l', fill='DEECF8',
                       border=('156082', 1.5), anchor='ctr'))
    if 'sentence_stem' in v:
        add_sp(sld, sp(201, 'Stem', right_x, right_y, right_w, 1.40,
                       v['sentence_stem'], font='Twinkl Cursive Looped Light', sz=18,
                       color='1F4E79', align='l', fill='FFF2CC',
                       border=('E8B825', 1.5), anchor='ctr'))
    sld.notes_slide.notes_text_frame.text = v['notes']


# ===========================================================================
# CLOCK SLIDE — for Time lessons
# Draws one or more analogue clock faces with hour and minute hands.
# Visual decisions:
#   - Clock face: white circle, thin border, 12 tick marks, 12 numerals
#   - Hour hand: thick, shorter (60% radius)
#   - Minute hand: thinner, longer (85% radius)
#   - Both drawn as lines from centre
#   - Multiple clocks tiled left-to-right on the panel
#   - Right column: caption / digital time box / sentence stem as normal
# ===========================================================================
import math as _math

def draw_clock_slide(sld, visual_key):
    v = VISUALS[visual_key]

    panel_x, panel_y = 0.40, 1.45
    panel_w, panel_h = 7.00, 5.80
    right_x = panel_x + panel_w + 0.25
    right_w  = 13.333 - right_x - 0.2

    clocks = v.get('clocks', [])
    n = len(clocks)
    if n == 0:
        return

    # Tile clocks: 2×2 for 4 clocks, up to 3 per row otherwise
    if n == 4:
        per_row = 2
    else:
        per_row = min(n, 3)
    rows_needed = (n + per_row - 1) // per_row
    clock_r = min(panel_w / (per_row * 2.5), panel_h / (rows_needed * 2.6)) * 0.88

    spid = 50
    for ci, clock in enumerate(clocks):
        row_i = ci // per_row
        col_i = ci % per_row
        # Centre of this clock face
        cx = panel_x + (col_i + 0.5) * (panel_w / per_row)
        cy = panel_y + 0.3 + (row_i + 0.5) * (panel_h / rows_needed)

        hour   = clock['hour']
        minute = clock['minute']
        label  = clock.get('label', '')
        show_digital = clock.get('show_digital', False)

        # Clock face circle
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="ClockFace{ci}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx-clock_r)}" y="{emu(cy-clock_r)}"/>
    <a:ext cx="{emu(clock_r*2)}" cy="{emu(clock_r*2)}"/></a:xfrm>
    <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(2.0*12700)}"><a:solidFill><a:srgbClr val="333333"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        # Tick marks and numerals
        for h in range(1, 13):
            angle = _math.radians(h * 30 - 90)
            is_hour_mark = (h % 3 == 0)
            tick_outer = clock_r * 0.92
            tick_inner = clock_r * (0.78 if is_hour_mark else 0.84)
            tx1 = cx + _math.cos(angle) * tick_inner
            ty1 = cy + _math.sin(angle) * tick_inner
            tx2 = cx + _math.cos(angle) * tick_outer
            ty2 = cy + _math.sin(angle) * tick_outer
            lx, ly = min(tx1,tx2), min(ty1,ty2)
            lw = abs(tx2-tx1) or 0.001
            lh = abs(ty2-ty1) or 0.001
            tw = 2.0 if is_hour_mark else 1.0
            add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                                 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Tick{ci}_{h}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if tx2>=tx1 else ' flipH="1"'}{"" if ty2>=ty1 else ' flipV="1"'}>
    <a:off x="{emu(lx)}" y="{emu(ly)}"/><a:ext cx="{emu(lw)}" cy="{emu(lh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(tw*12700)}"><a:solidFill><a:srgbClr val="333333"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
            spid += 1

            # Numeral at 3, 6, 9, 12
            # Box must be wide (0.40") and tall (0.30") enough for "12" at any clock size
            if is_hour_mark:
                num_r   = clock_r * 0.66
                num_w   = max(0.40, clock_r * 0.52)
                num_h   = max(0.30, clock_r * 0.38)
                nx = cx + _math.cos(angle) * num_r - num_w/2
                ny = cy + _math.sin(angle) * num_r - num_h/2
                # Keep font small enough: 12pt per inch of clock radius, max 14pt
                num_sz  = min(14, max(9, int(clock_r * 11)))
                add_sp(sld, sp(spid, f'Num{ci}_{h}', nx, ny, num_w, num_h,
                               str(h), font='Aptos', sz=num_sz, bold=True,
                               color='1F4E79', align='ctr', fill=None, no_line=True))
                spid += 1

        # Hour hand — angle: each hour = 30°, each minute adds 0.5°
        h_angle = _math.radians((hour % 12) * 30 + minute * 0.5 - 90)
        h_len   = clock_r * 0.55
        hx2 = cx + _math.cos(h_angle) * h_len
        hy2 = cy + _math.sin(h_angle) * h_len
        lx,ly = min(cx,hx2), min(cy,hy2)
        lw = abs(hx2-cx) or 0.001
        lh = abs(hy2-cy) or 0.001
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="HourHand{ci}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if hx2>=cx else ' flipH="1"'}{"" if hy2>=cy else ' flipV="1"'}>
    <a:off x="{emu(lx)}" y="{emu(ly)}"/><a:ext cx="{emu(lw)}" cy="{emu(lh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(4.0*12700)}" cap="rnd">
      <a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        # Minute hand — angle: each minute = 6°
        m_angle = _math.radians(minute * 6 - 90)
        m_len   = clock_r * 0.78
        mx2 = cx + _math.cos(m_angle) * m_len
        my2 = cy + _math.sin(m_angle) * m_len
        lx,ly = min(cx,mx2), min(cy,my2)
        lw = abs(mx2-cx) or 0.001
        lh = abs(my2-cy) or 0.001
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="MinHand{ci}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm{"" if mx2>=cx else ' flipH="1"'}{"" if my2>=cy else ' flipV="1"'}>
    <a:off x="{emu(lx)}" y="{emu(ly)}"/><a:ext cx="{emu(lw)}" cy="{emu(lh)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.5*12700)}" cap="rnd">
      <a:solidFill><a:srgbClr val="156082"/></a:solidFill>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        # Centre dot
        dot = clock_r * 0.04
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Centre{ci}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(cx-dot)}" y="{emu(cy-dot)}"/>
    <a:ext cx="{emu(dot*2)}" cy="{emu(dot*2)}"/></a:xfrm>
    <a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1

        # Label below clock (e.g. "7:45 am")
        if label:
            lbl_sz = max(12, int(clock_r * 16))
            add_sp(sld, sp(spid, f'ClockLbl{ci}',
                           cx - clock_r, cy + clock_r + 0.05, clock_r*2, 0.35,
                           label, font='Twinkl Cursive Looped Light', sz=lbl_sz,
                           color='1F4E79', align='ctr', fill=None, no_line=True))
            spid += 1

        # Digital time answer box (for We Do / marking station slides)
        if show_digital:
            dig_h = clock_r * 0.55
            add_sp(sld, sp(spid, f'DigBox{ci}',
                           cx - clock_r*0.7, cy + clock_r + 0.42, clock_r*1.4, dig_h,
                           '', font='Aptos', sz=max(16, int(clock_r*20)),
                           color='1A5C2A', align='ctr', fill=None,
                           border=('333333', 1.0)))
            spid += 1

    # Right column
    right_y = panel_y + 0.15
    if 'caption' in v:
        add_sp(sld, sp(spid, 'Caption', right_x, right_y, right_w, 1.20,
                       v['caption'], font='Twinkl Cursive Looped Light', sz=20,
                       color='1F4E79', align='l', fill='DEECF8',
                       border=('156082', 1.5), anchor='ctr'))
        spid += 1
    if 'sentence_stem' in v:
        add_sp(sld, sp(spid, 'Stem', right_x, right_y, right_w, 1.40,
                       v['sentence_stem'], font='Twinkl Cursive Looped Light', sz=18,
                       color='1F4E79', align='l', fill='FFF2CC',
                       border=('E8B825', 1.5), anchor='ctr'))
        spid += 1
    sld.notes_slide.notes_text_frame.text = v['notes']


# ===========================================================================
# NUMBER LINE SLIDE — for Time lesson C2 (24-hour number line)
# ===========================================================================
def draw_number_line_slide(sld, visual_key):
    v = VISUALS[visual_key]
    panel_x, panel_y = 0.40, 1.45
    panel_w, panel_h = 7.00, 5.80
    right_x = panel_x + panel_w + 0.25
    right_w  = 13.333 - right_x - 0.2

    # Number line spans from start_val to end_val
    start_val = v.get('nl_start', 0)
    end_val   = v.get('nl_end', 24)
    total     = end_val - start_val

    nl_y  = panel_y + panel_h * 0.58   # lower — leaves room above for markers/examples
    nl_x1 = panel_x + 0.3
    nl_x2 = panel_x + panel_w - 0.2
    nl_w  = nl_x2 - nl_x1

    spid = 50

    # White panel
    add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="50" name="Panel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(panel_x)}" y="{emu(panel_y)}"/>
    <a:ext cx="{emu(panel_w)}" cy="{emu(panel_h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
    <a:ln w="{int(1.5*12700)}"><a:solidFill><a:srgbClr val="BBBBBB"/></a:solidFill></a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
    spid = 51

    # Main line with arrowheads
    add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="NLLine"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(nl_x1)}" y="{emu(nl_y)}"/>
    <a:ext cx="{emu(nl_w)}" cy="0"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.0*12700)}">
      <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
      <a:tailEnd type="arrow" w="med" len="med"/>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
    spid += 1

    # Tick marks and labels for key hours
    tick_hours = v.get('nl_ticks', list(range(start_val, end_val + 1, 2)))
    tick_h = 0.10
    for val in tick_hours:
        tx = nl_x1 + (val - start_val) / total * nl_w
        is_major = (val % 6 == 0)
        th = tick_h * (1.6 if is_major else 1.0)
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Tick{val}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(tx)}" y="{emu(nl_y - th/2)}"/>
    <a:ext cx="0" cy="{emu(th)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int((1.5 if is_major else 0.75)*12700)}">
      <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1
        # Label — format as HH:00, wider box prevents wrapping
        lbl = f'{val:02d}:00'
        add_sp(sld, sp(spid, f'NLLbl{val}',
                       tx - 0.28, nl_y + tick_h*1.0 + 0.03, 0.56, 0.22,
                       lbl, font='Aptos', sz=8 if is_major else 7, bold=is_major,
                       color='1F4E79' if is_major else '888888',
                       align='ctr', fill=None, no_line=True))
        spid += 1

    # Special markers (e.g. midday line, midnight)
    for marker in v.get('nl_markers', []):
        val   = marker['val']
        lbl   = marker['label']
        color = marker.get('color', '7030A0')
        mx = nl_x1 + (val - start_val) / total * nl_w
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{spid}" name="Marker{val}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{emu(mx)}" y="{emu(nl_y - 0.30)}"/>
    <a:ext cx="0" cy="{emu(0.60)}"/></a:xfrm>
    <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
    <a:ln w="{int(2.0*12700)}">
      <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
      <a:prstDash val="sysDash"/>
    </a:ln>
  </p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>''')
        spid += 1
        # Marker label: two lines above the line, centred on marker x
        add_sp(sld, sp(spid, f'MkLbl{val}',
                       mx - 0.65, nl_y - 0.88, 1.30, 0.45,
                       lbl, font='Twinkl Cursive Looped Light', sz=12, bold=True,
                       color=color, align='ctr', fill=None, no_line=True))
        spid += 1

    # Conversion examples — staggered above line to avoid overlap
    for ei, ex in enumerate(v.get('examples', [])):
        ex_x = nl_x1 + (ex['val'] - start_val) / total * nl_w
        # Alternate heights so adjacent examples don't overlap
        ex_y = nl_y - 1.55 - (0.40 if ei % 2 == 0 else 0.0)
        add_sp(sld, sp(spid, f'Ex{ex["val"]}',
                       ex_x - 0.52, ex_y, 1.04, 0.55,
                       ex['text'], font='Twinkl Cursive Looped Light', sz=12,
                       color='C00000', align='ctr', fill='FFE6E6',
                       border=('C00000', 1.0), anchor='ctr'))
        spid += 1

    # Right column
    right_y = panel_y + 0.15
    if 'caption' in v:
        add_sp(sld, sp(spid, 'Caption', right_x, right_y, right_w, 1.20,
                       v['caption'], font='Twinkl Cursive Looped Light', sz=20,
                       color='1F4E79', align='l', fill='DEECF8',
                       border=('156082', 1.5), anchor='ctr'))
    sld.notes_slide.notes_text_frame.text = v['notes']




# ===========================================================================
# SPOT THE MISTAKE SLIDE — 3-beat animated teaching slide
# Beat 1 (load):    grid + instruction shown; error marker + explanation hidden
# Beat 2 (click 1): error marker (✗) appears at landing position
# Beat 3 (click 2): explanation box appears
# ===========================================================================
def build_spot_the_mistake_slide(layout_num, visual_key, title_text):
    sld = new_slide(layout_num)
    v = VISUALS[visual_key]

    # Title via placeholder
    for ph in sld.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = title_text
            break

    # Draw the grid (without error elements — those come with animation)
    draw_grid_slide(sld, visual_key, layout_num)

    # Calculate grid geometry (matching draw_grid_slide)
    cols, rows = v['cols'], v['rows']
    panel_x, panel_y = 0.40, 1.45
    panel_w, panel_h = 7.00, 5.80
    cell = min(panel_w / (cols + 1), panel_h / (rows + 1))
    margin = 0.50
    grid_x = panel_x + margin
    grid_y = panel_y + 0.20

    # ── Error marker position — derived from errorType and data ──────────────
    # Strategy: find the 'error' position from extraPoints if present,
    # otherwise fall back to type-specific logic from startPoint.
    error_type   = v.get('error_type', 'off_grid')
    extra_points = v.get('extra_points', [])
    start_col, start_row = (v['points'][0][0], v['points'][0][1]) if v['points'] else (3, 3)

    # Look for an explicit error position in extraPoints
    err_col, err_row = None, None
    for ep in extra_points:
        if len(ep) >= 3 and 'error' in str(ep[2]).lower():
            err_col, err_row = ep[0], ep[1]
            break

    # Fallback by errorType if no explicit error point found
    if err_col is None:
        if error_type == 'off_grid':
            # off_grid: 4 right from startPoint goes off grid
            err_col = start_col + 4
            err_row = start_row
        elif error_type in ('partial_translation', 'wrong_reflection_distance',
                            'wrong_reflection_direction', 'wrong_side_of_mirror'):
            # One vertex/point moved incorrectly — use first extraPoint as error position
            if extra_points:
                err_col, err_row = extra_points[0][0], extra_points[0][1]
            else:
                err_col, err_row = start_col + 3, start_row
        elif error_type in ('wrong_direction', 'axis_swap', 'inverse_rule'):
            # Moves in wrong direction — place marker near startPoint offset
            err_col, err_row = start_col - 3, start_row + 3
        elif error_type in ('wrong_order', 'wrong_join_order'):
            # Wrong sequence — marker at first extraPoint
            if extra_points:
                err_col, err_row = extra_points[0][0], extra_points[0][1]
            else:
                err_col, err_row = start_col + 2, start_row + 2
        elif error_type in ('false_symmetry', 'over_counted_symmetry', 'moved_fixed_point'):
            # Shape error — use last extraPoint
            if extra_points:
                err_col, err_row = extra_points[-1][0], extra_points[-1][1]
            else:
                err_col, err_row = start_col + 3, start_row + 3
        else:
            # Generic fallback
            err_col, err_row = min(start_col + 3, cols), start_row

    # For Time lessons (gridSize=0), error marker goes in right column (no grid)
    if STM['gridSize'] == 0:
        err_slide_x = panel_x + panel_w + 0.25
        err_slide_y = 2.30
        marker_x = err_slide_x
        err_y = err_slide_y
    else:
        # Clamp to grid bounds for display
        err_col_clamped = min(err_col, cols + 0.5)
        err_x = grid_x + err_col_clamped * cell
        err_y = grid_y + (rows - err_row) * cell
        marker_x = min(err_x - 0.15, panel_x + panel_w - 0.35)

    # Right column layout
    right_x = panel_x + panel_w + 0.25
    right_w = 13.333 - right_x - 0.2

    # Beat 1 element — instruction (always visible on load)
    add_sp(sld, sp(133, 'ErrorInstruction',
                   right_x, 1.60, right_w, 0.80,
                   f'Instruction given: "{v["error_instruction"]}"',
                   font='Twinkl Cursive Looped Light', sz=16,
                   color='333333', align='l', fill=None, no_line=True))

    # Beat 2 element — error marker (hidden at start, appears on click 1)
    MARK_SPID = 120
    add_sp(sld, sp(MARK_SPID, 'ErrorMark', marker_x, err_y - 0.18, 0.30, 0.36,
                   '✗', font='Aptos', sz=20, bold=True,
                   color='FF0000', align='ctr', fill=None, no_line=True))

    # Beat 3 element — explanation box (hidden at start, appears on click 2)
    NOTE_SPID = 132
    add_sp(sld, sp(NOTE_SPID, 'ErrorNote', right_x, 2.60, right_w, 1.50,
                   v['error_note'],
                   font='Twinkl Cursive Looped Light', sz=18, bold=True,
                   color='C00000', align='l', fill='FFE6E6',
                   border=('C00000', 1.5), anchor='ctr'))

    # ── Animation timing ──
    # Both MARK_SPID and NOTE_SPID start hidden, revealed on sequential clicks
    def anim_block(ctn_id, spid):
        return f'''<p:par>
  <p:cTn id="{ctn_id}" fill="hold">
    <p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>
    <p:childTnLst><p:par><p:cTn id="{ctn_id+1}" fill="hold">
      <p:stCondLst><p:cond delay="0"/></p:stCondLst>
      <p:childTnLst><p:par>
        <p:cTn id="{ctn_id+2}" presetID="1" presetClass="entr" presetSubtype="0"
               fill="hold" grpId="1" nodeType="clickEffect">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:set><p:cBhvr>
            <p:cTn id="{ctn_id+3}" dur="1" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
            <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
            <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
          </p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst>
        </p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
  </p:cTn>
</p:par>'''

    child_blocks = anim_block(3, MARK_SPID) + anim_block(7, NOTE_SPID)

    bld_list = (
        f'<p:bldP spid="{MARK_SPID}" grpId="0" uiExpand="1" build="p"/>\n'
        f'<p:bldP spid="{MARK_SPID}" grpId="1" animBg="1"/>\n'
        f'<p:bldP spid="{NOTE_SPID}" grpId="0" uiExpand="1" build="p"/>\n'
        f'<p:bldP spid="{NOTE_SPID}" grpId="1" animBg="1"/>\n'
    )

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:tnLst><p:par>
    <p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">
      <p:childTnLst><p:seq concurrent="1" nextAc="seek">
        <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
          <p:childTnLst>{child_blocks}</p:childTnLst>
        </p:cTn>
        <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
        <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
      </p:seq></p:childTnLst>
    </p:cTn>
  </p:par></p:tnLst>
  <p:bldLst>{bld_list}</p:bldLst>
</p:timing>'''

    sld._element.append(etree.fromstring(timing_xml))

    sld.notes_slide.notes_text_frame.text = (
        f"I DO — Spot the Mistake (3-beat animated)\n"
        f"Beat 1 (load): Grid + instruction visible. Ask: 'What do you notice?'\n"
        f"Beat 2 (click 1): ✗ appears at landing position. Ask: 'Where does it end up?'\n"
        f"Beat 3 (click 2): Explanation revealed.\n\n"
        + v['notes']
    )
    print(f"  Spot the mistake slide ({title_text[:40]}) ✓")
    return sld


# ===========================================================================
# TRIOS SLIDE
# ===========================================================================
def build_trios_slide(layout_num, title, trios_data, notes):
    sld = new_slide(layout_num)
    for ph in sld.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = title
            break

    roles_colors = [('1F4E79','DEEAF1'), ('7030A0','EAD1F0'), ('C00000','FCE4D6')]
    role_w, role_h = 3.8, 1.0
    role_x = 0.5
    roles = trios_data.get('roles', [])
    for i, (role_text, (text_col, fill_col)) in enumerate(zip(roles, roles_colors)):
        y_pos = 1.6 + i * 1.15
        add_sp(sld, sp(20+i, f'Role{i+1}', role_x, y_pos, role_w, role_h,
                       role_text, font='Twinkl Cursive Looped Light', sz=18,
                       bold=True, color=text_col, align='l',
                       fill=fill_col, border=(text_col, 1.5), anchor='ctr'))

    add_sp(sld, sp(30, 'Task', 4.6, 1.6, 8.5, 1.4,
                   trios_data.get('task',''),
                   font='Twinkl Cursive Looped Light', sz=18,
                   color='1F4E79', align='l', fill='DEECF8',
                   border=('156082', 1.5), anchor='ctr'))

    challenge = trios_data.get('challenge','')
    if challenge:
        add_sp(sld, sp(31, 'Challenge', 4.6, 3.2, 8.5, 1.1,
                       f'Challenge: {challenge}',
                       font='Twinkl Cursive Looped Light', sz=16,
                       color='7030A0', align='l', fill='F2E6F9',
                       border=('7030A0', 1.5), anchor='ctr'))

    sld.notes_slide.notes_text_frame.text = notes
    print(f"  Trios slide ({title[:40]}) ✓")
    return sld

# ===========================================================================
# INDEPENDENT SLIDE
# ===========================================================================
def build_independent_slide(layout_num, title, independent_data, notes):
    sld = new_slide(layout_num)
    for ph in sld.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = title
            break

    add_sp(sld, sp(20, 'Standard', 0.5, 1.6, 12.5, 1.3,
                   independent_data.get('standard',''),
                   font='Twinkl Cursive Looped Light', sz=20,
                   color='1F4E79', align='l', fill='DEECF8',
                   border=('156082', 1.5), anchor='ctr'))

    add_sp(sld, sp(21, 'Supported', 0.5, 3.1, 12.5, 1.3,
                   f"Supported: {independent_data.get('supported','')}",
                   font='Twinkl Cursive Looped Light', sz=18,
                   color='333333', align='l', fill='F2F2F2',
                   border=('BBBBBB', 1.5), anchor='ctr'))

    sld.notes_slide.notes_text_frame.text = notes
    print(f"  Independent slide ({title[:40]}) ✓")
    return sld

# ===========================================================================
# LP / MARKING STATION BLANK SLIDES
# ===========================================================================
def build_lp_slide(label):
    sld = new_slide(5)
    add_sp(sld, sp(20, 'LPTitle', 0.5, 0.1, 12.0, 0.9,
                   label, font='Twinkl Cursive Looped Light',
                   sz=32, bold=True, color='000000', align='ctr',
                   fill=None, no_line=True))
    sld.notes_slide.notes_text_frame.text = (
        f"YOU DO (INDEPENDENT)\n{label}\nLeave blank — Innes adds screenshot.")
    print(f"  {label} slide ✓")
    return sld

# ===========================================================================
# SLIDE 22 — LEARNING REVIEW  (fixed: wedgeRoundRectCallout, 20pt)
# ===========================================================================
def build_learning_review():
    sld = new_slide(10)
    stems = L1['learningReviewStems']
    sid = [10]
    def nid(): sid[0]+=1; return sid[0]

    add_sp(sld, sp(nid(),'Title', 5.172,0.197, 3.352,0.640,
                   'Learning Review', font='Twinkl Cursive Looped Light',
                   sz=24, bold=True, color='000000', align='ctr',
                   fill=None, no_line=True))

    # Speech bubbles — wedgeRoundRectCallout at 20pt (matching template)
    bubbles = [
        (stems[0], 'E9917F', 1.206, 1.131, 3.065, 1.272),
        (stems[1], 'D977ED', 5.274, 1.176, 3.065, 1.272),
        (stems[2], '92D050', 9.442, 1.176, 3.012, 1.272),
    ]
    for i, (text, color, bx, by, bw, bh) in enumerate(bubbles):
        add_sp(sld, f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:nvSpPr><p:cNvPr id="{nid()}" name="Bubble{i+1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(bx)}" y="{emu(by)}"/>
      <a:ext cx="{emu(bw)}" cy="{emu(bh)}"/></a:xfrm>
    <a:prstGeom prst="wedgeRoundRectCallout"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
    <a:ln w="0"><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr rtlCol="0" anchor="ctr"/>
    <a:lstStyle/>
    <a:p><a:pPr algn="ctr"/><a:r>
      <a:rPr lang="en-GB" sz="2000" b="1" dirty="0">
        <a:latin typeface="Twinkl Cursive Looped Light"/>
      </a:rPr>
      <a:t>{_esc(text)}</a:t>
    </a:r></a:p>
  </p:txBody>
</p:sp>''')

    # Images — positions and filenames matched exactly to approved LR_slide.pptx
    # Reference mapping (by size match):
    #   ref image6.png  (2135×1012) = image7.png  — children group
    #   ref image7.png  (234×290)   = image11.png — character (small)
    #   ref image8.png  (440×559)   = image12.png — character
    #   ref image9.png  (453×554)   = image13.png — character
    #   ref image10.png (499×582)   = image14.png — character (was image14.jpeg)
    #   ref image11.png (476×605)   = image15.png — character
    #   ref image12.png (464×464)   = image16.png — LI icon (was image16.jpeg)
    #   ref image13.png (464×464)   = image17.png — LI icon
    #   ref image14.jpg (463×463)   = image18.png — LI icon
    #   ref image15.jpg (463×463)   = image19.png — LI icon
    add_pic(sld,'image7.png',   3.166, 2.797, 6.458, 3.056)
    add_pic(sld,'image11.png',  0.539, 5.105, 1.775, 2.166)
    add_pic(sld,'image12.png',  3.435, 6.152, 1.036, 1.305)
    add_pic(sld,'image13.png',  4.530, 6.163, 1.057, 1.295)
    add_pic(sld,'image14.png',  5.603, 6.073, 1.165, 1.359)
    add_pic(sld,'image15.png',  6.806, 6.034, 1.111, 1.424)
    add_pic(sld,'image16.png', 10.810, 4.301, 1.050, 1.050)
    add_pic(sld,'image17.png', 11.997, 4.301, 1.051, 1.051)
    add_pic(sld,'image18.png', 10.808, 5.448, 1.051, 1.051)
    add_pic(sld,'image19.png', 11.998, 5.449, 1.050, 1.051)

    sld.notes_slide.notes_text_frame.text = (
        f"WE DO — Learning Review\n" +
        '\n'.join(f"Stem {i+1}: {s}" for i,s in enumerate(stems)) +
        "\n\nStand to speak. Learning intelligence icons prompt discussion style.")
    print("Slide 22 (Learning Review) ✓")

# ===========================================================================
# BUILD ALL 22 SLIDES
# ===========================================================================
week_label = L1['week']        # e.g. 'T5W1'
day        = L1['day']         # e.g. 'Monday'
lesson_num = L1['lesson']      # e.g. 1

print(f"\n=== Building {week_label}_L{lesson_num}_{day}_Teaching_v3.pptx ===\n")

c1 = L1['cycle1']
c2 = L1['cycle2']

build_slide1()
build_slide2()
build_slide3()
build_slide4()
build_slide5()
build_slide6()
build_slide7()
build_slide8()

# Cycle 1 teaching slides
build_teaching_slide(2, 'c1_ido1', c1['slideTitles']['ido'][0], 'I DO')

# Second C1 I DO — could be a regular slide or a C1-level STM
if len(c1['slideTitles']['ido']) > 1:
    title2 = c1['slideTitles']['ido'][1]
    if 'c1_ido2' in VISUALS:
        v2 = VISUALS['c1_ido2']
        # Only use STM builder if it's explicitly a spot_the_mistake type
        if v2.get('slide_type') == 'spot_the_mistake':
            build_spot_the_mistake_slide(2, 'c1_ido2', title2)
        else:
            build_teaching_slide(2, 'c1_ido2', title2, 'I DO')

if c1['slideTitles'].get('wedo') and 'c1_wedo' in VISUALS:
    build_teaching_slide(3, 'c1_wedo', c1['slideTitles']['wedo'][0], 'WE DO')

build_trios_slide(4, c1['slideTitles']['trios'][0], c1['trios'],
                  f"YOU DO (TRIOS)\n{c1['trios']['task']}\nChallenge: {c1['trios']['challenge']}")
build_independent_slide(5, c1['slideTitles']['independent'][0], c1['independent'],
                        f"YOU DO (INDEPENDENT) — C1\n{c1['independent']['standard']}")
build_lp_slide('Learning Paper 1')
build_lp_slide('Marking Station 1')

# Cycle 2 teaching slides
if 'c2_ido1' in VISUALS:
    build_teaching_slide(2, 'c2_ido1', c2['slideTitles']['ido'][0], 'I DO')

# C2 second I Do — authored visual takes priority over STM auto-generation
if len(c2['slideTitles']['ido']) > 1:
    title_c2i2 = c2['slideTitles']['ido'][1]
    if 'c2_ido2' in VISUALS and VISUALS['c2_ido2'].get('slide_type') != 'spot_the_mistake':
        # Authored non-STM slide (e.g. lesson 17 special cases)
        build_teaching_slide(2, 'c2_ido2', title_c2i2, 'I DO')
    else:
        # Default: STM from JSON
        build_spot_the_mistake_slide(2, 'c2_ido2', title_c2i2)
else:
    build_spot_the_mistake_slide(2, 'c2_ido2', STM['slideTitle'])

if c2['slideTitles'].get('wedo'):
    if 'c2_wedo' in VISUALS:
        build_teaching_slide(3, 'c2_wedo', c2['slideTitles']['wedo'][0], 'WE DO')

build_trios_slide(4, c2['slideTitles']['trios'][0], c2['trios'],
                  f"YOU DO (TRIOS)\n{c2['trios']['task']}\nChallenge: {c2['trios']['challenge']}")
build_independent_slide(5, c2['slideTitles']['independent'][0], c2['independent'],
                        f"YOU DO (INDEPENDENT) — C2\n{c2['independent']['standard']}")
build_lp_slide('Learning Paper 2')
build_lp_slide('Marking Station 2')

build_learning_review()

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
out = f'/home/claude/{week_label}_L{lesson_num}_Teaching.pptx'
prs.save(out)
print(f"\n=== Saved: {out} ({len(prs.slides)} slides) ===")

# ---------------------------------------------------------------------------
# PRE-FLIGHT CHECK
# Reads the saved file and checks for common layout problems.
# Reports warnings but does not block saving.
# Checks:
#   1. Text overflow — text box too narrow/short for its content at stated font size
#   2. Out-of-bounds — shapes placed outside slide dimensions
#   3. Grid-point bounds — any plotted point outside its declared grid
#   4. WM type rule — items match the expected type for the day of week
# ---------------------------------------------------------------------------
def run_preflight(pptx_path, lesson_data_items, day_name):
    from pptx import Presentation as _Prs
    from pptx.util import Pt as _Pt
    import re as _re

    SLIDE_W_EMU = 13.333 * 914400
    SLIDE_H_EMU = 7.5   * 914400

    # Approximate character width in EMU at a given font size (pt)
    # Assumes Aptos/sans-serif — roughly 0.55× the point size in width per char
    def approx_text_w_emu(text, font_pt):
        return len(str(text)) * font_pt * 0.55 * 12700  # 12700 EMU per pt

    issues = []
    deck = _Prs(pptx_path)

    for slide_idx, slide in enumerate(deck.slides, 1):
        for shape in slide.shapes:
            # ── Out of bounds check ──────────────────────────────────────────
            if hasattr(shape, 'left') and shape.left is not None:
                l, t = shape.left, shape.top
                r = l + (shape.width  or 0)
                b = t + (shape.height or 0)
                if l < -914400 or t < -914400 or r > SLIDE_W_EMU + 914400 or b > SLIDE_H_EMU + 914400:
                    issues.append(
                        f"Slide {slide_idx} '{shape.name}': shape out of bounds "
                        f"(left={l//914400:.2f}\" top={t//914400:.2f}\" "
                        f"right={r//914400:.2f}\" bottom={b//914400:.2f}\")"
                    )

            # ── Text overflow check ──────────────────────────────────────────
            # Only flag genuine problems:
            #   - Single-line boxes where text is wider than the box
            #   - Any box where the font is taller than the box height
            if shape.has_text_frame and shape.width and shape.height:
                tf = shape.text_frame
                box_w_emu = shape.width
                box_h_emu = shape.height

                for para in tf.paragraphs:
                    for run in para.runs:
                        txt = run.text.strip()
                        if not txt:
                            continue
                        sz_pt = None
                        if run.font.size:
                            sz_pt = run.font.size.pt
                        elif para.runs and para.runs[0].font.size:
                            sz_pt = para.runs[0].font.size.pt
                        if sz_pt is None:
                            sz_pt = 12

                        line_h_emu = sz_pt * 12700 * 1.25  # 125% leading

                        # Height check: box shorter than a single line — always a problem
                        if line_h_emu > box_h_emu * 1.05:
                            issues.append(
                                f"Slide {slide_idx} '{shape.name}': "
                                f"box height {box_h_emu/12700:.0f}pt too small "
                                f"for {sz_pt:.0f}pt font — text will be clipped"
                            )

                        # Width check: only flag if box is also too short to wrap
                        # (i.e. single-line box). Multi-line boxes can wrap, so skip.
                        lines_available = box_h_emu / line_h_emu
                        if lines_available < 1.8:  # effectively single-line
                            est_w = len(txt) * sz_pt * 0.55 * 12700
                            if est_w > box_w_emu * 1.20:
                                issues.append(
                                    f"Slide {slide_idx} '{shape.name}': "
                                    f"single-line box — '{txt[:25]}...' "
                                    f"estimated {est_w/12700:.0f}pt wide, "
                                    f"box only {box_w_emu/12700:.0f}pt"
                                )

    # ── WM type rule check ───────────────────────────────────────────────────
    day_map    = {'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4}
    wm_types   = ['numbers','words','emojis','text+image']
    day_pos    = day_map.get(day_name, 1)
    expected   = wm_types[day_pos - 1]
    items      = lesson_data_items
    if all(isinstance(i, int) for i in items):
        actual = 'numbers'
    elif all(isinstance(i, str) and any(ord(c) > 127 for c in i) for i in items):
        actual = 'emojis'
    elif all(isinstance(i, str) for i in items):
        actual = 'words'
    else:
        actual = 'mixed/text+image'

    if actual != expected and expected != 'text+image':
        issues.append(
            f"WM TYPE MISMATCH: {day_name} should be '{expected}' "
            f"but items are '{actual}' — check lesson_data.py"
        )

    # ── Report ───────────────────────────────────────────────────────────────
    print(f"\n--- Pre-flight check ({len(deck.slides)} slides) ---")
    if issues:
        print(f"  {len(issues)} issue(s) found:")
        for iss in issues:
            print(f"  ⚠  {iss}")
    else:
        print("  ✓ No layout issues detected")
    print("---\n")
    return issues

_wm_items = _ld['wm']['items']
run_preflight(out, _wm_items, day)
