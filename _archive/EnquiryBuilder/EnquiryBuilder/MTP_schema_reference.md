# MTP JSON Schema Reference
*Enquiry lesson builders — Science, History, Geography*
*Last updated: 2026-07-21*

---

## Structure overview

All three builders share the same two-level structure:

```
{
  ... enquiry-level fields ...
  "lessons": [
    {
      ... lesson-level fields ...
      "slides": [
        { "type": "...", ... slide-spec fields ... }
      ]
    }
  ]
}
```

---

## 1. Science

### Enquiry-level fields

| Field | Required | Where used |
|---|---|---|
| `key_question` | Yes | Slide 1 — Key Question title |
| `challenge` | Yes | Slide 1 — challenge text below KQ |
| `strand` | Yes | Slide 3 — discipline/strand beaker icon. Values: `"Biology"`, `"Earth and Space Science"`, `"Chemistry"`, `"Physics"` |
| `topic` | No | Output filename, display only |
| `year_group` | No | Display only (default `"Y5"`) |
| `subject` | No | Display only (default `"science"`) |
| `lessons` | Yes | Array of lesson objects |

> The `enquiry` sub-object (`enquiry.key_question`, `enquiry.challenge`) is an older alias for the flat form above — both work.

### Lesson-level fields

| Field | Required | Where used |
|---|---|---|
| `lesson_number` | Yes | Building blocks animation (determines how many atoms are lit); output filename |
| `day_label` | Yes | Filename sort prefix — `{term_week}_{seq}{Day}` e.g. `T2W3_1Tue`. Computed from Block 1 timetable input. |
| `term_week` | Yes | Week reference e.g. `T2W3`. Derived from timetable computation. |
| `building_block_text` | Yes | Slide 4 — text label on the current lesson's atom/electron |
| `what` | Yes | Slide 5 LO — WALT (I am learning to…) |
| `why` | Yes | Slide 5 LO — TIB (This is because…) |
| `success` | Yes | Slide 5 LO — ISB (I will show this by…) |
| `vocabulary` | Yes | Slide 7 — Key Vocabulary (click-reveal). Array of `{"word": "...", "definition": "..."}` |
| `quiz` | L2+ | Slide 6 — Recap Quiz (L1 gets KWL instead). Array of `{"question": "...", "answer": "..."}` |
| `quiz_title` | No | Slide 6 header (default `"Recap Quiz"`) |
| `lp` | No | Learning paper reference — display only |
| `slides` | Yes | Array of variable slide specs |

### Variable slide types

| `type` | Key fields | What it builds |
|---|---|---|
| `wedo_hook` | `title`, `bullets[]` | We Do — animated bullet list |
| `wedo_grid` | `title`, `rows[]` | We Do — grid/table layout |
| `ido_diagram` | `title`, `diagram_path`, `labels[]` | I Do — diagram with callout labels |
| `youdo_provocation` | `title`, `question`, `images[]` | You Do — provocative question + images |
| `youdo_task` | `title`, `task`, `images[]` | You Do — task instructions |
| `concept_cartoon` | `title`, `image_path`, `speech_a`, `speech_b`, `speech_c` | Cloned concept cartoon from template |
| `learning_review` | `questions[]` | Final slide — 3 reflection questions |
| `image_slide` | see §4 | Any image layout from `image_layouts.py` |

---

## 2. History

### Enquiry-level fields

| Field | Required | Where used |
|---|---|---|
| `concept` | Yes | All variable slides — concept colour scheme (bg + border). Values: `"civilisation"`, `"invasion"`, `"empire"`, `"monarchy"`, `"revolution"` |
| `topic` | No | Display only (default `"History"`) |
| `concept_cartoon_pptx` | For `concept_cartoon` slides | Path to the source PPTX containing the concept cartoon to clone |
| `lessons` | Yes | Array of lesson objects |

### Lesson-level fields

