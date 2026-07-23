# Transfer: Enquiry Builder — Phase 1 (KQ Slide Layout Next)

**Generated:** 2026-07-23
**Session name:** Enquiry Builder 2  
**Originating focus:** MTP schema definition, asset intake, slide type palette. Context monitor active (auto-transfers at 1.5MB).

> **SESSION NAMING RULE — follow this before doing anything else:**  
> This session was called **Enquiry Builder 2**. The next session must be called **Enquiry Builder 3**. Each new session increments the number by 1. Name the Cowork session by clicking the session title at the top of the screen and typing the correct name *before* starting any work. If you cannot rename it, state the correct name in your first message so Innes can rename it.

---

## Status

Phase 0 complete ✅. Schema locked ✅. Asset intake for `key_question` slide complete ✅. No builder script written yet.

**Next session starts here:** Lock the `key_question` slide layout (asset positions in EMU/cm from the Geographer.pptx), then continue through remaining 17 slide types. Once all defined → write builder script.

---

## Decisions locked ✅

### MTP schema top-level fields
`topic`, `key_question`, `challenge`, `state_of_being` (`"geographer"/"historian"/"scientist"`), `year_group`, `year_colour` (hex, no #), `lessons` (array), `vocabulary` (object), `ko` (object), `resources` (array)

### vocabulary object
```json
{
  "top_10": [{"word": "", "definition": "", "image": ""}],
  "ko":     [{"word": "", "definition": ""}]
}
```
Lesson-level vocab lives inside each lesson object: `[{"word": "", "definition": ""}]`

### ko object
```json
{"key_facts": ["..."], "key_skills": ["..."], "vocabulary": [["word", "definition"]]}
```

### resources array
Types: `sort_cards`, `word_cards`, `statement_sort`. More to be added (`image_sort`, `word_bank`, `writing_support`).

### Lesson object fields (all locked)
`lesson_number`, `building_block_text`, `day_label`, `concept`, `skill`, `what`, `why`, `success`, `vocabulary`, `quiz`, `slides`

- `quiz`: `[]` for lesson 1; `[{question, answer}]` from lesson 2 onwards
- `concept` and `skill` both at lesson level — can vary lesson by lesson

### Slide type palette (18 types, locked)
`key_question`, `subject_concepts_skills`, `subject_progression`, `enquiry_lesson_progression`, `we_are_learning`, `kwl`, `lesson_quiz`, `vocabulary`, `i_do`, `i_do_image`, `we_do`, `we_do_image`, `you_do_trio`, `you_do_trio_image`, `you_do_independent`, `you_do_independent_image`, `concept_cartoon`, `learning_review`

- `kwl` — lesson 1 only
- `lesson_quiz` — lesson 2 onwards  
- Image variants — Claude decides which to use based on lesson content
- Design rules (colours, jigsaw, progression images) operate at **lesson level**, not per-slide

### Canonical concept values
**Geographer:** `place_space_scale`, `physical_geography`, `environmental_impact_and_sustainability`, `human_geography`, `cultural_awareness_and_diversity`  
**Historian:** `civilisation`, `monarchy`, `empire`, `invasion`, `revolution`  
**Scientist:** `chemistry`, `earth_and_space`, `biology`, `physics`

### Canonical skill values
**Geographer:** `map_skills`, `field_work`, `observing`, `questioning`, `concluding`  
**Historian:** `chronology`, `using_sources`, `questioning_and_understanding`, `interpretations`  
**Scientist:** `plan_and_question`, `test`, `observe_and_measure`, `record_and_present`, `conclude`

### Geography colour maps

**Concept → light / dark:**
| Concept | Light | Dark |
|---|---|---|
| `place_space_scale` | `#FFF2CC` | `#FFC000` |
| `human_geography` | `#FFCCCC` | `#C3580C` |
| `cultural_awareness_and_diversity` | `#DDEAF8` | `#4574C4` |
| `physical_geography` | `#B3E5A1` | `#4EA72E` |
| `environmental_impact_and_sustainability` | `#CCCCFF` | `#7030A0` |

**Skill → jigsaw PNG + fill colour:**
| Skill | PNG | Colour |
|---|---|---|
| `map_skills` | `jigsaw_geo_map_skills.png` | `#CBFFA9` |
| `field_work` | `jigsaw_geo_field_work.png` | `#FFAAFF` |
| `observing` | `jigsaw_geo_observing.png` | `#FFFFAD` |
| `questioning` | `jigsaw_geo_questioning.png` | `#FFCEA5` |
| `concluding` | `jigsaw_geo_concluding.png` | `#97F4FF` |

Jigsaw pieces are geography-specific. Historian/scientist use a different (TBD) concept-driven device.

---

## Asset inventory (git repo `imcl75/enquiry-builder` — only these 6 files exist)

| Path | Description | Size |
|---|---|---|
| `assets/geography/icon_geo_geographer.png` | Geographer icon | 296×299 RGBA |
| `assets/shared/kq_cloud.png` | Cloud banner — all KQ slides, all subjects | 3533×1008 RGBA |
| `assets/shared/slide_shared_kq_21c_skills.png` | 21c skills icons — KQ slide | 600×595 RGBA |
| `assets/shared/slide_shared_kq_children.png` | Children image — KQ slide | 2204×935 RGBA |
| `assets/geography/template/.gitkeep` | Placeholder — no template PPTX | — |
| `assets/history/.gitkeep` | Placeholder | — |

**Still needed:** 5 jigsaw PNGs — stage from `/Users/innes/Pictures/PPTX Slide assets/Geographer/` via device bridge.

---

## Immediate next steps (in order)

1. **Extract KQ slide layout from Geographer.pptx** — connect Innes's Mac folder, open the PPTX, measure positions of all 5 KQ assets in EMU. Lock the spec.
2. **Stage and commit the 5 jigsaw PNGs** from Mac folder.
3. **Continue through remaining 17 slide types** — assets → naming → commit → layout spec → save brain doc after each.
4. **Write the geography PPTX builder script** once all slide types are defined.

---

## Session start prompt

```
This session must be named "Enquiry Builder 3" — rename it now before starting anything else. Then: read `Transfers/transfer_enquiry_builder.md` from GitHub repo `imcl75/claude_files` (use the github-sync skill to fetch it), then follow the session start protocol in the brain doc. We are defining slide layouts before writing any builder script. First task: extract the key_question slide layout from Geographer.pptx on my Mac (connect /Users/innes/Pictures/PPTX Slide assets/Geographer/ via device bridge) and lock the asset positions. Then continue through remaining slide types. Do not ask for confirmation before starting.
```
