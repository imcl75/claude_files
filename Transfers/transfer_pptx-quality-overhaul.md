# Transfer: PPTX Quality Overhaul — Testing and Loose Ends

**Generated:** 2026-07-08
**Originating focus:** Full overhaul of all PPTX-producing skills to eliminate layout errors, missing visuals, corrupt output and skipped QA — adding preflight validators, delivery gates and template fixes across 9 skills.
**Skill in use:** none (infrastructure/tooling work)

---

## Status

All six phases of the overhaul are complete. Every PPTX-producing skill now has a delivery gate in its SKILL.md and the shared validator infrastructure is in GitHub. The immediate next task is a comprehensive testing regime to verify that every change actually works end-to-end, followed by fixing the one confirmed loose end (ETIW template off-canvas shapes).

---

## What's been produced

All scripts pushed to `imcl75/claude_files` GitHub repo.

### Shared/ (applies to all skills)
- `Shared/validate_pptx_layout.py` — upgraded validator: MISSING-VISUAL, LAYOUT-MISMATCH, OFF-CANVAS, TEXT-SPILL, COLLISION checks. Now reads sldIdLst (not rels) for referenced slides. Icon/Fact overlap exemption added.
- `Shared/validate_base_template.py` — new: checks template PPTX placeholder widths against visual containers before any lesson is built. Run once per session before first build.
- `Shared/fix_pptx_ooxml.py` — exists, unchanged.

### Writing
- `Writing/build_lesson.py` — `build_lo` fixed: scans for Layout 5 by rels ref (not hardcoded `slide2.xml`). Preflight validator added (`preflight_validate()`). Post-build `validate_pptx_layout.py --strict` wired in at end of `assemble()`.
- `Writing/assets/writing_lesson_base.pptx` — all 7 Layout 5 placeholders widened from 2.799" to 3.520" (matching containers). Fixes LO text overflow on long ISB statements.

### Maths
- `Maths/build_lesson_v3.py` — `draw_stm_word_problem_slide` fixed: when `chart_image` key present in VISUALS spec, chart is embedded in right panel. Missing `chart_image` when text references a chart → preflight blocks build.
- `Maths/maths_preflight.py` — new: validates lesson_data.py before build. Checks STM gate, required fields per slide type, text limits, visual references without chart_image, trios chart refs, date consistency.

### Spelling
- `Spelling/spelling_preflight.py` — new: validates lesson.json before node build. Checks cloze collisions, perPairNote empty, verbNoun structure, etymology.baseForm length, syllable break pipe not hyphen, LP field counts, spellData structure.

### Working Memory
- `WorkingMemory/working_memory_starters.py` — TITLE_H and QA_TITLE_H reduced from 1.45" to 1.15". New builds validate clean.

### SKILL.md files updated (delivery gates added)
All nine saved by Innes during this session:
- writing-lesson-pptx — Gate + build_lo fix record + template check step
- maths-complete-planning-and-resources — Gate + STM visual reference rule
- spelling-shed — Gate + fix_pptx_ooxml made mandatory
- working-memory-starters — Gate + title height fix record + sldIdLst fix record
- lo-slides — Gate replacing advisory QA checklist
- rapid-maths — Gate replacing advisory QA checklist
- etiw-dictation — Gate added before Step 5
- writer-planning-overview-and-lesson-sequence — Gate added between Steps 4b and 5
- being-a-reader — Gate added at top of Step 6

---

## Decisions locked in

- Validator reads `sldIdLst` from `presentation.xml`, not the rels file — avoids false positives from orphaned template slides in zip
- `validate_base_template.py` runs on template PPTXs only (not built outputs) — separate concern from post-build validation
- Icon/Fact overlaps in picture_scene working memory slides are intentional — permanently exempted in validator
- `build_lo` Layout 5 detection: scans `_rels/slideN.xml.rels` for `slideLayout5.xml` reference — works regardless of slide file numbering
- STM chart fix: `chart_image` key in VISUALS spec triggers right-panel embed; missing key with chart reference in text → preflight error blocks build
- Demo PPTX files produced in this session are synthetic (python-pptx, not WFA template/fonts) — not representative of real output quality

---

## Specific user requirements

> "This project will be successful if I never see such issues [missing charts, wrong layouts, overflowing text]."

> "When claude is deliberately using a simplified version — just tell me and then I won't worry."

> "I would want to never see such poor quality again. This is a small sample from a massive list."

The testing regime must prove — not just assert — that each fix works on real builds, not synthetic demos.

---

## Loose ends (must be fixed in next session)

