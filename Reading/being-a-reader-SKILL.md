---
name: being-a-reader
description: "Create a full week of Being a Reader reading comprehension resources for Y3, Y4, Y5, or Y6. Use this skill whenever Innes asks for reading lessons, Being a Reader lessons, reading comprehension resources, vocabulary/retrieval/inference lessons, or says things like 'make this week's reading', 'create the reading for next week', 'Being a Reader for [text]', 'reading lessons linked to [book]'. Also trigger when he uploads content and mentions reading questions, comprehension questions, or refers to the three-lesson reading cycle. Final output is a single zip per week containing: PPTX + answers PDF at root, one folder per lesson day each holding two class PDFs. Always confirm adapted pupil profiles and class lists at session start. Always ask year group at session start."
---

# Being a Reader Skill

## Overview

Being a Reader is Innes's weekly reading comprehension system. Each week produces a **single zip file** delivered via `present_files`. Structure:

```
{TxWy} - Being a Reader.zip
└── {TxWy}/                            ← outer folder always named week_ref
    ├── {TxWy} - ReaderTeaching.pptx
    ├── {TxWy} - ReaderAnswers.pdf
    ├── 1-{Day1}/                      ← numbered in day-of-week order
    │   ├── LMES.pdf
    │   └── IM.pdf
    ├── 2-{Day2}/
    │   ├── LMES.pdf
    │   └── IM.pdf
    └── 3-{Day3}/
        ├── LMES.pdf
        └── IM.pdf
```

- Day folders are numbered 1, 2, 3 in calendar order (earliest day in the week = 1).
- Class PDFs are named `LMES.pdf` / `IM.pdf` only — no week_ref or day prefix in the filename.
- When shared text mode is on, each day folder also contains a `TextSheet/` subfolder with `LMES.pdf` and `IM.pdf` text-only sheets.
- The answers PDF is at `{TxWy}/{TxWy} - ReaderAnswers.pdf`.

Order of lessons is always **Vocabulary → Retrieval → Inference**.

---

## Step 0: Session Setup

At the start of every Being a Reader session, clone (or update) the web tool repo so all build scripts are available:

```python
import subprocess, os, shutil, zipfile

REPO = '/home/claude/being-a-reader-web'
if not os.path.exists(REPO):
    subprocess.run(
        ['git', 'clone', 'https://github.com/wallscourtfarm/being-a-reader-web', REPO],
        check=True
    )
else:
    subprocess.run(['git', '-C', REPO, 'pull'], check=True)

print("Repo ready at", REPO)
```

The following files are now available and match the web tool exactly:
- `/home/claude/being-a-reader-web/pdf_builder.py` — PDF generation (ReportLab)
- `/home/claude/being-a-reader-web/pptx_builder.py` — PPTX generation (XML surgery)
- `/home/claude/being-a-reader-web/content_generator.py` — content spec (passed to AI)
- `/home/claude/being-a-reader-web/pupil_data.py` — class lists and adapted pupil profiles
- `/home/claude/being-a-reader-web/BeingAReader_Template.pptx` — PPTX template
- `/home/claude/being-a-reader-web/fluency_slide_base.pptx` — proven v16 fluency slide base
- `/home/claude/being-a-reader-web/Fluency Rubric Focus.pptx` — rubric images and text
- `/home/claude/being-a-reader-web/fluency_icons/` — fluency activity icons

Extract the reader icon for PDF headers:

```python
template = os.path.join(REPO, 'BeingAReader_Template.pptx')
icon_dest = '/home/claude/reader_icon_saved.png'
if not os.path.exists(icon_dest):
    with zipfile.ZipFile(template) as z:
        with z.open('ppt/media/image2.png') as src, open(icon_dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)
    print("Icon extracted →", icon_dest)
```

---

## Step 1: Gather Required Inputs

Before generating anything, collect from Innes:

