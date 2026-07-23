# Enquiry Builder — Universal Skill

One skill covering History, Geography and Science enquiry units for Y5
at Wallscourt Farm Academy. Most of the workflow, schema and rules are shared
across subjects. Read the shared sections first, then the subject-specific
section for any overrides.

---

## Quick start — beginning of any enquiry session

1. Read `claude/enquiry-builder-pipeline-status.md` for current status
2. Run the subject restore step (see subject section below)
3. Confirm MTP JSON exists and is complete — generate if not
4. Build lesson PPTXs → LP → send to Innes
5. Sync to GitHub via github-sync skill

---

## Repo

```
imcl75/claude_files
├── History/
│   ├── build_history_lesson.py       ← History builder (solid, programmatic)
│   ├── history_registry.py           ← concept colours, asset paths, layout names
│   ├── restore_history_assets.py     ← run before every History session
│   └── mtp_roman_civilisation_final.json
├── Geography/
│   ├── build_geography_lesson.py
│   └── geography_registry.py         ← auto-downloads assets
├── EnquiryBuilder/
│   ├── build_science_lesson.py       ← unified builder, all science lesson types
│   ├── build_lp.py                   ← LP builder, all subjects
│   ├── build_resources.py            ← sort cards, word cards, statement sort, writing toolkit
│   ├── lib_ooxml.py                  ← OOXML engine (Science, History and shared)
│   ├── science_registry.py           ← layout names, colours, anchor IDs
│   ├── class_lp_groups.json          ← Y5 LP group assignments (do NOT ask Innes)
│   ├── build_ko_pdf.py               ← KO PDF builder
│   └── templates/
│       └── history-example.pptx      ← base PPTX for History builder
└── Shared/
    └── fix_pptx_ooxml.py             ← post-processor, run on every output
```

---

## Shared workflow

The ten stages below apply to all subjects. Subject-specific rules are noted
in each stage; see the subject sections for full detail.

### Stage 1 — Gather MTP inputs

Ask for:
- Subject (History / Geography / Science)
- Topic / key question
- Number of lessons (typically 14 — confirm with Innes)
- Year group (Y5 for all subjects)
- Concept (drives colour scheme for History; master choice for Geography;
  strand for Science)

Do NOT ask what slides to include — derive from the MTP.

### Stage 2 — Generate MTP JSON

Generate the full MTP as JSON (schema below). Present as a lesson-by-lesson
readable summary before proceeding. Check the CLF Curriculum Progression
document for prior learning and cross-curricular links. All curriculum
content must come from the CLF knowledge base, not training knowledge.

Include a `knowledge_organiser` block and a `supporting_resources` block
at enquiry level (see schemas below).

### Stage 3 — Generate planning DOCX

Generate using Node.js `docx` package. Include per lesson:
- LO / TIB / ISB (with correct grammar — see LO grammar rules)
- Teaching sequence table (Phase | Title | Detail) for each slide
- Lesson vocabulary (3–5 words)
- Recall quiz (4–5 questions reviewing the previous lesson; L1 uses KWL opener)
- Images to generate (slide location, tool, full prompt)

Include at document level:
- Unit overview table (all lessons)
- Top 10 key vocabulary
- Full image generation requirements table

Innes reviews the DOCX before image generation begins.

**Orientation rule:** `size: { width: 16838, height: 11906 }` — do NOT add
`orientation: PageOrientation.LANDSCAPE` — it double-swaps to portrait.

### Stage 4 — Generate images

Generate all images in the MTP `images` array, plus the two KO images:
- `knowledge_organiser.strip_image` — 1792×1024 panorama (DALL-E)
- `knowledge_organiser.notes_image` — 1024×1024 detail (DALL-E)

Generate DALL-E images in pairs (not threes — parallel requests time out).
Use `quality: 'fast'` for DALL-E icon/diagram generation.

**Photos, scenes, real-world objects** → Higgsfield (`nano_banana_pro`,
1:1 for grid items, 16:9 for full-slide). Download CDN URLs immediately
via `job_display` — they do not persist between sessions.

**Diagrams, labelled illustrations** → DALL-E (`fast` quality).

Every deliverable must have real images before delivery. No placeholder.

Show KO images to Innes for approval before proceeding.

### Stage 5 — Build Knowledge Organiser PDF

```bash
python3 EnquiryBuilder/build_ko_pdf.py ko_config.json
```

