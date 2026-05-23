#!/usr/bin/env python3
"""
inject_key_spelling.py
Prepends the Key Spelling Practice slide to spelling_shed_slides_v3.pptx.

Usage:
    python inject_key_spelling.py "February"

The script:
  1. Reads key_spelling_template.pptx from the same directory as this script
  2. Replaces "February" with the supplied word throughout the slide XML
  3. Copies the media files (timer MP4 + poster PNG) into the main deck with new names
  4. Shifts all existing slides up by 1 and inserts the new slide as slide 1
  5. Updates presentation.xml and all relationship files accordingly
  6. Overwrites spelling_shed_slides_v3.pptx in place
"""

import sys, os, re, zipfile, shutil
from lxml import etree

# ── Config ────────────────────────────────────────────────────────────────────
KEY_WORD     = sys.argv[1] if len(sys.argv) > 1 else "February"
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
TEMPLATE     = os.path.join(SCRIPT_DIR, "key_spelling_template.pptx")
import json as _lj
with open("/home/claude/lesson.json") as _lf:
    _lcode = _lj.load(_lf).get("code", "XX")
MAIN         = f"/home/claude/spelling_shed_slides_{_lcode}.pptx"
TEMP_OUT     = "/home/claude/spelling_shed_slides_v3_tmp.pptx"

NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_PRS = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R   = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# ── Read template ─────────────────────────────────────────────────────────────
with zipfile.ZipFile(TEMPLATE) as tz:
    t_slide_xml  = tz.read("ppt/slides/slide1.xml").decode("utf-8")
    t_slide_rels = tz.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")
    t_mp4        = tz.read("ppt/media/media1.mp4")
    t_poster     = tz.read("ppt/media/image1.png")

# Substitute the spelling word (replace "February" everywhere in the XML)
t_slide_xml = t_slide_xml.replace("February", KEY_WORD)

# ── Read main deck ────────────────────────────────────────────────────────────
with zipfile.ZipFile(MAIN) as mz:
    m_files = {n: mz.read(n) for n in mz.namelist()}

# Find highest existing image/media numbers
def max_num(files, pattern):
    nums = [int(re.search(r"(\d+)", os.path.basename(n)).group(1))
            for n in files if re.match(pattern, n)]
    return max(nums, default=0)

max_img = max_num(m_files, r"ppt/media/image\d+")
max_med = max_num(m_files, r"ppt/media/media\d+")
new_img = max_img + 1
new_med = max_med + 1

# ── Shift existing slides up by 1 ─────────────────────────────────────────────
shifted = {}
for name, data in m_files.items():
    ms = re.match(r"^ppt/slides/slide(\d+)\.xml$", name)
    mr = re.match(r"^ppt/slides/_rels/slide(\d+)\.xml\.rels$", name)
    if ms:
        shifted[f"ppt/slides/slide{int(ms.group(1)) + 1}.xml"] = data
    elif mr:
        shifted[f"ppt/slides/_rels/slide{int(mr.group(1)) + 1}.xml.rels"] = data
    else:
        shifted[name] = data

# ── Fix notesSlide back-references (each points to old slide{n}, must be slide{n+1}) ──
for name in list(shifted.keys()):
    mn = re.match(r"^ppt/notesSlides/_rels/notesSlide(\d+)\.xml\.rels$", name)
    if mn:
        rels_xml = shifted[name].decode("utf-8")
        def _fix_ns_ref(m2):
            n = int(m2.group(1))
            return f'Target="../slides/slide{n + 1}.xml"'
        updated = re.sub(
            'Target="../slides/slide([0-9]+).xml"',
            _fix_ns_ref,
            rels_xml
        )
        shifted[name] = updated.encode("utf-8")

# ── Add new media files ───────────────────────────────────────────────────────
shifted[f"ppt/media/image{new_img}.png"] = t_poster
shifted[f"ppt/media/media{new_med}.mp4"] = t_mp4

# ── Update template slide rels: remap media paths, drop notesSlide ref ────────
rels_tree = etree.fromstring(t_slide_rels.encode())
for el in rels_tree.findall(f"{{{NS_REL}}}Relationship"):
    t = el.get("Target", "")
    rtype = el.get("Type", "")
    if "media1.mp4" in t:
        el.set("Target", t.replace("media1.mp4", f"media{new_med}.mp4"))
    elif "image1.png" in t:
        el.set("Target", t.replace("image1.png", f"image{new_img}.png"))
    elif "notesSlide" in t:
        rels_tree.remove(el)   # drop notes reference — not needed

# Compact-renumber remaining rIds (1, 2, 3, ...) so there are no gaps
all_rels = rels_tree.findall(f"{{{NS_REL}}}Relationship")
old_to_new = {el.get("Id"): f"rId{i+1}" for i, el in enumerate(all_rels)}
for el in all_rels:
    el.set("Id", old_to_new[el.get("Id")])

new_rels_xml = etree.tostring(rels_tree, xml_declaration=True,
                               encoding="UTF-8", standalone=True)