### 1. ETIW template off-canvas shapes — CONFIRMED BUG
`easter_etiw.pptx` has 7 shapes on slides 3 and 4 that are 29.269cm wide but the canvas is 27.517cm — shapes extend 1.75cm off the right edge. The validator detects this on the template. The fix is identical to the writing_lesson_base.pptx fix: unzip, find the offending shapes, reduce their cx to fit within 27.517cm (25,171,200 EMU), rezip, normalise through python-pptx, push to GitHub. Then update the ETIW SKILL.md to include validate_base_template.py in session-start.

### 2. Validator hasn't been tested against a real being-a-reader PPTX
Being a reader has a very fixed template and Innes considers it high quality. But it's never been put through the validator. Run it on an existing `BeingAReader_Template.pptx` from GitHub to confirm it's clean or catch any structural issues.

### 3. Rapid Maths — validate_base_template.py not yet run on the template
`rapid_maths_TEMPLATE.pptx` (uploaded by Innes at session start) hasn't been checked for placeholder/container mismatches. Run `validate_base_template.py` on it to confirm clean.

### 4. LP-producing skills not individually tested
`learning-paper` and `being-a-reader` LP outputs haven't been run through the validator since the label_builder.py changes made earlier today. Confirm clean.

---

## Testing regime (to be built and run in the new session)

The new Claude should build a systematic test suite covering:

**A. Validator unit tests** — synthetic PPTX files with known injected errors, confirm each check type fires correctly and clean files pass:
- OFF-CANVAS: shape right edge > canvas width
- TEXT-SPILL: text box too narrow for content
- COLLISION: two overlapping content shapes
- MISSING-VISUAL: slide text says "the chart" with no image
- LAYOUT-MISMATCH: photo on Learning Review layout
- sldIdLst filter: file with orphaned slides only flagged slides in deck order
- Icon/Fact exemption: picture_scene overlap correctly suppressed

**B. Template validator unit tests** — synthetic layouts with known placeholder/container mismatches:
- Narrow placeholder inside wide container → PLACEHOLDER-OVERFLOW flagged
- Correct placeholder widths → clean pass
- `writing_lesson_base.pptx` (fixed) → must pass clean
- `easter_etiw.pptx` → must flag OFF-CANVAS

**C. Preflight unit tests:**
- `maths_preflight.py`: STM gate missing, visual reference without chart_image, date mismatch → errors; clean lesson_data → pass
- `spelling_preflight.py`: cloze collision, perPairNote set, hyphen syllable break → errors; clean lesson.json → pass

**D. End-to-end build tests** (where possible without full lesson data):
- Writing: build a minimal writing lesson using the fixed `build_lesson.py` + fixed `writing_lesson_base.pptx`. Confirm LO slide populates, validator passes.
- Maths: run `maths_preflight.py --all` against the current lesson_data.py in GitHub.
- Spelling: run `spelling_preflight.py` on all lesson JSONs in GitHub.
- Working memory: rebuild T6W1, confirm validator exits 0.

**E. Real asset checks:**
- Run `validate_pptx_layout.py` on `BeingAReader_Template.pptx` from GitHub
- Run `validate_base_template.py` on `rapid_maths_TEMPLATE.pptx` from GitHub
- Run `validate_pptx_layout.py` on `easter_etiw.pptx` to confirm the 7 OFF-CANVAS errors are still present (before fix)

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `Shared/validate_pptx_layout.py` | final — in GitHub | No, fetch from GitHub |
| `Shared/validate_base_template.py` | final — in GitHub | No, fetch from GitHub |
| `Writing/build_lesson.py` | final — in GitHub | No, fetch from GitHub |
| `Writing/assets/writing_lesson_base.pptx` | fixed — in GitHub | No, fetch from GitHub |
| `Maths/build_lesson_v3.py` | final — in GitHub | No, fetch from GitHub |
| `Maths/maths_preflight.py` | final — in GitHub | No, fetch from GitHub |
| `Spelling/spelling_preflight.py` | final — in GitHub | No, fetch from GitHub |
| `WorkingMemory/working_memory_starters.py` | final — in GitHub | No, fetch from GitHub |
| `easter_etiw.pptx` | in skill assets — NOT yet fixed | No, in `/mnt/skills/user/etiw-dictation/assets/` |
| `rapid_maths_TEMPLATE.pptx` | Innes uploads at session start | Yes — needed for validate_base_template check |

---

## Immediate next step

1. Fetch all updated scripts from GitHub using github-sync.
2. Build the testing suite — start with validator unit tests (Section A above) since they require no lesson data and give immediate pass/fail proof. Run them all, report results.
3. Fix the ETIW `easter_etiw.pptx` off-canvas shapes.
4. Run the full end-to-end and real asset checks (Sections D and E).
5. Report a final clean bill of health across all skills.
