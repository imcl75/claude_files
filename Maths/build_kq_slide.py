"""
build_kq_slide.py
-----------------
Prepends a Key Question slide to a teaching PPTX.

Usage:
    python3 build_kq_slide.py <teaching_pptx> <key_question_text>

The KQ slide is built by:
1. Copying KQ_Slide_template.pptx wholesale via XML manipulation
2. Replacing "Replace this text" in TextBox 28 with the supplied question
3. Inserting the result as slide 1 of the teaching PPTX

NEVER rebuilds the slide from scratch. NEVER adds new shapes.
Template: assets/KQ_Slide_template.pptx
"""

import sys
import os
import shutil
import zipfile
import re
from lxml import etree

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'KQ_Slide_template.pptx')
PLACEHOLDER_TEXT = 'Replace this text'

NSMAP = {
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':   'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def _unpack(pptx_path, dest):
    """Unzip a PPTX into dest/."""
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(pptx_path, 'r') as z:
        z.extractall(dest)


def _repack(src_dir, out_path):
    """Repack a directory into a PPTX zip."""
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, src_dir)
                z.write(fpath, arcname)


def _replace_text_in_slide_xml(slide_xml_path, old_text, new_text):
    """
    Replace all <a:t> text nodes that together equal old_text with new_text,
    keeping the run formatting of the first run intact.
    """
    tree = etree.parse(slide_xml_path)
    root = tree.getroot()

    ns_a = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    # Walk all text bodies
    for txBody in root.iter(f'{{{ns_a}}}txBody'):
        for para in txBody.iter(f'{{{ns_a}}}p'):
            # Collect all runs
            runs = para.findall(f'.//{{{ns_a}}}r')
            full_text = ''.join(
                (r.find(f'{{{ns_a}}}t').text or '') for r in runs
                if r.find(f'{{{ns_a}}}t') is not None
            )
            if full_text == old_text:
                # Keep first run's rPr, replace its text, delete extras
                if runs:
                    first_r = runs[0]
                    t_el = first_r.find(f'{{{ns_a}}}t')
                    if t_el is not None:
                        t_el.text = new_text
                    # Remove all other runs
                    for extra_r in runs[1:]:
                        para.remove(extra_r)

    tree.write(slide_xml_path, xml_declaration=True, encoding='UTF-8', standalone=True)


def _get_slide_count(prs_xml_path):
    """Return list of existing slide rId entries from presentation.xml."""
    tree = etree.parse(prs_xml_path)
    root = tree.getroot()
    ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    sldIdLst = root.find(f'{{{ns_p}}}sldIdLst')
    if sldIdLst is None:
        return []
    return sldIdLst.findall(f'{{{ns_p}}}sldId')


