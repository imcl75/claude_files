# Transfer: Enquiry Supporting Resources Builder

**Generated:** 2026-07-18
**Originating focus:** Building `build_resources.py` (writing toolkit + enquiry supporting resources), wiring it into the enquiry-lesson-builder skill, and packaging updated skills.
**Skill in use:** enquiry-lesson-builder (reference), none (manual build)

---

## Status

`build_resources.py` is complete, tested, and live in the GitHub repo (`EnquiryBuilder/build_resources.py`). The enquiry-lesson-builder and github-sync skills have been updated and repackaged. Three skill files are sitting in outputs ready to install. The Y5 Astronomy MTP needs a `supporting_resources` block added before the end-to-end Astronomy build can begin.

---

## What's been produced

- `/mnt/user-data/outputs/build_resources.py` — final, pushed to GitHub `EnquiryBuilder/build_resources.py`
- `/mnt/user-data/outputs/test_writing_toolkit.pdf` — test output, Y5 planet writing toolkit, all section types working
- `/mnt/user-data/outputs/knowledge-organiser.skill` — packaged (from previous session, ready to install)
- `/mnt/user-data/outputs/enquiry-lesson-builder.skill` — updated and repackaged (Stage 6 added, MTP schema updated)
- `/mnt/user-data/outputs/github-sync.skill` — updated and repackaged (`build_resources.py` added to FILE_MAP)
- `EnquiryBuilder/build_ko_pdf.py` — in GitHub repo (from previous session)
- `EnquiryBuilder/mtp/y5_astronomy_mtp.json` — in GitHub repo, has `knowledge_organiser` block, needs `supporting_resources` block

---

## Decisions locked in

- **Writing toolkit format:** A4 portrait (not landscape), row-based layout (1 or 2 sections per row), content-driven heights
- **Section types:** `bullet_list`, `multi_column_list` (sub-columns with headings, e.g. Fronted Adverbials), `word_grid` (dense word columns), `two_panel` (left structured entries, right categorised word lists)
- **Colour scheme:** Page header = year group colour only. Section headers use `TOOLKIT_SECTION_COLOURS` — a fixed palette distinct from WFA year colours (slate blue, forest green, warm purple, burnt sienna), cycling across sections. Year colours must NOT appear as section headers — they have specific meaning for children.
- **Resource is called "Writing Toolkit"** (not "Writing Mat")
- **Config schema uses `rows` array** — each row has 1–2 sections, each with a `type` field. Sections are fully data-driven from `enquiry.writing_features` at build time — no hardcoded grammar feature names.
- **L1 resources** (sort cards, word cards, statement sort) built at Stage 6 alongside writing toolkit
- **Writing toolkit built at start of writing phase** (before first `writing_grammar` lesson)
- **MTP schema** has `supporting_resources` block at top level alongside `knowledge_organiser`

```python
# TOOLKIT_SECTION_COLOURS (in build_resources.py)
TOOLKIT_SECTION_COLOURS = [
    '#4a6fa5',   # slate blue
    '#3a7a50',   # forest green
    '#7a4a90',   # warm purple
    '#b05028',   # burnt sienna
]
```

---

## Specific user requirements

> "don't build something rigid which only ever covers fronted adverbials, conjunctions as another enquiry might have a writing focus of using prepositional phrases, embedded clauses, relative pronouns etc. This will need to be established at the very beginning of the process (i think it's in the MTP inputs process already?)"

> "I would avoid the year group colours as these have a context for the children and it's confusing. The colours are just to help each supporting tool stand out from another."

> "if it's for, e.g Y5, the ONLY part that should be orange is the header bar and no orange anywhere else for the same reason as above"

`writing_features` IS already in the MTP schema at `enquiry.writing_features` — confirmed. No `model_write` field in MTP; model text is generated dynamically in `writing_draft` lesson slides.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/user-data/outputs/build_resources.py` | final | No — also in GitHub |
| `/mnt/user-data/outputs/knowledge-organiser.skill` | ready to install | No |
| `/mnt/user-data/outputs/enquiry-lesson-builder.skill` | ready to install | No |
| `/mnt/user-data/outputs/github-sync.skill` | ready to install | No |
| `EnquiryBuilder/mtp/y5_astronomy_mtp.json` | in GitHub, needs `supporting_resources` block | No — fetch from repo |
| `/mnt/skills/user/enquiry-lesson-builder/SKILL.md` | outdated (new .skill not yet installed) | Install .skill file |
| `/mnt/skills/user/github-sync/SKILL.md` | outdated (new .skill not yet installed) | Install .skill file |

---

## Enquiry-lesson-builder skill changes (for reference)

- **New Stage 6** — Build Supporting Resources (between KO PDF and vocab poster)
- Stages renumbered: old 6→7 (vocab poster), 7→8 (lesson PPTXs), 8→9 (LPs), 9→10 (Deliver)
- Stage 10 Deliver now includes supporting resource PDFs; L1 resources labelled in zip
- `build_resources.py` added to source files table
- `supporting_resources` block added to MTP JSON schema (with `l1_resources` and `writing_toolkit` sub-blocks)
- Outstanding issues: LP preview injection still open; Y5 Astronomy end-to-end build still open (needs `supporting_resources` block in MTP); supporting resources issue closed

## Github-sync skill changes

- `build_resources.py` added to FILE_MAP under `EnquiryBuilder`

---

## Open questions / blockers

- Three skill files need installing before the updated skill logic is live: `knowledge-organiser.skill`, `enquiry-lesson-builder.skill`, `github-sync.skill`
- Y5 Astronomy MTP (`y5_astronomy_mtp.json`) needs `supporting_resources` block before end-to-end build
- LP preview injection for science not yet implemented (longer piece of work — needs LPs built before PPTXs)

---

## Immediate next step

1. Innes installs the three .skill files from outputs (knowledge-organiser, enquiry-lesson-builder, github-sync).
2. Fetch `EnquiryBuilder/mtp/y5_astronomy_mtp.json` from the repo and add the `supporting_resources` block (sort cards based on planet types, word cards from `knowledge_organiser.vocabulary`, statement sort about the solar system, writing toolkit config for the information text writing phase).
3. Then begin the Y5 Astronomy end-to-end build: generate images → build KO PDF → build supporting resources → build lesson PPTXs and LPs.
