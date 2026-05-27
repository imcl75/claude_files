# Transfer: WFA Pupil Data Management Tool

**Generated:** 2026-05-27
**Originating focus:** Iterative build of the WFA attainment tracking web app — UI, grid, Setup page.
**Skill in use:** none (direct code push to GitHub via API)

---

## Status

App is live and deployed. Both frontend (Cloudflare Pages) and backend (Render, auto-deploy on) are active. This session focused on Setup page workflow improvements and grid column fixes. Final push of the session was flag column centring. All changes deployed to `wallscourtfarm/wfa-data` main.

## What's been produced

- `frontend/src/components/YearGroupGrid.jsx` — live (v3.14+), multiple fixes this session
- `frontend/src/components/Setup.jsx` — live, thresholds workflow redesigned

## Decisions locked in

- **SATs thresholds table** is view-only in Setup UI. The 2017–2025 DfE data is hardcoded as `BUILTIN_THRESHOLDS` in Setup.jsx. No editing, no saving from the frontend. "Maintained centrally."
- **Paper year selection** for Y6: small dropdown in each term header (T1–T5 only), populated from `BUILTIN_THRESHOLDS`. Selecting a year auto-fills Met (t2) and Exceeding (t4) for all three tests in that term (Reading, Maths total, GPS total). One dropdown per term, not per test.
- **KS2 Combined column** in Y6 grid: appears at end of Assessment group in each term. Shows GDS (blue) / EXS (green) / WTS (amber). Logic:
  - GDS: writing_dooya = D AND reading_tot ≥ t4 AND maths_tot ≥ t4
  - EXS: all three EXS+ (writing = O1/O2/D, reading_tot ≥ t2, maths_tot ≥ t2), not all GDS
  - WTS: any area below EXS
  - Blank if any required data missing OR no thresholds configured for that term
  - Reads from `testConfig.term_targets['Y6:term:Reading']` and `['Y6:term:Maths (total)']`
- **Column labels fixed**: Ph → `Phonics Scr.`, KS1R/W/M → `KS1 R` / `KS1 W` / `KS1 M`, Comb → `DOOYA Comb`
- **Flag dots (PP/SEN/LAC/EAL)**: centred vertically and horizontally via flex. FlagHeader label centred (`justifyContent:'center'`, not `flex-end`).
- **DOOYA Combined** (existing, renamed): shows ✓ green if all three DOOYA are O2+, ✗ pink if any below O2, blank if any missing. Still named `DOOYA Comb`.

## Architecture reminder

- Frontend: `https://wfa-tracker.pages.dev` — Cloudflare Pages, auto-deploys from `wallscourtfarm/wfa-data` main on any push touching `frontend/**`
- Backend: FastAPI on Render, auto-deploy ON — pushes to main redeploy automatically
- Data: Google Sheets ("WFA Pupil Tracker"), service account `wfa-tracker-app@wfa-tracker.iam.gserviceaccount.com`
- GitHub PAT: `github_pat_REDACTED`
- Auth: `APP_PASSWORD=[APP_PASSWORD_REDACTED]`
- Working files for this project live at `/home/claude/` (YearGroupGrid.jsx, Setup.jsx etc.)

## Key files

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/home/claude/YearGroupGrid.jsx` | latest pushed | No — fetch from repo if missing |
| `/home/claude/Setup.jsx` | latest pushed | No — fetch from repo if missing |

To get latest from repo:
```bash
TOKEN="github_pat_REDACTED"
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/wallscourtfarm/wfa-data/contents/frontend/src/components/YearGroupGrid.jsx" \
  | python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())" \
  > /home/claude/YearGroupGrid.jsx
```

## Open questions / blockers

- Which score columns to show by default per year group — user has not yet specified (pending)
- Y6 KS2 Comb: needs paper year set in Setup → T1–T5 dropdowns for thresholds to populate the combined cell
- Reporting/analysis views (PP gap, cohort distribution, declining pupils) — not yet started
- Previous Year T6 column group (frozen historical data) — not yet built
- Milestone data entry — columns exist in grid, backend exists, no real data yet
- Export for Bromcom (CSV) — not yet started


## Render deploy hook

If auto-deploy stops working, trigger manually:
```bash
curl -X POST "https://api.render.com/deploy/srv-d8armk0jo6nc739eja90?key=j6LWEYezStU"
```

## Immediate next step

Confirm flag centring fix renders correctly (dots centred in cells, headers centred). Then take stock of what Innes wants to tackle next — likely either column visibility defaults per year group, or testing the full Setup → test targets → grid colour-coding flow with real data.
