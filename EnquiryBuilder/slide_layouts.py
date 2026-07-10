"""
slide_layouts.py
Builds PPTX slides with flexible image layouts.
All positions in EMU. Slide = 12192000 x 6858000.
"""

import os, re, copy, shutil
from lxml import etree
from pathlib import Path

NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'

SLIDE_W = 12192000
SLIDE_H = 6858000
MARGIN  = 152400      # 0.4cm
TITLE_H = 533400      # 1.4cm — title area height
GAP     = 114300      # 0.3cm — gap between images

BADGE_POS = (10467618, 46838, 1720862, 697890)  # x,y,w,h from sci_example

ASSETS = Path(__file__).parent / 'assets'

BADGE_FILES = {
    'ido':        str(ASSETS / 'badge_ido.png'),
    'wedo':       str(ASSETS / 'badge_wedo.png'),
    'youdo':      str(ASSETS / 'badge_youdo_ind.png'),
    'youdo_trio': str(ASSETS / 'badge_youdo_trio.png'),
}

# ─── Frame XML (the green border shape from sci_example) ─────────────────────

FRAME_XML = (
    '<p:sp xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
    '<p:nvSpPr><p:cNvPr id="1" name="Frame 1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
    '<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm>'
    '<a:prstGeom prst="frame"><a:avLst><a:gd name="adj1" fmla="val 1241"/></a:avLst></a:prstGeom>'
    '<a:solidFill><a:schemeClr val="accent6"><a:lumMod val="50000"/></a:schemeClr></a:solidFill>'
    '<a:ln><a:solidFill><a:schemeClr val="accent6"><a:lumMod val="50000"/></a:schemeClr>'
    '</a:solidFill></a:ln></p:spPr>'
    '<p:style><a:lnRef idx="2"><a:schemeClr val="accent1"><a:shade val="15000"/></a:schemeClr></a:lnRef>'
    '<a:fillRef idx="1"><a:schemeClr val="accent1"/></a:fillRef>'
    '<a:effectRef idx="0"><a:schemeClr val="accent1"/></a:effectRef>'
    '<a:fontRef idx="minor"><a:schemeClr val="lt1"/></a:fontRef></p:style>'
    '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/>'
    '<a:p><a:pPr algn="ctr"/></a:p></p:txBody></p:sp>'
).format(P=NS_P, A=NS_A, R=NS_R)

# ─── helpers ─────────────────────────────────────────────────────────────────

def _next_id(tree):
    ids = set()
    for el in tree.iter():
        v = el.get('id')
        if v and v.isdigit():
            ids.add(int(v))
    return max(ids, default=0) + 1

def _next_rid(rels_path):
    tree = etree.parse(rels_path)
    rids = set()
    for el in tree.getroot():
        m = re.match(r'rId(\d+)', el.get('Id', ''))
        if m: rids.add(int(m.group(1)))
    n = 1
    while n in rids: n += 1
    return f'rId{n}', tree

def _next_media_num(media_dir):
    existing = set()
    if os.path.exists(media_dir):
        for f in os.listdir(media_dir):
            m = re.match(r'image(\d+)', f.split('.')[0])
            if m: existing.add(int(m.group(1)))
    n = 1
    while n in existing: n += 1
    return n

def _embed_image(work_dir, slide_path, img_path):
    """Copy image to ppt/media, add rel, return rId."""
    media_dir = f'{work_dir}/ppt/media'
    os.makedirs(media_dir, exist_ok=True)

    # Check if identical image already embedded
    with open(img_path, 'rb') as f:
        content = f.read()
    for existing in os.listdir(media_dir):
        with open(f'{media_dir}/{existing}', 'rb') as f:
            if f.read() == content:
                existing_name = existing
                break
    else:
        ext = Path(img_path).suffix
        n = _next_media_num(media_dir)
        existing_name = f'image{n}{ext}'
        with open(f'{media_dir}/{existing_name}', 'wb') as f:
            f.write(content)

    rels_path = slide_path.replace('/slides/slide', '/slides/_rels/slide').replace('.xml', '.xml.rels')
    new_rid, rels_tree = _next_rid(rels_path)
    etree.SubElement(rels_tree.getroot(), 'Relationship', {
        'Id': new_rid,
        'Type': f'{NS_R}/image',
        'Target': f'../media/{existing_name}'
    })
    rels_tree.write(rels_path, xml_declaration=True, encoding='UTF-8', standalone=True)
    return new_rid

