# Transfer: Geography lesson builder — puzzle pieces, vocab/quiz, LO fix

**Generated:** 2026-07-13
**Originating focus:** QA fixes on `build_geography_lesson.py` — three remaining bugs after progression slides confirmed working.
**Skill in use:** none (direct Python OOXML build)

---

## Status

Three bugs remain unfixed. All other slides (key question, concepts & skills, progression, KWL, LO content, i_do/we_do/you_do/you_do_trio, learning review) are confirmed working. Progression slides across all 5 concepts have been signed off by Innes. The three bugs below need a focused rethink.

---

## What's been produced

- `/mnt/Geographer/geo_qa_L1_v4.pptx` — L1 test build, confirmed broken on puzzle pieces
- `/mnt/Geographer/geo_qa_L2_v4.pptx` — L2 test build, confirmed broken on puzzle pieces + vocab
- `/mnt/Geographer/progression_*.pptx` (×5) — all signed off, do not touch
- `/mnt/user-data/outputs/build_geography_lesson.py` — main builder (current state, 3 bugs in it)
- `/mnt/user-data/outputs/geography_registry.py` — CORRECT, do not change
- `/mnt/user-data/outputs/test_mtp.json` — minimal 2-lesson physical geography MTP for QA builds
- `/mnt/uploads/Geographer.pptx` — base template (do not modify; re-read from uploads each build)

---

## Decisions locked in

- All 5 masters' `PUZZLE_PIECE_GROUPS_BY_MASTER` orderings are confirmed correct — do not touch the registry
- Progression slides: confirmed using Innes's PNG files from `/mnt/Geographer/[Concept folder]/`
- Assets root resolves via glob: `/sessions/*/mnt/Geographer` → `/mnt/Geographer/`
- Font embedding: Twinkl Cursive Looped from `/mnt/uploads/7a6...ttf`

---

## Bug 1 — Puzzle pieces: double rendering (30 clicks, all 15 pieces visible)