| Input | Example |
|-------|---------|
| Year group | Y3 / Y4 / Y5 / Y6 |
| Term (Y5 only) | T1–T6 — drives calibration from progression table |
| Text / book | I Want My Hat Back (Jon Klassen) |
| Key question | "How do writers use dialogue?" |
| Week reference | T5W2 |
| Day + date for each lesson | Voc=Tue 28/04, Ret=Thu 30/04, Inf=Fri 01/05 |
| Fluency focus | Expression & Volume / Phrasing / Smoothness / Pace |
| Fluency activity | e.g. Stress that word, Echo read, Hot seat read |
| Shared text mode | on / off — if on, collect the source text (up to 500 words) |

Generate all content (extracts, questions, answers, vocabulary) yourself unless Innes supplies an XLSX.

### Adapted Pupil Profiles — Session Start Protocol

At the start of every session, confirm stored profiles with a single yes/no prompt before asking any other inputs:

> *Adapted pupils on record: Adnan (Ph2), Callum (Ph2), Hope (3 years behind), Roland (2 years behind), Asimenia / Jimi / Reggie (current-adapted, LMES), Teddie (1 year behind), Asel / Bailey / Daisy (current-adapted, IM). Still correct?*

Only update profiles if Innes flags a change. Profiles update roughly 2–3 times per year.

**Current stored profiles — Y4 (2025-26):**

| Pupil | Level tag | Resolves Y4 | Resolves Y5 | Class |
|-------|-----------|-------------|-------------|-------|
| Adnan | `Ph2` | Ph2 | Ph2 | LMES |
| Callum | `Ph2` | Ph2 | Ph2 | LMES |
| Hope | `3-behind` | Y1 | Y2 | LMES |
| Roland | `2-behind` | Y2 | Y3 | LMES |
| Asimenia | `current-adapted` | Y4-adapted | Y5-adapted | LMES |
| Jimi | `current-adapted` | Y4-adapted | Y5-adapted | LMES |
| Reggie | `current-adapted` | Y4-adapted | Y5-adapted | LMES |
| Teddie | `1-behind` | Y3 | Y4-adapted | IM |
| Asel | `current-adapted` | Y4-adapted | Y5-adapted | IM |
| Bailey | `current-adapted` | Y4-adapted | Y5-adapted | IM |
| Daisy | `current-adapted` | Y4-adapted | Y5-adapted | IM |

**Standard class lists (2025-26) — Y4:**

LMES (23): Aaliyah, Cameron, Cruz, Delton, Dovind, Elliot, Eloho, Fola, Heidi, Isabelle, Isla, Jacob, Josh, Lilly, Lily H, Maisie, Mary, Meshach, Mia, Ralf, Ruby, Sebastian, Taylor

IM (26): Amir, Arthur, Bonnie, Carena, Ceecee, Cody, Connie, Diyan, Emilia, Freya, Haris, Iris, Izzy, Jesse, Lois, Louie, Maddie, Maximilian, Penny, Phoebe, Ramani, Rory, Sam, Sohan, Zeek, Ziyad

**Day document sort order (within each class):** Ph2 → Y1 → Y2 → Y3 → Y4-adapted → standard copies (one per standard pupil in that class, all identical, unnamed).

---

## Step 2: Content Generation Rules

### Text Extracts

- Write **one extract per lesson**, used on both PPTX slide and PDF worksheet
- **CRITICAL: The extract text must be byte-for-byte identical across PPTX slide, PPTX practice Q, and PDF worksheet**
- For narrative/book topics: write as **narrative literary prose** — a single flowing paragraph that reads like a well-written literary analysis. NOT non-fiction report style, NOT bullet points, NOT multiple separated paragraphs
- Standard extract: **Y4 = 200–250 words / Y5 = 250–300 words / Y6 = 280–320 words, single paragraph**
- Supported extract: **Y4-adapted = 200–220 words (close to standard length, slightly simplified vocabulary and sentence structure)**
- Embed lesson vocabulary words naturally in the standard extract

### Vocabulary (5 words per lesson, 15 total)

- **Y4:** Tier 2 words, accessible for age 8–9. Child-friendly definition: one clear sentence.
- **Y5:** Tier 2 words — complexity increases progressively through the year (see Y5 progression table below). Definition: one precise sentence.
- Focus word (Write it 5 times slide) = the most commonly encountered Tier 2 word
- Never repeat words across weeks on the same topic

