# Transfer: History — Roman Civilisation next session

**Generated:** 2026-07-21  
**For:** Next session picking up History enquiry work  
**Status doc:** Read `claude/enquiry-builder-pipeline-status.md` from project first — it is the authoritative running record. This transfer fills in the human context that doc doesn't capture.

---

## What's solid — do not touch these

The History builder (`History/build_history_lesson.py`) is working. All 14 Roman Civilisation PPTXs built clean on 2026-07-21. Do not refactor, "tidy", or re-derive anything in it.

The Roman Civilisation MTP (`EnquiryBuilder/mtp_roman_civilisation_final.json`) has:
- 14 lessons, `term_week_start: "T2W3"`
- L01–L02: `lp_note` (KWL intro lessons — no LP paper, but still need LL)
- L03–L14: fully structured three-level `lp` objects (standard / adapted / further_adapted, each with `elements[]`)
- NO concept_cartoon slides in any lesson (checked 2026-07-21)
- `day_label` fields are **placeholders** ("Day 1"..."Day 14") — NOT real timetable labels yet

---

## First thing — ask Innes before doing anything else

**Ask exactly this:**

> "What days of the week do History lessons fall? Give me the repeating schedule, e.g. `Tue, Thu` or `Mon, Tue, Tue, Thu`. The sequence resets each week — I'll use that to compute T2W3_1Tue, T2W3_2Thu etc. for all 14 lessons."

Once you have the answer, compute `day_label` for every lesson:
- Start from `term_week_start: "T2W3"`
- Sequence number resets to 1 at the start of each new week
- Format: `T2W3_1Tue`, `T2W3_2Thu`, `T2W4_1Tue`, etc.
- Update `day_label` in every lesson in `mtp_roman_civilisation_final.json`
- Push the updated MTP to repo

This unlocks correct output filenames for all builds.

---

## What to build this session (in order)

### 1. Update day_labels in the MTP (after asking Innes — see above)

Edit `EnquiryBuilder/mtp_roman_civilisation_final.json`. Replace every `"day_label": "Day N"` with the correct computed label. Push to repo.

### 2. Fix `build_ko_pdf.py` — two bugs (no input from Innes needed)

File: `EnquiryBuilder/build_ko_pdf.py`

**Bug 1** — line 56–58: `ICON_DIR` is hardcoded to `/Users/innes/Desktop/...`. In cloud it raises `FileNotFoundError` immediately. Fix:
```python
_ICON_DIR_CANDIDATES = [
    '/Users/innes/Desktop/Claude Assets/States of Being Icons/enquiry-reading-maths-writer-images',
    '/tmp/ko_icons',
]
ICON_DIR = next((p for p in _ICON_DIR_CANDIDATES if os.path.isdir(p)), None)
```
Then in `main()`, wrap the icon load in a try/except that draws a filled colour rectangle if `ICON_DIR` is None or the file doesn't exist.

**Bug 2** — line 350: `main()` is called bare at module level. Wrap it:
```python
if __name__ == '__main__':
    main()
```

After fixing, build the Roman Civilisation KO:
```bash
python EnquiryBuilder/build_ko_pdf.py \
  EnquiryBuilder/mtp_roman_civilisation_final.json \
  --out KO/KO_Roman_Civilisation_Y5.pdf
```

### 3. Build LP sheets for L03–L14 (12 lessons)

The structured LP data is already in the MTP. Run `build_lp_all_levels()` from `EnquiryBuilder/build_lp.py` for each lesson where `lp` is a dict (not `lp_note`). That's L03–L14.

Output naming:
```
LPs/T2W3_1Tue_L03_LP_Standard_Roman_Society.pptx   (example — use real day_label)
LPs/T2W3_1Tue_L03_LP_Adapted_Roman_Society.pptx
LPs/T2W3_1Tue_L03_LP_Further_Adapted_Roman_Society.pptx
```

Cohort data is in `EnquiryBuilder/class_lp_groups.json` — Y5 2026-27: 5IM (30 children, 6 adapted, 0 further_adapted), 5LS (30, 1 adapted, 3 further_adapted).

### 4. Build LL sticker sheets for ALL 14 lessons

Every lesson — including L01 and L02 — needs a 12-per-page learning label sheet.

The Maths pipeline has `Maths/generate_labels.py` which uses `WFA_Labels_template.docx` (a DOCX template with five text placeholders). The History LL needs the same approach. The fields are: date, topic/lesson title, WALT (what), two success criteria.

Steps:
1. Check whether an LL DOCX template for History already exists (look for `WFA_Labels_template.docx` or similar in the repo — the Maths one is at `Maths/WFA_Labels_template.docx`)
2. If not, ask Innes — she may have a History LL template, or the Maths one may be adaptable (same layout, different label content)
3. Build a simple generator that reads the MTP and outputs one DOCX per lesson

