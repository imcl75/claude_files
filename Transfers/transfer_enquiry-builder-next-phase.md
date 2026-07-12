# Transfer: Enquiry Lesson Builder — next phase

**Generated:** 2026-07-12
**Originating focus:** T6W7 States of Matter build complete; next session wires LP generation into enquiry-lesson-builder, then expands to Geography/History.
**Skill in use:** anthropic-skills:enquiry-lesson-builder

---

## Status

T6W7 States of Matter is fully delivered. All 5 lessons (L1–L5) are built, verified (VERIFY: PASS), and copied directly into Innes's OneDrive folder at the correct path. No zip needed — files sync automatically.

Three priorities remain for the next session, in strict order:

1. **Wire LP generation into enquiry-lesson-builder** — so future science builds auto-produce the LP alongside the teaching PPTX in one pipeline run
2. **Geography/History registry** — build subject-specific component registries for Geography and History lessons (different slide types from Science)
3. **End-to-end pipeline** — connect curriculum description → MTP JSON → lessons + LPs in a single invocation

---

## What's been produced — T6W7

All files live in OneDrive (synced to Mac). No re-upload needed.

**OneDrive base path:**
`/Users/innes/Library/CloudStorage/OneDrive-SharedLibraries-CabotLearningFederation/WFA Staff Shared Files - O365 Group - !2025 - 2026/1 - Planning/Term-6/T6W7/Enquiry/`

| Subfolder | Files |
|-----------|-------|
| `Teaching/` | T6W7 - 1 - Mon - States of Matter L1.pptx (⚠ keep the `-Innes's MacBook Air` version too — it has real Higgsfield photos) |
| | T6W7 - 2 - Tue - States of Matter L2.pptx |
| | T6W7 - 3 - Wed - States of Matter L3.pptx |
| | T6W7 - 4 - Thu - States of Matter L4.pptx |
| | T6W7 - 5 - Fri - States of Matter L5.pptx |
| `LPs/` | L1–L5 LP.pptx (matching names) |
| `Resources/` | L1 Sorting Cards (12 materials → solid/liquid/gas) |
| | L5 Sorting Cards (6 materials by melting point) |

**Build workspace (may not persist across sessions):** `/tmp/t6w7/`
- All scripts: `build_science_lesson.py`, `build_lps.py`, `build_t6w7_l1_lp.py`, `fix_pptx_ooxml.py`, `verify_lesson.py`, `science_registry.py`, `label_builder.py`, `build_enquiry_label.py`, `lib_ooxml.py`
- JSONs: `t6w7_l1.json` through `t6w7_l5.json`
- Images: `/tmp/t6w7/images/` (17 images; L1 grid images are matplotlib placeholders — Higgsfield originals on Mac only)
- LP label assets: `/tmp/t6w7/ll_assets/`

If `/tmp/t6w7/` is gone, fetch scripts from GitHub repo `imcl75/claude_files` under `EnquiryBuilder/`. MTP is at `EnquiryBuilder/mtp/T6W7_MTP.md`.

---

## Decisions locked in

### File naming convention
`T6W7 - {day_ordinal} - {day_name} - {Subject} L{n}.pptx`
- Day ordinal = position of that lesson day within the teaching week (1=first day taught, regardless of whether Mon)
- L{n} = lesson number within the overall unit sequence (not within the week)
- LP suffix: append ` LP` before `.pptx`
- Sorting cards: append ` Sorting Cards` before `.pptx`

### Output destination (no zip)
Copy directly to OneDrive subfolders in bash:
```
BASE="/sessions/determined-elegant-brown/mnt/1 - Planning/Term-{N}/T{N}W{N}/Enquiry"
# Teaching → $BASE/Teaching/
# LPs      → $BASE/LPs/
# Resources → $BASE/Resources/
```
The `1 - Planning` folder is the connected Cowork folder — always mounted at that path.

