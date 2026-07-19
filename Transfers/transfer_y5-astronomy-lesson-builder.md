# Transfer: Y5 Astronomy Science Lesson Builder

**Generated:** 2026-07-19
**Originating focus:** Building `out_L5.pptx` (Y5 Astronomy Lesson 5) to match Innes's hand-corrected IM reference exactly, then establishing a reliable slide-cloning workflow for remaining lessons.
**Skill in use:** enquiry-lesson-builder

---

## Status

L5 deck is complete and approved — 11 slides. Slides 1, 3, 7, 8 were cloned directly from Innes's uploaded reference files. Slide 9 (a broken programmatic version) was deleted. Final file is `out_L5_final.pptx`. The builder script (`build_science_lesson.py`) still has its old `build_kq_challenge()` function but it is now bypassed for L5. The remaining lesson decks (L1–L4, L6–L14) have not been started.

A lessons-learned document has been written and is in outputs. This MUST be read before starting any new lesson deck.

---

## What's been produced

- `/mnt/user-data/outputs/out_L5_final.pptx` — **final, approved, 11 slides**
- `/mnt/user-data/outputs/build_science_lesson.py` — builder script (still contains old programmatic slide builders — see decisions below)
- `/mnt/user-data/outputs/y5_astronomy_mtp.json` — MTP JSON driving lesson content
- `/mnt/user-data/outputs/science_lesson_builder_lessons_learned.md` — **critical, read this first**

---

## Decisions locked in

- **Clone, don't build** — if Innes has a hand-corrected reference slide, clone it byte-for-byte. Never try to reproduce it programmatically.
- **Media renaming is mandatory** — when inserting any external slide, rename ALL its media files with `_{10 random digits}` suffix before inserting. No exceptions.
- **Slide order from presentation.xml only** — never use alphabetical filename sort to determine slide number.
- **Post-processing = `_normalise_fonts()` only** — no blanket position/size fixes. All other fixes must target specific shapes on specific slides.
- **Slide 9 deleted** — Innes replaced it with a slide 10 (phases layout) which is now slide 9 in the final deck. The programmatic phases builder in the script is no longer used for L5.
- **All media in `out_L5_final.pptx` already has unique 10-digit suffixes** — safe to insert further slides without conflict.

## Specific user requirements

> "what don't you name everything on every single slide with a human readable name and add a string of 10 random numbers to the end so this can't happen"

> "remake it IDENTICALLY" — Innes's instruction for every cloned slide. Do not alter content, position, size, font, or anything else.

> "there also needs to be some logic created around slides with images and selecting the right layout depending on the purpose of having the image on the slide in the first place"

Image layout logic (from lessons-learned doc):
- **A. Full-bleed** — image fills slide, minimal text overlay
- **B. Split-screen** — image half, text half (cx ≈ 5500000–6000000)
- **C. Illustration** — image smaller, secondary to text, captioned
- **D. Diagram/labelled** — image is main content, labels around it (phases layout: image cx=9035107, right-column text at x=9361172)
- **E. Icon/branding** — small corner image (cx ≈ 400000–800000)

Decision driver: what is the image *for*? Main content → D/A. Equal to text → B. Supporting text → C. Decorative → E.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/user-data/outputs/out_L5_final.pptx` | Final approved | No |
| `/mnt/user-data/outputs/build_science_lesson.py` | Active builder | No |
| `/mnt/user-data/outputs/y5_astronomy_mtp.json` | Current MTP data | No |
| `/mnt/user-data/outputs/science_lesson_builder_lessons_learned.md` | Reference doc | No |

Innes will upload reference slides for other lessons as needed — use the clone workflow each time.

---

## The clone_slide_from_file workflow (implement this as a reusable function)

```python
def clone_slide_from_file(src_pptx_path, deck_path, target_slide_number):
    import zipfile, lxml.etree as et, os, random, string, re

    P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    def rand10():
        return ''.join(random.choices(string.digits, k=10))

    # 1. Read source slide (always slide 1 of the source file)
    with zipfile.ZipFile(src_pptx_path, 'r') as z:
        src_slides = sorted([f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')])
        slide_xml = z.read(src_slides[0])
        rels_path = src_slides[0].replace('slides/slide','slides/_rels/slide').replace('.xml','.xml.rels')
        slide_rels_bytes = z.read(rels_path) if rels_path in z.namelist() else b''
        src_media = {f: z.read(f) for f in z.namelist() if f.startswith('ppt/media/')}

    # 2. Rename ALL src media with unique suffixes
    rename_map = {}
    for old_path in src_media:
        ext = os.path.splitext(old_path)[1]
        label = re.sub(r'\d+', '', os.path.splitext(os.path.basename(old_path))[0]).strip('_') or 'media'
        rename_map[old_path] = f'ppt/media/{label}_{rand10()}{ext}'

    # 3. Update rels to point to renamed media
    if slide_rels_bytes:
        rels_root = et.fromstring(slide_rels_bytes)
        for rel in rels_root:
            target = rel.get('Target', '')
            if '../media/' in target:
                old = f'ppt/media/{target.split("../media/")[-1]}'
                if old in rename_map:
                    rel.set('Target', f'../media/{os.path.basename(rename_map[old])}')
        slide_rels_bytes = et.tostring(rels_root, xml_declaration=True, encoding='UTF-8', standalone=True)

    # 4. Find target slide filename from presentation.xml
    with zipfile.ZipFile(deck_path, 'r') as z:
        prs = et.fromstring(z.read('ppt/presentation.xml'))
        rels = et.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rid_to_target = {r.get('Id'): r.get('Target') for r in rels}
    ordered = [rid_to_target[s.get(f'{{{R}}}id')] for s in prs.find(f'{{{P}}}sldIdLst')]
    target_file = f'ppt/{ordered[target_slide_number - 1]}'
    target_rels = target_file.replace('slides/slide','slides/_rels/slide').replace('.xml','.xml.rels')

    # 5. Write new deck
    tmp = deck_path + '.tmp'
    with zipfile.ZipFile(deck_path, 'r') as zin:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                fn = item.filename
                if fn == target_file:
                    zout.writestr(item, slide_xml)
                elif fn == target_rels:
                    zout.writestr(item, slide_rels_bytes)
                else:
                    zout.writestr(item, zin.read(fn))
            for old_path, data in src_media.items():
                zout.writestr(rename_map[old_path], data)
    os.replace(tmp, deck_path)
```

---

## Open questions / blockers

- Remaining lesson decks L1–L4, L6–L14 not started. Each will need its MTP JSON verified and slides built or cloned.
- Innes may have hand-corrected reference slides for some slides in other lessons — ask at the start of each lesson build which slides he has references for.
- The builder script's programmatic slide builders (kq_challenge, phases, etc.) may need the image-layout logic applied before use on new lessons.

## Immediate next step

Read `science_lesson_builder_lessons_learned.md` from GitHub (or outputs). Ask Innes which lesson to build next and whether he has any hand-corrected reference slides for it. Fetch `build_science_lesson.py` and `y5_astronomy_mtp.json` from GitHub. Add `clone_slide_from_file()` to the builder script before doing anything else.