### Questions

- Standard: 7 questions. Adapted (all levels): 5 questions max (fewer for Y1/Ph; see Adapted Version Spec). Genuinely adapted content — not just fewer questions from the same text.
- Questions progress Q1 (easiest) → Q7 (hardest)
- **Q7 is always first to drop** if the page doesn't fit on a single A4
- **Y4 calibration:** answerable in 1–3 sentences by an 8–9 year old; inference questions focus on unstated meaning from clues
- **Y5 calibration:** see progression table below — pupils enter Y5 as Y4 readers; complexity builds gradually across the year
- Use at least 4 different question formats per lesson, and vary the mix across all three lessons so no two lessons in the same week use the same dominant type

### Question type distribution — aim for this variety each week

**Vocabulary lesson** — focus on word meaning, context, and language choices:
Best types: `quote` (find the word), `tick_v` (which meaning fits), `fill` (complete with vocab word), `true_false` (does this definition fit), `mc`, `short`, `short2`, `written` (how does the word choice affect the reader)

**Retrieval lesson** — focus on locating specific detail and sequencing:
Best types: `short` (what/when/where/who), `evidence2` / `evidence3` (write two/three things), `order` (sequence events), `attrib_table` (who did what), `quote` (find and copy), `tick_v`, `short2`

**Inference lesson** — focus on deduction, author intent, and extended response:
Best types: `written` (extended reasoning), `evidence2_ext` (two detailed inferences), `select` (tick all emotions/effects), `tf_table` (valid inference or not), `short2` (what does X suggest), `quote` (find evidence that)

**Across-week variety rules — HARD CONSTRAINTS:**

1. **No type in all three lessons.** Before finalising, list the types used in each lesson. Any type appearing in Vocabulary AND Retrieval AND Inference must be replaced in at least one lesson. Exception: `written` at Q6–Q7 is permitted in all three.
2. **Each lesson must have a distinct dominant type.**
   - Vocabulary: owns `tick_v`, `fill`, `match` — do not use these in Retrieval or Inference
   - Retrieval: owns `quote`, `order`, `attrib_table` — do not use these in Vocabulary or Inference
   - Inference: owns `mc`, `select`, `tf_table` — do not use these in Vocabulary or Retrieval
3. **Shared pool** (usable in any lesson, but not all three): `short`, `short2`, `evidence2`, `evidence2_ext`, `evidence3`, `true_false`
4. **Q1 rule:** always an accessible closed format (`tick_v`, `mc`, `short`, `true_false`, `fill`) — never open-ended writing
5. **Q7 rule:** always the hardest — `written` extended response, `evidence2_ext`, or equivalent
6. **No more than 2 `written` questions per page** — use `short2` for mid-range responses
- Fluency target: **90 wpm** (texts become more challenging; rate stays constant)

### Question types

All question tuples: `(qnum, qtype, qtext, options_or_None, correct)`

| Type | options | correct | Notes |
|------|---------|---------|-------|
| `mc` | `["A","B","C","D"]` | `"B"` | 2×2 MC grid |
| `tick2` | `["A","B","C","D"]` | `"C"` | 4 options in a row, tick one |
| `tick3` | `["A","B","C","D","E","F"]` | `"E"` | 6 options, tick one |
| `written` | `None` | answer string | 3 writing lines (default) |
| `short` | `None` | answer string | 1 writing line — simple retrieval |
| `short2` | `None` | answer string | 2 writing lines |
| `quote` | `None` | phrase string | "Find and copy" — rounded grey box |
| `true_false` | `None` | `"True"` or `"False"` | Radio buttons |
| `select` | `["A","B","C","D","E"]` | `["B","D"]` | Tick ALL that apply — square checkboxes; correct is a **list** |
| `tick_v` | `["A","B","C","D"]` | `"C"` or `["B","D"]` | KS2-style vertical tick; "[Tick one.]" / "[Tick two.]" appended inline to question |
| `tf_table` | `["Stmt 1","Stmt 2","Stmt 3"]` | `["True","False","True"]` | KS2-style True/False multi-row table |
| `evidence2` | `None` | `["Answer 1","Answer 2"]` | KS2-style numbered 1./2. list, 1 line each |
| `evidence2_ext` | `None` | `["Answer 1","Answer 2"]` | Numbered 1./2. list, 2 lines each |
| `evidence3` | `None` | `["A1","A2","A3"]` | KS2-style numbered 1./2./3. list |
| `fill` | `None` | `"word1/word2"` | Inline fill-in-blank; use `______________` in qtext |
| `match` | `[("L1","R1"),...]` | — | Connecting circles |
| `attrib_table` | `[["James","Mandy"],"stmt1","stmt2",...]` | `["James","Mandy","James","Mandy"]` | KS2-style attribution table |
| `order` | `["step1","step2",...]` | `"2,1,3"` | KS2-style sequencing |

