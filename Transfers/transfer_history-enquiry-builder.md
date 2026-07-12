# Transfer: History Enquiry Lesson Builder

**Generated:** 2026-07-12
**Originating focus:** Full planning conversation for Priority 2 of the enquiry-lesson-builder — extending it from Science to History, producing one PPTX per lesson from an MTP JSON.
**Skill in use:** enquiry-lesson-builder (to be extended), enquiry-planner (to be extended)

---

## Status

Pure planning — nothing built yet. All design decisions are locked in. The immediate next step is to extend the enquiry-planner to output both a DOCX and a JSON (the MTP), then build `build_history_lesson.py` which reads the JSON and produces one PPTX per lesson. First test unit: Ancient Egypt (concept = Civilisation, ~14 lessons).

---

## Decisions locked in

- One PPTX per day/lesson (not one big weekly file)
- Every slide in a deck shares the same concept colour (bg + border), set by the enquiry-level `concept` field in the MTP
- The enquiry-planner is extended to output BOTH a human-readable DOCX (for Innes to check) and a JSON (for the lesson builder to consume); JSON is never shown to Innes
- MTP files saved to `[OneDrive root]/Term-N/TnWn/Enquiry/` — Claude always asks Innes to share the root folder (path changes year-to-year)
- Separate `history_registry.py` (not shared with geography)
- Variable number of I Do / We Do / You Do slides per lesson — set in MTP `slides` array; Claude decides during MTP generation and asks Innes if unsure
- LO wording standardised across all enquiries: "I am learning… / This is so… / I will be successful by…"
- Skill focus (`skill_focus`) per lesson determined by Claude when generating MTP; Claude asks Innes if uncertain
- KWL in lesson 1 only; Recap Quiz in all other lessons; both in the same position (slot 6)
- Vocabulary slide in every lesson: up to 5 words + child-friendly definitions, Claude selects
- Quiz: up to 5 Q+A pairs on a single slide, Q clicks in → A clicks in → Q2… Claude writes questions from previous lesson's content (big ideas, not fine detail)
- Science enquiry builder needs a vocabulary slide added — note this as a TODO after History builder is complete

---

## Colour scheme

```python
CONCEPT_COLOURS = {
    'civilisation': {'bg': 'FFF2CC', 'border': 'FFC000'},
    'invasion':     {'bg': 'FFEBEB', 'border': 'C05102'},
    'empire':       {'bg': 'EFEFFF', 'border': '7438A5'},
    'monarchy':     {'bg': 'E2F0D9', 'border': '00AE4B'},
    'revolution':   {'bg': 'DAE3F3', 'border': '4573C4'},
}
```

---

## Slide sequence — every lesson

**Fixed slides (auto-generated from MTP metadata — not in `slides` array):**

