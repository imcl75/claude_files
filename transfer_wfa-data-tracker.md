# Transfer: WFA Data Tracker — continuation

**Generated:** 2026-05-30
**Originating focus:** WFA attainment tracker (React/FastAPI/Google Sheets) — major session completing column hide/show, targets, TT Set dropdown, prev T6, milestones, domain go-live.
**Skill in use:** none (direct repo manipulation via GitHub API)

---

## Status

Tracker is stable and live at `tracker.wallscourt-farm-academy.co.uk`. Tonight's session fixed a long-running column hide/show bug, wired the targets system, built the prev T6 column group, fixed milestones loading, and shipped TT Set as a proper dropdown. All commits pushed and auto-deployed. Ready to continue with items 2, 3, 1 from the feature list (in that order per Innes).

---

## Repo / infra

| Item | Value |
|---|---|
| Frontend repo | `wallscourtfarm/wfa-data` → Cloudflare Pages auto-deploy |
| Backend repo | same repo → Render auto-deploy |
| Frontend URL | `https://tracker.wallscourt-farm-academy.co.uk` |
| Backend URL | `https://api.wallscourt-farm-academy.co.uk` |
| GitHub PAT | `[redacted — see wfa-data repo settings]` |
| Last FE commit | `fd55756` |

---

## Decisions locked in

- **`hiddenCols` is the single source of truth** for ALL column visibility. No `defaultHide` in column defs. `loadHiddenCols(yg)` reads from localStorage key `wfa-hidden-v6-{yg}`, falls back to `buildDefaultHidden(yg)`. Saves synchronously on every update.
- **`hide` in column defs** = `hiddenCols.has(colId)` only. `unlockPast` is in `columnDefs` useMemo deps.
- **TT Set** stores numeric strings 0–11. Custom `TtSetEditor` (forwardRef, ref-not-state pattern) shows dropdown with readable labels. `valueFormatter` renders label from number.
- **NA value** = the string `"NA"` — means data genuinely doesn't exist. Displayed as grey italic, excluded from all stats and target banding.
- **Summary stats denominator** = full cohort (`rows.length`) for all subjects including KS2 Combined.
- **Prev T6 column group** — collapsed by default, toggled via grey "T6" button before T1 in term picker. `applyColumnState` + `window.dispatchEvent(new Event('resize'))` handles layout after toggle. Prev cols have `hide: true` as default in defs, controlled by `useEffect([prevT6Open])`. Excluded from localStorage column-width save.
- **`applyColumnState` works for prev T6 (useEffect)**. Regular column hide/show uses declarative column defs only — no `applyColumnState` in the hide path.
- **Targets** (`backend/targets_config.py`) — built from `target_info.xlsx`. Six tracks: phonics, reading_level, phonics_screen, spelling_pct, mtc_score, times_tables. `expected_for(field, year, term)` and `compare_to_target(field, value, year, term)` are the public API. `term_targets` returned from yeargroup GET endpoint for reading_level, mtc_raw, tt_set per term.
- **Milestones** (`backend/routers/milestones.py`) — single `get_all_values()` call per worksheet. Repair logic moves Y/N from `first_name` column to `gld_pass` if sheet was corrupted. `first_name` and `last_name` columns are reference columns written by backend.
- **`onMouseDown` not `onClick`** on ScoreHeader ✕ button — AG Grid captures click events on header cells.
- **COL_STATE_VERSION = 'v6'** — localStorage key prefix. Bump if column structure changes and old saved state needs clearing.
- **Seed data** — 60 Y4 pupils have fake 2024-25 T6 data in the attainment sheet for demo purposes. Real prev T6 data will populate naturally after next year-end.

---

## Remaining feature items (priority order per Innes: 2, 3, 1)

### 2 — PP/SEN manual override
Currently `is_pp`, `is_sen`, `is_lac`, `is_eal` are import-only (set via Bromcom CSV import). Innes wants to be able to toggle these directly in the grid without re-importing. Discuss UI approach before building — probably a toggle in the pupil row (inline in grid or via a modal).

### 3 — Y1 Phonics screen panel in Test Scores
Y4 MTC test scores panel is built and working. Y1 Phonics screen panel exists as a placeholder. Phonics screen data is in `ph_score` field; targets are in `targets_config.py` under `phonics_screen` (Y1 only, T1–T6, values 18–32). Should follow same pattern as `Y4_SUBJECTS` / `MtcPip`. Panel should show per-term scores against the target threshold.

### 1 — Reporting/analysis views
PP gap, cohort distribution, declining pupils. Needs discussion before building — agree what views are wanted and how they're structured before writing any code.

---

## Files in play

| Path | Notes |
|---|---|
| `frontend/src/components/YearGroupGrid.jsx` | Main grid — all hide/show, TT Set, prev T6, targets logic |
| `backend/routers/attainment.py` | Yeargroup endpoint returns `prev_t6`, `prev_t6_targets`, `term_targets` |
| `backend/routers/milestones.py` | Clean version — single API call per sheet, repair logic |
| `backend/targets_config.py` | Six target tracks from `target_info.xlsx` |
| `backend/main.py` | CORS includes `tracker.wallscourt-farm-academy.co.uk` |

---

## Immediate next step

Start with item 2 (PP/SEN manual override). Fetch current `YearGroupGrid.jsx` and `pupils.py` from repo. Ask Innes: should the override be an inline toggle in the pupil row (clicking the PP/SEN dot flips it), or a separate edit panel? Also confirm: should changes write back to the pupils Google Sheet immediately, or batch-save?
