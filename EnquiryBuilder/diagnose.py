import zipfile, re
from lxml import etree
from collections import Counter

def diagnose_pptx(path):
    issues = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()

        bad_media = [n for n in names if re.match(r'ppt/media/media\d+\.mp4$', n)]
        if bad_media:
            issues.append(f'FIX1: Non-standard media names: {bad_media}')

        ns_rels = [n for n in names if re.match(r'ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels$', n)]
        for rf in ns_rels:
            content = z.read(rf).decode('utf-8')
            targets = re.findall(r'Type="[^"]*slide[^"]*"\s+Target="([^"]+)"', content)
            if '../slides/slide1.xml' in content and 'notesSlide1' not in rf:
                issues.append(f'FIX2: Wrong notesSlide back-ref in {rf}')

        slides = [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)]
        for sname in slides:
            content = z.read(sname).decode('utf-8')
            empty_runs = re.findall(r'<a:r>\s*</a:r>', content)
            if empty_runs:
                issues.append(f'FIX3: {len(empty_runs)} empty <a:r> in {sname}')

        nm_rels = [n for n in names if 'notesMasters/_rels' in n and n.endswith('.rels')]
        for rf in nm_rels:
            content = z.read(rf).decode('utf-8')
            if 'theme1.xml' in content:
                issues.append(f'FIX4: notesMaster references theme1.xml (should be theme2.xml) in {rf}')

        if 'ppt/theme/theme2.xml' not in names:
            if any('notesMasters' in n for n in names):
                issues.append('FIX5: theme2.xml missing but notesMaster exists')

        if 'ppt/_rels/presentation.xml.rels' in names:
            prels = z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')
            non_numeric = re.findall(r'Id="(rId[A-Za-z][A-Za-z0-9]*)"', prels)
            if non_numeric:
                issues.append(f'FIX6: Non-numeric rIds in presentation.xml.rels: {non_numeric}')

        custom_parts = [n for n in names if n.startswith('customXml/')]
        if custom_parts:
            SHAREPOINT_MARKERS = ['schemas.microsoft.com/sharepoint','schemas.microsoft.com/office/2006/metadata','schemas.microsoft.com/office/infopath']
            for part in custom_parts:
                if part.endswith('.xml') and '_rels' not in part:
                    content = z.read(part).decode('utf-8', errors='ignore')
                    if any(m in content for m in SHAREPOINT_MARKERS):
                        issues.append(f'FIX7: SharePoint customXml metadata ({len(custom_parts)} parts)')
                        break

        broken_rels = []
        for rf in [n for n in names if n.endswith('.rels')]:
            content = z.read(rf).decode('utf-8')
            for target in re.findall(r'Target="([^"]+)"', content):
                if target.startswith('http') or target.startswith('#') or target.startswith('mailto'):
                    continue
                base = '/'.join(rf.replace('_rels/', '').split('/')[:-1]) + '/'
                if target.startswith('../'):
                    parts_list = base.rstrip('/').split('/')
                    for p in target.split('/'):
                        if p == '..':
                            if parts_list: parts_list.pop()
                        else:
                            parts_list.append(p)
                    resolved = '/'.join(parts_list)
                else:
                    resolved = base + target
                if resolved not in names:
                    broken_rels.append((rf, target))
        if broken_rels:
            issues.append(f'BROKEN RELS ({len(broken_rels)}): {broken_rels[:10]}')

        for sname in slides:
            xml = z.read(sname)
            root = etree.fromstring(xml)
            ids = [el.get('id') for el in root.xpath('.//*[local-name()="cNvPr"]')]
            dupes = [k for k, v in Counter(ids).items() if v > 1]
            if dupes:
                issues.append(f'DUPE SHAPE IDs in {sname}: {dupes[:5]}')

        prs_xml = z.read('ppt/presentation.xml')
        prs_root = etree.fromstring(prs_xml)
        ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
        sld_id_count = len(prs_root.findall('.//p:sldIdLst/p:sldId', ns))
        actual_count = len(slides)
        if sld_id_count != actual_count:
            issues.append(f'SLIDE COUNT MISMATCH: sldIdLst={sld_id_count}, actual files={actual_count}')

        for sname in slides:
            xml = z.read(sname)
            root = etree.fromstring(xml)
            shape_ids = {el.get('id') for el in root.xpath('.//*[local-name()="cNvPr"]')}
            for spid in root.xpath('.//*[local-name()="spTgt"]/@spid'):
                if spid not in shape_ids:
                    issues.append(f'ANIM TARGET MISSING: {sname} spTgt spid={spid} not found (shape ids on slide: {sorted(shape_ids)})')

    return issues

import sys
issues = diagnose_pptx(sys.argv[1])
if issues:
    print(f'Found {len(issues)} issue(s):')
    for i in issues:
        print(f'  - {i}')
else:
    print('No known issues detected')
