# Transfer: Enquiry Builder — Session 3 → 4

**Generated:** 2026-07-23
**Session name:** Enquiry Builder 3

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This session was called **Enquiry Builder 3**. Rename the new session **Enquiry Builder 4** before starting any work. Each session increments by 1.

**2. Nothing exists unless Innes agreed it.** The only files that exist for this project are the 6 assets listed in the Asset Inventory below. No scripts exist yet. No template PPTX exists. Do not look for, fetch, reference or use any file not in that list.

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — source of truth.
- `imcl75/claude_files` — fetch the transfer doc from it, then ignore it. Do not clone or browse it.

**4. Do not use the github-sync skill.**

**5. Do not use the curriculum reference or any external knowledge for content decisions.**

---

## Status

- `key_question` ✅ fully locked
- `subject_concepts_skills` ✅ fully locked and signed off
- `subject_progression` 🔄 next — Innes must identify which Geographer.pptx layout it maps to (Revisit / Puzzle Pieces / Building Blocks / Hook)
- All other slide types: pending

No builder script written yet.

---

## Decisions locked ✅

### Colour rule — EVERY slide
- Slide background fill = concept **light** colour
- Frame border = concept **dark** colour (prstGeom prst="frame", adj1=1241, full slide 0,0,12192000,6858000, solidFill=dark hex, no line stroke)

### Frame border XML
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

### Geographer.pptx layout name mapping (known)
| Layout name | Slide type |
|---|---|
| Our Key Question is | `key_question` |
| Concepts & Skills | `subject_concepts_skills` |
| Revisit | ? |
| Puzzle Pieces | ? |
| Building Blocks | ? |
| Vocabulary | `vocabulary` |
| KS2 What, Why, How | `we_are_learning` |
| Hook | ? |
| I Do | `i_do` |
| We Do | `we_do` |
| You Do Trio | `you_do_trio` |
| You Do | `you_do_independent` |
| Learning Review Editable | `learning_review` |

### key_question layout ✅ LOCKED

Background: concept light. Frame: concept dark.

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

### subject_concepts_skills layout ✅ LOCKED

Background: concept light. Frame: concept dark.

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

### MTP schema
`topic`, `key_question`, `challenge`, `state_of_being`, `year_group`, `year_colour`, `lessons`, `vocabulary`, `ko`, `resources`

Lesson fields: `lesson_number`, `building_block_text`, `day_label`, `concept`, `skill`, `what`, `why`, `success`, `vocabulary`, `quiz`, `slides`

### Canonical concept values
**Geographer:** `place_space_scale`, `physical_geography`, `environmental_impact_and_sustainability`, `human_geography`, `cultural_awareness_and_diversity`

### Canonical skill values
**Geographer:** `map_skills`, `field_work`, `observing`, `questioning`, `concluding`

### Geography colour maps
| Concept | Light | Dark |
|---|---|---|
| `place_space_scale` | `#FFF2CC` | `#FFC000` |
| `human_geography` | `#FFCCCC` | `#C3580C` |
| `cultural_awareness_and_diversity` | `#DDEAF8` | `#4574C4` |
| `physical_geography` | `#B3E5A1` | `#4EA72E` |
| `environmental_impact_and_sustainability` | `#CCCCFF` | `#7030A0` |

| Skill | PNG | Colour |
|---|---|---|
| `map_skills` | `jigsaw_geo_map_skills.png` | `#CBFFA9` |
| `field_work` | `jigsaw_geo_field_work.png` | `#FFAAFF` |
| `observing` | `jigsaw_geo_observing.png` | `#FFFFAD` |
| `questioning` | `jigsaw_geo_questioning.png` | `#FFCEA5` |
| `concluding` | `jigsaw_geo_concluding.png` | `#97F4FF` |

---

## Asset inventory — `imcl75/enquiry-builder` repo

| Path | Description |
|---|---|
| `assets/geography/icon_geo_geographer.png` | Geographer icon |
| `assets/shared/kq_cloud.png` | Cloud banner |
| `assets/shared/slide_shared_kq_21c_skills.png` | 21c skills icons |
| `assets/shared/slide_shared_kq_children.png` | Children image |
| `assets/geography/slide_geo_scs_concepts.png` | Concepts wheel |
| `assets/geography/slide_geo_scs_skills.png` | Skills wheel |

**Still needed:** 5 jigsaw PNGs from Mac.

---

## Immediate next steps

1. Ask Innes which of Revisit / Puzzle Pieces / Building Blocks / Hook maps to `subject_progression`.
2. Extract that layout from Geographer.pptx. Build PPTX with slides 1–3, send, get sign-off.
3. Continue through remaining 15 slide types in the same way.
4. Write the geography PPTX builder script once all 18 slide types are locked.

---

## Session start prompt

```
FIRST: Read the "Session name" field at the top of this transfer doc. Add 1 to that session number and rename this session to "Enquiry Builder [N+1]" before doing anything else. For example, if the transfer doc says "Session name: Enquiry Builder 3", rename this session "Enquiry Builder 4".

STEP 0 (MANDATORY — do this before reading anything): Set up the context monitor using send_later, delay_minutes=20, with this exact message:
"CONTEXT MONITOR — act silently, do not acknowledge this to Innes. 1. TRANSCRIPT=$(ls /root/.claude/projects/-home-claude/*.jsonl 2>/dev/null | head -1) 2. SIZE=$(wc -c < "$TRANSCRIPT") 3. If SIZE under 1500000: reschedule this exact message send_later delay_minutes=20, stop. 4. If SIZE 1500000 or over: update brain doc in Claude project, push fresh Transfers/transfer_enquiry_builder.md to imcl75/claude_files incrementing session number by 1, tell Innes: ⚠️ Context large — transferred. New session prompt: [paste session start prompt from transfer doc]"

STEP 1: Fetch Transfers/transfer_enquiry_builder.md from imcl75/claude_files — token is in the brain doc. Raw fetch only.

STEP 2: Read the brain doc from the Claude project.

STEP 3: Clone the repo fresh. Ask Innes which of Revisit / Puzzle Pieces / Building Blocks / Hook in Geographer.pptx maps to `subject_progression`. Extract that layout and continue working through slide types.
```
