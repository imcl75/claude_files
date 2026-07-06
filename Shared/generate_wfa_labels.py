#!/usr/bin/env python3
"""
generate_wfa_labels.py  —  WFA Learning Label Sheet Generator  v1.0
Exactly replicates the Flask Learning Labels Tool
(https://staff.wallscourt-farm-academy.co.uk/learning-labels/)

Produces 12 identical Avery 99×42mm labels (2 col × 6 row) as DOCX.
All DXA measurements, font sizes, and icon dimensions match the LL tool.

MODES
─────
mathematician   : maths topic label (same as existing generate_labels.py)
geographer      : Geographer subject label
historian       : Historian subject label
scientist       : Scientist subject label
reader          : Reader subject label
computer_scientist : Computer Scientist
artist / musician / athlete / linguist / Designer / Citizen : as labelled

USAGE
─────
# Single label:
python3 generate_wfa_labels.py --mode mathematician \\
    --date "06/07/2026" --topic "Statistics" \\
    --lf "draw a line graph." \\
    --ican1 "draw and label axes." \\
    --ican2 "plot points accurately." \\
    --out T6W7_L20_Mon_Labels.docx

python3 generate_wfa_labels.py --mode geographer \\
    --date "07/07/2026" \\
    --question "Are England and Brazil different?" \\
    --lf "compare human geography features." \\
    --ican1 "identify human geography features." \\
    --ican2 "compare two countries." \\
    --out T6W7_L4_Tue_Labels.docx

# Batch from labels_data.json (drop-in replacement for generate_labels.py):
python3 generate_wfa_labels.py --json /home/claude/labels_data.json 20 21 22

ICON SETUP
──────────
Icons are cached at /home/claude/ll_icons/{subject}.png
On first run the script fetches them from the LL tool HTML.
You can also manually copy icons:
  - mathematician.png is extracted from WFA_Labels_template.docx automatically
  - others are fetched from staff.wallscourt-farm-academy.co.uk/learning-labels/
"""

import argparse, base64, io, json, os, re, sys, zipfile, urllib.request

# ─── LL Tool exact measurements (all DXA unless noted) ───────────────────────
# Source: generateEnquiryDocx() in index.html
PAGE_W, PAGE_H       = 11905, 16837          # A4
MAR_TOP, MAR_BOT     = 1215, 820
MAR_L, MAR_R         = 389, 446
TBL_W                = 11376                 # outer table
COL_CELL             = 5616                 # label column
COL_GAP              = 144                  # gap column
ROW_H                = 2399                 # exact row height
CELL_M_TOP           = 141
CELL_M_LR            = 115
INNER_W              = 5386                 # inner nested table
INNER_RGT_COL        = 1000                # icon column
INNER_LFT_COL        = INNER_W - INNER_RGT_COL  # 4386

# Font sizes in half-points (OOXML w:sz). Enquiry mode:
EQ_DATE    = 16   # 8pt
EQ_KQ_LBL  = 16   # 8pt bold
EQ_KQ_TEXT = 20   # 10pt bold underline
EQ_LF      = 18   # 9pt
EQ_ICAN    = 16   # 8pt
EQ_CAP     = 13   # 6.5pt
# Mathematician mode:
MQ_DATE    = 20   # 10pt
MQ_TOPIC   = 26   # 13pt bold underline
MQ_LF      = 22   # 11pt
MQ_ICAN    = 18   # 9pt
MQ_CAP     = 13   # 6.5pt

# Icon pixel dimensions [w, h] (ICON_DIMS from LL tool, 96dpi screen px → inches w/96)
ICON_DIMS = {
    "Citizen":            (38, 38),
    "Designer":           (38, 35),
    "artist":             (38, 37),
    "athlete":            (37, 38),
    "computer_scientist": (38, 35),
    "geographer":         (38, 37),
    "historian":          (38, 26),
    "linguist":           (38, 37),
    "mathematician":      (38, 33),
    "musician":           (38, 36),
    "reader":             (32, 38),
    "scientist":          (38, 27),
    "writer":             (38, 37),
}

