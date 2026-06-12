"""
build_lesson.py — WFA Year 4 Writing Lesson PPTX Generator

Usage (called by SKILL.md workflow):
    python3 build_lesson.py \
        --base     <path/to/writing_lesson_base.pptx> \
        --kc       <path/to/kc_wheel.png> \
        --cover    <path/to/book_cover_image.jpg|png> \
        --lesson   <lesson_number>           e.g. 3
        --term     <term_number>             e.g. 5
        --week     <week_number>             e.g. 1
        --topic    <short_topic_label>       e.g. "Reporting Clauses"
        --out      <output_directory>

Slides are passed as JSON via stdin or --slides-json <file>.

Slide JSON structure:
[
  {"type": "cover",      "day": "Tuesday AM"},
  {"type": "kc"},
  {"type": "lo",         "wal": "...", "tib": "...", "isb": "..."},
  {"type": "warmup",     "title": "Grammar Warm-Up",
                          "subtitle": "...",
                          "cards": [{"label":"A","lines":["..."]}, ...]},
  {"type": "we_do",      "title": "...", "lines": ["..."]},
  {"type": "i_do",       "title": "...",
                          "left_label":"...", "left_lines":["..."],
                          "right_label":"...", "right_lines":["..."]},
  {"type": "you_do",     "title": "...", "lines": ["..."]},
  {"type": "you_do_trio","lines": ["..."]},          # title cleared (icon says it)
  {"type": "book_page",  "label": "Bear and Fox"},   # placeholder slide
  {"type": "rules",      "source_slide_xml": "..."},  # verbatim XML from carry-over
  {"type": "learning_review",
                          "q1": "...", "q2": "...", "q3": "..."}
]
"""

import argparse, json, os, re, shutil, sys, zipfile

# ── Constants ─────────────────────────────────────────────────────────
RELS_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
REL_SLD = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'
REL_LAY = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout'
REL_IMG = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'

FONT = ('<a:latin typeface="Twinkl Cursive Looped" '
        'panose="02000000000000000000" pitchFamily="2" charset="77"/>')

# Slide layout numbers in the base PPTX
LAYOUT = {
    'cover':         3,   # Enquiry Detail
    'lo':            5,   # Learning Focus
    'i_do':          6,   # I Do
    'we_do':         7,   # We Do
    'you_do_trio':   8,   # You Do Trio
    'you_do':        9,   # You Do (independent)
    'learning_review': 14,
    'blank':         17,  # for book page placeholders
    'rules':         18,  # 1_We Do (used for existing-XML carry-over slides)
}

# Timer placeholder position (EMU)
TX, TY, TCX, TCY = 10_607_675, 6_289_675, 1_484_313, 444_500

# Day schedule
DAY_SCHEDULE = {
    1: 'Monday AM',
    2: 'Tuesday AM',
    3: 'Tuesday PM',
    4: 'Wednesday AM',
    5: 'Thursday AM',
    6: 'Friday AM',
    7: 'Friday PM',
}

# ── Helpers ───────────────────────────────────────────────────────────

def media_ph_sp(uid=50):
    """Invisible media placeholder shape for slide XML."""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="TimerPH"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph type="media" idx="15"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:endParaRPr lang="en-GB"/></a:p></p:txBody></p:sp>')

def inject_timer(xml, uid=50):
    return xml.replace('</p:spTree>', media_ph_sp(uid) + '</p:spTree>', 1)

def rels_str(layout_num, extra_rels=''):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            f'<Relationships xmlns="{RELS_NS}">'
            f'<Relationship Id="rId1" Type="{REL_LAY}" '
            f'Target="../slideLayouts/slideLayout{layout_num}.xml"/>'
            f'{extra_rels}</Relationships>')

def ph_title(text, uid=2):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Title {uid}"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr/><p:txBody><a:bodyPr><a:normAutofit/></a:bodyPr><a:lstStyle/>'
            f'<a:p><a:r><a:rPr lang="en-GB" dirty="0"/>'
            f'<a:t>{_esc(text)}</a:t></a:r></a:p></p:txBody></p:sp>')