### Root cause
`clone_from_layout('Puzzle Pieces', master_idx)` deep-copies the layout's spTree into the **slide's** spTree. But the slide still references the Puzzle Pieces layout via `rId1`. PowerPoint renders BOTH:
- Layout non-placeholder shapes (all 15 groups with layout's own entrance animations)
- Slide non-placeholder shapes (same 15 groups again, with the timing we injected)

Result: 15+15 = 30 entrance animations; all pieces visible from both sets. There is **no OOXML override mechanism for non-placeholder groups** — duplicates always both render.

### Fix required
Change `build_puzzle_pieces` to use a **blank layout reference** for the slide:

1. Call `fresh_geo(work, 'Our Key Question is', master_idx)` (or any layout with no groups) to create a blank slide that references the master but NOT the Puzzle Pieces layout.
2. Read the Puzzle Pieces layout's spTree: `layout_root.find(f'.//{P}spTree')`.
3. Deep-copy ALL elements from the layout spTree into the slide's spTree (background image, decorative shapes, all 15 groups, everything). This replaces `clone_from_layout`.
4. The rId mapping still needs to be done: copy the layout's media relationships into the slide's `.rels` file with fresh rIds, and update `r:embed` references in the copied spTree.
5. Update text/EMF for pieces 1..N as before.
6. Inject timing: strip entrance animations for pieces 1..N-1; keep pieces N..15 with their `presetClass="entr"` animations. **Use IDs from the just-copied slide spTree** (same as layout IDs since we deepcopy without renumbering — this part is fine).

Key point: the slide must NOT reference the Puzzle Pieces layout. Use any other layout from the same master so master styling (background, colours) is preserved.

### Expected behaviour per lesson number
- L1: slide opens with piece 1 hidden. Click 1 reveals piece 1. Pieces 2–15 remain hidden.
- L2: piece 1 visible on open. Click 1 reveals piece 2. Pieces 3–15 remain hidden.
- LN: pieces 1..N-1 visible on open. Click 1 reveals piece N. Pieces N+1..15 hidden.

---

## Bug 2 — Vocab / quiz: content still overflows (5 items spill off slide)

### Root cause
Current fix: explicit `<p:spPr>` with `cy=3700000` (~4.05 in). With 5 items at natural font size, total height ≈ 4.0 in. This fits inside the box without triggering `normAutofit`. So normAutofit never fires and items overflow the VISIBLE content area.

### Fix required
**Do not rely on normAutofit.** Set font size explicitly based on item count:

```python
# In both build_recap_quiz and build_key_vocabulary:
item_count = len(vocab)   # or len(qna)
if item_count <= 4:
    word_sz  = 1800  # 18pt
    def_sz   = 1400  # 14pt (for definition lines)
else:
    word_sz  = 1400  # 14pt
    def_sz   = 1200  # 12pt
```

Set `sz=word_sz` on the word/question run and `sz=def_sz` on the definition/answer run.
Remove `<a:normAutofit/>` and keep `<a:bodyPr>` simple (no autofit).
Keep the explicit `<p:spPr>` with `cy=4350000` (~4.76 in, bottom at ~6.73 in within slide).

This is more predictable than trusting normAutofit. The reduced font sizes at 5 items have been confirmed by Innes to be acceptable.

The two sizes to set on content shape in `build_key_vocabulary`:
- Word paragraph: bold, sz=word_sz
- Definition paragraph: normal weight, sz=def_sz

Same logic for `build_recap_quiz` (question paragraph + answer paragraph).

---

## Bug 3 — LO slide: animations stripped from content text boxes

### Symptom
The three LO content text boxes (WALT / TIB / ISB) appear on slide open with no click-reveal animation. They should animate in on clicks 1, 2, 3.

### Likely root cause
`build_lo` currently just appends static text box shapes to the spTree with no timing. The animations must be added explicitly via a `<p:timing>` element on the slide — they are NOT inherited from the layout.

Looking at `build_lo` (line 875–944): there is NO timing injection. The function builds three text boxes but writes no `<p:timing>` element to the slide. The layout's `KS2 What, Why, How` has its own timing, but since `fresh_geo` creates a slide that references this layout, the layout timing SHOULD apply... but it appears not to.

### Fix required
After writing the text boxes, inject a `<p:timing>` block into the LO slide that animates boxes 501, 502, 503 (the LO content box IDs set in the code) on clicks 1, 2, 3:
- Each click: `<p:set>` changing `style.visibility` from hidden → visible on the target box
- Same pattern as the vocabulary/quiz animation already working in those slides

Check whether `fresh_geo` slides inherit their layout's timing or not. If layout timing runs, double-animation may occur here too (same issue as puzzle pieces). If `fresh_geo` does NOT cause double rendering (because `fresh_geo` shapes are placeholders, not groups), then the LO bug is simply missing timing injection.

---

## Specific user requirements

> "The positions of all 15 pieces are great, just the logic for only displaying them to match the N of the lesson isn't working."

> "Key vocabulary is STILL not fitting on the slide in L2."

> "animations have been removed from the LO slide text boxes"

> "this needs a full re-think, probably transfer to do that in a clean session — focussing specifically on the jigsaw slide animations and 100% fixing the layouts for quiz and vocabulary as this still is not done"

Innes also updated the vocab slide layout in L1 manually and saved over the output file at `/mnt/Geographer/geo_qa_L1_v4.pptx`. Read that file at the start of the new session and extract the updated positions/sizes for the content shape before touching `build_key_vocabulary`.

---

## Files in play

| Path | State | Note |
|------|-------|------|
| `/mnt/user-data/outputs/build_geography_lesson.py` | current, 3 bugs | Main builder — primary target |
| `/mnt/user-data/outputs/geography_registry.py` | correct, do not change | |
| `/mnt/user-data/outputs/test_mtp.json` | ready | 2-lesson physical_geography MTP for QA |
| `/mnt/uploads/Geographer.pptx` | base template | Re-read from uploads; do not modify |
| `/mnt/Geographer/geo_qa_L1_v4.pptx` | manually edited by Innes | Read to extract updated vocab layout positions |

---

## Open questions / blockers

- Need to confirm whether `fresh_geo` slides inherit layout timing (affects LO fix approach). Inspect a `fresh_geo`-built slide XML to check for `<p:timing>` and whether layout timing fires.
- Confirm updated vocab/quiz layout positions from Innes's manual edit of `geo_qa_L1_v4.pptx` before touching those functions.

---

## Immediate next step

1. Read `geo_qa_L1_v4.pptx` (unzip it) and extract the current `<p:spPr>` x/y/cx/cy for the vocab content shape — Innes has updated these positions manually.
2. Fix `build_puzzle_pieces`: change to blank-layout-reference approach (see Bug 1 above).
3. Fix `build_key_vocabulary` and `build_recap_quiz`: explicit font sizes by item count, no normAutofit.
4. Fix `build_lo`: add timing injection for the three LO content boxes.
5. QA build using `test_mtp.json` → check L1 and L2 puzzle pieces, L2 vocab (5 items), LO animations.
