# History Enquiry Builder — Correct Transfer
# Session 15 -> Session 16 (written 2026-07-21, corrected 2026-07-22)

## THE SINGLE MOST IMPORTANT FACT

The History slide visual specification is COMPLETELY UNKNOWN to Claude.

Do not guess. Do not infer from code. Do not assume it matches Science or Geography.

## What Innes will bring to session 16

Innes will provide a History lesson PPTX slide deck at the start of the session.
This is the reference — the correct output. Claude's job is to read it and extract
the full visual specification from it.

## What to do at the start of session 16

Step 1: Wait for Innes to provide the slide deck (PPTX upload or file path).
Step 2: Read the PPTX — unzip it and inspect the XML of every slide.
Step 3: For every slide type present, extract and record:
  - Layout name (from slideLayout ref)
  - All shape positions (x, y, cx, cy in EMUs — read from spPr/xfrm)
  - All font sizes (from rPr sz= attributes, in hundredths of a point)
  - All colours (from solidFill/srgbClr hex values)
  - Text content structure (which shape has what role, paragraph order)
  - Animation XML (grpId present?, bldLst present?, nodeType values, order of effects)
  - Whether slide is clone-from-template or fresh build (infer from structure)
  - Placeholder indices (ph idx= values)
Step 4: Write claude/visual-spec-history.md to the project with the same level
  of precision as claude/visual-spec-science.md and claude/visual-spec-geography.md.
  Exact numbers. No approximations. No "similar to Science" guesses.
Step 5: Confirm with Innes that the spec matches what he sees.
Step 6: Only then proceed to building or fixing any History lessons.

## What NOT to do

- Do not build L01 before seeing the reference deck
- Do not assume History animation uses grpId or bldLst — find out from the XML
- Do not infer spec from build_history_lesson.py — the code may be wrong
- Do not do LP docs, KO docs, or day_label updates until slides are confirmed

## Known outstanding History issues (deal with after spec is confirmed)

- day_label fields in Roman Civilisation data are placeholder ("Day 1"..."Day 14")
- LP generation not wired into History build loop
- LL sticker sheets for History not built
- Three-level LP (standard/adapted/further_adapted) not implemented for History

## Pipeline status (session 16)

Science:   Builder working. Visual spec LOCKED in claude/visual-spec-science.md
Geography: Builder working. Visual spec LOCKED in claude/visual-spec-geography.md
History:   Builder exists. Visual spec UNKNOWN — extract from Innes's reference deck.

## Save and sync rule

Every significant output goes:
  1. Saved as a file in /home/claude/
  2. Sent to Innes via SendUserFile immediately
  3. Pushed to GitHub via github-sync skill

No exceptions. Context compaction can start at any moment.
