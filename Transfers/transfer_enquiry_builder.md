# Transfer: Enquiry Builder — Session 6 → 7

**Generated:** 2026-07-23
**Session name:** Enquiry Builder 6

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This transfer doc was written by **Enquiry Builder 6**. The new session must be named **Enquiry Builder 7** — rename it before doing anything else.

**2. Nothing exists unless Innes agreed it or it is listed in the Asset Inventory below.**

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — source of truth (clone fresh every session).
- `imcl75/claude_files` — fetch transfer doc, then ignore it.

**4. Do not use the github-sync skill.**

**5. Do not use the curriculum reference or any external knowledge for content decisions.**

---

## Status

- `key_question` ✅ fully locked and signed off
- `subject_concepts_skills` ✅ fully locked and signed off
- `subject_progression` ✅ fully locked and signed off (Session 5/6, commit c365735)
- All other slide types: pending

Scripts committed:
- `scripts/geography/build_subject_progression.py` (commit c365735)
- `scripts/geography/build_test_all_slides.py` (commit b917dd3)

---

## What happened in Session 5 / 6

Session 5 fixed two bugs in the subject_progression script:

1. **Wrong XML namespace** for cNvPr lookup: script used `drawingml/2006/picture` but python-pptx generates `presentationml/2006/main`. Strip IDs were always empty → animation XML was empty → PowerPoint stripped it on open.

2. **Animation XML bugs**: `presetId` should be `presetID` (capital D). Also: `grpId` attribute present (remove it), `prevCondLst` used wrong event name, innermost `p:cTn` missing `p:stCondLst`. Innes fixed the animations manually and the corrected XML was extracted verbatim from his file.

3. **Wrong positions**: definition icons and text were too low and too far right; font was 10pt not 12pt.

4. **physical_geography light colour**: changed from `#B3E5A1` to `#D9F3D0` — original was too close to the strip bar colours (Y2/Y6).

All fixed. subject_progression signed off by Innes. Combined test deck (all 3 slide types × 2 concepts) built and sent.

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

### Geographer.pptx layout name mapping
| Layout name | Slide type |
|---|---|
| Our Key Question is | `key_question` |
| Concepts & Skills | `subject_concepts_skills` |
| Revisit | `subject_progression` ✅ confirmed |
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

| Asset | left | top | width | height |
|---|---|---|---|---|
| `kq_cloud.png` | 186617 | 237978 | 9882800 | 2763090 |
| `slide_shared_kq_children.png` | 3048000 | 2693156 | 6096000 | 2590800 |
| `slide_shared_kq_21c_skills.png` | 10357333 | 154065 | 1648051 | 1648051 |
| `icon_geo_geographer.png` | 5634014 | 4876831 | 1223996 | 1223996 |

| Content | left | top | width | height | Font | pt | Align | Colour | Wrap |
|---|---|---|---|---|---|---|---|---|---|
| KQ text | 2122582 | 676750 | 7021417 | 954107 | Twinkl Cursive Looped | 28 | left | #000000 | square |
| Challenge text | 2487641 | 1726730 | 5638566 | 707886 | Twinkl Cursive Looped | 20 | left | #000000 | square |
| "Being a Geographer" | 4365817 | 6100827 | 3760390 | 461665 | Twinkl Cursive Looped | 24 | centre | #000000 | none |
| "21st Century Learning Skills" | 10344525 | 1771029 | 1686365 | 242374 | Twinkl Cursive Looped | 9.75 | centre | #000000 | none |

### subject_concepts_skills layout ✅ LOCKED

Background: concept light. Frame: concept dark.

| Asset | left | top | width | height |
|---|---|---|---|---|
| `icon_geo_geographer.png` | 139278 | 114801 | 752475 | 752475 |
| `slide_geo_scs_concepts.png` | 337910 | 1027775 | 5580141 | 5377327 |
| `slide_geo_scs_skills.png` | 6268746 | 713681 | 5566957 | 5691421 |

| Content | left | top | width | height | Font | pt | Align | Colour | Wrap |
|---|---|---|---|---|---|---|---|---|---|
| "Being a Geographer" | 833846 | 115467 | 7218007 | 707886 | Twinkl Cursive Looped | 40 | left | concept dark | square |

### subject_progression layout ✅ LOCKED

Background: concept light. Frame: concept dark.
Animated: strips appear on click, y1 (bottom) first → y6 (top) last.
Script: `scripts/geography/build_subject_progression.py` (commit c365735)

