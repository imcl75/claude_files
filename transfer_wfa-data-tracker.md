# Transfer: WFA Pupil Data Tracker — bug fixes and feature additions

**Generated:** 2026-05-28
**Originating focus:** Bug fixing and feature development on the WFA Pupil Data Tracker (React/FastAPI/Google Sheets).
**Skill in use:** none (direct GitHub API push + Render deploy hook)

---

## Status

Tracker is live and working. CV/WV/TGT profile flags working end-to-end (enter Y in pupils sheet or via grid, shows in frontend, filters work). Milestones sheet cleaned up. Frontend build pipeline healthy. Several pending items remain from the to-do list.

## Key infrastructure

- **Frontend:** https://wfa-tracker.pages.dev (Cloudflare Pages, auto-deploys from `gh-pages` branch via GitHub Actions on pushes to `main` that touch `frontend/**`)
- **Backend:** https://api.wallscourt-farm-academy.co.uk (Render, deploy hook: `curl -X POST "https://api.render.com/deploy/srv-d8armk0jo6nc739eja90?key=j6LWEYezStU"`)
- **Repo:** wallscourtfarm/wfa-data
- **GH PAT:** [GH-PAT-REDACTED]
- **Auth:** APP_PASSWORD=WFAdata26!
- **Google Sheet:** linked via Setup page in the app

## What was done this session

- Fixed frontend build pipeline (Setup.jsx syntax error — missing `useEffect(()=>{` opening after spreadsheet URL effect)
- Moved clf_vul, wfa_vul, target from milestones sheet → pupils sheet (profile flags, not milestones)
- Added `/pupils/profile` POST endpoint to save the three flags
- Fixed `attainment.py` yeargroup endpoint to include clf_vul/wfa_vul/target in its pupil data (was only returning 8 fields; grid reads from attainment endpoint not pupils endpoint directly)
- Fixed all `get_all_records(numericise_ignore=["all"])` calls (broken in gspread 6.x) across milestones.py, pupils.py, attainment.py — replaced with `get_all_values()` + manual dict building
- Milestones sheet: cleared corrupted data, reset with clean 12-column header
- CV/WV/TGT: enter `Y` to flag, blank to clear (no N needed)

## Current sheet structure

**pupils sheet columns (in order):**
`upn | first_name | last_name | year_group | tutor_group | sex | is_pp | is_fsm | is_sen | sen_status | sen_type | is_lac | is_eal | is_service_child | is_disadvantaged | status | date_added | date_updated | last_seen_in_import | clf_vul | wfa_vul | target`

**milestones sheet columns:**
`upn | gld_pass | phonics_y1_score | phonics_y2_score | ks1_reading | ks1_writing | ks1_maths | mtc_score | ks2_reading_outcome | ks2_writing_outcome | ks2_maths_outcome | date_updated`

## Decisions locked in

- clf_vul / wfa_vul / target are pupil profile flags (not milestone data) — live in pupils sheet, import-safe (not in MUTABLE_FIELDS)
- Bromcom CSV import will never overwrite clf_vul/wfa_vul/target (not in MUTABLE_FIELDS in pupil_import.py)
- Milestones sheet has no clf_vul/wfa_vul/target columns — they were removed
- gspread 6.x: always use `get_all_values()` + manual dict, never `get_all_records(numericise_ignore=["all"])`

## Pending to-do items (from session memory)

1. **Previous Year T6 column group** — frozen read-only column group showing last year's end-of-year attainment data for each pupil
2. **Termly targets for non-score data** — e.g. reading level target by term/year group
3. **Reporting/analysis views** — PP gap, cohort distribution, declining pupils
4. **Bromcom CSV export** — export current data in Bromcom-compatible format
5. **PP/SEN manual override** — currently import-only, need to allow editing in the tool
6. **Y1 (Phonics) and Y4 (MTC) Test Score panels** — placeholder exists in the UI, not yet built
7. **Y5/Y6 morning display tools** — separate project (transfer file exists: outputs/transfer_y5-y6-morning-tools.md)
8. **Staff/games subdomains** — separate project

## Immediate next step

Ask Innes which pending item to tackle first, then proceed. Most likely candidates are the Previous Year T6 column group or PP/SEN manual override as they are data-model additions; reporting views are larger scope.
