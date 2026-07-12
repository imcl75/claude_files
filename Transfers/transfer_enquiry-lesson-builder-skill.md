# Transfer: Enquiry lesson builder skill rewrite

**Generated:** 2026-07-12
**Originating focus:** Designing the full specification for a new History/Geography/Science enquiry lesson builder skill, following a test build of a 14-lesson Ancient Egypt unit.
**Skill in use:** skill-creator (to write the new SKILL.md)

---

## Status

The test build is complete (14 Egypt PPTXs + DOCX). That work surfaced a comprehensive set of design decisions about how the skill should work. The skill has NOT been updated yet — the entire new SKILL.md needs to be written and submitted via Settings > Capabilities.

The existing skill at `/mnt/skills/user/enquiry-lesson-builder/SKILL.md` is the **science-only** enquiry builder (PPTXs from an enquiry description). This rewrite creates a new, separate skill for History/Geography/Science that follows the full CLF-driven MTP workflow.

The new skill should be named `enquiry-lesson-builder` (replace existing) or `history-geo-science-enquiry-builder` (new). Check with Innes at start.

---

## What's been produced (test build — keep for reference, not the focus of new session)

- `outputs/egypt_mtp.json` — 14-lesson MTP for Ancient Egypt (Y5). **Content generated from training knowledge, NOT CLF KB — needs replacement with CLF-accurate version.**
- `outputs/history_registry.py` — Colour scheme and asset paths for history builder
- `outputs/build_history_lesson.py` — PPTX builder (~600 lines), works, all 14 PPTXs verified
- `outputs/generate_egypt_docx.js` — DOCX generator (Node.js, `docx` npm). Orientation bug fixed: use `size: { width: 16838, height: 11906 }` WITHOUT `orientation: PageOrientation.LANDSCAPE`.
- `outputs/Egypt_Enquiry_Plan.docx` — planning DOCX, readable, tables fit correctly
- `outputs/Egypt_Lessons/L01–L14_*.pptx` — 14 lesson PPTXs, 10 slides each, ~2.2 MB each

---

## Decisions locked in

### Year group
- **Default Y5 from now on.** Innes is moving to Y5 in September. Unless he says otherwise, assume Y5.

### CLF Curriculum Knowledge Base
- The CLF KB lives in the project knowledge at:
  - `/Users/innes/Library/Application Support/Claude/local-agent-mode-sessions/.../019ce895-.../docs/CLF Primary Curriculum Historians July 2026.md`
  - Equivalent files exist for Geographers, Scientists, etc.
- **Every MTP must be generated from the CLF KB for the relevant year group and subject.** Never use training knowledge for curriculum content.
- Y4 History: Anglo-Saxons/Vikings + Maya (concept: Invasion / Civilisation)
- Y5 History: Romans + Ancient Egypt (concept: Empire / Civilisation / Monarchy)
- Y5 Egypt covers: New Kingdom 1520–1075 BC AND Old Kingdom 2575–2150 BC

### Workflow (mandatory — no skipping steps)
1. Innes triggers the skill (e.g. "plan my history enquiry", "history enquiry for Romans")
2. Claude asks the **5 start questions** (see below) — all at once
3. Claude reads the relevant CLF KB section (identified from the key question)
4. Claude proposes: key question (if not given), enquiry outcome (if not given), model text draft
5. Innes approves before any building starts
6. Claude generates MTP JSON and DOCX
7. Innes reviews MTP DOCX
8. Claude batch-generates key images (from MTP `images` array)
9. Innes approves images
10. Claude builds all lesson PPTXs + LPs

### Start questions (ask all at once, never one at a time)
```
1. Key question — e.g. "How has Ancient Rome shaped modern life?" 
   (This tells me the topic and which CLF curriculum section to use. Year group is Y5 by default.)

2. How many weeks is the unit, how many lessons per week, and which days?
   Are any days doubled (two lessons on the same day)?

3. Writing outcome:
   a. Genre — inform, explain or persuade?
   b. Any specific text features to build in? (e.g. fronted adverbials, complex sentences, 
      relative clauses, passive voice, modal verbs)

4. Enquiry/subject outcome — what will pupils produce?
   Is it combined with the writing outcome?
   (I'll suggest if you're unsure. Common: museum exhibition, annotated timeline, 
   travel guide, fact file, science fair display.)

5. Any specific focus, person, event or angle to prioritise?
```

**Do NOT ask about year group** (Y5 default), **differentiation context** (read from project memory), or **school defaults** (all in CLAUDE.md and project knowledge).

### Lesson slide sequence
Standard: **I Do → (We Do) → You Do Trio → You Do (independent)**

