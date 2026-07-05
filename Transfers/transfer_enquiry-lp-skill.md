# Transfer: Enquiry LP skill build

**Generated:** 2026-07-05
**Originating focus:** Building a new consolidated skill for creating enquiry-based learning papers (LPs) covering history, geography, science and other subjects — incorporating Higgsfield image generation and the WFA learning label format.
**Skill in use:** none yet — this is the session that creates the skill

---

## Status

The geography enquiry "Are England and Brazil different?" has just been completed (L1–L6, all files delivered). During that build, six geography LPs were produced as ReportLab PDFs. Two iterations of those LPs had significant layout bugs (blue block header, overlapping checklist). The third iteration was structurally correct but server-side rendering was unreliable — Innes confirmed they display correctly in a real viewer.

The immediate task for the new session is: **design and write a comprehensive enquiry LP skill** that handles geography, history, science and other enquiry subjects, with Higgsfield image integration for LP header images, and correct WFA learning label format locked in from the start.

## What's been produced (reference — this session)

- `/mnt/user-data/outputs/T6W4_L456_Geographers_Complete.zip` — final delivery zip (53MB), all six LPs inside
- `/home/claude/build_l456_lps_v2.py` — the corrected LP builder for geography enquiry (good reference — has working learning_label() function, correct ReportLab coordinate logic, working table/word bank/writing line helpers)
- `/mnt/skills/user/geography-enquiry/SKILL.md` — geography deck build skill (NOT the LP skill — separate thing)
- `/mnt/skills/user/reportlab-pdf-creation/SKILL.md` — existing ReportLab rules skill (MUST be read at start of any LP build)

## Decisions locked in

**WFA learning label format (white background, no coloured block):**
```
Key Question                                [date right-aligned]
Are England and Brazil different?
──────────────────────────────────────────────────────────── (thin blue line)
LF: to describe and compare... (blue bold)
• I can describe... (dark, 8pt)
• I can identify... (dark, 8pt)
──────────────────────────────────────────────────────────── (thicker blue line)
[content starts here]
```
All text on white. No filled rectangles in the header. Blue is `#1798d3`.

**Correct ReportLab coordinates (bottom-left origin, y increases upward):**
- `drawString(x, y, text)` — baseline at y, text ascends upward
- `rect(x, y_bottom, w, h)` — bottom-left corner at (x, y_bottom)
- The working `learning_label()` function in `build_l456_lps_v2.py` has correct coordinate logic — use it verbatim as the starting point

**Task type substitution rules for adaptation (established in this session):**
- Open comparison writing → cloze sentences
- Fill-in table → labelling/which-country? exercise with answer boxes
- Challenge box → remove entirely (not replaced)
- Explanation paragraph → tick-box observation frame
- Standard word bank (9+ words) → shorter word bank (5–7 most important words only)

**PDF format for geography/history/science LPs** — ReportLab PDF (not PPTX). PPTX only for maths LPs which use the separate maths LP builder.

**Higgsfield images on LPs:**
- Model: `nano_banana_pro`, aspect ratio `16:9`
- Only for subject LPs where a visual genuinely helps engagement (geography, history, science — not maths, not writing)
- Placed below the learning label and above Part A — full content width, height ~1.6"
- Use narrative prompt style (full sentence describing scene, setting, lighting), not keyword list
- Download via `curl` after `job_display`, then embed via `ImageReader` in ReportLab
- The L6 before/after image slides in the lesson deck used this pattern successfully

**Zip-only delivery** — never present individual files alongside the zip.

## What needs to be built in the new session

The new skill file `/mnt/skills/user/enquiry-lp/SKILL.md` should encode:

1. **Learning label function** — copy and document the correct version from `build_l456_lps_v2.py`. This is the single biggest source of past bugs.

2. **Task type taxonomy by lesson stage:**
   - Early lesson (vocabulary/prior knowledge): short table + explanation frame
   - Mid-enquiry (application/comparison): labelling exercise or comparison table + sentence starters
   - Assessment lesson: extended writing frame + vocabulary checklist (no answer boxes needed)

