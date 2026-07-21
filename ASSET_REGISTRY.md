# Asset Registry

This repo is the **single source of truth** for every asset, template, image, font, and style used in any WFA Maple Learning Zone builder. If a builder asks you for a file, it must be in this registry. If it is not, stop and commit it before building.

Last updated: 2026-07-21

---

## Rules

1. **Never ask Innes to upload an asset that should already be here.** Run `python restore_history_assets.py` (or the equivalent for the builder you are using) and try the repo first.
2. **When something works and Innes approves it, commit it immediately** — same session, before closing.
3. **Binary assets (PNGs, PPTXs, TTFs) cannot be fetched by the github-sync fetch mechanism** — they must be committed to the repo in the correct folder.
4. **Do not move assets between folders without updating the registry and all builder files that reference them.**
5. **If a builder silently skips a missing asset, that is a bug.** All builders must pre-flight check assets and abort if anything is missing.

---

## Shared assets — used by multiple builders

**Repo path:** `Assets/Shared/`

| File | Used by | Notes |
|------|---------|-------|
| `21C-skills-KQ-slide.png` | History | Also stored in `History/assets/Historians/` for direct builder access |
| `4-children-KQ-slide.png` | History | Also stored in `History/assets/Historians/` for direct builder access |
| `cloud-KQ-slide.png` | Future builders | KQ slide variant |
| `KQ-key-and-text-KQ-slide.png` | Future builders | KQ slide variant |
| `areas-of-study.png` | Future builders | Subject overview graphic |
| `geographer-icon.png` | Future builders | Geographer subject icon |
| `scientist-icon.png` | Future builders | Scientist subject icon |
| `sci-skills.png` | Future builders | Science skills graphic |

---

## History

**Builder:** `History/build_history_lesson.py`  
**Registry:** `History/history_registry.py`  
**Restore script:** `History/restore_history_assets.py`  
**Asset root in registry:** `History/assets/Historians/` (relative to repo; also resolves from Mac path)

Run `python restore_history_assets.py` at the start of any cloud session before using the History builder.

### Static assets (always required)

| File | Registry key | Repo path |
|------|-------------|-----------|
| `hist-icon.png` | `hist_icon` | `History/assets/Historians/hist-icon.png` |
| `hist-sub-concepts.png` | `sub_concepts` | `History/assets/Historians/hist-sub-concepts.png` |
| `Hist-skill.png` | `skill` | `History/assets/Historians/Hist-skill.png` |
| `21C-skills-KQ-slide.png` | `skills_21c` | `History/assets/Historians/21C-skills-KQ-slide.png` |
| `4-children-KQ-slide.png` | `children_kq` | `History/assets/Historians/4-children-KQ-slide.png` |

### Building block bricks (required per lesson skill_focus)

| File | Registry key | Repo path |
|------|-------------|-----------|
| `Hist-block-yellow-questioning-and-understanding.png` | `questioning` | `History/assets/Historians/` |
| `Hist-block-peach-chronology.png` | `chronology` | `History/assets/Historians/` |
| `Hist-block-pink-sources.png` | `sources` | `History/assets/Historians/` |
| `Hist-block-blue-interpretations.png` | `interpretations` | `History/assets/Historians/` |

### Concept card images (Y1–Y6 per concept used in enquiry)

| Concept | Folder | Prefix | Repo path |
|---------|--------|--------|-----------|
| Civilisation | `Civilisation/` | `civ` | `History/assets/Historians/Civilisation/civ-Y1.png` … `civ-Y6.png` |
| Empire | `Empire/` | `emp` | `History/assets/Historians/Empire/emp-Y1.png` … `emp-Y6.png` |
| Invasion | `Invasion/` | `inv` | `History/assets/Historians/Invasion/inv-Y1.png` … `inv-Y6.png` |
| Monarchy | `Monarchy/` | `mon` | `History/assets/Historians/Monarchy/mon-Y1.png` … `mon-Y6.png` |
| Revolution | `Revolution/` | `rev` | `History/assets/Historians/Revolution/rev-Y1.png` … `rev-Y6.png` |

---

## Geography

**Builder:** `Geography/build_geography_lesson.py`  
**Registry:** `Geography/geography_registry.py`  
**Asset root in registry:** `Geography/assets/` (local; falls back to `/tmp/geo_assets` downloaded from repo on demand)  
**Fonts:** `Geography/fonts/`

