# Transfer: WFA domain consolidation, migration and shared assets

**Generated:** 2026-05-25
**Originating focus:** Consolidating all WFA tools (GitHub Pages, Streamlit, Flask) under wallscourt-farm-academy.co.uk, structuring shared assets, and migrating/retiring duplicate repos.
**Skill in use:** none (direct Flask/GitHub dev)

---

## Status

Full audit complete. Architecture agreed. No code written yet for this work — this chat established the plan only. wfa-app (Flask on Render) is the primary platform and has been scaled to Y1–Y6 in a parallel thread today (v26.05.25a deployed). Domain consolidation work starts in a new chat.

---

## Credentials and infrastructure

```
Domain:    wallscourt-farm-academy.co.uk (Cloudflare — Innes owns it)
Flask app: wallscourtfarm/wfa-app → Render auto-deploy → wallscourt-farm-academy.co.uk
Data repo: wallscourtfarm/spelling-homelearning (class JSONs, sessions, results)
PAT:       github_pat_***REDACTED***
Git user:  innes@wallscourtfarm.co.uk / Innes McLean
Current version: v26.05.25a
```

---

## Full tool inventory and decisions

### Zone 1 — Innes only (personal tools, stay on Streamlit for now, not on public site)
| # | Tool | Repo | Status |
|---|---|---|---|
| 6 | Spelling Lesson Generator | wallscourtfarm/spelling-shed-app | Keep on Streamlit |
| 7 | Reading App | wallscourtfarm/reading-app | Keep on Streamlit |
| 10 | Reports | wallscourtfarm/wfa-reports | Keep on Streamlit |
| 11 | Spelling Home Learning (old) | wallscourtfarm/spelling-homelearning | Keep on Streamlit for now |

### Zone 2 — Staff tools (teachers, under wallscourt-farm-academy.co.uk)
| # | Tool | Current location | Decision |
|---|---|---|---|
| 1 | WFA App (spelling/assessment) | Flask — wallscourt-farm-academy.co.uk | ✅ Done, already live |
| 2 | Morning displays Y1–Y6 | GitHub Pages / staff-learning-tools | Merge into staff-tools → staff.wallscourt-farm-academy.co.uk |
| 3 | Menu Publisher | Streamlit / menu-publisher | Migrate into Flask app |
| 4 | SATs Reasoning | Streamlit / staff-learning-tools/sats-reasoning | Migrate into Flask app |
| 5 | Staff Tools (scheduling, cover, labels, booking, rota) | GitHub Pages / staff-tools | → staff.wallscourt-farm-academy.co.uk |
| 8 | Handwriting Tool | Streamlit / wfa-handwriting-tool | Migrate into Flask app |
| 9 | Word Puzzles | Streamlit / word-puzzles | Migrate into Flask app |
| 14 | GPS/SATS static reasoning | GitHub Pages / staff-learning-tools | Merge into staff-tools |

### Zone 3 — Learners (public, no login)
| # | Tool | Current location | Decision |
|---|---|---|---|
| 13 | Learning games (TT, phonics, mastering number, karate, callum) | learning-games repo | → games.wallscourt-farm-academy.co.uk |

### Repos to archive
- `learner-activities` — identical to learning-games (only index.html title differs), last sync was May 13 "Consolidate from learning-games"
- `wfa` — old monorepo origin, superseded by staff-tools + learning-games; games are 2 weeks older than learning-games versions
- `spelling-homelearning` Streamlit app — superseded by wfa-app Flask (data repo of same name is KEPT)
- `staff-tools/spellings-tracker` Streamlit path — appears empty, retire

---

## Domain architecture

| Subdomain | Points to | How |
|---|---|---|
| `wallscourt-farm-academy.co.uk` | Flask app (Render) | Already live |
| `staff.wallscourt-farm-academy.co.uk` | `staff-tools` repo (GitHub Pages) | CNAME → wallscourtfarm.github.io |
| `games.wallscourt-farm-academy.co.uk` | `learning-games` repo (GitHub Pages) | CNAME → wallscourtfarm.github.io |

All CNAMEs: Proxy = **DNS only (grey cloud)** in Cloudflare — GitHub handles HTTPS.

---

## Phased plan

### Phase 1 — Games subdomain (quickest win)
**Innes does (Cloudflare):**
> DNS → Add record → Type: CNAME · Name: games · Target: wallscourtfarm.github.io · Proxy: DNS only → Save

**Innes does (GitHub):**
> wallscourtfarm/learning-games → Settings → Pages → Custom domain: games.wallscourt-farm-academy.co.uk → Save → Enforce HTTPS

**Claude does:**
- Archive `learner-activities` repo (set to archived in GitHub API)
- Archive `wfa` repo
- Update `learning-games` index.html — title and any internal links

### Phase 2 — Staff subdomain + repo consolidation
**Innes does (Cloudflare):**
> DNS → Add record → Type: CNAME · Name: staff · Target: wallscourtfarm.github.io · Proxy: DNS only → Save

**Innes does (GitHub):**
> wallscourtfarm/staff-tools → Settings → Pages → Custom domain: staff.wallscourt-farm-academy.co.uk → Save

