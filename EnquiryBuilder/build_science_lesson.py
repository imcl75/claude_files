import subprocess
"""
build_science_lesson.py  —  v3
Clone-and-replace approach:
  1. Unpack sci_example.pptx (has all named layouts + master)
  2. Delete every existing slide file from the unpacked dir
  3. For each lesson slide, copy in the right source slide (with its media)
  4. Edit text by shape-name, not by text-content search
  5. Repack
"""

import sys, json, os, re, shutil, zipfile, glob, copy
from pathlib import Path
from lxml import etree

DIR          = Path(__file__).parent
SCI_EXAMPLE  = DIR / 'sci_example.pptx'
SCI_TEMPLATE = DIR / 'sci_template.pptx'
KQ_LO        = DIR / 'kq_lo_science_clean.pptx'

# Map slide type → (source pptx, 1-indexed slide number)
SOURCES = {
    'cover':           (SCI_TEMPLATE, 2),
    'lo':              (KQ_LO,        1),
    'recall':          (SCI_TEMPLATE, 9),
    'ido':             (SCI_EXAMPLE, 13),
    'wedo':            (SCI_EXAMPLE, 15),
    'youdo':           (SCI_EXAMPLE, 12),
    'misconception3':  (SCI_EXAMPLE, 16),
    'misconception4':  (SCI_TEMPLATE, 12),
    'fed_in_facts':    (SCI_TEMPLATE, 13),
    'quiz':            (SCI_TEMPLATE, 14),
    'learning_review': (SCI_EXAMPLE, 17),
}

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

# ─── zip helpers ──────────────────────────────────────────────────────────────

def unzip(src, dst):
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    with zipfile.ZipFile(src) as z:
        z.extractall(dst)

def rezip(src_dir, dst_path):
    if os.path.exists(dst_path):
        os.remove(dst_path)
    with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, src_dir))

# ─── XML helpers ──────────────────────────────────────────────────────────────

def parse(path):
    return etree.parse(path)

def write(tree, path):
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)

def find_shape(slide_tree, name):
    """Find a <p:sp> by its cNvPr name attribute."""
    for sp in slide_tree.iter(f'{{{NS_P}}}sp'):
        for el in sp.iter():
            if el.get('name') == name:
                return sp
    return None

def all_text_of(sp):
    return ''.join(t.text or '' for t in sp.iter(f'{{{NS_A}}}t'))

def set_text(sp, new_text):
    """Replace all text in a shape with new_text, keeping the FIRST run's formatting."""
    txBody = sp.find(f'{{{NS_P}}}txBody')
    if txBody is None:
        txBody = sp.find(f'{{{NS_A}}}txBody')
    if txBody is None:
        return

    A = NS_A
    paras = txBody.findall(f'{{{A}}}p')
    if not paras:
        return

    # Preserve first run's rPr; clear all subsequent paragraphs
    first_p = paras[0]
    runs = first_p.findall(f'{{{A}}}r')

    # Find first rPr for formatting template
    rPr_template = None
    if runs:
        rPr_template = runs[0].find(f'{{{A}}}rPr')

    # Remove all runs from first_p
    for r in list(first_p.findall(f'{{{A}}}r')):
        first_p.remove(r)

    # Remove extra paragraphs
    for p in paras[1:]:
        txBody.remove(p)

    # Split new_text on newlines → one paragraph each
    lines = new_text.split('\n') if '\n' in new_text else [new_text]

    # Save a CLEAN copy of first_p BEFORE adding any content (fixes deepcopy bug)
    para_template = copy.deepcopy(first_p)

    for i, line in enumerate(lines):
        if i == 0:
            p = first_p
        else:
            p = copy.deepcopy(para_template)  # always clone the CLEAN template
            txBody.append(p)

        r = etree.SubElement(p, f'{{{A}}}r')
        if rPr_template is not None:
            r.insert(0, copy.deepcopy(rPr_template))
        t = etree.SubElement(r, f'{{{A}}}t')
        t.text = line

def clear_text(sp):
    """Remove all text content from a shape (make it blank)."""
    txBody = sp.find(f'{{{NS_P}}}txBody')
    if txBody is None:
        txBody = sp.find(f'{{{NS_A}}}txBody')
    if txBody is None:
        return
    A = NS_A
    for p in list(txBody.findall(f'{{{A}}}p')):
        txBody.remove(p)
    # Add one empty paragraph to keep the txBody valid
    etree.SubElement(txBody, f'{{{A}}}p')

