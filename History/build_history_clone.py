#!/usr/bin/env python3
"""
build_history_clone.py
Builds a History lesson PPTX by cloning slides from the master PPTX.
NO shapes are constructed from scratch. Everything is cloned from the master
and text content is replaced. Concept colour is swapped via XML string substitution.

Usage:
    python3 build_history_clone.py <mtp.json> --lesson N --master <master.pptx> --out <out.pptx>
"""

import os, sys, shutil, zipfile, copy, json, argparse
from lxml import etree

# ── Namespaces ────────────────────────────────────────────────────────────────
P   = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A   = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_  = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT  = 'http://schemas.openxmlformats.org/package/2006/content-types'

# ── Concept colours (border, light-bg) ───────────────────────────────────────
CONCEPT_COLOURS = {
    'civilisation': ('FFC000', 'FFF3CC'),
    'empire':       ('7438A5', 'EFEFFF'),
    'invasion':     ('C05102', 'FFEBEB'),
    'monarchy':     ('00AE4B', 'E2F0D9'),
    'revolution':   ('4573C4', 'DAE3F3'),
}
MASTER_BORDER = 'FFC000'
MASTER_BG     = 'FFF3CC'

# ── Master slide → purpose ────────────────────────────────────────────────────
# (1-indexed as they appear in the master PPTX)
SLIDE_KEY_QUESTION     = 1   # Layout 1
SLIDE_TITLE_IMAGE      = 2   # Layout 6 (full-bleed enquiry image)
SLIDE_CONCEPTS         = 3   # Layout 7 (substantive concept + curriculum timeline)
SLIDE_BUILDING_BLOCKS  = 4   # Layout 8 (brick wall)
SLIDE_LO               = 5   # Layout 5 What/Why/How
SLIDE_KWL              = 6   # Layout 10 (KWL table — lesson 1 only)
SLIDE_RECAP_QUIZ       = 7   # Layout 11 (Recap Quiz — lessons 2+)
SLIDE_VOCABULARY       = 8   # Layout 3 Vocabulary
SLIDE_I_DO             = 9   # Layout 8 I Do
SLIDE_WE_DO            = 10  # Layout 9 We Do
SLIDE_YOU_DO_TRIO      = 11  # Layout 10 You Do Trio
SLIDE_YOU_DO           = 12  # Layout 11 You Do
SLIDE_CONTEXT          = 13  # Layout 6 (contextualising activity — not currently used)
SLIDE_LEARNING_REVIEW  = 14  # Layout 12

ACTIVITY_SLIDE_MAP = {
    'i_do':        SLIDE_I_DO,
    'we_do':       SLIDE_WE_DO,
    'you_do_trio': SLIDE_YOU_DO_TRIO,
    'you_do':      SLIDE_YOU_DO,
}