Write config from `knowledge_organiser` block. Script auto-composites the
subject icon and crops images to the correct display ratio.

Output: `KO_{YG}_{Subject}_{topic}.pdf`

This is a Lesson 1 resource — goes into children's books at the start of
the unit.

### Stage 6 — Build supporting resources

```bash
python3 EnquiryBuilder/build_resources.py resources_config.json
```

Write config from `supporting_resources` block.

**L1 resources** — sort cards, word cards, statement sort — build after
KO PDF. Include in L1 pack.

**Writing toolkit** — build at the start of the writing phase. Sections are
driven entirely by `enquiry.writing_features` — do NOT hardcode grammar
feature names.

Year group colour in page header only. Section headers use
`TOOLKIT_SECTION_COLOURS` — never WFA year colours.

Outputs:
- `SortCards_{YG}_{Subject}_{topic}.pdf`
- `WordCards_{YG}_{Subject}_{topic}.pdf`
- `StatementSort_{YG}_{Subject}_{topic}.pdf`
- `WritingToolkit_{YG}_{Subject}_{topic}.pdf`

### Stage 7 — Build vocab poster

A3 landscape HTML. Header = year group colour. 5×2 grid of vocabulary cards
(word / image / definition). Generate images in pairs (DALL-E `fast`).

### Stage 8 — Build lesson PPTXs

Run the subject builder (see subject sections). Produce one PPTX per lesson.
Validate via LibreOffice → PyMuPDF. Check every slide.

Run `fix_pptx_ooxml.py` on every output before delivery, all subjects.

### Stage 9 — Build Learning Papers (LPs)

```bash
python3 EnquiryBuilder/build_lp.py mtp.json --lesson N \
  --subject [historian|geographer|scientist]
```

Three levels per lesson: `standard` / `adapted` / `further_adapted`.
Cohort assignments in `EnquiryBuilder/class_lp_groups.json` — load this at
the start of every session. Do NOT ask Innes for LP assignments.

Build LP BEFORE the teaching PPTX when LP preview injection is needed.

### Stage 10 — Deliver

Zip: PPTXs + LP PPTXs + DOCX + vocab poster HTML + KO PDF + supporting
resource PDFs. Label L1 resources clearly. Label writing toolkit with the
first writing lesson number. Confirm file count before presenting.

---

## Shared MTP JSON schema

These fields appear in every enquiry MTP regardless of subject.

```json
{
  "subject": "History",
  "topic": "The Roman Empire",
  "key_question": "How did the Roman Empire change the world?",
  "challenge": "Design a Roman information trail through the school...",
  "concept": "empire",
  "total_lessons": 14,
  "writing_outcome": "A persuasive speech as a Roman senator",
  "enquiry_outcome": "An information trail about the impact of the Roman Empire",

  "phases": {
    "1": { "name": "Discover",     "lessons": [1,2,3,4,5] },
    "2": { "name": "Investigate",  "lessons": [6,7,8,9,10] },
    "3": { "name": "Communicate",  "lessons": [11,12,13,14] }
  },

  "knowledge_organiser": {
    "key_facts": ["...", "..."],
    "key_skills": ["...", "..."],
    "vocabulary": [["word", "definition"], ["word", "definition"]],
    "strip_image": { "prompt": "...", "filename": "ko_strip.png" },
    "notes_image": { "prompt": "...", "filename": "ko_notes.png" }
  },

  "supporting_resources": {
    "l1_resources": {
      "sort_cards": { "title": "...", "items": [{"text": "..."}] },
      "word_cards":  { "title": "...", "note": "from vocabulary at build time" },
      "statement_sort": { "title": "...", "statements": [{"text": "..."}] }
    },
    "writing_toolkit": {
      "title": "...", "subtitle": "...",
      "note": "rows generated from enquiry.writing_features — do NOT hardcode"
    }
  },

  "lessons": [
    {
      "lesson_number": 1,
      "day_label": "Monday",
      "phase": 1,
      "skill_focus": "questioning",
      "building_block_text": "Who were the Ancient Egyptians?",
      "what": "About the geography and society of Ancient Egypt",
      "why": "Knowing where Egypt is helps us ask better questions",
      "success": "Locate Egypt on a map and name three features of Egyptian society",
      "vocabulary": [
        { "word": "Empire", "definition": "A group of countries ruled by one powerful leader." }
      ],
      "quiz": [
        { "question": "...", "answer": "..." }
      ],
      "slides": [
        { "type": "i_do",        "title": "...", "content": "..." },
        { "type": "we_do",       "title": "...", "content": "..." },
        { "type": "you_do_trio", "title": "...", "content": "..." }
      ]
    }
  ]
}
```

