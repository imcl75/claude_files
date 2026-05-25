# Transfer: HL PDF redesign + Flask class manager inline editing

**Generated:** 2026-05-25
**Originating focus:** Completing the home learning PDF v2 redesign (Streamlit) and adding inline editing to the Flask class manager.
**Skill in use:** none (direct repo edits to `wallscourtfarm/spelling-homelearning` and `wallscourtfarm/wfa-app`)

---

## Status

All planned work from the previous transfer is complete and live. Innes is testing. No code changes are pending. Possible follow-up items may emerge from testing.

## What's been produced

All changes pushed directly to GitHub repos — no local output files. Summary of what was deployed:

**`wallscourtfarm/spelling-homelearning`**
- `pdf_builder.py` — full `build_hl_pdf()` rewrite (v2 design); new helpers: `_draw_hl_header`, `_draw_hl_col_title`, `_draw_hl_bottom_bar`, `_draw_hl_maths_content`, `_draw_hl_reading_content`, `_draw_hl_image_content`; internal pupil sort removed (caller controls order)
- `app.py` — new Streamlit UI: subject selectors (left/right), title override, mode toggle (Claude generates / Upload image), image uploaders × 2 versions with "Use same for both" checkbox, due-day text input, print order selectbox
- `hl_generator.py` — `generate_hl_content` gains `left_only`, `right_only` flags; `_validate` updated to skip irrelevant checks per flag
- `data_manager.py` — `sort_pupils_for_print(pupil_list, mode)` added (modes: table / cls_alpha / alpha / pair)
- `icons/` — all 13 subject PNGs pushed (extracted from learning-labels page)

**`wallscourtfarm/wfa-app`**
- `templates/class_manager.html` — TABLE column replaced with inline `<input>` saving on blur/Enter via `/api/class/pupil/update`; PAIR column entire cell now clickable to open pair modal; `saveTableInline()` JS function added; CSS for `.inline-tbl` and `.pair-cell` added

## Decisions locked in

- Header: 13mm, white bg, YG (#1798d3) bottom border 2pt, logo left, "Maple Learning Zone — T6W1 · Name" at 11pt, "Home Learning due: Thursday" right-aligned 11pt
- Column title: 12pt bold navy, underlined in YG, 8mm subject icon right side; LGREY separator below
- Content area: 132.5 × 155.5mm fixed every week regardless of subject
- Bottom bars: white, YG top border only, TT Rockstars QR always left, Spelling Shed QR always right
- Print order selectbox defaults to "By table group (for handing out)"
- Pupil sort is caller-controlled — `build_hl_pdf` does NOT re-sort internally
- Streamlit app is public and searchable (confirmed by Innes)
- Flask class manager inline table edit: saves immediately on blur/Enter, Escape reverts; no full reload — updates `_pupils` in memory only
- Pair cell: whole cell clickable in non-pair-mode; Unpair button still works independently

## Specific user requirements

> "the content area for 'maths' (and all others) can be made taller"
> "the bottom area doesn't need the pale blue - plain white is fine"
> "if the home learning is about e.g. science then I would want to be able to have the scientist logo"
> "the content area sizes (133x156) can stay exactly the same every week"

Spelling page instruction must always include rule explanation after rule title when provided: `rule_title – rule_explanation`.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `wallscourtfarm/spelling-homelearning` → all files | live, current | No — fetch via GitHub API using PAT |
| `wallscourtfarm/wfa-app` → `templates/class_manager.html` | live, current | No — fetch via GitHub API |

**GitHub PAT:** `ghp_REDACTED_see_spelling-homelearning_secrets`

## Open questions / blockers

- Inline table save in Flask class manager: untested under real conditions — confirm writes are reaching GitHub data repo correctly
- Single-column generate modes (left_only / right_only) untested end-to-end — Claude prompt may return unexpected JSON structure
- Image upload "Use same for both" checkbox: confirm adapted PDF receives correct image bytes (Streamlit file uploader state may clear on rerun)
- Streamlit app sharing confirmed public — no action needed

## Immediate next step

Wait for Innes's test results. If issues arise, fetch the relevant file from the repo, diagnose, fix, push. Most likely failure points listed above under open questions.