def ph_body(lines, uid=3, idx=1, xfrm_xml=''):
    spPr = f'<p:spPr>{xfrm_xml}</p:spPr>' if xfrm_xml else '<p:spPr/>'
    paras = ''
    for ln in lines:
        if ln == '':
            paras += ('<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>'
                      '<a:endParaRPr lang="en-GB" dirty="0"/></a:p>')
        else:
            paras += (f'<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>'
                      f'<a:r><a:rPr lang="en-GB" dirty="0"/>'
                      f'<a:t>{_esc(ln)}</a:t></a:r></a:p>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Content {uid}"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph idx="{idx}"/></p:nvPr></p:nvSpPr>'
            f'{spPr}<p:txBody>'
            f'<a:bodyPr><a:normAutofit lnSpcReduction="10000"/></a:bodyPr>'
            f'<a:lstStyle/>{paras}</p:txBody></p:sp>')

def text_box(uid, name, x, y, w, h, lines, sz=2000, bold=False,
             color=None, fill=None, align='l', font=True):
    fill_xml = (f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
                if fill else '<a:noFill/>')
    paras = ''
    for ln in lines:
        rpr = f'lang="en-GB" sz="{sz}" dirty="0"'
        if bold: rpr += ' b="1"'
        c = f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else ''
        f_xml = FONT if font else ''
        if ln == '':
            paras += f'<a:p><a:pPr algn="{align}"/><a:endParaRPr lang="en-GB">{f_xml}</a:endParaRPr></a:p>'
        else:
            paras += (f'<a:p><a:pPr algn="{align}"/><a:r>'
                      f'<a:rPr {rpr}>{c}{f_xml}</a:rPr>'
                      f'<a:t>{_esc(ln)}</a:t></a:r></a:p>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="{name}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}<a:ln/></p:spPr>'
            f'<p:txBody>'
            f'<a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720" anchor="ctr"/>'
            f'<a:lstStyle/>{paras}</p:txBody></p:sp>')

def wrap_slide(body_xml):
    sld_ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
              'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:sld {sld_ns}><p:cSld><p:spTree>'
            f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            f'<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            f'{body_xml}</p:spTree></p:cSld>'
            f'<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')

def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
                  .replace('>', '&gt;').replace('"', '&quot;'))

# ── Slide builders ────────────────────────────────────────────────────

def build_cover(spec, base_unpacked, cover_img_dest_name):
    """Copy slide1.xml from base (which is lesson 1 cover) and patch day text."""
    xml = open(f'{base_unpacked}/ppt/slides/slide1.xml', encoding='utf-8').read()
    day = spec.get('day', 'Monday AM')
    # Replace the day text (Monday AM / Tuesday AM etc.)
    for old_day in ['Monday AM','Tuesday AM','Tuesday PM','Wednesday AM',
                    'Thursday AM','Friday AM','Friday PM']:
        if old_day in xml:
            xml = xml.replace(old_day, day, 1)
            break
    # Swap cover image to user-supplied one
    rels = open(f'{base_unpacked}/ppt/slides/_rels/slide1.xml.rels', encoding='utf-8').read()
    rels = re.sub(
        r'(<Relationship Id="rId4"[^>]*Target="\.\./media/)[^"]+(")',
        rf'\g<1>{cover_img_dest_name}\g<2>', rels)
    return xml, rels

def build_kc(kc_img_dest_name):
    xml = wrap_slide(
        f'<p:pic>'
        f'<p:nvPicPr><p:cNvPr id="2" name="KeyConcepts"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="rId2"/>'
        f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        f'</p:pic>'
    )
    rels = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            f'<Relationships xmlns="{RELS_NS}">'
            f'<Relationship Id="rId1" Type="{REL_LAY}" Target="../slideLayouts/slideLayout17.xml"/>'
            f'<Relationship Id="rId2" Type="{REL_IMG}" Target="../media/{kc_img_dest_name}"/>'
            f'</Relationships>')
    return xml, rels

