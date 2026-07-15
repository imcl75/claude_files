# Transfer: Cross-subject MTP alignment + vocab poster resource

**Generated:** 2026-07-15
**Originating focus:** MTP structural comparison across History/Science/Geography, plus building a vocabulary display poster resource for each enquiry subject.
**Skill in use:** none (direct builder work, structural analysis)

---

## Status

Vocab poster resource is complete and approved for all three subjects (History, Science, Geography). The MTP structural analysis is done — misalignments are documented below. Next session is MTP alignment work: standardising the Science JSON format and field names to match History and Geography so all three builders share a common MTP schema.

---

## What's been produced

### Vocab poster HTMLs (outputs folder)
- `vocab_poster_history.html` — final, approved. Ancient Egypt enquiry, Y4 blue (#1798d3)
- `vocab_poster_science.html` — final, approved. States of matter enquiry, Y4 blue
- `vocab_poster_geography.html` — final, approved. England & Brazil enquiry, Y4 blue
- `vocab_poster_geography_y5.html` — Y5 orange (#e57d24) demo, approved as the colour-swap pattern

### Vocab images (~/Pictures/claude-images/)
All vocab images are flat icon illustration style. Filenames:
- History: `vocab_chronology`, `vocab_evidence`, `vocab_primary_source`, `vocab_secondary_source`, `vocab_civilisation`, `vocab_settlement`, `vocab_trade`, `vocab_society`, `vocab_legacy`, `vocab_enquiry`
- Science: `vocab_sci_observe`, `vocab_sci_predict`, `vocab_sci_evidence`, `vocab_sci_experiment`, `vocab_sci_classify`, `vocab_sci_fair_test`, `vocab_sci_variable`, `vocab_sci_conclusion`, `vocab_sci_data`, `vocab_sci_properties`
- Geography: `vocab_geo_location`, `vocab_geo_climate`, `vocab_geo_physical`, `vocab_geo_human`, `vocab_geo_population`, `vocab_geo_continent`, `vocab_geo_hemisphere`, `vocab_trade` (reused), `vocab_geo_migration`, `vocab_geo_comparison`
- Subject icons: `icon_historian.png`, `icon_scientist.png`, `icon_geographer.png`

---

## Decisions locked in

### Vocab poster format
- A3 landscape, prints via Chrome File → Print → A3 landscape, no margins, background graphics on
- 5×2 grid, 10 words per poster, one page only
- Card layout: **word (top)** → **image (middle, flex)** → **definition (bottom)**
- Word: Fredoka One font, `3.4vh`, year group colour
- Definition: Nunito 800 weight, `1.85vh`, black
- Year group colour via single CSS var `--col` — swap to change year group
- All sizing in `vh`/`vw` so layout scales to viewport and prints correctly at A3

### Year group colours
- Y4: `#1798d3` | Y5: `#e57d24` | Y3: `#c0157b` | Y6: `#2bae62`

### Image generation style (use for all future vocab images)
```
Flat icon illustration of [description], clean simple graphic, no people, muted colours, white background, no text, no watermarks, no borders
```
- Tool: dall-e MCP, quality: `fast`, aspect: `1:1`
- No American flag/US imagery unless topic is specifically about the USA
- Flags of other countries are fine
- Avoid illustrated people with faces — silhouettes or symbols instead

### State-of-being icons
- Header uses `<img>` tag, not emoji
- CSS: `height: 6vh; filter: brightness(0) invert(1)` (white on blue header)
- Files: `~/Pictures/claude-images/icon_historian.png`, `icon_scientist.png`, `icon_geographer.png`

---

## MTP structural misalignments (analysis complete — fixes needed)

| Feature | Geography ✓ | History ✓ | Science ✗ needs change |
|---|---|---|---|
| MTP file structure | One file, all lessons | One file, all lessons | Per-lesson JSON files |
| LO fields | `what` / `why` / `success` | `what` / `why` / `success` | `lo` / `tib` / `isb` |
| Concept field | `substantive_concept` per lesson | `concept` at enquiry level | `science_strand` |
| Lesson identifier | `lesson_number` (top level) | `lesson_number` (top level) | `lesson.number` (nested) |
| Key vocab slide | Fixed slide 7 | Fixed slide 7 | Missing |

Science subject-specific fixed slides (being_a_scientist, discipline/strand) should be retained — they just need to sit alongside the shared core.

---

## Specific user requirements

> "the skill is in really good shape for Sci, Hist and Geog. The MTP process still needs tested for each subject and I want to check the content of these are as aligned as possible between subjects."

Goal: a common MTP schema — one JSON format all three builders read the same core fields from, with subject-specific extensions permitted.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `History/build_history_lesson.py` (GitHub) | final | No — fetch from repo |
| `History/history_registry.py` (GitHub) | final | No — fetch from repo |
| `History/egypt_mtp.json` (GitHub) | current MTP | No — fetch from repo |
| `EnquiryBuilder/build_science_lesson.py` (GitHub) | needs alignment | No — fetch from repo |
| `EnquiryBuilder/science_registry.py` (GitHub) | current | No — fetch from repo |
| `EnquiryBuilder/json/t6w7_l1.json` (GitHub) | per-lesson format — needs replacing | No — fetch from repo |
| `Geography/build_geography_lesson.py` (GitHub) | final (reference) | No — fetch from repo |
| `Geography/lib_ooxml.py` (GitHub) | shared lib | No — fetch from repo |

---

## Open questions / blockers

- Should Science get a `key_vocabulary` slide added, or is vocab handled only via the printed poster?
- Should the unified MTP use a `lessons` array (like History/Geography) or another structure?
- The three builders each have different sandbox path patches for `lib_ooxml` — should be unified

---

## Immediate next step

Fetch `EnquiryBuilder/build_science_lesson.py`, `History/build_history_lesson.py` and `Geography/build_geography_lesson.py` from the repo. Propose a unified MTP JSON schema that all three builders can read (keeping subject-specific extensions), and draft the changes needed to `build_science_lesson.py` to adopt it. Show the schema to Innes before making any changes.