| # | Slide | Notes |
|---|-------|-------|
| 1 | Key Question | Cloud + KQ text + challenge; 4-children PNG centred; 21C-skills PNG top right; hist-icon + "Being an Historian" bottom centre; day label bottom left |
| 2 | Concepts & Skills | `hist-sub-concepts.png` (left) + `Hist-skill.png` (right); each image clicks in separately |
| 3 | Concept card | 6 PNGs stacked: `[Concept]/[prefix]-Y1.png` (bottom) → Y6 (top); each row clicks in on mouse click |
| 4 | Building Blocks | "Our Enquiry…" title; brick wall 4/3/4/3 = 14 bricks; each brick = skill colour PNG + text overlay; ALL bricks click in one at a time (including previous lessons'); concept colour BG |
| 5 | What / Why / How | 3-panel LO; enquiry question as title; "I am learning… / This is so… / I will be successful by…" |
| 6 | **L1:** KWL — **L2+:** Recap Quiz | See specs below |
| 7 | Key Vocabulary | Word clicks in → definition clicks in → word 2… up to 5 pairs |

**Variable slides** (defined per lesson in `slides` array):
- `i_do` / `we_do` / `you_do` / `you_do_trio` — any quantity, any order, Claude decides

---

## Component specs

### Key Question slide
- Background: concept colour; border rectangle same colour
- Cloud thought-bubble shape with enquiry question (underlined) + challenge text below
- `4-children-KQ-slide.png` centred mid-slide
- `21C-skills-KQ-slide.png` top right
- `hist-icon.png` + "Being an Historian" text bottom centre
- Day label (e.g. "Monday a.m.") bottom left, large bold text

### Concepts & Skills slide
- `hist-sub-concepts.png` left half; `Hist-skill.png` right half
- Click 1: concepts circle appears; Click 2: skills pie appears

### Concept card slide
- Stack 6 PNGs vertically (Y1 bottom row, Y6 top row)
- Each appears on its own mouse click (Y1 first → Y6 last)
- PNGs path: `/Users/innes/Pictures/PPTX Slide assets/Historians/[ConceptFolder]/[prefix]-Y[n].png`
- Concept folders: `Civilisation/civ-`, `Invasion/inv-`, `Empire/emp-`, `Monarchy/mon-`, `Revolution/rev-`

### Building Blocks slide
- Title: "Our Enquiry…" with "I Do" badge tag
- Layout: brick wall — Row 1 (bottom): 4 bricks; Row 2: 3 bricks; Row 3: 4 bricks; Row 4 (top): 3 bricks = 14 total
- Each brick = skill-coloured PNG with short text label overlaid
- Brick PNGs: `/Users/innes/Pictures/PPTX Slide assets/Historians/`
  - `Hist-block-yellow-questioning-and-understanding.png` → skill_focus = `questioning`
  - `Hist-block-peach-chronology.png` → skill_focus = `chronology`
  - `Hist-block-pink-sources.png` → skill_focus = `sources`
  - `Hist-block-blue-interpretations.png` → skill_focus = `interpretations`
- Text on each brick = `building_block_text` from MTP for that lesson (short phrase, e.g. "Who were the Egyptians?")
- In lesson N: bricks 1→N all animate in one at a time on mouse click

### LO (What / Why / How) slide
- Enquiry question as slide title (top, with key question icon)
- Three panels (left/centre/right), each with a child character illustration + thought bubble
- Panel text: "I am learning… [what]" / "This is so… [why]" / "I will be successful by… [success]"
- Same child character PNGs as science LO slide — confirm if separate assets needed or reuse

### KWL slide (Lesson 1 only)
- Layout: "We Do"
- Title: "What knowledge am I bringing to this enquiry? What would I like to find out?"
- 2-column table: header row = "Prior Knowledge and Skill" | "I am curious about…"; one empty body row (teacher writes on interactive board live)
- Fixed every time; only concept colour changes

### Recap Quiz slide (Lessons 2+ only)
- Layout: "You Do"
- Up to 5 Q+A pairs
- Animation: Q1 clicks in → A1 clicks in → Q2 clicks in → A2 clicks in → …
- Questions consolidate big ideas from previous lesson, not fine details
- Claude writes Q+A from previous lesson's content when generating MTP

### Key Vocabulary slide
- Layout: "We Do"
- Up to 5 words, Claude selects (highest lesson impact + broader concept relevance)
- Animation: Word 1 clicks in → Definition 1 clicks in → Word 2 → …
- Child-friendly definitions, Claude writes them

### Variable slides (I Do / We Do / You Do / You Do Trio)
- All use concept colour background + border
- Content from `slides` array in MTP

---

## MTP JSON structure

```json
{
  "subject": "history",
  "topic": "Ancient Egypt",
  "key_question": "What is the legacy of Ancient Egypt?",
  "challenge": "Our challenge is to create a museum exhibition about Ancient Egypt.",
  "concept": "civilisation",
  "total_lessons": 14,
  "writing_outcome": {
    "genre": "inform",
    "description": "A non-chronological report about Ancient Egypt"
  },
  "enquiry_outcome": "Museum exhibition display",
  "lessons": [
    {
      "lesson_number": 1,
      "day_label": "Monday a.m.",
      "phase": 1,
      "skill_focus": "questioning",
      "building_block_text": "Who were the Ancient Egyptians?",
      "what": "About the geography and society of Ancient Egypt",
      "why": "understanding where Egypt is and how it was organised helps us explore why this civilisation became so powerful",
      "success": "locating Egypt on a map and describing at least three features of Egyptian society",
      "vocabulary": [
        {"word": "Civilisation", "definition": "A large group of people who live together and share a language, laws and way of life."},
        {"word": "Pharaoh", "definition": "The ruler of Ancient Egypt, believed by Egyptians to be a god as well as a king."}
      ],
      "quiz": [],
      "slides": [
        {"type": "i_do", "title": "Where in the World is Egypt?", "content": "Egypt is in North Africa on the banks of the River Nile..."},
        {"type": "we_do", "title": "Reading a Map", "content": "Look at the map together — what do you notice about where Egypt is positioned?"},
        {"type": "you_do_trio", "title": "What Do We Already Know?", "content": "Discuss in trios: what do you already know about Ancient Egypt?"}
      ]
    }
  ]
}
```

---

## MTP DOCX format (what Innes checks)

Each lesson appears as:

```
LESSON 1 — Monday a.m. — Phase 1: Discover
Concept: Civilisation | Skill: Questioning and Understanding
Building block text: Who were the Ancient Egyptians?

I am learning: [what]
This is so: [why]
I will be successful by: [success]

VOCABULARY
1. Civilisation — A large group of people who live together...
2. Pharaoh — The ruler of Ancient Egypt...

QUIZ — No quiz (first lesson)

SLIDE PLAN
I Do: Where in the World is Egypt? — [content summary]
We Do: Reading a Map — [content summary]
You Do (Trio): What Do We Already Know? — [content summary]
```

---

## Asset paths

```
ASSETS_ROOT = '/Users/innes/Pictures/PPTX Slide assets/Historians/'

Static (every deck):
  hist-icon.png
  hist-sub-concepts.png
  Hist-skill.png
  21C-skills-KQ-slide.png
  4-children-KQ-slide.png

Concept card rows (substitute concept folder/prefix):
  Civilisation/civ-Y1.png … civ-Y6.png
  Invasion/inv-Y1.png … inv-Y6.png
  Empire/emp-Y1.png … emp-Y6.png
  Monarchy/mon-Y1.png … mon-Y6.png
  Revolution/rev-Y1.png … rev-Y6.png

Building blocks:
  Hist-block-yellow-questioning-and-understanding.png
  Hist-block-peach-chronology.png
  Hist-block-pink-sources.png
  Hist-block-blue-interpretations.png
```

---

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `/var/folders/.../skills/enquiry-planner/SKILL.md` | existing | Needs extending: add History JSON output + new per-lesson fields |
| `/var/folders/.../skills/enquiry-lesson-builder/SKILL.md` | existing (science only) | Will be extended after History builder complete |
| `EnquiryBuilder/build_science_lesson.py` | final | On GitHub — reference for build pattern |
| `EnquiryBuilder/science_registry.py` | final | On GitHub — reference for registry pattern |
| `EnquiryBuilder/lib_ooxml.py` | final | On GitHub — reuse as-is |
| `EnquiryBuilder/build_lp.py` | final | On GitHub — reuse as-is |
| `[OneDrive root]/Term-N/TnWn/Enquiry/` | target output folder | Ask Innes to share root folder at start of build |

---

## Open questions / blockers

- LO child character illustrations: confirm whether the same PNG assets used in the science LO slide apply here, or if History has separate ones (likely already in the WFA template — check before building)
- LP (Learning Paper) for History lessons: not discussed — ask Innes whether each History lesson also needs an LP, and if so whether it follows the same LP builder as science

---

## Immediate next step

1. Ask Innes to share the OneDrive root planning folder path
2. Run the enquiry-planner for Ancient Egypt (History, ~14 lessons, concept = Civilisation) — this generates the MTP DOCX + JSON
3. Present the DOCX for Innes to review and approve
4. Once approved, build Lesson 1 PPTX using `build_history_lesson.py` as a test
5. Get Innes's sign-off on L1 output, then build all remaining lessons