**Claude does:**
- Move all content from `staff-learning-tools` into `staff-tools` (morning displays under `morning/`, GPS/SATS under existing paths)
- Update menu.json commit path in wfa-app (currently commits to `staff-learning-tools`, must update to `staff-tools`)
- Update all internal links in HTML files
- Update `staff-tools` landing page index.html to include morning displays section
- Archive `staff-learning-tools`

### Phase 3 — Shared assets (`wfa-shared` web layer)
**Claude does:**
- Add `web/` directory to `wallscourtfarm/wfa-shared`
- `web/wfa_logo.webp` — single canonical logo (use 5ca7fa8e version — same as wfa-app static)
- `web/wfa.css` — CSS variables (`--wfa-blue`, `--y1` through `--y6`), Nunito font import, base card/header styles
- Served via jsDelivr: `https://cdn.jsdelivr.net/gh/wallscourtfarm/wfa-shared@main/web/`
- Then sweep all HTML tools in staff-tools + learning-games to reference shared CSS and logo URL

### Phase 4 — Flask landing page
**Claude does:**
- `/` route in wfa-app: if not authenticated → public landing page (three sections: staff tools, learner games, login)
- If authenticated → existing dashboard (no change)
- Landing page links: staff.wallscourt-farm-academy.co.uk, games.wallscourt-farm-academy.co.uk, in-app tools

### Phase 5 — Streamlit → Flask migrations (staff tools)
Priority order:
1. Menu Publisher (simple, high staff impact — reads PDF, calls Claude, commits JSON)
2. Handwriting Tool (Claude skill already exists — handwriting-sheet skill in /mnt/skills/user/)
3. Word Puzzles (self-contained PDF generator)
4. SATs Reasoning (Claude API call + question bank)

Each becomes a route in wfa-app behind the existing Flask auth.

---

## Shared assets audit findings

**Logo versions found (inconsistent):**
- `logo.png` SHA 59cf6ef1 — staff-tools (×6), learning-games, staff-learning-tools (all consistent ✓)
- `wfa_logo.webp` SHA 5ca7fa8e — wfa-app, spelling-shed-app, reading-app (consistent ✓)
- `wfa_logo.webp` SHA 8a872373 — staff-learning-tools root (DIFFERENT version)
- `wfa_logo.jpg` SHA 5c5b620b — staff-learning-tools, handwriting-tool, reading-app (consistent ✓)
- `wfa_logo.png` SHA 3c47c0e8 — word-puzzles (yet another version)
- `wfa_logo.png` SHA 4f9ed732 — wfa-reports (another version)

Canonical version to use: `wfa_logo.webp` SHA 5ca7fa8e (already in wfa-app static, smallest and most consistent)

**`wfa-shared` Python package already has:** brand colours, logo_html(), Streamlit CSS — used by all Streamlit apps. Do not duplicate this; extend it with the `web/` layer.

**Colours hardcoded in HTML:** `#1798d3` embedded in every HTML tool's `<style>` block. Target: replace with `var(--wfa-blue)` from shared CSS after Phase 3.

**Fonts:** every HTML tool loads Nunito from Google Fonts independently. Consolidate into shared CSS `@import`.

**`clf_vocabulary.json`** in `word-puzzles` only — may be useful to other tools. Note for Phase 5 (word puzzles migration into Flask).

---

## Specific user requirements

> "I prefer staff.wallscourt-farm-academy.co.uk" (not tools.)

> "there are three main sections of whatever the top of the site becomes — 1) my own tools — I use them (not available or visible to others); 2) tools used by teachers; 3) things learners can access"

> "I own the domain (via cloudflare), you will need to give me instructions for anything I need to do"

> "Some may be for me only, others are for the whole school to use — I'll want to keep those 'separate' even if still all under the https://wallscourt-farm-academy.co.uk/ domain"

---

## Open questions / blockers

- Innes needs to confirm the Streamlit URLs for each app before we can update links (some known: menu-publisher-new.streamlit.app, spelling-shed-app-create.streamlit.app, wfa-handwriting-tool.streamlit.app, word-puzzles.streamlit.app, reading-generator.streamlit.app — confirm all are correct)
- Menu Publisher reads from a PDF upload and calls Claude API — confirm `ANTHROPIC_API_KEY` is set in Render environment before building Flask version
- `staff-learning-tools/sats-reasoning/app.py` uses Anthropic — check which model and whether it needs updating when ported to Flask
- Decision needed: should the public landing page require any auth at all, or fully open? (recommendation: fully open, login button leads to Flask app)
- `precision-teaching` tool in staff-tools has its own `data/pupils.json` and `data/skill-ladders.json` — check if these are live data or demo data before any repo moves

## Immediate next step

Start Phase 1. Ask Innes to:
1. Add the `games` CNAME in Cloudflare (instructions above)
2. Set custom domain on `wallscourtfarm/learning-games` repo in GitHub Pages

While Innes does that, Claude archives `learner-activities` and `wfa` repos via GitHub API and updates the `learning-games` index.html for the new domain. Then move to Phase 2.
