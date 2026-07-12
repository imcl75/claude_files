# Transfer: Enquiry Lesson Builder — Geography PPTX builder

**Generated:** 2026-07-12
**Originating focus:** Adding full geography support to the enquiry-lesson-builder skill, then building Geography/build_geography_lesson.py.
**Skill in use:** enquiry-lesson-builder (skill updated; builder script still to write)

---

## Status

The `enquiry-lesson-builder` skill is complete for History and Science. Geography reference file (`references/geography.md`) has just been written and the skill repackaged and installed. The immediate next task is to write `Geography/build_geography_lesson.py` in the GitHub repo and test it against a sample MTP.

---

## What's been produced

- `/var/folders/7w/.../skills/enquiry-lesson-builder/SKILL.md` — installed, final
- `/var/folders/7w/.../skills/enquiry-lesson-builder/references/science.md` — installed, final (verbatim copy from previous science skill)
- `/var/folders/7w/.../skills/enquiry-lesson-builder/references/history.md` — installed, final
- `/var/folders/7w/.../skills/enquiry-lesson-builder/references/geography.md` — installed, final (written this session)
- `enquiry-lesson-builder.skill` — packaged and presented to Innes this session

---

## Decisions locked in

- Geography deck colour changes **per lesson** (not per enquiry) — driven by `substantive_concept` field in MTP
- Slide order every lesson: KQ Cover → Concepts & Skills → Progression → Puzzle Pieces → LO → KWL(L1)/Quiz(L2+) → Vocabulary → Teaching slides → Learning Review
- LO slides are **inline** (not delegated to lo-slides skill)
- Puzzle piece backgrounds are EMF+ image files (~6.4 MB each) — cannot set colour via XML fill; must swap `r:embed` rId on the `<p:pic>` element
- Pieces are cumulative: lesson N shows N pieces, each coloured by that lesson's `skill_focus`
- Piece arrangement: 5 bottom row, 6 middle row, 4 top row (15 total)

## Skill → EMF rId mapping (confirmed by visual inspection of icon PNGs)

| skill_focus | EMF rId | EMF file | Icon file | Colour |
|-------------|---------|----------|-----------|--------|
| `questioning_predicting` | rId6 | image12.emf | image13.png | Orange |
| `observing_recording` | rId8 | image14.emf | image15.png | Yellow |
| `field_work` | rId10 | image16.emf | image17.svg | Purple |
| `map_skills` | rId12 | image18.emf | image20.png | Green |
| `concluding_communicating` | rId15 | image21.emf | image22.png | Blue |

## Master index mapping (per-lesson, from substantive_concept)

| substantive_concept | Master index | Colour |
|--------------------|-------------|--------|
| `place_space_scale` | 0 | Yellow (#FFF3CC) |
| `human_geography` | 1 | Peach (#FFCCCC) |
| `cultural_awareness` | 2 | Blue (#4573C4) |
| `physical_geography` | 3 | Green |
| `environmental_impact` | 4 | Purple (#CCCCFF) |

Masters 3 and 4 have `1_` prefix in their OOXML names.

## LO placeholder indices

| Content | idx |
|---------|-----|
| Date | ph0 |
| WALT | lo10 |
| TIB | lo13 |
| ISB | lo14 |

---

## Existing builder scripts for reference (in repo imcl75/claude_files)

- `History/build_history_lesson.py` — model for geography builder
- `History/history_registry.py` — registry pattern; geography will need `geography_registry.py`
- `History/generate_history_docx.js` — DOCX generator (Node.js `docx` package)
- `Shared/fix_pptx_ooxml.py` — **mandatory** post-processor on all PPTX outputs
- `EnquiryBuilder/build_l1_final.py` — science builder (different pattern, not the model)

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/Users/innes/Downloads/Example Enquiry Slides/Geographer.pptx` | Template — on Innes's Mac | Fetch from Mac path when needed |
| `/Users/innes/Downloads/Example Enquiry Slides/geography-example.pptx` | 16-slide L1 reference deck | Fetch from Mac path |
| `imcl75/claude_files` GitHub repo | Contains History/ and Shared/ scripts | github-sync skill to fetch |

---

## Specific user requirements

> "replace existing skill - but you must retain the slide formats for the science teaching PPTX as they are not the same as the History (or, still to come, geography)"

Science formats live in `references/science.md` and are untouched.

---

## Open questions / blockers

- Exact hex for `physical_geography` master (M3) background not extracted — only known to be green. Extract from Geographer.pptx XML or visually from template when needed.
- `Geography/build_geography_lesson.py` does not yet exist — this is the immediate next task.
- `Geography/geography_registry.py` does not yet exist.
- No test MTP has been written for geography yet — will need one before test build.

---

## Immediate next step

Use the github-sync skill to fetch the repo, read `History/build_history_lesson.py` and `History/history_registry.py` as models, then write `Geography/build_geography_lesson.py` and `Geography/geography_registry.py`. The geography builder must: (1) select the correct master per `substantive_concept`, (2) swap EMF rIds for Puzzle Pieces per `skill_focus`, (3) handle per-lesson master switching that History does not need. After writing, run a test build against a minimal 2-lesson Brazil MTP.
