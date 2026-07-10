# Transfer: States of Matter enquiry — post-build revision

**Generated:** 2026-07-10
**Originating focus:** Building 5-lesson Being a Scientist enquiry deck (T6W7, Mon 13–Fri 17 July) — first build complete, revision required based on Innes feedback.
**Skill in use:** enquiry-lesson-builder

---

## Status

First full build of all 5 lesson PPTXs is complete and delivered as `T6W7_States_of_Matter_Lessons.zip`. Innes opened the slides and identified issues — detailed feedback coming tomorrow. The confirmed problem category is **wrong assets placed on slides** — shapes or images from the template source slides are showing up incorrectly (wrong badge, wrong placeholder content, wrong shape used). This is described as a recurring basic error.

---

## What's been produced

- `T6W7_States_of_Matter_Lessons.zip` — delivered, under revision
  - `Teaching/T6W7 - 1 - Mon - States of Matter L1.pptx` (8 slides)
  - `Teaching/T6W7 - 2 - Tue - States of Matter L2.pptx` (9 slides)
  - `Teaching/T6W7 - 3 - Wed - States of Matter L3.pptx` (8 slides)
  - `Teaching/T6W7 - 4 - Thu - States of Matter L4.pptx` (7 slides)
  - `Teaching/T6W7 - 5 - Fri - States of Matter L5.pptx` (8 slides)
  - `Images/L1/` through `Images/L5/` — 25 image files (Higgsfield downloads + Python diagrams)
- `EnquiryBuilder/states_of_matter_mtp.json` — full MTP with all image paths populated, in GitHub

---

## Decisions locked in

- Key question: `Can materials change their state?`
- No challenge / no written outcome — knowledge and skills focus only
- 5 lessons: Mon 13 – Fri 17 July
- Chemistry strand; disciplinary focus: observe_and_measure, record_and_present, conclude
- Images organised in `Images/L1/` – `Images/L5/` subfolders in the zip (Innes requested this explicitly)
- Diagrams (particle model, heating, reversible changes, water cycle, thermometer) generated via Python/matplotlib — NOT dall-e — because the Filesystem MCP bridge timed out during this session, preventing dall-e images from being transferred to the container. Python diagrams are embedded and working.
- All 12 Higgsfield images downloaded from CDN and embedded. Job IDs and CDN URLs are in this session's history if regeneration is needed.
- `kq_lo_science_clean.pptx` is NOT in GitHub — regenerate at session start from `KQ_LO.pptx` using the setup script in the previous transfer file (or re-run the inline script).
- Template PPTXs ARE now in GitHub under `EnquiryBuilder/templates/` — fetch from there, no re-upload needed.

---

## Known issues (Innes feedback — detail to follow tomorrow)

**Confirmed category:** Wrong assets placed on slides — shapes or images from template source files are appearing incorrectly. This is described as a basic recurring error.

**Known specific issues identified during build (before Innes feedback):**

1. **Misconception slides** — `edit_misconception()` in `build_science_lesson.py` uses `learners[idx]['statement']` as the key but the MTP JSON uses `'view'`. This was patched in this session with `.get('view', .get('statement'))` but the patch is only in `/home/claude/enquiry-builder/build_science_lesson.py` — not pushed to GitHub. The misconception slide rendered with correct text in QA but confirm this is still correct.

2. **L2 misconception slide** — the central image placeholder (`Rectangle 1` shape) renders as a blank white box. This is because `edit_misconception()` writes `[{prompt[:80]}]` as text into that shape but no image is embedded there. This may be one of the "wrong asset" issues Innes is referring to.

3. **Slide 8 / sci_template** — the builder permanently excludes `sci_template slide 8` (vertical WWH format). Confirmed still excluded.

4. **Badge images** — only `badge_ido.png` was extractable from `sci_example.pptx` assets. `badge_wedo.png` and `badge_youdo_ind.png` were not found (those slides have 0 embedded pictures — the badges may be in the slide layout XML, not in the slide media). `add_badge()` silently skips if file missing, so layout slides show no badge. This may be another visible issue.