| Field | Required | Where used |
|---|---|---|
| `lesson_number` | Yes | Building blocks brick count (bricks 1–N animate in); determines KWL vs Quiz |
| `day_label` | Yes | Filename sort prefix — `{term_week}_{seq}{Day}` e.g. `T2W3_1Tue`. Computed from Block 1 timetable input. |
| `term_week` | Yes | Week reference e.g. `T2W3`. Derived from timetable computation. |
| `building_block_text` | Yes | Slide 4 — text on the current lesson's building block brick |
| `skill_focus` | Yes | Slide 4 — brick colour. Values: `"questioning"`, `"chronology"`, `"sources"`, `"interpretations"` |
| `what` | Yes | Slide 5 LO — WALT (I am learning to...) |
| `why` | Yes | Slide 5 LO — TIB (This is because...) |
| `success` | Yes | Slide 5 LO — ISB (I will show this by...) |
| `vocabulary` | Yes | Slide 7 — Key Vocabulary. Array of `{"word": "...", "definition": "..."}` |
| `quiz` | L2+ | Slide 6 — Recap Quiz. Array of `{"question": "...", "answer": "..."}` |
| `slides` | Yes | Array of variable slide specs |

### Variable slide types

| `type` | Key fields | What it builds |
|---|---|---|
| `i_do` | `title`, `content` | I Do slide — sentences animated in on click |
| `we_do` | `title`, `content` | We Do slide — same pattern |
| `you_do` | `title`, `content` | You Do (individual) slide |
| `you_do_trio` | `title`, `content` | You Do Trio slide |
| `concept_cartoon` | `title`, `speech_a`, `speech_b`, `speech_c`, `learners[]` | Cloned from `concept_cartoon_pptx` |
| `image_slide` | see §4 | Any image layout from `image_layouts.py` |

> `content` is a string. The builder splits it on sentence boundaries (`.`, `?`, `!`) and animates each sentence in on a separate click.

---

## 3. Geography

### Enquiry-level fields

| Field | Required | Where used |
|---|---|---|
| `default_substantive_concept` | Yes | Fallback concept for lessons that don't specify one. Values: `"place_space_scale"`, `"human_geography"`, `"cultural_awareness"`, `"physical_geography"`, `"environmental_impact"` |
| `key_question` | Yes | Slide 1 — key question text |
| `lessons` | Yes | Array of lesson objects |

### Lesson-level fields

| Field | Required | Where used |
|---|---|---|
| `lesson_number` | Yes | Puzzle pieces (pieces 1–N shown); determines KWL vs Quiz; output filename |
| `day_label` | Yes | Filename sort prefix — `{term_week}_{seq}{Day}` e.g. `T2W3_1Tue`. Computed from Block 1 timetable input. |
| `term_week` | Yes | Week reference e.g. `T2W3`. Derived from timetable computation. |
| `lesson_title` | No | Output filename (falls back to `puzzle_piece_text` then `building_block_text`) |
| `substantive_concept` | No | Overrides `default_substantive_concept`. Selects colour master (Yellow/Peach/Blue/Green/Purple) |
| `puzzle_piece_text` | Yes | Slide 4 — text on the current lesson's puzzle piece |
| `skill_focus` | Yes | Slide 4 — which EMF skill icon on the piece. Values: `"questioning_predicting"`, `"observing_recording"`, `"field_work"`, `"map_skills"`, `"concluding_communicating"` |
| `date` or `day` | Yes | Slide 5 LO — date line |
| `what` or `learning_label.lf` | Yes | Slide 5 LO — WALT |
| `why` or `learning_label.sc1` | Yes | Slide 5 LO — TIB |
| `success` or `learning_label.sc2` | Yes | Slide 5 LO — ISB |
| `vocabulary` | Yes | Slide 7 — Key Vocabulary. Array of `{"word": "...", "definition": "..."}` |
| `quiz` | L2+ | Slide 6 — Recap Quiz. Array of `{"question": "...", "answer": "..."}` |
| `learning_review` | For LR slides | 3 reflection question strings — used when a `learning_review` slide appears in `slides[]` |
| `images` | No | Background images for slide 1. Array of `{"use": "key_question_bg", "local_path": "/abs/path/img.jpg"}` |
| `slides` | Yes | Array of variable slide specs |

### Variable slide types

