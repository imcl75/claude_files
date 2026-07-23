# Transfer: Enquiry Builder — Session 8 → 9

**The session that wrote this transfer doc was called "Enquiry Builder 8". This new session must therefore be named "Enquiry Builder 9".**

**Generated:** 2026-07-23

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This transfer doc was written by **Enquiry Builder 8**. The new session must be named **Enquiry Builder 9** — rename it before doing anything else.

**2. Nothing exists unless Innes agreed it or it is listed in the Asset Inventory below.**

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — source of truth (clone fresh every session).
- `imcl75/claude_files` — fetch transfer doc, then ignore it.

**4. Do not use the github-sync skill.**

**5. Do not use the curriculum reference or any external knowledge for content decisions.**

---

## ⚠️ CRITICAL — SLIDE STATE UNKNOWN

Innes reported (Session 7) that actual progress is **2-3 sessions ahead** of what is in these docs. **Before doing any slide work, ask Innes:**

> "Which slides are locked beyond subject_progression? Please list them so I can update the brain doc."

Update the brain doc with his answer before proceeding to any slide work.

---

## Status (as documented — actual may be further ahead)

- `key_question` ✅ fully locked and signed off
- `subject_concepts_skills` ✅ fully locked and signed off
- `subject_progression` ✅ fully locked and signed off (commit 65b7a3c)
- `enquiry_lesson_progression` — BUILT, awaiting sign-off (commit 0203df6)
- All other slide types: UNKNOWN — ask Innes

Scripts committed to `imcl75/enquiry-builder`:
- `scripts/geography/build_subject_progression.py` (commit 65b7a3c)
- `scripts/geography/build_enquiry_lesson_progression.py` (commit 0203df6)
- `scripts/geography/build_test_all_slides.py`

---

## What happened in Session 8

1. **5 jigsaw PNGs committed** (commit 63c2959): `assets/geography/jigsaw_geo_{skill}.png`, 3084×3080 RGBA. Staged from Mac `/Users/innes/Pictures/PPTX Slide assets/Geographer/Jigsaw Pieces/new/`.

2. **`build_enquiry_lesson_progression.py` rewritten** (commit 0203df6):
   - 3-row staggered grid: 6 bottom, 5 middle, 4 top (max 15 pieces)
   - Piece size 3,424,464 × 3,424,464 EMU (extracted from Innes's reference PPTX)
   - Pieces fill bottom row first (lesson 1 = bottom-left), then middle, then top
   - P-namespace fix for pic ID collection
   - Only current lesson's piece gets onClick Appear animation
   - Text from `building_block_text` in lower 28% of piece at 16pt black

3. Test outputs for all 5 concepts at L01 and L14 sent to Innes. **Awaiting sign-off.**

---

## Decisions locked

### Colour rule — EVERY slide
- Slide background fill = concept **light** colour
- Frame border = concept **dark** colour (prstGeom prst="frame", adj1=1241, solidFill=dark hex, no line stroke)

### enquiry_lesson_progression layout (commit 0203df6)

- Layout name in Geographer.pptx: **Building Blocks** (confirmed by Innes)
- Heading text: always "Connections" (not concept title)
- Concept icon(s) + definition(s): same positions as subject_progression
- Jigsaw grid: 3-row staggered (6+5+4, fills bottom-left first)

| Row | y (EMU) | Slots | x values (EMU) |
|---|---|---|---|
| Bottom (fills first) | 3,764,939 | 6 | -301,716 / 1,529,421 / 3,360,558 / 5,191,695 / 7,022,832 / 8,853,969 |
| Middle | 1,900,549 | 5 | 1,503,174 / 3,347,458 / 5,178,595 / 7,009,732 / 8,840,869 |
| Top | 41,049 | 4 | 3,321,211 / 5,152,348 / 6,996,011 / 8,847,419 |

- Piece size: 3,424,464 × 3,424,464 EMU
- "Connections" heading: x=833,846 y=115,467 cx=7,218,007 cy=707,886 — 40pt, concept dark

### Skill → jigsaw PNG (all now in repo)
| Skill | PNG |
|---|---|
| `map_skills` | `jigsaw_geo_map_skills.png` |
| `field_work` | `jigsaw_geo_field_work.png` |
| `observing` | `jigsaw_geo_observing.png` |
| `questioning` | `jigsaw_geo_questioning.png` |
| `concluding` | `jigsaw_geo_concluding.png` |

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

### Animation rules (capital D, always)
`presetID="1"` not `presetId`. Lowercase d causes silent failure. Full XML in brain doc.

### key_question layout — LOCKED

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

### subject_concepts_skills layout — LOCKED

| Asset | left | top | width | height |
|---|---|---|---|---|
| `icon_geo_geographer.png` | 139278 | 114801 | 752475 | 752475 |
| `slide_geo_scs_concepts.png` | 337910 | 1027775 | 5580141 | 5377327 |
| `slide_geo_scs_skills.png` | 6268746 | 713681 | 5566957 | 5691421 |

| Content | left | top | width | height | Font | pt | Align | Colour | Wrap |
|---|---|---|---|---|---|---|---|---|---|
| "Being a Geographer" | 833846 | 115467 | 7218007 | 707886 | Twinkl Cursive Looped | 40 | left | concept dark | square |

### subject_progression layout — LOCKED

Animated: strips appear on click, y1 (bottom) first → y6 (top) last.
Script: `scripts/geography/build_subject_progression.py` (commit 65b7a3c)

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

### MTP schema
`topic`, `key_question`, `challenge`, `state_of_being`, `year_group`, `year_colour`, `lessons`, `vocabulary`, `ko`, `resources`

Lesson fields: `lesson_number`, `building_block_text`, `day_label`, `concept`, `skill`, `what`, `why`, `success`, `vocabulary`, `quiz`, `slides`

### Canonical concept values
**Geographer:** `place_space_scale`, `physical_geography`, `environmental_impact_and_sustainability`, `human_geography`, `cultural_awareness_and_diversity`

### Canonical skill values
**Geographer:** `map_skills`, `field_work`, `observing`, `questioning`, `concluding`

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
| `assets/geography/jigsaw_geo_map_skills.png` | Jigsaw piece — map_skills |
| `assets/geography/jigsaw_geo_field_work.png` | Jigsaw piece — field_work |
| `assets/geography/jigsaw_geo_observing.png` | Jigsaw piece — observing |
| `assets/geography/jigsaw_geo_questioning.png` | Jigsaw piece — questioning |
| `assets/geography/jigsaw_geo_concluding.png` | Jigsaw piece — concluding |
| `assets/geography/progression/{concept}/y1.png … y6.png` | Year-group strips (all 5 concepts) |

---

## Immediate next steps

1. Ask Innes if he has opened the test_elp files and is happy with the enquiry_lesson_progression layout.
2. Ask Innes which slides are actually locked (he said 2-3 sessions ahead of docs).
3. Proceed based on his answers.

---

## Session start prompt

```
The session that wrote this transfer doc was called "Enquiry Builder 8". This new session must therefore be named "Enquiry Builder 9" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo:
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder

STEP 3: Ask Innes:
1. Has he opened the test_elp files — is he happy with the enquiry_lesson_progression layout?
2. Which slides does he want to build next? (He is 2-3 sessions ahead of docs, so some may already be built elsewhere.)
```