**Q7 is always first to drop** if space runs out.

### We Do Questions (PPTX Practice Q slide)

Two questions per lesson shown with answers on the PPTX Practice Questions slide.

**HARD RULE — We Do questions must NEVER appear in the LP question list.** Write the LP questions first, then write the We Do questions as simpler whole-class modelling versions of a similar skill.

### Y5 Progression Table (use TERM to select the right row)

| Term | Extract length (std) | Extract length (sup) | Vocabulary | Question demand |
|------|---------------------|---------------------|------------|-----------------|
| T1 | 220–245 words | 145–160 words | Tier 2, Y4-level; familiar register | Q1–Q5 as Y4; Q6–Q7 begin to ask for a reason or short justification |
| T2 | 235–260 words | 150–165 words | Tier 2, slightly less familiar words | Q6–Q7 require a full sentence with evidence |
| T3 | 250–275 words | 160–175 words | Tier 2; one word per lesson that stretches | Q4–Q7 expect 2 sentences; first inference question about author purpose |
| T4 | 265–290 words | 168–182 words | Tier 2 mix, higher register overall | Q5–Q7 need 2–3 sentences; inference includes effect on reader |
| T5 | 278–305 words | 175–190 words | Tier 2 with occasional Tier 3 for standard | Q6–Q7 require extended response; at least one question weighs two interpretations |
| T6 | 290–320 words | 180–200 words | Tier 2/3 mix for standard | Full Y5 demand — bias, purpose, ambiguity expected at Q5–Q7 |

---

## Adapted Version Spec

### Level Tags

| Tag | Reading level | Lesson structure | Text approach |
|-----|--------------|-----------------|---------------|
| `Y4-adapted` | Low Y4 | 3 lessons, each with single skill focus (Voc / Ret / Inf) — same as standard | Simpler text on same topic; same topic but lighter vocabulary and shorter sentences |
| `Y3` | Y3 level | 3 lessons, each blends all three skill types | Separate shorter text per lesson, same topic |
| `Y2` | Y2 level | 3 lessons, each blends all three skill types | Separate shorter text per lesson, same topic |
| `Y1` | Y1 level | 3 lessons, each blends all three skill types | Separate shorter text per lesson, same topic |
| `Ph2` | Phase 2 phonics | 3 lessons, each blends all three skill types | Very short simple text; adult support assumed |

### Text Length by Level

| Level | Words per text |
|-------|---------------|
| `Y4-adapted` | 200–220 words (one text per lesson, close to standard length but simpler vocabulary and shorter sentences) |
| `Y3` | 130–170 words (separate text per lesson) |
| `Y2` | 90–130 words (separate text per lesson) |
| `Y1` | 60–90 words (separate text per lesson) |
| `Ph2` | 30–50 words (separate text per lesson); very short sentences, simple vocabulary |

### Question Distribution by Level