def build_lo(spec, base_unpacked):
    """Copy slide2.xml from base and patch the three LO texts."""
    xml = open(f'{base_unpacked}/ppt/slides/slide2.xml', encoding='utf-8').read()
    rels = open(f'{base_unpacked}/ppt/slides/_rels/slide2.xml.rels', encoding='utf-8').read()

    # The LO slide has three body placeholders: idx 10 (WAL), 13 (TIB), 14 (ISB)
    # Find and replace their text content
    def replace_ph_text(x, target_idx, new_text):
        pattern = (rf'(<p:ph type="body"[^>]*idx="{target_idx}"[^>]*/>'
                   rf'.*?</p:nvSpPr>.*?<a:t>)[^<]*(</a:t>)')
        return re.sub(pattern, rf'\g<1>{_esc(new_text)}\g<2>', x, flags=re.DOTALL)

    xml = replace_ph_text(xml, '10', spec.get('wal', ''))
    xml = replace_ph_text(xml, '13', spec.get('tib', ''))
    xml = replace_ph_text(xml, '14', spec.get('isb', ''))
    return xml, rels

def build_warmup(spec):
    """Three-card warm-up slide (Layout 9 — You Do)."""
    title   = spec.get('title', 'Grammar Warm-Up')
    subtitle = spec.get('subtitle', '')
    cards   = spec.get('cards', [])  # list of {label, lines}

    cw, label_h = 3_413_760, 548_640
    body_h = 3_200_000
    hy = 2_200_000
    cx_positions = [618_786, 4_378_264, 8_168_640]
    hcolors = ['1F618D', 'CA6F1E', '6C3483']

    uid = 10
    shapes = ph_title(title, uid=uid)
    uid += 1

    if subtitle:
        shapes += text_box(uid, 'Subtitle', 618_786, 1_100_000, 10_973_228, 700_000,
                           [subtitle], sz=2133, fill=None, color='2C3E50')
        uid += 1

    for i, card in enumerate(cards[:3]):
        cx = cx_positions[i]
        hc = hcolors[i]
        label = card.get('label', str(i+1))
        lines = card.get('lines', [])

        # Header
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Hdr{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="{cx}" y="{hy}"/>'
                   f'<a:ext cx="{cw}" cy="{label_h}"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="{hc}"/></a:solidFill><a:ln/></p:spPr>'
                   f'<p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/>'
                   f'<a:p><a:pPr algn="ctr"/><a:r>'
                   f'<a:rPr lang="en-GB" sz="2400" b="1" dirty="0">'
                   f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>{FONT}</a:rPr>'
                   f'<a:t>{_esc(label)}</a:t></a:r></a:p></p:txBody></p:sp>')
        uid += 1

        # Body card
        by = hy + label_h
        body_paras = ''
        for ln in lines:
            if ln == '':
                body_paras += '<a:p><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'
            else:
                body_paras += (f'<a:p><a:r><a:rPr lang="en-GB" sz="2200" dirty="0">{FONT}</a:rPr>'
                               f'<a:t>{_esc(ln)}</a:t></a:r></a:p>')
        shapes += (f'<p:sp><p:nvSpPr><p:cNvPr id="{uid}" name="Body{uid}"/>'
                   f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                   f'<p:spPr><a:xfrm><a:off x="{cx}" y="{by}"/>'
                   f'<a:ext cx="{cw}" cy="{body_h}"/></a:xfrm>'
                   f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                   f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:ln/>'
                   f'<a:effectLst><a:outerShdw blurRad="50800" dist="25400" dir="8100000" '
                   f'algn="bl" rotWithShape="0">'
                   f'<a:srgbClr val="000000"><a:alpha val="10000"/></a:srgbClr>'
                   f'</a:outerShdw></a:effectLst></p:spPr>'
                   f'<p:txBody><a:bodyPr lIns="91440" tIns="91440" rIns="91440" '
                   f'bIns="91440" anchor="t"/><a:lstStyle/>{body_paras}</p:txBody></p:sp>')
        uid += 1

    return inject_timer(wrap_slide(shapes)), rels_str(LAYOUT['you_do'])