5. **Cover slide** — TextBox 17 (challenge) is cleared when `challenge` is null. Innes can confirm whether this looks correct or whether the empty box is visible and unwanted.

6. **Recall slide** — shape names `Text Placeholder 5` and `Text Placeholder 12` assumed correct from transfer file. Not re-verified by examining actual slide XML in this session.

**The core problem:** The builder uses shape names from the template files as documented in the transfer brief. These names need to be re-verified by actually unpacking the PPTX and listing all shape names and their positions. Previous sessions have had recurring drift between documented shape names and actual shape names. Before revising, the next session should run a shape-name audit on every source template slide used.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `EnquiryBuilder/build_science_lesson.py` | in GitHub, patched in-session (learner key fix, null-challenge fix) — push to GitHub | No (fetch from repo, but note the in-session patches need pushing) |
| `EnquiryBuilder/slide_layouts.py` | in GitHub, unchanged | No |
| `EnquiryBuilder/generate_mtp.py` | in GitHub, unchanged | No |
| `EnquiryBuilder/clean.py` | in GitHub, unchanged | No |
| `EnquiryBuilder/SKILL.md` | in GitHub | No |
| `EnquiryBuilder/templates/Being_a_Scientist_slide_deck.pptx` | in GitHub | No |
| `EnquiryBuilder/templates/science-example.pptx` | in GitHub | No |
| `EnquiryBuilder/templates/KQ_LO.pptx` | in GitHub | No |
| `EnquiryBuilder/states_of_matter_mtp.json` | in GitHub | No |
| `kq_lo_science_clean.pptx` | NOT in GitHub (binary, regenerate at session start) | Regenerate from KQ_LO.pptx using setup script |
| `Images/L1/` – `Images/L5/` | 25 files on disk this session, NOT in GitHub | Higgsfield images must be re-downloaded (URLs in session history); Python diagrams must be regenerated |

---

## Session start setup (next session)

```bash
# 1. Fetch scripts from GitHub (EnquiryBuilder/)
# 2. Fetch templates from GitHub (EnquiryBuilder/templates/)
# 3. Regenerate kq_lo_science_clean.pptx from KQ_LO.pptx (inline script — same as previous sessions)
# 4. Regenerate Python diagrams (particle model, heating, reversible changes, water cycle, thermometer)
# 5. Re-download Higgsfield images using job_display → CDN URL → curl
#    (Job IDs from THIS session — available in session history only while this chat is open)
#    OR regenerate fresh Higgsfield images if session expired
# 6. Run shape-name audit on ALL source template slides before touching the builder
```

---

## CRITICAL — shape-name audit needed before any revision

Before rewriting any text or placing any asset, the next session MUST:

1. Unpack each source PPTX and print every shape name + position on every source slide used by the builder:
   - `sci_template.pptx`: slides 2 (cover), 9 (recall), 12 (misconception4), 13 (fed_in_facts), 14 (quiz)
   - `sci_example.pptx`: slides 12 (youdo), 13 (ido), 15 (wedo), 16 (misconception3), 17 (learning_review)
   - `kq_lo_science_clean.pptx`: slide 1 (lo)

2. Cross-reference against the shape names hard-coded in `build_science_lesson.py` (`edit_cover`, `edit_lo`, `edit_recall`, `edit_misconception`, `edit_learning_review`).

3. Fix any mismatches before doing any build.

This audit is the prerequisite for the revision. Do not skip it.

---

## Open questions / blockers

- Innes's full detailed feedback not yet received — expected tomorrow
- Higgsfield CDN URLs from this session will expire. Either save them from session history NOW or plan to regenerate.
- Python diagram quality: Innes has not yet commented on the matplotlib-generated diagrams. These may also be in the issues list.
- Badge images for wedo and youdo: need to find where these actually live in the template (likely slide layout XML, not slide media).

---

## Immediate next step

Wait for Innes's detailed feedback. At session start: fetch all scripts and templates from GitHub, run the shape-name audit on all source slides, then address Innes's specific list of issues one by one — do not start rebuilding until the full audit is done and the issue list is in hand.
