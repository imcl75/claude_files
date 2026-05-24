# Transfer: WFA App Flask Development

**Generated:** 2026-05-24
**Originating focus:** Building and extending the Wallscourt Farm Academy spelling app at wallscourtfarm.co.uk — Flask/Render, data repo wallscourtfarm/spelling-homelearning.
**Skill in use:** none (direct Flask dev)

---

## Status

App is live on Render at `wallscourtfarm.co.uk`. Significant session building: Print tab, three paper assessments (word, rule, homophone), Insights page with AI actions, Learners tab, Rules tab fixes, and the first Digital/iPad feature (Spelling Bee sessions with QR cards). Current version: `v26.05.23au`.

---

## What's been produced

All code lives in `/home/claude/wfa-app/` (GitHub: `wallscourtfarm/wfa-app`, main branch → Render auto-deploy).

Key routes added this session:
- `routes/homophone_assessment.py` — Homophone Assessment (all words per stage, SSE import, word-level storage)
- `routes/insights.py` — Class Insights (rule priorities, homophone gaps, spelling spread, AI Actions for Impact + PDF download)
- `routes/learners.py` — Learners tab with expandable detail rows (key spellings, homophones, rule confidence)
- `routes/digital_sessions.py` — Digital/iPad: Spelling Bee session creation, QR card PDF, pupil-facing page (`/live/bee/SESSION/PUPIL`), result submission, result processing

Templates added: `homophone_assessment.html`, `insights.html`, `learners.html` (rebuilt), `live_bee.html`, `live_bee_pupil.html`, `live_error.html`

---

## Decisions locked in

- **Assessment denominator fix:** All three confirm routes (word, rule, homophone) initialise every assessment word as `False` before overlaying Vision results. Denominator = all words in assessment, not just Vision-returned words.
- **Challenge words (rtype==1):** Already excluded everywhere via `r[4] == 0` filter. No UI change needed.
- **Revision words (rtype==2):** Also excluded everywhere — same filter. 168 standard rules remain.
- **Homophone assessment:** Tests ALL words in selected stages (not just 2 per rule). Word-level storage in `pupil["homophone_mastered"]` (flat list). Stage confidence derived dynamically from this set.
- **Confidence thresholds:** 90%+ = confident, 60–89% = partial, <60% = developing.
- **Digital results:** Saved via Flask API `/api/live/submit` (not directly to GitHub — PAT stays server-side).
- **Rules page default:** Stage 4 opens by default; Custom Rules starts collapsed.
- **Assessment dropdown order:** Spelling Bee → Word Assessment → Rule Reassessment → Homophones → Digital/iPad → TT Check.

---

## Specific user requirements

> "homophones should assess all homophone words within the selected set as it's really a case of knowing can they use the correct 'sea' in the correct context, not just can they spell 'sea'."

> "the percentage should be out of all words (this is true for all assessments) not just words from a completed section"

> "revision words — these either duplicate already assessed words / rules or we dont teach them or both" — excluded.

> "1 tablet between 2, pupil A has a paper copy and reads pupil B's words, pupil B types their words and then vice versa. ipad version marks it and makes data available for upload"

---

## Data model (key fields per pupil)

```python
pupil = {
  "first", "last", "id", "cls", "group", "pair_id", "pair_colour",
  "tt_set", "tt_mode",
  "word_pos": int,           # position in WORD_BANK (0–629)
  "mastered": [str],         # key spellings mastered
  "rule_confidence": {       # rule_id → list of entries
    "4-1": [{"week", "rule", "date", "status": "full|partial|none", "correct", "total", "score"}]
  },
  "homophone_mastered": [str],   # flat list of mastered homophone words
  "homophone_history": {         # stage str → list of entries
    "2": [{"week", "date", "correct", "total", "score", "status"}]
  }
}
```

Word bank zones: R 0–20, Y1 21–77, Y2 78–130, Y3 131–184, Y4 185–238, Y5 239–289, Y6 290–343, Post 344–629.

---

## Homophone data issue (NEEDS FIXING — spelling_rules.py)