def prepend_kq_slide(teaching_pptx, key_question, template_path=None):
    """
    Insert KQ slide as slide 1 of teaching_pptx (in-place).
    """
    if template_path is None:
        template_path = TEMPLATE_PATH

    tmp_kq   = '/tmp/_kq_unpack'
    tmp_deck = '/tmp/_deck_unpack'

    # Clean up
    for d in (tmp_kq, tmp_deck):
        if os.path.exists(d):
            shutil.rmtree(d)

    _unpack(template_path, tmp_kq)
    _unpack(teaching_pptx,  tmp_deck)

    # --- Edit the KQ slide XML ---
    kq_slide_xml = os.path.join(tmp_kq, 'ppt', 'slides', 'slide1.xml')
    _replace_text_in_slide_xml(kq_slide_xml, PLACEHOLDER_TEXT, key_question)

    # --- Copy KQ slide into deck ---
    deck_slides_dir = os.path.join(tmp_deck, 'ppt', 'slides')
    deck_rels_dir   = os.path.join(tmp_deck, 'ppt', 'slides', '_rels')
    os.makedirs(deck_rels_dir, exist_ok=True)

    # How many slides does the deck already have?
    existing = sorted(
        f for f in os.listdir(deck_slides_dir)
        if re.match(r'^slide\d+\.xml$', f)
    )
    n_existing = len(existing)

    # Rename existing slides upward to make room for slide1
    for i in range(n_existing, 0, -1):
        old_xml  = os.path.join(deck_slides_dir, f'slide{i}.xml')
        new_xml  = os.path.join(deck_slides_dir, f'slide{i+1}.xml')
        old_rels = os.path.join(deck_rels_dir, f'slide{i}.xml.rels')
        new_rels = os.path.join(deck_rels_dir, f'slide{i+1}.xml.rels')
        if os.path.exists(old_xml):
            os.rename(old_xml, new_xml)
        if os.path.exists(old_rels):
            os.rename(old_rels, new_rels)

    # Copy KQ slide1.xml and its rels into the deck
    shutil.copy(
        os.path.join(tmp_kq, 'ppt', 'slides', 'slide1.xml'),
        os.path.join(deck_slides_dir, 'slide1.xml')
    )
    kq_rels_src = os.path.join(tmp_kq, 'ppt', 'slides', '_rels', 'slide1.xml.rels')
    if os.path.exists(kq_rels_src):
        shutil.copy(kq_rels_src, os.path.join(deck_rels_dir, 'slide1.xml.rels'))

    # --- Copy KQ media files into deck media ---
    kq_media_dir   = os.path.join(tmp_kq, 'ppt', 'media')
    deck_media_dir = os.path.join(tmp_deck, 'ppt', 'media')
    os.makedirs(deck_media_dir, exist_ok=True)

    if os.path.exists(kq_media_dir):
        # Find what media filenames the KQ slide actually references
        rels_tree = etree.parse(os.path.join(deck_rels_dir, 'slide1.xml.rels'))
        referenced = set()
        for el in rels_tree.getroot():
            target = el.get('Target', '')
            if '../media/' in target:
                referenced.add(os.path.basename(target))

        # Copy only referenced media, renaming to avoid collisions
        existing_media = set(os.listdir(deck_media_dir))
        remap = {}  # old_name -> new_name in deck

        for mfile in referenced:
            src = os.path.join(kq_media_dir, mfile)
            if not os.path.exists(src):
                continue
            # Find a non-colliding name
            dest_name = mfile
            if dest_name in existing_media:
                base, ext = os.path.splitext(mfile)
                idx = 1
                while f'kq_{base}_{idx}{ext}' in existing_media:
                    idx += 1
                dest_name = f'kq_{base}_{idx}{ext}'
            remap[mfile] = dest_name
            shutil.copy(src, os.path.join(deck_media_dir, dest_name))
            existing_media.add(dest_name)

        # Update slide1 rels to point to renamed media
        if remap:
            rels_path = os.path.join(deck_rels_dir, 'slide1.xml.rels')
            with open(rels_path, 'r', encoding='utf-8') as f:
                rels_content = f.read()
            for old, new in remap.items():
                rels_content = rels_content.replace(f'../media/{old}', f'../media/{new}')
            with open(rels_path, 'w', encoding='utf-8') as f:
                f.write(rels_content)

    # --- Update [Content_Types].xml to include new slide ---
    ct_path = os.path.join(tmp_deck, '[Content_Types].xml')
    ct_tree = etree.parse(ct_path)
    ct_root = ct_tree.getroot()
    ns_ct = 'http://schemas.openxmlformats.org/package/2006/content-types'
    slide_ct = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'

    # Check if slide content type already registered
    already = any(
        el.get('ContentType') == slide_ct
        for el in ct_root.findall(f'{{{ns_ct}}}Override')
    )
    if not already:
        new_el = etree.SubElement(ct_root, f'{{{ns_ct}}}Override')
        new_el.set('PartName', '/ppt/slides/slide1.xml')
        new_el.set('ContentType', slide_ct)

    # Ensure all renumbered slides are registered
    for i in range(1, n_existing + 2):
        part = f'/ppt/slides/slide{i}.xml'
        exists = any(
            el.get('PartName') == part
            for el in ct_root.findall(f'{{{ns_ct}}}Override')
        )
        if not exists:
            new_el = etree.SubElement(ct_root, f'{{{ns_ct}}}Override')
            new_el.set('PartName', part)
            new_el.set('ContentType', slide_ct)

    ct_tree.write(ct_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # --- Update presentation.xml slide list ---
    prs_xml = os.path.join(tmp_deck, 'ppt', 'presentation.xml')
    prs_rels_xml = os.path.join(tmp_deck, 'ppt', '_rels', 'presentation.xml.rels')

    # Add relationship for the new slide in presentation.xml.rels
    rels_tree = etree.parse(prs_rels_xml)
    rels_root = rels_tree.getroot()
    ns_rel = 'http://schemas.openxmlformats.org/package/2006/relationships'
    slide_rel_type = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'

    # Find existing slide rIds and shift them if needed; add new rId for slide1
    existing_rids = {el.get('Id') for el in rels_root}
    # Find a free rId
    rid_nums = set()
    for rid in existing_rids:
        m = re.match(r'rId(\d+)', rid)
        if m:
            rid_nums.add(int(m.group(1)))
    new_rid_num = max(rid_nums) + 1 if rid_nums else 1
    new_rid = f'rId{new_rid_num}'

    new_rel = etree.SubElement(rels_root, f'{{{ns_rel}}}Relationship')
    new_rel.set('Id', new_rid)
    new_rel.set('Type', slide_rel_type)
    new_rel.set('Target', 'slides/slide1.xml')
    rels_tree.write(prs_rels_xml, xml_declaration=True, encoding='UTF-8', standalone=True)

    # Update sldIdLst in presentation.xml — prepend the new slide
    prs_tree = etree.parse(prs_xml)
    prs_root = prs_tree.getroot()
    ns_p = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    ns_r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    sldIdLst = prs_root.find(f'{{{ns_p}}}sldIdLst')
    if sldIdLst is None:
        sldIdLst = etree.SubElement(prs_root, f'{{{ns_p}}}sldIdLst')

    existing_ids = [int(el.get('id', 256)) for el in sldIdLst]
    new_slide_id = max(existing_ids) + 1 if existing_ids else 256

    new_sld = etree.Element(f'{{{ns_p}}}sldId')
    new_sld.set('id', str(new_slide_id))
    new_sld.set(f'{{{ns_r}}}id', new_rid)
    sldIdLst.insert(0, new_sld)

    prs_tree.write(prs_xml, xml_declaration=True, encoding='UTF-8', standalone=True)

    # --- Repack ---
    _repack(tmp_deck, teaching_pptx)

    # Cleanup
    shutil.rmtree(tmp_kq)
    shutil.rmtree(tmp_deck)

    print(f'KQ slide prepended: "{key_question[:60]}..."' if len(key_question) > 60 else f'KQ slide prepended: "{key_question}"')


def generate_key_question(lesson):
    """
    Derive a key question from a lesson plan dict.
    Uses: topic, li, loText.walt, cycle1.focus, cycle2.focus
    Returns a single question string suitable for the KQ slide.
    """
    topic       = lesson.get('topic', '')
    li          = lesson.get('li', '')
    walt        = lesson.get('loText', {}).get('walt', '')
    c1_focus    = lesson.get('cycle1', {}).get('focus', '')
    c2_focus    = lesson.get('cycle2', {}).get('focus', '')

    # Build a prompt for Claude to generate the question
    # (called inline from build_lesson_v3.py via the Anthropic API)
    import anthropic
    client = anthropic.Anthropic()

    prompt = f"""You are generating a single Key Question for a Year 4 maths lesson slide.

The Key Question is a big-idea conceptual question that frames what the lesson is really about.
It should be a genuine question a child could think about — not a restatement of the objective.
It should be open, thought-provoking, and answerable through the lesson.
It must be one sentence, end with a question mark, and use child-friendly language.

Lesson details:
- Topic: {topic}
- Learning intention: {li}
- WALT: {walt}
- Cycle 1 focus: {c1_focus}
- Cycle 2 focus: {c2_focus}

Reply with ONLY the question. No preamble, no explanation."""

    message = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=100,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return message.content[0].text.strip()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 build_kq_slide.py <teaching_pptx> <key_question_text>')
        sys.exit(1)
    teaching_pptx = sys.argv[1]
    key_question  = sys.argv[2]
    prepend_kq_slide(teaching_pptx, key_question)