def build_we_do(spec):
    title = spec.get('title', '')
    lines = spec.get('lines', [])
    body  = ph_title(title) + ph_body(lines)
    return inject_timer(wrap_slide(body)), rels_str(LAYOUT['we_do'])

def build_i_do(spec):
    title = spec.get('title', 'Adding speech punctuation')
    ll    = spec.get('left_label', '')
    lr    = [spec.get('left_lines', [])] if isinstance(spec.get('left_lines'), str) else spec.get('left_lines', [])
    rl    = spec.get('right_label', '')
    rr    = [spec.get('right_lines', [])] if isinstance(spec.get('right_lines'), str) else spec.get('right_lines', [])

    col_w = 5_500_000; label_h = 440_000; lx = 250_000; rx = 6_350_000
    col_y = 1_450_000; body_h = 4_800_000

    shapes = ph_title(title)
    shapes += text_box(10, 'LL', lx, col_y, col_w, label_h,
                       [ll], sz=1800, bold=True, fill='1F618D', color='FFFFFF', align='ctr')
    shapes += text_box(11, 'LB', lx, col_y+label_h, col_w, body_h,
                       lr, sz=2400, fill='EBF5FB', color='1A252F', align='l')
    shapes += text_box(12, 'RL', rx, col_y, col_w, label_h,
                       [rl], sz=1800, bold=True, fill='1E8449', color='FFFFFF', align='ctr')
    shapes += text_box(13, 'RB', rx, col_y+label_h, col_w, body_h,
                       rr, sz=2200, fill='EAFAF1', color='1A252F', align='l')
    shapes += text_box(14, 'Arrow', 5_870_000, col_y+label_h+1_800_000, 430_000, 550_000,
                       ['\u2192'], sz=5200, fill=None, color='1A252F', align='ctr', font=False)
    return inject_timer(wrap_slide(shapes)), rels_str(LAYOUT['i_do'])

def build_you_do(spec):
    title = spec.get('title', '')
    lines = spec.get('lines', [])
    # Optional challenge bar
    challenge = spec.get('challenge', '')
    shapes = ph_title(title) + ph_body(lines)
    if challenge:
        shapes += text_box(10, 'Challenge', 618_786, 3_900_000, 10_973_228, 500_000,
                           ['Challenge: ' + challenge], sz=1900, bold=False,
                           fill='1F618D', color='FFFFFF', align='l')
    return inject_timer(wrap_slide(shapes)), rels_str(LAYOUT['you_do'])

def build_you_do_trio(spec):
    """You Do Trio slide: no title (icon does that), extended body box."""
    lines = spec.get('lines', [])
    # Remove title, extend body using user-validated dimensions
    # cx=10,206,000 (28.35cm) cy=6,199,200 (17.22cm) x=246,528 y=365,125
    XFRM = ('<a:xfrm><a:off x="246528" y="365125"/>'
            '<a:ext cx="10206000" cy="6199200"/></a:xfrm>')
    body = ph_body(lines, uid=3, idx=1, xfrm_xml=XFRM)
    return inject_timer(wrap_slide(body)), rels_str(LAYOUT['you_do_trio'])

def build_book_page(spec):
    label = spec.get('label', 'book spread')
    lines = [f'[ INSERT BOOK SPREAD: {label} ]',
             '', f'Display the double-page spread: {label}']
    note = text_box(2, 'Note', 300_000, 250_000, 11_592_000, 6_100_000,
                    lines, sz=2400, fill='F2F3F4', color='1A252F', align='ctr')
    return inject_timer(wrap_slide(note)), rels_str(LAYOUT['blank'])

def build_rules_slide(spec):
    """Carry-over slide: verbatim XML provided (e.g. speech punctuation checklist)."""
    xml  = spec.get('source_slide_xml', '')
    rels_raw = spec.get('source_slide_rels', '')
    if not xml:
        raise ValueError("rules slide requires source_slide_xml")
    # Inject timer if not already present
    if 'TimerPH' not in xml and 'idx="15"' not in xml:
        xml = inject_timer(xml)
    return xml, rels_raw

