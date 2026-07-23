# Transfer: Enquiry Builder — Session 5 → 6

**The session that wrote this transfer doc was called "Enquiry Builder 5". This new session must therefore be named "Enquiry Builder 6".**

**Generated:** 2026-07-23

---

## ⚠️ ABSOLUTE RULES — read before doing anything else

**1. Session name:** This transfer doc was written by **Enquiry Builder 5**. The new session must be named **Enquiry Builder 6** — rename it before doing anything else.

**2. Nothing exists unless Innes agreed it or it is listed in the Asset Inventory below.**

**3. The only repos that matter:**
- `imcl75/enquiry-builder` — source of truth (clone fresh every session).
- `imcl75/claude_files` — fetch transfer doc, then ignore it.

**4. Do not use the github-sync skill.**

**5. Do not use the curriculum reference or any external knowledge for content decisions.**

---

## Status (as of Session 5 — all signed off by Innes)

- `key_question` ✅ fully locked and signed off (commit 55aeea1)
- `subject_concepts_skills` ✅ fully locked and signed off (commit 55aeea1)
- `subject_progression` ✅ fully locked and signed off (commit 65b7a3c)
- `enquiry_lesson_progression` ✅ fully locked and signed off (commit 9bb1d4a / 55aeea1)
- Combined deck builder `build_geography_deck.py` ✅ committed and tested (commit 55aeea1)
- **Phase 1 gate: PASSED**

Scripts committed to `imcl75/enquiry-builder`:
- `scripts/geography/build_key_question.py`
- `scripts/geography/build_subject_concepts_skills.py`
- `scripts/geography/build_subject_progression.py`
- `scripts/geography/build_enquiry_lesson_progression.py`
- `scripts/geography/build_geography_deck.py`

---

## What happened in Session 5

1. **enquiry_lesson_progression bugs fixed:**
   - Text box positions extracted from Innes's manually edited PPTX (dx=1,026,720 / dy=1,196,707 / cx=1,326,980 / cy=760,992)
   - Text box not animating fixed — pairs (pic_id, tb_id) collected and passed to animation function

2. **Animation behaviour changed (Innes's decision):**
   - ALL pieces now animate on click (each piece + its text box on the same click), not just the current lesson
   - `nodeType="clickEffect"` for piece, `nodeType="withEffect"` for simultaneous text box
   - 7 cTn IDs per pair, base starting at 3

3. **enquiry_lesson_progression signed off by Innes.**

4. **build_key_question.py and build_subject_concepts_skills.py written** from locked brain doc specs (these slide types were signed off in earlier sessions but had no build scripts in the repo).

5. **build_geography_deck.py written** — combined deck builder taking MTP JSON + optional concept override; outputs all 4 signed-off slide types in order.

6. **Test deck built and sent:** `output/deck_england_and_brazil.pptx` (8 slides, human_geography colouring, from `mtp/reference/england_brazil_mtp.json`).

7. **Brain doc updated** in Claude project with all locked constants and Phase 1 gate passed.

---

## Decisions locked

### enquiry_lesson_progression — text box position (relative to piece top-left)

| Constant | Value (EMU) |
|---|---|
| TXT_DX (x offset) | 1,026,720 |
| TXT_DY (y offset) | 1,196,707 |
| TXT_CX (width) | 1,326,980 |
| TXT_CY (height) | 760,992 |

### enquiry_lesson_progression — animation
- ALL pieces animate, each on its own click
- piece: `nodeType="clickEffect"`, text box: `nodeType="withEffect"` (same click, simultaneous)
- `presetID="1"` — capital D always; lowercase d causes silent failure
- 7 cTn IDs per pair: `base = 3 + i * 7`

### Jigsaw grid
| Row | y (EMU) | Slots | x values (EMU) |
|---|---|---|---|
| Bottom (fills first) | 3,764,939 | 6 | -301,716 / 1,529,421 / 3,360,558 / 5,191,695 / 7,022,832 / 8,853,969 |
| Middle | 1,900,549 | 5 | 1,503,174 / 3,347,458 / 5,178,595 / 7,009,732 / 8,840,869 |
| Top | 41,049 | 4 | 3,321,211 / 5,152,348 / 6,996,011 / 8,847,419 |

Piece size: 3,424,464 × 3,424,464 EMU

### Colour rule — EVERY slide
- Slide background fill = concept **light** colour
- Frame border = concept **dark** colour (prstGeom prst="frame", adj1=1241, solidFill=dark hex, no line stroke)

### Geography colour maps
| Concept | Light | Dark |
|---|---|---|
| `place_space_scale` | `#FFF2CC` | `#FFC000` |
| `human_geography` | `#FFCCCC` | `#C3580C` |
| `cultural_awareness_and_diversity` | `#DDEAF8` | `#4574C4` |
| `physical_geography` | `#D9F3D0` | `#4EA72E` |
| `environmental_impact_and_sustainability` | `#CCCCFF` | `#7030A0` |

### Skill → jigsaw PNG
| Skill | PNG |
|---|---|
| `map_skills` | `jigsaw_geo_map_skills.png` |
| `field_work` | `jigsaw_geo_field_work.png` |
| `observing` | `jigsaw_geo_observing.png` |
| `questioning` | `jigsaw_geo_questioning.png` |
| `concluding` | `jigsaw_geo_concluding.png` |

### MTP schema
`topic`, `key_question`, `challenge`, `state_of_being`, `year_group`, `year_colour`, `lessons`, `vocabulary`, `ko`, `resources`

Lesson fields: `lesson_number`, `building_block_text`, `day_label`, `concept`, `skill`, `what`, `why`, `success`, `vocabulary`, `quiz`, `slides`

### Canonical concept values
`place_space_scale`, `physical_geography`, `environmental_impact_and_sustainability`, `human_geography`, `cultural_awareness_and_diversity`

### Canonical skill values
`map_skills`, `field_work`, `observing`, `questioning`, `concluding`

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

Ask Innes what he wants to build next. Options likely include:
1. Phase 2 — generating actual lesson slides (the individual lesson PowerPoints with content per lesson)
2. Any other slide types he wants added to the geography deck
3. A different subject pipeline (Science or History)

---

## Session start prompt

```
The session that wrote this transfer doc was called "Enquiry Builder 5". This new session must therefore be named "Enquiry Builder 6" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo:
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
(Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on next:
- Phase 2 (individual lesson slides)?
- More slide types for the geography deck?
- A different subject pipeline?
```
