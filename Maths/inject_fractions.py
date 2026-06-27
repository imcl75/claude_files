"""
inject_fractions.py  —  inserts 2 fractions slides into a teaching PPTX
after slide 5 (WM Q&A).

Usage: python3 inject_fractions.py <teaching_pptx> <lesson_num>

Source PPTX: /home/claude/T6W5_Fractions_Teaching.pptx
  Slide indices (1-based) per lesson:
    L17 (Mon): slides 1 (I→M), 2 (M→I)
    L18 (Tue): slides 3 (I→M), 4 (M→I)
    L19 (Wed): slides 5 (I→M), 6 (M→I)
"""
import sys, re, zipfile, shutil, os

FRACTIONS_SRC = '/home/claude/T6W5_Fractions_Teaching.pptx'

# Lesson → 1-based slide indices in fractions source
LESSON_SLIDES = {
    17: [1, 2],
    18: [3, 4],
    19: [5, 6],
}

INSERT_AFTER = 5   # insert after this many slides (WM Q&A is slide 5)

def inject(teaching_pptx, lesson_num):
    frac_slide_nums = LESSON_SLIDES[lesson_num]

    with zipfile.ZipFile(teaching_pptx) as z:
        t = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    with zipfile.ZipFile(FRACTIONS_SRC) as z:
        f = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}

    # ── Current state of teaching PPTX ───────────────────────────────────────
    existing_slide_nums = sorted(
        int(re.search(r'slide(\d+)', n).group(1))
        for n in t if re.match(r'ppt/slides/slide\d+\.xml$', n))
    max_slide_num = max(existing_slide_nums)

    existing_media = {n.split('/')[-1] for n in t if n.startswith('ppt/media/')}

    prs_rels = t['ppt/_rels/presentation.xml.rels'].decode()
    existing_rids = [int(m) for m in re.findall(r'rId(\d+)', prs_rels)]
    max_rid = max(existing_rids, default=0)

    prs_str = t['ppt/presentation.xml'].decode()
    existing_sld_ids = [int(m) for m in re.findall(r'<p:sldId\b[^>]*\bid="(\d+)"', prs_str)]
    max_sld_id = max(existing_sld_ids, default=255)

    SLIDE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'
    new_prs_rels_entries = []
    new_sldid_entries = []
    new_ct_entries = []

    for frac_sn in frac_slide_nums:
        max_slide_num += 1
        max_rid       += 1
        max_sld_id    += 1

        new_sn  = max_slide_num
        new_rid = f'rIdFr{max_rid}'
        new_id  = max_sld_id

        # ── Slide XML (unchanged) ──────────────────────────────────────────
        t[f'ppt/slides/slide{new_sn}.xml'] = f[f'ppt/slides/slide{frac_sn}.xml']

        # ── Rels: copy + remap media names + fix layout ───────────────────
        rels = f[f'ppt/slides/_rels/slide{frac_sn}.xml.rels'].decode()
        rels = re.sub(r'Target="\.\./slideLayouts/slideLayout\d+\.xml"',
                      'Target="../slideLayouts/slideLayout13.xml"', rels)
        rels = re.sub(r'<Relationship[^>]+notesSlide[^>]+/>', '', rels)

        # Remap media filenames that conflict
        for m in re.finditer(r'Target="\.\./media/([^"]+)"', rels):
            orig_fname = m.group(1)
            src_key    = f'ppt/media/{orig_fname}'
            if src_key not in f:
                continue
            img_data = f[src_key]
            candidate = orig_fname
            if candidate in existing_media:
                base, ext = orig_fname.rsplit('.', 1)
                n = 0
                while candidate in existing_media:
                    n += 1
                    candidate = f'{base}_inj{n}.{ext}'
                rels = rels.replace(f'../media/{orig_fname}', f'../media/{candidate}')
            existing_media.add(candidate)
            t[f'ppt/media/{candidate}'] = img_data

        t[f'ppt/slides/_rels/slide{new_sn}.xml.rels'] = rels.encode()

        # ── Presentation rels entry ────────────────────────────────────────
        new_prs_rels_entries.append(
            f'<Relationship Id="{new_rid}" Type="{SLIDE_REL}" '
            f'Target="slides/slide{new_sn}.xml"/>')

        # ── sldId entry ────────────────────────────────────────────────────
        new_sldid_entries.append(
            f'<p:sldId id="{new_id}" r:id="{new_rid}"/>')

        # ── Content type entry ─────────────────────────────────────────────
        new_ct_entries.append(
            f'<Override PartName="/ppt/slides/slide{new_sn}.xml" '
            f'ContentType="application/vnd.openxmlformats-officedocument.'
            f'presentationml.slide+xml"/>')

    # ── Insert sldId entries after 5th existing slide entry ──────────────────
    sld_id_pat = re.compile(r'<p:sldId\b[^/]*/>')
    matches = list(sld_id_pat.finditer(prs_str))
    if len(matches) >= INSERT_AFTER:
        insert_pos = matches[INSERT_AFTER - 1].end()
    else:
        insert_pos = matches[-1].end()
    new_block = ''.join(new_sldid_entries)
    prs_str = prs_str[:insert_pos] + new_block + prs_str[insert_pos:]

    # ── Update presentation rels ──────────────────────────────────────────────
    prs_rels = prs_rels.replace(
        '</Relationships>', ''.join(new_prs_rels_entries) + '</Relationships>')

    # ── Update content types ──────────────────────────────────────────────────
    ct_str = t['[Content_Types].xml'].decode()
    ct_str = ct_str.replace('</Types>', ''.join(new_ct_entries) + '</Types>')

    t['ppt/presentation.xml']            = prs_str.encode()
    t['ppt/_rels/presentation.xml.rels'] = prs_rels.encode()
    t['[Content_Types].xml']             = ct_str.encode()

    # ── Write ─────────────────────────────────────────────────────────────────
    tmp = teaching_pptx + '.frac_tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in t.items():
            z.writestr(name, data)
    shutil.move(tmp, teaching_pptx)

    total = len([n for n in t if re.match(r'ppt/slides/slide\d+\.xml$', n)])
    print(f'  Injected fractions slides {frac_slide_nums} → {teaching_pptx} ({total} slides total)')

if __name__ == '__main__':
    teaching_pptx = sys.argv[1]
    lesson_num    = int(sys.argv[2])
    inject(teaching_pptx, lesson_num)