def set_placeholder(slide_tree, ph_type, new_text):
    """Set text of a placeholder by type (title / body)."""
    for sp in slide_tree.iter(f'{{{NS_P}}}sp'):
        ph = sp.find(f'.//{{{NS_P}}}ph')
        if ph is None:
            continue
        t = ph.get('type', '')
        idx = ph.get('idx', '')
        if ph_type == 'title' and (t == 'title' or t == 'ctrTitle' or idx == '0'):
            set_text(sp, new_text)
            return True
        if ph_type == 'body' and (t == 'body' or idx == '1' or (t == '' and idx not in ('', '0'))):
            set_text(sp, new_text)
            return True
    return False

# ─── slide clearing ────────────────────────────────────────────────────────────

def clear_all_slides(work_dir):
    """Delete every slide XML + rels from work_dir and de-register them."""
    # Delete physical files
    for f in glob.glob(f'{work_dir}/ppt/slides/slide*.xml'):
        os.remove(f)
    for f in glob.glob(f'{work_dir}/ppt/slides/_rels/slide*.xml.rels'):
        os.remove(f)

    # Clear sldIdLst in presentation.xml
    pres_path = f'{work_dir}/ppt/presentation.xml'
    t = parse(pres_path)
    r = t.getroot()
    lst = r.find(f'{{{NS_P}}}sldIdLst')
    if lst is not None:
        for c in list(lst): lst.remove(c)
    write(t, pres_path)

    # Remove slide rels from presentation.xml.rels
    pres_rels = f'{work_dir}/ppt/_rels/presentation.xml.rels'
    t = parse(pres_rels)
    r = t.getroot()
    SLIDE_TYPE = f'{NS_R}/slide'
    for rel in list(r):
        if 'slide' in rel.get('Type', '') and 'Layout' not in rel.get('Type','') and 'Master' not in rel.get('Type',''):
            r.remove(rel)
    write(t, pres_rels)

    # Remove slide entries from [Content_Types].xml
    ct_path = f'{work_dir}/[Content_Types].xml'
    t = parse(ct_path)
    r = t.getroot()
    SLIDE_CT = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
    for el in list(r):
        if el.get('ContentType') == SLIDE_CT:
            r.remove(el)
    write(t, ct_path)

# ─── slide cloning ─────────────────────────────────────────────────────────────

# Cache unpacked source PPTXs
_src_cache = {}

def get_src(pptx_path):
    key = str(pptx_path)
    if key not in _src_cache:
        dst = f'/tmp/srcunpack_{Path(pptx_path).stem}'
        unzip(pptx_path, dst)
        _src_cache[key] = dst
    return _src_cache[key]

def next_media_num(work_dir):
    existing = set()
    media_dir = f'{work_dir}/ppt/media'
    if os.path.exists(media_dir):
        for f in os.listdir(media_dir):
            m = re.match(r'(?:image|hdphoto)(\d+)', f.split('.')[0])
            if m: existing.add(int(m.group(1)))
    n = 1
    while n in existing: n += 1
    return n

def next_slide_num(work_dir):
    existing = set()
    for f in os.listdir(f'{work_dir}/ppt/slides'):
        m = re.match(r'slide(\d+)\.xml$', f)
        if m: existing.add(int(m.group(1)))
    n = 1
    while n in existing: n += 1
    return n