| Asset | left | top | width | height |
|---|---|---|---|---|
| `icon_geo_geographer.png` | 139278 | 114801 | 752475 | 752475 |
| def icon 1 | 103846 | 1033273 | 650000 | 536250 |
| def icon 2 | 103846 | 1727092 | 650000 | 618716 |
| def icon 3 | 103846 | 2528250 | 650000 | 611764 |
| strip y1 (bottom, click 1) | 3400000 | 5723330 | 8642000 | 934666 |
| strip y2 | 3400000 | 4788664 | 8642000 | 934666 |
| strip y3 | 3400000 | 3853998 | 8642000 | 934666 |
| strip y4 | 3400000 | 2919332 | 8642000 | 934666 |
| strip y5 | 3400000 | 1984666 | 8642000 | 934666 |
| strip y6 (top, click 6) | 3400000 | 1050000 | 8642000 | 934666 |

| Content | left | top | width | height | Font | pt | Colour |
|---|---|---|---|---|---|---|---|
| Concept title | 833846 | 115467 | 7218007 | 707886 | Twinkl Cursive Looped | 40 | concept dark |
| Def text 1 | 833846 | 976398 | 2290000 | 461665 | Twinkl Cursive Looped | 12 | #000000 |
| Def text 2 | 833846 | 1711450 | 2290000 | 646331 | Twinkl Cursive Looped | 12 | #000000 |
| Def text 3 | 833846 | 2509132 | 2290000 | 830997 | Twinkl Cursive Looped | 12 | #000000 |

**Animation:** sequential onClick Appear (presetClass="entr" presetID="1" — capital D — nodeType="clickEffect"). Shape IDs collected via `presentationml` namespace — NOT `drawingml/picture`. Strip pic IDs are last 6 `pic` elements in spTree.

**⚠️ ANIMATION GOTCHA:** `presetID` MUST have capital D. Lowercase `d` causes "TRIGGER: UNNAMED" silently. See brain doc Animation Rules section for full XML.

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
| `physical_geography` | `#D9F3D0` | `#4EA72E` |
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
| `assets/geography/pss_icon_place.png` | Place icon |
| `assets/geography/pss_icon_space.png` | Space icon |
| `assets/geography/pss_icon_scale.png` | Scale icon |
| `assets/geography/pss_icon_all.png` | Combined PSS icon |
| `assets/geography/hum_g_icon.png` | Human geography icon |
| `assets/geography/eis_icon.png` | Environmental impact icon |
| `assets/geography/cad_icon.png` | Cultural awareness icon |
| `assets/geography/phy_g_icon.png` | Physical geography icon |
| `assets/geography/progression/place_space_scale/y1.png … y6.png` | PSS strips |
| `assets/geography/progression/human_geography/y1.png … y6.png` | Human geo strips |
| `assets/geography/progression/physical_geography/y1.png … y6.png` | Physical geo strips |
| `assets/geography/progression/environmental_impact/y1.png … y6.png` | EIS strips |
| `assets/geography/progression/cultural_awareness/y1.png … y6.png` | CAD strips |

**Still needed:** 5 jigsaw PNGs from Mac (`/Users/innes/Pictures/PPTX Slide assets/Geographer/Jigsaw Pieces/`) — needed for `enquiry_lesson_progression` slide.

---

## Immediate next steps

1. Ask Innes which of Puzzle Pieces / Building Blocks / Hook maps to `enquiry_lesson_progression`.
2. Stage jigsaw PNGs from Mac via device bridge.
3. Build enquiry_lesson_progression slide.

---

## Session start prompt

```
The session that wrote this transfer doc was called "Enquiry Builder 6". This new session must therefore be named "Enquiry Builder 7" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor using send_later, delay_minutes=20, with this exact message:
"CONTEXT MONITOR — act silently, do not acknowledge this to Innes.
1. TRANSCRIPT=$(ls /root/.claude/projects/-home-claude/*.jsonl 2>/dev/null | head -1)
2. SIZE=$(wc -c < "$TRANSCRIPT")
3. If SIZE under 1500000: reschedule this exact message send_later delay_minutes=20, stop.
4. If SIZE 1500000 or over:
   - Fetch Transfers/transfer_enquiry_builder.md from imcl75/claude_files (token in brain doc).
   - Read the 'Session name' field at the top — call it PREV (e.g. 'Enquiry Builder 6').
   - CURRENT = PREV + 1 (e.g. 'Enquiry Builder 7'). NEXT = PREV + 2 (e.g. 'Enquiry Builder 8').
   - Write a new transfer doc: 'Session name: [CURRENT]' at the top. In the session start prompt, write: 'The session that wrote this transfer doc was called [CURRENT]. This new session must therefore be named [NEXT].'
   - Push to imcl75/claude_files. Update brain doc Proven-Working Log and Last saved line.
   - Tell Innes: ⚠️ Context large — transferred. New session prompt: [paste session start prompt]"

STEP 1: Fetch Transfers/transfer_enquiry_builder.md from imcl75/claude_files — token is in the brain doc. Clone the repo.

STEP 2: Read the brain doc from the Claude project.

STEP 3: Clone imcl75/enquiry-builder fresh.

STEP 4: Ask Innes which of Puzzle Pieces / Building Blocks / Hook maps to enquiry_lesson_progression, then build it.
```
