# Transfer: Enquiry Builder Session 17

**Generated:** 2026-07-26
**Originating focus:** Phase 11 — image variant teaching slide builders for Science and History.
**Skill in use:** none (direct script build)

---

## Status

Phase 11 complete and signed off. Science and History image teaching slide builders written, tested across all concepts and phases, and committed to the repo. Brain doc updated. Next session is Phase 12 (MTP schema review) followed by Phase 13 (general enquiry deliverables pipeline).

## What's been produced

- `scripts/science/build_science_image_teaching_slides.py` — final, committed (0fc9e46)
- `scripts/history/build_history_image_teaching_slides.py` — final, committed (bddcfde)
- `assets/history/historian_icon_white.png` — generated via PIL (all non-transparent pixels → white), committed (bddcfde)

## Decisions locked in

- Science: single colour set (light D9F3D0 / dark 4EA72E) — no LIGHT_BAR_CONCEPTS; dark is saturated enough, always white text + white icon on full_bleed bar
- History: `LIGHT_BAR_CONCEPTS = {"civilisation"}` — civilisation dark=FFC000 (gold) → black text + dark icon on full_bleed bar; all other 4 concepts → white text + white icon
- `POS_HIST_ICON_FULLBLEED = (11197120, 5735458, 878845, 678176)` — computed from bar geometry (bar y=5368633, h=1411826; icon vertically centred)
- Shape ID 10 is reserved for the Title shape — skipped in all image builders
- All animation helpers identical across geo/sci/hist: `_click_pRg`, `_click_pRg_with_img`, `_click_img`, `_click_all_imgs`, `_build_timing`
- Para indices on image slides are consecutive (0,1,2,3), not alternating
- `withEffect` used for simultaneous image + bullet reveal on `_click_pRg_with_img`
- Utility functions (set_background, inject_xml, add_image, etc.) live in `scripts/geography/build_subject_progression.py` — imported by all subject builders; never duplicated

## Specific user requirements

After Phase 11, Innes specified the following next-steps order:

> "After this, next steps will be to do a circle round to MTP and check there is nothing missing there which the slide builders expect and updating as needed. Then: 1) general enquiry deliverables - Knowledge Organiser, top 10 Vocabulary, handwriting vocabulary word lists 2) Supporting resources 3) learning papers with Learning labels 4) Learning label sheets. After the MTP review, please check what already exists for 1-4 as these have been worked on with claude and we should be leveraging those as starting points."

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `scripts/science/build_science_image_teaching_slides.py` | final, in repo | No |
| `scripts/history/build_history_image_teaching_slides.py` | final, in repo | No |
| `assets/history/historian_icon_white.png` | final, in repo | No |
| `scripts/geography/build_image_teaching_slides.py` | reference (geo canonical) | No |
| `scripts/science/build_science_common.py` | reference | No |
| `scripts/history/build_history_common.py` | reference | No |

## Open questions / blockers

- None. Phase 11 is clean.

## Immediate next step

Phase 12 — MTP schema review. Read all three image teaching slide builders (geo, science, history) and check that every field they expect is present in the MTP JSON schema in the brain doc. If any fields are missing or inconsistently named, note them and ask Innes before changing the schema. Do not change the schema during the session without asking.

After Phase 12: Phase 13 — check the repo for any existing scripts for Knowledge Organiser, Vocabulary, handwriting word lists, supporting resources, learning papers, and learning label sheets before building anything new.

---

## Session protocol reminder

Start every session:
1. State the goal in one sentence.
2. State which phase gate we are working towards.
3. Clone repo fresh (token and clone command in brain doc — read it).
4. Read the brain doc in the project.