def clone_slide(work_dir, src_pptx, slide_num):
    """Clone slide_num from src_pptx into work_dir. Returns new slide path."""
    src_dir = get_src(src_pptx)
    media_dir = f'{work_dir}/ppt/media'
    os.makedirs(media_dir, exist_ok=True)

    # Read source slide and rels
    src_slide = f'{src_dir}/ppt/slides/slide{slide_num}.xml'
    src_rels  = f'{src_dir}/ppt/slides/_rels/slide{slide_num}.xml.rels'

    with open(src_slide, encoding='utf-8') as f:
        slide_xml = f.read()
    if os.path.exists(src_rels):
        with open(src_rels, encoding='utf-8') as f:
            rels_xml = f.read()
    else:
        rels_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'

    # Copy media files, remapping names to avoid collisions
    media_remap = {}  # src_name → dst_name
    if os.path.exists(src_rels):
        rels_tree = etree.parse(src_rels)
        for rel in rels_tree.getroot():
            tgt = rel.get('Target', '')
            if '../media/' in tgt:
                src_name = tgt.split('../media/')[1]
                src_path = f'{src_dir}/ppt/media/{src_name}'
                if not os.path.exists(src_path):
                    continue
                with open(src_path, 'rb') as f:
                    content = f.read()
                # Check if identical file already in work_dir
                existing_match = None
                if os.path.exists(media_dir):
                    for ef in os.listdir(media_dir):
                        with open(f'{media_dir}/{ef}', 'rb') as f:
                            if f.read() == content:
                                existing_match = ef
                                break
                if existing_match:
                    media_remap[src_name] = existing_match
                else:
                    n = next_media_num(work_dir)
                    ext = Path(src_name).suffix
                    prefix = 'hdphoto' if 'hdphoto' in src_name else 'image'
                    new_name = f'{prefix}{n}{ext}'
                    with open(f'{media_dir}/{new_name}', 'wb') as f:
                        f.write(content)
                    media_remap[src_name] = new_name

    # Remap media references in slide XML and rels
    for old, new in media_remap.items():
        slide_xml = slide_xml.replace(f'../media/{old}', f'../media/{new}')
        rels_xml  = rels_xml.replace(f'../media/{old}', f'../media/{new}')

    # Ensure the layout referenced in rels exists in work_dir
    if os.path.exists(src_rels):
        rels_tree = etree.parse(src_rels)
        for rel in rels_tree.getroot():
            if 'slideLayout' in rel.get('Type', ''):
                layout_fname = rel.get('Target', '').split('/')[-1]
                src_layout = f'{src_dir}/ppt/slideLayouts/{layout_fname}'
                dst_layout = f'{work_dir}/ppt/slideLayouts/{layout_fname}'
                if not os.path.exists(dst_layout) and os.path.exists(src_layout):
                    shutil.copy(src_layout, dst_layout)
                    src_lr = f'{src_dir}/ppt/slideLayouts/_rels/{layout_fname}.rels'
                    if os.path.exists(src_lr):
                        os.makedirs(f'{work_dir}/ppt/slideLayouts/_rels', exist_ok=True)
                        shutil.copy(src_lr, f'{work_dir}/ppt/slideLayouts/_rels/{layout_fname}.rels')

    # Write slide and rels to work_dir
    new_num = next_slide_num(work_dir)
    new_slide_path = f'{work_dir}/ppt/slides/slide{new_num}.xml'
    new_rels_path  = f'{work_dir}/ppt/slides/_rels/slide{new_num}.xml.rels'

    with open(new_slide_path, 'w', encoding='utf-8') as f:
        f.write(slide_xml)
    os.makedirs(f'{work_dir}/ppt/slides/_rels', exist_ok=True)
    with open(new_rels_path, 'w', encoding='utf-8') as f:
        f.write(rels_xml)

    # Register in presentation.xml.rels → get new rId
    pres_rels_path = f'{work_dir}/ppt/_rels/presentation.xml.rels'
    prt = parse(pres_rels_path)
    prr = prt.getroot()
    existing_rids = {int(m.group(1)) for el in prr
                     for m in [re.match(r'rId(\d+)', el.get('Id',''))] if m}
    rid_n = 1
    while rid_n in existing_rids: rid_n += 1
    new_rid = f'rId{rid_n}'
    PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
    etree.SubElement(prr, 'Relationship', {
        'Id': new_rid,
        'Type': f'{NS_R}/slide',
        'Target': f'slides/slide{new_num}.xml'
    })
    write(prt, pres_rels_path)

    # Register in sldIdLst
    pres_path = f'{work_dir}/ppt/presentation.xml'
    pt = parse(pres_path)
    pr = pt.getroot()
    lst = pr.find(f'{{{NS_P}}}sldIdLst')
    if lst is None:
        lst = etree.SubElement(pr, f'{{{NS_P}}}sldIdLst')
    existing_ids = {int(el.get('id', 256)) for el in lst}
    new_id = max(existing_ids, default=255) + 1
    etree.SubElement(lst, f'{{{NS_P}}}sldId', {
        'id': str(new_id),
        f'{{{NS_R}}}id': new_rid,
    })
    write(pt, pres_path)

    # Register in [Content_Types].xml
    ct_path = f'{work_dir}/[Content_Types].xml'
    ct = parse(ct_path)
    ctr = ct.getroot()
    CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
    SLIDE_CT = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
    pname = f'/ppt/slides/slide{new_num}.xml'
    if not any(el.get('PartName') == pname for el in ctr):
        etree.SubElement(ctr, f'{{{CT_NS}}}Override', {
            'PartName': pname,
            'ContentType': SLIDE_CT
        })
    write(ct, ct_path)

    print(f"  + slide{new_num}.xml ← {Path(src_pptx).stem}:slide{slide_num}")
    return new_slide_path

# ─── per-slide text editors ───────────────────────────────────────────────────

