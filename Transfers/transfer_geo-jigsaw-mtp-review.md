# Transfer: Geography Lesson Builder — Jigsaw slide complete, MTP review pending

**Generated:** 2026-07-15
**Originating focus:** Fixing and finalising the `build_puzzle_pieces` jigsaw (Connections) slide in `build_geography_lesson.py`, then reviewing MTP JSON structure before a full `build_one_lesson` test.
**Skill in use:** none (manual OOXML builder work)

---

## Status

The jigsaw slide is fully working. Colours, text, animations and positions are all locked in. The builder files on disk are updated and tested. Next step is to review the MTP JSON structure to confirm all required fields are present before running a full end-to-end lesson build.

---

## What's been produced

- `/mnt/user-data/outputs/build_geography_lesson.py` — main builder, **updated and final** for jigsaw slide
- `/mnt/user-data/outputs/geography_registry.py` — registry with positions and PNG filenames, **updated and final**
- `/mnt/user-data/outputs/jig_v9_colour_L5.pptx` — last approved colour/text test (5 lessons, real titles)
- `/mnt/user-data/outputs/jig_v8_L1.pptx`, `jig_v8_L5.pptx`, `jig_v8_L15.pptx` — animation fix test builds
- `/mnt/user-data/outputs/geographers_template.pptx` — base template (do not modify)

---

## Decisions locked in

- **Jigsaw PNG source:** `ASSETS_ROOT/Jigsaw Pieces/` on Innes's Mac = `/Users/innes/Pictures/PPTX Slide assets/Geographer/Jigsaw Pieces/`; sandbox fallback = `jigsaw_tmp/`
- **PNG filenames** (in `SKILL_JIGSAW_PNG`):
  - `questioning_predicting` → `new-Jig-orange-questioning.png`
  - `observing_recording` → `new-Jig-yellow-observing.png`
  - `field_work` → `new-Jig-purple-field-work.png`
  - `map_skills` → `new-Jig-green-map-skills.png`
  - `concluding_communicating` → `new-Jig-blue-concluding.png`
- **Animation logic:** Piece 1 always visible (no timing entry). Pieces 2..N each get a click-reveal `style.visibility` animation. Pieces N+1..15 not rendered. Lesson 1 has no timing element at all (empty timing caused PowerPoint repair).
- **Slide order in full build:** Key Question (1), Concepts & Skills (2), Progression (3), Puzzle Pieces (4), LO (5), KWL/Quiz (6), Vocab (7), variable slides (8+)
- **Jigsaw layout:** `'Puzzle Pieces'` = slideLayout49 for master 3 (physical_geography / green)
- **Text box proportions** (hand-tuned by Innes 2026-07-15):
  - Side margin: 30% of piece width
  - Top offset: 31% of piece height
  - Text box height: 38% of piece height
  - Font: 10pt bold Twinkl Cursive Looped, dark (`#1C1C1C`), `normAutofit`, centre-aligned

- **Piece positions** — all 15 locked in `JIGSAW_PIECE_POSITIONS` in `geography_registry.py`:

```python
JIGSAW_PIECE_POSITIONS = [
    ( -312726, 3569551, 3437304, 3437304),  # slot  1
    ( 1560881, 3554757, 3446656, 3446656),  # slot  2
    ( 3447222, 3556997, 3446654, 3446654),  # slot  3
    ( 5291717, 3544384, 3550011, 3437303),  # slot  4
    ( 7221656, 3538947, 3437303, 3437303),  # slot  5
    ( -322666, 1691479, 3446656, 3446656),  # slot  6
    ( 1547846, 1677908, 3446654, 3446654),  # slot  7
    ( 3382693, 1682081, 3550011, 3437303),  # slot  8
    ( 5333906, 1675668, 3437303, 3437303),  # slot  9
    ( 7205896, 1663481, 3446656, 3446656),  # slot 10
    ( 9090881, 1655639, 3437303, 3437303),  # slot 11
    ( 3421196,  -208063, 3446656, 3446656), # slot 12
    ( 5304404,  -212433, 3446654, 3446654), # slot 13
    ( 7142654,  -202176, 3550011, 3437303), # slot 14
    ( 9087125,  -208042, 3437304, 3437304), # slot 15
]
```

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/user-data/outputs/build_geography_lesson.py` | Final (jigsaw done) | No |
| `/mnt/user-data/outputs/geography_registry.py` | Final | No |
| `/mnt/user-data/outputs/geographers_template.pptx` | Base template, unchanged | No |
| `/mnt/user-data/outputs/test_mtp.json` | Exists on disk — content unknown / not reviewed | No |
| `/mnt/user-data/outputs/lib_ooxml.py` | Unchanged | No |

---

## Open questions / blockers

- **MTP JSON structure not yet reviewed.** Before running `build_one_lesson` with real data, need to confirm what fields the MTP JSON provides per lesson (`lesson_number`, `lesson_title`, `skill_focus`, `puzzle_piece_text`?) and check they map correctly to what `build_puzzle_pieces` and the other slide builders expect.
- `build_history_lesson.py` and `build_science_lesson.py` also exist in outputs — status unknown, not touched this session.

---

## Immediate next step

Read `test_mtp.json` from disk and read the relevant field-consumption sections of `build_geography_lesson.py` (particularly `build_one_lesson` and `build_puzzle_pieces`) to confirm the MTP JSON has all required keys. Fix any mismatches, then run a full `build_one_lesson` test with real MTP data and check all 14 slides in the output.
