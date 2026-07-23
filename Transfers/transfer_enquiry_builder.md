# Transfer: Enquiry Builder — Session 3 → 4

**Generated:** 2026-07-23
**Session name:** Enquiry Builder 3

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This session was called **Enquiry Builder 3**. Rename the new session **Enquiry Builder 4** before starting any work. Each session increments by 1.

**2. Nothing exists unless Innes agreed it.** The only files that exist for this project are the 6 assets listed in the Asset Inventory below, in the `imcl75/enquiry-builder` repo. No scripts exist yet. No template PPTX exists. Do not look for, fetch, reference or use any file that is not in that list — even if it appears in a repo, a skill's FILE_MAP, a previous session's output, or anywhere else.

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — the Enquiry Builder project (assets, scripts, MTP files). This is the source of truth.
- `imcl75/claude_files` — used ONLY to pass this transfer doc between sessions. Fetch the transfer doc from it, then ignore it. Do not clone it. Do not browse it. Do not use any other file from it.

**4. Do not use the github-sync skill** to fetch any script files. Old Geography and EnquiryBuilder scripts in that repo are from a failed previous project and have been archived. They do not exist for this project.

**5. Do not use the curriculum reference or any external knowledge** for content decisions. All content comes from Innes.

---

## Status

Phase 0 ✅. Schema locked ✅. key_question slide ✅ FULLY LOCKED. SCS assets committed ✅ (slide_geo_scs_concepts.png, slide_geo_scs_skills.png). SCS slide layout extracted from Geographer.pptx — PPTX sent to Innes for sign-off, awaiting confirmation.

**No builder script written yet.**

---

## Decisions locked ✅

### Colour rule — applies to EVERY slide
Every slide carries the lesson colour:
- **Slide background fill** = concept **light** colour
- **Frame border** = concept **dark** colour (prstGeom prst="frame", adj1=1241, full slide 0,0,12192000,6858000)

### Frame border shape
```xml
<p:sp>
  <p:nvSpPr><p:cNvPr id="100" name="Frame"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm>
    <a:prstGeom prst="frame"><a:avLst><a:gd name="adj1" fmla="val 1241"/></a:avLst></a:prstGeom>
    <a:solidFill><a:srgbClr val="CONCEPT_DARK_HEX"/></a:solidFill>
    <a:ln><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
</p:sp>
```

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
Types so far: `sort_cards`, `word_cards`, `statement_sort`. More to be added.

### Lesson object fields (all locked)
`lesson_number`, `building_block_text`, `day_label`, `concept`, `skill`, `what`, `why`, `success`, `vocabulary`, `quiz`, `slides`

- `quiz`: `[]` for lesson 1; `[{question, answer}]` from lesson 2 onwards
- `concept` and `skill` both at lesson level — can vary lesson by lesson

### Slide type palette (18 types, locked)
`key_question`, `subject_concepts_skills`, `subject_progression`, `enquiry_lesson_progression`, `we_are_learning`, `kwl`, `lesson_quiz`, `vocabulary`, `i_do`, `i_do_image`, `we_do`, `we_do_image`, `you_do_trio`, `you_do_trio_image`, `you_do_independent`, `you_do_independent_image`, `concept_cartoon`, `learning_review`

- `kwl` — lesson 1 only
- `lesson_quiz` — lesson 2 onwards
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

---

## Slide layout specs

### key_question ✅ FULLY LOCKED

Background: concept light. Frame: concept dark (see frame XML above).

Images:
| Asset | left | top | width | height |
|---|---|---|---|---|
| `kq_cloud.png` | 186617 | 237978 | 9882800 | 2763090 |
| `slide_shared_kq_children.png` | 3048000 | 2693156 | 6096000 | 2590800 |
| `slide_shared_kq_21c_skills.png` | 10357333 | 154065 | 1648051 | 1648051 |
| `icon_geo_geographer.png` | 5634014 | 4876831 | 1223996 | 1223996 |

