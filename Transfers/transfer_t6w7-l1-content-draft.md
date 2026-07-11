# Transfer: T6W7 States of Matter — MTP now confirmed, L1 content drafting is next

**Generated:** 2026-07-11
**Originating focus:** Continuing `enquiry-lesson-builder` skill work on T6W7 States of Matter (Y4 Chemistry). This session corrected a chain of wrong assumptions about which MTP is authoritative, and got the real one confirmed by Innes.
**Skill in use:** enquiry-lesson-builder

**This transfer supersedes `Transfers/transfer_t6w7-states-of-matter-rebuild.md`. That file is now wrong — it says a docx Innes uploaded was his own real planning document. It wasn't. Ignore that transfer entirely; this one has the corrected state.**

---

## Status

Three MTPs have existed for this unit across sessions, and getting this straight took most of this session:

1. **Invented placeholder** — the content in `t6w7_l1.json` today. Written by an earlier Claude session with no real source, silently treated as fact by every session since. Still sitting in `t6w7_l1.json`, still wrong, not yet overwritten.
2. **"Draft A"** — a docx Innes uploaded mid-session. Assumed (wrongly, by this session, initially) to be Innes's own external planning document. It was actually *also* Claude-authored, from a different prior session, never confirmed by Innes. Now saved at `EnquiryBuilder/mtp/T6W7_draft_A_NOT_IN_USE.md` — kept for reference only, **do not build from it**.
3. **"Plan B" — the confirmed one.** Pasted by Innes from a separate Claude chat where it was proposed but never actioned. Innes explicitly confirmed this is the one to use (via a direct choice between four options, including "neither, I have the real plan" and "write a new one together" — he picked Plan B over both). Saved at `EnquiryBuilder/mtp/T6W7_MTP.md`, marked CONFIRMED with today's date.

**Deck build pipeline is unaffected by any of this and remains solid** — registry-driven orchestrator, mandatory verifier, `being_a_scientist`/`kq_challenge` fix, all from Rounds 1–3 this session, pushed and documented in SKILL.md. Nothing about the pipeline needs revisiting. The only outstanding work is content: rewrite `t6w7_l1.json` (and then L2–L5) against `T6W7_MTP.md` instead of the placeholder.

**Important nuance about Plan B:** it is a summary-level MTP — learning objectives, phase headlines (recall / I Do / We Do / provocation / You Do), and an image-generation plan per lesson. It does **not** contain scripted slide text, provocation question wording, or exact card-sort item lists the way the discarded Draft A did. Slide-level content still needs to be drafted from these headlines and shown to Innes before building, not invented wholesale and delivered.

## What's been produced

- `EnquiryBuilder/mtp/T6W7_MTP.md` — **the confirmed MTP**, all 5 lessons, LOs + phase headlines + image plan. Read this first.
- `EnquiryBuilder/mtp/T6W7_draft_A_NOT_IN_USE.md` — discarded, do not use, kept only so nobody re-derives it from scratch by mistake.
- `EnquiryBuilder/SKILL.md` — corrected. Stage 1 now explains the three-MTP history and the actual rule: never build from a document just because it exists as a file — confirm with Innes explicitly first. Stage 2 points at `T6W7_MTP.md` and flags it as summary-level.
- Everything from Rounds 1–3 (unaffected): `lib_ooxml.py`, `science_registry.py`, `build_science_lesson.py` v4, `verify_lesson.py`, the `being_a_scientist`/`kq_challenge` fix. All pushed, all documented in SKILL.md's Architecture History.
- `T6W7 - 1 - Mon - States of Matter L1 v4.pptx` — delivered earlier this session. Correct slide mechanics, content is the invented placeholder (item 1 above). Not usable once L1 is rebuilt against `T6W7_MTP.md` — will be superseded, don't reference its content for anything.

## Decisions locked in

- `T6W7_MTP.md` (Plan B) is the confirmed source for all 5 lessons. No fair test / investigation outcome this unit — Draft A had one, Plan B doesn't, don't reintroduce it.
- Key question: "Can materials change their state?"
- No cover slide, ever. Deck structure stays: `being_a_scientist` → `kq_challenge` → `discipline` → `lo` → content slides → `concept_cartoon` → `learning_review`. (Note: `T6W7_MTP.md` doesn't mention a concept cartoon or a discipline-specific slide explicitly — check with Innes whether these still apply given Plan B's structure, since Plan B was authored independently of this skill's slide-type conventions.)
- Every PPTX must pass `verify_lesson.py` (`VERIFY: PASS`) before delivery.
- Before building from any MTP file found in `EnquiryBuilder/mtp/`, confirm with Innes it's the one he wants used — a file existing there is not itself confirmation (this is exactly the mistake made with Draft A).

## Specific user requirements

> "claude made that plan. OK, it got lost." — about Draft A, correcting the assumption it was Innes's own document.

> Chose "Plan B (just pasted)" when asked directly which MTP to build from, over "Plan A (the docx)", "Neither, I have the real plan", and "Write a new one together now".

> "does it make sense for you to do that here or in the transferred session? you will need to create a new transfer file" — Innes explicitly wants L1 content drafting to happen in the new session, not this one.

## Files in play

| Path | State | Re-upload needed? |
|---|---|---|
| `EnquiryBuilder/mtp/T6W7_MTP.md` (in repo) | Confirmed MTP, summary-level, all 5 lessons | No — fetch from repo |
| `EnquiryBuilder/mtp/T6W7_draft_A_NOT_IN_USE.md` (in repo) | Discarded, reference only | No — do not use |
| `EnquiryBuilder/t6w7_l1.json` (in repo) | Wrong content (invented placeholder), correct JSON structure | No — fetch, then rewrite content only |
| `EnquiryBuilder/SKILL.md` (in repo) | Current, corrected MTP-source history | No — fetch from repo |
| `EnquiryBuilder/{lib_ooxml.py, science_registry.py, build_science_lesson.py, verify_lesson.py}` (in repo) | Working pipeline, no changes needed | No — fetch from repo |
| `EnquiryBuilder/templates/*.pptx` (in repo) | Unchanged | No — fetch from repo |
| `T6W7 - 1 - Mon - States of Matter L1 v4.pptx` | Delivered, wrong content, will be superseded | N/A |

## Open questions / blockers

- L1 slide-level content (We Do 8-item grid labels, particle model bullet text, oobleck provocation phrasing, 12-card sort list with reasons) needs drafting from `T6W7_MTP.md`'s headlines and should be shown to Innes before building — Plan B doesn't specify exact wording.
- Whether `kq_challenge`, `discipline`, and `concept_cartoon` slide types (part of this skill's established L1 structure) still belong in a deck built from Plan B, which doesn't mention them, needs checking with Innes rather than assumed.
- `science_registry.py`'s component types were built around the discarded invented content — confirm they still fit Plan B's phase structure (recall / I Do / We Do / provocation / You Do) before reusing them as-is.
- 19 images needed across the week (13 Higgsfield `nano_banana_pro`, 4 dall-e) — none generated yet.
- Task #11 (PowerPoint repair-dialog root cause) still open, unrelated to any of this.

## Immediate next step

Read `EnquiryBuilder/mtp/T6W7_MTP.md` from the repo, draft L1's slide-by-slide content (We Do grid items, particle model bullets, oobleck provocation text, 12-card sort list with reasons) against it, and show Innes the draft before generating any images or building. Confirm with him whether `kq_challenge`/`discipline`/`concept_cartoon` still belong in the deck given Plan B doesn't mention them. Only after content is approved: generate images, build, verify, deliver.