SUBJECT_LABELS = {
    "historian":          "historian",
    "scientist":          "scientist",
    "geographer":         "geographer",
    "reader":             "reader",
    "mathematician":      "mathematician",
    "writer":             "writer",
    "computer_scientist": "computer scientist",
    "artist":             "artist",
    "musician":           "musician",
    "athlete":            "athlete",
    "linguist":           "linguist",
    "Designer":           "designer",
    "Citizen":            "citizen",
}

# ─── Maths template placeholders (must match exactly what's in the DOCX XML) ──
T_DATE  = "15/06/2026"
T_TOPIC = "Calculation"
T_LF    = "LF: To identify which operation is required to solve a problem."
T_IC1   = "I can identify the operation and clauclate using a suitable method"
T_IC2   = "I can solve problems involving the four operations"

TEMPLATE_PATH  = "/home/claude/WFA_Labels_template.docx"
ICON_CACHE_DIR = "/home/claude/ll_icons"
LL_TOOL_URL    = "https://staff.wallscourt-farm-academy.co.uk/learning-labels/index.html"
GITHUB_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/imcl75/claude_files/main/"
    "Maths/WFA_Labels_template.docx"
)

# ─── Icon helpers ─────────────────────────────────────────────────────────────

def _get_github_token():
    try:
        with open('/mnt/skills/user/github-sync/SKILL.md') as f:
            text = f.read()
        m = re.search(r'GITHUB_TOKEN:\s*(\S+)', text)
        return m.group(1) if m else None
    except Exception:
        return None

