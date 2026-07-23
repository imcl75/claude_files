#!/usr/bin/env python3
"""
Build T6W4 LP4, LP5, LP6 (standard + adapted) as PPTX files.
Uses LP3 fixed as template base — preserves correct WFA learning label format.
Only updates: date (id=4), label text (id=5), instruction (id=7), body content.
"""
import re, os, shutil, zipfile

BASE_PPTX = '/mnt/user-data/outputs/T6W4_LP3_Geographers_England_Comparison_Frame_fixed.pptx'
WORK_ROOT = '/home/claude/lp_builds'

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def rd(p): return open(p, encoding='utf-8').read()
def rw(p, t): open(p, 'w', encoding='utf-8').write(t)

def update_shape_text(xml, shape_id, paragraphs):
    """
    Replace all <a:p> content in a shape with new paragraphs.
    paragraphs = list of (text, bold, underline, size, colour)
    """
    def make_para(text, bold=False, underline=False, sz=650, col='000000'):
        b = ' b="1"' if bold else ''
        u = ' u="sng"' if underline else ''
        return (f'<a:p><a:pPr indent="0" marL="0"><a:buNone/></a:pPr>'
                f'<a:r><a:rPr lang="en-GB" sz="{sz}"{b}{u} dirty="0">'
                f'<a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
                f'<a:latin typeface="Aptos" pitchFamily="34" charset="0"/>'
                f'<a:ea typeface="Aptos" pitchFamily="34" charset="-122"/>'
                f'<a:cs typeface="Aptos" pitchFamily="34" charset="-120"/>'
                f'</a:rPr><a:t>{esc(text)}</a:t></a:r>'
                f'<a:endParaRPr lang="en-GB" sz="{sz}" dirty="0"/></a:p>')

    new_body = ''.join(make_para(*p) if isinstance(p, tuple) else make_para(p) for p in paragraphs)

    def replacer(m):
        sp = m.group(0)
        # Replace everything between <p:txBody>...<a:bodyPr and </p:txBody>
        sp = re.sub(r'(<p:txBody>.*?<a:lstStyle/>).*?(</p:txBody>)',
                    lambda m2: m2.group(1) + new_body + m2.group(2),
                    sp, flags=re.DOTALL)
        return sp

    return re.sub(rf'<p:sp>(?:(?!<p:sp>).)*?<p:cNvPr id="{shape_id}".*?</p:sp>',
                  replacer, xml, count=1, flags=re.DOTALL)

def update_date(xml, date_str):
    def replacer(m):
        sp = m.group(0)
        sp = re.sub(r'<a:t>[^<]*</a:t>', f'<a:t>{esc(date_str)}</a:t>', sp, count=1)
        return sp
    return re.sub(r'<p:sp>(?:(?!<p:sp>).)*?<p:cNvPr id="4".*?</p:sp>',
                  replacer, xml, count=1, flags=re.DOTALL)

def learning_label_paras(key_q, lf, ican1, ican2):
    return [
        ('Key Question', True, True, 650, '000000'),
        (key_q, True, True, 650, '000000'),
        (f'LF: {lf}', False, False, 650, '000000'),
        (ican1, False, False, 650, '000000'),
        (ican2, False, False, 650, '000000'),
    ]

# ── pptxgenjs-style shape builder (direct XML) ──────────────────────

SLIDE_W = 6120000   # 6.75" in EMU
SLIDE_H = 7857600   # 8.69" in EMU (A4 portrait at 914400 EMU/inch)

def text_shape(uid, name, x, y, cx, cy, paras, body_props=''):
    """paras = [(text, bold, sz, colour, italic), ...]"""
    xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="{name}"/>'
           f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
           f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
           f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
           f'<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
           f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t">'
           f'{body_props}<a:normAutofit/></a:bodyPr><a:lstStyle/>')
    for para in paras:
        text, bold, sz, col, *rest = para
        italic = rest[0] if rest else False
        b = ' b="1"' if bold else ''
        i = ' i="1"' if italic else ''
        font = 'Twinkl Cursive Looped'
        xml += (f'<a:p><a:pPr indent="0" marL="0"><a:buNone/></a:pPr>'
                f'<a:r><a:rPr lang="en-GB" sz="{sz}"{b}{i} dirty="0">'
                f'<a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
                f'<a:latin typeface="{font}"/>'
                f'</a:rPr><a:t>{esc(text)}</a:t></a:r></a:p>')
    xml += '</p:txBody></p:sp>'
    return xml

def line_shape(uid, y, dash=False):
    """Horizontal dashed or solid line across content area."""
    dash_xml = '<a:prstDash val="dash"/>' if dash else ''
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Line{uid}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="342900" y="{y}"/>'
            f'<a:ext cx="5434200" cy="0"/></a:xfrm>'
            f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:noFill/><a:ln w="9525"><a:solidFill>'
            f'<a:srgbClr val="AAAAAA"/></a:solidFill>{dash_xml}</a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

