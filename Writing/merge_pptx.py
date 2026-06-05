"""
merge_pptx.py — Merge multiple PPTX files into one at the zip level.
All inputs must share the same media assets (same base PPTX).
Usage: python3 merge_pptx.py out.pptx file1.pptx file2.pptx ...
"""
import os, re, shutil, sys, zipfile

REL_SLD = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'
RELS_NS  = 'http://schemas.openxmlformats.org/package/2006/relationships'

def _strip_slide_rels(rels_xml):
    """Remove any Relationship elements whose Target points to a slide file."""
    return re.sub(
        r'<Relationship\s[^>]*Target="slides/slide\d+[^"]*"[^>]*/>', 
        '', rels_xml
    )

def merge(output_path, input_files):
    tmp = '/tmp/_pptx_merge'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)

    # Unpack first lesson as the base
    with zipfile.ZipFile(input_files[0]) as z:
        z.extractall(tmp)

    slides_dir = f'{tmp}/ppt/slides'
    rels_dir   = f'{tmp}/ppt/slides/_rels'

    # Count slides already in base (from lesson 1)
    existing = sorted(
        [f for f in os.listdir(slides_dir) if re.match(r'slide\d+\.xml$', f)],
        key=lambda x: int(re.search(r'\d+', x).group())
    )
    next_idx = len(existing) + 1

    # Append slides from each subsequent lesson
    for pptx_path in input_files[1:]:
        src_tmp = f'{tmp}/_src'
        shutil.rmtree(src_tmp, ignore_errors=True)
        os.makedirs(src_tmp)
        with zipfile.ZipFile(pptx_path) as z:
            z.extractall(src_tmp)

        src_slides = sorted(
            [f for f in os.listdir(f'{src_tmp}/ppt/slides')
             if re.match(r'slide\d+\.xml$', f)],
            key=lambda x: int(re.search(r'\d+', x).group())
        )

        for src_name in src_slides:
            src_xml  = f'{src_tmp}/ppt/slides/{src_name}'
            src_rels = f'{src_tmp}/ppt/slides/_rels/{src_name}.rels'
            dst_name = f'slide{next_idx}.xml'
            shutil.copy(src_xml, os.path.join(slides_dir, dst_name))
            if os.path.exists(src_rels):
                shutil.copy(src_rels, os.path.join(rels_dir, f'{dst_name}.rels'))
            next_idx += 1

        shutil.rmtree(src_tmp)

    # Enumerate all slides in final order
    all_slides = sorted(
        [f for f in os.listdir(slides_dir) if re.match(r'slide\d+\.xml$', f)],
        key=lambda x: int(re.search(r'\d+', x).group())
    )

    # Rebuild presentation.xml rels — strip ALL existing slide rels first, add clean set
    pr_path = f'{tmp}/ppt/_rels/presentation.xml.rels'
    pp_path = f'{tmp}/ppt/presentation.xml'

    prx = open(pr_path, encoding='utf-8').read()
    ppx = open(pp_path, encoding='utf-8').read()

    # Strip existing slide rels (correct regex)
    prx = _strip_slide_rels(prx)

    # Verify strip worked
    remaining = re.findall(r'Target="slides/slide\d+', prx)
    if remaining:
        print(f'WARNING: {len(remaining)} slide rels not stripped — check regex', file=sys.stderr)

    # Add clean slide rels
    new_rels = ''
    new_ids  = ''
    for i, fname in enumerate(all_slides, 1):
        rid = f'rId{100+i}'   # use high rId range to avoid collisions
        new_rels += (f'<Relationship Id="{rid}" '
                     f'Type="{REL_SLD}" '
                     f'Target="slides/{fname}"/>')
        new_ids  += f'<p:sldId id="{4100+i}" r:id="{rid}"/>'

    prx = prx.replace('</Relationships>', new_rels + '</Relationships>')
    ppx = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>',
                 f'<p:sldIdLst>{new_ids}</p:sldIdLst>',
                 ppx, flags=re.DOTALL)

    open(pr_path, 'w', encoding='utf-8').write(prx)
    open(pp_path, 'w', encoding='utf-8').write(ppx)

    # Remove notes to keep file clean
    nd = f'{tmp}/ppt/notesSlides'
    if os.path.exists(nd):
        shutil.rmtree(nd)
    os.makedirs(f'{nd}/_rels', exist_ok=True)

    # Repack
    if os.path.exists(output_path):
        os.remove(output_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(tmp):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, tmp))

    shutil.rmtree(tmp)
    total = len(all_slides)
    print(f'Merged {total} slides → {output_path}')

if __name__ == '__main__':
    merge(sys.argv[1], sys.argv[2:])