def ensure_template():
    """Download WFA_Labels_template.docx from GitHub if not locally available."""
    if os.path.exists(TEMPLATE_PATH):
        return
    print("  Downloading WFA_Labels_template.docx from GitHub...", end=" ", flush=True)
    token = _get_github_token()
    headers = {"Authorization": f"token {token}"} if token else {}
    req = urllib.request.Request(GITHUB_TEMPLATE_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(TEMPLATE_PATH, 'wb') as f:
        f.write(data)
    print(f"OK ({len(data)} bytes)")
    # Also extract mathematician icon while we're here
    _extract_mathematician_icon(data)

def _extract_mathematician_icon(template_bytes):
    os.makedirs(ICON_CACHE_DIR, exist_ok=True)
    path = os.path.join(ICON_CACHE_DIR, "mathematician.png")
    if os.path.exists(path):
        return
    with zipfile.ZipFile(io.BytesIO(template_bytes)) as z:
        media = [n for n in z.namelist() if n.startswith('word/media/') and n.endswith('.png')]
        if media:
            with open(path, 'wb') as f:
                f.write(z.read(media[0]))

def fetch_icons_from_tool():
    """Download all subject icons from the LL tool HTML and cache them."""
    os.makedirs(ICON_CACHE_DIR, exist_ok=True)
    already_cached = [k for k in ICON_DIMS
                      if os.path.exists(os.path.join(ICON_CACHE_DIR, f"{k}.png"))]
    if len(already_cached) == len(ICON_DIMS):
        return  # all present
    print("  Fetching icons from LL tool...", end=" ", flush=True)
    req = urllib.request.Request(LL_TOOL_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    m = re.search(r"const ICONS = \{(.*?)\};", html, re.DOTALL)
    if not m:
        print("WARNING: could not find ICONS in LL tool HTML")
        return
    icons_body = m.group(1)
    count = 0
    for key in ICON_DIMS:
        cache_path = os.path.join(ICON_CACHE_DIR, f"{key}.png")
        if os.path.exists(cache_path):
            continue
        pat = r'"' + re.escape(key) + r'"\s*:\s*"data:image/png;base64,([A-Za-z0-9+/=\n]+)"'
        km = re.search(pat, icons_body)
        if km:
            b64 = km.group(1).replace('\n', '')
            with open(cache_path, 'wb') as f:
                f.write(base64.b64decode(b64))
            count += 1
    print(f"cached {count} new icons")

def get_icon_bytes(subject):
    """Return PNG bytes for the given subject, or None if unavailable."""
    fetch_icons_from_tool()
    path = os.path.join(ICON_CACHE_DIR, f"{subject}.png")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    return None

# ─── MATHEMATICIAN mode: template text replacement ─────────────────────────────

def build_mathematician_docx(date, topic, lf, ican1, ican2, out_path):
    """Use the maths DOCX template (text replacement only — icon stays as-is)."""
    ensure_template()
    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        files = {name: z.read(name) for name in z.namelist()}
    xml = files['word/document.xml'].decode('utf-8')
    # Ensure LF / I can don't already contain the prefix (strip if caller passed full string)
    lf_full   = lf    if lf.startswith("LF: To ")  else f"LF: To {lf}"
    ic1_full  = ican1 if ican1.startswith("I can ") else f"I can {ican1}"
    ic2_full  = ican2 if ican2.startswith("I can ") else f"I can {ican2}"
    xml = xml.replace(T_DATE,  date)
    xml = xml.replace(T_TOPIC, topic)
    xml = xml.replace(T_LF,    lf_full)
    xml = xml.replace(T_IC1,   ic1_full)
    xml = xml.replace(T_IC2,   ic2_full)
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            if name == 'word/document.xml':
                zout.writestr(name, xml.encode('utf-8'))
            else:
                zout.writestr(name, data)

# ─── ENQUIRY mode: build DOCX from scratch ────────────────────────────────────

# Pixel-to-EMU: 1 px at 96dpi = 914400/96 = 9525 EMU
# DXA to EMU: 1 DXA = 914400/1440 = 635 EMU
PX_TO_EMU = 9525
DXA_TO_EMU = 635

NSMAP = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
}

def _e(tag_name, attribs=None, text=None, children=None):
    """Build an XML string element."""
    ns, tag = tag_name.split(':') if ':' in tag_name else ('', tag_name)
    full_tag = f"{{{NSMAP[ns]}}}{tag}" if ns else tag
    parts = [f'<{tag_name}']
    if attribs:
        for k, v in attribs.items():
            parts.append(f' {k}="{v}"')
    if text is not None:
        parts.append(f'>{_xmlesc(text)}</{tag_name}>')
    elif children:
        parts.append('>')
        parts.extend(children)
        parts.append(f'</{tag_name}>')
    else:
        parts.append('/>')
    return ''.join(parts)

def _xmlesc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def _none_borders():
    sides = ['top','left','bottom','right','insideH','insideV']
    els = [f'<w:{s} w:val="none" w:color="FFFFFF" w:sz="0"/>' for s in sides]
    return '<w:tcBorders>' + ''.join(els) + '</w:tcBorders>'

def _spacing(line=280, rule='auto', before=0, after=0):
    return f'<w:spacing w:line="{line}" w:lineRule="{rule}" w:before="{before}" w:after="{after}"/>'

def _fonts():
    return '<w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri"/>'

def _text_para(text, sz, bold=False, underline=False,
               align=None, line=280, line_rule='auto', after=0, before=0):
    """Build a <w:p> paragraph XML string."""
    ppr_parts = [f'<w:pPr>{_spacing(line, line_rule, before, after)}']
    if align:
        ppr_parts.append(f'<w:jc w:val="{align}"/>')
    ppr_parts.append('</w:pPr>')
    ppr = ''.join(ppr_parts)
    rpr = f'<w:rPr>{_fonts()}'
    if bold:      rpr += '<w:b/>'
    if underline: rpr += '<w:u w:val="single"/>'
    rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
    preserve = ' xml:space="preserve"' if text and (' ' in text or text[0] == ' ') else ''
    run = f'<w:r>{rpr}<w:t{preserve}>{_xmlesc(text)}</w:t></w:r>'
    return f'<w:p>{ppr}{run}</w:p>'

def _image_para(rId, cx_emu, cy_emu, doc_pr_id):
    """Build a right-aligned inline image paragraph."""
    pic_xml = (
        f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="0" name=""/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rId}"/>'
        f'<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx_emu}" cy="{cy_emu}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic>'
    )
    graphic = (
        f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'{pic_xml}</a:graphicData></a:graphic>'
    )
    inline = (
        f'<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        f'<wp:extent cx="{cx_emu}" cy="{cy_emu}"/>'
        f'<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{doc_pr_id}" name="" descr="" title=""/>'
        f'<wp:cNvGraphicFramePr/>'
        f'{graphic}</wp:inline>'
    )
    drawing = f'<w:drawing>{inline}</w:drawing>'
    ppr = f'<w:pPr><w:jc w:val="right"/>{_spacing(720,"exact",0,20)}</w:pPr>'
    return f'<w:p>{ppr}<w:r>{drawing}</w:r></w:p>'

