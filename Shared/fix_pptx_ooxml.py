#!/usr/bin/env python3
"""
fix_pptx_ooxml.py — Shared post-processing utility for WFA PPTX files built by ZIP manipulation.

Fixes four OOXML issues that cause PowerPoint's repair dialog on open:
  1. Non-standard media filenames (e.g. conn_col.emf, conn_icon.png) → imageN.ext
  2. notesSlide back-references after slide renumbering
  3. Empty <a:r> runs in notesSlides (pptxgenjs quirk)
  4. notesMaster theme reference: theme1.xml → theme2.xml (adds theme2.xml if missing)

Usage as a script:
    python3 fix_pptx_ooxml.py <input.pptx>              # overwrites in place
    python3 fix_pptx_ooxml.py <input.pptx> <output.pptx>  # writes to new file

Usage as a module:
    from fix_pptx_ooxml import fix_pptx
    fix_pptx('/home/claude/MyLesson.pptx')  # in place
    fix_pptx('/home/claude/MyLesson.pptx', '/home/claude/MyLesson_fixed.pptx')
"""

import re
import sys
import zipfile
from lxml import etree


def fix_pptx(input_path, output_path=None):
    """
    Apply all OOXML fixes to a PPTX file.
    If output_path is None, overwrites input_path in place.
    Returns True if any fixes were applied.
    """
    if output_path is None:
        output_path = input_path

    # Read all entries from ZIP
    files = {}
    with zipfile.ZipFile(input_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    any_fixed = False

    # ------------------------------------------------------------------ #
    # 1. Non-standard media filenames → imageN.ext                        #
    # ------------------------------------------------------------------ #
    media_prefix = 'ppt/media/'

    existing_nums = []
    for name in files:
        if name.startswith(media_prefix):
            m = re.match(r'image(\d+)\.\w+', name[len(media_prefix):])
            if m:
                existing_nums.append(int(m.group(1)))

    max_n = max(existing_nums, default=0)
    non_std = [
        name for name in files
        if name.startswith(media_prefix)
        and not re.match(r'ppt/media/image\d+\.\w+', name)
    ]

    if non_std:
        rename_map = {}
        counter = max_n + 1
        for name in sorted(non_std):
            basename = name[len(media_prefix):]
            ext = basename.rsplit('.', 1)[-1] if '.' in basename else 'bin'
            rename_map[name] = f'{media_prefix}image{counter}.{ext}'
            counter += 1

        # Rename entries
        for old, new in rename_map.items():
            files[new] = files.pop(old)

        # Update all _rels references
        rels_pattern = re.compile(
            r'ppt/(slides|slideLayouts|slideMasters|notesMasters|notesSlides)/_rels/.*\.rels'
        )
        for name in list(files.keys()):
            if not rels_pattern.match(name):
                continue
            content = files[name].decode('utf-8')
            changed = False
            for old, new in rename_map.items():
                old_base = old[len(media_prefix):]
                new_base = new[len(media_prefix):]
                if old_base in content:
                    content = content.replace(old_base, new_base)
                    changed = True
            if changed:
                files[name] = content.encode('utf-8')

        print(f"  [fix_pptx_ooxml] Renamed {len(rename_map)} non-standard media file(s): "
              f"{[k[len(media_prefix):] for k in rename_map]}")
        any_fixed = True

    # ------------------------------------------------------------------ #
    # 2. notesSlide back-references after slide renumbering               #
    # ------------------------------------------------------------------ #
    ns_to_slide = {}
    for name, data in files.items():
        if not re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', name):
            continue
        s_num = int(re.search(r'slide(\d+)', name).group(1))
        for m in re.finditer(r'notesSlide(\d+)\.xml', data.decode('utf-8', errors='ignore')):
            ns_to_slide[int(m.group(1))] = s_num

    fixed_backrefs = 0
    for name in list(files.keys()):
        if not re.match(r'ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels', name):
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
            fixed_backrefs += 1

    if fixed_backrefs:
        print(f"  [fix_pptx_ooxml] Fixed {fixed_backrefs} notesSlide back-reference(s)")
        any_fixed = True

    # ------------------------------------------------------------------ #
    # 3. Empty <a:r> runs in notesSlides (pptxgenjs quirk)               #
    # ------------------------------------------------------------------ #
    empty_run_pat = re.compile(
        r'<a:r>\s*<a:rPr[^/]*/>\s*<a:t>\s*</a:t>\s*</a:r>'
    )
    fixed_runs = 0
    for name in list(files.keys()):
        if not re.match(r'ppt/notesSlides/notesSlide\d+\.xml', name):
            continue
        content = files[name].decode('utf-8')
        fixed = empty_run_pat.sub('', content)
        if fixed != content:
            files[name] = fixed.encode('utf-8')
            fixed_runs += 1

    if fixed_runs:
        print(f"  [fix_pptx_ooxml] Removed empty <a:r> runs from {fixed_runs} notesSlide(s)")
        any_fixed = True

    # ------------------------------------------------------------------ #
    # 4. notesMaster theme reference: theme1.xml → theme2.xml            #
    # ------------------------------------------------------------------ #
    nm_rels_key = 'ppt/notesMasters/_rels/notesMaster1.xml.rels'
    if nm_rels_key in files:
        nm_rels = files[nm_rels_key].decode('utf-8')
        if 'theme/theme1.xml' in nm_rels:
            files[nm_rels_key] = nm_rels.replace(
                'theme/theme1.xml', 'theme/theme2.xml'
            ).encode('utf-8')
            print("  [fix_pptx_ooxml] Fixed notesMaster theme reference (theme1 → theme2)")
            any_fixed = True

    # Add theme2.xml if referenced but missing
    if 'ppt/theme/theme1.xml' in files and 'ppt/theme/theme2.xml' not in files:
        files['ppt/theme/theme2.xml'] = files['ppt/theme/theme1.xml']
        ct = files['[Content_Types].xml'].decode('utf-8')
        if 'theme2.xml' not in ct:
            ct = ct.replace(
                '<Override PartName="/ppt/theme/theme1.xml"',
                '<Override PartName="/ppt/theme/theme2.xml"'
                ' ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
                '<Override PartName="/ppt/theme/theme1.xml"'
            )
            files['[Content_Types].xml'] = ct.encode('utf-8')
        print("  [fix_pptx_ooxml] Added missing theme2.xml")
        any_fixed = True

    # ------------------------------------------------------------------ #
    # 5. Non-numeric relationship IDs in presentation.xml.rels            #
    # (e.g. rIdKQ) cause PowerPoint repair on open. Rename to rIdN.       #
    # ------------------------------------------------------------------ #
    if 'ppt/_rels/presentation.xml.rels' in files:
        prels_str = files['ppt/_rels/presentation.xml.rels'].decode('utf-8')
        non_std_ids = re.findall(r'Id="(rId[A-Za-z][A-Za-z0-9]*)"', prels_str)
        if non_std_ids:
            nums = [int(m) for m in re.findall(r'rId(\d+)', prels_str)]
            next_num = max(nums) + 1 if nums else 1
            for bad_id in non_std_ids:
                new_id = f'rId{next_num}'
                for fkey in ['ppt/_rels/presentation.xml.rels', 'ppt/presentation.xml']:
                    if fkey in files:
                        files[fkey] = files[fkey].decode('utf-8').replace(bad_id, new_id).encode('utf-8')
                next_num += 1
            print(f'  [fix_pptx_ooxml] Fixed {len(non_std_ids)} non-numeric rId(s): {non_std_ids}')
            any_fixed = True


    # ------------------------------------------------------------------ #
    # 6. SharePoint / Teams customXml metadata                            #
    # Files saved to/from SharePoint or Teams carry customXml/ parts that #
    # embed 23+ broken external schema references PowerPoint can never     #
    # validate, causing persistent repair dialogs on every open.          #
    # Strip the parts entirely — they carry no document content.          #
    # ------------------------------------------------------------------ #
    STRIP_PREFIX  = 'customXml/'
    STRIP_RELTYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml'
    SHAREPOINT_MARKERS = [
        'schemas.microsoft.com/sharepoint',
        'schemas.microsoft.com/office/2006/metadata',
        'schemas.microsoft.com/office/infopath',
    ]
    custom_parts = [n for n in files if n.startswith(STRIP_PREFIX)]
    if custom_parts:
        is_sharepoint = False
        for part in custom_parts:
            if part.endswith('.xml') and '_rels' not in part:
                content_str = files[part].decode('utf-8', errors='ignore')
                if any(m in content_str for m in SHAREPOINT_MARKERS):
                    is_sharepoint = True
                    break
        if is_sharepoint:
            for part in list(custom_parts):
                del files[part]
            # Remove customXml relationships from both _rels/.rels and ppt/_rels/presentation.xml.rels
            for rels_key in ['_rels/.rels', 'ppt/_rels/presentation.xml.rels']:
                if rels_key in files:
                    root = etree.fromstring(files[rels_key])
                    for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                        tgt = rel.get('Target', '')
                        typ = rel.get('Type', '')
                        if typ == STRIP_RELTYPE or 'customXml' in tgt:
                            root.remove(rel)
                    files[rels_key] = etree.tostring(root, xml_declaration=True,
                                                     encoding='UTF-8', standalone=True)
            # Remove from Content_Types
            if '[Content_Types].xml' in files:
                ct_root = etree.fromstring(files['[Content_Types].xml'])
                CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
                for el in list(ct_root):
                    if el.get('PartName', '').startswith('/customXml'):
                        ct_root.remove(el)
                files['[Content_Types].xml'] = etree.tostring(ct_root, xml_declaration=True,
                                                               encoding='UTF-8', standalone=True)
            print(f'  [fix_pptx_ooxml] Fix #6: Stripped SharePoint metadata ({len(custom_parts)} customXml parts)')
            any_fixed = True

    # ------------------------------------------------------------------ #
    # 7. docProps/app.xml stale/wrong (Slides/Notes/HiddenSlides counts, #
    #    TitlesOfParts) - carried over unmodified from whichever source  #
    #    template's own app.xml the build's working directory started   #
    #    from (e.g. science-example.pptx's own 17-slide app.xml), never #
    #    regenerated to describe the actual assembled deck. Confirmed   #
    #    11 Jul 2026 (Round 9) by diffing against a working, PowerPoint-#
    #    native file: the working file's app.xml has Slides/Notes counts#
    #    and a TitlesOfParts vector matching its real 11 slides exactly;#
    #    this build's had <Slides>17</Slides>, <Notes>9</Notes> and a   #
    #    TitlesOfParts vector describing a different, unrelated deck.   #
    #    PowerPoint cross-validates this summary info against the       #
    #    package and flags the mismatch as corruption on open.          #
    # ------------------------------------------------------------------ #
    app_key = 'docProps/app.xml'
    pres_key = 'ppt/presentation.xml'
    if app_key in files and pres_key in files:
        slide_files = sorted(
            (n for n in files if re.match(r'ppt/slides/slide\d+\.xml$', n)),
            key=lambda n: int(re.search(r'\d+', n).group())
        )
        notes_files = [n for n in files if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', n)]
        pres_xml = files[pres_key].decode('utf-8')
        n_hidden = len(re.findall(r'<p:sldId\b[^>]*\bshow="0"', pres_xml))

        P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
        A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
        titles = []
        for sf in slide_files:
            try:
                sroot = etree.fromstring(files[sf])
            except Exception:
                titles.append('PowerPoint Presentation')
                continue
            title_text = None
            for sp in sroot.iter(f'{{{P_NS}}}sp'):
                ph = sp.find(f'.//{{{P_NS}}}nvSpPr/{{{P_NS}}}nvPr/{{{P_NS}}}ph')
                if ph is not None and ph.get('type') == 'title':
                    runs = sp.findall(f'.//{{{A_NS}}}t')
                    title_text = ''.join(r.text or '' for r in runs).strip()
                    break
            titles.append(title_text if title_text else 'PowerPoint Presentation')

        app_xml = files[app_key].decode('utf-8')
        old_slides_m = re.search(r'<Slides>(\d+)</Slides>', app_xml)
        old_notes_m = re.search(r'<Notes>(\d+)</Notes>', app_xml)
        old_hidden_m = re.search(r'<HiddenSlides>(\d+)</HiddenSlides>', app_xml)
        needs_fix = (
            old_slides_m is None or int(old_slides_m.group(1)) != len(slide_files)
            or old_notes_m is None or int(old_notes_m.group(1)) != len(notes_files)
            or old_hidden_m is None or int(old_hidden_m.group(1)) != n_hidden
        )
        if needs_fix:
            fonts = ['Aptos', 'Arial', 'Calibri', 'Sassoon Infant Rg', 'Sassoon Primary Rg',
                     'Segoe UI', 'Twinkl Cursive Looped', 'Twinkl Cursive Looped Light']
            vt = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
            heading_pairs = (
                f'<HeadingPairs><vt:vector size="6" baseType="variant" xmlns:vt="{vt}">'
                f'<vt:variant><vt:lpstr>Fonts Used</vt:lpstr></vt:variant><vt:variant><vt:i4>{len(fonts)}</vt:i4></vt:variant>'
                f'<vt:variant><vt:lpstr>Theme</vt:lpstr></vt:variant><vt:variant><vt:i4>1</vt:i4></vt:variant>'
                f'<vt:variant><vt:lpstr>Slide Titles</vt:lpstr></vt:variant><vt:variant><vt:i4>{len(titles)}</vt:i4></vt:variant>'
                f'</vt:vector></HeadingPairs>'
            )
            total = len(fonts) + 1 + len(titles)
            lpstrs = ''.join(f'<vt:lpstr>{esc}</vt:lpstr>' for esc in
                              [f.replace('&', '&amp;').replace('<', '&lt;') for f in fonts]
                              + ['office theme']
                              + [t.replace('&', '&amp;').replace('<', '&lt;') for t in titles])
            titles_of_parts = f'<TitlesOfParts><vt:vector size="{total}" baseType="lpstr" xmlns:vt="{vt}">{lpstrs}</vt:vector></TitlesOfParts>'

            app_xml = re.sub(r'<Slides>\d+</Slides>', f'<Slides>{len(slide_files)}</Slides>', app_xml) \
                if '<Slides>' in app_xml else app_xml.replace('</PresentationFormat>', f'</PresentationFormat><Slides>{len(slide_files)}</Slides>')
            app_xml = re.sub(r'<Notes>\d+</Notes>', f'<Notes>{len(notes_files)}</Notes>', app_xml) \
                if '<Notes>' in app_xml else app_xml.replace('</Slides>', f'</Slides><Notes>{len(notes_files)}</Notes>')
            app_xml = re.sub(r'<HiddenSlides>\d+</HiddenSlides>', f'<HiddenSlides>{n_hidden}</HiddenSlides>', app_xml) \
                if '<HiddenSlides>' in app_xml else app_xml.replace('</Notes>', f'</Notes><HiddenSlides>{n_hidden}</HiddenSlides>')
            app_xml = re.sub(r'<HeadingPairs>.*?</HeadingPairs>', heading_pairs, app_xml, flags=re.S)
            app_xml = re.sub(r'<TitlesOfParts>.*?</TitlesOfParts>', titles_of_parts, app_xml, flags=re.S)

            files[app_key] = app_xml.encode('utf-8')
            print(f'  [fix_pptx_ooxml] Fix #7: Regenerated docProps/app.xml '
                  f'(Slides {old_slides_m.group(1) if old_slides_m else "?"}→{len(slide_files)}, '
                  f'Notes {old_notes_m.group(1) if old_notes_m else "?"}→{len(notes_files)}, '
                  f'HiddenSlides {old_hidden_m.group(1) if old_hidden_m else "?"}→{n_hidden})')
            any_fixed = True

    # ------------------------------------------------------------------ #
    # 8. Ghost slide IDs in p14:sectionLst (Sections panel data) —        #
    #    presentation.xml carries a <p14:sectionLst> left over from       #
    #    whichever source template the build started from, listing       #
    #    section membership by sldId. When the working directory's       #
    #    source template (e.g. science-example.pptx) had a different,    #
    #    larger slide set at some point, its sectionLst references       #
    #    sldIds that don't exist in the real, assembled <p:sldIdLst>.     #
    #    PowerPoint validates every id in sectionLst against sldIdLst on  #
    #    open and throws the repair dialog on any that don't resolve.    #
    #    Confirmed 11 Jul 2026 (independently, via Claude Code diffing    #
    #    Claude's v9 output against Innes's own PowerPoint-repaired      #
    #    file): v9's sectionLst had 13 ghost ids (328, 326, 2079-2092)   #
    #    none of which existed in the real 11-slide deck (ids 256-266);  #
    #    the repaired file's sectionLst only listed the 11 real ids.     #
    #    Fix: drop any <p14:sldId> in any section whose id isn't in the  #
    #    real sldIdLst. Never invents or reorders — only removes ghosts. #
    # ------------------------------------------------------------------ #
    if pres_key in files:
        pres_xml = files[pres_key].decode('utf-8')
        real_ids_ordered = re.findall(r'<p:sldId\b[^>]*\bid="(\d+)"', pres_xml)
        real_ids = set(real_ids_ordered)
        sec_m = re.search(r'<p14:sectionLst.*?</p14:sectionLst>', pres_xml, re.S)
        if sec_m and real_ids:
            sec_xml = sec_m.group(0)
            listed_ids = set(re.findall(r'<p14:sldId id="(\d+)"/>', sec_xml))
            ghost_ids = listed_ids - real_ids
            orphan_ids = [i for i in real_ids_ordered if i not in listed_ids]

            new_sec_xml = sec_xml
            for gid in ghost_ids:
                new_sec_xml = new_sec_xml.replace(f'<p14:sldId id="{gid}"/>', '')

            if orphan_ids:
                # Real slides not claimed by any section (left behind once ghosts
                # are removed, or never had a section entry at all) get appended
                # to the last section's sldIdLst, in deck order, so every real
                # slide is accounted for exactly once - matching how PowerPoint's
                # own repair reconciles this list.
                sections = list(re.finditer(r'<p14:sldIdLst>.*?</p14:sldIdLst>', new_sec_xml, re.S))
                if sections:
                    last = sections[-1].group(0)
                    insert = ''.join(f'<p14:sldId id="{i}"/>' for i in orphan_ids)
                    fixed_last = last.replace('</p14:sldIdLst>', insert + '</p14:sldIdLst>')
                    new_sec_xml = new_sec_xml[:sections[-1].start()] + fixed_last + new_sec_xml[sections[-1].end():]

            if new_sec_xml != sec_xml:
                pres_xml = pres_xml.replace(sec_xml, new_sec_xml)
                files[pres_key] = pres_xml.encode('utf-8')
                msg = []
                if ghost_ids:
                    msg.append(f'removed {len(ghost_ids)} ghost id(s) {sorted(ghost_ids, key=int)}')
                if orphan_ids:
                    msg.append(f'reclaimed {len(orphan_ids)} orphaned real id(s) {orphan_ids} into last section')
                print(f'  [fix_pptx_ooxml] Fix #8: p14:sectionLst — ' + '; '.join(msg))
                any_fixed = True

    # ------------------------------------------------------------------ #
    # Write output                                                         #
    # ------------------------------------------------------------------ #
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)

    if any_fixed:
        print(f"  [fix_pptx_ooxml] Done → {output_path}")
    else:
        print(f"  [fix_pptx_ooxml] No issues found — {output_path} unchanged")

    return any_fixed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    # Process every path argument in place.
    # Formerly treated argv[2] as an output path — that corrupted multi-file
    # glob calls by overwriting file 2 with the fixed content of file 1.
    for in_path in sys.argv[1:]:
        print(f"[fix_pptx_ooxml] Processing: {in_path}")
        fix_pptx(in_path)