The Geography registry auto-downloads assets from the repo to `/tmp/geo_assets` if the local path is not found. No separate restore script required — the builder handles it.

### Base PPTX template

| File | Purpose | Repo path |
|------|---------|-----------|
| `geographers_template.pptx` | **Active base template** — all lessons built from this | `Geography/geographers_template.pptx` |
| `geo_final_PSS.pptx` | Reference / alternative template | `Geography/geo_final_PSS.pptx` |
| `jigsaw-animated.pptx` | Coordinate reference for jigsaw piece layout | `Geography/jigsaw-animated.pptx` |

### Icons (used in KQ, concepts/skills slides)

| File | Repo path |
|------|-----------|
| `geo-concepts.png` | `Geography/assets/geo-concepts.png` |
| `geo-Place-icon.png` | `Geography/assets/geo-Place-icon.png` |
| `geo-space-icon.png` | `Geography/assets/geo-space-icon.png` |
| `geo-scale-icon.png` | `Geography/assets/geo-scale-icon.png` |
| `geo-P-S-S-icon-combined.png` | `Geography/assets/geo-P-S-S-icon-combined.png` |
| `geo-human-geog-icon.png` | `Geography/assets/geo-human-geog-icon.png` |
| `geo-culture-icon.png` | `Geography/assets/geo-culture-icon.png` |
| `geo-physical-geog-icon.png` | `Geography/assets/geo-physical-geog-icon.png` |
| `geo-sustain-icon.png` | `Geography/assets/geo-sustain-icon.png` |
| `Skills.png` | `Geography/assets/Skills.png` |

### Jigsaw pieces (5 approved versions — do not substitute)

| File | Repo path |
|------|-----------|
| `new-Jig-orange-questioning.png` | `Geography/assets/Jigsaw Pieces/` |
| `new-Jig-green-map-skills.png` | `Geography/assets/Jigsaw Pieces/` |
| `new-Jig-blue-concluding.png` | `Geography/assets/Jigsaw Pieces/` |
| `new-Jig-purple-field-work.png` | `Geography/assets/Jigsaw Pieces/` |
| `new-Jig-yellow-observing.png` | `Geography/assets/Jigsaw Pieces/` |

### Progression strip images (Y1–Y6 per concept)

| Concept | Folder | Filename pattern | Repo path |
|---------|--------|-----------------|-----------|
| Culture | `Culture/` | `Culture-prog-y{n}.png` | `Geography/assets/Culture/` |
| Environment | `Environment/` | `Env-prog-y{n}.png` | `Geography/assets/Environment/` |
| Human Geography | `Human Geography/` | `Hum-geo-prog-y{n}.png` | `Geography/assets/Human Geography/` |
| Physical Geography | `Physical Geography/` | `Physical-geo-prog-y{n}.png` | `Geography/assets/Physical Geography/` |
| Place Space Scale | `Place Space Scale/` | `PSS-geo-prog-y{n}.png` | `Geography/assets/Place Space Scale/` |

### Fonts

| File | Repo path |
|------|-----------|
| `TwinklCursiveLooped-Regular.ttf` | `Geography/fonts/` |
| `TwinklCursiveLooped-Light.ttf` | `Geography/fonts/` |

---

## Maths

**Builder:** `Maths/build_lesson_v3.py`  
**Asset root:** `Maths/assets/`

### Templates and PPTXs

| File | Repo path |
|------|-----------|
| `template_v3.pptx` | `Maths/assets/template_v3.pptx` |
| `KQ_Slide_template.pptx` | `Maths/assets/KQ_Slide_template.pptx` |
| `LR_slide.pptx` | `Maths/assets/LR_slide.pptx` |
| `Working_Memory_Template.pptx` | `Maths/assets/Working_Memory_Template.pptx` |
| `rapid_maths_TEMPLATE.pptx` | `Maths/assets/rapid_maths_TEMPLATE.pptx` |
| `key-question-new.pptx` | `Maths/assets/key-question-new.pptx` |
| `WFA_Labels_template.docx` | `Maths/WFA_Labels_template.docx` |

### Slide images