def _build_left_col(mode, date, question, lf, ican1, ican2):
    """Build content paragraphs for the left (text) column."""
    lf_txt  = lf    if lf.startswith("LF: To ")  else f"LF: To {lf}"
    ic1_txt = ican1 if ican1.startswith("I can ") else f"I can {ican1}"
    ic2_txt = ican2 if ican2.startswith("I can ") else f"I can {ican2}"
    parts = []
    if mode == 'mathematician':
        parts.append(_text_para(date,     MQ_DATE))
        parts.append(_text_para(question, MQ_TOPIC, bold=True, underline=True))
        parts.append(_text_para(lf_txt,   MQ_LF))
        parts.append(_text_para(ic1_txt,  MQ_ICAN))
        parts.append(_text_para(ic2_txt,  MQ_ICAN))
    else:
        parts.append(_text_para(date,          EQ_DATE))
        parts.append(_text_para("Key Question", EQ_KQ_LBL, bold=True))
        parts.append(_text_para(question,       EQ_KQ_TEXT, bold=True, underline=True))
        parts.append(_text_para(lf_txt,         EQ_LF))
        parts.append(_text_para(ic1_txt,        EQ_ICAN))
        parts.append(_text_para(ic2_txt,        EQ_ICAN))
    return ''.join(parts)

def _build_right_col(subject, rId, doc_pr_id):
    """Build icon + caption paragraphs for the right column."""
    parts = []
    px_w, px_h = ICON_DIMS.get(subject, (38, 38))
    cx = px_w * PX_TO_EMU
    cy = px_h * PX_TO_EMU
    if rId:
        parts.append(_image_para(rId, cx, cy, doc_pr_id))
    cap = SUBJECT_LABELS.get(subject, subject)
    cap_sz = MQ_CAP if subject == 'mathematician' else EQ_CAP
    parts.append(_text_para(cap, cap_sz, align='right'))
    return ''.join(parts)

def _no_borders():
    return (
        '<w:tcBorders>'
        '<w:top w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:left w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:bottom w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:right w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '</w:tcBorders>'
    )

def _tc(width_dxa, content_xml, top_m=0, bot_m=0, l_m=0, r_m=0):
    return (
        f'<w:tc><w:tcPr>'
        f'<w:tcW w:type="dxa" w:w="{width_dxa}"/>'
        f'{_no_borders()}'
        f'<w:tcMar>'
        f'<w:top w:type="dxa" w:w="{top_m}"/>'
        f'<w:left w:type="dxa" w:w="{l_m}"/>'
        f'<w:bottom w:type="dxa" w:w="{bot_m}"/>'
        f'<w:right w:type="dxa" w:w="{r_m}"/>'
        f'</w:tcMar>'
        f'<w:vAlign w:val="top"/>'
        f'</w:tcPr>{content_xml}</w:tc>'
    )

def _gap_cell():
    """The 144-DXA gap cell with white top/bottom borders."""
    borders = (
        '<w:tcBorders>'
        '<w:top w:val="single" w:sz="8" w:color="FFFFFF"/>'
        '<w:bottom w:val="single" w:sz="8" w:color="FFFFFF"/>'
        '<w:left w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:right w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '</w:tcBorders>'
    )
    return (
        f'<w:tc><w:tcPr>'
        f'<w:tcW w:type="dxa" w:w="{COL_GAP}"/>'
        f'{borders}</w:tcPr><w:p/></w:tc>'
    )