**Valid slide types (all subjects):** `i_do`, `we_do`, `you_do`, `you_do_trio`,
`concept_cartoon`

---

## Shared LO grammar rules

| Field | Format | Example |
|-------|--------|---------|
| LO | Infinitive verb phrase — no "to" prefix | `compare and group materials by their properties` |
| TIB | "I understand/know that…" | `I understand that empire means rule by force over many peoples` |
| ISB | Progressive "-ing" phrase | `analysing sources and explaining what they tell us about Roman life` |

Never pass a leading "to" to the LO field. Never pass "I can" to ISB — the
builder prepends labels automatically.

---

## SUBJECT: History

### Restore step
```bash
python3 restore_history_assets.py
```
Fetches all 39 PNGs into `/home/claude/assets/`. Run before every session.

### How it works

**Programmatic approach** — same architecture as Geography and Science.
`build_history_lesson.py` calls `fresh(work, 'Blank')` for each slide,
adds shapes programmatically, and routes variable slides through
`VARIABLE_DISPATCH`. No string replacement, no clone-of-master approach.

Base PPTX: `EnquiryBuilder/templates/history-example.pptx` — provides the
named slide layouts only. All slide content is built from scratch.

### Concept colours

| Concept | Border hex | Light BG hex |
|---------|-----------|--------------|
| civilisation | `FFC000` | `FFF3CC` |
| empire | `7438A5` | `EFEFFF` |
| invasion | `C05102` | `FFEBEB` |
| monarchy | `00AE4B` | `E2F0D9` |
| revolution | `4573C4` | `DAE3F3` |

Applied via `_apply_concept_bg(sp, bg_hex, border_hex)` — inserts a filled
background rectangle and a coloured border rectangle into each slide's spTree.

### Per-slide-type badge colours

| Slide type | Badge fill | Badge text |
|-----------|-----------|-----------|
| `i_do` | `1F3864` (navy) | `FFFFFF` |
| `we_do` | `1A5C2A` (forest green) | `FFFFFF` |
| `you_do` | `7D2200` (dark red) | `FFFFFF` |
| `you_do_trio` | `4B0082` (purple) | `FFFFFF` |

### Slide sequence

Slides 1–7 are fixed. Slides 8 onwards are driven entirely by the lesson's
`slides[]` array — a lesson can have any number of any type in any order.

| Position | Slide |
|----------|-------|
| 1 | Key Question — cloud callout, KQ text, 4-children image, day label |
| 2 | Concepts & Skills — concept card images + skills PNG |
| 3 | Concept Card — concept name, Y1–Y6 progression images |
| 4 | Building Blocks — coloured brick PNGs up to lesson N, with text |
| 5 | LO — What / Why / How (success criteria) |
| 6 | KWL (L1 only) or Recap Quiz (L2+) |
| 7 | Key Vocabulary — animated: word → definition → next word |
| 8+ | Variable — one slide per entry in `slides[]`, in order |

Include `learning_review` as the last entry in `slides[]` when needed.

**Valid slide types in `slides[]`:**
`i_do`, `we_do`, `you_do`, `you_do_trio`, `concept_cartoon`,
`image_slide`, `learning_review`

### Building blocks

14 coloured brick PNGs, one per lesson, keyed by `skill_focus`:

| `skill_focus` | PNG colour |
|--------------|-----------|
| `questioning` | yellow |
| `chronology` | peach |
| `sources` | pink |
| `interpretations` | blue |

Slide 4 renders only the first N bricks (where N = current lesson number).
Each brick displays the `building_block_text` from its lesson's MTP entry.

### Running the builder

```bash
python3 History/build_history_lesson.py mtp.json \
  --base-pptx EnquiryBuilder/templates/history-example.pptx \
  --lesson N \
  --out-pptx L{N}.pptx

# Or build all lessons:
python3 History/build_history_lesson.py mtp.json \
  --base-pptx EnquiryBuilder/templates/history-example.pptx \
  --out-dir ./lessons/
```

Then run fix_pptx_ooxml on every output:
```bash
python3 Shared/fix_pptx_ooxml.py L{N}.pptx
```

### Status (2026-07-22)

