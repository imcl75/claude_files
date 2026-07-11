# Transfer: enquiry-lesson-builder — LP wiring + geography/history expansion

**Generated:** 2026-07-11
**Originating focus:** Debugging T6W7 L1 (States of Matter) PPTX repair-dialog loop to resolution, then building its Learning Paper. Next phase is expanding `enquiry-lesson-builder`'s scope.
**Skill in use:** `enquiry-lesson-builder` (science-only, custom repo skill) + `learning-paper` (label pipeline)

---

## Status

T6W7 L1 PPTX is confirmed clean in real PowerPoint (v12) after five separate root-caused defects fixed across an extended repair-dialog debugging loop (see "What's been produced" for the writeup location — do not re-investigate these, they're closed). T6W7 L1's Learning Paper (LP1, sorting task) is built, QA-rendered, and delivered — not yet confirmed by Innes in real PowerPoint.

Three-part plan agreed with Innes for what comes next (his own framing): (1) T6W7 L1 LPs — **done this session**. (2) Wire LP generation into `enquiry-lesson-builder`'s own workflow so one call produces PPTX + LP together, not a manual second step — **not started**. (3) Build `geography_registry.py` / `history_registry.py` to extend the whole pipeline beyond science — **not started**. He explicitly expects each subject registry to likely need its own real debugging pass, not a copy-paste.

## What's been produced

- GitHub `imcl75/claude_files`, `EnquiryBuilder/SKILL.md` — full Round 5–11 debugging narrative (SmartArt crash, animation XML structure, layout mismatches, docProps/app.xml, p14:sectionLst ghost ids, doubled fontScale, invalid `masterClr`/`autofit` attribute). Read this before touching the science builder.
- GitHub `Shared/OOXML_VALIDATION_NOTES.md` — **the distilled reference**: every confirmed-invalid OOXML construct found this session, a confirmed false positive in `diagnose.py`'s "BROKEN RELS" check (don't trust that specific check), and what's cosmetic PowerPoint repackaging noise vs a real defect. Read this before writing any new hand-built PPTX XML, in this skill or any other.
- GitHub `EnquiryBuilder/lib_ooxml.py`, `Shared/fix_pptx_ooxml.py` — updated with Round 10/11 fixes (Fix #8 sectionLst, #9 fontScale, #10a/10b masterClr + bodyPr attribute).
- GitHub `Science/build_t6w7_l1_lp.py` — LP builder for T6W7 L1, python-pptx based, uses the real `label_builder.py` pipeline (not hand-rolled). Pattern copied from `Geography/build_geo_lps_pptx_v3.py`. Contains a reusable `_wrap_line_count()` helper — **use this pattern for any future LP builder**, see "Decisions locked in".
- GitHub `Science/T6W7_L1_LP1_Scientist_States_of_Matter.pptx` — delivered LP (2 slides: pupil page + Marking Station).
- Delivered to Innes (session-local, not persisted): `T6W7 - 1 - Mon - States of Matter L1.pptx` (v12) and `T6W7 - 1 - Mon - States of Matter L1 - LP.pptx` — re-fetch from the GitHub paths above if needed again, session-local paths won't exist in a new chat.

## Decisions locked in

- `enquiry-lesson-builder` stays science-only until the geography/history registries are actually built — do not use it for those subjects in the meantime.
- LP generation is architecturally separate from the PPTX lesson builder (different tech: raw OOXML zip manipulation vs python-pptx). Wiring them together means a shared module both call, fed from the same MTP JSON — not merging the two build methods.
- LP content/label spec: label via `label_builder.build_enquiry_label()` (ReportLab-rendered PNG, embedded) — never hand-roll the label, it's specced as mandatory in the `learning-paper` skill for good reason (repeated past failures). LP body content font is Twinkl Cursive Looped; label itself renders in Helvetica (ReportLab base font, not overridden — this is what the existing pipeline does, not a bug).
- **Environment gotcha, will bite immediately on any LP/label work**: all the repo's label scripts (`label_builder.py`, `generate_label_png.py`, `build_enquiry_label.py`) hardcode `/home/claude` (sys.path inserts, `ASSETS` constant, default `png_dest`). That path does not exist and is not writable in this Cowork sandbox. Every such script needs `sys.path` pointed at a real working dir and `ASSETS`/`png_dest` patched after import, before calling. See `Science/build_t6w7_l1_lp.py`'s top section for the working pattern.
- **Environment gotcha #2**: the outputs folder (wherever Read/Write/Edit and bash's mounted path both point) is write-once — cannot overwrite or delete a file once written there. Do ALL iterative building and QA rendering in `/tmp` (bash-only scratch, freely overwritable), and only copy the final file into outputs once, at the end, under a name not previously used.
- **Recurring bug class, found twice this session** — fixed-height text boxes for text that can wrap to 2+ lines. Once in `force_shrink_to_fit` (OOXML runs, caused real double-shrink), once in this session's LP builder (`heading()`/`instruction()`/`word_bank()`/table headers/`answer_text()` all had this same flaw, caused visible overlap in first QA render). Any new layout code placing text in a fixed box needs a wrap-line estimate driving the box height, not a hardcoded single-line assumption. `_wrap_line_count()` in `Science/build_t6w7_l1_lp.py` is a reusable pattern (chars-per-line ≈ `width_pt / (size_pt * 0.52)`, empirically established for Twinkl Cursive Looped in `lib_ooxml.py`).
- Adapted/differentiated LP version was **not** built for T6W7 L1 — `learning-paper` skill's own stated default is "no unless asked", and scope for this session was explicitly just the one LP. Revisit if Innes wants one.

## Specific user requirements

> "enquiry-lesson-builder is supposed to be built to do the PPTXs, lesson resources and learning papers (with the correct learning labels). AND do that for science, geography and history."

This is Innes's stated end-goal for the skill's scope — the three-part plan above is how to get there without derailing into a single unscoped mega-task.

Standing communication instruction (repeated multiple times this session, do not regress): no process narration that implies unearned confidence about fixes not yet confirmed by Innes in real PowerPoint; report findings plainly.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| GitHub `EnquiryBuilder/SKILL.md` | current, Round 11 | No — fetch via github-sync |
| GitHub `Shared/OOXML_VALIDATION_NOTES.md` | current | No — fetch via github-sync |
| GitHub `Shared/fix_pptx_ooxml.py`, `EnquiryBuilder/lib_ooxml.py` | current, Fix #10 | No — fetch via github-sync |
| GitHub `Science/build_t6w7_l1_lp.py` | final, working | No — fetch via github-sync |
| GitHub `Geography/build_geo_lps_pptx_v3.py` | reference pattern, not project-specific | No — fetch via github-sync |
| GitHub `LearningPaper/*.py`, `Shared/label_builder.py`, `Shared/generate_wfa_labels.py` | current | No — fetch via github-sync, then patch `/home/claude` paths per gotcha above |

## Open questions / blockers

- Innes has not yet confirmed T6W7 L1's LP opens/prints correctly in real PowerPoint (the PPTX itself, v12, IS confirmed clean by him).
- Chemistry discipline slide (slide 3 of T6W7 L1) has a known, still-unfixed shape overlap (`TextBox 1`/`TextBox 6`, 29% overlap) — flagged to Innes across multiple earlier rounds, no response yet on how he wants it handled. Low priority, cosmetic, template-inherited.
- No design decided yet for exactly how LP generation gets called from within `enquiry-lesson-builder`'s workflow (shared module shape, where in the MTP JSON schema the LP-specific content lives vs. reusing existing `youdo_task`/`isb` fields, whether LP build is a mandatory or optional step per lesson).
- No decision on which subject to build first between geography and history, or whether existing `Geography/*.py` files (several versions: v2, v3, `build_l456_lps_v2.py`, etc.) should be consolidated/cleaned up as part of building `geography_registry.py`, given they predate this session's registry-based architecture.

## Immediate next step

Ask Innes which of the two remaining plan items to start on: wiring LP generation into `enquiry-lesson-builder`'s own workflow, or starting the geography/history registry expansion. Both are substantial new builds, not continuations of anything already in flight — treat as fresh scoping conversations, not a resume-and-continue.
