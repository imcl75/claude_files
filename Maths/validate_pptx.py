"""
validate_pptx.py — checks a PPTX for all known causes of PowerPoint repair prompts.
Usage: python3 validate_pptx.py path/to/file.pptx
Prints every violation found. Zero violations = no repair prompt.
"""
import sys, zipfile, re
from lxml import etree

def validate(path):
    violations = []

    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        files = {n: z.read(n) for n in names if not n.endswith('/')}

    # ── 1. Orphaned relationships ─────────────────────────────────────────────
    # Every Target in every _rels file must resolve to an actual file in the ZIP
    for name, data in files.items():
        if '/_rels/' not in name and not name.endswith('.rels'):
            continue
        rels_str = data.decode('utf-8', errors='ignore')
        for m in re.finditer(r'Target="([^"]+)"', rels_str):
            target = m.group(1)
            if target.startswith('http') or target.startswith('#'):
                continue  # external or internal anchor — skip
            # Resolve relative path
            base_dir = name.rsplit('/', 1)[0].replace('_rels', '').rstrip('/')
            if target.startswith('/'):
                resolved = target.lstrip('/')
            else:
                parts = (base_dir + '/' + target).split('/')
                stack = []
                for p in parts:
                    if p == '..':
                        if stack: stack.pop()
                    elif p and p != '.':
                        stack.append(p)
                resolved = '/'.join(stack)
            if resolved and resolved not in names:
                violations.append(
                    f'ORPHANED_REL: {name} → Target="{target}" resolves to '
                    f'"{resolved}" which does not exist')

    # ── 2. Missing content type declarations ──────────────────────────────────
    ct_xml = files.get('[Content_Types].xml', b'').decode('utf-8', errors='ignore')
    # Build set of declared extensions and part names
    declared_exts  = set(re.findall(r'Extension="([^"]+)"', ct_xml))
    declared_parts = set(re.findall(r'PartName="([^"]+)"', ct_xml))
    SKIP = {'[Content_Types].xml', '_rels/.rels'}
    for name in files:
        if name in SKIP or name.endswith('.rels') or '/_rels/' in name:
            continue
        part_name = '/' + name
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        if part_name not in declared_parts and ext not in declared_exts:
            violations.append(f'MISSING_CONTENT_TYPE: "{name}" (ext=.{ext}) '
                               f'not in [Content_Types].xml')

    # ── 3. Duplicate slide IDs in presentation.xml ───────────────────────────
    prs_str = files.get('ppt/presentation.xml', b'').decode('utf-8', errors='ignore')
    sld_ids = re.findall(r'<p:sldId\b[^>]*\bid="(\d+)"', prs_str)
    seen_ids = set()
    for sid in sld_ids:
        if sid in seen_ids:
            violations.append(f'DUPLICATE_SLD_ID: id="{sid}" appears more than once '
                               f'in ppt/presentation.xml sldIdLst')
        seen_ids.add(sid)

    # ── 4. Duplicate rIds within any single _rels file ────────────────────────
    for name, data in files.items():
        if not (name.endswith('.rels') or '/_rels/' in name):
            continue
        rels_str = data.decode('utf-8', errors='ignore')
        rids = re.findall(r'\bId="([^"]+)"', rels_str)
        seen_rids = set()
        for rid in rids:
            if rid in seen_rids:
                violations.append(f'DUPLICATE_RID: Id="{rid}" appears more than once '
                                   f'in {name}')
            seen_rids.add(rid)

    # ── 5. Notes slide references without a corresponding file ───────────────
    for name, data in files.items():
        if not (name.endswith('.rels') or '/_rels/' in name):
            continue
        rels_str = data.decode('utf-8', errors='ignore')
        for m in re.finditer(r'<Relationship[^>]+>', rels_str):
            rel = m.group()
            if 'notesSlide' in rel:
                target_m = re.search(r'Target="([^"]+)"', rel)
                if target_m:
                    target = target_m.group(1)
                    base_dir = name.rsplit('/', 1)[0].replace('_rels', '').rstrip('/')
                    parts = (base_dir + '/' + target).split('/')
                    stack = []
                    for p in parts:
                        if p == '..':
                            if stack: stack.pop()
                        elif p and p != '.':
                            stack.append(p)
                    resolved = '/'.join(stack)
                    if resolved not in names:
                        violations.append(
                            f'ORPHANED_NOTES_REF: {name} references '
                            f'notesSlide "{target}" → "{resolved}" which does not exist')

    # ── 6. Slide layout references that don't exist ───────────────────────────
    for name, data in files.items():
        if not (name.endswith('.rels') or '/_rels/' in name):
            continue
        if 'slides/_rels/' not in name:
            continue
        rels_str = data.decode('utf-8', errors='ignore')
        for m in re.finditer(r'Target="(\.\./slideLayouts/[^"]+)"', rels_str):
            target = m.group(1)
            base_dir = name.rsplit('/', 1)[0].replace('_rels', '').rstrip('/')
            parts = (base_dir + '/' + target).split('/')
            stack = []
            for p in parts:
                if p == '..':
                    if stack: stack.pop()
                elif p and p != '.':
                    stack.append(p)
            resolved = '/'.join(stack)
            if resolved not in names:
                violations.append(
                    f'MISSING_LAYOUT: {name} references "{target}" → '
                    f'"{resolved}" which does not exist')

    # ── 7. Slide files referenced in presentation.xml but not present ─────────
    prs_rels = files.get('ppt/_rels/presentation.xml.rels', b'').decode('utf-8', errors='ignore')
    for m in re.finditer(r'Target="(slides/slide\d+\.xml)"', prs_rels):
        target = 'ppt/' + m.group(1)
        if target not in names:
            violations.append(f'MISSING_SLIDE_FILE: presentation rels references '
                               f'"{target}" which does not exist')

    # ── 8. Shared notesSlide references (two slides pointing to same file) ────
    # PowerPoint treats this as an error requiring repair — the validator's
    # orphaned-ref check misses this because the file exists, just shared.
    notes_target_to_slides = {}
    for name, data in files.items():
        if not re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels$', name):
            continue
        rels_str = data.decode('utf-8', errors='ignore')
        slide_num = re.search(r'slide(\d+)', name).group(1)
        for m in re.finditer(r'Target="(\.\./notesSlides/[^"]+)"', rels_str):
            target = m.group(1)
            notes_target_to_slides.setdefault(target, []).append(f'slide{slide_num}')
    for target, slides in notes_target_to_slides.items():
        if len(slides) > 1:
            violations.append(
                f'SHARED_NOTES_REF: {target} is referenced by multiple slides: '
                f'{sorted(slides)} — PowerPoint will repair this')

    # ── Report ────────────────────────────────────────────────────────────────
    print(f'\n{"="*60}')
    print(f'Validating: {path}')
    print(f'{"="*60}')
    if violations:
        print(f'FOUND {len(violations)} VIOLATION(S):')
        for v in violations:
            print(f'  ✗ {v}')
    else:
        print('✓ No violations found — should open without repair prompt')
    print()
    return violations

if __name__ == '__main__':
    for path in sys.argv[1:]:
        validate(path)