- You Do Trio always precedes You Do Independent — warm-up/rehearsal in trios
- Trio task = subset of or stepping stone to the independent task; verbal or minimal writing
- If trio task would need significant resources → make the whole thing a group task instead (no separate independent)
- Number of I Do / We Do slides varies by lesson — plan lesson flow first, derive slides from it
- Some lessons may skip We Do; some may have 2× I Do

### MTP JSON structure — per lesson

```json
{
  "lesson_number": 3,
  "day": "Wednesday",
  "week": 2,
  "phase": 1,
  "skill_focus": "sources",
  "building_block_text": "What sources tell us about Egypt",
  "learning_label": {
    "lf": "I am learning to use sources as evidence.",
    "sc1": "I can identify what a source tells us.",
    "sc2": "I can explain what a source cannot tell us."
  },
  "what": "Use sources as historical evidence",
  "why": "Historians never have a complete picture — sources have limits",
  "success": "I can annotate a source and explain its limits",
  "vocabulary": [
    {"word": "source", "definition": "An object, text or image that gives us information about the past"},
    {"word": "artefact", "definition": "A human-made object from the past"},
    {"word": "primary source", "definition": "Evidence from the time being studied"},
    {"word": "reliability", "definition": "How trustworthy a source is"}
  ],
  "quiz": [
    {"question": "What is a source?", "answer": "An object, text or image that gives us information about the past"},
    {"question": "Name one type of primary source.", "answer": "Any of: artefact / photograph / letter / diary / newspaper"},
    {"question": "Why might two sources about the same event tell us different things?", "answer": "They may have been created by different people with different viewpoints or purposes"},
    {"question": "What did we use to learn about the Maya last lesson?", "answer": "The Mayan calendar / Mayan artefacts (accept any correct reference)"}
  ],
  "lesson_flow": "Teacher models analysing a Roman source (a relief carving) using the see/think/wonder framework. Class analyses a second source together. Trios sort three source cards by reliability. Pupils independently annotate one source and explain its limits.",
  "images": [
    {"use": "key_question_bg", "prompt": "Ancient Roman relief carving showing soldiers, photorealistic, warm stone tones, museum quality"},
    {"use": "i_do_1", "prompt": "Close-up of the Trajan's Column relief, Rome, showing Roman legionaries, detailed stonework, natural lighting"}
  ],
  "you_do_trio": {
    "description": "In trios, sort three source cards (relief carving, coin, written account) and agree which tells us most about Roman daily life — verbal justification, no writing needed.",
    "preparation_for": "Independent annotation task where each pupil selects one source and writes an annotation."
  },
  "independent_task": {
    "type": "lp",
    "organisation": "individual",
    "ll_needed": true,
    "ll_delivery": "embedded",
    "lp_title": "What can this source tell us?",
    "description": "Pupils select one source and write an annotation: what it tells us, what it can't tell us, and whether it is reliable.",
    "lp_shared": false,
    "supporting_resource": {
      "needed": true,
      "description": "Source card sheet — three images with brief captions",
      "ll_needed": false
    },
    "adaptation": {
      "support": "Pre-selected source with sentence stems: 'This source shows... I think this because... This source cannot tell us...'",
      "resources": "Annotation frame printed on LP, vocabulary card"
    }
  },
  "learning_review": [
    "What does this source tell us about Roman life?",
    "What can't it tell us — and why?",
    "Would you call this source reliable? Why?"
  ],
  "slides": [
    {"type": "i_do", "title": "Analysing a source", "content": "See / Think / Wonder on the Trajan's Column relief. What do we see? What does it tell us? What questions does it raise?"},
    {"type": "we_do", "title": "Analyse together", "content": "Class analyses a Roman coin together. What period? What does the image suggest about Roman values?"},
    {"type": "you_do_trio", "title": "Sort the sources", "content": "Three source cards — sort by how much they tell us about daily life. Agree as a trio, justify verbally."},
    {"type": "you_do", "title": "Annotate your source", "content": "Choose one source. Write an annotation on your LP: what it shows, what it can't tell us, whether it's reliable."}
  ]
}
```

### independent_task.type values
| Value | Meaning |
|-------|---------|
| `lp` | Pupils write on the LP; it goes in the book |
| `book` | Pupils read LP but write in books |
| `ll_only` | No LP; pupils write in books or answer slide questions. LL sticker only. |
| `group_verbal` | Group task, no written output. Teacher assesses during task + learning review. No LP, no LL. |
| `group_shared_lp` | Group task, one LP per trio (possibly photocopied per member). LL embedded. |

