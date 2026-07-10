# Transfer: Enquiry Lesson Builder — States of Matter full build

**Generated:** 2026-07-10
**Originating focus:** Building the enquiry-lesson-builder skill from scratch (catalogue → builder → image layouts → MTP generator → SKILL.md), culminating in a full States of Matter enquiry build as the first live run.
**Skill in use:** enquiry-lesson-builder (just saved to project)

---

## Status

The enquiry-lesson-builder skill is complete and saved to the project. All scripts are in GitHub. The builder has been tested with placeholder images and produces correct output (8 slides, right template sources, text replacement working). The first live run — States of Matter, Y4 — is the immediate next task. This means: generate the full MTP, generate all images via dall-e/Higgsfield, confirm with Innes, build all lesson PPTXs, QA, deliver as zip.

---

## What's been produced

- `EnquiryBuilder/build_science_lesson.py` — in GitHub, final. Clones slides from template sources, text replace, image embedding, clean.py integration.
- `EnquiryBuilder/slide_layouts.py` — in GitHub, final. Handles image_grid, provocation, comparison, image_right, image_left, diagram_annotated layout variants.
- `EnquiryBuilder/generate_mtp.py` — in GitHub, final. MTP JSON validator.
- `EnquiryBuilder/clean.py` — in GitHub, final. Removes orphaned media after slide clear.
- `EnquiryBuilder/SKILL.md` — in GitHub and saved as project skill `enquiry-lesson-builder`.

---

## Decisions locked in

- **Clone-and-replace only** — every slide is cloned from an actual template PPTX and only text/images replaced. Never build slides from scratch using pptxgenjs or pptxgenlib.
- **Template sources:**
  - Cover → `sci_template.pptx` slide 2
  - LO → `kq_lo_science_clean.pptx` slide 1 (accent1 shapes stripped)
  - Recall → `sci_template.pptx` slide 9
  - I Do → `sci_example.pptx` slide 13
  - We Do → `sci_example.pptx` slide 15
  - You Do → `sci_example.pptx` slide 12
  - Misconception → `sci_example.pptx` slide 16
  - Fed in Facts → `sci_template.pptx` slide 13
  - Quiz → `sci_template.pptx` slide 14
  - Learning Review → `sci_example.pptx` slide 17
  - Image layout slides (grid/provocation/comparison etc.) → blank slide from Blank layout + shapes injected
- **sci_template slide 8 is permanently retired** — never use the vertical single-pupil WWH slide
- **LO slide** — always from `kq_lo_science_clean.pptx`. Editable shapes: Title 27 (key question), TextBox 38 (lo), TextBox 39 (tib), TextBox 40 (isb).
- **Slide order** — cover always first, lo always second, learning_review always last.
- **Image generation** — dall-e for diagrams/science illustrations; Higgsfield for photographic scenes. Generate all images first, download to `/tmp/enquiry_images/`, fill `path` fields in JSON, then build.
- **Animations** — `animate_sequence` field on each slide defines the click-by-click reveal order. Images/diagrams first (thinking time), then explanatory text. Each learner on misconception slides reveals separately. Activity instructions reveal one at a time. Animation XML not yet implemented in builder — this is still to build.
- **Science strands** — Biology / Physics / Chemistry / Earth and Space Science (not "materials").
- **Lessons per enquiry** — typically 10–14.
- **Every enquiry** must include at least one `image_grid` or `provocation` slide.

---

## Specific user requirements

> "i will give you an EXAMPLE do not just build a rigid version so you can find and replace - claude needs to use its AI capability to actually show some intelligence about what is needed in each lesson. some parts will be standard."

> "if the question is 'what do these 6 substances have in common?' then claude needs to be able to put 6, correctly sized images within the slide. If the image is a provocation for a discussion, the layout will be completely different"

> "the skill also needs to have a flexible capability to integrate images and diagrams from /image-generation"

The images need to enhance understanding and stimulate discussion, not decorate slides. Layout follows learning intent, not a fixed grid.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| GitHub `EnquiryBuilder/build_science_lesson.py` | final | Fetch via github-sync at session start |
| GitHub `EnquiryBuilder/slide_layouts.py` | final | Fetch via github-sync |
| GitHub `EnquiryBuilder/generate_mtp.py` | final | Fetch via github-sync |
| GitHub `EnquiryBuilder/clean.py` | final | Fetch via github-sync |
| `Being_a_Scientist_slide_deck.pptx` | sci_template source | **Yes — re-upload** |
| `science-example.pptx` | sci_example source | **Yes — re-upload** |
| `KQ_LO.pptx` | source for kq_lo_science_clean | **Yes — re-upload** |
| `/mnt/skills/user/github-sync/SKILL.md` | has PAT | No (in skill folder) |

