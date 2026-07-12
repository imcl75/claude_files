# Transfer: Enquiry Lesson Builder — Priority 2 (Geography/History)

**Generated:** 2026-07-12
**Originating focus:** Extending the enquiry-lesson-builder skill beyond science to Geography and History subjects.
**Skill in use:** enquiry-lesson-builder (extended)

---

## Status

Priority 1 (LP generation wired into enquiry-lesson-builder) is complete and pushed to GitHub. All T6W7 States of Matter science lessons (L1–L5) have been built and delivered: 5 teaching PPTXs in `T6W7/Enquiry/Teaching/`, 5 LP PPTXs in `T6W7/Enquiry/LPs/`. Priority 2 (Geography/History registry) is next — Innes said "we need to plan together first" before building, so this transfer opens at the planning conversation.

---

## What's been produced

- `EnquiryBuilder/build_science_lesson.py` — final, pushed to GitHub. Contains `quiz_recap` monkeypatch + `build_quiz_recap()` function.
- `EnquiryBuilder/quiz_recap_template.pptx` — final, pushed to GitHub. Clone source for quiz slides (whiteboard/pen image, Content Placeholder 2, paragraph-reveal animations).
- `EnquiryBuilder/t6w7_l1.json` through `t6w7_l5.json` — pushed to GitHub, **but** t6w7_l1.json on GitHub still has old image paths (`/tmp/t6w7/images/`) which are broken. The working version with correct paths (`/sessions/admiring-sleepy-wozniak/images/`) is only in the outputs folder. **Push the corrected t6w7_l1.json to GitHub before rebuilding L1.**
- `T6W7/Enquiry/Teaching/` — 5 lesson PPTXs (L1–L5, States of Matter), all verified
- `T6W7/Enquiry/LPs/` — 5 LP PPTXs (L1–L5, States of Matter)

---

## Architecture — how the builder currently works

The skill lives at `/mnt/skills/user/enquiry-lesson-builder/` (or `/sessions/.../mnt/.claude/skills/enquiry-lesson-builder/`).

Key files on GitHub (`imcl75/claude_files`, `EnquiryBuilder/` folder):
- `build_science_lesson.py` — main orchestrator; dispatches slide components
- `science_registry.py` — component registry (defines valid components + their fields)
- `lib_ooxml.py` — shared OOXML helpers (clone, find_sp, xr, etc.)
- `build_lp.py` — LP PPTX builder (wired into build_science_lesson.py's `build_lesson()`)
- `quiz_recap_template.pptx` — clone source for quiz slides
- `t6w7_l1.json` … `t6w7_l5.json` — lesson specs (component order + content)
- Various template PPTXs for other components

**Component dispatch pattern (in build_science_lesson.py):**
```python
DISPATCH = {
    'lo': lambda work, templates, layouts, spec: build_lo_slide(...),
    'quiz_recap': lambda work, templates, layouts, spec: build_quiz_recap(work, templates['quiz_recap'], spec),
    'concept_cartoon': lambda ...,
    ...
}
```

`quiz_recap` was added via monkeypatch after `import science_registry as REG`:
```python
REG.COMPONENTS['quiz_recap'] = {
    'presence': 'optional', 'mode': 'fresh_quiz',
    'fields': ['qna'],
}
```

---

## Decisions locked in

- Folder structure for enquiry outputs: `TnWn/Enquiry/Teaching/` (lesson PPTXs), `TnWn/Enquiry/LPs/` (LP PPTXs), `TnWn/Enquiry/Resources/` (other resources)
- Quiz recap slide: always comes after LO, before concept cartoon; L1 has no quiz (nothing to recap)
- Concept cartoon: in every lesson (L1–L5); content created by Claude, not supplied by Innes
- Quiz animations: paragraph-by-paragraph click reveal; Q paragraphs normal weight, A paragraphs bold green (`00B050`) with Wingdings arrow prefix (``)
- LP output path: `TnWn/Enquiry/LPs/`, not Teaching

---

## Specific user requirements

> "the slides for lesson 2 onwards should always have a quiz to recap the prior learning from the enquiry — key facts and knowledge from the previous lesson(s)"

> "concept cartoon … should be in every lesson"

> "we need to plan together first" — re Priority 2 (Geography/History)

---

## Priority 2 — what needs planning

The current build system is science-only (`science_registry.py`, `build_science_lesson.py`). Priority 2 is to support Geography and History enquiries with their own component sets.

**Things to discuss/plan with Innes before building:**

1. **Component differences** — what slide types does a Geography/History lesson need vs a science lesson? E.g. do they have: knowledge organiser slides, source analysis, timeline, map work, key vocabulary, concept cartoon equivalent?
2. **Shared vs separate registries** — one `enquiry_registry.py` with subject-aware components, or separate `geography_registry.py` / `history_registry.py`?
3. **Shared infrastructure** — `lib_ooxml.py`, `build_lp.py`, and the LP label system can probably be reused as-is. Confirm.
4. **Template PPTXs** — which WFA slide layouts are used for Geo/History lessons? Same pale-blue template or different?
5. **Example lesson** — does Innes want to build a specific Geography or History enquiry as the first test case? If so, which topic/unit?

---

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `EnquiryBuilder/build_science_lesson.py` | final | On GitHub |
| `EnquiryBuilder/science_registry.py` | final | On GitHub |
| `EnquiryBuilder/lib_ooxml.py` | final | On GitHub |
| `EnquiryBuilder/build_lp.py` | final | On GitHub |
| `EnquiryBuilder/t6w7_l1.json` | broken image paths on GitHub | Push corrected version from outputs before rebuilding |
| `EnquiryBuilder/quiz_recap_template.pptx` | final | On GitHub |

---

## Open questions / blockers

- Corrected `t6w7_l1.json` not yet pushed to GitHub (image paths point to session-local `/sessions/admiring-sleepy-wozniak/images/` which won't exist in a new session — needs updating to a stable path or the images re-generated and stored in the skill folder)
- Priority 2 architecture not yet designed — must plan with Innes first

## Immediate next step

Start the planning conversation for Priority 2: ask Innes what slide components a Geography/History enquiry lesson needs, whether to use a shared or separate registry, and which specific enquiry unit to use as the first test build.
