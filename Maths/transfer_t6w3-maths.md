# Transfer: T6W3 Maths Resources

**Generated:** 2026-06-17
**Originating focus:** Building and fixing T6W3 maths teaching slides, LPs and labels across multiple sessions.
**Skill in use:** maths-complete-planning-and-resources

---

## ⚠ READ THIS ENTIRE FILE BEFORE DOING ANYTHING

Do not start any work until you have read every section. Ask any questions first. Do not build anything until you are certain you understand what is needed.

**If no transfer file exists in a future session:** ask Innes what week/lessons are needed, confirm the day dates, and ask if there are any changes from the previous build before touching any files.

**Before building anything:** run Step 1 (environment restore), then build ONE example slide, render to PNG in the chat, and wait for Innes's explicit approval before building anything else.

---

## Status

T6W3 complete. All four lessons built, QA'd and delivered. All builders, lesson data, and SKILL.md saved to skill folder and GitHub.

## What's been produced

Final zip: `T6W3 - Maths Resources.zip`

```
Teaching/
  T6W3 - 1 - Monday - Teaching.pptx
  T6W3 - 2 - Tuesday - Teaching.pptx
  T6W3 - 3 - Wednesday - Teaching.pptx
  T6W3 - 4 - Friday - Teaching.pptx
LPs and Resources/
  T6W3 - 1 - Monday - LP.pptx
  T6W3 - 2 - Tuesday - LP.pptx
  T6W3 - 3 - Wednesday - LP.pptx
  T6W3 - 4 - Friday - LP.pptx
Labels/
  T6W3 - 2 - Tuesday - Labels.docx
  T6W3 - 3 - Wednesday - Labels.docx
  T6W3 - 4 - Friday - Labels.docx
```

Monday is Type A (no label sheet). Maths timetable is Mon/Tue/Wed/Fri — no Thursday.

## Decisions locked in

**Teaching slides:**
- All word problem slides use blank problem slide layout: problem text left + VAA banners (animated) + large blank squared paper right (11×10 cells, 0.597")
- No calculations drawn, no bar models drawn — Innes does all working live
- VAA banners animated: Visualise (click 1), Analyse + "I know / I'm finding" (click 2), Attack + operation labels (click 3)
- `sync_past(pic_id)` required after every `add_pic_id` call — keeps nid() counter in sync with python-pptx auto-assigned IDs
- Grid drawn LAST so raw-XML IDs never clash with animated shape IDs
- `sp()` supports `autofit=True` — problem text uses this

**Short division grid:**
- `n_cols = n_div + 2 + (2 if has_rem else 1)` — always one extra blank col on right
- Col 0: blank spacer, Col 1: divisor, Cols 2+: dividend, bus-stop at col 2

**Compact LP layout (all T6W3 LPs use compact: true):**
- `repsPerPage = floor(usable / repH)` — never fixed, always calculated from content height
- Marking station: 1 rep only
- LP1 (has goingFurther): instruction in strip + small Q gaps + purple GF box on right
- LP2 (no goingFurther): NO instruction in strip + zero Q gaps (~0.02") + instruction text in plain grey box on right
- LP2 dispatch: `_buildCompactWithData(slide, isMarkingStation, LP2_DATA)` — never reassign LP1_DATA const
- Column positions: left x=0.23" w=4.363", right x=4.894" w=2.337" h=0.81"
- Question font 10pt, title 13pt bold, instruction 9pt grey

**Zip and naming:**
- `{TxWy} - Maths Resources.zip`, subfolders `Teaching/`, `LPs and Resources/`, `Labels/`
- Files: `{TxWy} - {N} - {DayName} - Teaching/LP/Labels.ext`

**Language:** No "carry/carrying" (use regroup), no "bar model" references anywhere.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/maths-complete-planning-and-resources/` | Fully populated | No |
| `imcl75/claude_files` Maths/ | Up to date | No |

## Open questions / blockers

- bar_model slide with column_subtraction/multiplication calc methods not tested — may need checking in T6W4+
- Grid Method and Expanded/Compact Column multiplication not verified against reference layouts

## Immediate next step

T6W4 maths. Run environment restore (Step 1 of SKILL.md) — everything is in skill folder, no GitHub fetch needed. Build ONE example slide, render to PNG, show Innes, wait for approval before building anything else.