Text boxes:
| Content | left | top | width | height | Font | pt | Align | Colour | Wrap |
|---|---|---|---|---|---|---|---|---|---|
| KQ text | 2122582 | 676750 | 7021417 | 954107 | Twinkl Cursive Looped | 28 | left | #000000 | square |
| Challenge text | 2487641 | 1726730 | 5638566 | 707886 | Twinkl Cursive Looped | 20 | left | #000000 | square |
| "Being a Geographer" | 4365817 | 6100827 | 3760390 | 461665 | Twinkl Cursive Looped | 24 | centre | #000000 | none |
| "21st Century Learning Skills" | 10344525 | 1771029 | 1686365 | 242374 | Twinkl Cursive Looped | 9.75 | centre | #000000 | none |

### subject_concepts_skills 🔄 PENDING INNES SIGN-OFF

Layout extracted from Geographer.pptx Layout 1. PPTX sent to Innes — awaiting confirmation.

Background: concept light. Frame: concept dark (see frame XML above).

Images:
| Asset | left | top | width | height |
|---|---|---|---|---|
| `icon_geo_geographer.png` | 139278 | 114801 | 752475 | 752475 |
| `slide_geo_scs_concepts.png` | 337910 | 1027775 | 5580141 | 5377327 |
| `slide_geo_scs_skills.png` | 6268746 | 713681 | 5566957 | 5691421 |

Text boxes:
| Content | left | top | width | height | Font | pt | Align | Colour | Wrap |
|---|---|---|---|---|---|---|---|---|---|
| "Being a Geographer" | 833846 | 115467 | 7218007 | 707886 | Twinkl Cursive Looped | 40 | left | concept dark | square |

---

## Asset inventory — `imcl75/enquiry-builder` repo

**These 6 files are the only assets that exist. Nothing else.**

| Path | Description | Dimensions |
|---|---|---|
| `assets/geography/icon_geo_geographer.png` | Geographer icon | 296×299 |
| `assets/shared/kq_cloud.png` | Cloud banner — all KQ slides, all subjects | 3533×1008 |
| `assets/shared/slide_shared_kq_21c_skills.png` | 21c skills icons — KQ slide | 600×595 |
| `assets/shared/slide_shared_kq_children.png` | Children image — KQ slide | 2204×935 |
| `assets/geography/slide_geo_scs_concepts.png` | Concepts wheel — SCS slide | (check repo) |
| `assets/geography/slide_geo_scs_skills.png` | Skills wheel — SCS slide | (check repo) |

**Still needed:** 5 jigsaw PNGs from Mac — stage via device bridge when working on progression slides.

---

## Immediate next steps (in order)

1. **Get Innes sign-off on SCS slide** — if he hasn't confirmed yet, check and ask. Once confirmed, mark as ✅ in brain doc.
2. **Continue through remaining 16 slide types** — one at a time. After each: extract layout from Geographer.pptx (or ask Innes for assets/positions), build PPTX with all slides so far, send, wait for sign-off.
3. **Write the geography PPTX builder script** once all 18 slide types are fully defined.

---

## Session start prompt

```
This session must be named "Enquiry Builder 4" — rename it now before starting anything else.

STEP 0 (before reading anything): Set up the context monitor using send_later, delay_minutes=20, with this exact message: "CONTEXT MONITOR — act silently, do not acknowledge this to Innes. 1. TRANSCRIPT=$(ls /root/.claude/projects/-home-claude/*.jsonl 2>/dev/null | head -1) 2. SIZE=$(wc -c < \"$TRANSCRIPT\") 3. If SIZE under 1500000: reschedule this exact message send_later delay_minutes=20, stop. 4. If SIZE 1500000 or over: update brain doc in Claude project, push fresh Transfers/transfer_enquiry_builder.md to imcl75/claude_files incrementing session number by 1, tell Innes: ⚠️ Context large — transferred. New session prompt: [paste session start prompt from transfer doc]"

STEP 1: Fetch Transfers/transfer_enquiry_builder.md from imcl75/claude_files — token is in the brain doc. Raw fetch only, do not clone or browse that repo.

STEP 2: Read the brain doc from the Claude project.

STEP 3: Clone the repo fresh. Check if Innes has confirmed the SCS slide. If yes, mark it locked in the brain doc and continue with the next slide type. If not, the PPTX was already sent — ask Innes to confirm.
```
