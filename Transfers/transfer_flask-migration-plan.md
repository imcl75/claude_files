# Transfer: Flask migration plan + spelling-homelearning app state

**Generated:** 2026-05-22
**Originating focus:** Long session fixing spelling bee save bugs and TT advance in the WFA spelling-homelearning Streamlit app, ending with a discussion of migrating to Flask for full layout control.
**Skill in use:** none

---

## Status

The Streamlit app (`wallscourtfarm/spelling-homelearning`) is restored to its last working state (commit `2b89b7885d`). All core functionality works. The layout of the Spelling Bee assessment tab is functional but has unavoidable whitespace gaps caused by Streamlit's column system. Innes has asked for a plan to migrate to Flask + plain HTML/CSS/JS for full layout control.

---

## Current app state (Streamlit)

Repo: `wallscourtfarm/spelling-homelearning`  
Live: `wallscourtfarm-spelling-homelearning-main-app-py.streamlit.app` (password protected)  
GitHub PAT: `REDACTED_SEE_STREAMLIT_SECRETS  
Streamlit secrets: `GITHUB_TOKEN`, `ANTHROPIC_API_KEY`, `APP_PASSWORD`

### What works
- **Spelling Bee** tab: card-based pupil rows, word pill selection, saves via `apply_assessment_pupils` — cls short-form (`"IM"`) mapped to full class ID (`"Y4_IM"`) via `yg_class_ids`
- **TT Check** tab: data_editor table, advance via `advance_tt_pupils` (atomic)
- **Word Assessment**, **Rule Reassessment**, **Digital/iPad** tabs: all functional
- **Home Learning** generator: PDF output, column method grid support added today
- **Classes** tab: CSV import, TT tracking import
- Menu publisher: `menu-publisher-new.streamlit.app` (password `wfa-menu`)

### Known remaining layout issue
Spelling Bee assessment rows have ~186px gap between name and pills, ~409px between last pill and rule column. Caused by Streamlit's proportional column system — cannot be solved within Streamlit without breaking the layout entirely (proven today).

### Key bugs fixed today
- TT advance: `advance_tt_pupils` atomic function in data_manager — no `cd` scoping issues
- Spelling Bee save: reads `_bee_acc` dict (populated by `st.pills` in `_child_assess`), maps cls short form to full class ID, calls `apply_assessment_pupils`
- `@st.fragment` retained on `_render_tab_assess` — fragment reruns preserve pill state; full app reruns do not
- `apply_assessment_pupils` in data_manager: atomic load/modify/save, bypasses all fragment scope issues

---

## Flask migration plan

### What Innes asked for
A plain-English explanation of:
1. What migration will take to enact
2. What he'll be able to do that he can't now
3. A plan for implementing it

This needs to be written for Innes to read — clear, non-technical, honest about effort.

---

## What the migration involves

### The architecture
**Current:** Python (Streamlit) does everything — UI, logic, data, PDF generation — all in one file. Streamlit controls the layout.

**Proposed:** Split into two parts:
- **Flask backend** (Python): handles data, PDF generation, GitHub API calls, authentication. Runs on a free server (Render or Railway).
- **HTML/CSS/JS frontend**: handles what the user sees and interacts with. Innes (or Claude) writes the layout exactly as wanted — no column constraints, no framework fighting.

The two parts talk to each other via a simple API. The frontend asks the backend for data; the backend returns it; the frontend displays it however it likes.

### What Innes will be able to do that he can't now
- Pixel-precise layouts: the 20px gaps, compact rows, everything exactly as designed
- Faster UI: no Streamlit re-render lag on every click
- Mobile-friendly design (iPads for the class)
- Custom interactive widgets: drag-and-drop, inline editing, anything HTML/CSS/JS can do
- Multiple pages/routes (e.g. a direct URL for the spelling bee, another for TT check)
- Proper forms with instant validation
- The morning display tools and the assessment app on the same hosting

### What stays the same
- All the Python logic (word selection, assessment, PDF generation) moves across unchanged
- Data stays in GitHub (same JSON files)
- Password protection
- All existing functionality

### Honest caveats
- One-off migration effort: significant. Estimated 2–3 days of Claude work across several sessions.
- Hosting changes: Streamlit Cloud → Render or Railway (both free, both straightforward to set up). Innes needs a free account on one of them.
- No downside in capability — everything Streamlit does, Flask does better or equally well.

---

## Implementation plan

### Phase 1 — Set up Flask skeleton (1 session)
- Create new repo `wallscourtfarm/wfa-app` (or add to existing)
- Flask app with: login route, session auth, one working page (e.g. TT Check)
- Deploy to Render (free tier, auto-deploys from GitHub push)
- Innes verifies he can log in and see a working page

### Phase 2 — Migrate data layer (1 session)
- Move all data_manager functions to Flask routes (REST API endpoints)
- Test: load class data, save assessment, advance TT — all via API calls
- Keep Streamlit app running in parallel during migration

### Phase 3 — Migrate each tab (1–2 sessions per tab)
Order (easiest first):
1. TT Check — simple table, already working logic
2. Spelling Bee — the motivating case; compact layout is the win
3. Word Assessment / Rule Reassessment
4. Home Learning generator
5. Classes / import tools
6. Digital / iPad tab

### Phase 4 — PDF generation
- Move `pdf_builder.py` and `hl_generator.py` to Flask routes
- PDF returned as a download response
- No change to the actual PDF logic

### Phase 5 — Cut over
- Point staff to the new URL
- Keep Streamlit app alive for one term as fallback
- Decommission once confirmed stable

---

## Decisions locked in

- Migration target: **Flask + plain HTML/CSS/JS** (not Next.js, not Dash)
- Hosting: **Render** (free, deploys from GitHub, no credit card)
- Data storage: stays in GitHub JSON files (no database needed at this stage)
- Streamlit app stays live during migration — no big-bang cutover

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `wallscourtfarm/spelling-homelearning` (GitHub repo) | Live, restored to working state | No |
| `data_manager.py` | Working — all atomic save functions present | No |
| `pdf_builder.py` | Working — column method grids added | No |
| `hl_generator.py` | Working — column method guidance in system prompt | No |

## Open questions / blockers

- Does Innes want to proceed with Flask migration? If yes, which tab to build first?
- Does Innes have (or want to create) a Render account for hosting?
- Should the new app be a new GitHub repo or added to the existing one?

## Immediate next step

In a new chat: write the Flask + HTML explanation for Innes to read (plain English, no jargon), covering what it takes, what it unlocks, and the phased plan. Then ask which phase to start with.

If starting Phase 1 immediately: create the Flask skeleton and deploy to Render before touching any existing functionality.