def _pic_xml(shape_id, rId, x, y, w, h):
    return (
        f'<p:pic xmlns:p="{NS_P}" xmlns:a="{NS_A}" xmlns:r="{NS_R}">'
        f'<p:nvPicPr>'
        f'<p:cNvPr id="{shape_id}" name="Img{shape_id}"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
        f'<p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{rId}"/>'
        f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        f'</p:pic>'
    )

def _textbox_xml(shape_id, text, x, y, w, h,
                 font_size=1400, bold='0', align='ctr',
                 colour='000000', bg_colour=None, bg_alpha=None,
                 italic='0', font_face='Calibri'):
    fill = ''
    if bg_colour:
        alpha_str = f'<a:alpha val="{bg_alpha}"/>' if bg_alpha else ''
        fill = (f'<a:solidFill><a:srgbClr val="{bg_colour}">'
                f'{alpha_str}</a:srgbClr></a:solidFill>')
    else:
        fill = '<a:noFill/>'

    bold_str = '1' if bold in (True, '1', 1) else '0'
    italic_str = '1' if italic in (True, '1', 1) else '0'

    return (
        f'<p:sp xmlns:p="{NS_P}" xmlns:a="{NS_A}">'
        f'<p:nvSpPr><p:cNvPr id="{shape_id}" name="Txt{shape_id}"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill}</p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" anchor="ctr"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="{align}"/><a:r>'
        f'<a:rPr lang="en-GB" b="{bold_str}" i="{italic_str}" sz="{font_size}" dirty="0">'
        f'<a:solidFill><a:srgbClr val="{colour}"/></a:solidFill>'
        f'<a:latin typeface="{font_face}"/></a:rPr>'
        f'<a:t>{_esc(text)}</a:t></a:r></a:p></p:txBody></p:sp>'
    )

def _esc(text):
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def _add_shape(tree, xml_str):
    spTree = tree.getroot().find(f'.//{{{NS_P}}}spTree')
    el = etree.fromstring(xml_str)
    spTree.append(el)
    return el

def _write(tree, path):
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)


# ─── blank slide builder ──────────────────────────────────────────────────────

BLANK_SLIDE_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">'
    '<p:cSld><p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '{shapes}</p:spTree></p:cSld>'
    '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
).format(P=NS_P, A=NS_A, R=NS_R, shapes='{shapes}')

BLANK_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="{PKG}">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" '
    'Target="../slideLayouts/slideLayout15.xml"/>'
    '</Relationships>'
).format(PKG=NS_PKG)

def create_blank_slide(work_dir):
    """
    Create a new blank slide (accent6 background + frame border).
    Returns the slide path.
    """
    from build_science_lesson import (
        next_slide_num, NS_P as BP, NS_R as BR
    )

    new_num = next_slide_num(work_dir)
    slide_path = f'{work_dir}/ppt/slides/slide{new_num}.xml'
    rels_path  = f'{work_dir}/ppt/slides/_rels/slide{new_num}.xml.rels'

    # Write slide XML with just the Frame shape
    slide_xml = BLANK_SLIDE_XML.format(shapes=FRAME_XML)
    with open(slide_path, 'w', encoding='utf-8') as f:
        f.write(slide_xml)

    os.makedirs(f'{work_dir}/ppt/slides/_rels', exist_ok=True)
    with open(rels_path, 'w', encoding='utf-8') as f:
        f.write(BLANK_RELS)

    # Register in presentation
    _register_slide(work_dir, new_num, slide_path, rels_path)
    return slide_path

