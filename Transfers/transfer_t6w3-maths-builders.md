# Transfer: T6W3 Maths Resources + Builder Fixes

**Generated:** 2026-06-15
**Originating focus:** Building T6W3 maths teaching slides and LPs; multiple builder fixes applied and locked into skill/GitHub.
**Skill in use:** maths-complete-planning-and-resources

---

## Status

T6W3 complete. All four days (L9 Mon, L10 Tue, L11 Wed, L12 Thu) built, QA'd, zipped and delivered. Significant builder fixes were made across LP layout, teaching slide animations, and calculation grid rendering. All fixes pushed to GitHub and written into SKILL.md.

## What's been produced

- `/mnt/user-data/outputs/T6W3 - Maths Resources.zip` — final, contains:
  - Teaching PPTXs: L9–L12
  - LP PPTXs: L9–L12
  - Label sheets: L10–L12
  - Sort cards PDF (Mon+Tue reuse)

## Decisions locked in

**LP layout rules (now in SKILL.md):**
- LL rule: LP1 = LL on EVERY rep (each rep = one child's cut strip). LP2 = NO LL ever.
- Cut marks only at rep boundaries, never between individual questions.
- CUT_GAP = 0.20" (0.28" adapted), split either side of cut line.
- All right-column boxes (GF, instruction, hints) sized to content via `estimateRightColH` with 0.70 char-width factor. Box labels placed separately — box height does NOT subtract label height.
- Title and instruction on every rep (self-contained strips).
- Standard LP1 repsPerQ=2, LP2 TARGET=3 (pedagogical, fixed).
- Adapted LP rep count is fully dynamic: rightContentH drives repH, repsPerQ = floor(usable/repH), capped at 4.
- GF box in right column below LL (not in left column).
- LP2 right column: instruction box (content-sized), no LL.
- Adapted LP2: no LL; hints repeated on every rep.

**Teaching slide animation rules (now in SKILL.md):**
- ALL word problem slide functions must have full VAA animations: Visualise → Analyse → Attack → Step2+Calc → Answer.
- `_apply_animation` called UNCONDITIONALLY. Answer always in anim_groups.
- `draw_identify_calculate_slide`: was missing Visualise + had no animations at all — now fixed.
- `draw_bar_model_slide`: Answer was not animated for mental calc — now fixed.
- For grid-based calculations: Step2Lbl + ALL grid digits appear as ONE animation group (single click). Nothing hides progressively within the calculation.

**Calculation grid layout (now in SKILL.md):**
- Grid placed in RIGHT AREA of slide (grid_x = px + pw + 0.40) when calc_method requires a grid. Left panel free for VAA banners.
- Cell size auto-scaled to fill right area: CELL_BIG = min(1.20, avail_h / est_rows × 0.70), DIGIT/CARRY sizes scaled proportionally.
- `draw_squared_paper` rewritten from reference file `layouts_for_methods.pptx`:
  - Short division: 4 rows (quotient, dividend, 2 blank); bus-stop bracket; remainder superscripts in red; quotient in green.
  - Column addition: 5 rows (carry, top, op+bot, answer, blank); double lines above/below answer row.
  - Column subtraction: 5 rows; borrow notation in red above top number.
  - ALL digit shapes returned in single animation group.
- `ROWS_BY_METHOD`: short_division=4, column_addition=5, column_subtraction=5, column_multiplication=6.

**Sort cards:**
- No operation symbols on cards — they defeat the purpose. Numbered (Problem 1–8) only.
- Write-on boxes: "Operation: ___" and "Signal word/phrase: ___".

**Trios/independent resource rule:**
- Physical sort activity → build separate resource.
- Screen discussion → author problems into trios slide text.
- LP transition → independent slide matches LP content; LP preview slide follows.

**Signal word definition:** "A word in a problem that gives clues as to which operation to use."

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/maths-complete-planning-and-resources/SKILL.md` | Updated with all session rules | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/build_lesson_v3.py` | Updated (animations, grid, layout) | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/build_lp_v3.js` | Updated (LL rule, rep layout, adapted) | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/inject_lp_previews.py` | Updated (smart crop from metadata) | No |
| `/mnt/skills/user/maths-complete-planning-and-resources/maths_plan_v3.json` | T6W3 L9–L12 complete | No |
| GitHub `imcl75/claude_files` Maths/ | All builders current as of final push | No |

## Reference file

Innes uploaded `layouts_for_methods.pptx` containing exact reference layouts for:
- Slide 1: Grid Method
- Slide 2: Expanded Column Method
- Slide 3: Compact Column Method
- Slide 4: Column Addition
- Slide 5: Column Subtraction
- Slide 6: Short Division

Key measurements extracted: CELL=0.5972", DIGIT_SZ=32pt, CARRY_SZ=20pt, problem text 36pt.
If grid rendering issues arise, re-check against this file. It is NOT in GitHub — Innes would need to re-upload it if needed.

## Open questions / blockers

- `draw_bar_model_slide` column_subtraction and column_multiplication calc methods not tested this session — may need checking if those lesson types appear in T6W4+.
- Grid Method (`calc_type='grid'`) and Expanded/Compact Column (`calc_type='column_multiplication'`, `'expanded_column_mult'`) not yet rewritten to match reference — only short_division and column_addition/subtraction were confirmed broken and fixed.
- T6W4+ resources not yet started.

## Immediate next step

Start T6W4 maths planning. Run environment restore (Step 1 of SKILL.md) — fetch all builders from GitHub at session start before building anything.