| File | Repo path |
|------|-----------|
| `4 children KQ slide.png` | `Maths/assets/` |
| `cloud KQ slide.png` | `Maths/assets/` |
| `KQ key icon.png` | `Maths/assets/` |
| `maths-icon.png` | `Maths/assets/` |
| `banner_analyse.png` | `Maths/assets/` |
| `banner_attack.png` | `Maths/assets/` |
| `banner_visualise.png` | `Maths/assets/` |
| `i do icon.png` | `Maths/assets/` |
| `we do icon.png` | `Maths/assets/` |
| `you do icon.png` | `Maths/assets/` |
| `you do trio icon.png` | `Maths/assets/` |

---

## Science (EnquiryBuilder)

**Builder:** `EnquiryBuilder/build_science_lesson.py`  
**Registry:** `EnquiryBuilder/science_registry.py`

### Templates

| File | Repo path |
|------|-----------|
| `science-example.pptx` | `EnquiryBuilder/templates/science-example.pptx` |
| `Being_a_Scientist_slide_deck.pptx` | `EnquiryBuilder/templates/Being_a_Scientist_slide_deck.pptx` |
| `KQ_LO.pptx` | `EnquiryBuilder/templates/KQ_LO.pptx` |
| `KQ_and_BeingAScientist.pptx` | `EnquiryBuilder/templates/KQ_and_BeingAScientist.pptx` |
| `quiz_recap_template.pptx` | `EnquiryBuilder/quiz_recap_template.pptx` |

---

## History (EnquiryBuilder templates)

**Builder:** `History/build_history_lesson.py`

### Templates

| File | Repo path |
|------|-----------|
| `history-example.pptx` | `EnquiryBuilder/templates/history-example.pptx` |

---

## Learning Paper / LL sticker sheets

**Asset root:** `LearningPaper/`

### ETIW assets

| File | Repo path |
|------|-----------|
| `ETIW-LKS2-Y3-Y4.png` | `LearningPaper/etiw_assets/` |
| `ETIW-UKS2-Y5-Y6.png` | `LearningPaper/etiw_assets/` |
| `ETIW-Y1.png` | `LearningPaper/etiw_assets/` |
| `ETIW-Y2.png` | `LearningPaper/etiw_assets/` |
| Year-group logos (Y1–Y6) | `LearningPaper/etiw_assets/logo-Y{n}.png` |
| `writer-icon.png` | `LearningPaper/etiw_assets/` |

### LL label assets

| File | Repo path |
|------|-----------|
| Subject icons (artist, athlete, citizen, etc.) | `LearningPaper/ll_assets/icon_{subject}.png` |
| Phase badges (EYFS, Y1, Y2, LKS2, UKS2) | `LearningPaper/ll_assets/phase_{phase}.png` |
| `school_logo.png` | `LearningPaper/ll_assets/` |
| `full_page.png` | `LearningPaper/ll_assets/` |

---

## Spelling

**Builder:** `Spelling/spelling-shed/`

| File | Repo path |
|------|-----------|
| `key_spelling_template.pptx` | `Spelling/key_spelling_template.pptx` |
| `you_do_image.png` | `Spelling/you_do_image.png` |

---

## Writing

**Builder:** `Writing/writing-lesson-pptx/`

| File | Repo path |
|------|-----------|
| `writing_lesson_base.pptx` | `Writing/assets/writing_lesson_base.pptx` |

---

## Shared badges

| File | Repo path |
|------|-----------|
| `badge_ido.png` | `Shared/badges/` |
| `badge_wedo.png` | `Shared/badges/` |
| `badge_youdo_ind.png` | `Shared/badges/` |
| `badge_youdo_trio.png` | `Shared/badges/` |

---

## Home Learning

| File | Repo path |
|------|-----------|
| `ico_inf.png` | `Home Learning/ico_inf.png` |
| `ico_ret.png` | `Home Learning/ico_ret.png` |
| `ico_voc.png` | `Home Learning/ico_voc.png` |

---

## Adding a new asset

1. Commit it to the correct folder in this repo (same session it is first used).
2. Add it to this registry under the correct subject heading.
3. If it is used by multiple builders, also add a canonical copy to `Assets/Shared/`.
4. Update the builder's restore script or registry `_REPO_PATH` if the auto-discovery path changes.
5. Push and confirm the commit appears on GitHub before closing the session.