def _register_slide(work_dir, slide_num, slide_path, rels_path):
    """Register slide in presentation.xml, .rels, and Content_Types."""
    import re

    # presentation.xml.rels → new rId
    pres_rels = f'{work_dir}/ppt/_rels/presentation.xml.rels'
    rt, rels_t = _next_rid(pres_rels)
    etree.SubElement(rels_t.getroot(), 'Relationship', {
        'Id': rt,
        'Type': f'{NS_R}/slide',
        'Target': f'slides/slide{slide_num}.xml'
    })
    rels_t.write(pres_rels, xml_declaration=True, encoding='UTF-8', standalone=True)

    # presentation.xml sldIdLst
    pres_path = f'{work_dir}/ppt/presentation.xml'
    pt = etree.parse(pres_path)
    pr = pt.getroot()
    lst = pr.find(f'{{{NS_P}}}sldIdLst')
    if lst is None:
        lst = etree.SubElement(pr, f'{{{NS_P}}}sldIdLst')
    existing_ids = {int(el.get('id', 256)) for el in lst}
    new_id = max(existing_ids, default=255) + 1
    etree.SubElement(lst, f'{{{NS_P}}}sldId', {
        'id': str(new_id),
        f'{{{NS_R}}}id': rt,
    })
    pt.write(pres_path, xml_declaration=True, encoding='UTF-8', standalone=True)

    # [Content_Types].xml
    ct_path = f'{work_dir}/[Content_Types].xml'
    ct = etree.parse(ct_path)
    ctr = ct.getroot()
    CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
    SLIDE_CT = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
    pname = f'/ppt/slides/slide{slide_num}.xml'
    if not any(el.get('PartName') == pname for el in ctr):
        etree.SubElement(ctr, f'{{{CT_NS}}}Override', {
            'PartName': pname,
            'ContentType': SLIDE_CT
        })
    ct.write(ct_path, xml_declaration=True, encoding='UTF-8', standalone=True)


# ─── badge adder ──────────────────────────────────────────────────────────────

def add_badge(work_dir, slide_path, mode):
    """Add I Do / We Do / You Do badge image top-right."""
    badge_file = BADGE_FILES.get(mode, BADGE_FILES['ido'])
    if not os.path.exists(badge_file):
        return
    rId = _embed_image(work_dir, slide_path, badge_file)
    tree = etree.parse(slide_path)
    sid = _next_id(tree)
    x, y, w, h = BADGE_POS
    _add_shape(tree, _pic_xml(sid, rId, x, y, w, h))
    _write(tree, slide_path)


# ─── title adder ──────────────────────────────────────────────────────────────

def add_title(slide_path, title, font_size=2400):
    """Add title text box at top of slide."""
    tree = etree.parse(slide_path)
    sid = _next_id(tree)
    # Full width minus badge area, top margin
    x = MARGIN
    y = MARGIN
    w = SLIDE_W - MARGIN - 1914400  # leave room for badge
    h = TITLE_H
    _add_shape(tree, _textbox_xml(
        sid, title, x, y, w, h,
        font_size=font_size, bold='1', align='l'
    ))
    _write(tree, slide_path)


# ─── layout: text_only ───────────────────────────────────────────────────────
# Handled by existing clone-and-replace in build_science_lesson.py


# ─── layout: image_grid ──────────────────────────────────────────────────────

def build_image_grid(work_dir, slide_path, slide_def, image_dir):
    """
    NxM grid of images with labels.
    slide_def['grid'] = {'rows': 2, 'cols': 3, 'items': [{'label':..,'prompt':..,'path':..}]}
    """
    grid  = slide_def.get('grid', {})
    rows  = grid.get('rows', 2)
    cols  = grid.get('cols', 3)
    items = grid.get('items', [])
    title = slide_def.get('title', '')
    mode  = slide_def.get('mode', 'wedo')

    add_badge(work_dir, slide_path, mode)
    add_title(slide_path, title)

    # Available area below title
    ax = MARGIN
    ay = MARGIN + TITLE_H + GAP
    aw = SLIDE_W - 2 * MARGIN
    ah = SLIDE_H - ay - MARGIN

    # Cell dimensions
    cell_w = (aw - (cols - 1) * GAP) // cols
    cell_h = (ah - (rows - 1) * GAP) // rows
    label_h = min(int(cell_h * 0.18), 228600)  # max 0.6cm
    img_h   = cell_h - label_h - GAP // 2

    tree = etree.parse(slide_path)

    for i, item in enumerate(items[:rows * cols]):
        row = i // cols
        col = i % cols
        ix = ax + col * (cell_w + GAP)
        iy = ay + row * (cell_h + GAP)

        img_path = item.get('path', '')
        if img_path and os.path.exists(img_path):
            rId = _embed_image(work_dir, slide_path, img_path)
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _pic_xml(sid, rId, ix, iy, cell_w, img_h))
            _write(tree, slide_path)
        else:
            # Placeholder box
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            placeholder = (
                f'<p:sp xmlns:p="{NS_P}" xmlns:a="{NS_A}">'
                f'<p:nvSpPr><p:cNvPr id="{sid}" name="ImgPlaceholder{sid}"/>'
                f'<p:cNvSpPr txBox="0"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{ix}" y="{iy}"/>'
                f'<a:ext cx="{cell_w}" cy="{img_h}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:schemeClr val="accent6">'
                f'<a:lumMod val="30000"/><a:lumOff val="70000"/></a:schemeClr></a:solidFill>'
                f'<a:ln><a:solidFill><a:schemeClr val="accent6">'
                f'<a:lumMod val="50000"/></a:schemeClr></a:solidFill></a:ln>'
                f'</p:spPr><p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/>'
                f'<a:p><a:pPr algn="ctr"/><a:r>'
                f'<a:rPr lang="en-GB" sz="1000" dirty="0"/>'
                f'<a:t>{_esc(item.get("prompt","")[:40])}</a:t>'
                f'</a:r></a:p></p:txBody></p:sp>'
            )
            _add_shape(tree, placeholder)
            _write(tree, slide_path)

        # Label
        label = item.get('label', '')
        if label:
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _textbox_xml(
                sid, label, ix, iy + img_h + GAP // 4,
                cell_w, label_h,
                font_size=1200, bold='1', align='ctr'
            ))
            _write(tree, slide_path)


