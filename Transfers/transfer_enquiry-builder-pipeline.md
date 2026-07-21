# Transfer: EnquiryBuilder pipeline — outstanding tasks

**Generated:** 2026-07-21
**Originating focus:** Iterative improvement of the WFA EnquiryBuilder pipeline — workflow doc, MTP schema, History builder, LP wiring, naming convention.
**Skill in use:** enquiry-lesson-builder (Science); History/Geography builders are standalone Python scripts in the repo.

---

## Status

Two sessions of pipeline work complete. Workflow doc, MTP schema reference, and Science skill all updated and pushed. Several builder-level changes (concept cartoon fix, output naming, LP wiring, LL generation) are documented but not yet coded. Roman Civilisation MTP exists but has not been run through the builder end-to-end.

---

## What's been produced

- `EnquiryBuilder/ENQUIRY_BUILDER_WORKFLOW.md` — final, pushed. Block 1 now includes timetable question; Block 2 History has challenge/writing features; MTP draft step between Block 4 and 5; CLF check mandatory; quiz 4–5 questions; Y5 default.
- `EnquiryBuilder/MTP_schema_reference.md` — final, pushed. All three builders now have `day_label` and `term_week` lesson-level fields. Y5 default. History `concept_cartoon_pptx` field noted (legacy; see concept cartoon fix below).
- `EnquiryBuilder/mtp_roman_civilisation_final.json` — draft MTP for Y5 Roman Civilisation History enquiry. 14 lessons. `lp_task` per lesson is still plain text (see LP spec upgrade below).
- `enquiry-lesson-builder.skill` — updated skill file with `day_label`/`term_week` replacing `day`/`session` in the schema example. Innes needs to save this over the existing skill.
- `Writing/IMAGE_INTEGRATION_WRITING.md` — integration guide for image slides in the writing lesson pipeline. Separate session needed to implement.
- `transfer_image-integration-writing.md` — prompt for starting the image integration session. In outputs.

---

## Decisions locked in

- **Y5 default** — all content from September 2026. Innes moves to Y5.
- **Day labels** — `{term_week}_{seq_in_week}{Day}` e.g. `T2W3_1Tue`. Sequence resets each week. Computed from the lesson timetable list Innes provides at Block 1. Written as `day_label` + `term_week` per lesson in MTP JSON.
- **Timetable input format** — Innes provides an ordered list of days at enquiry outset, e.g. `Tue, Thu` or `Mon, Tue, Tue, Wed, Thu, Thu, Fri`. Repeats for multi-lesson weeks. Can be up to 7 per week.
- **Naming convention** — `T2W3_1Tue_L01_Teaching_Who_were_the_Romans.pptx`. Folder root: `Enquiry_Roman_Civilisation_Y5_T2W3/Teaching/`, `LPs/`, `LLs/`, `Resources/`, `KO/`.
- **LP levels** — Standard / Adapted / Further Adapted (not A/Y/O/D). Assignments in `EnquiryBuilder/class_lp_groups.json`.
- **All lessons need LL** — the 12-per-page sticker sheet. Even if no LP, every lesson gets an LL. LP only where children do a task on paper.
- **Three-level LP drafted at MTP time** — Claude generates standard/adapted/further_adapted `elements[]` when building the MTP. Innes reviews before build.
- **Concept cartoon** — fresh-build only (no source PPTX). Speech bubbles (rounded rectangles). Fields: `speech_a`, `speech_b`, `speech_c`. No `learners[]`.
- **Quiz** — 4–5 questions per lesson (L2+). L1 uses KWL instead.
- **CLF curriculum check** — mandatory before any content is drafted. Documents at `/mnt/.projects/019ce895-59c7-71c2-b81d-5e89f848fb8d/docs/`.

---

## Specific user requirements

> "I want the three-level LP content in the MTP at enquiry-build time (Claude drafts all three levels when generating the MTP, you review and adjust)."

> "All LPs need an LL. When I say LL I specifically mean the LL sheet (12 per page). These are needed when the only thing they will stick in their book is a learning label."

> "I prefer speech bubbles but rounded rectangles are OK."

> "I can tell you the schedule each enquiry. It will change from time to time so I would rather you ask at the outset."

---

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `EnquiryBuilder/ENQUIRY_BUILDER_WORKFLOW.md` | Final | Pushed to repo |
| `EnquiryBuilder/MTP_schema_reference.md` | Final | Pushed to repo |
| `EnquiryBuilder/mtp_roman_civilisation_final.json` | Draft | Pushed to repo. `lp_task` plain text — needs upgrading to structured `lp` object |
| `History/build_history_lesson.py` | Needs edit | Concept cartoon dispatcher fix + output naming fix. Fetch from repo before editing. |
| `EnquiryBuilder/build_lp.py` | Current | `build_lp_all_levels()` exists and works. Needs wiring into Block 7 pipeline. |
| `EnquiryBuilder/class_lp_groups.json` | Current | Y5 2026-27: 5IM (30 children, 6 adapted, 0 further_adapted), 5LS (30, 1 adapted, 3 further_adapted) |
| `EnquiryBuilder/image_layouts.py` | Current | 10 layout types. Used by History/Geography builders. |

