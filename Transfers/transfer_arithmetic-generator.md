# Transfer: Arithmetic Generator bug fixes (indices + percentages)

**Generated:** 2026-07-11
**Originating focus:** Fixing indices superscript rendering gap and making percentages Y6-only in the KS2 arithmetic paper generator tool.
**Skill in use:** none (direct code editing)

---

## Status

Both issues fixed and pushed as **11.07.26u**. No further issues are pending from this session. A long multi-session series of curriculum-scope fixes is now largely complete; the tool is stable but an audit of all Y3/Y4/Y5 tagged number ranges has not been done exhaustively.

## What's been produced

- `/Users/innes/projects/staff-tools/arithmetic-generator/index.html` — current working file, version **11.07.26u**, pushed to `wallscourtfarm/staff-tools` on GitHub

## Decisions locked in

- **Indices fix**: wrapped text and box question eqHTML in a `<span>` so the entire formula is one flex child of `.q-header` — eliminates the 3mm flex gap that was splitting `7` from `²`
- **Y5 percentages removed**: `y5Percentages` topic checkbox deleted from UI; all four percentage slots in `genY5Arith` fall through to `tt()` since `t.y5Percentages` is now always falsy
- **Y6 generator percentage retagged**: `yg:'Y5'` → `yg:'Y6'` on the `pct% of a =` slot in the Y6 generator's Y5 band; fallback also changed from `tf('Y5')` → `tf('Y6')`
- **Percentages are Y6-only content** at WFA — user confirmed: "we tend to only teach it in Y6"
- **Y6 new arithmetic content** = long division, BODMAS with indices/brackets, dividing fractions only (long multiplication is Y5 and was retagged in a prior session)
- **Y3 curriculum**: ×2/4/5/8/10 tables only; division within known table facts + partition-friendly (quotient 12–20, dividend ≤200)
- **Y3 number range**: all Y3-tagged questions must use numbers ≤999
- **Y4 number range**: ≤9,999 (4-digit)
- **Y5 number range**: ≤999,999

## Specific user requirements

> "indices still formatted incorrectly. Lets make % just year 6 too as we tend to only teach it in Y6"

> "Y6 new arithmetic content is really only long division, bodmas, dividing fractions"

> "if you use a number >1000 its not a year 3 question!"

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/Users/innes/projects/staff-tools/arithmetic-generator/index.html` | final, v11.07.26u | No — on disk and pushed |

## Open questions / blockers

- **Full Y3/Y4 number-range audit not done**: bugs have been found one at a time across sessions; a systematic pass checking every Y3-tagged slot for values >999 and every Y4-tagged slot for values >9,999 has not been completed — more lurking bugs are possible
- **Y4 and Y5 standalone papers don't yet have `yg` tags or score strips** — this was planned but never implemented (Y6 paper has the full Y3/Y4/Y5/Y6 band system; standalone papers don't)

## Immediate next step

If continuing: do a systematic audit of all `yg:'Y3'` and `yg:'Y4'` tagged slots in `genY6Arith` and all number-generating lines in `genY3Arith` / `genY4Arith` to confirm no number-range violations remain. Or if the user has a new issue to fix, pick that up directly.