def rect_shape(uid, x, y, cx, cy, fill='FFFFFF', stroke='CCCCCC', stroke_w=9525):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Rect{uid}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            f'<a:ln w="{stroke_w}"><a:solidFill>'
            f'<a:srgbClr val="{stroke}"/></a:solidFill></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

# ══════════════════════════════════════════════════════════════════════
# CONTENT BUILDERS
# Each returns list of shape XML strings to insert in slide body
# ══════════════════════════════════════════════════════════════════════

def DARK(): return '1A1A1A'
def BLUE(): return '1798d3'
def GREEN(): return '4FAD5B'
def ORANGE(): return 'E67E22'
def heading(uid, y, text):
    return text_shape(uid, f'Head{uid}', 342900, y, 5434200, 260000,
                      [(text, True, 1000, BLUE())])

def instruction(uid, y, text):
    return text_shape(uid, f'Instr{uid}', 342900, y, 5434200, 260000,
                      [(text, False, 900, DARK())])

def write_line(uid, y):
    return line_shape(uid, y, dash=False)

def word_bank_shape(uid, y, label, words):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="WB{uid}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="342900" y="{y}"/>'
            f'<a:ext cx="5434200" cy="330000"/></a:xfrm>'
            f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 15000"/></a:avLst></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="FEF9E7"/></a:solidFill>'
            f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{ORANGE()}"/></a:solidFill></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr lIns="60000" tIns="60000" rIns="60000" bIns="60000" wrap="square" anchor="ctr"/>'
            f'<a:lstStyle/><a:p>'
            f'<a:r><a:rPr lang="en-GB" sz="800" b="1" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{ORANGE()}"/></a:solidFill>'
            f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
            f'<a:t>{esc(label)}: </a:t></a:r>'
            f'<a:r><a:rPr lang="en-GB" sz="800" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
            f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
            f'<a:t>{esc(words)}</a:t></a:r>'
            f'</a:p></p:txBody></p:sp>')


def build_slide1(slide_xml, date, lf, ican1, ican2, key_q,
                 instruction_text, body_shapes_xml):
    """Replace date, label, instruction, then insert body shapes before </p:spTree>."""
    # Update date (id=4)
    xml = update_date(slide_xml, date)
    # Update learning label (id=5)
    xml = update_shape_text(xml, 5, learning_label_paras(key_q, lf, ican1, ican2))
    # Update instruction (id=7)
    xml = update_shape_text(xml, 7, [(instruction_text, False, False, 900, '000000')])
    # Remove all body shapes (id >= 8)
    xml = re.sub(r'<p:sp>(?:(?!<p:sp>).)*?<p:cNvPr id="(?:[89]|[1-9]\d+)".*?</p:sp>',
                 '', xml, flags=re.DOTALL)
    # Insert new body shapes
    xml = xml.replace('</p:spTree>', body_shapes_xml + '\n</p:spTree>')
    return xml


def build_slide2(title_text, body_xml, base_slide2_xml):
    """Build marking station slide from base slide 2."""
    xml = base_slide2_xml
    # Update instruction/title shape (id=5 equivalent)
    xml = re.sub(r'<p:sp>(?:(?!<p:sp>).)*?<p:cNvPr id="5".*?</p:sp>',
                 '', xml, count=1, flags=re.DOTALL)
    xml = xml.replace('</p:spTree>',
        text_shape(500, 'MSTitle', 342900, 400000, 5434200, 500000,
                   [(title_text, True, 1200, GREEN())]) + '\n</p:spTree>')
    # Remove content shapes (id >= 6)
    xml = re.sub(r'<p:sp>(?:(?!<p:sp>).)*?<p:cNvPr id="(?:[6-9]|[1-9]\d+)".*?</p:sp>',
                 '', xml, flags=re.DOTALL)
    xml = xml.replace('</p:spTree>', body_xml + '\n</p:spTree>')
    return xml


def pack(work_dir, out_path):
    if os.path.exists(out_path): os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(work_dir):
            for fn in files:
                p = os.path.join(root, fn)
                z.write(p, os.path.relpath(p, work_dir))


def prep_workdir(name):
    d = f'{WORK_ROOT}/{name}'
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree('/home/claude/lp_base/unpacked', d)
    return d


