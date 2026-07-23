# Transfer: Enquiry Builder Phase 1

**Generated:** 2026-07-23
**Originating focus:** Foundation session — establishing the brain doc, MTP JSON schema, and slide type palette for the Enquiry Builder.
**Skill in use:** none (foundation/schema work only)

---

## Status

Phase 0 complete and confirmed by Innes. Brain doc written and saved to the project (`claude/enquiry-builder-brain.md`). No scripts written yet. Phase 1 starts next: build the geography PPTX builder script.

## What's been produced

- `claude/enquiry-builder-brain.md` (project doc) — final, confirmed

## Decisions locked in

- MTP JSON schema is universal across all subjects. Optional fields are omitted where not needed; the builder never errors on a missing optional field.
- `strand`, `substantive_concept`, `skill_focus` are the universal field names for subject-specific metadata — same names for all subjects, omit if not needed.
- Slide types are a palette — the lesson JSON drives which slides appear and in what order. No fixed default deck per lesson.
- Canonical slide type palette locked: `key_question`, `subject_concepts`, `subject_progression`, `enquiry_lesson_progression`, `we_are_learning`, `kwl`, `lesson_quiz`, `vocabulary`, `i_do`, `i_do_image`, `we_do`, `we_do_image`, `you_do_trio`, `you_do_trio_image`, `you_do_independent`, `you_do_independent_image`, `concept_cartoon`, `learning_review`
- Image slides use a `layout` field + `images` array (not a single `image_path`). Nine layouts: `full_bleed`, `hero_left`, `hero_right`, `double_stack_left`, `double_stack_right`, `diagram_focus`, `horiz_small_squares`, `horiz_small_squares_2row`, `central_wide`
- All technical implementation decisions are made independently — only ask Innes about content and design choices that affect what he sees.

## Specific user requirements

> "Always number your questions so when I respond I can number my responses — no room for confusion."

> "If it's a technical consideration then I don't (ever) care — you decide what will work best."

- Never ask Innes to upload a file — everything needed is in the repo.
- Never mark a phase complete without a real output file Innes has opened and confirmed correct.
- Never start Phase N+1 before Phase N gate is passed.
- Phase 0 gate ✅ passed.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `mtp/reference/england_brazil_mtp.json` | locked reference, do not edit | No — in repo |
| `mtp/reference/y5_astronomy_mtp.json` | locked reference, do not edit | No — in repo |
| `config/class_config.json` | placeholder | No — in repo |
| `assets/geography/` | template PPTX, fonts, progression images, jigsaw pieces | No — in repo, not yet inspected |
| `scripts/` | empty — no scripts written yet | No |

## Open questions / blockers

- Contents of `assets/geography/` not yet inspected — must do this before writing any Phase 1 script.
- Image slide layout exact pixel/EMU dimensions not yet established — will emerge during Phase 1 when template PPTX is inspected.

## Immediate next step

Follow the session start protocol in the brain doc. Then inspect `assets/geography/` in the repo to catalogue what template files exist (PPTX, images, fonts). Use what's there to build a script that takes one lesson's JSON and produces a PPTX deck. Phase 1 gate: one lesson deck produced and confirmed correct by Innes.
