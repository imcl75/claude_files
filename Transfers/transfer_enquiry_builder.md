# Transfer: Enquiry Builder — Phase 1 (Slide Design Session)

**Generated:** 2026-07-23  
**Originating focus:** MTP schema definition, asset intake, slide type palette definition. Phase 1 gate not yet reached — no builder script written yet.

---

## Status

Phase 0 complete ✅. Schema session complete ✅. Asset intake for `key_question` slide complete ✅. No builder script written yet. Next session: continue slide-by-slide design definition — starting with the `key_question` slide layout spec, then through remaining 17 slide types. Once all slide types are fully defined (MTP fields + layout elements), write the geography PPTX builder script.

---

## What's been produced

- `claude/enquiry-builder-brain.md` (Claude project doc — NOT in git repo) — all locked decisions live here
- Git repo `imcl75/enquiry-builder` — clean, 6 asset files only

---

## Decisions locked ✅

### MTP Schema
- `state_of_being`: `"geographer"`, `"historian"`, or `"scientist"` (replaces old `subject` field)
- `strand` field removed — replaced by `concept` and `skill` at lesson level
- `vocabulary` split into three tiers: `top_10` (word/definition/image), `ko` (word/definition), and lesson-level vocab (word/definition only)
- `quiz`: empty `[]` for lesson 1; `[{question, answer}]` from lesson 2 onwards
- `concept` and `skill` both sit at lesson level (not enquiry level) — they can vary lesson by lesson

### Slide type palette (18 types, locked)
`key_question`, `subject_concepts_skills`, `subject_progression`, `enquiry_lesson_progression`, `we_are_learning`, `kwl`, `lesson_quiz`, `vocabulary`, `i_do`, `i_do_image`, `we_do`, `we_do_image`, `you_do_trio`, `you_do_trio_image`, `you_do_independent`, `you_do_independent_image`, `concept_cartoon`, `learning_review`

- `kwl` — lesson 1 only
- `lesson_quiz` — lesson 2 onwards
- Image variants (`_image` suffix) — Claude decides which variant based on lesson content; both variants exist in the palette for flexibility
- Design rules (concept/skill colours, jigsaw, progression images) operate at **lesson level**, not per-slide

### Geography colour maps (locked)

**Concept → light/dark colour pair:**
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

Jigsaw pieces are geography-specific. Historian and scientist use a different (TBD) concept-driven device.

---

## Asset inventory (git repo — only these 6 files exist)

| Path | Description | Size |
|---|---|---|
| `assets/geography/icon_geo_geographer.png` | Geographer icon — geography-specific | 296×299 RGBA |
| `assets/shared/kq_cloud.png` | Cloud banner — all KQ slides, all subjects | 3533×1008 RGBA |
| `assets/shared/slide_shared_kq_21c_skills.png` | 21c skills icons — KQ slide | 600×595 RGBA |
| `assets/shared/slide_shared_kq_children.png` | Children image — KQ slide | 2204×935 RGBA |
| `assets/geography/template/.gitkeep` | Placeholder — no template PPTX (built from scratch) | — |
| `assets/history/.gitkeep` | Placeholder | — |

**Jigsaw pieces NOT yet committed** — they were uploaded by Innes as inline images last session, which can't be saved as files. Innes must connect the folder `/Users/innes/Pictures/PPTX Slide assets/Geographer/` via the device bridge and we stage them in the next session.

---

## Open questions / what to do next

The `key_question` slide assets are all in place. The next session must:

1. **Lock the `key_question` slide layout spec** — positions (in EMU or cm) of:  
   - Cloud banner (`kq_cloud.png`)  
   - Enquiry key question text (from `key_question` field)  
   - Geographer icon (`icon_geo_geographer.png`)  
   - Children image (`slide_shared_kq_children.png`)  
   - 21c skills icons (`slide_shared_kq_21c_skills.png`)  
   - Any background colour (white? concept light colour?)  
   Show Innes a reference screenshot of the Geographer.pptx KQ slide if needed to agree positions.

2. **Stage the 5 jigsaw PNGs from Innes's Mac** — connect `/Users/innes/Pictures/PPTX Slide assets/Geographer/` and stage `jigsaw_geo_*.png` files, agree naming, commit.

3. **Continue through remaining 17 slide types** — same process: agree assets → stage → name → commit → lock layout spec → save brain doc.

4. **Once all 18 slide types are defined → write the builder script.**

---

## Session start prompt (copy this verbatim to start the next session)

```
Read `Transfers/transfer_enquiry_builder.md` from GitHub repo `imcl75/claude_files` (use the github-sync skill to fetch it), then follow the session start protocol in the brain doc. We are in Phase 1 — working through slide type definitions before writing any builder script. Pick up from where the transfer doc says to start. Do not ask for confirmation before starting.
```

---

## Rules reminder

- Jigsaw pieces (5 PNGs) still need to be committed — stage from Mac, do not ask Innes to upload inline.
- Old reference MTP files (`mtp/reference/`) are obsolete — do not use or edit them.
- `output/` is gitignored. Nothing generated goes into the repo.
- Never start Phase N+1 before Phase N gate is passed (Phase 1 gate = one complete lesson deck confirmed correct by Innes).
- Save brain doc after every decision.
- Number all questions.