All slide types confirmed working. Roman Civilisation 14-lesson unit built
clean 2026-07-21 (~8.9 MB per PPTX, zero errors). Concept cartoon routes via
`_concept_cartoon_router` → `build_image_slide`. Learning review handler added
2026-07-21.

---

## SUBJECT: Geography

### Restore step

No separate restore script. `geography_registry.py` auto-downloads assets
from the repo when missing. Check `ASSET_REGISTRY.md` for details.

### How it works

Clone-and-populate using `lib_ooxml.py` (Geography has its **own** copy —
not shared with EnquiryBuilder). `fresh_geo(work, layout_name, master_idx)`
creates slides. The correct `master_idx` is set from `substantive_concept`.

Builder: `Geography/build_geography_lesson.py`

### Masters — one per concept

| Concept | Master index | Colour |
|---------|-------------|--------|
| place_space_scale | 0 | Yellow |
| human_geography | 1 | Peach |
| cultural_awareness | 2 | Blue |
| physical_geography | 3 | Green |
| environmental_impact | 4 | Purple |

Masters 3 and 4 add a `1_` prefix to the four teaching layout names
(I Do, We Do, You Do Trio, You Do).

### Slide sequence

| # | Slide | Layout name |
|---|-------|------------|
| 1 | Key Question | `Our Key Question is` |
| 2 | Concepts & Skills | No editable content — layout provides everything |
| 3 | Progression | `Revisit` — year-group strip images, animated bottom-to-top |
| 4 | Puzzle Pieces | Cloned from layout; jigsaw positions are LOCKED |
| 5 | LO (What, Why, How) | `KS2 What, Why, How` (M0/1) or `What, Why, How` (M2–4) |
| 6 | KWL (L1) or Recap Quiz (L2+) | |
| 7 | Key Vocabulary | `We Do` layout |
| 8+ | Variable slides | From MTP `slides[]` array |

### Puzzle piece positions — DO NOT CHANGE

Nine jigsaw piece positions are fixed by pixel coordinates confirmed from
`geo_L1_v6IM.pptx` (2026-07-21). Full coordinate table is in
`claude/visual-spec-geography.md`. Text colour is BLACK throughout. Do not
attempt to move or rescale puzzle pieces — any change breaks the layout.

### OOXML rules (hard — never deviate)

- No `grpId` attribute on any `<p:cTn>` — causes Mac crash
- No `<p:bldLst>` in Geography animation
- `<a:picLocks/>` bare — no attributes
- Animation: `presetClass="entr"`, `nodeType="clickEffect"`

### Running the builder

```bash
python3 Geography/build_geography_lesson.py mtp.json \
  --base-pptx Geographer.pptx \
  --lesson N \
  --out-pptx L{N}.pptx
```

### Geography-specific MTP additions

```json
{
  "substantive_concept": "place_space_scale",
  "disciplinary_concept": "change",
  "geography_skills": ["map reading", "fieldwork", "data analysis"]
}
```

---

## SUBJECT: Science

### Restore step

No template PPTX — Science is fully programmatic. Assets (icons, fonts) live
in the repo. Run the standard fetch from `restore_history_assets.py` for
shared assets, then check science-specific assets per `ASSET_REGISTRY.md`.

### How it works

All slides generated from scratch using `lib_ooxml.py` functions:
`fresh`, `xr`, `xw`, `save`, `clone`. The only clone is the Recap Quiz slide.

Builder: `EnquiryBuilder/build_science_lesson.py` — unified builder, all
lesson types in a single MTP JSON run.

**Always run `fix_pptx_ooxml.py` on every output before delivery, all subjects.**
Fix #6 strips SharePoint metadata from `_rels/.rels` and
`ppt/_rels/presentation.xml.rels`.

```bash
python3 Shared/fix_pptx_ooxml.py output.pptx
```

### Lesson types and slides generated

| `lesson.type` | Slides |
|--------------|--------|
| `science_l1` | Cover → Being a Scientist → Discipline → Atom model → LO → content slides → Concept cartoon → Learning review |
| `science_content` | Cover → LO → Quiz → content slides → Learning review |
| `writing_grammar` | Cover → LO → Quiz → I Do (grammar model) → We Do → You Do → Learning review |
| `writing_plan` | Cover → LO → Quiz → planning frame → We Do → You Do → Learning review |
| `writing_draft` | Cover → LO → Quiz → model text → You Do → Learning review |
| `writing_edit` | Cover → LO → Quiz → editing checklist → peer/self edit → Learning review |
| `writing_share` | Cover → LO → Quiz → sharing protocol → reflection → Learning review |

