# Transfer: Enquiry Builder — Phase 1 (KQ Slide Layout Next)

**Generated:** 2026-07-23
**Session name:** Enquiry Builder 2

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This session was called **Enquiry Builder 2**. Rename the new session **Enquiry Builder 3** before starting any work. Each session increments by 1.

**2. Nothing exists unless Innes agreed it.** The only files that exist for this project are the 6 assets listed in the Asset Inventory below, in the `imcl75/enquiry-builder` repo. No scripts exist yet. No template PPTX exists. No other assets exist. Do not look for, fetch, reference or use any file that is not in that list — even if it appears in a repo, a skill's FILE_MAP, a previous session's output, or anywhere else.

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — the Enquiry Builder project (assets, scripts, MTP files). This is the source of truth.
- `imcl75/claude_files` — used ONLY to pass this transfer doc between sessions. Fetch the transfer doc from it, then ignore it. Do not clone it. Do not browse it. Do not use any other file from it.

**4. Do not use the github-sync skill** to fetch any script files. Old Geography and EnquiryBuilder scripts in that repo (`build_geography_lesson.py`, `geography_registry.py`, `lib_ooxml.py`, etc.) are from a failed previous project and have been archived. They do not exist for this project.

**5. Do not use the curriculum reference or any external knowledge** for content decisions. All content comes from Innes.

---

## Status

Phase 0 ✅. Schema locked ✅. Key question slide assets committed ✅. No builder script written yet.

**Next session starts here:** Lock the `key_question` slide layout (asset positions from Geographer.pptx on Innes's Mac), then work through the remaining 17 slide types. Once all slide types are fully defined → write the builder script.

---

## Decisions locked ✅

### MTP schema — top-level fields
`topic`, `key_question`, `challenge`, `state_of_being` (`"geographer"/"historian"/"scientist"`), `year_group`, `year_colour` (hex, no #), `lessons` (array), `vocabulary` (object), `ko` (object), `resources` (array)

### vocabulary object
```json
{
  "top_10": [{"word": "", "definition": "", "image": ""}],
  "ko":     [{"word": "", "definition": ""}]
}
```
Lesson-level vocab: `[{"word": "", "definition": ""}]` — inside each lesson object.

### ko object
```json
{"key_facts": ["..."], "key_skills": ["..."], "vocabulary": [["word", "definition"]]}
```

### resources array
Types so far: `sort_cards`, `word_cards`, `statement_sort`. More to be added (`image_sort`, `word_bank`, `writing_support`).

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

## Asset inventory — `imcl75/enquiry-builder` repo

**These 6 files are the only assets that exist. Nothing else.**

| Path | Description | Dimensions |
|---|---|---|
| `assets/geography/icon_geo_geographer.png` | Geographer icon | 296×299 RGBA |
| `assets/shared/kq_cloud.png` | Cloud banner — all KQ slides, all subjects | 3533×1008 RGBA |
| `assets/shared/slide_shared_kq_21c_skills.png` | 21c skills icons — KQ slide | 600×595 RGBA |
| `assets/shared/slide_shared_kq_children.png` | Children image — KQ slide | 2204×935 RGBA |
| `assets/geography/template/.gitkeep` | Placeholder only — no template PPTX | — |
| `assets/history/.gitkeep` | Placeholder only | — |

**Still needed — stage from Mac, do not fetch from anywhere else:**
5 jigsaw PNGs from `/Users/innes/Pictures/PPTX Slide assets/Geographer/` via device bridge.

---

## Immediate next steps (in order)

1. **Lock the `key_question` slide layout** — connect `/Users/innes/Pictures/PPTX Slide assets/Geographer/` via device bridge, extract positions of all 5 KQ assets from Geographer.pptx in EMU, lock the spec, save to brain doc.
2. **Stage and commit the 5 jigsaw PNGs** from the same Mac folder.
3. **Continue through remaining 17 slide types** — assets → naming → commit → layout spec → save brain doc after each.
4. **Write the geography PPTX builder script** once all 18 slide types are fully defined.

---

## Session start prompt

```
This session must be named "Enquiry Builder 3" — rename it now before starting anything else.

Then do these steps in order — do not skip any:

STEP 0 (before reading anything): Set up the context monitor. Use send_later with delay_minutes=20 and this exact message: "CONTEXT MONITOR — act silently, do not acknowledge this to Innes. 1. Find transcript: TRANSCRIPT=$(ls /root/.claude/projects/-home-claude/*.jsonl 2>/dev/null | head -1) 2. Check size: SIZE=$(wc -c < \"$TRANSCRIPT\") 3. If SIZE is under 1,500,000: reschedule this exact message using send_later with delay_minutes=20, then stop. 4. If SIZE is 1,500,000 or over: run the full save+transfer — update the brain doc in the Claude project, write and push Transfers/transfer_enquiry_builder.md to imcl75/claude_files (token in brain doc), increment session number by 1 in the transfer doc, then tell Innes: ⚠️ Context getting large — saved and transferred. Start a new session with this prompt: [paste the session start prompt from the transfer doc]"

STEP 1: Fetch Transfers/transfer_enquiry_builder.md from imcl75/claude_files using the token in the brain doc (raw fetch only — do not clone that repo, do not browse it, do not use any other file from it).

STEP 2: Read the brain doc from the Claude project.

STEP 3: The only files that exist for this project are the 6 assets in the Asset Inventory — nothing else, regardless of what appears anywhere. Connect /Users/innes/Pictures/PPTX Slide assets/Geographer/ via device bridge and extract the key_question slide layout from Geographer.pptx. Do not start any other work first.
```