3. **Task type taxonomy by subject:**
   - Geography: comparison tables, map labelling, land use recording, description frames
   - History: evidence analysis (what/who/when/why), timeline ordering, significance ranking, source evaluation frame
   - Science: predict/observe/explain table, classification table, results recording grid, explanation frame
   - Other subjects (art, DT, citizenship): note-taking frame, evaluation frame, response to stimulus

4. **Adaptation rules (standard → adapted):** the four substitution rules above, encoded explicitly.

5. **LP-to-deck alignment rule:** always read the deck's You Do slide content before writing the LP's Part B. They must match exactly — same task, same stimulus, same vocabulary.

6. **Enquiry stage awareness rule:** lesson number within the sequence affects LP structure (introduction vs application vs assessment).

7. **Higgsfield image decision rule:** when to generate (places/environments/habitats pupils haven't seen) and when not to (skills-based lessons, diagrams needed instead). From the image integration document already in this project.

8. **Marking station rules:** Part A answers mirror Part A exactly (same order, same item labels). Part B has a model answer, not just points. Both on page 2 of the PDF.

9. **Standard helpers to include verbatim:** `learning_label()`, `section_head()`, `body()`, `body_bold()`, `writing_line()`, `word_bank()`, `table_header()`, `table_row()`, `ans_box()`, `marking_header()`, `answer_row()` — all debugged versions from `build_l456_lps_v2.py`.

10. **Rendering verification rule:** use PyMuPDF (`fitz`) for QA renders, not pdftoppm or LibreOffice Draw. Those two fail to render standard PDF fonts (Helvetica) in this environment. PyMuPDF renders correctly. Install: `pip install pymupdf --break-system-packages`.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/home/claude/build_l456_lps_v2.py` | Working LP builder — key reference | **Yes — will not persist. Innes should upload at session start, or fetch from repo.** |
| `/mnt/skills/user/reportlab-pdf-creation/SKILL.md` | Existing — must be read first | No (lives in skill folder) |
| `/mnt/skills/user/geography-enquiry/SKILL.md` | Existing — reference for geography deck builds | No (lives in skill folder) |
| `/mnt/project/wfa-reportlab-rules.md` | Existing in project | No |

**Best approach:** at session start, ask Innes to confirm `build_l456_lps_v2.py` is accessible (fetch from GitHub repo `imcl75/claude_files` via github-sync skill if not present locally).

## Specific user requirements

> "There needs to be an all encompassing skill for creating enquiry based LPs (covering history, geography, science and other states of being)."

> "[The skill needs to include] the use of the higgsfield mcp to generate images for the LPs."

> "Use the CLF curriculum progression document to help guide you on prior learning and any cross curricular links which can be made."

> "Be consistent but make sure you are not duplicating content from previous weeks."

The CLF curriculum progression document is in the project at `/mnt/project/CLF_Curriculum_Progression_Summary_v3_3.pdf` — search it at the start of any build to check prior learning and cross-curricular links before designing LP tasks.

## Open questions / blockers

- The skill should cover "other states of being" — need to confirm with Innes what subjects these are in practice. Likely: Art (I am an Artist), DT (I am a Designer), Music (I am a Musician), Computing (I am a Digitally Literate Citizen), Citizenship (I am a Rights Holder). Ask at session start.
- Should adapted LP always be produced automatically alongside standard, or only when requested? Innes has always asked for both so far — probably default to both.
- Should the skill encode LP format for multiple year groups (Y5 Hazel from September) or stay Y4-only for now?

## Immediate next step

1. Read `/mnt/skills/user/reportlab-pdf-creation/SKILL.md` first.
2. Fetch `build_l456_lps_v2.py` from GitHub if not present locally.
3. Confirm with Innes: which "other states of being" subjects need LP support, and whether adapted LP should be automatic or on request.
4. Then design the skill structure (show Innes the proposed task type taxonomy for each subject before writing any code).
5. Write the skill to `/mnt/skills/user/enquiry-lp/SKILL.md` and push to repo.