### Atom model (L1 only, slide 4)

Fully hardcoded constants in `build_science_lesson.py`:
- 14 electron positions, ring positions, nucleus, labels
- Orange overlay animation: hidden orange electron (ID=1000) + label
  (ID=1001) revealed by one click
- `delay="indefinite"`, `nodeType="clickEffect"` for first shape,
  `nodeType="withEffect"` for second

Current lesson names on electrons:
The Universe, Our Solar System, Sizes and Distances, Day/Night and the
Seasons, The Moon, Planet Conditions, Relative Clauses, Parenthesis,
Planning, Writing 1, Writing 2, Writing 3, Editing, Sharing.

### Animation rules (Science)

- Clean `<p:seq>` only — no hide-at-start `<p:par>` blocks
- Root node: `<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">`
- No `grpId` attribute on any `<p:cTn>`

### Concept cartoon (Science)

Always specific to the enquiry science content. Three learner views:
- Learner A — common misconception
- Learner B — partially correct
- Learner C — scientifically accurate

Central image: Higgsfield photorealistic stimulus.
Teacher note: names which learner is correct and names the misconception
explicitly so the teacher knows what to address.

### Science LO grammar rules

| Field | TextBox ID | Format |
|-------|-----------|--------|
| LO | 38 | Infinitive, no "to" prefix — label builder prepends "LF: To" |
| TIB | 39 | "I understand that…" or "I know that…" |
| ISB | 40 | "-ing" phrase — label builder prepends "I can" |

### Science-specific MTP additions

```json
{
  "enquiry": {
    "science_strand": "Earth and Space Science",
    "year_group": "Y5",
    "writing_genre": "information text",
    "writing_features": ["relative clauses", "parenthesis", "technical vocabulary"]
  }
}
```

Science lesson schema additions:
```json
{
  "number": 1,
  "type": "science_l1",
  "term_week": "T1W1",
  "lo": "understand how the universe began and the scale of space",
  "tib": "I know that Earth is a tiny part of an enormous universe...",
  "isb": "describing the Big Bang theory and placing our solar system...",
  "concept_cartoon": {
    "title": "Why do we have seasons?",
    "learners": [
      {"name": "Learner A", "statement": "common misconception"},
      {"name": "Learner B", "statement": "partially correct"},
      {"name": "Learner C", "statement": "scientifically accurate"}
    ],
    "teacher_note": "Learner C is correct. Address Learner A explicitly.",
    "image_prompt": "Earth orbiting the Sun with 23.5 degree axis tilt visible, photorealistic"
  },
  "opening": "KWL grid — give out Knowledge Organiser",
  "images": [
    {
      "slide": "content_1",
      "tool": "higgsfield",
      "prompt": "...",
      "ratio": "16:9",
      "filename": "L1_content1.png"
    }
  ]
}
```

### Running the builder

```bash
python3 EnquiryBuilder/build_science_lesson.py mtp.json \
  --lesson N \
  --out L{N}.pptx
```

---

## Shared: image generation rules

- **Photos, scenes, people, real objects** → Higgsfield `nano_banana_pro`
  (1:1 for grids, 16:9 for full slides). Download CDN URLs immediately via
  `job_display` — they do not persist between sessions.
- **Diagrams, labelled illustrations** → DALL-E `fast` quality; run at most
  2 in parallel to avoid timeout.
- **Background removal** when placing images on coloured slide backgrounds —
  use `rembg` or Higgsfield background removal.
- Every deliverable needs real images before delivery. No exceptions.

---

## Shared: pipeline status

After every build session, update `claude/enquiry-builder-pipeline-status.md`
with what was built, what was delivered and what remains outstanding.

---

## Outstanding issues (all subjects, as of 2026-07-22)

| # | Subject | Issue | Severity |
|---|---------|-------|----------|
| 1 | All | KO builder icon path hardcoded to Mac — fails in cloud | Medium |
| 2 | All | KO builder bare `main()` call — wrap in `if __name__ == '__main__'` | Low |
| 3 | History/Geo | LP not yet auto-wired into build loop — manual call per lesson | Low |
| 4 | Science | Y5 Astronomy L2–L14 not yet built | Low |
| 5 | All | LL sticker sheet generator not built | Low |