Current homophone rules have incomplete pairs. Missing partners:

| Rule | Has | Missing |
|---|---|---|
| 2-31 | there, their, here, hear, sea | they're, see |
| 2-32 | quiet, quite, bare, bear, sun | son |
| 3-17 | great, grate, meet, meat, main | mane |
| 3-29 | ball, bawl, break, brake, fair | fare |
| 4-1 | accept, except, peace, piece, plain | plane |
| 5-29 | cereal, serial, complement, compliment, stationary | stationery |

Also check: `there/their/they're` should be a triple in 2-31. Edit `spelling_rules.py` directly — change the `words` tuple for each affected rule. Verify with Innes before changing as it affects what gets assessed.

---

## Next priorities (in order)

### 1. Digital / iPad — shared assessment page
URL: `/live/assess/SESSION_ID` — shared across all pupils for word/rule/homophone assessments.

Flow:
- Teacher creates session from Word Assessment / Rule Reassessment / Homophone Assessment pages (add "Digital session" button alongside "Generate sheets")
- Session saved to `data/sessions/SESSION_ID.json` with word list and type
- All pupils access same URL; pick their name from a dropdown
- Teacher reads words aloud; pupils type on iPad
- Same keyboard UI as bee page (`live_bee_pupil.html`)
- On completion: POST to `/api/live/submit` with `session_type: 'word'|'rule'|'homophone'`
- Processing: same logic as paper import but reads JSON instead of Vision scan

Session data structure:
```python
{
  "session_id": "ABCD1234",
  "created_at": "...",
  "week_ref": "T6W1",
  "type": "word",   # or "rule" or "homophone"
  "items": [{"word": "friend", "sentence": "...", "rule_id": "4-1"}],
  "pupils": [{"id": "p04", "first": "Amir", "last": "Al Arab"}]
}
```

### 2. Session management page
- List all sessions (teacher-facing) with status: n results received / n pupils
- Re-download QR cards for a session
- Re-process results
- Mark session as archived

### 3. Class/pupil management
- Edit learner details (name, group, pair, TT set/mode)
- Pairing UI
- Add/remove pupils
- Move pupil to different class

### 4. Other year groups
- Y2, Y3, Y5, Y6 class files exist in data repo but are empty (106 bytes each)
- Need class setup UI and year-group-appropriate content

---

## Lower priority refinements (logged)

- Bee data surfacing in Insights panel
- Home learning personalisation from assessment data (mastered / homophone_mastered)
- Teaching schedule auto-populate for Settings weekly config
- Reporting: generate end-of-year spelling reports from assessment data

---

## Files in play

| Path | Notes |
|---|---|
| `/home/claude/wfa-app/` | Full working copy — all routes, templates, static |
| `wallscourtfarm/wfa-app` (GitHub) | Main branch → Render auto-deploy |
| `wallscourtfarm/spelling-homelearning` (GitHub) | Data repo — class JSONs, sessions, results, cloze sentences |
| `data/classes/Y4_IM.json`, `Y4_WU.json` | 31 + 30 pupils with mastered/word_pos populated |
| `data/sessions/` | 60+ spelling bee sessions from old Streamlit app |
| `data/rule_cloze_sentences.json` | 160KB — cloze sentences for all rules |
| `data/cloze_sentences.json` | 33KB — cloze sentences for key spellings |

---

## Environment / credentials

```
PAT: [WFA_PAT — check Render env vars or ask Innes]
DATA_REPO: wallscourtfarm/spelling-homelearning
Git config: user.email = innes@wallscourtfarm.co.uk, user.name = Innes McLean
Remote: https://imcl75:{PAT}@github.com/wallscourtfarm/wfa-app.git
Version bump target: base.html → v26.05.23au (current)
```

---

## Immediate next step

Fix the homophone word list data in `spelling_rules.py` — update the 6 rules listed above to include complete pairs/triples. Show Innes the proposed changes before committing (e.g. "2-31 Homophones: adding 'see' and 'they\'re' — making it a 7-word rule. OK?"). Then begin the shared assessment digital page (`/live/assess/`).