# ─── layout: provocation ─────────────────────────────────────────────────────

def build_provocation(work_dir, slide_path, slide_def, image_dir):
    """
    Large dominant image filling the slide.
    Question/title overlaid at bottom in semi-transparent bar.
    """
    title  = slide_def.get('title', '')
    mode   = slide_def.get('mode', 'wedo')
    images = slide_def.get('images', [])

    add_badge(work_dir, slide_path, mode)

    img_item = images[0] if images else {}
    img_path = img_item.get('path', '')

    if img_path and os.path.exists(img_path):
        rId = _embed_image(work_dir, slide_path, img_path)
        tree = etree.parse(slide_path)
        sid = _next_id(tree)
        # Full slide image (slightly inset from border)
        inset = 114300  # 0.3cm
        _add_shape(tree, _pic_xml(sid, rId, inset, inset,
                                  SLIDE_W - 2*inset, SLIDE_H - 2*inset))
        _write(tree, slide_path)

    # Title bar overlay at bottom
    bar_h = 762000  # 2cm
    tree = etree.parse(slide_path)
    sid = _next_id(tree)
    _add_shape(tree, _textbox_xml(
        sid, title,
        0, SLIDE_H - bar_h, SLIDE_W, bar_h,
        font_size=2400, bold='1', align='ctr',
        colour='FFFFFF',
        bg_colour='000000', bg_alpha='70000'
    ))
    _write(tree, slide_path)


# ─── layout: comparison ──────────────────────────────────────────────────────

def build_comparison(work_dir, slide_path, slide_def, image_dir):
    """
    2 or 3 images side by side with labels. Title at top.
    """
    title  = slide_def.get('title', '')
    mode   = slide_def.get('mode', 'wedo')
    images = slide_def.get('images', [])
    n      = len(images)
    if n == 0:
        return

    add_badge(work_dir, slide_path, mode)
    add_title(slide_path, title)

    ax   = MARGIN
    ay   = MARGIN + TITLE_H + GAP
    aw   = SLIDE_W - 2 * MARGIN
    ah   = SLIDE_H - ay - MARGIN
    lbl_h = 266700   # 0.7cm label
    img_h = ah - lbl_h - GAP

    col_w = (aw - (n - 1) * GAP) // n

    for i, item in enumerate(images):
        ix = ax + i * (col_w + GAP)
        img_path = item.get('path', '')

        if img_path and os.path.exists(img_path):
            rId = _embed_image(work_dir, slide_path, img_path)
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _pic_xml(sid, rId, ix, ay, col_w, img_h))
            _write(tree, slide_path)

        label = item.get('label', '')
        if label:
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _textbox_xml(
                sid, label, ix, ay + img_h + GAP // 2, col_w, lbl_h,
                font_size=1600, bold='1', align='ctr'
            ))
            _write(tree, slide_path)


# ─── layout: image_right / image_left ────────────────────────────────────────