| Skill type | `Y4-adapted` | `Y3` | `Y2` | `Y1` | `Ph2` |
|-----------|-------------|------|------|------|-------|
| Retrieval (closed/short) | Standard mix for the lesson type | Majority | Dominant | Dominant | Dominant |
| Vocabulary | Standard | 1–2 questions | 1–2 questions | 1 simple question | 1 simple question |
| Basic inference (tick/circle) | Standard | 2 questions | 1 question | 1 question | 1 question |
| Extended inference (written) | Standard | 1 short sentence | None | None | None |
| Glossary | Rarely | If needed | Usually | Always | Always |
| Total questions per lesson | 5 | 5 | 5 | 6 | 3 |
| Lines per written answer | 2 | 2 | 1–2 | 1 | None |

### Naming Convention

- The pupil's **first name** appears **right-aligned in the top-right corner** of the header row (same line as the date). No label such as 'supported', 'adapted' or 'lower ability' anywhere on the page.
- Layout otherwise identical to the standard paper.

### Output per Pupil

One PDF per named pupil containing their three lesson pages. File name:

```
{TxWy} - Reader_{FirstName}.pdf    e.g. T5W2 - Reader_Amara.pdf
```

Include answers for all adapted versions in the All Answers PDF, grouped by pupil after the standard answers.

---

## Step 3: Build the PDFs

Use `pdf_builder.py` from the cloned repo. Call `build_all_pdfs()`:

```python
import sys
sys.path.insert(0, '/home/claude/being-a-reader-web')
from pdf_builder import build_all_pdfs
import tempfile, os

out_dir = tempfile.mkdtemp()

pdf_files = build_all_pdfs(
    week_data=week_data,         # dict with Vocabulary/Retrieval/Inference lesson data
    year_group=year_group,
    key_q=key_question,
    week_ref=week_ref,
    output_dir=out_dir,
    shared_text_mode=is_shared_text_mode,
    shared_text=shared_text_val,  # None if not shared text mode
)
# pdf_files is a dict: {arc_name: file_path}
# e.g. {"Monday/LMES.pdf": "/tmp/abc/Monday_LMES.pdf"}
```

Each page **must fit on exactly one A4 page** — hard constraint.

### Page Dimensions

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
W, H = A4   # 595.28 x 841.89 points
MARGIN = 8 * mm
CW = W - 2 * MARGIN
```

### Colours

**Y4 (Maple — default):**
```python
BOX_BORDER = (0.173, 0.173, 0.424)   # #2c2c6c
BOX_BG     = (0.941, 0.941, 0.973)   # #f0f0f8
GREEN      = (0.102, 0.478, 0.102)   # #1a7a1a — answer text
DARK       = (0.133, 0.133, 0.133)   # body text
GREY_LINE  = (0.6, 0.6, 0.6)
```

**Y5 (Hazel — pale orange):**
```python
BOX_BORDER = (0.706, 0.392, 0.071)   # #b46312
BOX_BG     = (0.988, 0.949, 0.914)   # #fcf2e9
```

**Y3 (green scheme):**
```python
BOX_BORDER = (0.102, 0.451, 0.102)
BOX_BG     = (0.894, 0.969, 0.894)
```

**Y6 (dark red scheme):**
```python
BOX_BORDER = (0.502, 0.102, 0.102)
BOX_BG     = (0.969, 0.894, 0.894)
```

Colour selection is handled automatically by `pdf_builder.py`'s `get_colours(year_group)` function — no manual patching needed.

### Header Layout — EXACT (do not vary)

```
Key Question  [icon]  Day DD/MM/YYYY
```

All on one line, left to right. "Key Question" at left margin. Icon positioned after label text (dynamic width). Date immediately after icon. The date is **NOT right-aligned**.

Then below the header line (with thin divider):
- Key question: bold, underlined, in scheme colour
- LF: [learning focus] — plain 8pt
- I can [statement 1] — plain 8pt
- I can [statement 2] — plain 8pt
- Thin divider line

### Text Extract Box

Rounded-corner bordered box. Font: Helvetica 10.5pt. Single flowing paragraph.

### Question Rendering Rules — EXACT (do not vary)

**Question numbering: plain `1.` `2.` `3.` — NEVER `Q1.` `Q2.` etc.**

**Tick one / Tick two instruction — INLINE with question text:**
`[Tick one.]` or `[Tick two.]` is appended directly to the question text. Example: `1. Which word means 'contrast'? [Tick one.]`

**Answer lines: SOLID, not dashed**

Standard: 3 lines per written question. Adapted: 2 lines (Y4-adapted / Y3); 1 line (Y2); none or 1 (Y1); none at all (Ph2 — tick/circle only).

**Inter-question spacing:** ~3–4mm between question blocks.

**Tick box position:** Draw the tick box immediately after the option text (3mm gap), not right-aligned to the page edge.

---

## Step 4: Build the PPTX

Use `pptx_builder.py` from the cloned repo:

```python
from pptx_builder import build_pptx

