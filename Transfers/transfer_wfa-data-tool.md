# Transfer: WFA Pupil Data Management Tool

**Generated:** 2026-05-26
**Originating focus:** Building and iterating the school's replacement for the Excel-based pupil attainment tracker.
**Skill in use:** none (bespoke build)

---

## Status

v3.4 pushed and building. Core grid is working well — Y6 data loads, DOOYA colours display, auto-save on cell exit, read-only past terms, class filter, flag filters (PP/SEN/LAC/EAL), multi-column sort. Several table UX issues resolved tonight. Three major feature areas still to build: targets, reporting/analysis, and export.

## What's been produced

**Live URLs:**
- Frontend: https://wfa-tracker.pages.dev (Cloudflare Pages, auto-deploys from `wallscourtfarm/wfa-data` main branch via GitHub Actions `deploy-frontend.yml`)
- Backend API: https://api.wallscourt-farm-academy.co.uk (Render, `backend/` subfolder)

**GitHub repo:** `wallscourtfarm/wfa-data`
- `backend/routers/attainment.py` — attainment CRUD
- `backend/routers/pupils.py` — pupil list + import
- `backend/routers/setup.py` — class mapping + current term
- `backend/pupil_import.py` — Bromcom CSV normalisation
- `frontend/src/components/YearGroupGrid.jsx` — main grid (v3.4)
- `frontend/src/App.jsx` — shell + sidebar (v3.4)

**Google Sheet:** "WFA Pupil Tracker"
- `pupils` tab — 400 pupils, all year groups, from Bromcom CSV
- `attainment` tab — 295 records (Y6 seeded from DOOYA Excel; T5 current term has blank scores for most)
- `classes` tab — teacher initials mapping (correctly set up for Y1–Y5; Y6 is 6E1/6E2 but initials mapping still needs doing via Setup page)
- `term_settings` tab — current term per academic year

**Credentials:**
- `APP_PASSWORD=WFAdata26!`
- Google service account: `wfa-tracker-app@wfa-tracker.iam.gserviceaccount.com`
- GitHub PAT (workflow scope): `[WFA_GITHUB_PAT — stored in Render env vars and previous transfer]`
- Render env vars hold `JWT_SECRET` and `GOOGLE_CREDENTIALS_JSON`

## Decisions locked in

**Architecture:**
- FastAPI (Render) + React/AG Grid Community (Cloudflare Pages) + Google Sheets as data store
- UPN as universal key
- All interaction through the frontend — Google Sheets never opened directly
- GitHub Actions (`deploy-frontend.yml`) handles Cloudflare Pages deploy on every push to main touching `frontend/**`

**Data model — attainment tab columns:**
`upn, academic_year, term, reading_dooya, writing_dooya, maths_dooya, reading_r1, reading_r2, arith_raw, reasoning_p1, reasoning_p2, gp_raw, spelling_raw, ph_score, ph_phase, reading_speed, writing_speed, reading_level, date_updated`

**DOOYA codes:** `D, O1, O2, Y, A, A - YR, A - Y1, A - Y2, A - Y3, A - Y4, A - Y5` (spaces around dash — canonical)

**DOOYA colours:** D=`#1798d3`, O1=`#2bae62`, O2=`#a8dfc0`, Y=`#E8B84B`, A=`#c0157b`

**Term colours:** T1=blue `#1798d3`, T2=green `#2bae62`, T3=orange `#e57d24`, T4=pink `#c0157b`, T5=purple `#7b2fc0`, T6=gold `#c9a800`

**Grid behaviour (all implemented):**
- First/Last name pinned left; class + flags scroll
- Score column headers rotated vertically
- Right-click score column header → hide; "👁 N hidden" button → restore panel
- Auto-save on cell exit; Revert button restores to page-load state
- Enter key moves cursor down
- Jump-to-term buttons (T1–T6) coloured by term, snapping term to left of viewport
- Past terms read-only (🔒 label, greyed cells)
- Class filter dropdown + PP/SEN/LAC/EAL toggle buttons
- Multi-column sort: Ctrl+click to add secondary sort
- Column widths persist to localStorage (keyed `wfa-col-state-v2-{yearGroup}`); Reset widths button clears and resets

**Critical bug history (all fixed):**
- `numericise_ignore="all"` → must be `["all"]` in gspread 6.x — fixed in `attainment.py`, `pupils.py`, `setup.py`, `pupil_import.py`
- `version` undefined in `App.jsx` sidebar — caused blank page crash
- Missing `function buildRows(d, cmap) {` declaration — caused build failure

**Reading scores:**
- KS2: single R1 score; R2 always blank
- KS1: R1 + R2 separately; Reading Total = R1+R2 (calculated, not stored)
- Calculated totals (R Tot, M Tot, GPS) shown in grid but not stored

## Specific user requirements

> "The backend — Google Sheets — should only really be for setup and holding data. I want to interact with the data solely through the front end."

> "I need to be able to see all data like the excel — 1 year group, whole year's data."

> "I need to be able to edit current and future data, previous data is read only. Many fields are not needed in each year group or every term so those would be hidden."

> "Always tell me the version number and always bump it on every update so I am always certain I am looking at the same version."

## Files in play

| Path | State | Notes |
|------|-------|-------|
| `wallscourtfarm/wfa-data` GitHub repo | Live | All source, auto-deploys |
| `/mnt/user-data/uploads/Y6_DOOYA_25-26_Cohort_Combined_Tracker.xlsx` | Used for seeding | No longer needed |
| `/mnt/user-data/uploads/StudentList_2026-5-26_13_41_32.csv` | Used for import | May need re-upload if re-importing |

## Open questions / still to do

**Immediate table fixes that may still be needed:** Check v3.4 carefully once deployed — the MR1/column truncation, "6..." class code, and "●..." flag dot issues should all be resolved by minWidth enforcement + versioned localStorage key. If anything still shows wrongly, investigate further before moving on.

**Setup still needed (Innes to do):**
- Y6 class initials mapping — go to Setup page and enter teacher initials for 6E1 and 6E2

**Not yet built — priority order Innes gave:**
1. Test data targets — entry per pupil per year, probably stored in a new `targets` sheet tab
2. Reporting on key groups — especially PP gap; cohort attainment distribution; declining pupils; test score vs target. This was described as "the primary purpose of the tool"
3. Test data analysis — individual pupil trends, year-group comparisons
4. Export formats for Bromcom — CSV/spreadsheet in the exact format Bromcom expects for bulk import
5. Linking to/from other tools — e.g. the morning display tools at `wallscourtfarm.github.io`

**Also not yet built:**
- Previous Year T6 column group (frozen, before T1 — shows prior year T6 DOOYA + scores)
- Milestone data (GLD end-R, Phonics end-Y1/Y2, KS1 outcomes end-Y2, MTC end-Y4, KS2 results end-Y6)

## Immediate next step

Check v3.4 has deployed correctly (verify version shows in both sidebar and toolbar). If table issues are resolved, move to the next feature on Innes's list: **test data targets** — ask Innes what fields a target record needs (likely: UPN, academic_year, year_group, reading_target_dooya, writing_target_dooya, maths_target_dooya, and possibly numeric score targets) and whether targets are set once per year or per term.