# ══════════════════════════════════════════════════════════════════════
# LP4 Standard
# ══════════════════════════════════════════════════════════════════════
def build_lp4_standard():
    wd = prep_workdir('lp4_std')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    # ── Body shapes ──────────────────────────────────────────────────
    uid = 100
    shapes = ''
    y = 1500000   # start below label area

    shapes += heading(uid, y, 'Part A   Land use sort'); uid+=1; y+=320000
    shapes += instruction(uid, y, 'For each land use below, write E (England), B (Brazil) or Both. Then write the type of land use.'); uid+=1; y+=280000

    # Table header row
    COL = [2800000, 1400000, 1234200]  # cx of each col
    col_xs = [342900, 342900+COL[0], 342900+COL[0]+COL[1]]
    HEADER_H = 240000; ROW_H = 220000
    for i, (txt, cx, x) in enumerate(zip(['Land use','England / Brazil / Both','Type'], COL, col_xs)):
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="TH{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
                   f'<a:ext cx="{cx}" cy="{HEADER_H}"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="{BLUE()}"/></a:solidFill>'
                   f'<a:ln><a:noFill/></a:ln></p:spPr>'
                   f'<p:txBody><a:bodyPr lIns="45720" tIns="45720" anchor="ctr"/><a:lstStyle/>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="800" b="1" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>{esc(txt)}</a:t></a:r></a:p></p:txBody></p:sp>')
        uid+=1
    y += HEADER_H

    rows = [
        'Coffee plantation', 'Coal mine / quarry', 'Cattle ranch / farmland',
        'Offshore wind farm', 'Iron ore mine', 'Arable crop field (wheat, barley)',
        'Oil rig or power station', 'Terraced housing / urban suburb',
        'Hydro-electric dam', 'Shopping centre / commercial area',
        'Port / container terminal', 'Moorland / national park',
    ]
    for ri, row in enumerate(rows):
        fill = 'F5F5F5' if ri%2==0 else 'FFFFFF'
        for ci, (txt, cx, x) in enumerate(zip([row,'',''], COL, col_xs)):
            shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="TR{uid}"/>'
                       f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                       f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/>'
                       f'<a:ext cx="{cx}" cy="{ROW_H}"/></a:xfrm>'
                       f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                       f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                       f'<a:ln w="6350"><a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill></a:ln></p:spPr>'
                       f'<p:txBody><a:bodyPr lIns="45720" tIns="30000" anchor="ctr"/><a:lstStyle/>'
                       f'<a:p><a:r><a:rPr lang="en-GB" sz="750" dirty="0">'
                       f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                       f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                       f'<a:t>{esc(txt)}</a:t></a:r></a:p></p:txBody></p:sp>')
            uid+=1
        y += ROW_H

    y += 80000
    shapes += heading(uid, y, 'Part B   Comparison sentences'); uid+=1; y+=300000
    shapes += instruction(uid, y, 'Write one sentence about what England and Brazil have in common and one about how they differ. Use at least ONE word from the vocabulary bank.'); uid+=1; y+=360000
    shapes += text_shape(uid, f'P{uid}', 342900, y, 5434200, 260000, [('England and Brazil are similar because...', True, 900, DARK())]); uid+=1; y+=280000
    for _ in range(3): shapes += write_line(uid, y+160000); uid+=1; y+=170000
    y += 60000
    shapes += text_shape(uid, f'P{uid}', 342900, y, 5434200, 260000, [('However, they are different because...', True, 900, DARK())]); uid+=1; y+=280000
    for _ in range(3): shapes += write_line(uid, y+160000); uid+=1; y+=170000
    y += 80000
    shapes += word_bank_shape(uid, y, 'Word bank', 'land use  \u2022  natural resource  \u2022  trade  \u2022  economic activity  \u2022  agricultural  \u2022  industrial'); uid+=1

    rw(s1, build_slide1(xml, '06/07/2026',
        'to describe and compare how people use land in England and Brazil',
        'I can describe two ways land is used in Brazil',
        'I can compare land use in England and Brazil using geographical vocabulary',
        'Are England and Brazil different?',
        'Complete the land use sort and comparison sentences below.',
        shapes))

    # Slide 2 — marking station (simplified)
    s2 = f'{wd}/ppt/slides/slide2.xml'
    s2xml = rd(s2)
    ans_shapes = ''
    uid = 200
    ay = 1000000
    ans_shapes += heading(uid, ay, 'Part A   Suggested answers'); uid+=1; ay+=320000
    for ab, item, typ in [
        ('B','Coffee plantation','Agricultural'), ('Both','Coal mine / quarry','Industrial / mining'),
        ('B','Cattle ranch / farmland','Agricultural'), ('E','Offshore wind farm','Energy'),
        ('B','Iron ore mine','Industrial / mining'), ('E','Arable crop field (wheat, barley)','Agricultural'),
        ('Both','Oil rig or power station','Energy'), ('Both','Terraced housing / urban suburb','Residential'),
        ('B','Hydro-electric dam','Energy'), ('Both','Shopping centre / commercial area','Commercial'),
        ('Both','Port / container terminal','Transport / trade'), ('E','Moorland / national park','Recreational'),
    ]:
        line = f'\u2192 {ab}   {item}   {typ}'
        ans_shapes += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                                 [(line, False, 800, GREEN())]); uid+=1; ay+=210000
    ay += 60000
    ans_shapes += heading(uid, ay, 'Part B   Model sentences'); uid+=1; ay+=300000
    for line in [
        'England and Brazil are similar because both countries use land for agriculture, industry and energy.',
        'However, they are different because Brazil\u2019s main agricultural land uses include coffee and cattle,',
        'while England\u2019s focus more on arable crops. Trade links the two countries.',
    ]:
        ans_shapes += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 220000,
                                 [(line, False, 800, DARK())]); uid+=1; ay+=240000

    rw(s2, build_slide2('Marking Station', ans_shapes, s2xml))
    out = '/mnt/user-data/outputs/T6W4_LP4_Geographers_Human_Geography.pptx'
    pack(wd, out)
    print(f'LP4 standard → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
# LP4 Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp4_adapted():
    wd = prep_workdir('lp4_adp')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    uid = 100; shapes = ''; y = 1500000
    shapes += heading(uid, y, 'Part A   Which country?'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Read each statement. Write England, Brazil or Both in the box on the right.'); uid+=1; y+=280000
    shapes += word_bank_shape(uid, y, 'Countries', 'England  \u2022  Brazil  \u2022  Both'); uid+=1; y+=380000

    stmts = [
        'This country grows coffee beans as one of its most important crops.',
        'This country has oil fields and uses wind turbines for energy.',
        'This country has huge iron ore mines in the ground.',
        'This country has mostly flat farmland in the east and hilly farmland in the west.',
        'This country has hydro-electric dams on its rivers.',
        'This country has large ports where goods are shipped abroad.',
        'This country trades with the other, buying and selling different goods.',
    ]
    RH = 240000
    BW = 1100000
    for i, stmt in enumerate(stmts):
        fill = 'F0F4FF' if i%2==0 else 'FFFFFF'
        # Statement
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="S{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="342900" y="{y}"/>'
                   f'<a:ext cx="{4376100}" cy="{RH}"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                   f'<a:ln w="6350"><a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill></a:ln></p:spPr>'
                   f'<p:txBody><a:bodyPr lIns="45720" tIns="40000" anchor="ctr"/><a:lstStyle/>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="800" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>{esc(f"{i+1}. {stmt}")}</a:t></a:r></a:p></p:txBody></p:sp>'); uid+=1
        # Answer box
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="B{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="{4719000}" y="{y+20000}"/>'
                   f'<a:ext cx="{BW}" cy="{RH-40000}"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
                   f'<a:ln w="9525"><a:solidFill><a:srgbClr val="888888"/></a:solidFill></a:ln></p:spPr>'
                   f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'); uid+=1
        y += RH

    y += 100000
    shapes += heading(uid, y, 'Part B   Cloze comparison sentences'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Fill in the missing words using the word bank below.'); uid+=1; y+=300000

    for line in [
        'England and Brazil are similar because they both use land for',
        '___________________ and ___________________.',
        '',
        'However, they are different because Brazil grows ___________________, while',
        'England grows ___________________. England imports ___________________ from Brazil.',
    ]:
        if line == '':
            y += 80000
        else:
            shapes += text_shape(uid, f'CL{uid}', 342900, y, 5434200, 240000,
                                 [(line, False, 900, DARK())]); uid+=1; y+=250000

    y += 60000
    shapes += word_bank_shape(uid, y, 'Word bank',
        'agriculture  \u2022  energy  \u2022  coffee  \u2022  wheat  \u2022  iron ore  \u2022  trade  \u2022  industry'); uid+=1

    rw(s1, build_slide1(xml, '06/07/2026',
        'to describe and compare how people use land in England and Brazil',
        'I can match a land use to the correct country',
        'I can complete a comparison sentence about England and Brazil',
        'Are England and Brazil different?',
        'Complete Part A and Part B below.',
        shapes))

    s2 = f'{wd}/ppt/slides/slide2.xml'
    s2xml = rd(s2)
    uid = 200; ans = ''; ay = 1000000
    ans += heading(uid, ay, 'Part A   Which country? (answers)'); uid+=1; ay+=320000
    for ab, stmt in [
        ('Brazil','This country grows coffee beans...'), ('Both','Oil fields and wind turbines...'),
        ('Brazil','Huge iron ore mines...'), ('England','Flat farmland in the east / hilly in the west.'),
        ('Brazil','Hydro-electric dams...'), ('Both','Large ports...'), ('Both','Trades with the other...'),
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(f'\u2192 {ab}   {stmt}', False, 800, GREEN())]); uid+=1; ay+=210000
    ay += 60000
    ans += heading(uid, ay, 'Part B   Cloze model answers'); uid+=1; ay+=310000
    for line in [
        'England and Brazil are similar because they both use land for agriculture and energy.',
        'However, they are different because Brazil grows coffee, while England grows wheat.',
        'England imports coffee from Brazil.',
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 220000,
                          [(line, False, 800, DARK())]); uid+=1; ay+=240000
    rw(s2, build_slide2('Marking Station', ans, s2xml))
    out = '/mnt/user-data/outputs/T6W4_LP4_Geographers_Human_Geography_adapted.pptx'
    pack(wd, out)
    print(f'LP4 adapted → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
# LP5 Standard
# ══════════════════════════════════════════════════════════════════════
def build_lp5_standard():
    wd = prep_workdir('lp5_std')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    # Embed map image into ppt/media and add relationship
    map_src = '/home/claude/lp5_map.png'
    shutil.copy(map_src, f'{wd}/ppt/media/lp5_map.png')
    rels_path = f'{wd}/ppt/slides/_rels/slide1.xml.rels'
    rels = rd(rels_path)
    if 'lp5_map' not in rels:
        IMG_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
        rels = rels.replace('</Relationships>',
            f'<Relationship Id="rId99" Type="{IMG_REL}" Target="../media/lp5_map.png"/>'
            f'</Relationships>')
        rw(rels_path, rels)

    uid = 100; shapes = ''; y = 1450000

    # Map image shape
    MAP_H = 1600000; MAP_W = 3600000
    map_x = (5777100 - MAP_W) // 2 + 342900
    shapes += (f'<p:pic><p:nvPicPr>'
               f'<p:cNvPr id="{uid}" name="Map{uid}"/>'
               f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
               f'<p:nvPr/></p:nvPicPr>'
               f'<p:blipFill><a:blip r:embed="rId99"/>'
               f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               f'<p:spPr><a:xfrm><a:off x="{map_x}" y="{y}"/>'
               f'<a:ext cx="{MAP_W}" cy="{MAP_H}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'); uid+=1
    y += MAP_H + 80000

    shapes += heading(uid, y, 'Part A   Map skills questions'); uid+=1; y+=310000
    for qi, (q, nl) in enumerate([
        ('1. What feature is shown at grid reference 322 510?', 2),
        ('2. Write the 4-figure grid reference for Ashton settlement.', 2),
        ('3. Write the 6-figure grid reference for St Mary\u2019s Church/school.', 2),
        ('4. What do the contour lines around grid square 31 50 tell you about the land?', 3),
        ('5. Name one land use shown on the map and write its grid reference.', 2),
    ]):
        shapes += text_shape(uid, f'Q{uid}', 342900, y, 5434200, 240000,
                             [(q, True, 850, DARK())]); uid+=1; y+=260000
        for _ in range(nl):
            shapes += write_line(uid, y+150000); uid+=1; y+=165000
        y += 40000

    y += 40000
    shapes += heading(uid, y, 'Part B   Compare two places'); uid+=1; y+=310000
    shapes += instruction(uid, y,
        'After looking at the board: write two sentences comparing the OS map area with the satellite image of Brazil.'); uid+=1; y+=300000
    for _ in range(4):
        shapes += write_line(uid, y+150000); uid+=1; y+=165000

    rw(s1, build_slide1(xml, '07/07/2026',
        'to use maps to investigate and describe places',
        'I can read a grid reference correctly',
        'I can describe what a map tells me about a place',
        'Are England and Brazil different?',
        'Use the map above to answer the questions below.',
        shapes))

    s2 = f'{wd}/ppt/slides/slide2.xml'
    uid = 200; ans = ''; ay = 1000000
    ans += heading(uid, ay, 'Part A   Suggested answers'); uid+=1; ay+=320000
    for n, ql, at in [
        ('1', 'Feature at 322 510', 'Woodland (shaded green area)'),
        ('2', '4-figure ref for Ashton', '3248'),
        ('3', '6-figure ref for St Mary\u2019s', '322 510 (approx.)'),
        ('4', 'Contour lines in 31 50', 'Close together \u2014 land is steeply sloping / hilly. Hill over 150m.'),
        ('5', 'Land use + grid ref', 'e.g. Woodland at 326 503 / Road B4027 at 320 490 (any valid)'),
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(f'{n}. {ql}', True, 800, DARK())]); uid+=1; ay+=210000
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(at, False, 800, GREEN())]); uid+=1; ay+=220000
    rw(s2, build_slide2('Marking Station', ans, rd(s2)))
    out = '/mnt/user-data/outputs/T6W4_LP5_Geographers_Map_Skills.pptx'
    pack(wd, out)
    print(f'LP5 standard → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
# LP5 Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp5_adapted():
    wd = prep_workdir('lp5_adp')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    shutil.copy('/home/claude/lp5_map.png', f'{wd}/ppt/media/lp5_map.png')
    rels_path = f'{wd}/ppt/slides/_rels/slide1.xml.rels'
    rels = rd(rels_path)
    if 'lp5_map' not in rels:
        rels = rels.replace('</Relationships>',
            f'<Relationship Id="rId99" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/lp5_map.png"/></Relationships>')
        rw(rels_path, rels)

    uid = 100; shapes = ''; y = 1450000
    MAP_H = 1500000; MAP_W = 3400000
    map_x = (5777100 - MAP_W) // 2 + 342900
    shapes += (f'<p:pic><p:nvPicPr><p:cNvPr id="{uid}" name="Map{uid}"/>'
               f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
               f'<p:nvPr/></p:nvPicPr>'
               f'<p:blipFill><a:blip r:embed="rId99"/>'
               f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               f'<p:spPr><a:xfrm><a:off x="{map_x}" y="{y}"/>'
               f'<a:ext cx="{MAP_W}" cy="{MAP_H}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'); uid+=1
    y += MAP_H + 80000

    shapes += heading(uid, y, 'Part A   Reading the map'); uid+=1; y+=310000
    shapes += text_shape(uid, f'Rem{uid}', 342900, y, 5434200, 230000,
        [('Remember: go ACROSS first, then UP \u2014 \u201calong the corridor, up the stairs\u201d', True, 850, BLUE())]); uid+=1; y+=280000

    for q, opts in [
        ('1. What is shown at grid reference 322 510?',
         ['A. The river', 'B. The woodland', 'C. The road', 'D. Ashton settlement']),
        ('2. The 4-figure grid reference for Ashton is:',
         ['A. 4832', 'B. 3248', 'C. 4823', 'D. 2348']),
        ('3. The contour lines near grid square 31 50 are close together. This means:',
         ['A. The land is flat', 'B. The land is wet', 'C. The land is steep', 'D. There is a river']),
    ]:
        shapes += text_shape(uid, f'Q{uid}', 342900, y, 5434200, 240000,
                             [(q, True, 850, DARK())]); uid+=1; y+=260000
        for opt in opts:
            shapes += text_shape(uid, f'Opt{uid}', 500000, y, 5100000, 200000,
                                 [(opt, False, 800, DARK())]); uid+=1; y+=205000
        y += 40000

    y += 40000
    shapes += heading(uid, y, 'Part B   Comparison sentence (cloze)'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Fill in the missing words.'); uid+=1; y+=260000
    for line in [
        'The OS map of Westhaven shows ___________________ and ___________________.',
        'This is different from the satellite image of Brazil because ___________________________',
        '____________________________________________________________.',
    ]:
        shapes += text_shape(uid, f'CL{uid}', 342900, y, 5434200, 230000,
                             [(line, False, 900, DARK())]); uid+=1; y+=250000
    y += 60000
    shapes += word_bank_shape(uid, y, 'Word bank',
        'woodland  \u2022  roads  \u2022  hills  \u2022  settlement  \u2022  rainforest  \u2022  flat  \u2022  land use'); uid+=1

    rw(s1, build_slide1(xml, '07/07/2026',
        'to use maps to investigate and describe places',
        'I can read a grid reference using the rule "along first, then up"',
        'I can name one thing a map shows me about a place',
        'Are England and Brazil different?',
        'Use the map above to complete the tasks below.',
        shapes))

    uid = 200; ans = ''; ay = 1000000
    ans += heading(uid, ay, 'Part A   Answers'); uid+=1; ay+=320000
    for n, a in [('1','B. The woodland'),('2','B. 3248'),('3','C. The land is steep')]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(f'{n}. \u2192 {a}', False, 850, GREEN())]); uid+=1; ay+=220000
    ay += 80000
    ans += heading(uid, ay, 'Part B   Model sentence'); uid+=1; ay+=310000
    for line in [
        'The OS map of Westhaven shows woodland and roads.',
        'This is different from the satellite image of Brazil because Brazil shows flat farmland',
        'and rainforest with very different land use patterns.',
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 220000,
                          [(line, False, 800, DARK())]); uid+=1; ay+=240000
    rw(f'{wd}/ppt/slides/slide2.xml', build_slide2('Marking Station', ans, rd(f'{wd}/ppt/slides/slide2.xml')))
    out = '/mnt/user-data/outputs/T6W4_LP5_Geographers_Map_Skills_adapted.pptx'
    pack(wd, out)
    print(f'LP5 adapted → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
# LP6 Standard
# ══════════════════════════════════════════════════════════════════════
def build_lp6_standard():
    wd = prep_workdir('lp6_std')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    uid = 100; shapes = ''; y = 1500000
    shapes += heading(uid, y, 'Part A   Before and after'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Look at the images on the board. For each pair, record what you observe.'); uid+=1; y+=280000

    for pair in ['Image pair 1: Amazon rainforest', 'Image pair 2: English landscape']:
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Box{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="342900" y="{y}"/>'
                   f'<a:ext cx="5434200" cy="600000"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="EAF5FB"/></a:solidFill>'
                   f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{BLUE()}"/></a:solidFill></a:ln></p:spPr>'
                   f'<p:txBody><a:bodyPr lIns="60000" tIns="50000" wrap="square"/><a:lstStyle/>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="850" b="1" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="{BLUE()}"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>{esc(pair)}</a:t></a:r></a:p>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="800" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>What changed? _____________________  What caused it? _____________________</a:t></a:r></a:p>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="800" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>What might the geographical impact be? _____________________________________</a:t></a:r></a:p>'
                   f'</p:txBody></p:sp>'); uid+=1; y+=650000

    y += 80000
    shapes += heading(uid, y, 'Part B   Geographical comparison'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Write your comparison. Use the vocabulary checklist to tick each word when you use it.'); uid+=1; y+=300000

    # Vocabulary checklist (right side)
    VC_TERMS = ['hemisphere','biome','climate zone','topography','land use',
                'natural resource','trade','deforestation','urbanisation','temperate','tropical']
    vcx = 4300000; vc_top = y
    VC_ITH = 170000
    vc_box_h = 200000 + len(VC_TERMS) * VC_ITH + 100000
    shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="VCBox{uid}"/>'
               f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
               f'<p:spPr><a:xfrm><a:off x="{vcx}" y="{vc_top}"/>'
               f'<a:ext cx="1477200" cy="{vc_box_h}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
               f'<a:solidFill><a:srgbClr val="FEF9E7"/></a:solidFill>'
               f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{ORANGE()}"/></a:solidFill></a:ln></p:spPr>'
               f'<p:txBody><a:bodyPr lIns="50000" tIns="50000" wrap="square" anchor="t"/><a:lstStyle/>'
               f'<a:p><a:r><a:rPr lang="en-GB" sz="700" b="1" dirty="0">'
               f'<a:solidFill><a:srgbClr val="{ORANGE()}"/></a:solidFill>'
               f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
               f'<a:t>Vocabulary checklist</a:t></a:r></a:p>'
               + ''.join(f'<a:p><a:r><a:rPr lang="en-GB" sz="650" dirty="0">'
                          f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                          f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                          f'<a:t>\u25a1 {t}</a:t></a:r></a:p>' for t in VC_TERMS)
               + f'</p:txBody></p:sp>'); uid+=1

    # Writing lines (left of checklist)
    WW = 3800000
    wy = y
    for prompt, nl in [
        ('Physical geography \u2014 how the two countries compare:', 3),
        ('Human geography \u2014 how land use compares:', 3),
        ('Environmental impact \u2014 how humans are affecting each place:', 3),
    ]:
        shapes += text_shape(uid, f'WP{uid}', 342900, wy, WW, 240000,
                             [(prompt, True, 800, DARK())]); uid+=1; wy+=260000
        for _ in range(nl):
            shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="WL{uid}"/>'
                       f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                       f'<p:spPr><a:xfrm><a:off x="342900" y="{wy}"/>'
                       f'<a:ext cx="{WW}" cy="10000"/></a:xfrm>'
                       f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
                       f'<a:noFill/><a:ln w="6350"><a:solidFill>'
                       f'<a:srgbClr val="AACCDD"/></a:solidFill></a:ln></p:spPr>'
                       f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'); uid+=1; wy+=185000
        wy+=60000

    rw(s1, build_slide1(xml, '08/07/2026',
        'to explain how humans affect the environment in England and Brazil and compare them',
        'I can describe one way humans are affecting Brazil\u2019s environment',
        'I can write a structured comparison using geographical vocabulary',
        'Are England and Brazil different?',
        'Complete Part A using the images on the board. Then write your comparison in Part B.',
        shapes))

    uid=200; ans=''; ay=1000000
    ans += heading(uid, ay, 'Part A   Key points'); uid+=1; ay+=310000
    for lbl, note in [
        ('Amazon rainforest','Deforestation: cleared for cattle / soya / mining. Impact: loss of biome, species, carbon storage.'),
        ('English landscape','Urban growth: farmland covered by housing and roads. Quarrying changes highland landscapes.'),
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(lbl, True, 800, GREEN())]); uid+=1; ay+=210000
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(note, False, 800, DARK())]); uid+=1; ay+=220000
    ay+=80000
    ans += heading(uid, ay, 'Part B   Model comparison (extract)'); uid+=1; ay+=310000
    for line in [
        'Physically, England has a temperate maritime climate with four seasons and deciduous woodland,',
        'while Brazil has a tropical climate with biomes including the rainforest, cerrado and pantanal.',
        'In terms of human geography, Brazil\u2019s main land uses are agriculture and mining, while England',
        'focuses more on arable farming and services. Humans are having a greater environmental impact',
        'in Brazil: around 20% of the Amazon has been deforested since the 1970s. In England, urban',
        'growth has covered farmland around cities like Bristol.',
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 215000,
                          [(line, False, 800, DARK())]); uid+=1; ay+=225000
    rw(f'{wd}/ppt/slides/slide2.xml', build_slide2('Marking Station', ans, rd(f'{wd}/ppt/slides/slide2.xml')))
    out = '/mnt/user-data/outputs/T6W4_LP6_Geographers_Environmental_Impact.pptx'
    pack(wd, out)
    print(f'LP6 standard → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
# LP6 Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp6_adapted():
    wd = prep_workdir('lp6_adp')
    s1 = f'{wd}/ppt/slides/slide1.xml'
    xml = rd(s1)

    uid=100; shapes=''; y=1500000
    shapes += heading(uid, y, 'Part A   What has changed?'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Look at the images on the board. Tick the boxes that apply to each image pair.'); uid+=1; y+=280000

    tick_items = ['Trees / vegetation removed','Buildings added','Farmland expanded','Roads or infrastructure built']
    for pair in ['Image pair 1: Amazon rainforest', 'Image pair 2: English landscape']:
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="TBox{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="342900" y="{y}"/>'
                   f'<a:ext cx="5434200" cy="660000"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="EAF5FB"/></a:solidFill>'
                   f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{BLUE()}"/></a:solidFill></a:ln></p:spPr>'
                   f'<p:txBody><a:bodyPr lIns="60000" tIns="50000" wrap="square"/><a:lstStyle/>'
                   f'<a:p><a:r><a:rPr lang="en-GB" sz="850" b="1" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="{BLUE()}"/></a:solidFill>'
                   f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                   f'<a:t>{esc(pair)}</a:t></a:r></a:p>'
                   + ''.join(f'<a:p><a:r><a:rPr lang="en-GB" sz="800" dirty="0">'
                              f'<a:solidFill><a:srgbClr val="{DARK()}"/></a:solidFill>'
                              f'<a:latin typeface="Twinkl Cursive Looped"/></a:rPr>'
                              f'<a:t>\u25a1 {esc(t)}</a:t></a:r></a:p>' for t in tick_items)
                   + f'</p:txBody></p:sp>'); uid+=1; y+=720000

    y+=80000
    shapes += heading(uid, y, 'Part B   Cloze comparison'); uid+=1; y+=310000
    shapes += instruction(uid, y, 'Fill in the missing words using the word bank.'); uid+=1; y+=290000

    for line in [
        'Physically, England has a _______________ climate, while Brazil has a',
        '_______________ climate. England\u2019s main biome is _______________ forest.',
        '',
        'For human geography, Brazil uses land mainly for _______________ such as',
        'coffee and soya, while England uses land more for _______________ and services.',
        '',
        'Humans are affecting Brazil by _______________ the Amazon. In England,',
        '_______________ growth has covered farmland around cities.',
    ]:
        if line == '':
            y += 80000
        else:
            shapes += text_shape(uid, f'CL{uid}', 342900, y, 5434200, 240000,
                                 [(line, False, 900, DARK())]); uid+=1; y+=255000

    y += 80000
    shapes += word_bank_shape(uid, y, 'Word bank',
        'temperate  \u2022  tropical  \u2022  deciduous  \u2022  agriculture  \u2022  arable farming  \u2022  deforesting  \u2022  biome  \u2022  urban'); uid+=1

    rw(s1, build_slide1(xml, '08/07/2026',
        'to explain how humans affect the environment in England and Brazil and compare them',
        'I can name one cause of Amazon deforestation',
        'I can complete comparison sentences using geographical vocabulary',
        'Are England and Brazil different?',
        'Complete Part A using the images on the board. Then fill in Part B below.',
        shapes))

    uid=200; ans=''; ay=1000000
    ans += heading(uid, ay, 'Part B   Cloze answers'); uid+=1; ay+=320000
    for a, lbl in [
        ('temperate','Climate (England)'), ('tropical','Climate (Brazil)'),
        ('deciduous','England\u2019s biome'), ('agriculture','Brazil land use'),
        ('arable farming','England land use'), ('deforesting','Human impact on Brazil'), ('urban','England impact type'),
    ]:
        ans += text_shape(uid, f'A{uid}', 342900, ay, 5434200, 200000,
                          [(f'\u2192 {a}   ({lbl})', False, 850, GREEN())]); uid+=1; ay+=220000
    rw(f'{wd}/ppt/slides/slide2.xml', build_slide2('Marking Station', ans, rd(f'{wd}/ppt/slides/slide2.xml')))
    out = '/mnt/user-data/outputs/T6W4_LP6_Geographers_Environmental_Impact_adapted.pptx'
    pack(wd, out)
    print(f'LP6 adapted → {os.path.getsize(out)//1024}KB')


# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    os.makedirs(WORK_ROOT, exist_ok=True)
    build_lp4_standard()
    build_lp4_adapted()
    build_lp5_standard()
    build_lp5_adapted()
    build_lp6_standard()
    build_lp6_adapted()
    print('All done.')
