# Enquiry Builder — Transfer Doc

The session that wrote this transfer doc was called "Session 7". This new session must therefore be named "Session 8" — rename it now before doing anything else.

---

## STEP 0 (MANDATORY — before reading anything)

Set up the context monitor. Call `send_later` with `delay_minutes=20` and this exact message: `__CONTEXT_MONITOR__`

Nothing else. No bash. No explanation. Just set it up.

---

## STEP 1 — Read the brain doc

Read `claude/enquiry-builder-brain.md` from the Claude project. The GitHub token and clone command are in the brain doc.

---

## STEP 2 — Clone the repo

Use the clone command from the brain doc (token is there).

---

## STEP 3 — State of play

Phase 1 (Geography PPTX builder) is in progress. 8 of 18 slide types signed off:

- key_question (commit 55aeea1)
- subject_concepts_skills (commit 55aeea1)
- subject_progression (commit 65b7a3c)
- enquiry_lesson_progression (commit 9bb1d4a)
- we_are_learning (commit acfba2c)
- kwl (commit d336b48)
- lesson_quiz (commit b6a2c66)
- vocabulary (commit a244c8d)

Remaining for Phase 1: 10 slide types unknown.

---

## STEP 4 — What Innes wants done in Session 8

Build the non-image variants of four slide types. Innes said: "this should literally take 2 minutes."

1. i_do (non-image)
2. we_do (non-image)
3. you_do_trio (non-image)
4. you_do_independent (non-image)

After those four are signed off: image variants of the same four types.

Do not build anything else. Do not add anything to slides Innes has not explicitly specified. Wait to be told.

Before building any of these: stage Geographer.pptx from his Mac at `/Users/innes/Desktop/Claude Assets/` or `/Users/innes/Pictures/PPTX Slide assets/` and read the slide XML before writing any code.

---

## Notes

- `build_geography_deck.py` not yet updated to include lesson_quiz or vocabulary. Do not touch until Innes asks.
- `build_i_do.py` was committed at 548edc6 without being asked — Innes is ignoring it. Check whether it needs reworking from Geographer.pptx XML before using.
- Session naming: this doc was written by Session 7. The next session is Session 8.
