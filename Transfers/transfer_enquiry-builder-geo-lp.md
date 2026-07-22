# Transfer: Enquiry Builder — Geography LP wiring

**Generated:** 2026-07-22
**Originating focus:** Getting Geography LPs to build automatically from MTP JSON, matching how Science works.
**Skill in use:** enquiry-lesson-builder (for reference), github-sync

---

## The fundamental architecture (confirmed this session — do not deviate)

One universal MTP JSON schema drives everything. One LP builder. One KO builder. One resources builder. Subject doesn't matter — the content in the boxes changes, the structure doesn't. Builders handle visual differences (colours, masters, layouts) from two fields: `subject` at lesson level and `substantive_concept` (Geography) or `strand` (Science). Innes was explicit: never say "Science LP builder" or "Geography LP builder" — there is one LP builder.

---

## Status

Priority 1 (wire LP build into Geography lesson builder) is **partially done**:
- `EnquiryBuilder/build_lp.py` updated: `_add_label`, `_build_one_level`, `_build_legacy` all now accept `subject` param, read from `lesson.subject`, default `'scientist'` for backwards compat. **Committed.**
- `Geography/england_brazil_mtp.json` updated: all 5 lessons have `subject: "geographer"`, `year_group: "Y4"`, and three-level `lp` blocks. **Committed.**
- `build_geography_lesson.py` does NOT yet call `build_lp.py` — the actual wiring step is **not done**.
- Test build of L4 LP: standard and adapted produced (30KB each). `further_adapted` failed.

**Known bug in england_brazil_mtp.json:** `row_boxes` elements use `"labels"` but the renderer (`_render_row_boxes`) expects `"items"`. Affects L1, L4, L5 further_adapted levels. Fix: rename `"labels"` → `"items"` in those elements before re-testing.

---

## What's been produced

- `EnquiryBuilder/build_lp.py` — subject param added, committed to repo (commit b103f82)
- `Geography/england_brazil_mtp.json` — lp blocks added for all 5 lessons, committed (same commit)
- `claude/enquiry-builder-pipeline-status.md` — written to project, full status table and priority list

---

## Decisions locked in

- History is on hold. Do not touch anything History-related. Return only when Science and Geography are both fully complete.
- One MTP schema for all subjects — never generate a Geography MTP with different fields to a Science MTP.
- `subject` field at lesson level drives label icon; `substantive_concept` (geo) / `strand` (sci) drives slide visuals.
- KWL is a static slide — no unique MTP content needed. Specified in `slides[]` for lesson 1 only. Already exists in Science deck.
- Innes uses British English. No em dashes. No bullet points in conversation. No AI hallmarks.

## Specific user requirements

> "Stop deleting things FFS"

> "make your answers MUCH shorter and precise"

> "I am forgetting that history exists and you need to too"

> "Literally you make the MTP the EXACT same way and it is used to fill in the slides, LPs, LLs, resources etc"

> "swap out an experiment about states of matter for an explanation of oxbow lakes and you have a geography LP — this is the fundamental part you are NOT showing me you understand"

---

## Priority order (confirmed by Innes this session)

1. **Wire `build_lp.py` into `build_geography_lesson.py`** — so LPs build automatically when you build a Geography lesson. Fix the `row_boxes` labels→items bug in the MTP first, then add the LP call at the end of the geography builder, matching what `build_science_lesson.py` does (search for `build_lp` in that file to find the exact pattern).
2. **Wire label sheet into both builders** — `Shared/generate_wfa_labels_pdf.py` exists, produces A4 sheet of 12 Avery labels children stick in their books. Not yet called automatically by either builder.
3. **Wire KO PDF into Geography builder** — `build_ko_pdf.py` is generic and already wired into Science. Geography needs the same call.
4. **Wire supporting resources into Geography builder** — `build_resources.py` handles sort cards, word cards, statement sort (L1 pack) and writing toolkit (first writing lesson). Already works for Science; Geography needs it.
5. **KWL slide for Geography lesson 1** — confirm `build_geography_lesson.py` handles a `type: "kwl"` slide entry in `slides[]`.

---

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `EnquiryBuilder/build_lp.py` | Updated, committed | subject param added |
| `Geography/england_brazil_mtp.json` | Updated, committed | lp blocks added; row_boxes bug (labels→items) |
| `Geography/build_geography_lesson.py` | Unchanged | Needs LP call wired in (Priority 1) |
| `EnquiryBuilder/build_science_lesson.py` | Unchanged | Reference: search `build_lp` to find the wiring pattern |
| `Shared/generate_wfa_labels_pdf.py` | Unchanged | Exists, not wired in |
| `EnquiryBuilder/build_resources.py` | Unchanged | Exists, not wired in |
| `EnquiryBuilder/build_ko_pdf.py` | Unchanged | Exists, wired into Science only |
| `LearningPaper/build_enquiry_label.py` | Unchanged | Label on LP itself — already wired into build_lp.py |

## Open questions / blockers

- `row_boxes` in `england_brazil_mtp.json` uses `"labels"` key but renderer needs `"items"` — fix before LP test passes
- `build_geography_lesson.py` LP call not yet added — this is the core Priority 1 task

## Immediate next step

1. In `Geography/england_brazil_mtp.json`, rename all `"labels"` keys inside `row_boxes` elements to `"items"`.
2. In `Geography/build_geography_lesson.py`, find where the script finishes building slides and add a call to `build_lp.py` — use the pattern in `EnquiryBuilder/build_science_lesson.py` (search `build_lp`).
3. Test: run `build_geography_lesson.py` against `england_brazil_mtp.json` lesson 4 and confirm LP files are produced alongside the PPTX.
4. Commit and push. Then move to Priority 2.
