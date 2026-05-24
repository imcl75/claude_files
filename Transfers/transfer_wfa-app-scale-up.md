# Transfer: WFA App — Scaling to Y2–Y6 and open items

**Generated:** 2026-05-24
**Originating focus:** Building and refining the WFA Spelling App at wallscourtfarm.co.uk — Flask/Render, data repo wallscourtfarm/spelling-homelearning. Heavy session: digital bee flow, session management, class management, nav rationalisation, iPad keyboard debugging, spelling correctness logic.
**Skill in use:** none (direct Flask dev)

---

## Status

App is live on Render at `wallscourtfarm.co.uk`. Current version: **v26.05.24u**. All Y4 features are working and tested on iPad. The app currently only serves Y4 (two classes: Y4_IM, Y4_WU). Scaling to Y2–Y6 is the main next priority.

---

## What's been produced this session

All code in `/home/claude/wfa-app/` (GitHub: `wallscourtfarm/wfa-app`, main branch → Render auto-deploy).

### Digital bee / assessment flow
- `routes/digital_sessions.py` — Spelling Bee now has Create session + Download PDFs on one card; `/live/bee/SESSION/PUPIL` pupil page working on iPad; `/live/assess/SESSION` shared assess page for word/rule/homophone digital sessions
- `templates/live_bee_pupil.html` — iPad keyboard: touchstart+click, lowercase keys, shift toggles labels, `isCorrect()` for smart capitalisation, safe-area-inset padding, `{{ items | tojson }}` (was `items_json` — Jinja2 HTML-escape was the root cause of all keyboard failures)
- `templates/live_assess.html` — same keyboard fixes applied
- QR cards PDF: white pill badges (navy text) on colour header, `canvas.roundRect()` not custom path

### Session management
- `routes/digital_sessions.py` — `/sessions` page, `/api/sessions/list`, `/api/sessions/archive`
- `templates/live_sessions.html` — list all sessions (bee + word/rule/homophone), re-download QR, re-process, archive/unarchive

### Class management
- `routes/class_manager.py` + `templates/class_manager.html` — add/edit/remove pupils, move between classes, pair/unpair with colour picker

### Nav rationalisation
- Assessment dropdown: Spelling Bee (paper+digital unified), Word Assessment, Rule Reassessment, Homophones, Session Manager, TT Check
- Learners + Classes → **Pupils ▾** dropdown (Overview = /learners, Manage = /class-manager)
- Print tab: handwriting only (paired lists + recording sheet moved to Spelling Bee; TT sheet moved to TT Check)
- Digital tab removed; `/live/bee` redirects to `/spelling-bee`
- Default class selector: Y4 ALL across all pages (except class manager which needs a specific class)
- Rules page: Stage 4 open by default, Custom Rules at bottom collapsed

### Spelling correctness logic
```javascript
function isCorrect(typed, word) {
  var t = typed.trim();
  if (t.toLowerCase() !== word.toLowerCase()) return false;
  if (word.charAt(0) !== word.charAt(0).toLowerCase()) {
    return t.charAt(0) !== t.charAt(0).toLowerCase();
  }
  return true;
}
```
Rule: if target starts with capital (proper noun/month), typed must also start with capital. Random capitals elsewhere ignored. Applied in both `live_bee_pupil.html` and `live_assess.html`.

---

## Decisions locked in

- All class defaults → 'all' (Y4 ALL) not a specific class, except class manager
- Paired word lists + recording sheet: one card on Spelling Bee, checkbox for recording sheet (checked by default), one "Download PDFs" button triggers both
- Session result appears inline in the generate card, not as a separate card below
- `touchstart` + `click` (not `pointerdown`) for iPad keyboard — `pointerdown` is iOS 13+ only
- `{{ items | tojson }}` not `{{ items_json }}` — Jinja2 auto-escapes plain strings in script tags, breaking JS parse
- Homophone assessment tests ALL words in selected stages (not 2 per rule)
- Confidence thresholds: 90%+ = confident, 60–89% = partial, <60% = developing
- Bee QR cards: white pill badges, navy text (`#1a3c6e`), not colour-matched text (which was illegible for cyan/yellow pairs)
- Rules page: Stage 4 expanded by default; Custom Rules at bottom, collapsed

