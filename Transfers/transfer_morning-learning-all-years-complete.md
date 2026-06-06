# Transfer: Morning Learning tools — all years complete

**Generated:** 2026-06-06
**Originating focus:** Completing Y1–Y4 morning learning tools (phase mechanism, pickFresh, bank expansion, assessment drill panels) to match the Y5/Y6 standard.
**Skill in use:** none (direct file editing + git push)

---

## Status

All six year groups are feature-complete and deployed. Original transfer doc goals fully met. Session also added assessment-specific drill panel types to Y1, Y4, and Y6.

---

## What's been produced

All files at `/Users/innes/projects/staff-tools/morning/` → `https://staff.wallscourt-farm-academy.co.uk/morning/[year]-[class]/`

| File | Version | State |
|------|---------|-------|
| `year1-beech/index.html` | b.06.06.26b | Final |
| `year2-willow/index.html` | w.06.06.26d | Final |
| `year3-acer/index.html` | a.06.06.26d | Final |
| `year4-maple/index.html` | m.06.06.26o | Final |
| `year5-hazel/index.html` | h.06.06.26g | Final (unchanged this session) |
| `year6-elm/index.html` | e.06.06.26i | Final |

---

## Decisions locked in

### Architecture (all files)
- **Phase mechanism**: `getSchoolPhase()` returns 1–5 from Sep 1. `CURR_WT=[0,0.15,0.35,0.55,0.75,0.95][phase]`. `pickPhased(prev,curr)` on DEFAULT_TT (filter `yr!==N`) and KNOWLEDGE_QUIZ (filter `subject.startsWith('YN')`).
- **pickFresh**: 15-item localStorage window per bank, prefix `yN_seen_`
- **pickNFresh** (Y1 only): picks N distinct items from bank avoiding recently seen
- **getActivityPool()**: phase-weighted type list. Pool must have **no duplicate entries** — `indexOf` finds first occurrence only, duplicates make later entries unreachable in toggle cycle.
- **Version tag**: phase label + assessment badge appended in `init()`

### Assessment drill panels
- **Y4 `mtcdrill`** (Spr1+): default view. 4 quads, 2-column grid — Quick Fire (14), Missing Number (12, mix `? × n` and `n × ?`), Table Focus (`Math.max × Math.min`, 2-col), Division Link (12). `color:transparent` on hidden answers. Reveal All toggles. Pool (no dups): `['mtcdrill','combined','maths','number','literacy','spotmistakecombo','humanities','boggle']`.
- **Y4 MTC table selector**: `y4_mtc_tables` localStorage. Top of Setup panel, checkboxes ×2–×12. `getMTCTables()` used in `genMTCFacts()` and focus table rotation.
- **Y6 `satsdrill`** (Spr1+): 4 quads — Punctuation (GPS_PUNCTUATION 47 entries), Grammar (GPS_GRAMMAR 45 entries), Arithmetic (6 from ARITHMETIC_SATS 60 entries), Word Class (GPS_WORD_CLASS_CONTEXT 40 entries — `(1)word` format with green number chips, pupils write `1=adj` on whiteboards). `renderGPSQ()` / `renderGrammarQ()` helpers. Reveal All toggles; individual items tap-to-reveal.
- **Y1 `phonicsscreen`** (Spr1+): 4 quads — Real Words (6 PHONICS_BLEND), Alien Words (6 ALIEN_BLEND, purple header), Segment & Blend (4 words + phoneme split), Grapheme of Day (rotates by date).

### CSS critical rules
- Assessment panel body: use `#panel-id .cpanel-body` (specific) not a class alongside `.cpanel-body` — otherwise `.cpanel-body`'s `overflow:hidden` + `justify-content:center` wins and hides content.
- Hidden answers: `color:transparent` (not colour-matching) — box visible as tap cue, number truly invisible.
- MTC comma-gap fix (Y2/Y3/Y4): after inserting new bank entries, run `re.sub(r'([\]}])\n(\{)', r'\1,\n\2', seg)` to add missing commas between original and new entries.
- Apostrophe safety: after agent-generated content, check for unescaped apostrophes in single-quoted JS strings. Run `node --check` on extracted `<script>` block before pushing.

### Colours
- Y1 #e67e22 · Y2 #27AE60 · Y3 #C0157A · Y4 #1798d3 · Y5 #e67e22 · Y6 #27AE60

### localStorage prefixes
- y1_ y2_ y3_ y4_ y5_ y6_ (Y2 was incorrectly using y1_ — fixed this session)

---

## Specific user requirements (verbatim where wording mattered)

> "MTC mode — some additional activities to focus on the skills for MTC" — drill panel is now the DEFAULT view from Spr1, not buried in toggle

> "always write the questions with the larger number first e.g. 3 x 2 (not 2 x 3)" — Table Focus only; Quick Fire and Division Link use natural order; Missing Number restores random mix

> "it would be handy to be able to set the tables which are viewed" — Setup panel top section, persists in localStorage

> "GPS type questions — punctuation (e.g. add semi colon in the correct place). Identify the word class of X in this sentence" — redesigned using 2025 KS2 GPS Paper 1 as reference

> "for 'word class' having a number next to each word makes it easier for the learner to record the word class on their whiteboard" — green number chips, `(1)ancient` → `1 = adjective`

> "SATs reasoning — more questions covering more topics beyond just worded problems" — REASONING_SATS expanded to 75 entries: speed/distance, angles, coordinates, algebra sequences, fractions, statistics, scale/proportion, area/perimeter

---

## Files in play

| Path | Notes |
|------|-------|
| `/Users/innes/projects/staff-tools/morning/year[1-6]-[class]/index.html` | All final |
| CLF Curriculum PDF | `/Users/innes/Library/CloudStorage/GoogleDrive-.../My Drive/Claude Curriculum/CLF_Curriculum_Progression_Summary_v3.pdf` |
| 2025 GPS Paper 1 PDF | `/Users/innes/Library/CloudStorage/GoogleDrive-.../My Drive/GPS/2025_KS2_English_GPS_Paper1_questions.pdf` |

---

## Open questions / blockers

- **Y2/Y3 assessment modes**: not added. Y2 could get Phonics Screen (copy Y1 pattern). Y3 has no specific KS2 assessment.
- **Y5 assessment mode**: no drill panel added. Could add SATs-style GPS+Arithmetic+Reasoning following Y6 pattern.
- **GPS bank spot-checking**: agent-generated entries mostly correct; apostrophe-why and which-punctuation multi-choice options worth verifying against mark schemes in classroom use.

## Immediate next step

All planned work complete. If continuing: live classroom testing feedback → further tweaks. Or start a new resource entirely.
