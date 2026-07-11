# Transfer: enquiry-lesson-builder — LP wiring + geography/history expansion

**Generated:** 2026-07-11 (updated, supersedes earlier same-slug version)
**Originating focus:** Debugging T6W7 L1 (States of Matter) PPTX repair-dialog loop to resolution, building its Learning Paper through four readability revisions, and capturing durable LP-building principles. Next phase is expanding `enquiry-lesson-builder`'s scope.
**Skill in use:** `enquiry-lesson-builder` (science-only, custom repo skill) + `learning-paper` (label pipeline) — both closed out for this lesson; next phase uses neither directly, it's new build work.

---

## Status

T6W7 L1 PPTX confirmed clean in real PowerPoint (v12) — closed, do not re-investigate. T6W7 L1's Learning Paper is at **v4, delivered, matches Innes's own real-PowerPoint evidence** — this is the final state, not a draft. LP went through 4 rounds of real feedback (v1 built → v2 added missing particle-model diagram → v3 readability pass, sizes/label-scale/spacing matched to Innes's own edit → v4 recalibrated a font-wrap heuristic against his real-PowerPoint screenshot). All fixes are captured as durable, reusable rules in `LearningPaper/LP_CONTENT_PRINCIPLES.md` — read that file before building any future LP, any subject.

Three-part plan agreed with Innes for what comes next (his own framing): (1) T6W7 L1 LPs — **done**. (2) Wire LP generation into `enquiry-lesson-builder`'s own workflow so one call produces PPTX + LP together, not a manual second step — **not started**. (3) Build `geography_registry.py` / `history_registry.py` to extend the whole pipeline beyond science — **not started**. Treat both as fresh scoping conversations, not continuations.

## What's been produced

- GitHub `EnquiryBuilder/SKILL.md` — full Round 5–11 PPTX debugging narrative. Closed, don't re-investigate.
- GitHub `Shared/OOXML_VALIDATION_NOTES.md` — every confirmed-invalid OOXML construct found this session, plus a confirmed false positive in `diagnose.py`'s "BROKEN RELS" check (don't trust that specific check). Read before writing any new hand-built PPTX XML.
- GitHub `Shared/fix_pptx_ooxml.py`, `EnquiryBuilder/lib_ooxml.py` — Fix #8–#10 (sectionLst, fontScale, invalid masterClr/bodyPr-autofit).
- GitHub `Science/build_t6w7_l1_lp.py` — **the reference LP builder pattern going forward**, not just this one lesson's script. Contains `_wrap_line_count()` (font-fit heuristic, see gotcha below), `add_reference_image()` (resource-on-page pattern), and wrap-aware height helpers for headings/instructions/table rows/word banks. Any new LP builder should copy this file's structure, not `Geography/build_geo_lps_pptx_v3.py` (older pattern, doesn't have the wrap-fixes).
- GitHub `Science/T6W7_L1_LP1_Scientist_States_of_Matter.pptx` — final delivered LP, v4.
- GitHub `LearningPaper/LP_CONTENT_PRINCIPLES.md` — **read this before any future LP work, full stop.** Five rules: (1) resource-on-page (if text names a model/map/diagram, it must be on the page), (2) label must be scaled to ~70.7% of the pipeline's natural render size, (3) pupil-page text sized for children (12pt default for instructional text, headings 14-16pt, table cells can go to 10pt if space requires), (4) write-line gap before the first line must match the gap between lines (0.8cm/0.315"), (5) table rows must grow for wrapping content, never clip. Plus a critical QA limitation section (see gotcha below).

## Decisions locked in

- `enquiry-lesson-builder` stays science-only until the geography/history registries are actually built.
- LP generation is architecturally separate from the PPTX lesson builder (raw OOXML zip manipulation vs python-pptx). Wiring them together means a shared module both call, fed from the same MTP JSON.
- **Critical environment gotcha**: there is no Twinkl Cursive Looped font file anywhere in the repo, and it is not installed in this Cowork sandbox (`fc-list` finds nothing). Every LibreOffice-rendered QA screenshot for LP content therefore uses a substitute font that is WIDER than the real one — confirmed directly when Innes's real PowerPoint fit "Balloon (filled with air)" on one line at 10pt in a 1.74" column, but every LibreOffice render of the same file wrapped it to two lines. **LibreOffice QA screenshots are only trustworthy for gross layout (positioning, overlap, page-fill) — never for whether a specific line of body text fits a specific box width.** For that question, only Innes's own PowerPoint (a screenshot or an edited file he sends back) is trustworthy evidence. `_wrap_line_count()`'s chars-per-pt-width ratio (0.46, in `Science/build_t6w7_l1_lp.py`) is calibrated from exactly one such real data point — treat it as a reasonable starting estimate, not a precise measurement, and recalibrate again if Innes provides more real evidence it's off.
- Other sandbox gotchas carried over from PPTX debugging, still apply to any script from the repo: hardcoded `/home/claude` paths need patching to a real writable dir before use (`sys.path`, `ASSETS` constant, `png_dest` defaults — see top of `build_t6w7_l1_lp.py` for the working pattern); the outputs folder is write-once (do iterative/QA work in `/tmp`, copy the final file to outputs once under a new name).
- Recurring bug class, now fixed in multiple places this session: fixed-height/fixed-width text boxes for text that can wrap to 2+ lines. Any new layout code placing text in a box needs a wrap-line estimate driving the box size, never a hardcoded single-line assumption.
- Adapted/differentiated LP version was **not** built for T6W7 L1 (skill default "no unless asked", scope was explicitly just the one LP). Revisit if Innes wants one.

## Specific user requirements

> "enquiry-lesson-builder is supposed to be built to do the PPTXs, lesson resources and learning papers (with the correct learning labels). AND do that for science, geography and history."

Innes's stated end-goal for the skill's scope — the three-part plan above is how to get there without derailing into a single unscoped mega-task.

> "the balloon text does fit on one line in the PPTX version - perhaps you need to look at working out the size comparison ratio between the rendered version and the size once it's in the PPTX?"

This is what surfaced the font-substitution QA gotcha above — his instinct was correct and led directly to the fix.

Standing communication instruction (repeated multiple times, do not regress): no process narration implying unearned confidence about fixes not yet confirmed by Innes in real PowerPoint; report findings plainly, correct claims openly when his evidence contradicts them rather than defending the original claim.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| GitHub `EnquiryBuilder/SKILL.md` | current, Round 11 | No — fetch via github-sync |
| GitHub `Shared/OOXML_VALIDATION_NOTES.md` | current | No — fetch via github-sync |
| GitHub `Shared/fix_pptx_ooxml.py`, `EnquiryBuilder/lib_ooxml.py` | current, Fix #10 | No — fetch via github-sync |
| GitHub `Science/build_t6w7_l1_lp.py` | final, v4 pattern — use as the LP builder template | No — fetch via github-sync |
| GitHub `LearningPaper/LP_CONTENT_PRINCIPLES.md` | current, 5 rules + QA gotcha | No — fetch via github-sync, read first |
| GitHub `LearningPaper/*.py`, `Shared/label_builder.py`, `Shared/generate_wfa_labels.py` | current | No — fetch via github-sync, then patch `/home/claude` paths per gotcha above |

## Open questions / blockers

- No design decided yet for exactly how LP generation gets called from within `enquiry-lesson-builder`'s workflow (shared module shape, where in the MTP JSON schema the LP-specific content lives vs. reusing existing `youdo_task`/`isb` fields, whether LP build is a mandatory or optional step per lesson).
- No decision on which subject to build first between geography and history, or whether existing `Geography/*.py` files (several versions predating this session's registry-based architecture and the LP wrap-fixes) should be consolidated as part of building `geography_registry.py`.
- Chemistry discipline slide (T6W7 L1 PPTX, slide 3) has a known, still-unfixed shape overlap — flagged to Innes across multiple earlier rounds, no response yet. Low priority, cosmetic, unrelated to the LP work.

## Immediate next step

Ask Innes which of the two remaining plan items to start on: wiring LP generation into `enquiry-lesson-builder`'s own workflow, or starting the geography/history registry expansion. Both are substantial new builds, not continuations of anything already in flight — treat as fresh scoping conversations, not a resume-and-continue.
