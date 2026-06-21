#!/usr/bin/env python3
"""Post-process geography lesson PPTXs to fix layout text."""
import zipfile, re, os, shutil

PPTXS = [
    '/home/claude/T6W4_-_Lesson_1_-_Geographers_-_Locating_Brazil.pptx',
    '/home/claude/T6W4_-_Lesson_2_-_Geographers_-_Brazil_Physical_Geography.pptx',
    '/home/claude/T6W4_-_Lesson_3_-_Geographers_-_England_Physical_Geography.pptx',
]

LAYOUT_PATCHES = {
    'Enquiry - Being a writer': 'Enquiry — Being a Geographer',
    'Enquiry - Being a Writer': 'Enquiry — Being a Geographer',
}

for pptx_path in PPTXS:
    tmp = pptx_path + '.tmp'
    with zipfile.ZipFile(pptx_path, 'r') as zin:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith('ppt/slideLayouts/') and item.filename.endswith('.xml'):
                    text = data.decode('utf-8')
                    for old, new in LAYOUT_PATCHES.items():
                        text = text.replace(old, new)
                    data = text.encode('utf-8')
                zout.writestr(item, data)
    os.replace(tmp, pptx_path)
    print(f'Patched: {os.path.basename(pptx_path)}')

print('Done.')
