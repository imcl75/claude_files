# Transfer: T6W3 Maths Resources

**Generated:** 2026-06-15
**Originating focus:** Rebuilding T6W3 maths teaching slides and LPs; significant builder fixes and skill/GitHub restoration.
**Skill in use:** maths-complete-planning-and-resources

---

## ⚠ CLAUDE — READ THIS ENTIRE FILE BEFORE DOING ANYTHING

Do not start any work until you have read every section. Ask Innes any questions you have. Do not assume anything. Do not start building until you are certain you understand exactly what is needed.

**Before building any PPTX:** render a single example slide to PNG in the chat and ask Innes "is this correct?" Wait for explicit approval before building anything else. This is non-negotiable — skipping this step is what caused days of wasted time this week.

---

## Status

T6W3 complete. All four lessons (L9 Mon, L10 Tue, L11 Wed, L12 Thu) built, QA'd and delivered. Multiple builder fixes applied this session. Skill folder and GitHub are both up to date.

## What's been produced

- `/mnt/user-data/outputs/T6W3 - Maths Resources.zip` — final, correct structure:
  ```
  Teaching/
    T6W3 - 1 - Monday - Teaching.pptx
    T6W3 - 2 - Tuesday - Teaching.pptx
    T6W3 - 3 - Wednesday - Teaching.pptx
    T6W3 - 4 - Thursday - Teaching.pptx
  LPs and Resources/
    T6W3 - 1 - Monday - LP.pptx
    T6W3 - 2 - Tuesday - LP.pptx
    T6W3 - 3 - Wednesday - LP.pptx
    T6W3 - 4 - Thursday - LP.pptx
  Labels/
    T6W3 - 2 - Tuesday - Labels.docx
    T6W3 - 3 - Wednesday - Labels.docx
    T6W3 - 4 - Thursday - Labels.docx
  ```
  Monday has no Labels — L9 is Type A (embedded LL, no sticker sheet).

## Decisions locked in

- **Short division grid fix:** blank spacer col 0, divisor col 1, bracket at col 2, dividend cols 2+, ALWAYS one extra blank column on the right: `n_cols = n_div + 2 + (2 if has_rem else 1)`
- **Zip structure:** `Teaching/`, `LPs and Resources/`, `Labels/` subfolders. Zip name: `{TxWy} - Maths Resources.zip`
- **File naming:** `{TxWy} - {N} - {DayName} - Teaching/LP/Labels.ext` where N resets each week (1=Monday, 2=Tuesday etc.)
- **Zip-only delivery** — no individual files alongside the zip
- **LP Type A/B:** L9=Type A (embedded LL). L10/L11/L12=Type B (separate sticker sheets)
- **VAA framework** replaces signal words for all word problem slides
- **Slide types in use:** `word_problem`, `identify_calculate`, `bar_model`, `stm_word_problem` — no `column_calc`
- **Maths timetable:** Mon/Tue/Wed/Fri — no Thursday lessons (T6W3 was Mon/Tue/Wed/Thu as an exception)
- **End of session:** always copy scripts back to skill folder AND push to GitHub — both, every time

## Builder fixes applied this session (do not regress)

- Short division grid: leading blank col added, bus-stop at col 2, extra blank col on right
- `build_lesson_v3.py` updated and saved to skill folder and GitHub
- Skill folder now fully populated (was empty at session start — caused most of today's problems)
- SKILL.md updated with: VAA framework, all slide types, short division spec, STM gate, timetable, file naming, zip structure, visual QA step

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/maths-complete-planning-and-resources/` | Fully populated — all scripts + assets | No |
| `imcl75/claude_files` GitHub repo `Maths/` | Up to date | No |

## Immediate next step

T6W4 maths resources. Before starting:
1. Run environment restore (Step 1 of SKILL.md) — everything is in the skill folder, no GitHub fetch needed
2. Build ONE example teaching slide, render to PNG, show Innes in chat
3. Wait for approval before building anything else