# ── ZIP helpers ───────────────────────────────────────────────────────────────
def unzip(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    with zipfile.ZipFile(src, 'r') as z:
        z.extractall(dst)

def rezip(src_dir, dst_pptx):
    os.makedirs(os.path.dirname(os.path.abspath(dst_pptx)), exist_ok=True)
    if os.path.exists(dst_pptx):
        os.remove(dst_pptx)
    with zipfile.ZipFile(dst_pptx, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src_dir):
            for f in files:
                fp = os.path.join(root, f)
                z.write(fp, os.path.relpath(fp, src_dir))


# ── Concept colour substitution ───────────────────────────────────────────────
def apply_concept_colour(xml_bytes, concept):
    """Swap amber master colours → concept-specific colours in a slide's XML bytes."""
    border, bg = CONCEPT_COLOURS.get(concept.lower(), (MASTER_BORDER, MASTER_BG))
    s = xml_bytes.decode('utf-8')
    s = s.replace(MASTER_BORDER, border)
    s = s.replace(MASTER_BG,     bg)
    return s.encode('utf-8')


def apply_concept_colour_to_layouts(work_dir, concept):
    """
    Swap concept colours in ALL slideLayout XML files.
    This is essential — layout files contain the amber frames/bars that
    appear on every slide. Without this, non-civilisation concepts still
    show amber borders.
    """
    layouts_dir = os.path.join(work_dir, 'ppt', 'slideLayouts')
    if not os.path.isdir(layouts_dir):
        return
    for fname in os.listdir(layouts_dir):
        if not fname.endswith('.xml'):
            continue
        path = os.path.join(layouts_dir, fname)
        with open(path, 'rb') as f:
            data = f.read()
        if MASTER_BORDER.encode() in data or MASTER_BG.encode() in data:
            data = apply_concept_colour(data, concept)
            with open(path, 'wb') as f:
                f.write(data)


# ── Placeholder text helpers ──────────────────────────────────────────────────
def find_ph(sp_list, idx=None, ph_type=None):
    """Return the first sp element whose ph matches idx or type."""
    for sp in sp_list:
        ph = sp.find(f'.//{{{P}}}nvPr/{{{P}}}ph')
        if ph is None:
            continue
        if idx is not None and ph.get('idx') == str(idx):
            return sp
        if ph_type is not None and ph.get('type') == ph_type:
            return sp
    return None


def set_para_text(para_el, new_text):
    """
    Replace the text in a paragraph element.
    Preserves the first run's rPr (formatting). Removes extra runs/texts.
    """
    ns_a = f'{{{A}}}'
    runs = para_el.findall(f'{ns_a}r')
    if not runs:
        # No runs — create one
        r = etree.SubElement(para_el, f'{ns_a}r')
        rPr = etree.SubElement(r, f'{ns_a}rPr')
        rPr.set('lang', 'en-GB')
        rPr.set('noProof', '1')
        t = etree.SubElement(r, f'{ns_a}t')
        t.text = new_text
        return
    # Keep first run, remove others
    first_run = runs[0]
    for extra in runs[1:]:
        para_el.remove(extra)
    # Remove any stray a:t outside runs
    for t_el in para_el.findall(f'{ns_a}t'):
        para_el.remove(t_el)
    # Set text in first run
    t_el = first_run.find(f'{ns_a}t')
    if t_el is None:
        t_el = etree.SubElement(first_run, f'{ns_a}t')
    t_el.text = new_text


def replace_ph_text(slide_tree, ph_idx=None, ph_type=None, new_text=''):
    """
    Find the placeholder in the slide and replace its text.
    For placeholders with a single paragraph of content.
    """
    sps = slide_tree.findall(f'.//{{{P}}}sp')
    sp = find_ph(sps, idx=ph_idx, ph_type=ph_type)
    if sp is None:
        return
    txBody = sp.find(f'{{{P}}}txBody')
    if txBody is None:
        return
    paras = txBody.findall(f'{{{A}}}p')
    if not paras:
        return
    # Set text in first paragraph; clear extra paragraphs
    set_para_text(paras[0], new_text)
    for extra in paras[1:]:
        txBody.remove(extra)


# ── Vocab slide replacement ───────────────────────────────────────────────────
def replace_vocab_slide(slide_tree, vocab_list):
    """
    Replace vocabulary word/definition pairs in the vocab slide.
    Rebuilds the paragraph list with correct formatting:
      - Word: bold, lvl=0
      - Definition: lvl=1, Wingdings v bullet, 75% bullet size
      - Spacer: empty para, buNone
    Handles 1–5 vocabulary items.
    """
    sps = slide_tree.findall(f'.//{{{P}}}sp')
    # Find the content placeholder (large text box with all vocab)
    sp = None
    for s in sps:
        cNvPr = s.find(f'.//{{{P}}}nvSpPr/{{{P}}}cNvPr')
        if cNvPr is not None and 'Content Placeholder' in cNvPr.get('name', ''):
            sp = s
            break
    if sp is None:
        return

    txBody = sp.find(f'{{{P}}}txBody')
    if txBody is None:
        return

    # Remove all existing paragraphs
    for p in txBody.findall(f'{{{A}}}p'):
        txBody.remove(p)

    def make_word_para(word_text):
        p = etree.SubElement(txBody, f'{{{A}}}p')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB')
        rPr.set('b', '1')
        rPr.set('noProof', '1')
        t = etree.SubElement(r, f'{{{A}}}t')
        t.text = word_text
        return p

    def make_def_para(def_text):
        p = etree.SubElement(txBody, f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('lvl', '1')
        buSzPct = etree.SubElement(pPr, f'{{{A}}}buSzPct')
        buSzPct.set('val', '75000')
        buFont = etree.SubElement(pPr, f'{{{A}}}buFont')
        buFont.set('typeface', 'Wingdings')
        buFont.set('pitchFamily', '2')
        buFont.set('charset', '2')
        buChar = etree.SubElement(pPr, f'{{{A}}}buChar')
        buChar.set('char', 'v')
        r = etree.SubElement(p, f'{{{A}}}r')
        rPr = etree.SubElement(r, f'{{{A}}}rPr')
        rPr.set('lang', 'en-GB')
        rPr.set('noProof', '1')
        t = etree.SubElement(r, f'{{{A}}}t')
        t.text = def_text
        return p

    def make_spacer_para():
        p = etree.SubElement(txBody, f'{{{A}}}p')
        pPr = etree.SubElement(p, f'{{{A}}}pPr')
        pPr.set('marL', '0')
        pPr.set('indent', '0')
        buNone = etree.SubElement(pPr, f'{{{A}}}buNone')
        ePr = etree.SubElement(p, f'{{{A}}}endParaRPr')
        ePr.set('lang', 'en-GB')
        ePr.set('sz', '800')
        ePr.set('noProof', '1')
        return p

    items = vocab_list[:5]
    # Fill remaining slots up to 5 with placeholders
    while len(items) < 5:
        n = len(items) + 1
        items.append({'word': f'Word / Phrase {n}', 'definition': f'Definition {n}'})

    for i, item in enumerate(items):
        make_word_para(item.get('word', f'Word {i+1}'))
        make_def_para(item.get('definition', f'Definition {i+1}'))
        if i < 4:  # No trailing spacer after last entry
            make_spacer_para()


# ── Quiz slide replacement ────────────────────────────────────────────────────
def replace_quiz_slide(slide_tree, quiz_list):
    """
    Replace quiz Q&A text in the recap quiz slide.
    Master paragraph structure (per Q&A pair):
      para[n*3+0]: Question (numbered, lvl=0)
      para[n*3+1]: Answer (lvl=1, Wingdings ü bullet, green)
      para[n*3+2]: Spacer (empty, lvl=1)
    Handles up to 5 Q&A pairs.
    """
    sps = slide_tree.findall(f'.//{{{P}}}sp')
    sp = find_ph(sps, idx=1)
    if sp is None:
        return
    txBody = sp.find(f'{{{P}}}txBody')
    if txBody is None:
        return
    paras = txBody.findall(f'{{{A}}}p')

    for i, item in enumerate(quiz_list[:5]):
        q_idx = i * 3
        a_idx = i * 3 + 1

        # Replace question text in para[q_idx]
        if q_idx < len(paras):
            q_para = paras[q_idx]
            runs = q_para.findall(f'{{{A}}}r')
            if runs:
                t = runs[0].find(f'{{{A}}}t')
                if t is not None:
                    t.text = item.get('question', '')
            else:
                set_para_text(q_para, item.get('question', ''))

        # Replace answer text in para[a_idx]
        if a_idx < len(paras):
            a_para = paras[a_idx]
            # Clear all existing runs and rebuild with correct format
            for r in a_para.findall(f'{{{A}}}r'):
                a_para.remove(r)
            r = etree.SubElement(a_para, f'{{{A}}}r')
            rPr = etree.SubElement(r, f'{{{A}}}rPr')
            rPr.set('lang', 'en-GB')
            rPr.set('b', '1')
            rPr.set('noProof', '1')
            fill = etree.SubElement(rPr, f'{{{A}}}solidFill')
            clr = etree.SubElement(fill, f'{{{A}}}srgbClr')
            clr.set('val', '00B050')
            t = etree.SubElement(r, f'{{{A}}}t')
            t.text = item.get('answer', '')


# ── Building blocks slide ─────────────────────────────────────────────────────
def update_building_blocks(slide_tree, lesson_num, mtp_lessons):
    """
    Show only the first lesson_num brick groups on the building blocks slide.
    Also updates each visible brick's text from the MTP building_block_text.

    Each brick is a p:grpSp (group shape) element — NOT a p:sp.
    The spTree contains: nvGrpSpPr, grpSpPr, 1 title p:sp, then 14 p:grpSp bricks.
    """
    spTree = slide_tree.find(f'.//{{{P}}}spTree')
    if spTree is None:
        return

    grp_tag = f'{{{P}}}grpSp'

    # Collect all brick group shapes (p:grpSp direct children of spTree)
    brick_groups = [el for el in list(spTree) if el.tag == grp_tag]

    if not brick_groups:
        print('  [WARN] update_building_blocks: no grpSp elements found in spTree')
        return

    # Build lesson text lookup
    lesson_texts = {}
    for lesson in mtp_lessons:
        n = lesson.get('lesson_number')
        text = lesson.get('building_block_text', f'Lesson {n}')
        if n:
            lesson_texts[n] = text

    # Remove ALL brick groups from spTree
    for grp in brick_groups:
        spTree.remove(grp)

    # Re-add only the first lesson_num groups, with updated text
    for i, grp in enumerate(brick_groups[:lesson_num]):
        lesson_n = i + 1
        bb_text = lesson_texts.get(lesson_n, f'Lesson {lesson_n}')

        # Update the text run inside the grpSp — find first non-empty a:t
        for t_el in grp.iter(f'{{{A}}}t'):
            if t_el.text and t_el.text.strip():
                t_el.text = bb_text
                break

        spTree.append(grp)

    print(f'  Building blocks: showing {min(lesson_num, len(brick_groups))} of {len(brick_groups)} bricks')


# ── Remove bottom bar (Shape 1) from a slide ─────────────────────────────────
def remove_bottom_bar(slide_tree):
    """
    Remove the amber/concept-colour bottom bar (Shape 1) from slides
    where it is unwanted (e.g. the Recap Quiz slide).
    """
    spTree = slide_tree.find(f'.//{{{P}}}spTree')
    if spTree is None:
        return
    for sp in list(spTree):
        if sp.tag != f'{{{P}}}sp':
            continue
        cNvPr = sp.find(f'.//{{{P}}}nvSpPr/{{{P}}}cNvPr')
        if cNvPr is not None and cNvPr.get('name') == 'Shape 1':
            spTree.remove(sp)
            break


# ── Slide file helpers ────────────────────────────────────────────────────────
def read_slide_xml(work_dir, slide_num):
    path = os.path.join(work_dir, 'ppt', 'slides', f'slide{slide_num}.xml')
    with open(path, 'rb') as f:
        return f.read()

def read_slide_rels(work_dir, slide_num):
    path = os.path.join(work_dir, 'ppt', 'slides', '_rels', f'slide{slide_num}.xml.rels')
    with open(path, 'rb') as f:
        return f.read()

def write_slide(work_dir, slide_num, xml_bytes):
    path = os.path.join(work_dir, 'ppt', 'slides', f'slide{slide_num}.xml')
    with open(path, 'wb') as f:
        f.write(xml_bytes)

def write_slide_rels(work_dir, slide_num, rels_bytes):
    os.makedirs(os.path.join(work_dir, 'ppt', 'slides', '_rels'), exist_ok=True)
    path = os.path.join(work_dir, 'ppt', 'slides', '_rels', f'slide{slide_num}.xml.rels')
    with open(path, 'wb') as f:
        f.write(rels_bytes)


# ── Presentation.xml rewrite ──────────────────────────────────────────────────
def rewrite_presentation_xml(work_dir, slide_count):
    """
    Rewrite presentation.xml so it lists exactly slide_count slides (slide1..slideN).
    Also updates _rels/presentation.xml.rels.
    Preserves all non-slide content (theme, master, layouts, etc.).
    """
    prs_path = os.path.join(work_dir, 'ppt', 'presentation.xml')
    rels_path = os.path.join(work_dir, 'ppt', '_rels', 'presentation.xml.rels')

    with open(prs_path, 'rb') as f:
        prs_tree = etree.parse(f)
    with open(rels_path, 'rb') as f:
        rels_tree = etree.parse(f)

    prs_root = prs_tree.getroot()
    rels_root = rels_tree.getroot()

    # Remove all existing slide relationships from rels
    rel_ns = f'{{{PKG}}}Relationship'
    slide_type = f'{R_}/slide'
    for rel in rels_root.findall(rel_ns):
        if rel.get('Type') == slide_type:
            rels_root.remove(rel)

    # Add new slide relationships rId_s1..rId_sN
    for i in range(1, slide_count + 1):
        rel = etree.SubElement(rels_root, rel_ns)
        rel.set('Id', f'rId_s{i}')
        rel.set('Type', slide_type)
        rel.set('Target', f'slides/slide{i}.xml')

    # Rewrite sldIdLst in presentation.xml
    sldIdLst = prs_root.find(f'{{{P}}}sldIdLst')
    if sldIdLst is None:
        sldIdLst = etree.SubElement(prs_root, f'{{{P}}}sldIdLst')
    for sldId in sldIdLst.findall(f'{{{P}}}sldId'):
        sldIdLst.remove(sldId)
    for i in range(1, slide_count + 1):
        sldId = etree.SubElement(sldIdLst, f'{{{P}}}sldId')
        sldId.set('id', str(255 + i))
        sldId.set(f'{{{R_}}}id', f'rId_s{i}')

    prs_tree.write(prs_path, xml_declaration=True, encoding='UTF-8', standalone=True)
    rels_tree.write(rels_path, xml_declaration=True, encoding='UTF-8', standalone=True)


# ── Content_Types.xml update ──────────────────────────────────────────────────
def update_content_types(work_dir, slide_count):
    ct_path = os.path.join(work_dir, '[Content_Types].xml')
    with open(ct_path, 'rb') as f:
        ct_tree = etree.parse(f)
    ct_root = ct_tree.getroot()
    ns_ct = 'http://schemas.openxmlformats.org/package/2006/content-types'
    ovr_tag = f'{{{ns_ct}}}Override'
    slide_ct = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
    to_remove = [ov for ov in ct_root.findall(ovr_tag) if ov.get('ContentType') == slide_ct]
    for ov in to_remove:
        ct_root.remove(ov)
    for i in range(1, slide_count + 1):
        ov = etree.SubElement(ct_root, ovr_tag)
        ov.set('PartName', f'/ppt/slides/slide{i}.xml')
        ov.set('ContentType', slide_ct)
    ct_tree.write(ct_path, xml_declaration=True, encoding='UTF-8', standalone=True)


# ── Delete unused slides ──────────────────────────────────────────────────────
def remove_all_slides(work_dir):
    """Remove all slide XML and rels files from the work directory."""
    slides_dir = os.path.join(work_dir, 'ppt', 'slides')
    rels_dir   = os.path.join(slides_dir, '_rels')
    for f in os.listdir(slides_dir):
        if f.startswith('slide') and f.endswith('.xml'):
            os.remove(os.path.join(slides_dir, f))
    if os.path.isdir(rels_dir):
        for f in os.listdir(rels_dir):
            if f.startswith('slide') and f.endswith('.rels'):
                os.remove(os.path.join(rels_dir, f))


# ── Lesson slide rels (layout relationship) ───────────────────────────────────
LAYOUT_FOR_MASTER_SLIDE = {
    1:  'slideLayout1.xml',
    2:  'slideLayout6.xml',
    3:  'slideLayout7.xml',
    4:  'slideLayout8.xml',
    5:  'slideLayout5.xml',
    6:  'slideLayout10.xml',
    7:  'slideLayout11.xml',
    8:  'slideLayout3.xml',
    9:  'slideLayout8.xml',
    10: 'slideLayout9.xml',
    11: 'slideLayout10.xml',
    12: 'slideLayout11.xml',
    13: 'slideLayout6.xml',
    14: 'slideLayout12.xml',
}

def make_slide_rels(master_slide_num, extra_image_rels=None):
    """
    Build a minimal slide rels XML string.
    Always includes the layout relationship.
    extra_image_rels: list of (rId, filename) tuples for image references.
    """
    layout = LAYOUT_FOR_MASTER_SLIDE[master_slide_num]
    rels = [f'<Relationship Id="rId1" Type="{R_}/slideLayout" Target="../slideLayouts/{layout}"/>']
    if extra_image_rels:
        for rid, fname in extra_image_rels:
            rels.append(
                f'<Relationship Id="{rid}" Type="{R_}/image" Target="../media/{fname}"/>'
            )
    inner = '\n  '.join(rels)
    return (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{PKG}">\n  {inner}\n</Relationships>'
    ).encode('utf-8')


# ── Build one lesson ──────────────────────────────────────────────────────────
def build_lesson(mtp, lesson_num, master_pptx, out_pptx):
    lesson = next((l for l in mtp['lessons'] if l['lesson_number'] == lesson_num), None)
    if lesson is None:
        raise ValueError(f'Lesson {lesson_num} not found in MTP')

    concept    = mtp.get('concept', 'civilisation').lower()
    key_q      = mtp['key_question']
    challenge  = mtp.get('challenge', '')
    is_lesson1 = (lesson_num == 1)

    print(f'Building Lesson {lesson_num}: {lesson.get("building_block_text", "")}')
    colours = CONCEPT_COLOURS.get(concept, (MASTER_BORDER, MASTER_BG))
    print(f'  Concept: {concept}  Border: #{colours[0]}  BG: #{colours[1]}')

    # Extract master to temp dir
    work = f'/tmp/hist_build_{os.getpid()}'
    unzip(master_pptx, work)

    # Apply concept colour to ALL layout files — fixes concept borders on every slide
    apply_concept_colour_to_layouts(work, concept)

    # Read all master slide XML
    master_slides = {}
    master_rels   = {}
    for n in range(1, 15):
        master_slides[n] = read_slide_xml(work, n)
        master_rels[n]   = read_slide_rels(work, n)

    # Remove all slides from work dir — we'll write our own
    remove_all_slides(work)

    out_slides = []   # list of (master_slide_num, xml_bytes, rels_bytes)

    # ── Slide 1: Key Question ─────────────────────────────────────────────────
    xml = master_slides[SLIDE_KEY_QUESTION]
    xml = apply_concept_colour(xml, concept)
    tree = etree.fromstring(xml)
    replace_ph_text(tree, ph_idx=12, new_text=key_q)
    replace_ph_text(tree, ph_idx=10, new_text=challenge)
    xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    out_slides.append((SLIDE_KEY_QUESTION, xml, make_slide_rels(SLIDE_KEY_QUESTION)))
    print(f'  [1] key_question')

    # ── Slide 2: Title Image ──────────────────────────────────────────────────
    xml  = master_slides[SLIDE_TITLE_IMAGE]
    xml  = apply_concept_colour(xml, concept)
    rels = master_rels[SLIDE_TITLE_IMAGE]
    out_slides.append((SLIDE_TITLE_IMAGE, xml, rels))
    print(f'  [2] title_image')

    # ── Slide 3: Substantive Concept + timeline ───────────────────────────────
    xml = master_slides[SLIDE_CONCEPTS]
    xml = apply_concept_colour(xml, concept)
    tree = etree.fromstring(xml)
    # Update the concept label (TextBox 7 contains the concept word)
    sps = tree.findall(f'.//{{{P}}}sp')
    for sp in sps:
        cNvPr = sp.find(f'.//{{{P}}}nvSpPr/{{{P}}}cNvPr')
        if cNvPr is not None and cNvPr.get('name', '') == 'TextBox 7':
            set_para_text(
                sp.find(f'{{{P}}}txBody').findall(f'{{{A}}}p')[0],
                concept.capitalize()
            )
    xml  = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    rels = master_rels[SLIDE_CONCEPTS]
    out_slides.append((SLIDE_CONCEPTS, xml, rels))
    print(f'  [3] concepts')

    # ── Slide 4: Building Blocks ──────────────────────────────────────────────
    xml = master_slides[SLIDE_BUILDING_BLOCKS]
    xml = apply_concept_colour(xml, concept)
    tree = etree.fromstring(xml)
    update_building_blocks(tree, lesson_num, mtp['lessons'])
    xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    out_slides.append((SLIDE_BUILDING_BLOCKS, xml, make_slide_rels(SLIDE_BUILDING_BLOCKS)))
    print(f'  [4] building_blocks (showing {lesson_num} of {mtp.get("total_lessons", 14)} bricks)')

    # ── Slide 5: What / Why / How ─────────────────────────────────────────────
    # Animations for this slide live in slideLayout5.xml — preserved by clone
    xml = master_slides[SLIDE_LO]
    xml = apply_concept_colour(xml, concept)
    tree = etree.fromstring(xml)
    replace_ph_text(tree, ph_type='title', new_text=key_q)
    replace_ph_text(tree, ph_idx=10, new_text=lesson.get('what', ''))
    replace_ph_text(tree, ph_idx=13, new_text=lesson.get('why', ''))
    replace_ph_text(tree, ph_idx=14, new_text=lesson.get('success', ''))
    xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    out_slides.append((SLIDE_LO, xml, make_slide_rels(SLIDE_LO)))
    print(f'  [5] lo')

    # ── Slide 6: KWL (lesson 1) or Recap Quiz (lessons 2+) ───────────────────
    if is_lesson1:
        xml = master_slides[SLIDE_KWL]
        xml = apply_concept_colour(xml, concept)
        # Fix typo in KWL title
        xml = xml.replace(b'bringing to thei enquiry', b'bringing to this enquiry')
        out_slides.append((SLIDE_KWL, xml, make_slide_rels(SLIDE_KWL)))
        print(f'  [6] kwl')
    else:
        quiz = lesson.get('quiz', [])
        xml  = master_slides[SLIDE_RECAP_QUIZ]
        xml  = apply_concept_colour(xml, concept)
        tree = etree.fromstring(xml)
        remove_bottom_bar(tree)
        replace_quiz_slide(tree, quiz)
        xml  = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        out_slides.append((SLIDE_RECAP_QUIZ, xml, make_slide_rels(SLIDE_RECAP_QUIZ)))
        print(f'  [6] recap_quiz ({len(quiz)} questions)')

    # ── Slide 7: Vocabulary ───────────────────────────────────────────────────
    vocab = lesson.get('vocabulary', [])
    xml   = master_slides[SLIDE_VOCABULARY]
    xml   = apply_concept_colour(xml, concept)
    tree  = etree.fromstring(xml)
    replace_vocab_slide(tree, vocab)
    xml   = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    out_slides.append((SLIDE_VOCABULARY, xml, make_slide_rels(SLIDE_VOCABULARY)))
    print(f'  [7] vocabulary ({len(vocab)} words)')

    # ── Variable lesson slides (I Do / We Do / You Do Trio / You Do) ──────────
    for slide_spec in lesson.get('slides', []):
        stype  = slide_spec['type']
        master = ACTIVITY_SLIDE_MAP.get(stype)
        if master is None:
            print(f'  [?] UNKNOWN slide type: {stype} — skipped')
            continue
        xml  = master_slides[master]
        xml  = apply_concept_colour(xml, concept)
        tree = etree.fromstring(xml)
        replace_ph_text(tree, ph_type='title', new_text=slide_spec.get('title', ''))
        replace_ph_text(tree, ph_idx=1, new_text=slide_spec.get('content', ''))
        xml  = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        out_slides.append((master, xml, make_slide_rels(master)))
        print(f'  [{len(out_slides)}] {stype}: {slide_spec.get("title", "")}')

    # ── Learning Review ───────────────────────────────────────────────────────
    xml  = master_slides[SLIDE_LEARNING_REVIEW]
    xml  = apply_concept_colour(xml, concept)
    tree = etree.fromstring(xml)
    review = lesson.get('learning_review', [])
    if len(review) >= 1:
        replace_ph_text(tree, ph_idx=17, new_text=review[0])
    if len(review) >= 2:
        replace_ph_text(tree, ph_idx=15, new_text=review[1])
    if len(review) >= 3:
        replace_ph_text(tree, ph_idx=16, new_text=review[2])
    xml  = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    out_slides.append((SLIDE_LEARNING_REVIEW, xml, make_slide_rels(SLIDE_LEARNING_REVIEW)))
    print(f'  [{len(out_slides)}] learning_review')

    # ── Write slides ──────────────────────────────────────────────────────────
    for i, (master_n, xml_bytes, rels_bytes) in enumerate(out_slides, 1):
        write_slide(work, i, xml_bytes)
        write_slide_rels(work, i, rels_bytes)

    # ── Update manifest files ─────────────────────────────────────────────────
    rewrite_presentation_xml(work, len(out_slides))
    update_content_types(work, len(out_slides))

    # ── Pack to output PPTX ───────────────────────────────────────────────────
    rezip(work, out_pptx)
    shutil.rmtree(work, ignore_errors=True)
    size = os.path.getsize(out_pptx)
    print(f'  → {out_pptx} ({size:,} bytes, {len(out_slides)} slides)')


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mtp_json')
    ap.add_argument('--lesson', type=int, required=True)
    ap.add_argument('--master', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    with open(args.mtp_json) as f:
        mtp = json.load(f)

    build_lesson(mtp, args.lesson, args.master, args.out)


if __name__ == '__main__':
    main()