def build_learning_review(spec, base_unpacked):
    """Copy slide14.xml from base (Learning Review) and patch the three questions."""
    # Find the learning review slide in the base (it's the last slide)
    # In the base PPTX it is stored as slide15.xml (15th slide in lesson 2)
    # We'll locate it by checking for Learning Review layout (14)
    import xml.etree.ElementTree as ET
    slides_dir = f'{base_unpacked}/ppt/slides'
    rels_dir   = f'{base_unpacked}/ppt/slides/_rels'

    review_xml = review_rels = None
    for i in range(1, 20):
        rp = os.path.join(rels_dir, f'slide{i}.xml.rels')
        if not os.path.exists(rp): continue
        if 'slideLayout14' in open(rp).read():
            review_xml  = open(os.path.join(slides_dir, f'slide{i}.xml'), encoding='utf-8').read()
            review_rels = open(rp, encoding='utf-8').read()
            break

    if not review_xml:
        raise RuntimeError("Could not find Learning Review slide in base PPTX")

    q1 = spec.get('q1', '')
    q2 = spec.get('q2', '')
    q3 = spec.get('q3', '')

    def patch_q(xml, idx, text):
        return re.sub(
            rf'(<p:ph type="body"[^>]*idx="{idx}"[^>]*/></p:nvPr></p:nvSpPr>.*?<a:t>)[^<]*(</a:t>)',
            rf'\g<1>{_esc(text)}\g<2>', xml, flags=re.DOTALL)

    review_xml = patch_q(review_xml, '10', q1)
    review_xml = patch_q(review_xml, '11', q2)
    review_xml = patch_q(review_xml, '12', q3)

    if 'TimerPH' not in review_xml and 'idx="15"' not in review_xml:
        review_xml = inject_timer(review_xml)

    return review_xml, review_rels

# ── Main assembler ────────────────────────────────────────────────────

