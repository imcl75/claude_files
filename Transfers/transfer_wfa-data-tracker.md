# Transfer: WFA Data Tracker — DOOYA 6 continuation

**Generated:** 2026-05-28
**Originating focus:** Continuing WFA attainment tracker development (React/FastAPI/Google Sheets). Picked up from a failed DOOYA 6 chat via conversation_search.
**Skill in use:** none (direct repo manipulation via GitHub API — PAT in github-sync SKILL.md)

---

## Status

Bromcom CSV export complete and working. Several data entry bugs fixed tonight. Tracker is stable. Ready to move to the remaining feature items tomorrow.

---

## What's been produced

All changes pushed directly to `wallscourtfarm/wfa-data` repo (auto-deploys to Render backend + Cloudflare Pages frontend).

### Tonight's commits (all live)

| Commit | What it does |
|--------|-------------|
| c42cbd3 | Bromcom export: handler moved into component scope, toolbar button added |
| b60587c | CORS: expose Content-Disposition header for CSV filename |
| dfe7b8f | Bromcom filename: reads Content-Disposition, falls back to `Bromcom_Y4_DDMMYY.csv` |
| ada84c6 | Bromcom: StreamingResponse → Response, Sheets calls wrapped in try/except |
| 2ffc884 | attainment: numericise_ignore on load — keeps F/A/B as strings |
| 050f5c4 | RR/MTC: cellDataType:false, mtc_raw uses agTextCellEditor |
| a5d148c | COL_STATE_VERSION bumped to v6 |
| 89cbe48 | Ph (red), A (orange), B (red) fixed colours in RR and MTC columns |
| 46a6fb1 | CRITICAL fix: unlock past terms guard was before unlockPast check — saves for past terms never fired |
| af9abf8 | model: mtc_raw Optional[str] |
| dc7e4dc | attainment: /backfill endpoint (bypasses term read-only check) |
| 71c4713 | diag: /attainment/diag/{upn} endpoint |
| 7c8f77d | load: first-match-wins for duplicate rows |
| d511f93 | Auto-dedup on load: deletes duplicate rows before returning data |
| 79e381d | DELETE /attainment/deduplicate/{upn} endpoint |
| be2916b | api.js: Pydantic 422 errors show readable text, not [object Object] |
| 97a9479 | STRING_FIELDS: add ph_phase, mtc_raw, tt_set — send "" not null |
| 7df6fb9 | model: add tt_set str="", explicit extra=ignore, mtc_raw str="" |
| db879df | Save error: red banner, 8-second timeout |

---

## Decisions locked in

- Bromcom export uses minimal format (no AdmissionNo, no Student ID) — Bromcom accepts this
- Bromcom field IDs are hardcoded in `backend/bromcom_config.py` — if they change, re-download Bromcom CSV and read row 2
- Special RR codes: Ph = red, F = target-band colour (treated as level 31), numbers = normal band
- Special MTC codes: A = orange (absent), B = red (below level)
- Auto-dedup runs on every yeargroup GET load — self-healing for duplicate attainment rows
- Save is cell-by-cell (on Enter/Tab); no bulk Save button — save indicator in toolbar shows Saving… / ✓ Saved / red error banner
- Unlock past terms button (🔒/🔓) in toolbar — allows backfilling data for past terms; was broken until tonight (46a6fb1)
- STRING_FIELDS in frontend: reading_dooya, writing_dooya, maths_dooya, reading_level, ph_phase, mtc_raw, tt_set — these send "" for empty, not null

## Jesse Jones (K803200021037) — resolved

- Was missing from grid: root cause was duplicate attainment rows (5 pairs) — auto-dedup now cleans on load
- Data in Google Sheet was correct all along; the load was returning the wrong (empty) duplicate row
- Past-term saves were silently failing due to the guard bug (46a6fb1) — now fixed
- MTC and other string-code saves were 422ing due to model type mismatch — now fixed

---

## Remaining feature items (priority order agreed)

1. **Termly targets for non-score data** — reading level targets, phonics phase targets etc. Innes uploaded `target_info.xlsx` in the original DOOYA 6 chat but that session failed before implementation. Start by asking Innes to re-upload target_info.xlsx or describe what was agreed. Key question: are targets per-pupil or year-group-level expected values?
2. **Previous Year T6 column group** — frozen read-only column group showing last year's end-of-year attainment
3. **Reporting/analysis views** — PP gap, cohort distribution, declining pupils. Needs discussion before building.
4. **PP/SEN manual override** — currently import-only
5. **Y1 Phonics and Y4 MTC test score panels** — placeholder exists in UI, not yet built

---

## Files in play

| Path | Notes |
|------|-------|
| `wallscourtfarm/wfa-data` (GitHub) | Main repo — backend (FastAPI/Render) + frontend (React/Cloudflare Pages) |
| `backend/routers/attainment.py` | Most active file tonight |
| `backend/routers/bromcom.py` | Export endpoint — complete |
| `backend/bromcom_config.py` | Hardcoded field IDs for Y1–Y6 |
| `backend/models.py` | AttainmentRecord — fixed tonight |
| `frontend/src/components/YearGroupGrid.jsx` | Main grid component — most fixes here |
| `frontend/src/api.js` | Error handling fixed |

GitHub PAT (wallscourtfarm org): read from `wallscourtfarm/wfa-data` or check github-sync SKILL.md for the imcl75 backup PAT. The wfa-data PAT is `[WFA-DATA-PAT-REDACTED]

---

## Open questions / blockers

- Jesse's duplicate rows in the attainment sheet: auto-dedup will clean them on next load, but Innes could also manually delete the 5 empty duplicate rows (the ones with blank DOOYA columns) if he wants the sheet tidy before that
- Termly targets: need Innes to re-share target_info.xlsx — confirm format and whether targets are per-pupil or year-group-level

## Immediate next step

Ask Innes which of the remaining 5 items to tackle first, then ask him to re-upload target_info.xlsx if that's the choice. Fetch current state of YearGroupGrid.jsx and attainment.py from the repo before writing any code.