def edit_cover(path, lesson):
    t = parse(path)

    # Key question: shape named "TextBox 16" inside Group 14
    # It's a child of a group — iterate all sp elements
    kq = None
    challenge = None
    day_box = None
    for sp in t.iter(f'{{{NS_P}}}sp'):
        name = ''
        for el in sp.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        if name == 'TextBox 16':
            kq = sp
        elif name == 'TextBox 17':
            challenge = sp
        elif name == 'TextBox 19':
            day_box = sp

    if kq is not None:
        set_text(kq, lesson['key_question'])
    challenge_text = lesson.get('challenge') or ''
    if challenge is not None:
        if challenge_text:
            set_text(challenge, 'Our Challenge is:\n' + challenge_text)
        else:
            clear_text(challenge)
    if day_box is not None:
        set_text(day_box, lesson['day'] + ' ' + lesson.get('session', ''))

    write(t, path)

def edit_lo(path, lesson):
    t = parse(path)

    # Clean kq_lo_science_clean.pptx has these editable shapes:
    # 'Title 27'      → set to key_question
    # 'TextBox 38'    → set to lo (I am learning to...)
    # 'TextBox 39'    → set to tib (This is so...)
    # 'TextBox 40'    → set to isb (I will be successful by...)
    # Everything else (clouds, panels, frame, pupil images) stays as-is

    for sp in t.iter(f'{{{NS_P}}}sp'):
        name = ''
        for el in sp.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        if name == 'Title 27':
            set_text(sp, lesson['key_question'])
        elif name == 'TextBox 38':
            set_text(sp, lesson.get('lo', ''))
        elif name == 'TextBox 39':
            set_text(sp, lesson.get('tib', ''))
        elif name == 'TextBox 40':
            set_text(sp, lesson.get('isb', ''))

    write(t, path)

def edit_recall(path, slide_def):
    t = parse(path)

    left_text  = '\n'.join(slide_def.get('left', []))
    right_text = '\n'.join(slide_def.get('right', []))
    wonder     = slide_def.get('wonder', '')

    ph12_count = 0
    for sp in t.iter(f'{{{NS_P}}}sp'):
        name = ''
        for el in sp.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        # Shape names from sci_template slide 9:
        # 'Text Placeholder 5'  — right column (I remember)
        # 'Text Placeholder 12' — appears twice: first = left col, second = wonder row
        # 'Rectangle: Rounded Corners 8' — header
        if name == 'Text Placeholder 5':
            set_text(sp, right_text)
        elif name == 'Text Placeholder 12':
            ph12_count += 1
            if ph12_count == 1:
                set_text(sp, left_text)
            else:
                set_text(sp, 'I Wonder… ' + wonder)

    write(t, path)

def edit_teaching(path, slide_def):
    t = parse(path)
    title   = slide_def.get('title', '')
    bullets = slide_def.get('bullets', slide_def.get('content', []))
    bullet_text = '\n'.join(str(b) for b in bullets)

    set_placeholder(t, 'title', title)
    set_placeholder(t, 'body', bullet_text)

    write(t, path)

def edit_misconception(path, slide_def):
    t = parse(path)
    title    = slide_def.get('title', 'Who do you agree with and why?')
    learners = slide_def.get('learners', [])

    # Shape names from sci_example slide 16:
    # 'Rectangle: Rounded Corners 2' → header
    # 'Speech Bubble: Rectangle with Corners Rounded 19' → Learner A (top-left)
    # 'Speech Bubble: Rectangle with Corners Rounded 21' → Learner B (top-right)
    # 'Speech Bubble: Rectangle with Corners Rounded 20' → Learner C (bottom-left)
    # 'TextBox 23' → 'Learner A'
    # 'TextBox 24' → 'Learner B'
    # 'TextBox 25' → 'Learner C'

    bubble_map = {
        'Speech Bubble: Rectangle with Corners Rounded 19': 0,
        'Speech Bubble: Rectangle with Corners Rounded 21': 1,
        'Speech Bubble: Rectangle with Corners Rounded 20': 2,
    }
    name_map = {
        'TextBox 23': 0,
        'TextBox 24': 1,
        'TextBox 25': 2,
    }

    for sp in t.iter(f'{{{NS_P}}}sp'):
        name = ''
        for el in sp.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        if name == 'Rectangle: Rounded Corners 2':
            set_text(sp, title)
        elif name in bubble_map:
            idx = bubble_map[name]
            if idx < len(learners):
                txt = learners[idx].get('view', learners[idx].get('statement', ''))
                set_text(sp, txt)
        elif name in name_map:
            idx = name_map[name]
            if idx < len(learners):
                set_text(sp, learners[idx].get('name', f'Learner {chr(65+idx)}'))
        elif name == 'Rectangle 1':
            # Central image placeholder — replace with image prompt note
            prompt = slide_def.get('image_prompt', '')
            set_text(sp, f'[{prompt[:80]}]' if prompt else '')

    write(t, path)

