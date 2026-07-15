# Transfer: Enquiry lesson builder — MTP testing + vocab resource

**Generated:** 2026-07-15
**Originating focus:** Fixing text overflow in the geography lesson builder, then planning next phase: cross-subject MTP testing and a new vocabulary display resource.
**Skill in use:** none (direct builder work on `build_geography_lesson.py`)

---

## Status

Geography lesson builder is in very good shape. All overflow issues resolved and pushed to GitHub. Next session has two goals: (1) test and align the MTP process across all three enquiry subjects (Sci, Hist, Geog), and (2) build a vocabulary display resource — printed word list with image + child-friendly definition, displayed in class for the duration of each enquiry.

## What's been produced

- `Geography/build_geography_lesson.py` in `imcl75/claude_files` — final, commit `e700311`
- `Geography/geography_registry.py` in `imcl75/claude_files` — final, includes `ensure_asset()` with GitHub fallback
- `Geography/assets/` in repo — 44 asset files: 9 concept icons, 5 jigsaw PNGs, 30 progression strips
- `test_v3_L1.pptx` / `test_v3_L2.pptx` — latest test builds, verified in outputs folder

## Decisions locked in

- `_fill_ph` overflow fix is two-layer:
  - Layer 1 (idx >= 10 PHs only): default to explicit `sz="2000"` (20pt) to avoid relying on inherited master font (was 28–32pt). Cap to `sz="1600"` (16pt) if longest line > 65 chars.
  - Layer 2 (all body PHs): `bodyPr` with `wrap="square" normAutofit`. For idx >= 10: also zero internal margins (`lIns=tIns=rIns=bIns=0`) to match layout definition.
- LO slide content boxes: explicit txBox shapes, `sz="1800"` (18pt) + normAutofit. Width 2559050 EMU, height 1698625 EMU. Fits 3–4 lines for typical 30–70 char LO text.
- Asset fallback chain: local ASSETS_ROOT → `/tmp/geo_assets` cache → GitHub raw API. All assets are in `Geography/assets/` in the repo so sandbox builds work without mounted folder.
- Builder uses OOXML direct XML construction (not python-pptx). Shared lib: `lib_ooxml.py`. Registry constants: `geography_registry.py`.

## Specific user requirements

> "this is an ongoing issue and we really need to find a universal fix to stop it happening, rather than patching every time it does"

(Overflow fix is now universal via `_fill_ph` — not slide-specific.)

> "the skill is in really good shape for Sci, Hist and Geog. The MTP process still needs tested for each subject and I want to check the content of these are as aligned as possible between subjects."

> "I also want to consider making a resource which would help less confident learners with key vocabulary from each enquiry — basically a word list with image and short child friendly definition that I would print and display for the duration of the enquiry."

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `Geography/build_geography_lesson.py` (GitHub) | final | No — fetch from repo |
| `Geography/geography_registry.py` (GitHub) | final | No — fetch from repo |
| `test_mtp.json` (local outputs) | rivers / physical geography, 2 lessons | No — in outputs |
| `geographers_template.pptx` (local outputs) | base template | No — in outputs |

## Open questions / blockers

- History and Science lesson builders have not yet been tested with their own MTP JSONs — need equivalent test MTP files for each subject.
- Degree of structural alignment between the three subject builders (slide order, PH indices, variable dispatch) is unknown until tested side by side.
- Vocabulary display resource format: single A4 or A3 per enquiry? One page per word or multiple words per page? Colour-coded by subject? Portrait or landscape? Needs Innes to confirm before building.

## Immediate next step

1. Fetch this transfer file and `build_geography_lesson.py` / `geography_registry.py` from GitHub.
2. Ask Innes to confirm the vocabulary resource format (size, layout, words per page, colour by subject or not).
3. Then: run `build_one_lesson` tests for History and Science builders to check structural parity with Geography; identify any cross-subject MTP field mismatches.
4. Separately, design and build the vocabulary display resource (PDF or PPTX, printable).
