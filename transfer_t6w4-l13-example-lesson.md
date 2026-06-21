# Transfer: T6W4 L13 Example Lesson Build

**Generated:** 2026-06-21
**Originating focus:** Building a complete example lesson (T6W4 L13, mixed numbers ↔ improper fractions) to test and develop the visual_teach / visual_stm pipeline and fraction_circles visual type.
**Skill in use:** maths-complete-planning-and-resources

---

## Status

L13 complete and delivered. The session was primarily a pipeline development session — new visual type (`fraction_circles`) added to `maths_visuals.py`, two new slide types (`visual_teach` with dict We Do, `visual_stm`) developed and tested, and a full working example lesson produced. Several LP builder fixes landed. All files pushed to GitHub.

## What's been produced

- `T6W4 - Maths Resources (L13 Example).zip` — final, delivered
  - `Teaching/T6W4 - 1 - Monday - Teaching.pptx` — 21 slides, full build
  - `LPs and Resources/T6W4 - 1 - Monday - LP.pptx` — 6 slides (LP1 standard, LP2 standard, LP1 adapted, LP2 adapted, MS1, MS2)
  - `Labels/T6W4 - 1 - Monday - Labels.docx` — Type B sticker sheet

## Decisions locked in

- **`fraction_circles` visual type** added to `maths_visuals.py` — spec: `{type, denominator, total, color, show_labels, total_label, max_per_row}`. Shows n/d as a row of circles with wedge sectors, full circles for wholes and a partial circle for remainder. Ideal for mixed number ↔ improper fraction teaching.
- **`visual_stm` slide type** — error authored INTO the visual spec. `error_instruction` always visible (red). `error_correction` (str or dict with text + visual) animated click-reveal (green). Both `c1_ido2` and `c2_ido2` now route through `build_teaching_slide` dispatcher.
- **`visual_teach` We Do with dict** — `we_do` key accepts str (backward-compatible) or `{visual: spec, text: '...'}`. Different representation from I Do on same slide. Multi-shape animation: all We Do elements (bg + pic + text) reveal together on one click.
- **Animation sequence** for `visual_teach`: visual always visible; each talk prompt click-reveals on its own click; We Do reveals on final click. This IS working in the PPTX XML — LibreOffice renders show everything visible (cannot show animation). Confirmed via XML inspection that all shape IDs are in `bldLst`.
- **LP type for fraction conversion = `'arithmetic'`** (not `'word_problems'`). This routes through the full-page separate-slide path (isArithmetic=true), giving 6 slides total. Using `'word_problems'` as type falls into the non-arithmetic half-page path which causes overlap.
- **`repsPerQ=1` forced for arithmetic/word_problems LP type** in both `_buildLP1WordProblems` and `_buildLP1WordProblemsAdapted`.
- **`repH` fix in `_buildLP1WordProblemsAdapted`** — was calculated as `rightContentH + CUT_GAP` (tiny, based on hint boxes). Fixed to `usable / repsPerQ` (full page). Enables adapted LP visuals to actually fit.
- **`MAX_STRIP` raised to 2.20"** when adapted questions have visuals (was 1.10").
- **Adapted LP questions** go in `adaptedSupport.lp1Questions` / `adaptedSupport.lp2Questions`, NOT in `lp1.adaptedQuestions`. The builder reads `ADAPTED_SUPPORT.lp1Questions`.
- **Hint key is `hint1`** (not `hint`). `ADAPTED_SUPPORT.hint1` → "Step-by-step:" box on right column.
- **Representation variety rule** (Innes's feedback): I Do and We Do on same slide should use different visual types. STMs may keep circles since the visual specifically disproves the error. Established pattern: circles (I Do) → bars (C1 We Do) → circles (STM) → circles (I Do) → number line (C2 We Do) → circles (STM).

## Specific user requirements

> "The capability to render different versions of the representations is critical e.g. I do with fraction representations of 2/3 then we do with representations of 3/5. These are just EXAMPLES — do not build this in a rigid manner."

> "it would be better to have some variety in representations (on the same slides and across different slides) rather than them all being circles showing fractions"

> "The learning papers don't seem to have any representations on them — might be intentional for this lesson? — but the spacing on the learning papers is really big so that's either wrong or the representation is missing."
(Response: adapted LP now has fraction circles on Q1/Q2. Standard LP has large spacing intentionally — Type B, pupils write working in books. Spacing is correct.)

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/maths-complete-planning-and-resources/maths_visuals.py` | updated — fraction_circles added | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/build_lesson_v3.py` | updated — visual_stm dispatcher, We Do with dict, c2_ido2 routing | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/build_lp_v3.js` | updated — arithmetic/word_problems dispatch, repsPerQ, repH, MAX_STRIP fixes | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/lesson_data.py` | L13 example data — fraction_circles + variety | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/lesson_data.js` | L13 example data — adaptedSupport.lp1Questions/lp2Questions | No |
| GitHub `imcl75/claude_files` | all above pushed, latest commit: `67d1de8` | No |

## Open questions / blockers

- **Standard slides (WM, vocab, learning review) not fully tested** — the test lesson_data.py stub has minimal data. These slides work correctly in production builds. No code fix needed, but the test lesson data should be replaced with proper production data for any real lesson.
- **Number line marker for 11/3 in We Do** — renders small at LibreOffice preview size. Readable in PowerPoint at full slide size. No fix needed unless Innes flags it in PowerPoint.
- **LP2 adapted visuals** — the `buildLP2ArithmeticAdapted` function was updated to use `ADAPTED_SUPPORT.lp2Questions` but the repH/MAX_STRIP fixes may need verifying for LP2 adapted if it also uses `_buildLP1WordProblemsAdapted` (it does — same function, confirmed working).
- **T6W4 L14–L16 not yet built** — only L13 was produced as an example.

## Immediate next step

If continuing to build T6W4: author `lesson_data.py` and `lesson_data.js` for L14 (adding fractions with same denominator, crossing the whole), then build the full 4-lesson week. Run Step 1 (environment restore from skill folder) before building anything. Dates for T6W4: Mon 23 Jun (L13, done), Tue 24 Jun (L14), Wed 25 Jun (L15), Fri 27 Jun (L16).

If beginning a new topic: no immediate action — the pipeline updates are all saved and pushed.