Output naming:
```
LLs/T2W3_1Tue_L01_LL_Who_were_the_Romans.docx
LLs/T2W3_2Thu_L02_LL_The_Empire_Grows.docx
...
```

### 5. Re-build teaching PPTXs with corrected day_labels

Once day_labels are updated in the MTP, re-run the builder for all 14 lessons to get correctly named output files. The PPTXs themselves built fine before — this is just renaming via a clean rebuild.

```bash
cd /home/claude/_repo/History
python restore_history_assets.py   # ALWAYS run this first in any cloud History session
python build_history_lesson.py \
  ../EnquiryBuilder/mtp_roman_civilisation_final.json \
  --base-pptx ../EnquiryBuilder/templates/history-example.pptx \
  --out-dir ../Enquiry_Roman_Civilisation_Y5_T2W3/Teaching/
```

---

## Setup — run this at the start of every cloud History session

```bash
cd /home/claude/_repo/History
python restore_history_assets.py
```

This copies History assets from the repo into `/home/claude/assets/`. Without it, the builder fails on missing PNGs.

---

## What NOT to do (critical — these caused repeated disasters in previous sessions)

### OOXML rules — treat these as immutable law

These are fully documented in `claude/geography-builder-postmortem.md` in the project. Before touching any PPTX builder:
1. **No `grpId` attribute** on any `<p:cTn>` element. Ever.
2. **No `<p:bldLst>` block** after `<p:timing>`. Ever.
3. **`spcBef`/`spcAft` are child elements** of `<a:pPr>`, never attributes.
4. **`<a:picLocks/>`** — bare, no attributes, unless specifically locking something.
5. **Never use `noChangeAspect="0"`** — it triggers PPT repair.

If any of these rules are in the current code and working, do not "clean them up". If they are absent, do not add them. Leave working animation XML alone.

### Text box coordinates — do not recalculate

If you see hardcoded coordinates in a builder and they're working, do NOT replace them with a formula you've derived. The coordinates were confirmed by Innes against real files. A new calculation is a regression waiting to happen.

### Do not refactor working builders

The History, Geography and Science builders all produce clean files. Do not reorganise them, rename functions, or "simplify" logic. Make the smallest targeted change needed.

### Do not use `lp_task` (deprecated field)

The Roman MTP's LP content is in structured `lp` objects (L03–L14). The old plain-text `lp_task` field is gone. Do not re-add it.

---

## Files — where things live

```
EnquiryBuilder/
  build_lp.py                    ← LP builder (solid — use build_lp_all_levels())
  build_ko_pdf.py                ← KO builder (has icon path + bare main() bugs — fix first)
  build_resources.py             ← Supporting resources (solid, not needed this session)
  mtp_roman_civilisation_final.json  ← THE MTP — day_labels need updating
  class_lp_groups.json           ← Cohort data (Y5 2026-27, current)
  templates/history-example.pptx ← Base PPTX for history builder

History/
  build_history_lesson.py        ← Solid — do not touch without a specific task
  history_registry.py            ← Asset paths
  restore_history_assets.py      ← Run this first in every History cloud session

Maths/
  generate_labels.py             ← LL generator (Maths-specific — adapt for History)
  WFA_Labels_template.docx       ← DOCX label template (may be reusable for History)

claude/                          ← Project docs
  enquiry-builder-pipeline-status.md   ← Status — update when tasks complete
  geography-builder-postmortem.md      ← OOXML rules — read this if touching any builder
```

---

## Questions to ask Innes (in order)

1. **Timetable** (before doing anything else): "What days do History lessons fall each week?"
2. **LL template**: "Do you have a History learning label DOCX template, or should I adapt the Maths one?" (Show her what the Maths one looks like first)
3. **LP review**: Once L03 LP is built, show her the Standard version and ask "Does the layout and content look right before I build the other 13?"
4. **KO content**: When building the KO, confirm the key image to use on the cover (there's no image path in the MTP currently — ask for one or build without)

---

## Update the status doc when done

Update `claude/enquiry-builder-pipeline-status.md` after each completed task. Tick off:
- `[ ]` KO builder icon path fix  
- `[ ]` KO builder bare main() fix  
- `[ ]` Roman MTP day_labels updated  
- `[ ]` Roman KO built  
- `[ ]` LP sheets L03–L14 built  
- `[ ]` LL sheets all 14 lessons built  
- `[ ]` Teaching PPTXs rebuilt with correct naming  

---

## What this session is NOT about

- Science or Geography — leave them alone
- Writing lesson builder — separate pipeline, separate session
- Y5 Astronomy — not in scope today
- Adding new lessons to the Roman MTP — the 14-lesson set is complete

Stay on Roman Civilisation History deliverables only.
