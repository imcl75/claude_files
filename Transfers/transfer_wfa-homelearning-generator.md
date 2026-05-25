# Transfer: WFA Home Learning Generator — post-infrastructure, ready for content work

**Generated:** 2026-05-25
**Originating focus:** Fixing the home learning generator after migration from Streamlit to Flask/Render failed due to CPU limits; reverted HL generation back to Streamlit; rebuilt minimal HL-only Streamlit app wired into the Flask ecosystem.
**Skill in use:** none (infrastructure / app code)

---

## Status

Home learning generator is working end-to-end. Streamlit app at `spelling-homelearning.streamlit.app` generates PDFs in ~90 seconds. Flask app on Render handles everything else (assessment, rules, settings, manage pupils). Both share the same GitHub data repo. Innes is ready to explore changes to the actual home learning content/PDF output.

## What's been produced

- `wallscourtfarm/spelling-homelearning` → `app.py` — minimal HL-only Streamlit app (final, deployed)
- `wallscourtfarm/spelling-homelearning` → `app_backup.py` — full original multi-tab app (backed up, untouched)
- `wallscourtfarm/wfa-app` → `routes/home_learning.py` — redirects to Streamlit with `?year={active_year}`
- `wallscourtfarm/wfa-app` → `templates/base.html` — v26.05.25x, HL nav link passes dynamic year
- `wallscourtfarm/staff-tools` → `index.html` — HL card links to Streamlit (no hardcoded year)

## Decisions locked in

- Home learning PDF generation stays on Streamlit permanently — Render free tier (0.1 vCPU) cannot handle ReportLab PDF rendering for 61 pupils
- Flask/Render handles all management (pupils, rules, settings, assessment); Streamlit handles only generation
- Data shared via `wallscourtfarm/spelling-homelearning` GitHub repo — same files, no sync step needed
- Class list in Streamlit is discovered dynamically from `data/classes/` — no code change needed when new year groups are added
- Streamlit `?year=N` URL param filters class selector to that year — Flask passes `active_year` dynamically so Y2 teacher sees Y2, Y4 sees Y4
- UptimeRobot HTTP monitors keep both Render and Streamlit warm (5 min intervals, already set up)

## Current Streamlit app behaviour

- Opens showing only classes for the year group passed via `?year=`
- Green box immediately lists every pupil's first name before generation starts
- Blue info box shows the 5 rule words + confirms 5 personal words = 10 per pupil
- Week and spelling rule shown as metrics (pulled from `weekly_config.json`)
- Default class selection: "Y4 — All" (or equivalent All for the year)
- Step 1/3, 2/3, 3/3 spinners during generation
- Both Standard and Adapted download buttons side by side, persist after clicking (session_state fix)
- WFA blue header bar with logo matching Flask app
- "← Back to WFA Dashboard" link at top and bottom

## Spelling words per pupil (10 total)

- 5 personal words: from `word_pos` in pupil's class JSON via `get_active_words(word_pos, mastered, 5)`
- 5 rule words: from the week's main spelling rule (`main_words` from custom or built-in rule)
- Both passed to `build_hl_pdf()` as `key_words_map` and `rule_words` respectively
- Custom rules (stage 0, e.g. "0-3") loaded from `data/custom_rules.json`

## Flask app current state

- Version: v26.05.25x (deploy this to Render if not already done)
- `/home-learning` route: redirects to `https://spelling-homelearning.streamlit.app/?year={session_year}`
- `get_rule()` in `data_manager.py`: fixed to handle custom rules (stage 0)
- `data_manager.py` `_get_file()` helper: must exist for `get_rule` to work — verify this if issues arise

## Repos and URLs

| Thing | URL |
|---|---|
| Flask app | `https://wallscourt-farm-academy.co.uk` |
| Streamlit HL | `https://spelling-homelearning.streamlit.app/` |
| Staff tools | `https://staff.wallscourt-farm-academy.co.uk` |
| Data repo | `wallscourtfarm/spelling-homelearning` (GitHub) |
| Flask repo | `wallscourtfarm/wfa-app` (GitHub) |
| PAT | `[PAT-REDACTED]` |

## Open questions / blockers

- Streamlit app needs to be made **public** in Streamlit Cloud settings (share.streamlit.io → spelling-homelearning → Settings → Sharing → Public) if not already done — currently may require Streamlit login
- Innes wants to explore changes to the actual home learning content and PDF output — specifics not discussed yet

## Immediate next step

Ask Innes what he wants to change about the home learning generation — likely the content Claude produces (maths questions, reading passage, spelling layout) or the PDF visual design. Read `wallscourtfarm/spelling-homelearning/hl_generator.py` and `pdf_builder.py` at the start of the new chat to understand current content generation before making any changes.