pptx_path = os.path.join(out_dir, f'{week_ref} - ReaderTeaching.pptx')

build_pptx(
    week_data=week_data,
    week_ref=week_ref,
    output_path=pptx_path,
    fluency_focuses=fluency_focuses,      # {'Vocabulary': 'Expression & Volume', ...}
    fluency_activities=fluency_activities, # {'Vocabulary': 'Stress that word', ...}
)
```

### XML Encoding Rules

```python
def to_xml(text):
    return (text
        .replace('&', '&amp;')
        .replace('“', '&#x201C;')
        .replace('”', '&#x201D;')
        .replace('‘', '&#x2018;')
        .replace('’', '&#x2019;'))
```

**DANGER: Never use a generic `<a:off x=... y=...>` regex across a whole slide — it will hit shapes inside groups. Always find the enclosing `<p:sp>` by name first.**

### Slide Map (24 slides, 8 per lesson)

| Slides | Lesson | What to replace |
|--------|--------|-----------------|
| 2, 9, 16 | Title | Day name text |
| 3, 10, 17 | Why We Read | Nothing — leave as is |
| 4, 11, 18 | Vocab Focus (hidden defs) | 5 words + 5 definitions in table |
| 5, 12, 19 | Write it 5 times | Focus word (appears TWICE: table cell + spider diagram) |
| 6, 13, 20 | Independent Read (Fluency) | Full fluency slide — injected from v16 base (see below) |
| 7, 14, 21 | Learning Objective | Nothing — leave as is (fixed per lesson type) |
| 8, 15, 22 | Practice Questions | Q1, A1, Q2, A2 + extract text |

**Note: Slides 1, 8 etc. in earlier versions of this skill were offset by 1 — the correct numbers are those above, matching the actual template file.**

### Vocab Hidden Slides — CRITICAL Geometry

The blue ? bars must exactly cover each table row. These dimensions are fixed and must be identical across all three vocab slides (slides 4, 11, 18):

```python
TABLE_TOP  = 2173922   # EMU from top of slide
TABLE_LEFT = 647700
TABLE_W    = 10663199
ROW_H      = 685800
N_ROWS     = 5
TABLE_H    = ROW_H * N_ROWS   # 3429000