def _inner_tbl(left_xml, right_xml):
    """Build the inner nested 2-column table."""
    tbl_borders = (
        '<w:tblBorders>'
        '<w:top w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:left w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:bottom w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:right w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:insideH w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:insideV w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '</w:tblBorders>'
    )
    grid = (
        f'<w:tblGrid>'
        f'<w:gridCol w:w="{INNER_LFT_COL}"/>'
        f'<w:gridCol w:w="{INNER_RGT_COL}"/>'
        f'</w:tblGrid>'
    )
    left_tc  = _tc(INNER_LFT_COL, left_xml)
    right_tc = _tc(INNER_RGT_COL, right_xml)
    return (
        f'<w:tbl>'
        f'<w:tblPr>'
        f'<w:tblW w:type="dxa" w:w="{INNER_W}"/>'
        f'{tbl_borders}'
        f'</w:tblPr>'
        f'{grid}'
        f'<w:tr>{left_tc}{right_tc}</w:tr>'
        f'</w:tbl>'
    )

def _label_cell(subject, mode, date, question, lf, ican1, ican2, rId, doc_pr_id):
    """Build a full outer label cell (including the inner nested table)."""
    left_xml  = _build_left_col(mode, date, question, lf, ican1, ican2)
    right_xml = _build_right_col(subject, rId, doc_pr_id)
    inner     = _inner_tbl(left_xml, right_xml)
    return _tc(COL_CELL, inner, CELL_M_TOP, 0, CELL_M_LR, CELL_M_LR)