def edit_learning_review(path, slide_def):
    t = parse(path)
    starters = slide_def.get('starters', ['', '', ''])

    # Shape names from sci_example slide 17:
    # 'Bubble1', 'Bubble2', 'Bubble3'
    bubble_map = {'Bubble1': 0, 'Bubble2': 1, 'Bubble3': 2}

    for sp in t.iter(f'{{{NS_P}}}sp'):
        name = ''
        for el in sp.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        if name in bubble_map:
            idx = bubble_map[name]
            if idx < len(starters):
                set_text(sp, starters[idx])

    write(t, path)

# ─── main build ───────────────────────────────────────────────────────────────


# ─── image layout integration ─────────────────────────────────────────────────

def build_with_layout(work_dir, slide_def, lesson, image_dir):
    """Route flexible layout slides to slide_layouts.py."""
    import sys
    sys.path.insert(0, str(DIR))
    import slide_layouts as sl
    return sl.build_flexible_slide(work_dir, slide_def, lesson, image_dir)


def build(lesson_path, output_path, image_dir="/tmp/enquiry_images"):
    with open(lesson_path) as f:
        lesson = json.load(f)

    print(f"\nBuilding: {lesson.get('key_question','')}")

    work = '/tmp/lesson_work'
    unzip(SCI_EXAMPLE, work)
    clear_all_slides(work)
    # Remove orphaned media from sci_example (clean.py walks rels references)
    subprocess.run(['python3', str(DIR / 'clean.py'), work], capture_output=True)

    for slide_def in lesson.get('slides', []):
        stype  = slide_def.get('type')
        mode   = slide_def.get('mode', '')
        layout = slide_def.get('layout', 'text_only')

        # Route flexible image layouts through slide_layouts.py
        if stype in ('teaching', 'discussion', 'activity') and layout != 'text_only':
            new_path = build_with_layout(work, slide_def, lesson, image_dir)
            if new_path:
                continue  # slide built by layout system

        if stype == 'cover':
            src_p, src_n = SOURCES['cover']
        elif stype == 'lo':
            src_p, src_n = SOURCES['lo']
        elif stype == 'recall':
            src_p, src_n = SOURCES['recall']
        elif stype in ('teaching',):
            if mode == 'wedo':   src_p, src_n = SOURCES['wedo']
            elif mode == 'youdo': src_p, src_n = SOURCES['youdo']
            else:                 src_p, src_n = SOURCES['ido']
        elif stype == 'discussion':
            src_p, src_n = SOURCES['wedo']
        elif stype == 'activity':
            if mode == 'youdo_trio': src_p, src_n = SOURCES['youdo']
            else:                     src_p, src_n = SOURCES['youdo']
        elif stype == 'misconception':
            n = len(slide_def.get('learners', []))
            src_p, src_n = SOURCES['misconception4'] if n >= 4 else SOURCES['misconception3']
        elif stype == 'fed_in_facts':
            src_p, src_n = SOURCES['fed_in_facts']
        elif stype == 'quiz':
            src_p, src_n = SOURCES['quiz']
        elif stype == 'learning_review':
            src_p, src_n = SOURCES['learning_review']
        else:
            print(f"  [skip] unknown type: {stype}")
            continue

        new_path = clone_slide(work, str(src_p), src_n)

        if stype == 'cover':
            edit_cover(new_path, lesson)
        elif stype == 'lo':
            edit_lo(new_path, lesson)
        elif stype == 'recall':
            edit_recall(new_path, slide_def)
        elif stype in ('teaching', 'discussion', 'activity'):
            edit_teaching(new_path, slide_def)
        elif stype == 'misconception':
            edit_misconception(new_path, slide_def)
        elif stype == 'fed_in_facts':
            pass  # header kept, blank body
        elif stype == 'quiz':
            edit_teaching(new_path, slide_def)  # same structure
        elif stype == 'learning_review':
            edit_learning_review(new_path, slide_def)

    rezip(work, output_path)
    size = os.path.getsize(output_path)
    print(f"  → {output_path}  ({size:,} bytes)")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 build_science_lesson.py lesson.json output.pptx [image_dir]")
        sys.exit(1)
    img_dir = sys.argv[3] if len(sys.argv) > 3 else "/tmp/enquiry_images"
    build(sys.argv[1], sys.argv[2], img_dir)