RECT_LEFT  = 2312410
RECT_W     = 8985789
# Rectangle top for row i: TABLE_TOP + i * ROW_H   (i = 0,1,2,3,4)
```

### Independent Read Slides — Fluency Injection

Slides 6, 13, 20 are **completely replaced** using a proven base slide (`fluency_slide_base.pptx`) rather than modifying the template's existing slide content. This is the only reliable approach — template XML surgery on these slides causes PowerPoint repair errors.

**How it works:**

1. Load `fluency_slide_base.pptx` — this is the proven v16 layout with correct Show/Hide animation timing, You Do image, button, and all fixed element positions.
2. For each lesson (Vocabulary/Retrieval/Inference), pull:
   - **You Do image** — from `fluency_slide_base.pptx` (always the same image, never changes)
   - **Activity icon** — from `fluency_icons/{icon_file}.png` based on the selected activity
   - **Rubric table image** — from the corresponding slide in `Fluency Rubric Focus.pptx` (identified as the largest image file on that slide)
   - **Rubric text** — the bullet-text `<p:sp>` from the rubric slide (matched by content length > 20 chars, name not containing "Title")
   - **Extract text** — from the already-patched template's practice-questions slide (slide 8/15/22)
3. Write the three images to the PPTX media directory with unique filenames.
4. Rewire rId references: `rId2`→You Do, `rId3`→activity icon, `rId4`→rubric image.
5. Replace the ActivityText shape (id=31) wholesale with fresh XML containing the activity name and description.
6. Replace the rubric textbox (id=6) wholesale with the rubric text from `Fluency Rubric Focus.pptx`.
7. Replace the ExtractBox (id=40) wholesale with the extract text.

**Fixed element positions (EMU) — never change these:**

```python
_ICON_X,  _ICON_Y,  _ICON_CX,  _ICON_CY  = 220421,  939485, 1656000, 1152000
_TEXT_X,  _TEXT_Y,  _TEXT_CX,  _TEXT_CY  = 1852421, 939485, 9092000, 1498915
_RUB_X,   _RUB_Y,   _RUB_CX,   _RUB_CY   = 144378, 2504555, 11030400, 1609200
_BGBOX_X, _BGBOX_Y, _BGBOX_CX, _BGBOX_CY = 144378, 4519360, 11880000, 1325198
_EXT_X,   _EXT_Y,   _EXT_CX,   _EXT_CY   = 30000,   784800, 12132000, 5508000
```

**Available fluency focuses:** Expression & Volume, Phrasing, Smoothness, Pace

**Available fluency activities:** per focus — see `FLUENCY_ACTIVITIES` dict in `pptx_builder.py`.

---

## Step 5: Permanent Slide Finishing Fixes — MANDATORY

`apply_finishing_fixes(slides_dir)` in `pptx_builder.py` applies nine deterministic, idempotent fixes. **Always runs as part of `build_pptx()` — no separate call needed.**

### The nine fixes

**Fix 1 — Slide 3 forced visible.** Ensures slide 3 (Why We Read, Vocabulary lesson) is visible.

**Fix 2 — Remove pen strokes.** Strips `<mc:AlternateContent>` ink annotation elements left by touch-screen editing.

**Fix 3 — Retrieval huge title.** The Title 1 shape on the Retrieval Read slide (slide 13) has a `sz="4400"` orphan `<a:r>` run that duplicates the fluency instruction at giant size. The fix deletes the orphan run.

**Fix 4 — Extract textbox font normalisation.** Forces every extract textbox on slides 6, 8, 13, 15, 20, 22 to `sz="2100"` and strips `<a:normAutofit>` shrinkage attributes.

**Fix 5 — Instruction box overlap.** Narrows the Title 1 box on slide 6 and repositions TextBox 5 on slides 13/20 to prevent instruction text overlapping the fluency element.

**Fix 6 — Spider focus word centring.** On slides 5, 12, 19, widens the focus-word textbox to 2.4M EMU, switches to `wrap="square"` with `anchor="ctr"`, adds `<a:pPr algn="ctr"/>`, and recentres it. Keeps the word centred on the spider intersection regardless of word length.

**Fix 7 — Oval anchor=ctr.** Forces `anchor="ctr"` on the bodyPr of any shape with `prst="ellipse"` or a name starting with `Oval` that contains text.

**Fix 8 — Title slide day-name layout.** Repositions day name on slides 2, 9, 16: enlarged to `sz="8800"`, centred horizontally, dominates the lower half of each title slide.

**Fix 9 — PQ button first click.** On slides 15 and 22 (Retrieval and Inference practice questions), the first interactiveSeq par has `delay="indefinite"` in the template, requiring two clicks before anything happens. Fix sets it to `delay="0"` so the Show/Hide button works on first click.

---

## Step 6: QA Checklist

Run these checks before delivering:

**PDFs:**
- [ ] Each individual page is exactly 1 page (no overflow)
- [ ] Header: "Key Question" [icon] "Day DD/MM/YYYY" on standard; pupil name right-aligned on adapted — date NOT right-aligned to page edge
- [ ] Tick instruction appears inline: "Question text? [Tick one.]" — not right-aligned
- [ ] Questions numbered 1. 2. 3. — no Q prefix
- [ ] Answer lines solid (not dashed)
- [ ] Q7 present on standard pages; Q5/Q6 present on adapted pages
- [ ] Match table has visible gap between columns for drawing lines
- [ ] All extracts are single paragraphs
- [ ] Ph2 pages: tick-only questions, glossary visible, large text
- [ ] Y1 pages: 6 questions, variety of tick_v / true_false / short across the 3 lessons
- [ ] Y4-adapted text: 200–220 words
- [ ] Day documents: adapted pupils appear before standard copies, sorted lowest→highest

**PPTX:**
- [ ] Title slides (2, 9, 16) show correct day names
- [ ] Vocab slides (4, 11, 18): all 5 words correct, all 5 ? bars aligned to rows
- [ ] Write-it-5-times slides (5, 12, 19): focus word in BOTH table cell AND spider diagram
- [ ] Extract text on slides matches PDF extract text exactly
- [ ] Fluency slides (6, 13, 20): You Do image visible, Show/Hide button present, extract hidden on load
- [ ] Show/Hide button works on first click on all three fluency slides and all three PQ slides (8, 15, 22)

---

## Step 7: File Naming and Output

```python
import zipfile