| `type` | Key fields | What it builds |
|---|---|---|
| `i_do` | `title`, `content` | I Do — fills layout PH 0 (title) + PH 1 (content) |
| `we_do` | `title`, `content` | We Do — same |
| `you_do_trio` | `title`, `content` | You Do Trio |
| `you_do` | `title`, `content` | You Do |
| `learning_review` | `questions[]` | Final slide — fills PH 10/11/12 |
| `image_slide` | see §4 | Any image layout from `image_layouts.py` |

---

## 4. `image_slide` spec (all three builders)

```json
{
  "type": "image_slide",
  "layout_key": "B1_hero_image_left",
  "title": "What did the Roman Forum look like?",
  "images": ["/abs/path/to/roman_forum.jpg"],
  "text": "The Forum was the political and commercial centre of Rome...",
  "phase": "i_do",
  "badge": "I Do"
}
```

### Fields

| Field | Required | Notes |
|---|---|---|
| `layout_key` | Yes | One of the 10 layout keys below |
| `title` | No | Slide title. For `A_full_bleed` goes in the banner; for all others goes in the top-title area |
| `images` | Depends on layout | Array of absolute file paths. Count required varies by layout (see below) |
| `text` | For split/gallery layouts | Body text in the text column or task box |
| `caption` | `C_supporting_illustration` only | Small caption below the image |
| `subtitle` | `A_full_bleed` only | Smaller line below the title in the banner |
| `speech_a` | `concept_cartoon` only | Top-left bubble text |
| `speech_b` | `concept_cartoon` only | Top-right bubble text |
| `speech_c` | `concept_cartoon` only | Bottom-centre bubble text |
| `phase` | **Science only** | Selects blank layout: `"i_do"`, `"we_do"`, `"you_do_trio"`, `"you_do"` |
| `badge` | **History** — display string | `"I Do"`, `"We Do"`, `"You Do"`, `"You Do (Trio)"` |
| `badge` | **Geography** — slug | `"i_do"`, `"we_do"`, `"you_do_trio"`, `"you_do"` |

### Layout keys and image counts

| `layout_key` | Images needed | Use when |
|---|---|---|
| `A_full_bleed` | 1 | Image IS the slide — full-bleed photo, title in bottom banner |
| `B1_hero_image_left` | 1 | One large image left; text right |
| `B2_hero_2images_left` | 2 | Two images stacked left; text right |
| `B3_hero_2images_right` | 2 | Text left; two images stacked right |
| `C_supporting_illustration` | 1 | Main text left; image right with optional caption |
| `D_diagram_focus` | 1 | Large diagram/image (~2/3 width); labels/text right column |
| `gallery_5row` | 5 | Five square images in a row below task text |
| `gallery_6x2` | 12 | Twelve images in 2 rows of 6 below task text |
| `gallery_1wide` | 1 | Single landscape image spanning full width below task text |
| `concept_cartoon` | 1 | Central image with 3 speech-bubble characters (fresh build, not cloned) |

### Choosing a layout

```
Image IS the content, no body text     → A_full_bleed  or  D_diagram_focus
Image and text have equal weight       → B1 / B2 / B3
Image supports/illustrates the text   → C_supporting_illustration
Sorting / classifying multiple images → gallery_5row / gallery_6x2 / gallery_1wide
Discussion starter                     → concept_cartoon
```

---

## 5. Fixed slide sequence (all builders)

| Slide | Science | History | Geography |
|---|---|---|---|
| 1 | Key Question | Key Question | Key Question / Our Key Question is |
| 2 | Being a Scientist | Concepts & Skills | Concepts & Skills |
| 3 | Discipline (strand) | Concept Card | Progression (year-group strips) |
| 4 | Building Blocks (atom model) | Building Blocks (brick wall) | Puzzle Pieces |
| 5 | Learning Objective | Learning Objective | Learning Objective |
| 6 | KWL (L1) / Recap Quiz (L2+) | KWL (L1) / Recap Quiz (L2+) | KWL (L1) / Recap Quiz (L2+) |
| 7 | Key Vocabulary | Key Vocabulary | Key Vocabulary |
| 8+ | `slides[]` variable slides | `slides[]` variable slides | `slides[]` variable slides |