### LP/LL type system (mirrors maths skill Type A/B)
| Type | What exists | LL delivery |
|------|------------|-------------|
| A | LP — write on sheet | Embedded top-right on LP |
| B | LP — read, write in books | Separate sticker sheet |
| C | No LP — write in books / answer slides | Separate sticker only |
| D | Supporting resource stuck in book | Embedded top-right on resource |
| E | Group task, verbal only | None |
| F | Group task, shared LP | Embedded on LP, flagged in teacher notes |

Type D can accompany any of A–C.

### Learning label format
- **LF**: "I am learning to [verb]..."
- **SC1**: first success criterion
- **SC2**: second success criterion
(Matches maths skill format exactly — use same `injectLabel()` approach or equivalent)

### Vocab and quiz constraints
- Vocabulary: exactly 4–5 words per lesson
- Quiz: exactly 4–5 questions per lesson (reviewing PREVIOUS lesson's content, not today's)
- Lesson 1 has no quiz (KWL instead) and no recap quiz slide

### Writing outcome — model text
- Generate a year-appropriate (Y5) model text in the specified genre containing the specified text features
- This goes into the DOCX and is used as the shared-write stimulus slide in Phase 3
- Must be about the enquiry topic, appropriate length for Y5 (6–10 sentences for inform/explain)

### Images in MTP
- MTP `images` array specifies **key topic-specific images** only (ones that need to be right)
- Decorative/generic slide backdrops generated at build time by the PPTX builder
- Image prompts must be specific enough for `/image-generation` skill to produce usable results
- Images batch-generated and shown to Innes for approval before any PPTX building starts

### Adaptation
- Class differentiation context (A/Y/O/D bands, named pupils, SEND notes) lives in project memory — **read from there, never ask each session**
- Per-lesson `adaptation` block specifies scaffold for less confident learners and what extra resources are needed

### Differentiation terminology
| Band | Meaning |
|------|---------|
| A | At an Earlier Stage — 1+ year below Y5 |
| Y | Yet to be on track — securing Y4, working into Y5 |
| O | On track — within Y5 curriculum |
| D | Greater Depth — applying Y5 skills independently |

### Subject coverage
Same skill framework for History, Geography, Science. Differences:
- CLF KB file changes per subject (Historians / Geographers / Scientists)
- Phase labels differ (History: Discover/Investigate/Communicate; Geography: Locate & Observe/Compare & Analyse/Create & Present; Science: Question & Predict/Test & Observe/Conclude & Report)
- Subject skill frameworks differ
- Concept colour schemes differ (history: concept-based; science/geography: TBD)

### DOCX generation
- Node.js `docx` npm package, landscape A4
- **Bug already fixed:** `size: { width: 16838, height: 11906 }` — do NOT add `orientation: PageOrientation.LANDSCAPE` (it double-swaps, making page portrait-width)
- Content width = 15398 DXA (16838 − 2×720 margins)

---

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `/mnt/skills/user/enquiry-lesson-builder/SKILL.md` | Existing (science-only) | This is what needs replacing / a new skill created alongside it |
| `outputs/build_history_lesson.py` | Final, working | PPTX builder for history; Geography/Science need equivalent |
| `outputs/history_registry.py` | Final | Asset paths and colour scheme for history |
| `outputs/generate_egypt_docx.js` | Final (orientation bug fixed) | DOCX generator — reusable for any subject |
| `outputs/egypt_mtp.json` | Draft only — CLF content not used | Do not use as a template for content; use for structure only |
| CLF KB: `...019ce895.../docs/CLF Primary Curriculum Historians July 2026.md` | Source of truth | Must be read before any MTP generation |
| CLF KB: `...019ce895.../docs/CLF Primary Curriculum Geographers July 2026.md` | Source of truth | For geography enquiries |
| CLF KB: `...019ce895.../docs/CLF Primary Curriculum Scientists July 2026.md` | Source of truth | For science enquiries |

---

## Open questions / to confirm with Innes at session start

- Should the new skill replace `enquiry-lesson-builder` or be a new skill alongside it? (The existing one is science-only PPTXs from an enquiry description — quite different scope.)
- The `lo-slides` skill generates standalone LO slides. Should the enquiry builder call it, or generate LO slides inline?
- Learning review questions: printed on the LP, on a separate sheet, or teacher-only in the DOCX plan?
- Supporting resource (Type D): does it always get a full LL, or just a small label strip?

---

## Immediate next step

Ask Innes the open questions above (all at once), then use the `skill-creator` skill to write the full new SKILL.md for the enquiry lesson builder, incorporating every design decision in this transfer file. The SKILL.md should cover History, Geography and Science with a shared framework and subject-specific sections. Once written, Innes installs it via Settings > Capabilities.