---

## Outstanding tasks

### 1. Concept cartoon fix — `build_history_lesson.py` (no input needed from Innes)

**File:** `History/build_history_lesson.py`

Current dispatcher (line ~1320):
```python
'concept_cartoon': build_concept_cartoon
```
Broken — `build_concept_cartoon` (lines 1051–1131) tries to clone from a source PPTX and raises `RuntimeError` if not found.

**Fix:** Change dispatcher to route through `build_image_slide` instead. `build_image_slide` already handles `layout_key: "concept_cartoon"` at line ~1285 using fresh rounded-rect speech bubbles.

MTP slide spec for concept cartoons changes from:
```json
{"type": "concept_cartoon", "learners": [...]}
```
to:
```json
{"type": "concept_cartoon", "speech_a": "...", "speech_b": "...", "speech_c": "..."}
```
Update `mtp_roman_civilisation_final.json` where concept cartoon slides exist.

Also remove `concept_cartoon_pptx` from the History enquiry-level fields (it's now unused).

### 2. Output naming — `build_history_lesson.py` (no input needed)

Current output: `L{n:02d}_{label[:40]}.pptx`

Required: `T{t}W{w}_{seq}{Day}_L{n:02d}_Teaching_{Topic}.pptx`

The builder needs to accept `day_label` and `term_week` from the MTP JSON and use them in the output filename. The topic label comes from `building_block_text` (spaces → underscores, truncated to 40 chars).

### 3. Structured LP spec in `mtp_roman_civilisation_final.json`

Replace every `lp_task: "..."` (plain text) with a structured `lp` object:

```json
"lp": {
  "standard": {
    "title": "...",
    "task": "...",
    "elements": [{"type": "answer_lines", "count": 6}, ...]
  },
  "adapted": {
    "task": "...",
    "elements": [{"type": "cloze", ...}, {"type": "word_bank", ...}]
  },
  "further_adapted": {
    "task": "...",
    "elements": [{"type": "matching", ...}]
  }
}
```

LP element types available in `build_lp.py`: `heading`, `instruction`, `answer_lines`, `cloze`, `matching`, `word_bank`, `reference_image`, `row_boxes`, `pair_boxes`, `table`, `graph_template`, `sentence_starter`, `spacer`, `sort_table`, `marking_station`, `answer_text`.

Lessons that need LP (paper task): L3–L10 knowledge lessons, L11 planning, L12–L13 writing drafts, L14 editing/publishing.
Lessons that need LL only (no LP): L1 intro, L2 KWL/setup (check MTP — may vary).
ALL 14 lessons need LL.

### 4. LP wiring in Block 7 pipeline

After the builder generates teaching PPTXs, `build_lp_all_levels()` from `build_lp.py` should be called for each lesson where `lp` block is present. Output paths should follow naming convention:
```
LPs/T2W3_1Tue_L03_LP_Standard_Roman_Society.pptx
LPs/T2W3_1Tue_L03_LP_Adapted_Roman_Society.pptx
LPs/T2W3_1Tue_L03_LP_Further_Adapted_Roman_Society.pptx
```

### 5. LL generation for all lessons

Every lesson needs a 12-per-page learning label sheet (`LLs/T2W3_1Tue_L01_LL_Who_were_the_Romans.pptx`). The LL builder already exists (used in maths pipeline). Wire it into the History/Geography/Science build step for every lesson regardless of whether an LP exists.

### 6. Roman Civilisation MTP end-to-end test

Once concept cartoon fix and naming fix are in place, run `mtp_roman_civilisation_final.json` through `build_history_lesson.py`. QA all 14 lesson decks. Requires LP structured spec to be in the MTP first (task 3).

### 7. github-sync FILE_MAP

The `github-sync` skill's FILE_MAP may not include the three new tracked files. Verify and add if missing:
- `EnquiryBuilder/ENQUIRY_BUILDER_WORKFLOW.md`
- `EnquiryBuilder/MTP_schema_reference.md`
- `EnquiryBuilder/mtp_roman_civilisation_final.json`

---

## Recommended order of attack

1. Task 7 (github-sync FILE_MAP) — quick, no risk
2. Task 1 (concept cartoon fix) — code change, no Innes input needed
3. Task 2 (output naming fix) — code change, no Innes input needed
4. Task 3 (LP spec in Roman MTP) — Claude drafts, Innes reviews
5. Task 4 + 5 (LP + LL wiring) — depends on tasks 1–3
6. Task 6 (end-to-end test) — depends on all above

---

## Immediate next step

Fetch `History/build_history_lesson.py` from repo, fix the concept cartoon dispatcher (task 1), fix output naming (task 2), push the updated file, then move to task 3 (LP structured spec in the Roman Civilisation MTP).
