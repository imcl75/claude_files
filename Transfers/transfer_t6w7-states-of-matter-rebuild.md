# Transfer: T6W7 States of Matter — MTP mismatch discovered, L1 content rebuild needed

**Generated:** 2026-07-11
**Originating focus:** Continuing `enquiry-lesson-builder` skill work on T6W7 States of Matter (Y4 Chemistry). This session fixed structural bugs (wrong `being_a_scientist` source slide, missing `kq_challenge` slide type, deck order), then discovered the underlying lesson *content* was never real.
**Skill in use:** enquiry-lesson-builder

---

## Status

Two separate problems exist and must not be conflated:

1. **Deck structure/build pipeline** — solid. Three rounds of fixes this session (registry-driven orchestrator, mandatory verifier, anchor-based slide resolution, `being_a_scientist`/`kq_challenge` fix) are pushed to GitHub at commit `f9abe28`. The pipeline itself (`lib_ooxml.py`, `science_registry.py`, `build_science_lesson.py` v4, `verify_lesson.py`) is trustworthy and documented in `EnquiryBuilder/SKILL.md`'s Architecture History (Rounds 1–3).

2. **Lesson content — was fake, just discovered.** `t6w7_l1.json` (the JSON that drives the builder) contains a key question, LO/TIB/ISB, We Do card grid, You Do oobleck provocation, particle-model diagram, and concept-cartoon statements that an earlier Claude session invented from general science knowledge while the pipeline was broken. No session since (including the last one, whose transfer file is the one Innes called "pretty useless") ever checked this against Innes's actual planning document, because Innes had never uploaded it. He uploaded it in this session. It shares almost nothing with what's been built: no KWL diagnostic, an 8-item grid instead of a 15-card sort, an oobleck slide and a particle-model slide that don't exist in the real plan, different LO/TIB/ISB wording throughout.

**Net result: every T6W7 L1 deck delivered so far (including the v4 file just handed to Innes) has the right slide structure and the wrong content.** This has not yet been said to Innes as bluntly as that — say it plainly at the start of the new session.

`generate_mtp.py` in the repo is part of the root cause: it validates an MTP JSON's structure but was being used as if Claude authoring the MTP content itself was normal practice. It isn't. SKILL.md now has an explicit rule against this (see below).

## What's been produced

- `T6W7 - 1 - Mon - States of Matter L1 v4.pptx` — delivered to Innes this session. Structurally correct (being_a_scientist → kq_challenge → discipline → lo → content → concept_cartoon → learning_review, verified, renders clean). Content is the invented placeholder described above — **do not treat this file's content as correct**, only its slide mechanics.
- `EnquiryBuilder/mtp/T6W7_States_of_Matter_Enquiry_Plan.md` in `imcl75/claude_files` — **NEW, pushed this session**. Full transcription of Innes's real 5-lesson MTP (uploaded as a .docx in this chat): all of L1–L5 — learning objectives, phase-by-phase activities, teacher notes, differentiation grid, resources. This is now the source of truth for T6W7 content. Read it before writing any T6W7 lesson JSON.
- `EnquiryBuilder/SKILL.md` — updated with a new "never invent MTP content" rule under Stage 1, and Stage 2's description corrected to stop calling `t6w7_l1.json` a trustworthy worked example. Pushed at `f9abe28`.
- All Round 1–3 architecture fixes (component registry, verifier, `being_a_scientist`/`kq_challenge` fix) — pushed, documented in SKILL.md history. No need to re-derive any of this; read SKILL.md.

## Decisions locked in

- Slide structure for L1: `being_a_scientist` → `kq_challenge` → `discipline` → `lo` → content slides → `concept_cartoon` → `learning_review`. No cover slide, ever — Innes rejected a self-designed one outright.
- `being_a_scientist` clones template slide 3 (anchor `"Areas of Study"`), not slide 2 — slide 2 is a caption, slide 3 has the actual wheel diagrams.
- `kq_challenge` is a real, separate component (was completely missing before this session) — clones template slide 2's nested KQ+Challenge group, strips the leftover 21st-Century-Skills content.
- Every PPTX must pass `verify_lesson.py` (`VERIFY: PASS`) before delivery — not optional.
- MTP content must come from Innes's actual planning document, never invented. Document now saved at `EnquiryBuilder/mtp/T6W7_States_of_Matter_Enquiry_Plan.md`.

## Specific user requirements

> "are you using the MTP for these lessons?" — followed by confirmation that the answer was no, and by "yes, clearly claude's transfer file to this session was pretty useless."

> "record everything you know and need to do and prepare the transfer" — this transfer.

No new build/design instructions were given this session beyond the MTP question — resume by rebuilding content, not by asking Innes to re-explain requirements he's already given multiple times across sessions (see SKILL.md Architecture History for the structural requirements already litigated).

## Files in play

| Path | State | Re-upload needed? |
|---|---|---|
| `EnquiryBuilder/mtp/T6W7_States_of_Matter_Enquiry_Plan.md` (in repo) | Real MTP, all 5 lessons, just added | No — fetch from repo |
| `EnquiryBuilder/t6w7_l1.json` (in repo) | Wrong content, correct structure — needs full content rewrite | No — fetch from repo, then rewrite |
| `EnquiryBuilder/SKILL.md` (in repo) | Current, includes Round 1–3 history + MTP source rule | No — fetch from repo |
| `EnquiryBuilder/{lib_ooxml.py, science_registry.py, build_science_lesson.py, verify_lesson.py}` (in repo) | Working pipeline, no changes needed | No — fetch from repo |
| `EnquiryBuilder/templates/{Being_a_Scientist_slide_deck.pptx, science-example.pptx, KQ_LO.pptx}` (in repo) | Unchanged | No — fetch from repo |
| `T6W7 - 1 - Mon - States of Matter L1 v4.pptx` | Delivered to Innes, wrong content | N/A — will be superseded, not a working file |

## Open questions / blockers

- `science_registry.py`'s current component types (`wedo_hook`, `wedo_grid`, `ido_diagram`, `youdo_provocation`, `youdo_task`) were built around the invented L1 content and don't map cleanly onto the real L1 structure (cold-task KWL → I Do three-object teaching → We Do 15-card sort → You Do independent sorting-table-plus-KWL-update). New component types are likely needed for L1 alone, and L2–L5 need entirely new ones the registry has never had: recap quiz, KWL grid, thermometer practical, bar chart task, cold-glass condensation demo, fair-test investigation. None of this exists yet.
- Whether Innes wants L1 rebuilt on its own first, or wants to see the full L1–L5 JSON plan before any building starts, hasn't been asked.
- Task #11 (PowerPoint repair-dialog root cause) is still open and unrelated to this — don't conflate the two threads.

## Immediate next step

Tell Innes plainly that every T6W7 L1 deck built so far has correct structure but invented content, not content from his real plan (this hasn't been stated this bluntly yet). Then read `EnquiryBuilder/mtp/T6W7_States_of_Matter_Enquiry_Plan.md` from the repo and rebuild `t6w7_l1.json`'s content field-by-field against the real L1 (KQ, LO, TIB, ISB, and every content slide) before touching L2–L5. Decide with Innes whether the existing content component types can be reused/renamed or whether new ones are needed for the KWL/card-sort/three-object structure, update `science_registry.py` accordingly, then rebuild, verify, render, and redeliver L1 before starting L2.