def assemble(args, slide_specs):
    base_pptx   = args.base
    kc_img_path = args.kc
    cover_path  = args.cover
    out_dir     = args.out

    os.makedirs(out_dir, exist_ok=True)
    build_tmp = os.path.join(out_dir, '_build_tmp')
    shutil.rmtree(build_tmp, ignore_errors=True)
    os.makedirs(build_tmp)

    # Unpack base PPTX
    import subprocess
    subprocess.run(['unzip', '-o', base_pptx, '-d', build_tmp + '/'], capture_output=True)

    # Copy assets into media
    media_dir = f'{build_tmp}/ppt/media'
    kc_dest   = 'kc_wheel.png'
    shutil.copy(kc_img_path, os.path.join(media_dir, kc_dest))

    # Cover image
    cover_ext  = os.path.splitext(cover_path)[1].lower()
    cover_dest = f'book_cover{cover_ext}'
    shutil.copy(cover_path, os.path.join(media_dir, cover_dest))

    # Ensure content types include jpg/png
    ct_path = f'{build_tmp}/[Content_Types].xml'
    ct = open(ct_path).read()
    for ext, mime in [('jpg','image/jpeg'), ('jpeg','image/jpeg'), ('png','image/png')]:
        if f'Extension="{ext}"' not in ct:
            ct = ct.replace('</Types>', f'<Default Extension="{ext}" ContentType="{mime}"/></Types>')
    open(ct_path, 'w').write(ct)

    # Build each slide
    slides = []  # list of (xml_str, rels_str)

    for spec in slide_specs:
        stype = spec.get('type')

        if stype == 'cover':
            xml, rels = build_cover(spec, build_tmp, cover_dest)
        elif stype == 'kc':
            xml, rels = build_kc(kc_dest)
        elif stype == 'lo':
            xml, rels = build_lo(spec, build_tmp)
        elif stype == 'warmup':
            xml, rels = build_warmup(spec)
        elif stype == 'we_do':
            xml, rels = build_we_do(spec)
        elif stype == 'i_do':
            xml, rels = build_i_do(spec)
        elif stype == 'you_do':
            xml, rels = build_you_do(spec)
        elif stype == 'you_do_trio':
            xml, rels = build_you_do_trio(spec)
        elif stype == 'book_page':
            xml, rels = build_book_page(spec)
        elif stype == 'rules':
            xml, rels = build_rules_slide(spec)
        elif stype == 'learning_review':
            xml, rels = build_learning_review(spec, build_tmp)
        else:
            print(f"WARNING: unknown slide type '{stype}', skipping", file=sys.stderr)
            continue

        slides.append((xml, rels))

    # Write slide files into build tmp
    sd = f'{build_tmp}/ppt/slides'
    rd = f'{build_tmp}/ppt/slides/_rels'

    for f in os.listdir(sd):
        if f.endswith('.xml'): os.remove(os.path.join(sd, f))
    for f in os.listdir(rd):
        if f.endswith('.rels'): os.remove(os.path.join(rd, f))

    for i, (sxml, srels) in enumerate(slides, 1):
        open(os.path.join(sd, f'slide{i}.xml'), 'w', encoding='utf-8').write(sxml)
        open(os.path.join(rd, f'slide{i}.xml.rels'), 'w', encoding='utf-8').write(srels)

    # Update presentation.xml
    pp  = f'{build_tmp}/ppt/presentation.xml'
    pr  = f'{build_tmp}/ppt/_rels/presentation.xml.rels'
    px  = open(pp, encoding='utf-8').read()
    prx = open(pr, encoding='utf-8').read()
    prx = re.sub(r'<Relationship[^/]*/slides/slide\d+[^>]*/>', '', prx)
    nr = ni = ''
    for i in range(1, len(slides)+1):
        rid = f'rId{4+i}'
        nr += f'<Relationship Id="{rid}" Type="{REL_SLD}" Target="slides/slide{i}.xml"/>'
        ni += f'<p:sldId id="{4100+i}" r:id="{rid}"/>'
    open(pr, 'w').write(prx.replace('</Relationships>', nr+'</Relationships>'))
    open(pp, 'w').write(re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>',
        f'<p:sldIdLst>{ni}</p:sldIdLst>', px, flags=re.DOTALL))

    # Clear notes
    nd = f'{build_tmp}/ppt/notesSlides'
    if os.path.exists(nd):
        for f in os.listdir(nd):
            if f.endswith('.xml') or f.endswith('.rels'):
                os.remove(os.path.join(nd, f))
    os.makedirs(f'{nd}/_rels', exist_ok=True)

    # Determine output filename  T[term]W[week] - Lesson [n] - Writers - [Topic]
    term  = getattr(args, 'term', 5)
    week  = getattr(args, 'week', 1)
    lesson = getattr(args, 'lesson', 1)
    topic = getattr(args, 'topic', 'Writing').replace(' ', '_')
    out_name = f'T{term}W{week}_-_Lesson_{lesson}_-_Writers_-_{topic}.pptx'
    out_path = os.path.join(out_dir, out_name)

    if os.path.exists(out_path): os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(build_tmp):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, build_tmp))

    shutil.rmtree(build_tmp)
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base',        required=True)
    parser.add_argument('--kc',          required=True)
    parser.add_argument('--cover',       required=True)
    parser.add_argument('--term',        type=int, default=5)
    parser.add_argument('--week',        type=int, default=1)
    parser.add_argument('--lesson',      type=int, required=True)
    parser.add_argument('--topic',       default='Writing')
    parser.add_argument('--out',         default='/home/claude')
    parser.add_argument('--slides-json', default=None)
    args = parser.parse_args()

    if args.slides_json:
        slide_specs = json.load(open(args.slides_json))
    else:
        slide_specs = json.load(sys.stdin)

    out_path = assemble(args, slide_specs)
    print(f"OUTPUT: {out_path}")

if __name__ == '__main__':
    main()