Note: `kq_lo_science_clean.pptx` is generated at setup time by running the cleanup script on `KQ_LO.pptx`. It is NOT in GitHub (binary PPTX). Regenerate it at session start.

---

## Setup steps at session start

```bash
# 1. Fetch scripts from GitHub
mkdir -p /home/claude/enquiry-builder
# fetch build_science_lesson.py, slide_layouts.py, generate_mtp.py, clean.py
# from imcl75/claude_files EnquiryBuilder/ using PAT from github-sync SKILL.md

# 2. Regenerate kq_lo_science_clean.pptx from uploaded KQ_LO.pptx
python3 << 'SETUP'
import zipfile, shutil, os
from lxml import etree

src = '/mnt/user-data/uploads/KQ_LO.pptx'
work = '/tmp/kqlo_clean'
shutil.rmtree(work, ignore_errors=True)
os.makedirs(work)
with zipfile.ZipFile(src) as z:
    z.extractall(work)

NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
slide_path = f'{work}/ppt/slides/slide1.xml'
tree = etree.parse(slide_path)
root = tree.getroot()

for spTree in root.iter(f'{{{NS_P}}}spTree'):
    to_delete = []
    for child in spTree:
        xml_str = etree.tostring(child, encoding='unicode')
        has_accent1 = 'accent1' in xml_str
        has_accent6 = 'accent6' in xml_str
        name = ''
        for el in child.iter():
            if 'cNvPr' in el.tag:
                name = el.get('name', '')
                break
        if (has_accent1 and not has_accent6) or 'Text Placeholder 33' in name:
            to_delete.append(child)
    for el in to_delete:
        spTree.remove(el)

tree.write(slide_path, xml_declaration=True, encoding='UTF-8', standalone=True)
dst = '/home/claude/enquiry-builder/kq_lo_science_clean.pptx'
if os.path.exists(dst): os.remove(dst)
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for r, dirs, files in os.walk(work):
        for f in files:
            full = os.path.join(r, f)
            z.write(full, os.path.relpath(full, work))
print(f"Created: {dst}")
SETUP

# 3. Copy template PPTXs to working dir
cp /mnt/user-data/uploads/Being_a_Scientist_slide_deck.pptx /home/claude/enquiry-builder/sci_template.pptx
cp /mnt/user-data/uploads/science-example.pptx /home/claude/enquiry-builder/sci_example.pptx

# 4. Create assets directory and extract badge/pupil images
# (build_science_lesson.py expects /home/claude/enquiry-builder/assets/)
# Run the asset extraction from sci_template.pptx and sci_example.pptx
```

---

## States of Matter enquiry — known parameters

These came from the test lesson built in this session:

- **Key question:** Can materials change their state?
- **Challenge:** Create a scientific report about how materials change
- **Science strand:** Chemistry
- **Disciplinary focus:** observe_and_measure, record_and_present, conclude
- **Writing outcome:** scientific report
- **Number of lessons:** ~10–12 (confirm with Innes)

The test lesson JSON is at GitHub `EnquiryBuilder/test_lesson.json` — do NOT use this as the MTP. Generate a fresh full MTP via Stage 1–2 of the skill.

---

## Open questions / blockers

- Animation XML not yet implemented in the builder. The `animate_sequence` field is captured in the MTP JSON but the builder currently produces static slides. This is a known gap — build the animations once the static version is working end-to-end.
- Asset extraction script (badges, pupil images etc.) needs to run at session start to populate `/home/claude/enquiry-builder/assets/`. The assets were created in this session but don't persist.
- Innes has not confirmed the exact number of lessons for States of Matter.
- Higgsfield MCP is available (`nano_banana_pro`, 16:9). Image URLs from Higgsfield are temporary — download immediately after generation.

---

## Immediate next step

Fetch all scripts from GitHub, re-upload the three template PPTXs (Being_a_Scientist_slide_deck.pptx, science-example.pptx, KQ_LO.pptx), run setup to create kq_lo_science_clean.pptx and extract assets, then ask Innes to confirm the number of lessons for the States of Matter enquiry before generating the full MTP.