---

## Specific user requirements

> "homophones should assess all homophone words within the selected set as it's really a case of knowing can they use the correct 'sea' in the correct context"

> "february (incorrect), February (correct), FebRuary (correct), febRuary (incorrect), frieNd (correct), FriENd (correct)"

> "keyboard keys lowercase unless shift (for those few capital letter words)"

> "the percentage should be out of all words (this is true for all assessments) not just words from a completed section"

---

## Files in play

| Path | Notes |
|---|---|
| `wallscourtfarm/wfa-app` (GitHub) | Main branch → Render auto-deploy |
| `wallscourtfarm/spelling-homelearning` (GitHub) | Data repo — class JSONs, sessions, results, cloze sentences |
| `data/classes/Y4_IM.json`, `Y4_WU.json` | 31 + 30 pupils, fully populated |
| `data/classes/Y2.json`, `Y3.json`, `Y5.json`, `Y6.json` | Exist but empty (106 bytes each) — need setup |
| `data/sessions/` | 60+ old Streamlit bee sessions + new Flask sessions |

### Credentials
```
PAT: github_pat_REDACTED
DATA_REPO: wallscourtfarm/spelling-homelearning
Git config: user.email = innes@wallscourtfarm.co.uk, user.name = Innes McLean
Remote: https://imcl75:{PAT}@github.com/wallscourtfarm/wfa-app.git
```

---

## Open items (in rough priority order)

### 1. Scale to Y2–Y6 (main next priority)
Empty class JSON files exist for Y2–Y6. Need to:
- Decide class structure for each year (how many classes, naming convention — currently Y4 uses `Y4_IM` / `Y4_WU`)
- Populate class JSON files with pupils (via class manager UI or bulk import)
- Add year groups to `ALL_CLASSES` in `data_manager.py` (currently only `['Y4_IM', 'Y4_WU']`)
- Update `CLASS_OPTIONS` across all routes that hardcode Y4 classes
- Update the word bank zones: R 0–20, Y1 21–77, Y2 78–130, Y3 131–184, Y4 185–238, Y5 239–289, Y6 290–343 — pupils start at the right zone for their year
- Rules page stage grouping: each year might want a different default stage open (Y2 → Stage 2, Y3 → Stage 3 etc.)
- Consider multi-year-group views: teacher may want to see all years together or filter by year

### 2. Homophone word list data gap (spelling_rules.py) — partially fixed this session
Fixed: 2-31, 2-32, 3-17, 3-29, 4-1, 5-29. Innes will flag more as found.

### 3. Bee data surfacing in Insights
- Spelling Bee results (from digital sessions) not currently feeding into the Insights panel
- Insights uses `rule_confidence` and `homophone_history` — Bee process route updates `mastered`/`word_pos` but doesn't add a structured confidence entry

### 4. Home learning personalisation
- HL currently not personalised from assessment data
- `mastered` / `homophone_mastered` could drive word selection per pupil

### 5. Teaching schedule auto-populate for Settings weekly config
- Currently manual in Settings

### 6. Reporting
- End-of-year spelling reports from assessment data — not started

### 7. Session management — additional features logged
- Re-process results: done
- Archived sessions: done
- Still missing: session status (how many results in vs expected), better result preview before processing

### 8. Pupil/class management — still to add
- Bulk import pupils (CSV)
- SS username/password management (currently in pupil record but no UI)
- `tt_mode` field exists in data but `tt_mode` is missing from some pupil records

---

## Immediate next step

Confirm with Innes the class structure for Y2–Y6:
- How many classes per year? What are the teacher initials/codes?
- Are the existing `Y2.json`, `Y3.json`, `Y5.json`, `Y6.json` files the right structure, or do they need splitting into multiple class files per year (like Y4 has IM and WU)?
- Should Y2–Y6 share the same spelling rules database, or are some stages not applicable?

Once confirmed, update `ALL_CLASSES` in `data_manager.py`, create/populate the JSON files via the class manager, and update CLASS_OPTIONS across all routes.