def build_image_text(work_dir, slide_path, slide_def, image_dir, img_side='right'):
    """
    Text on one side (55%), image on the other (45%).
    img_side: 'right' or 'left'
    """
    title   = slide_def.get('title', '')
    bullets = slide_def.get('bullets', slide_def.get('content', []))
    mode    = slide_def.get('mode', 'ido')
    images  = slide_def.get('images', [])

    add_badge(work_dir, slide_path, mode)
    add_title(slide_path, title)

    ay = MARGIN + TITLE_H + GAP
    ah = SLIDE_H - ay - MARGIN
    aw = SLIDE_W - 2 * MARGIN

    img_w  = int(aw * 0.45)
    txt_w  = aw - img_w - GAP

    if img_side == 'right':
        txt_x = MARGIN
        img_x = MARGIN + txt_w + GAP
    else:
        img_x = MARGIN
        txt_x = MARGIN + img_w + GAP

    # Text
    if bullets:
        tree = etree.parse(slide_path)
        sid = _next_id(tree)
        bullet_text = '\n'.join(f'\u2022  {b}' for b in bullets)
        _add_shape(tree, _textbox_xml(
            sid, bullet_text, txt_x, ay, txt_w, ah,
            font_size=1800, bold='0', align='l'
        ))
        _write(tree, slide_path)

    # Image
    if images:
        img_path = images[0].get('path', '')
        if img_path and os.path.exists(img_path):
            rId = _embed_image(work_dir, slide_path, img_path)
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _pic_xml(sid, rId, img_x, ay, img_w, ah))
            _write(tree, slide_path)


# ─── layout: diagram_annotated ───────────────────────────────────────────────

def build_diagram_annotated(work_dir, slide_path, slide_def, image_dir):
    """
    Central/right image with annotation text boxes around it.
    """
    title   = slide_def.get('title', '')
    mode    = slide_def.get('mode', 'ido')
    images  = slide_def.get('images', [])
    bullets = slide_def.get('bullets', [])

    add_badge(work_dir, slide_path, mode)
    add_title(slide_path, title)

    ay = MARGIN + TITLE_H + GAP
    ah = SLIDE_H - ay - MARGIN

    # Image takes right 55% of available width
    aw = SLIDE_W - 2 * MARGIN
    img_w = int(aw * 0.55)
    img_x = SLIDE_W - MARGIN - img_w
    ann_w = aw - img_w - GAP
    ann_x = MARGIN

    if images:
        img_path = images[0].get('path', '')
        if img_path and os.path.exists(img_path):
            rId = _embed_image(work_dir, slide_path, img_path)
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _pic_xml(sid, rId, img_x, ay, img_w, ah))
            _write(tree, slide_path)

    # Annotation questions
    if bullets:
        n = len(bullets)
        each_h = (ah - (n - 1) * GAP) // n
        for i, bullet in enumerate(bullets):
            by = ay + i * (each_h + GAP)
            tree = etree.parse(slide_path)
            sid = _next_id(tree)
            _add_shape(tree, _textbox_xml(
                sid, bullet, ann_x, by, ann_w, each_h,
                font_size=1800, bold='0', align='l'
            ))
            _write(tree, slide_path)


# ─── layout dispatcher ────────────────────────────────────────────────────────

def build_flexible_slide(work_dir, slide_def, lesson, image_dir):
    """
    Route to the right layout builder based on slide_def['layout'].
    Returns path to new slide, or None if text_only (handled by clone-and-replace).
    """
    layout = slide_def.get('layout', 'text_only')
    if layout == 'text_only':
        return None  # handled by existing clone logic

    slide_path = create_blank_slide(work_dir)

    if layout == 'image_grid':
        build_image_grid(work_dir, slide_path, slide_def, image_dir)
    elif layout == 'provocation':
        build_provocation(work_dir, slide_path, slide_def, image_dir)
    elif layout == 'comparison':
        build_comparison(work_dir, slide_path, slide_def, image_dir)
    elif layout in ('image_right', 'image_text'):
        build_image_text(work_dir, slide_path, slide_def, image_dir, img_side='right')
    elif layout == 'image_left':
        build_image_text(work_dir, slide_path, slide_def, image_dir, img_side='left')
    elif layout == 'diagram_annotated':
        build_diagram_annotated(work_dir, slide_path, slide_def, image_dir)
    else:
        # Unknown layout — treat as text_only
        return None

    return slide_path