_day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
lesson_days = [voc_day, ret_day, inf_day]
sorted_days = sorted(lesson_days, key=lambda d: _day_order.index(d) if d in _day_order else 99)
day_prefix = {day: f'{i+1}-{day}' for i, day in enumerate(sorted_days)}

zip_path = f'/mnt/user-data/outputs/{week_ref} - Being a Reader.zip'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(pptx_path, arcname=f'{week_ref}/{week_ref} - ReaderTeaching.pptx')
    for arc_name, file_path in pdf_files.items():
        # Rename day folder: Monday/... → 1-Monday/...
        parts = arc_name.split('/', 1)
        if len(parts) == 2 and parts[0] in day_prefix:
            arc_name = f'{day_prefix[parts[0]]}/{parts[1]}'
        zf.write(file_path, arcname=f'{week_ref}/{arc_name}')
```

Use `present_files` on the zip only — do not present individual PDFs.

---

## Shared Text Mode

When shared text mode is on, all three lessons use the same source text (up to 500 words) rather than generating separate extracts. The source text is provided by Innes at Step 1.

- Content generator produces extracts derived from the shared text for each lesson type
- PDF builder also generates a `TextSheet/` per lesson day per class — a single-page PDF containing only the full source text (for pupils to read from)
- The text sheet is filed at: `{N}-{Day}/TextSheet/LMES.pdf` and `{N}-{Day}/TextSheet/IM.pdf`

---

## Vocabulary Reference

### Y4 words used — I Want My Hat Back topic (do not repeat)

**T5W1:** dialogue, persistent, suspicious, repetition, reveal, pattern, deny, politely, panicked, hopeless, technique, infer, omission, echo, impression

**T5W2:** courteous, naive, indifferent, emphatic, deceiving, pattern, calm, stands out, suddenly, direct, deliberately, defensive, recognise, guilt, structure

---

### Y5 words used

**T1W1 (Kensuke's Kingdom — Tension and atmosphere):**
- Vocabulary: voyage, horizon, despair, provisions, resist
- Retrieval: stern, current, consciousness, thrash, afloat
- Inference: enclosed, dread, peer, content, uneasy

---

## Lesson Type Reference

### Vocabulary
- LF: To understand key vocabulary
- I can: use context and clues to make meaning / answer questions related to vocabulary
- LO: understand and take meaning from a text / develop understanding of vocabulary / answering questions which relate to vocabulary

### Retrieval
- LF: To be able to retrieve information from a text
- I can: scan to find key words / answer questions with reference to the text
- LO: find and extract information from within a text / develop a clear understanding of what I am reading / answering questions making reference to the text

### Inference
- LF: To make inferences and apply my knowledge
- I can: infer based on clues in the text / answer questions with evidence from the text
- LO: make inferences based a text and impressions given by the content / develop a deeper understanding of what I am reading / using inference to answer questions making reference to the text
