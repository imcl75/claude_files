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
    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    fix_pptx(in_path, out_path)