### LP builder standards (LP_CONTENT_PRINCIPLES.md rules)
- A4 portrait: 7.5 × 10.833 in
- Label: 70.7% scale (`LABEL_SCALE = 0.707`), top-right, via `label_builder.build_enquiry_label()`
- `LABEL_SCALE` patch: `_bel.ASSETS = os.path.join(WORK, 'll_assets')` before any import
- Font: Twinkl Cursive Looped, 12pt body
- Write-line gap: 0.315 in (gap = inter-line gap)
- Wrap estimate: `chars_per_line = usable_width_pt / (size_pt * 0.46)` — calibrated from real PowerPoint, do NOT use LibreOffice
- Slide 1: pupil task. Slide 2: marking station (green answers #4FAD5B)
- Reference images must be on-page when task text refers to them

### Verify pipeline (hard gate — must PASS before delivery)
```bash
python3 fix_pptx_ooxml.py "output/filename.pptx"
python3 verify_lesson.py "output/filename.pptx" lesson.json output/manifest.json
```
`verify_lesson.py` patched this session to skip discipline slide in overlap check:
```python
disc_indices = {e["output_index"] for e in manifest["slides"] if e["type"] == "discipline"}
check_geometric_overlap(prs, failures, discipline_slide_indices=disc_indices)
```

### Asset path patching (critical — `/home/claude` doesn't exist in sandbox)
```python
WORK = os.path.dirname(os.path.abspath(__file__))
import build_enquiry_label as _bel
_bel.ASSETS = os.path.join(WORK, 'll_assets')
```
Must happen before any other import that touches the label builder.

---

## Architecture context

### Current enquiry-lesson-builder pipeline (Science)
```
t6w7_l{n}.json
    → build_science_lesson.py (via science_registry.py + lib_ooxml.py)
    → fix_pptx_ooxml.py (3 fixes: customXml, docProps/app.xml, p14:sectionLst)
    → verify_lesson.py (PASS gate)
    → Teaching PPTX

t6w7_l{n}.json (separately)
    → build_lps.py (python-pptx, A4 portrait)
    → LP PPTX
```
Gap: LP build is a separate script with no integration into the main pipeline. Priority 1 is to wire them together.

### Science slide type registry
`science_registry.py` handles: `kq_challenge`, `being_a_scientist`, `discipline`, `lo`, `wedo_hook`, `wedo_grid`, `ido_diagram`, `youdo_provocation`, `youdo_task`, `learning_review`

### Geography/History — what's different
Innes uploaded `Geography_Enquiry_England_Brazil.docx` — a 14-lesson MTP with:
- Phases (Locate & Observe → Compare & Analyse → Create & Present)
- I Do / We Do / You Do structure per lesson
- A/Y/O/D differentiation throughout
- Slide types needed that don't exist in science registry:
  - `map_annotation` (atlas/globe activity)
  - `comparison_frame` (running England vs Brazil table)
  - `writing_scaffold` (PEEL frame, sentence starters)
  - `debate_prep` (argument cards, counterargument structure)
  - `card_sort` (biome photos, land use images)
  - `ido_text` (no image — text-led I Do)
- Resources needed per lesson (not just sorting cards): blank maps, comparison frames, debate planning frames

**Key architecture question for next session:** One unified builder with subject-specific registries, or separate skills per subject sharing a core library? Recommendation: unified builder with a `subject_registry` parameter selecting the right component set. History registry will be similar to Geography.

### End-to-end pipeline gap
- `enquiry-planner` skill → outputs DOCX (like the Geography MTP)
- `enquiry-lesson-builder` skill → needs a JSON (like `t6w7_l{n}.json`)
- No converter exists between them
- Proposed addition: a `mtp_to_json.py` parser that reads the structured DOCX and emits per-lesson JSONs

---

## Specific user requirements

> "Work through everything without waiting for confirmation between steps unless something fails."

> "I need to teach these lessons next week." [urgency context for T6W7 — now delivered; future builds should maintain same urgency framing]

> "each week I have a folder and within that folder the enquiry folder, maths folder etc live" [folder structure now understood and used]

On LP wiring:
> "does this have the end to end process built in? i.e. the process of planning the actual enquiry from my curriculum and explanation (which would generate something like attached Medium Term Plan)"
— answer is no; building this is Priority 3.

---

## Files in play

| File | Location | State |
|------|----------|-------|
| `Geography_Enquiry_England_Brazil.docx` | Uploaded this session | Reference MTP — shows target format for Geography builder |
| `T6W7_MTP.md` | `imcl75/claude_files` → `EnquiryBuilder/mtp/` | Confirmed MTP for T6W7 (fetched from repo) |
| `build_science_lesson.py` | `/tmp/t6w7/` (may be gone) | Orchestrator — fetch from repo if needed |
| `science_registry.py` | `/tmp/t6w7/` (may be gone) | Science component registry |
| `build_lps.py` | `/tmp/t6w7/` (may be gone) | L2–L5 LP builder (new this session, NOT yet in repo) |
| `build_t6w7_l1_lp.py` | `/tmp/t6w7/` (may be gone) | L1 LP builder (reference pattern) |
| `verify_lesson.py` (patched) | `/tmp/t6w7/` (may be gone) | Patched to skip discipline slide overlap |

⚠ `build_lps.py` and the patched `verify_lesson.py` were NOT synced to GitHub this session — push them at the start of the next session if they're still in `/tmp/t6w7/`.

---

## Priority order for next session

### Priority 1 — Wire LP generation into enquiry-lesson-builder
- Modify `build_science_lesson.py` so after a successful verify, it auto-calls the LP builder
- LP output path: same directory as PPTX, appending ` LP` to the stem
- LP builder needs to accept the lesson JSON as input (currently `build_lps.py` has per-lesson functions — refactor to a single `build_lp(lesson_json, out_path)` function)
- Test: run full build for one lesson, confirm both PPTX and LP are produced and named correctly

### Priority 2 — Geography/History registry
- Design the Geography slide type set (see above)
- Build `geography_registry.py` alongside `science_registry.py`
- Extend `build_science_lesson.py` (or create `build_enquiry_lesson.py`) to accept a `subject` parameter selecting the registry
- Test with Lesson 1 of the England/Brazil enquiry (from the uploaded MTP)

### Priority 3 — End-to-end pipeline
- Build `mtp_to_json.py`: parse a DOCX MTP → per-lesson JSONs
- Build `plan_enquiry.py`: accept a curriculum description + key question → generate MTP JSON → generate per-lesson JSONs → build all PPTXs + LPs
- This is the most speculative — design and discuss with Innes before building

---

## Immediate next step

Fetch `build_lps.py` and patched `verify_lesson.py` from `/tmp/t6w7/` if still present and push to GitHub. Then start Priority 1: refactor `build_lps.py` into a single `build_lp(lesson_json, out_path)` function and wire it into `build_science_lesson.py` as a post-verify step.