def build_enquiry_docx(subject, date, question, lf, ican1, ican2, out_path):
    """Build enquiry label DOCX from scratch XML (no template needed)."""
    mode = 'mathematician' if subject == 'mathematician' else 'enquiry'
    icon_bytes = get_icon_bytes(subject)

    # Build rels and decide rId assignments
    # rId1-5 = document infrastructure (styles, numbering, footnotes, settings, comments)
    # rId6+ = images (12 copies)
    BASE_RID = 6
    N_IMAGES = 12

    # Build relationships XML
    rels_start = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
        '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>'
    )
    img_rels = ''
    if icon_bytes:
        for i in range(N_IMAGES):
            rId = BASE_RID + i
            fname = f'icon_{i:02d}.png'
            img_rels += (
                f'<Relationship Id="rId{rId}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/{fname}"/>'
            )
    rels_xml = rels_start + img_rels + '</Relationships>'

    # Build document.xml
    outer_tbl_borders = (
        '<w:tblBorders>'
        '<w:top w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:left w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:bottom w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:right w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:insideH w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '<w:insideV w:val="none" w:color="FFFFFF" w:sz="0"/>'
        '</w:tblBorders>'
    )
    outer_grid = (
        f'<w:tblGrid>'
        f'<w:gridCol w:w="{COL_CELL}"/>'
        f'<w:gridCol w:w="{COL_GAP}"/>'
        f'<w:gridCol w:w="{COL_CELL}"/>'
        f'</w:tblGrid>'
    )

    rows_xml = ''
    img_idx = 0
    for row_idx in range(6):
        cells = ''
        for col_idx in range(2):  # left label, right label
            rId_str = f"rId{BASE_RID + img_idx}" if icon_bytes else None
            doc_pr_id = img_idx + 1
            cells += _label_cell(subject, mode, date, question, lf, ican1, ican2,
                                 rId_str, doc_pr_id)
            img_idx += 1
            if col_idx == 0:
                cells += _gap_cell()
        rows_xml += (
            f'<w:tr>'
            f'<w:trPr><w:trHeight w:val="{ROW_H}" w:hRule="exact"/></w:trPr>'
            f'{cells}</w:tr>'
        )

    # Page/section properties
    sect_pr = (
        f'<w:sectPr>'
        f'<w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
        f'<w:pgMar w:top="{MAR_TOP}" w:right="{MAR_R}" w:bottom="{MAR_BOT}" w:left="{MAR_L}"/>'
        f'</w:sectPr>'
    )

    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'mc:Ignorable="w14 w15 wp14">'
        '<w:body>'
        '<w:tbl>'
        '<w:tblPr>'
        f'<w:tblW w:type="dxa" w:w="{TBL_W}"/>'
        f'{outer_tbl_borders}'
        '</w:tblPr>'
        f'{outer_grid}'
        f'{rows_xml}'
        '</w:tbl>'
        f'{sect_pr}'
        '</w:body>'
        '</w:document>'
    )

    # Minimal supporting XML files
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '</Types>'
    )
    dot_rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults>'
        '<w:rPrDefault><w:rPr>'
        '<w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri"/>'
        '<w:sz w:val="20"/><w:szCs w:val="20"/>'
        '</w:rPr></w:rPrDefault>'
        '</w:docDefaults>'
        '</w:styles>'
    )
    settings_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
    )

    # Write DOCX
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        zout.writestr('[Content_Types].xml', content_types.encode('utf-8'))
        zout.writestr('_rels/.rels', dot_rels.encode('utf-8'))
        zout.writestr('word/document.xml', doc_xml.encode('utf-8'))
        zout.writestr('word/_rels/document.xml.rels', rels_xml.encode('utf-8'))
        zout.writestr('word/styles.xml', styles_xml.encode('utf-8'))
        zout.writestr('word/settings.xml', settings_xml.encode('utf-8'))
        if icon_bytes:
            for i in range(N_IMAGES):
                zout.writestr(f'word/media/icon_{i:02d}.png', icon_bytes)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description='WFA Learning Label Sheet Generator (replicates LL tool)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument('--mode', default='mathematician',
                   help='mathematician | geographer | historian | scientist | etc.')
    p.add_argument('--date', default='')
    p.add_argument('--question', default='', help='Key Question (enquiry mode)')
    p.add_argument('--topic', default='', help='Maths topic (mathematician mode)')
    p.add_argument('--lf', default='', help='Learning Focus after "To"')
    p.add_argument('--ican1', default='', help='I can statement 1 (after "I can")')
    p.add_argument('--ican2', default='', help='I can statement 2 (after "I can")')
    p.add_argument('--out', default='WFA_Labels.docx')
    p.add_argument('--json', default=None,
                   help='Batch mode: path to labels_data.json (mathematician)')
    args, extra = p.parse_known_args()

    if args.json:
        # Batch mode — drop-in for generate_labels.py
        with open(args.json) as f:
            all_labels = json.load(f)
        wanted = {int(x) for x in extra if x.isdigit()}
        labels = [l for l in all_labels if not wanted or l['lesson'] in wanted]
        if not labels:
            print("No matching label data."); sys.exit(1)
        ensure_template()
        for lbl in labels:
            week   = lbl.get('week', '')
            day    = lbl.get('day', '')[:3]
            lesson = lbl.get('lesson', 0)
            out    = f"/home/claude/{week}_L{lesson}_{day}_Labels.docx"
            # Strip prefixes if already present
            lf_raw    = lbl.get('lf', '')
            ic1_raw   = lbl.get('ican1', '')
            ic2_raw   = lbl.get('ican2', '')
            build_mathematician_docx(
                date=lbl.get('date', ''),
                topic=lbl.get('topic', ''),
                lf=lf_raw,
                ican1=ic1_raw,
                ican2=ic2_raw,
                out_path=out)
            print(f"  → {out}")
        return

    subject = args.mode
    question = args.question or args.topic

    if subject == 'mathematician':
        ensure_template()
        build_mathematician_docx(
            date=args.date, topic=question,
            lf=args.lf, ican1=args.ican1, ican2=args.ican2,
            out_path=args.out)
    else:
        build_enquiry_docx(
            subject=subject, date=args.date, question=question,
            lf=args.lf, ican1=args.ican1, ican2=args.ican2,
            out_path=args.out)

    print(f"✓ {args.out}")


if __name__ == '__main__':
    main()