# Update any r:embed/r:link references in the slide XML to use new rIds
for old_rid, new_rid in old_to_new.items():
    if old_rid != new_rid:
        t_slide_xml = t_slide_xml.replace(f'"{old_rid}"', f'"{new_rid}"')

shifted["ppt/slides/slide1.xml"]             = t_slide_xml.encode("utf-8")
shifted["ppt/slides/_rels/slide1.xml.rels"]  = new_rels_xml

# ── Update ppt/_rels/presentation.xml.rels ───────────────────────────────────
prs_rels_xml = shifted["ppt/_rels/presentation.xml.rels"].decode("utf-8")
prs_rels_tree = etree.fromstring(prs_rels_xml.encode())

# Shift Target paths of existing slide relationships (slide1→slide2, etc.)
for el in prs_rels_tree.findall(f"{{{NS_REL}}}Relationship"):
    t = el.get("Target", "")
    m = re.match(r"slides/slide(\d+)\.xml$", t)
    if m:
        el.set("Target", f"slides/slide{int(m.group(1)) + 1}.xml")

# Find next rId number
existing_rids = [int(re.search(r"\d+", el.get("Id")).group())
                 for el in prs_rels_tree.findall(f"{{{NS_REL}}}Relationship")
                 if re.search(r"\d+", el.get("Id", ""))]
new_rid = f"rId{max(existing_rids, default=0) + 1}"

# Add new relationship for slide1
new_rel = etree.SubElement(prs_rels_tree, f"{{{NS_REL}}}Relationship")
new_rel.set("Id", new_rid)
new_rel.set("Type", f"{NS_R}/slide")
new_rel.set("Target", "slides/slide1.xml")

shifted["ppt/_rels/presentation.xml.rels"] = etree.tostring(
    prs_rels_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

# ── Update ppt/presentation.xml: prepend new sldId entry ─────────────────────
prs_xml = shifted["ppt/presentation.xml"].decode("utf-8")
prs_tree = etree.fromstring(prs_xml.encode())

sld_id_lst = prs_tree.find(f"{{{NS_PRS}}}sldIdLst")
existing_ids = [int(el.get("id", 0)) for el in sld_id_lst]
new_sld_id = max(existing_ids, default=255) + 1

new_sld_el = etree.Element(f"{{{NS_PRS}}}sldId")
new_sld_el.set("id", str(new_sld_id))
new_sld_el.set(f"{{{NS_R}}}id", new_rid)
sld_id_lst.insert(0, new_sld_el)

shifted["ppt/presentation.xml"] = etree.tostring(
    prs_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

# ── Update docProps/app.xml slide count ──────────────────────────────────────
if '[Content_Types].xml' in shifted and 'docProps/app.xml' in shifted:
    import re as _re
    app_xml = shifted['docProps/app.xml'].decode('utf-8')
    def _inc_slides(m):
        return f'<Slides>{int(m.group(1)) + 1}</Slides>'
    app_xml = _re.sub('<Slides>([0-9]+)</Slides>', _inc_slides, app_xml)
    shifted['docProps/app.xml'] = app_xml.encode('utf-8')

# ── Update [Content_Types].xml ────────────────────────────────────────────────
ct_xml = shifted["[Content_Types].xml"].decode("utf-8")

# Add mp4 default type if absent
if "mp4" not in ct_xml:
    ct_xml = ct_xml.replace(
        "</Types>",
        '<Default Extension="mp4" ContentType="video/mp4"/></Types>')

# Shift all existing slide Override PartNames: slide{n} -> slide{n+1}
# Then add new slide1 entry for the injected key spelling slide
SLIDE_CT = ('application/vnd.openxmlformats-officedocument'
            '.presentationml.slide+xml')

def _shift_slide_ct(m):
    n = int(m.group(1))
    return f'PartName="/ppt/slides/slide{n + 1}.xml"'

ct_xml = re.sub(r'PartName="/ppt/slides/slide([0-9]+)\.xml"', _shift_slide_ct, ct_xml)

# Add new slide1 override for the injected slide
if 'PartName="/ppt/slides/slide1.xml"' not in ct_xml:
    ct_xml = ct_xml.replace(
        "</Types>",
        f'<Override PartName="/ppt/slides/slide1.xml" ' +
        f'ContentType="{SLIDE_CT}"/></Types>')

shifted["[Content_Types].xml"] = ct_xml.encode("utf-8")

# ── Write output ──────────────────────────────────────────────────────────────
with zipfile.ZipFile(TEMP_OUT, "w", zipfile.ZIP_DEFLATED) as oz:
    for name, data in shifted.items():
        if name.endswith("/"):
            continue  # strip directory entries — PowerPoint rejects them
        oz.writestr(name, data if isinstance(data, bytes) else data.encode("utf-8"))

os.replace(TEMP_OUT, MAIN)

total_slides = len([n for n in shifted if re.match(r"ppt/slides/slide\d+\.xml$", n)])
print(f"✓ Prepended Key Spelling Practice slide — word: '{KEY_WORD}'")
print(f"  Deck now has {total_slides} slides (was {total_slides - 1})")
