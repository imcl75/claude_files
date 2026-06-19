---
name: being-a-reader
description: "Create a full week of Being a Reader reading comprehension resources for Y4 or Y5. Use this skill whenever Innes asks for reading lessons, Being a Reader lessons, reading comprehension resources, vocabulary/retrieval/inference lessons, or says things like 'make this week's reading', 'create the reading for next week', 'Being a Reader for [text]', 'reading lessons linked to [book]'. Also trigger when he uploads content and mentions reading questions, comprehension questions, or refers to the three-lesson reading cycle. This skill produces 5 files: 3 PDFs (Standard Pupil, Supported Pupil, All Answers), 1 PPTX (teaching slides), and 1 XLSX (content data file). Always use this skill even for partial requests like 'just the PDFs' or 'just the PPTX' — the skill handles selective output. Always ask year group (Y4/Y5) at session start."
---

# Being a Reader Skill

## Overview

Being a Reader is Innes's weekly reading comprehension system. Each week produces **5 files** from a single set of content:

1. ~~**XLSX** — master data file (all content in structured table)~~ **Not built by default — omit from the build loop unless Innes specifically asks for it. Code and column structure are preserved in Step 3 for when it is needed.**
2. **PPTX** — teaching slides for smartboard delivery (21 slides, 7 per lesson)
3. **Standard Pupil PDF** — 3 pages (Voc, Ret, Inf), 7 questions each
4. **Supported Pupil PDF** — 3 pages (Voc, Ret, Inf), 5 questions each
5. **All Answers PDF** — 6 pages (Std Voc, Sup Voc, Std Ret, Sup Ret, Std Inf, Sup Inf)

Order is always **Vocabulary → Retrieval → Inference**.

---

## Step 0: Session Restore (ALWAYS RUN FIRST)

At the start of every Being a Reader session, extract the embedded scripts before doing anything else:

```python
import base64, re

with open('/mnt/skills/user/being-a-reader/SKILL.md') as f:
    skill = f.read()

import re, base64, os
pattern = r'_SCRIPT_B64\["([^"]+)"\] = \(([\s\S]+?)\)\n\n'
for name, b64_block in re.findall(pattern, skill):
    lines = re.findall(r'"([A-Za-z0-9+/=]+)"', b64_block)
    b64 = ''.join(lines)
    with open(f'/home/claude/{name}.py', 'wb') as f:
        f.write(base64.b64decode(b64))
    print(f"Extracted {name}.py")
```

Scripts will be at `/home/claude/build_reading_pdfs.py`, `/home/claude/replace_reading_pptx.py`, and `/home/claude/slide_finishing_fixes.py`.

The previous week's PPTX is stored in GitHub at `imcl75/claude_files/Reading/BeingAReader_Template.pptx`. Fetch it silently at session start using the github-sync fetch pattern if not already in the session. Only ask Innes if the GitHub fetch fails.

---

## Step 1: Gather Required Inputs

Before generating anything, collect from Innes:

| Input | Example |
|-------|---------|
| Year group | Y4 / Y5 |
| Term (Y5 only) | T1–T6 — drives calibration from progression table |
| Text / book | I Want My Hat Back (Jon Klassen) |
| Key question | "How do writers use dialogue?" |
| Week reference | T5W2 |
| Day + date for each lesson | Voc=Tue 28/04, Ret=Thu 30/04, Inf=Fri 01/05 |

Generate all content (extracts, questions, answers, vocabulary) yourself unless Innes supplies an XLSX.

---

## Step 2: Content Generation Rules

### Text Extracts

- Write **one extract per lesson**, used on both PPTX slide and PDF worksheet
- **CRITICAL: The extract text must be byte-for-byte identical across PPTX slide, PPTX practice Q, XLSX, and PDF worksheet**
- For narrative/book topics: write as **narrative literary prose** — a single flowing paragraph that reads like a well-written literary analysis. NOT non-fiction report style, NOT bullet points, NOT multiple separated paragraphs
- Standard extract: **Y4 = 200–250 words / Y5 = 250–300 words, single paragraph**
- Supported extract: **Y4 = 130–150 words / Y5 = 160–180 words, single simpler paragraph**
- Embed lesson vocabulary words naturally in the standard extract

### Vocabulary (5 words per lesson, 15 total)

- **Y4:** Tier 2 words, accessible for age 8–9. Child-friendly definition: one clear sentence.
- **Y5:** Tier 2 words — complexity increases progressively through the year (see Y5 progression table below). Definition: one precise sentence.
- Focus word (Write it 5 times slide) = the most commonly encountered Tier 2 word
- Never repeat words across weeks on the same topic

### Questions

- Standard: 7 questions. Supported: 5 questions (genuinely easier, not just fewer)
- Questions progress Q1 (easiest) → Q7 (hardest)
- **Q7 is always first to drop** if the page doesn't fit on a single A4
- **Y4 calibration:** answerable in 1–3 sentences by an 8–9 year old; inference questions focus on unstated meaning from clues
- **Y5 calibration:** see progression table below — pupils enter Y5 as Y4 readers; complexity builds gradually across the year
- Use at least 4 different question formats per lesson, and vary the mix across all three lessons so no two lessons in the same week use the same dominant type

### Question type distribution — aim for this variety each week

The goal is that across the three lessons pupils encounter the full range of question formats — preparing them for assessment variety rather than pattern-matching a single style. No type should appear in all three lessons in the same week unless unavoidable.

**Vocabulary lesson** — focus on word meaning, context, and language choices:
Best types: `quote` (find the word), `tick_v` (which meaning fits), `fill` (complete with vocab word), `true_false` (does this definition fit), `mc`, `short`, `short2`, `written` (how does the word choice affect the reader)

**Retrieval lesson** — focus on locating specific detail and sequencing:
Best types: `short` (what/when/where/who), `evidence2` / `evidence3` (write two/three things), `order` (sequence events), `attrib_table` (who did what), `quote` (find and copy), `tick_v`, `short2`

**Inference lesson** — focus on deduction, author intent, and extended response:
Best types: `written` (extended reasoning), `evidence2_ext` (two detailed inferences), `select` (tick all emotions/effects), `tf_table` (valid inference or not), `short2` (what does X suggest), `quote` (find evidence that), `impr_evidence` (Y6 only)

**Across-week variety rules — HARD CONSTRAINTS:**

1. **No type in all three lessons.** Before finalising, list the types used in each lesson. Any type appearing in Vocabulary AND Retrieval AND Inference must be replaced in at least one lesson. Exception: `written` at Q6–Q7 is permitted in all three because extended response is required there — but nowhere else.
2. **Each lesson must have a distinct dominant type** that does not appear in either of the other two. Plan this before authoring:
   - Vocabulary: owns `tick_v`, `fill`, `match` — do not use these in Retrieval or Inference
   - Retrieval: owns `quote`, `order`, `attrib_table` — do not use these in Vocabulary or Inference
   - Inference: owns `mc`, `select`, `tf_table` — do not use these in Vocabulary or Retrieval
3. **Shared pool** (usable in any lesson, but not all three): `short`, `short2`, `evidence2`, `evidence2_ext`, `evidence3`, `true_false`
4. **Q1 rule:** always an accessible closed format (`tick_v`, `mc`, `short`, `true_false`, `fill`) — never open-ended writing
5. **Q7 rule:** always the hardest — `written` extended response, `evidence2_ext`, or equivalent
6. **No more than 2 `written` questions per page** — use `short2` for mid-range responses
7. **After authoring, run this mental check:** list all 7 types for each lesson; if any non-`written` type appears in all three, fix it before building
- Fluency target (both year groups): **90 wpm** (texts become more challenging; rate stays constant)

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
| `true_false` | `None` | `"True"` or `"False"` | Radio buttons; correct filled on answer sheet |
| `select` | `["A","B","C","D","E"]` | `["B","D"]` | Tick ALL that apply — square checkboxes; correct is a **list** |
| `tick_v` | `["A","B","C","D"]` | `"C"` or `["B","D"]` | **KS2-style** vertical tick, box on right; "Tick one." / "Tick two." auto-inferred |
| `tf_table` | `["Stmt 1","Stmt 2","Stmt 3"]` | `["True","False","True"]` | **KS2-style** True/False multi-row table |
| `evidence2` | `None` | `["Answer 1","Answer 2"]` | **KS2-style** numbered 1./2. list, 1 line each — "Write two ways" |
| `evidence2_ext` | `None` | `["Answer 1","Answer 2"]` | Numbered 1./2. list, 2 lines each |
| `evidence3` | `None` | `["A1","A2","A3"]` | **KS2-style** numbered 1./2./3. list |
| `fill` | `None` | `"word1/word2"` | Inline fill-in-blank; use `______________` in qtext |
| `match` | `[("L1","R1"),...]` | — | Connecting circles — pupils draw lines between matched pairs |
| `impr_evidence` | `2` (n rows) | `[("Impression","Evidence text"),...]` | **KS2-style** Impression/Evidence 2-column table (Q38 style, Y6) |
| `attrib_table` | `[["James","Mandy"],"stmt1","stmt2",...]` | `["James","Mandy","James","Mandy"]` | **KS2-style** attribution table; options[0]=headers, options[1:]=rows |
| `order` | `["step1","step2",...]` | `"2,1,3"` | **KS2-style** sequencing, number box on right |

**KS2 2026 question type mapping** (for reference when calibrating question mix):
`tick_v` = KS2 "Tick one/two" (most frequent) · `short` = KS2 short line · `evidence2/3` = KS2 numbered list · `tf_table` = KS2 True/False table · `attrib_table` = KS2 attribution (James/Mandy) · `order` = KS2 sequencing · `quote` = KS2 "Find and copy" · `impr_evidence` = KS2 Q38 Impression/Evidence (Y6)

**Q7 is always first to drop** if space runs out — write Q7 as the hardest/longest question.

### Y5 Progression Table (use TERM to select the right row)

Pupils start Y5 at broadly Y4 standard. Do not jump calibration — step up only at the term boundaries below.

| Term | Extract length (std) | Extract length (sup) | Vocabulary | Question demand |
|------|---------------------|---------------------|------------|-----------------|
| T1 | 220–245 words | 145–160 words | Tier 2, Y4-level; familiar register | Q1–Q5 as Y4; Q6–Q7 begin to ask for a reason or short justification |
| T2 | 235–260 words | 150–165 words | Tier 2, slightly less familiar words | Q6–Q7 require a full sentence with evidence |
| T3 | 250–275 words | 160–175 words | Tier 2; one word per lesson that stretches | Q4–Q7 expect 2 sentences; first inference question about author purpose |
| T4 | 265–290 words | 168–182 words | Tier 2 mix, higher register overall | Q5–Q7 need 2–3 sentences; inference includes effect on reader |
| T5 | 278–305 words | 175–190 words | Tier 2 with occasional Tier 3 for standard | Q6–Q7 require extended response; at least one question weighs two interpretations |
| T6 | 290–320 words | 180–200 words | Tier 2/3 mix for standard | Full Y5 demand — bias, purpose, ambiguity expected at Q5–Q7 |

Note: Y5 extract lengths run ~15–20 words longer than Y4 equivalents at each tier. This is possible because the tighter question layout (question label grouped with its answer, first writing line flush to question text) recovers enough vertical space on the page to accommodate the longer extract box without losing questions.

**How to apply:** at Step 1, collect `TERM` (T1–T6) alongside `YEAR_GROUP`. For Y4, ignore this table.

### We Do Questions (PPTX Practice Q slide)

Two questions per lesson shown with answers on the PPTX Practice Questions slide.

**HARD RULE — We Do questions must NEVER appear in the LP question list.** Write the LP questions first, then write the We Do questions afterwards as simpler whole-class modelling versions of a similar skill. They should test the same lesson type (vocabulary/retrieval/inference) but use different wording, a different angle, or a simpler demand than any LP question. If a We Do question is accidentally identical or near-identical to an LP question, rewrite it before proceeding.

---

## Step 3: Build the XLSX

Read `/mnt/skills/public/xlsx/SKILL.md` first.

### Column Structure (locked — never change)

| Col | Header | Content |
|-----|--------|---------|
| A | Lesson Number | 1, 2, or 3 |
| B | Lesson | Vocabulary / Retrieval / Inference |
| C | Version | Standard / Standard (MC) / Supported |
| D | Section | Text / Vocabulary / Question / Answer |
| E | Word | Vocabulary word or Q1–Q7 |
| F | Content | Text, definition, question, or answer |

Row order per lesson/version: Text → Vocabulary (5 rows, Standard only) → Questions → Answers.
Apply `wrap_text=True`, `vertical="top"`. Column F width = 80.

---

## Step 4: Build the PDFs

Read `/mnt/skills/public/pdf/SKILL.md` first. Use ReportLab. Each page **must fit on exactly one A4 page** — hard constraint.

### Build Process

Build **12 individual PDFs** (Standard + Supported + Answers × 3 lessons), check each is 1 page, then merge into 3 and delete individuals.

```python
from pypdf import PdfReader, PdfWriter
# Merge: Standard = Voc_Std + Ret_Std + Inf_Std
# Supported = Voc_Sup + Ret_Sup + Inf_Sup
# All Answers = Voc_Std_Ans + Voc_Sup_Ans + Ret_Std_Ans + Ret_Sup_Ans + Inf_Std_Ans + Inf_Sup_Ans
```

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
BOX_BORDER = (0.173, 0.173, 0.424)   # #2c2c6c — text box border, question labels
BOX_BG     = (0.941, 0.941, 0.973)   # #f0f0f8 — text box background
GREEN      = (0.102, 0.478, 0.102)   # #1a7a1a — answer text
DARK       = (0.133, 0.133, 0.133)   # body text
GREY_LINE  = (0.6, 0.6, 0.6)        # answer lines, table borders
```

**Y5 (Hazel — pale orange scheme):**
```python
BOX_BORDER = (0.706, 0.392, 0.071)   # #b46312 — text box border, question labels
BOX_BG     = (0.988, 0.949, 0.914)   # #fcf2e9 — very pale orange background
GREEN      = (0.102, 0.478, 0.102)   # #1a7a1a — answer text (unchanged)
DARK       = (0.133, 0.133, 0.133)   # body text (unchanged)
GREY_LINE  = (0.6, 0.6, 0.6)        # answer lines, table borders (unchanged)
```

**Y5 colour patch — run this after Step 0 extraction if YEAR_GROUP == 'Y5':**
```python
with open('/home/claude/build_reading_pdfs.py', 'r') as f:
    src = f.read()
src = (src
    .replace("BOX_BORDER = (0.173, 0.173, 0.424)   # #2c2c6c",
             "BOX_BORDER = (0.706, 0.392, 0.071)   # #b46312 Y5")
    .replace("BOX_BG     = (0.941, 0.941, 0.973)   # #f0f0f8",
             "BOX_BG     = (0.988, 0.949, 0.914)   # #fcf2e9 Y5")
    # Key question text and underline colour in draw_header
    .replace("c.setFillColorRGB(0.173, 0.173, 0.424)",
             "c.setFillColorRGB(0.706, 0.392, 0.071)")
    .replace("c.setStrokeColorRGB(0.173, 0.173, 0.424)",
             "c.setStrokeColorRGB(0.706, 0.392, 0.071)")
)
with open('/home/claude/build_reading_pdfs.py', 'w') as f:
    f.write(src)
print("Y5 colour patch applied.")
```

### Header Layout — EXACT (do not vary)

```
Key Question  [icon]  Day DD/MM/YYYY
```

All on **one line, left to right**. "Key Question" at left margin. Icon ~26mm from left. Date **immediately after icon** (~34mm from left). **The date is NOT right-aligned to the right edge of the page.**

```python
# Correct:
c.drawString(MARGIN, y - 5*mm, "Key Question")
icon_x = MARGIN + 26*mm
c.drawImage(ICON_PATH, icon_x, y - 7*mm, width=7*mm, height=7*mm, mask='auto')
c.drawString(icon_x + 8*mm, y - 5*mm, f"{day} {date}")

# WRONG — do not do this:
c.drawRightString(MARGIN + CW, y - 5*mm, f"{day} {date}")
```

Then below the header line (with thin divider):
- Key question: bold, underlined, dark blue (#2c2c6c)
- LF: [learning focus] — plain 8pt
- I can [statement 1] — plain 8pt
- I can [statement 2] — plain 8pt
- Thin divider line

### Text Extract Box

Rounded-corner bordered box. Border #2c2c6c, bg #f0f0f8. Font: Helvetica 10.5pt. Single flowing paragraph. Approx 30–35mm tall for standard text, 22–27mm for supported.

### Question Rendering Rules — EXACT (do not vary)

**Question numbering: plain `1.` `2.` `3.` — NEVER `Q1.` `Q2.` etc.**

```python
label = f"{qnum[1:]}. "   # qnum is stored as "Q1", "Q2" etc — strip the Q
```

**Answer lines: SOLID, not dashed**

```python
def answer_lines(c, y, n, gap=6.5*mm):
    c.setStrokeColorRGB(*GREY_LINE)
    c.setLineWidth(0.4)
    # NO setDash — solid lines only
    for i in range(n):
        ly = y - (i + 1) * gap
        c.line(MARGIN, ly, MARGIN + CW, ly)
    return y - n * gap - 2*mm
```

Standard: 3 lines per written question. Supported: 2 lines.

**Inter-question spacing:** Allow ~3–4mm between bottom of one question block and top of the next question label. After `render_question()` return `y - 3*mm`. After MC tables add an extra 1mm. After match tables add an extra 1mm.

**MC table:** 4-cell 2×2, full page width, ~6mm row height.

**Match table:** Left col 28%, right col 48%, 24% gap between for drawing lines. Row height 7mm.

**Tick options — column logic:**
```python
max_len = max(len(o) for o in options)
if max_len > 25:
    per_row = 2   # long options: 2 per row
elif len(options) == 5:
    per_row = 5   # 5 short options: all on one row
else:
    per_row = 4
```

**Fill-in-blank:** Draw only the prompt as the question label (not the sentence). Draw the fill sentence separately with an inline underline blank (28mm wide).

**Order/Sequencing:** Small square boxes (~8×4mm) at left margin.

### Answer PDF Rendering

- MC correct: cell highlighted, bold text + ✓
- Tick correct: bold green text
- Match: ——■ connector, green italic definition on right
- Fill correct: bold green word inline where blank was
- Written: green italic text below question
- Order correct: green bold numbers in boxes

---

## Step 5: Build the PPTX

### CRITICAL: Do NOT build from scratch with pptxgenjs

**CRITICAL — build_reading_pdfs.py dispatch:** The `render_question` function must handle ALL question types in its dispatch section. Types with height estimates but missing dispatch will silently render nothing. Confirmed working types (both estimated AND dispatched): `mc`, `match`, `tick2`, `tick3`, `fill`, `order`, `written`, `short`, `short2`, `quote`, `true_false`, `select`, `tick_v`, `tf_table`, `evidence2`, `evidence2_ext`, `evidence3`, `attrib_table`, `impr_evidence`. If adding a new type, add it to BOTH the height estimate block AND the dispatch block.

**CRITICAL — replace_reading_pptx.py calibration:** The script searches for specific text from the *previous week's* PPTX to do word/definition/extract replacement. At the start of each session, the `T5W1_VOCAB`, `T5W1_FOCUS`, `t1_hints`, `T5W1_DAYS` and `T5W1_PQ` constants must match whatever is in the source PPTX. Survey slides 4, 11, 18 (vocab tables), slides 5, 12, 19 (focus words), slides 6, 13, 20 (extract first line) and slides 8, 15, 22 (PQ first line) before running — then patch accordingly. For Y5, the T6W1 (Varjak Paw) patch is already applied to the script in the base64 block.

**Template sources (GitHub `imcl75/claude_files/Reading/`):**
- Y4: `BeingAReader_Template.pptx` — updated after each Y4 build (this is the current week → next week flow)
- Y5: `BeingAReader_Y5_Master.pptx` — permanent fallback; use as base for the first Y5 session, and whenever the previous week's Y5 PPTX is unavailable

If the previous week's PPTX is not in the session, fetch from GitHub silently (use the github-sync fetch pattern). Ask Innes only if the fetch fails.

### Build Workflow

```bash
# 1. Unpack
python /mnt/skills/public/pptx/scripts/office/unpack.py PREVIOUS_WEEK.pptx unpacked/

# 2. Edit slide XML files (see below)

# 3. Apply finishing fixes — MANDATORY (see Step 5b)
python /home/claude/slide_finishing_fixes.py unpacked/

# 4. Clean
python /mnt/skills/public/pptx/scripts/clean.py unpacked/

# 5. Repack
python /mnt/skills/public/pptx/scripts/office/pack.py unpacked/ OUTPUT.pptx --original PREVIOUS_WEEK.pptx

# 6. QA: convert to PDF and rasterise
soffice --headless --convert-to pdf OUTPUT.pptx --outdir ./
pdftoppm -jpeg -r 120 OUTPUT.pdf qa/slide
```

### XML Encoding Rules

The PPTX XML uses **mixed encoding**:
- Em dashes (—) are stored as **literal unicode** (U+2014)
- Curly quotes are stored as **XML entities**: `&#x201C;` `&#x201D;` `&#x2018;` `&#x2019;`

Use this function when inserting T5W2 text into XML:

```python
def to_xml(text):
    return (text
        .replace('&', '&amp;')
        .replace('\u201c', '&#x201C;')
        .replace('\u201d', '&#x201D;')
        .replace('\u2018', '&#x2018;')
        .replace('\u2019', '&#x2019;'))
```

To find and extract existing text from a slide:

```python
import re

def extract_run_text(xml, hint):
    """Get the raw content of the <a:t> tag containing hint."""
    idx = xml.find(hint)
    if idx == -1:
        return None
    t_start = xml.rfind('<a:t>', 0, idx)
    t_end = xml.find('</a:t>', idx)
    return xml[t_start + 5: t_end] if t_start != -1 else None

def replace_sp_by_name(xml, shape_name, new_y, new_cy):
    """Reposition a shape by finding it by name — safe against group shape collision."""
    idx = xml.find(f'name="{shape_name}"')
    if idx == -1:
        return xml
    sp_start = xml.rfind('<p:sp>', 0, idx)
    sp_end = xml.find('</p:sp>', idx) + 7
    old_sp = xml[sp_start:sp_end]
    new_sp = re.sub(r'(<a:off x=")([^"]+)(" y=")([^"]+)(")',
                    lambda m: m.group(1)+m.group(2)+m.group(3)+str(new_y)+m.group(5),
                    old_sp, count=1)
    new_sp = re.sub(r'(<a:ext cx=")([^"]+)(" cy=")([^"]+)(")',
                    lambda m: m.group(1)+m.group(2)+m.group(3)+str(new_cy)+m.group(5),
                    new_sp, count=1)
    return xml[:sp_start] + new_sp + xml[sp_end:]
```

**DANGER: Never use a generic `<a:off x=... y=...>` regex across a whole slide — it will hit shapes inside groups (e.g. Oval 9 inside the Vocabulary badge group). Always find the enclosing `<p:sp>` by name first using the approach above.**

### Slide Map (21 slides, 7 per lesson)

| Slides | Lesson | What to replace |
|--------|--------|-----------------|
| 1, 8, 15 | Title | Day name text |
| 2, 9, 16 | Why We Read | Nothing — leave as is |
| 3, 10, 17 | Vocab Focus (hidden defs) | 5 words + 5 definitions in table |
| 4, 11, 18 | Write it 5 times | Focus word (appears TWICE: table cell + spider diagram) |
| 5, 12, 19 | Independent Read | Full text extract + fluency instruction (Ret/Inf only) |
| 6, 13, 20 | Learning Objective | Nothing — leave as is (fixed per lesson type) |
| 7, 14, 21 | Practice Questions | Q1, A1, Q2, A2 + extract text |

### Vocab Hidden Slides — CRITICAL Geometry

The blue ? bars must exactly cover each table row. These dimensions are fixed and must be identical across all three vocab slides (slides 3, 10, 17):

```python
TABLE_TOP  = 2173922   # EMU from top of slide
TABLE_LEFT = 647700
TABLE_W    = 10663199
ROW_H      = 685800    # Each row — generous for any definition length
N_ROWS     = 5
TABLE_H    = ROW_H * N_ROWS   # 3429000

RECT_LEFT  = 2312410   # Rectangles (blue ? bars) start here
RECT_W     = 8985789

# Rectangle top for row i:
rect_top_i = TABLE_TOP + i * ROW_H   # i = 0,1,2,3,4
```

**To update table row heights in XML:**
```python
# Update graphicFrame ext
new_gf = re.sub(r'(<a:ext cx=")([^"]+)(" cy=")([^"]+)(")',
                lambda m: m.group(1)+str(TABLE_W)+m.group(3)+str(TABLE_H)+m.group(5),
                gf, count=1)
# Update each row height
new_gf = re.sub(r'(<a:tr h=")(\d+)(")',
                lambda m: m.group(1)+str(ROW_H)+m.group(3), new_gf)
```

**Definitions MUST remain in table cells** — PowerPoint uses click animation to reveal them by moving the blue bar. Do not clear the definition text. The bleed-through seen in LibreOffice rendering does not occur in PowerPoint.

### Vocabulary Badge Circle — Do Not Move

The green "Vocabulary" circle badge (Group 8 containing Oval 9 + Oval 4) must stay at its original position. Oval 9 correct position:

```python
OVAL9_X, OVAL9_Y = 5180554, 1026138
OVAL9_CX, OVAL9_CY = 1316831, 1316831
```

If Oval 9 gets accidentally moved during rectangle updates, restore it explicitly.

### Independent Read Slide — Fluency Instruction

**Retrieval slide (slide 12):** The fluency instruction is in **Shape 0** at sz=4400 — this is a large text box intentionally displayed large. It is the primary display shape. Do not delete it. Do not add a duplicate. Just replace the text in the existing large shape.

```python
# Find Shape 0 (first p:sp), replace its text content
# T5W2 Retrieval: "Fluency focus – Volume.  Take turns reading aloud to the whole class.  Remember to position yourself and push your voice so everyone can hear."
```

The slide's structure: Shape 0 (large fluency instruction) → extract text box → Show/Hide Extract button.

**Inference slide (slide 19):** Fluency instruction is "Fluency focus – Echo read" — usually unchanged, just verify it's present.

### Reader Icon for PDF Header

The reader icon used in PDF headers is stored in the PPTX media. Extract it at session start:

```python
import zipfile
with zipfile.ZipFile('PREVIOUS_WEEK.pptx') as z:
    with open('reader_icon_saved.png', 'wb') as f:
        f.write(z.read('ppt/media/image2.png'))
```

---

---

## Step 5b: Permanent Slide Finishing Fixes — MANDATORY

The Innes-authored T5W1 PPTX template has four recurring bugs that re-emerge whenever content is replaced. These are not authorial errors in the content — they are template-level XML quirks. The bootstrap-extracted script `/home/claude/slide_finishing_fixes.py` repairs all four automatically. **Always run it after content replacement (Step 5) and before clean/pack.**

### The four fixes

**Fix 1 — Slide 13 huge fluency title.** The Title 1 shape on the Retrieval Read slide has `<a:defRPr sz="4400">` as the default size. Inside it is an orphan `<a:r>` run whose `<a:rPr>` has only `lang="en-GB"` and no `sz` attribute, so it inherits the 4400 size. That orphan run also contains the FULL fluency instruction, duplicating what's already in the smaller `sz="1800"` runs below. The fix deletes the orphan run.

**Fix 2 — Extract textbox font normalisation.** Slides 6, 8, 13, 15, 20, 22 all carry the long extract text. The original template uses inconsistent sizes (some `sz="1900"`, some `sz="2200"`, some `sz="2800"`) and several have `<a:normAutofit fontScale="70000" lnSpcReduction="20000"/>` actively shrinking the text further. The fix forces every extract textbox to `sz="2200"` and strips the autofit shrinkage attributes, so PPTX extracts always render at the same size on Read and PQ slides.

**Fix 3 — Spider focus word centring.** On slides 5, 12, 19, the standalone focus-word textbox in the "Other linked words" panel uses `wrap="none"` with `<a:spAutoFit/>`. The box auto-shrinks to fit the text width, and was originally placed for the longer T5W1 word "patient". When shorter words like "vibrate" or "wave" replace it, the box stays at the same `x` coordinate but the word now sits left-of-centre relative to the spider lines. The fix: widen the box to 2.4M EMU, switch to `wrap="square"` with `anchor="ctr"`, add `<a:pPr algn="ctr"/>`, and reposition `x`/`y` so the centre point of the box is preserved. Word stays centred on the spider intersection regardless of length.

**Fix 4 — Oval anchor=ctr.** Some "Fluency & Expression" / badge circles render with text top-aligned because their `<a:bodyPr>` has `anchor="t"` instead of `anchor="ctr"`. Slide 20 had this bug specifically. The fix walks every slide and forces `anchor="ctr"` on the bodyPr of any shape with `prst="ellipse"` or a name starting with `Oval` that contains text. Idempotent — slides already correct are unchanged.

**Fix 5 — Title slide day-name layout (slides 2, 9, 16).** The original template puts the day name in a tiny corner label at the top-left, which makes scrolling the deck to find a specific lesson day awkward. The fix repositions the layout to match Innes's preferred design: "Being a Reader" shifts up to y=2017477, "Lesson N - Type" shifts up to y=4552141, and the day name is enlarged to `sz="8800"` (88pt), centred horizontally at x=4423577, sized cx=3329758 cy=1446550, with `anchor="ctr"` and `algn="ctr"`. Result: the day name dominates the lower half of each title slide.

### Why this section exists

Without this step, every weekly build needs manual repair. The fixes are deterministic, idempotent, and add roughly 0.3 seconds to the build. Skipping them is never correct.

## Step 6: QA Checklist

Run these checks before delivering:

**PDFs:**
- [ ] Each of the 12 individual pages is exactly 1 page
- [ ] Header: "Key Question" [icon] "Day DD/MM/YYYY" — date NOT right-aligned
- [ ] Questions numbered 1. 2. 3. — no Q prefix
- [ ] Answer lines solid (not dashed)
- [ ] Q7 present on every page (if not, reduce spacing slightly)
- [ ] Match table has visible gap between columns for drawing lines
- [ ] Tick options on 1 row if short (≤25 chars each), 2 rows if long
- [ ] All extracts are single paragraphs, not split into multiple paragraphs

**PPTX:**
- [ ] Validate passes: `python /mnt/skills/public/pptx/scripts/office/pack.py ... --original`
- [ ] Title slides show correct day names (Tue/Thu/Fri not Mon/Tue/Wed)
- [ ] Vocab slides: all 5 words correct, all 5 ? bars aligned to rows, no bleed-through visible when tested in LibreOffice render (check pdftoppm output)
- [ ] Write-it-5-times slides: focus word appears in BOTH table cell AND spider diagram
- [ ] Extract text on slides matches PDF extract text exactly
- [ ] Fluency instruction on Retrieval slide renders at large size (sz=4400), single text box only

**After QA:**
- **Y4:** save as `BeingAReader_Template.pptx` in `/home/claude/` and push to `Reading/BeingAReader_Template.pptx` via github-sync (overwrites — this becomes next week's Y4 base)
- **Y5:** save as the output file only; the permanent Y5 master in GitHub is not overwritten each week

---

## Step 7: File Naming and Output

```
{TaWb}_Being_a_Reader.pptx         e.g. T5W2_Being_a_Reader.pptx
Reading_Content_{TaWb}.xlsx        e.g. Reading_Content_T5W2.xlsx
{TaWb}_Standard_Pupil.pdf          e.g. T5W2_Standard_Pupil.pdf
{TaWb}_Supported_Pupil.pdf         e.g. T5W2_Supported_Pupil.pdf
{TaWb}_All_Answers.pdf             e.g. T5W2_All_Answers.pdf
```

Copy all 5 to `/mnt/user-data/outputs/` and use `present_files`.

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

---

## Reference Files

- `references/question-types.md` — Full question type catalogue, rendering rules, Y4 guidance
- `references/pptx-slides.md` — Detailed PPTX slide specifications and image assets

---

## Embedded Scripts (auto-extracted at session start)

At the very start of every Being a Reader session, run this bootstrap to extract the working scripts:

```python
import base64, os, sys

_SCRIPT_B64 = {}
_SCRIPT_B64["build_reading_pdfs"] = (
    "IiIiClQ1VzIgUERGIGJ1aWxkZXIg4oCUIG1hdGNoZXMgVDVXMSBsYXlvdXQgZXhhY3RseS4KUHJv"
    "ZHVjZXMgMTIgaW5kaXZpZHVhbCBQREZzIHRoZW4gbWVyZ2VzIGludG8gMy4KIiIiCmltcG9ydCBz"
    "eXMKc3lzLnBhdGguaW5zZXJ0KDAsICcvaG9tZS9jbGF1ZGUnKQpmcm9tIHQ1dzJfY29udGVudCBp"
    "bXBvcnQgKgoKZnJvbSByZXBvcnRsYWIubGliLnBhZ2VzaXplcyBpbXBvcnQgQTQKZnJvbSByZXBv"
    "cnRsYWIucGRmZ2VuIGltcG9ydCBjYW52YXMKZnJvbSByZXBvcnRsYWIubGliLnVuaXRzIGltcG9y"
    "dCBtbQpmcm9tIHB5cGRmIGltcG9ydCBQZGZSZWFkZXIsIFBkZldyaXRlcgppbXBvcnQgb3MKClcs"
    "IEggPSBBNApNQVJHSU4gPSA4ICogbW0KQ1cgPSBXIC0gMiAqIE1BUkdJTiAgIyBjb250ZW50IHdp"
    "ZHRoCgojIENvbG91cnMgbWF0Y2hpbmcgVDVXMQpCT1hfQk9SREVSID0gKDAuMTczLCAwLjE3Mywg"
    "MC40MjQpICAgIyAjMmMyYzZjCkJPWF9CRyAgICAgPSAoMC45NDEsIDAuOTQxLCAwLjk3MykgICAj"
    "ICNmMGYwZjgKR1JFRU4gICAgICA9ICgwLjEwMiwgMC40NzgsIDAuMTAyKSAgICMgIzFhN2ExYQpE"
    "QVJLICAgICAgID0gKDAuMTMzLCAwLjEzMywgMC4xMzMpCkdSRVlfTElORSAgPSAoMC42LCAwLjYs"
    "IDAuNikKCklDT05fUEFUSCA9ICIvaG9tZS9jbGF1ZGUvcmVhZGVyX2ljb25fc2F2ZWQucG5nIgpP"
    "VVRfRElSICAgPSAiL2hvbWUvY2xhdWRlL3BkZnNfaW5kaXZpZHVhbCIKb3MubWFrZWRpcnMoT1VU"
    "X0RJUiwgZXhpc3Rfb2s9VHJ1ZSkKCgpkZWYgZHJhd19oZWFkZXIoYywgbGVzc29uX3R5cGUsIGRh"
    "dGVfc3RyLCBrZXlfcSwgbGYsIGljYW4xLCBpY2FuMik6CiAgICAiIiJEcmF3IHRoZSBsZWFybmlu"
    "ZyBsYWJlbCBoZWFkZXIuIFJldHVybnMgeSBhZnRlciBoZWFkZXIuIiIiCiAgICB5ID0gSCAtIE1B"
    "UkdJTgoKICAgICMgUm93IDE6ICJLZXkgUXVlc3Rpb24iIFtpY29uXSBkYXRlIOKAlCBhbGwgb24g"
    "b25lIGxpbmUgbGVmdC10by1yaWdodAogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDgp"
    "CiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHkg"
    "LSA1Km1tLCAiS2V5IFF1ZXN0aW9uIikKICAgIGljb25feCA9IE1BUkdJTiArIDI2Km1tCiAgICB0"
    "cnk6CiAgICAgICAgYy5kcmF3SW1hZ2UoSUNPTl9QQVRILCBpY29uX3gsIHkgLSA3Km1tLCB3aWR0"
    "aD03Km1tLCBoZWlnaHQ9NyptbSwKICAgICAgICAgICAgICAgICAgICBtYXNrPSdhdXRvJywgcHJl"
    "c2VydmVBc3BlY3RSYXRpbz1UcnVlKQogICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICBwYXNz"
    "CiAgICAjIERhdGUgaW1tZWRpYXRlbHkgYWZ0ZXIgaWNvbgogICAgYy5zZXRGb250KCJIZWx2ZXRp"
    "Y2EiLCA4KQogICAgZGF5LCBkYXRlID0gZGF0ZV9zdHIKICAgIGMuZHJhd1N0cmluZyhpY29uX3gg"
    "KyA4Km1tLCB5IC0gNSptbSwgZiJ7ZGF5fSB7ZGF0ZX0iKQogICAgeSAtPSA3Km1tCgogICAgIyBE"
    "aXZpZGVyCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnNldExpbmVX"
    "aWR0aCgwLjMpCiAgICBjLmxpbmUoTUFSR0lOLCB5LCBNQVJHSU4gKyBDVywgeSkKICAgIHkgLT0g"
    "MSptbQoKICAgICMgS2V5IHF1ZXN0aW9uIOKAlCB1bmRlcmxpbmVkLCBib2xkLCBkYXJrIGJsdWUK"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCAxMCkKICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KDAuMTczLCAwLjE3MywgMC40MjQpCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gNCptbSwg"
    "a2V5X3EpCiAgICBrcV93ID0gYy5zdHJpbmdXaWR0aChrZXlfcSwgIkhlbHZldGljYS1Cb2xkIiwg"
    "MTApCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuMTcz"
    "LCAwLjE3MywgMC40MjQpCiAgICBjLmxpbmUoTUFSR0lOLCB5IC0gNSptbSwgTUFSR0lOICsga3Ff"
    "dywgeSAtIDUqbW0pCiAgICB5IC09IDYqbW0KCiAgICAjIExGIGxpbmUKICAgIGMuc2V0Rm9udCgi"
    "SGVsdmV0aWNhIiwgOCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgYy5kcmF3U3Ry"
    "aW5nKE1BUkdJTiwgeSAtIDMuNSptbSwgbGYpCiAgICB5IC09IDQuNSptbQoKICAgICMgSSBjYW4g"
    "bGluZXMKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHkgLSAzLjUqbW0sIGljYW4xKQogICAgeSAt"
    "PSA0Km1tCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gMy41Km1tLCBpY2FuMikKICAgIHkg"
    "LT0gNC41Km1tCgogICAgIyBEaXZpZGVyCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJ"
    "TkUpCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLmxpbmUoTUFSR0lOLCB5LCBNQVJHSU4g"
    "KyBDVywgeSkKICAgIHkgLT0gMiptbQoKICAgIHJldHVybiB5CgoKZGVmIHdyYXBfdGV4dChjLCB0"
    "ZXh0LCBmb250LCBzaXplLCBtYXhfdyk6CiAgICAiIiJXcmFwIHRleHQgdG8gbGluZXMgZml0dGlu"
    "ZyBtYXhfdy4gUmV0dXJucyBsaXN0IG9mIGxpbmVzLiIiIgogICAgd29yZHMgPSB0ZXh0LnNwbGl0"
    "KCkKICAgIGxpbmVzLCBsaW5lID0gW10sICcnCiAgICBmb3IgdyBpbiB3b3JkczoKICAgICAgICB0"
    "ZXN0ID0gKGxpbmUgKyAnICcgKyB3KS5zdHJpcCgpCiAgICAgICAgaWYgYy5zdHJpbmdXaWR0aCh0"
    "ZXN0LCBmb250LCBzaXplKSA8PSBtYXhfdzoKICAgICAgICAgICAgbGluZSA9IHRlc3QKICAgICAg"
    "ICBlbHNlOgogICAgICAgICAgICBpZiBsaW5lOgogICAgICAgICAgICAgICAgbGluZXMuYXBwZW5k"
    "KGxpbmUpCiAgICAgICAgICAgIGxpbmUgPSB3CiAgICBpZiBsaW5lOgogICAgICAgIGxpbmVzLmFw"
    "cGVuZChsaW5lKQogICAgcmV0dXJuIGxpbmVzIG9yIFsnJ10KCgpkZWYgZHJhd190ZXh0X2JveChj"
    "LCB0ZXh0LCB5X3RvcCwgZm9udF9zaXplPTEwLjUpOgogICAgIiIiRHJhdyB0aGUgcmVhZGluZyB0"
    "ZXh0IGJveC4gUmV0dXJucyB5IGFmdGVyIGJveC4iIiIKICAgIGxpbmVzID0gd3JhcF90ZXh0KGMs"
    "IHRleHQsICJIZWx2ZXRpY2EiLCBmb250X3NpemUsIENXIC0gNiptbSkKICAgIGxpbmVfaCA9IGZv"
    "bnRfc2l6ZSAqIDEuNAogICAgYm94X2ggPSBsZW4obGluZXMpICogbGluZV9oICsgNSptbQoKICAg"
    "ICMgQm94CiAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JHKQogICAgYy5zZXRTdHJva2VDb2xv"
    "clJHQigqQk9YX0JPUkRFUikKICAgIGMuc2V0TGluZVdpZHRoKDAuOCkKICAgIGMucm91bmRSZWN0"
    "KE1BUkdJTiwgeV90b3AgLSBib3hfaCwgQ1csIGJveF9oLCAyKm1tLCBmaWxsPTEsIHN0cm9rZT0x"
    "KQoKICAgICMgVGV4dAogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLnNldEZvbnQo"
    "IkhlbHZldGljYSIsIGZvbnRfc2l6ZSkKICAgIHR5ID0geV90b3AgLSAzKm1tIC0gZm9udF9zaXpl"
    "ICogMC43MgogICAgZm9yIGxpbmUgaW4gbGluZXM6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJ"
    "TiArIDMqbW0sIHR5LCBsaW5lKQogICAgICAgIHR5IC09IGxpbmVfaAoKICAgIHJldHVybiB5X3Rv"
    "cCAtIGJveF9oIC0gMyptbQoKCmRlZiBhbnN3ZXJfbGluZXMoYywgeSwgbiwgZ2FwPTYuNSptbSk6"
    "CiAgICAiIiJEcmF3IG4gc29saWQgYW5zd2VyIGxpbmVzLiBSZXR1cm5zIHkgYWZ0ZXIgbGluZXMu"
    "IiIiCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnNldExpbmVXaWR0"
    "aCgwLjQpCiAgICBmb3IgaSBpbiByYW5nZShuKToKICAgICAgICBseSA9IHkgLSAoaSArIDEpICog"
    "Z2FwCiAgICAgICAgYy5saW5lKE1BUkdJTiwgbHksIE1BUkdJTiArIENXLCBseSkKICAgIHJldHVy"
    "biB5IC0gbiAqIGdhcCAtIDIqbW0KCgpkZWYgZHJhd19xdW90ZV9wdXBpbChjLCB5KToKICAgICIi"
    "IlNpbmdsZSB1bmRlcmxpbmUgZm9yICdmaW5kIGFuZCBjb3B5JyBhbnN3ZXIuIiIiCiAgICBseSA9"
    "IHkgLSA2LjUqbW0KICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgIGMuc2V0"
    "TGluZVdpZHRoKDAuNSkKICAgIGMubGluZShNQVJHSU4sIGx5LCBNQVJHSU4gKyBDVywgbHkpCiAg"
    "ICByZXR1cm4geSAtIDgqbW0KCgpkZWYgZHJhd19xdW90ZV9hbnN3ZXIoYywgYW5zd2VyLCB5KToK"
    "ICAgICIiIkZpbmQtYW5kLWNvcHkgYW5zd2VyOiBncmVlbiB0ZXh0IGFib3ZlIGEgbGluZS4iIiIK"
    "ICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJv"
    "bGRPYmxpcXVlIiwgOSkKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAxKm1tLCB5IC0gNC41Km1t"
    "LCBmJyJ7YW5zd2VyfSInKQogICAgbHkgPSB5IC0gNi41Km1tCiAgICBjLnNldFN0cm9rZUNvbG9y"
    "UkdCKCpHUkVZX0xJTkUpCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLmxpbmUoTUFSR0lO"
    "LCBseSwgTUFSR0lOICsgQ1csIGx5KQogICAgcmV0dXJuIHkgLSA4Km1tCgoKZGVmIGRyYXdfdHJ1"
    "ZV9mYWxzZV9wdXBpbChjLCB5KToKICAgICIiIlRydWUgLyBGYWxzZSB3aXRoIGNpcmN1bGFyIHJh"
    "ZGlvIGJ1dHRvbnMuIiIiCiAgICBoYWxmID0gQ1cgLyAyCiAgICBjLnNldExpbmVXaWR0aCgwLjUp"
    "CiAgICBmb3IgaSwgbGFiZWwgaW4gZW51bWVyYXRlKFsiVHJ1ZSIsICJGYWxzZSJdKToKICAgICAg"
    "ICB4ID0gTUFSR0lOICsgaSAqIGhhbGYKICAgICAgICBjeCA9IHggKyAzLjUqbW0KICAgICAgICBj"
    "eSA9IHkgLSAzLjUqbW0KICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAg"
    "IGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC41LCAwLjUsIDAuNSkKICAgICAgICBjLmNpcmNsZShjeCwg"
    "Y3ksIDIuOCptbSwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigq"
    "REFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDEwKQogICAgICAgIGMuZHJhd1N0"
    "cmluZyhjeCArIDQqbW0sIHkgLSA1Km1tLCBsYWJlbCkKICAgIHJldHVybiB5IC0gOCptbQoKCmRl"
    "ZiBkcmF3X3RydWVfZmFsc2VfYW5zd2VyKGMsIGNvcnJlY3QsIHkpOgogICAgIiIiVHJ1ZSAvIEZh"
    "bHNlIOKAlCBjb3JyZWN0IG9wdGlvbiBmaWxsZWQuIiIiCiAgICBoYWxmID0gQ1cgLyAyCiAgICBj"
    "LnNldExpbmVXaWR0aCgwLjUpCiAgICBmb3IgaSwgbGFiZWwgaW4gZW51bWVyYXRlKFsiVHJ1ZSIs"
    "ICJGYWxzZSJdKToKICAgICAgICB4ID0gTUFSR0lOICsgaSAqIGhhbGYKICAgICAgICBjeCA9IHgg"
    "KyAzLjUqbW0KICAgICAgICBjeSA9IHkgLSAzLjUqbW0KICAgICAgICBpZiBsYWJlbCA9PSBjb3Jy"
    "ZWN0OgogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JPUkRFUikKICAgICAgICAg"
    "ICAgYy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikKICAgICAgICAgICAgYy5jaXJjbGUo"
    "Y3gsIGN5LCAyLjgqbW0sIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgICAgIGMuc2V0RmlsbENv"
    "bG9yUkdCKCpEQVJLKQogICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgMTAp"
    "CiAgICAgICAgZWxzZToKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAg"
    "ICAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjUsIDAuNSwgMC41KQogICAgICAgICAgICBj"
    "LmNpcmNsZShjeCwgY3ksIDIuOCptbSwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICAgICAgYy5z"
    "ZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwg"
    "MTApCiAgICAgICAgYy5kcmF3U3RyaW5nKGN4ICsgNCptbSwgeSAtIDUqbW0sIGxhYmVsKQogICAg"
    "cmV0dXJuIHkgLSA4Km1tCgoKZGVmIGRyYXdfc2VsZWN0X3B1cGlsKGMsIG9wdGlvbnMsIHkpOgog"
    "ICAgIiIiVGljayBBTEwgdGhhdCBhcHBseSDigJQgc3F1YXJlIGNoZWNrYm94ZXMsIDItY29sdW1u"
    "IGxheW91dC4iIiIKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLU9ibGlxdWUiLCA4KQogICAgYy5z"
    "ZXRGaWxsQ29sb3JSR0IoMC41LCAwLjUsIDAuNSkKICAgIG5vdGUgPSAiKFRpY2sgYWxsIHRoYXQg"
    "YXBwbHkg4oCUIHRoZXJlIG1heSBiZSBtb3JlIHRoYW4gb25lIGNvcnJlY3QgYW5zd2VyKSIKICAg"
    "IGMuZHJhd1N0cmluZyhNQVJHSU4sIHksIG5vdGUpCiAgICB5IC09IDUuNSptbQogICAgY29sX3cg"
    "PSBDVyAvIDIKICAgIGJveF9zID0gMy41Km1tCiAgICByb3dfaCA9IDYqbW0KICAgIHJvd3MgPSAo"
    "bGVuKG9wdGlvbnMpICsgMSkgLy8gMgogICAgYy5zZXRMaW5lV2lkdGgoMC41KQogICAgZm9yIGks"
    "IG9wdCBpbiBlbnVtZXJhdGUob3B0aW9ucyk6CiAgICAgICAgcm93ID0gaSAvLyAyCiAgICAgICAg"
    "Y29sID0gaSAlIDIKICAgICAgICB4ID0gTUFSR0lOICsgY29sICogY29sX3cKICAgICAgICByeSA9"
    "IHkgLSByb3cgKiByb3dfaAogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAgICAg"
    "ICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjUsIDAuNSwgMC41KQogICAgICAgIGMucmVjdCh4LCBy"
    "eSAtIGJveF9zLCBib3hfcywgYm94X3MsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAg"
    "ICAgIGMuZHJhd1N0cmluZyh4ICsgYm94X3MgKyAyKm1tLCByeSAtIGJveF9zICsgMSptbSwgb3B0"
    "KQogICAgcmV0dXJuIHkgLSByb3dzICogcm93X2ggLSAyKm1tCgoKZGVmIGRyYXdfc2VsZWN0X2Fu"
    "c3dlcihjLCBvcHRpb25zLCBjb3JyZWN0X2xpc3QsIHkpOgogICAgIiIiVGljayBBTEwgdGhhdCBh"
    "cHBseSDigJQgY29ycmVjdCBib3hlcyB0aWNrZWQgaW4gYWNjZW50IGNvbG91ci4iIiIKICAgIGMu"
    "c2V0Rm9udCgiSGVsdmV0aWNhLU9ibGlxdWUiLCA4KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoMC41"
    "LCAwLjUsIDAuNSkKICAgIG5vdGUgPSAiKFRpY2sgYWxsIHRoYXQgYXBwbHkg4oCUIHRoZXJlIG1h"
    "eSBiZSBtb3JlIHRoYW4gb25lIGNvcnJlY3QgYW5zd2VyKSIKICAgIGMuZHJhd1N0cmluZyhNQVJH"
    "SU4sIHksIG5vdGUpCiAgICB5IC09IDUuNSptbQogICAgY29sX3cgPSBDVyAvIDIKICAgIGJveF9z"
    "ID0gMy41Km1tCiAgICByb3dfaCA9IDYqbW0KICAgIHJvd3MgPSAobGVuKG9wdGlvbnMpICsgMSkg"
    "Ly8gMgogICAgYy5zZXRMaW5lV2lkdGgoMC41KQogICAgZm9yIGksIG9wdCBpbiBlbnVtZXJhdGUo"
    "b3B0aW9ucyk6CiAgICAgICAgcm93ID0gaSAvLyAyCiAgICAgICAgY29sID0gaSAlIDIKICAgICAg"
    "ICB4ID0gTUFSR0lOICsgY29sICogY29sX3cKICAgICAgICByeSA9IHkgLSByb3cgKiByb3dfaAog"
    "ICAgICAgIGlzX2NvcnJlY3QgPSBvcHQgaW4gY29ycmVjdF9saXN0CiAgICAgICAgaWYgaXNfY29y"
    "cmVjdDoKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CRykKICAgICAgICAgICAg"
    "Yy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikKICAgICAgICBlbHNlOgogICAgICAgICAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9y"
    "UkdCKDAuNSwgMC41LCAwLjUpCiAgICAgICAgYy5yZWN0KHgsIHJ5IC0gYm94X3MsIGJveF9zLCBi"
    "b3hfcywgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBpZiBpc19jb3JyZWN0OgogICAgICAgICAg"
    "ICAjIFRpY2sgbWFyawogICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpCT1hfQk9SREVS"
    "KQogICAgICAgICAgICBjLnNldExpbmVXaWR0aCgxKQogICAgICAgICAgICBjLmxpbmUoeCArIDAu"
    "NiptbSwgcnkgLSBib3hfcyArIDEuOCptbSwgeCArIDEuNCptbSwgcnkgLSBib3hfcyArIDAuOCpt"
    "bSkKICAgICAgICAgICAgYy5saW5lKHggKyAxLjQqbW0sIHJ5IC0gYm94X3MgKyAwLjgqbW0sIHgg"
    "KyAzLjEqbW0sIHJ5IC0gYm94X3MgKyAyLjgqbW0pCiAgICAgICAgICAgIGMuc2V0TGluZVdpZHRo"
    "KDAuNSkKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CT1JERVIpCiAgICAgICAg"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgICAgIGVsc2U6CiAgICAgICAg"
    "ICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3RyaW5nKHggKyBib3hfcyArIDIqbW0sIHJ5IC0gYm94"
    "X3MgKyAxKm1tLCBvcHQpCiAgICByZXR1cm4geSAtIHJvd3MgKiByb3dfaCAtIDIqbW0KCgoKZGVm"
    "IGRyYXdfdGlja192X3B1cGlsKGMsIG9wdGlvbnMsIGNvcnJlY3QsIHkpOgogICAgIiIiS1MyLXN0"
    "eWxlIHZlcnRpY2FsIHRpY2sgbGlzdCDigJQgYm94IHNpdHMganVzdCBhZnRlciB0aGUgdGV4dCwg"
    "bm90IGF0IGZhciByaWdodC4iIiIKICAgIG5fY29ycmVjdCA9IDEgaWYgaXNpbnN0YW5jZShjb3Jy"
    "ZWN0LCBzdHIpIGVsc2UgbGVuKGNvcnJlY3QpCiAgICBpbnN0ciA9IGYiVGljayB7J29uZScgaWYg"
    "bl9jb3JyZWN0ID09IDEgZWxzZSAndHdvJ30uIgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9s"
    "ZCIsIDkpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGl3ID0gYy5zdHJpbmdXaWR0"
    "aChpbnN0ciwgIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBD"
    "VyAtIGl3LCB5LCBpbnN0cikKICAgIHkgLT0gNi41Km1tCiAgICBjLnNldEZvbnQoIkhlbHZldGlj"
    "YSIsIDkpCiAgICBtYXhfdyA9IG1heChjLnN0cmluZ1dpZHRoKG8sICJIZWx2ZXRpY2EiLCA5KSBm"
    "b3IgbyBpbiBvcHRpb25zKQogICAgYm94X3MgPSAzLjUqbW0KICAgIGJveF94ID0gTUFSR0lOICsg"
    "MiptbSArIG1heF93ICsgNCptbSAgIyBqdXN0IGFmdGVyIGxvbmdlc3Qgb3B0aW9uCiAgICByb3df"
    "aCA9IDcqbW0KICAgIGMuc2V0TGluZVdpZHRoKDAuNSkKICAgIGZvciBvcHQgaW4gb3B0aW9uczoK"
    "ICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgIGMuc2V0U3Ryb2tlQ29s"
    "b3JSR0IoMC40LCAwLjQsIDAuNCkKICAgICAgICBjLnJlY3QoYm94X3gsIHkgLSBib3hfcywgYm94"
    "X3MsIGJveF9zLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpE"
    "QVJLKQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAyKm1tLCB5IC0gYm94X3MgKyAxKm1t"
    "LCBvcHQpCiAgICAgICAgeSAtPSByb3dfaAogICAgcmV0dXJuIHkgLSAxKm1tCgoKZGVmIGRyYXdf"
    "dGlja192X2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KToKICAgICIiIktTMi1zdHlsZSB2"
    "ZXJ0aWNhbCB0aWNrIGxpc3Qg4oCUIGNvcnJlY3QgYW5zd2VyKHMpIHRpY2tlZC4iIiIKICAgIG5f"
    "Y29ycmVjdCA9IDEgaWYgaXNpbnN0YW5jZShjb3JyZWN0LCBzdHIpIGVsc2UgbGVuKGNvcnJlY3Qp"
    "CiAgICBpbnN0ciA9IGYiVGljayB7J29uZScgaWYgbl9jb3JyZWN0ID09IDEgZWxzZSAndHdvJ30u"
    "IgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICBjLnNldEZpbGxDb2xvclJH"
    "QigqREFSSykKICAgIGl3ID0gYy5zdHJpbmdXaWR0aChpbnN0ciwgIkhlbHZldGljYS1Cb2xkIiwg"
    "OSkKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBDVyAtIGl3LCB5LCBpbnN0cikKICAgIHkgLT0g"
    "Ni41Km1tCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICBtYXhfdyA9IG1heChjLnN0"
    "cmluZ1dpZHRoKG8sICJIZWx2ZXRpY2EiLCA5KSBmb3IgbyBpbiBvcHRpb25zKQogICAgY29ycmVj"
    "dF9saXN0ID0gW2NvcnJlY3RdIGlmIGlzaW5zdGFuY2UoY29ycmVjdCwgc3RyKSBlbHNlIGxpc3Qo"
    "Y29ycmVjdCkKICAgIGJveF9zID0gMy41Km1tCiAgICBib3hfeCA9IE1BUkdJTiArIDIqbW0gKyBt"
    "YXhfdyArIDQqbW0KICAgIHJvd19oID0gNyptbQogICAgYy5zZXRMaW5lV2lkdGgoMC41KQogICAg"
    "Zm9yIG9wdCBpbiBvcHRpb25zOgogICAgICAgIGlzX2NvcnJlY3QgPSBvcHQgaW4gY29ycmVjdF9s"
    "aXN0CiAgICAgICAgYnggPSBib3hfeAogICAgICAgIGlmIGlzX2NvcnJlY3Q6CiAgICAgICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpCiAgICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JS"
    "R0IoKkJPWF9CT1JERVIpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JS"
    "R0IoMSwgMSwgMSkKICAgICAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjQsIDAuNCwgMC40"
    "KQogICAgICAgIGMucmVjdChieCwgeSAtIGJveF9zLCBib3hfcywgYm94X3MsIGZpbGw9MSwgc3Ry"
    "b2tlPTEpCiAgICAgICAgaWYgaXNfY29ycmVjdDoKICAgICAgICAgICAgYy5zZXRTdHJva2VDb2xv"
    "clJHQigqQk9YX0JPUkRFUikKICAgICAgICAgICAgYy5zZXRMaW5lV2lkdGgoMSkKICAgICAgICAg"
    "ICAgYy5saW5lKGJ4ICsgMC41Km1tLCB5IC0gYm94X3MgKyAxLjgqbW0sIGJ4ICsgMS4zKm1tLCB5"
    "IC0gYm94X3MgKyAwLjcqbW0pCiAgICAgICAgICAgIGMubGluZShieCArIDEuMyptbSwgeSAtIGJv"
    "eF9zICsgMC43Km1tLCBieCArIDMqbW0sIHkgLSBib3hfcyArIDIuOCptbSkKICAgICAgICAgICAg"
    "Yy5zZXRMaW5lV2lkdGgoMC41KQogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JP"
    "UkRFUikKICAgICAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICAgICAg"
    "ZWxzZToKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgIGMu"
    "c2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMipt"
    "bSwgeSAtIGJveF9zICsgMSptbSwgb3B0KQogICAgICAgIHkgLT0gcm93X2gKICAgIHJldHVybiB5"
    "IC0gMSptbQoKCmRlZiBkcmF3X2ltcHJfZXZpZGVuY2VfcHVwaWwoYywgbl9yb3dzLCB5KToKICAg"
    "ICIiIkltcHJlc3Npb24vRXZpZGVuY2UgMi1jb2x1bW4gd3JpdGUtaW4gdGFibGUgKEtTMiBRMzgg"
    "c3R5bGUpLiIiIgogICAgaGRyX2ggPSA5Km1tCiAgICByb3dfaCA9IDM0Km1tCiAgICBjb2xfaSA9"
    "IENXICogMC40MAogICAgY29sX2UgPSBDVyAqIDAuNjAKICAgIGdhcF9sID0gNyptbQogICAgYy5z"
    "ZXRMaW5lV2lkdGgoMC41KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CRykKICAgIGMuc2V0"
    "U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgIGMucmVjdChNQVJHSU4sICAgICAgICAgeSAt"
    "IGhkcl9oLCBjb2xfaSwgaGRyX2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICBjLnJlY3QoTUFSR0lO"
    "ICsgY29sX2ksIHkgLSBoZHJfaCwgY29sX2UsIGhkcl9oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAg"
    "Yy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwg"
    "MTApCiAgICBjLmRyYXdDZW50cmVkU3RyaW5nKE1BUkdJTiArIGNvbF9pIC8gMiwgICAgICAgICB5"
    "IC0gaGRyX2ggKyAzKm1tLCAiSW1wcmVzc2lvbiIpCiAgICBjLmRyYXdDZW50cmVkU3RyaW5nKE1B"
    "UkdJTiArIGNvbF9pICsgY29sX2UgLyAyLCB5IC0gaGRyX2ggKyAzKm1tLCAiRXZpZGVuY2UiKQog"
    "ICAgeSAtPSBoZHJfaAogICAgZm9yIF8gaW4gcmFuZ2Uobl9yb3dzKToKICAgICAgICBjLnNldEZp"
    "bGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElO"
    "RSkKICAgICAgICBjLnJlY3QoTUFSR0lOLCAgICAgICAgIHkgLSByb3dfaCwgY29sX2ksIHJvd19o"
    "LCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMucmVjdChNQVJHSU4gKyBjb2xfaSwgeSAtIHJv"
    "d19oLCBjb2xfZSwgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRTdHJva2VD"
    "b2xvclJHQigqR1JFWV9MSU5FKQogICAgICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICAgICBs"
    "eV9pID0geSAtIHJvd19oICsgOSptbQogICAgICAgIGMubGluZShNQVJHSU4gKyAzKm1tLCBseV9p"
    "LCBNQVJHSU4gKyBjb2xfaSAtIDMqbW0sIGx5X2kpCiAgICAgICAgZm9yIGsgaW4gcmFuZ2UoMyk6"
    "CiAgICAgICAgICAgIGx5X2UgPSB5IC0gcm93X2ggKyA5Km1tICsgayAqIGdhcF9sCiAgICAgICAg"
    "ICAgIGMubGluZShNQVJHSU4gKyBjb2xfaSArIDMqbW0sIGx5X2UsIE1BUkdJTiArIENXIC0gMypt"
    "bSwgbHlfZSkKICAgICAgICB5IC09IHJvd19oCiAgICByZXR1cm4geSAtIDIqbW0KCgpkZWYgZHJh"
    "d19pbXByX2V2aWRlbmNlX2Fuc3dlcihjLCBwYWlycywgeSk6CiAgICAiIiJJbXByZXNzaW9uL0V2"
    "aWRlbmNlIHRhYmxlIHdpdGggYW5zd2VyIHRleHQuIiIiCiAgICBoZHJfaCA9IDkqbW0KICAgIHJv"
    "d19oID0gMzQqbW0KICAgIGNvbF9pID0gQ1cgKiAwLjQwCiAgICBjb2xfZSA9IENXICogMC42MAog"
    "ICAgZ2FwX2wgPSA3Km1tCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLnNldEZpbGxDb2xv"
    "clJHQigqQk9YX0JHKQogICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAgYy5y"
    "ZWN0KE1BUkdJTiwgICAgICAgICB5IC0gaGRyX2gsIGNvbF9pLCBoZHJfaCwgZmlsbD0xLCBzdHJv"
    "a2U9MSkKICAgIGMucmVjdChNQVJHSU4gKyBjb2xfaSwgeSAtIGhkcl9oLCBjb2xfZSwgaGRyX2gs"
    "IGZpbGw9MSwgc3Ryb2tlPTEpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuc2V0"
    "Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCAxMCkKICAgIGMuZHJhd0NlbnRyZWRTdHJpbmcoTUFSR0lO"
    "ICsgY29sX2kgLyAyLCAgICAgICAgIHkgLSBoZHJfaCArIDMqbW0sICJJbXByZXNzaW9uIikKICAg"
    "IGMuZHJhd0NlbnRyZWRTdHJpbmcoTUFSR0lOICsgY29sX2kgKyBjb2xfZSAvIDIsIHkgLSBoZHJf"
    "aCArIDMqbW0sICJFdmlkZW5jZSIpCiAgICB5IC09IGhkcl9oCiAgICBmb3IgaW1wciwgZXZpZCBp"
    "biBwYWlyczoKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgIGMuc2V0"
    "U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnJlY3QoTUFSR0lOLCAgICAgICAg"
    "IHkgLSByb3dfaCwgY29sX2ksIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMucmVj"
    "dChNQVJHSU4gKyBjb2xfaSwgeSAtIHJvd19oLCBjb2xfZSwgcm93X2gsIGZpbGw9MSwgc3Ryb2tl"
    "PTEpCiAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAgICAgIGMuc2V0"
    "TGluZVdpZHRoKDAuNCkKICAgICAgICBseV9pID0geSAtIHJvd19oICsgOSptbQogICAgICAgIGMu"
    "bGluZShNQVJHSU4gKyAzKm1tLCBseV9pLCBNQVJHSU4gKyBjb2xfaSAtIDMqbW0sIGx5X2kpCiAg"
    "ICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0"
    "aWNhLU9ibGlxdWUiLCA4LjUpCiAgICAgICAgZm9yIGssIGlsIGluIGVudW1lcmF0ZSh3cmFwX3Rl"
    "eHQoYywgaW1wciwgIkhlbHZldGljYS1PYmxpcXVlIiwgOC41LCBjb2xfaSAtIDYqbW0pWzoyXSk6"
    "CiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAzKm1tLCBseV9pICsgMSptbSArIGsg"
    "KiA1Km1tLCBpbCkKICAgICAgICBmb3IgayBpbiByYW5nZSgzKToKICAgICAgICAgICAgbHlfZSA9"
    "IHkgLSByb3dfaCArIDkqbW0gKyBrICogZ2FwX2wKICAgICAgICAgICAgYy5zZXRTdHJva2VDb2xv"
    "clJHQigqR1JFWV9MSU5FKQogICAgICAgICAgICBjLmxpbmUoTUFSR0lOICsgY29sX2kgKyAzKm1t"
    "LCBseV9lLCBNQVJHSU4gKyBDVyAtIDMqbW0sIGx5X2UpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JS"
    "R0IoKkdSRUVOKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLU9ibGlxdWUiLCA4LjUpCiAg"
    "ICAgICAgZm9yIGssIGVsIGluIGVudW1lcmF0ZSh3cmFwX3RleHQoYywgZXZpZCwgIkhlbHZldGlj"
    "YS1PYmxpcXVlIiwgOC41LCBjb2xfZSAtIDYqbW0pWzozXSk6CiAgICAgICAgICAgIGx5X2UgPSB5"
    "IC0gcm93X2ggKyA5Km1tICsgayAqIGdhcF9sCiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJH"
    "SU4gKyBjb2xfaSArIDMqbW0sIGx5X2UgKyAxKm1tLCBlbCkKICAgICAgICB5IC09IHJvd19oCiAg"
    "ICByZXR1cm4geSAtIDIqbW0KCgoKZGVmIGRyYXdfYXR0cmliX3RhYmxlX3B1cGlsKGMsIG9wdGlv"
    "bnMsIHkpOgogICAgIiIiQXR0cmlidXRpb24gdGFibGUg4oCUIHRpY2sgb25lIGNvbHVtbiBwZXIg"
    "cm93LiBLUzIgUTggKEphbWVzL01hbmR5KSBzdHlsZS4KICAgIG9wdGlvbnNbMF0gPSBsaXN0IG9m"
    "IGNvbHVtbiBoZWFkZXIgc3RyaW5nczsgb3B0aW9uc1sxOl0gPSBzdGF0ZW1lbnQgcm93cy4iIiIK"
    "ICAgIGhlYWRlcnMgPSBvcHRpb25zWzBdCiAgICByb3dzICAgID0gb3B0aW9uc1sxOl0KICAgIGNv"
    "bF9zdG10ID0gQ1cgKiAwLjYyCiAgICBuX2NvbHMgICA9IGxlbihoZWFkZXJzKQogICAgY29sX3cg"
    "ICAgPSAoQ1cgLSBjb2xfc3RtdCkgLyBuX2NvbHMKICAgIGhkcl9oICAgID0gOCptbQogICAgcm93"
    "X2ggICAgPSA5Km1tCiAgICBib3hfcyAgICA9IDMqbW0KICAgIGMuc2V0TGluZVdpZHRoKDAuNSkK"
    "ICAgICMgRHJhdyBoZWFkZXIgY2VsbHMgKHJpZ2h0IHNpZGUgb25seSDigJQgbGVmdCBjZWxsIGJs"
    "YW5rKQogICAgZm9yIGksIGhkciBpbiBlbnVtZXJhdGUoaGVhZGVycyk6CiAgICAgICAgaHggPSBN"
    "QVJHSU4gKyBjb2xfc3RtdCArIGkgKiBjb2xfdwogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpC"
    "T1hfQkcpCiAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAgICAgIGMu"
    "cmVjdChoeCwgeSAtIGhkcl9oLCBjb2xfdywgaGRyX2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAg"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2Et"
    "Qm9sZCIsIDkpCiAgICAgICAgYy5kcmF3Q2VudHJlZFN0cmluZyhoeCArIGNvbF93IC8gMiwgeSAt"
    "IGhkcl9oICsgMi41Km1tLCBoZHIpCiAgICB5IC09IGhkcl9oCiAgICBmb3IgaSwgc3RtdCBpbiBl"
    "bnVtZXJhdGUocm93cyk6CiAgICAgICAgZmlsbCA9ICgwLjk2LCAwLjk2LCAwLjk2KSBpZiBpICUg"
    "MiA9PSAwIGVsc2UgKDEsIDEsIDEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKmZpbGwpCiAg"
    "ICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAgICAgIGMucmVjdChNQVJH"
    "SU4sIHkgLSByb3dfaCwgY29sX3N0bXQsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAgICAgICAgZm9yIGogaW4gcmFuZ2Uobl9jb2xz"
    "KToKICAgICAgICAgICAgYy5yZWN0KE1BUkdJTiArIGNvbF9zdG10ICsgaiAqIGNvbF93LCB5IC0g"
    "cm93X2gsIGNvbF93LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxD"
    "b2xvclJHQigqREFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAg"
    "c3RtdF9saW5lcyA9IHdyYXBfdGV4dChjLCBzdG10LCAiSGVsdmV0aWNhIiwgOSwgY29sX3N0bXQg"
    "LSA0Km1tKQogICAgICAgIGZvciBrLCBzbCBpbiBlbnVtZXJhdGUoc3RtdF9saW5lc1s6Ml0pOgog"
    "ICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMiptbSwgeSAtIDMuNSptbSAtIGsgKiA0"
    "LjUqbW0sIHNsKQogICAgICAgIGZvciBqIGluIHJhbmdlKG5fY29scyk6CiAgICAgICAgICAgIGJ4"
    "ID0gTUFSR0lOICsgY29sX3N0bXQgKyBqICogY29sX3cgKyAoY29sX3cgLSBib3hfcykgLyAyCiAg"
    "ICAgICAgICAgIGJ5ID0geSAtIHJvd19oIC8gMiAtIGJveF9zIC8gMgogICAgICAgICAgICBjLnNl"
    "dEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAu"
    "NSwgMC41LCAwLjUpCiAgICAgICAgICAgIGMucmVjdChieCwgYnksIGJveF9zLCBib3hfcywgZmls"
    "bD0xLCBzdHJva2U9MSkKICAgICAgICB5IC09IHJvd19oCiAgICByZXR1cm4geSAtIDIqbW0KCgpk"
    "ZWYgZHJhd19hdHRyaWJfdGFibGVfYW5zd2VyKGMsIG9wdGlvbnMsIGNvcnJlY3RfbGlzdCwgeSk6"
    "CiAgICAiIiJBdHRyaWJ1dGlvbiB0YWJsZSB3aXRoIGNvcnJlY3QgY29sdW1uIHRpY2tlZC4iIiIK"
    "ICAgIGhlYWRlcnMgPSBvcHRpb25zWzBdCiAgICByb3dzICAgID0gb3B0aW9uc1sxOl0KICAgIGNv"
    "bF9zdG10ID0gQ1cgKiAwLjYyCiAgICBuX2NvbHMgICA9IGxlbihoZWFkZXJzKQogICAgY29sX3cg"
    "ICAgPSAoQ1cgLSBjb2xfc3RtdCkgLyBuX2NvbHMKICAgIGhkcl9oICAgID0gOCptbQogICAgcm93"
    "X2ggICAgPSA5Km1tCiAgICBib3hfcyAgICA9IDMqbW0KICAgIGMuc2V0TGluZVdpZHRoKDAuNSkK"
    "ICAgIGZvciBpLCBoZHIgaW4gZW51bWVyYXRlKGhlYWRlcnMpOgogICAgICAgIGh4ID0gTUFSR0lO"
    "ICsgY29sX3N0bXQgKyBpICogY29sX3cKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JH"
    "KQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnJlY3Qo"
    "aHgsIHkgLSBoZHJfaCwgY29sX3csIGhkcl9oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMu"
    "c2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQi"
    "LCA5KQogICAgICAgIGMuZHJhd0NlbnRyZWRTdHJpbmcoaHggKyBjb2xfdyAvIDIsIHkgLSBoZHJf"
    "aCArIDIuNSptbSwgaGRyKQogICAgeSAtPSBoZHJfaAogICAgZm9yIGksIChzdG10LCBjb3JyZWN0"
    "X2hkcikgaW4gZW51bWVyYXRlKHppcChyb3dzLCBjb3JyZWN0X2xpc3QpKToKICAgICAgICBmaWxs"
    "ID0gKDAuOTYsIDAuOTYsIDAuOTYpIGlmIGkgJSAyID09IDAgZWxzZSAoMSwgMSwgMSkKICAgICAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigqZmlsbCkKICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpH"
    "UkVZX0xJTkUpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgeSAtIHJvd19oLCBjb2xfc3RtdCwgcm93"
    "X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkK"
    "ICAgICAgICBmb3IgaiBpbiByYW5nZShuX2NvbHMpOgogICAgICAgICAgICBjLnJlY3QoTUFSR0lO"
    "ICsgY29sX3N0bXQgKyBqICogY29sX3csIHkgLSByb3dfaCwgY29sX3csIHJvd19oLCBmaWxsPTEs"
    "IHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0"
    "Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgICAgICBzdG10X2xpbmVzID0gd3JhcF90ZXh0KGMsIHN0"
    "bXQsICJIZWx2ZXRpY2EiLCA5LCBjb2xfc3RtdCAtIDQqbW0pCiAgICAgICAgZm9yIGssIHNsIGlu"
    "IGVudW1lcmF0ZShzdG10X2xpbmVzWzoyXSk6CiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJH"
    "SU4gKyAyKm1tLCB5IC0gMy41Km1tIC0gayAqIDQuNSptbSwgc2wpCiAgICAgICAgZm9yIGosIGhk"
    "ciBpbiBlbnVtZXJhdGUoaGVhZGVycyk6CiAgICAgICAgICAgIGJ4ID0gTUFSR0lOICsgY29sX3N0"
    "bXQgKyBqICogY29sX3cgKyAoY29sX3cgLSBib3hfcykgLyAyCiAgICAgICAgICAgIGJ5ID0geSAt"
    "IHJvd19oIC8gMiAtIGJveF9zIC8gMgogICAgICAgICAgICBpc19jb3JyZWN0ID0gKGhkciA9PSBj"
    "b3JyZWN0X2hkcikKICAgICAgICAgICAgaWYgaXNfY29ycmVjdDoKICAgICAgICAgICAgICAgIGMu"
    "c2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpOyBjLnNldFN0cm9rZUNvbG9yUkdCKCpCT1hfQk9SREVS"
    "KQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwg"
    "MSwgMSk7IGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC41LCAwLjUsIDAuNSkKICAgICAgICAgICAgYy5y"
    "ZWN0KGJ4LCBieSwgYm94X3MsIGJveF9zLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgICAgICBp"
    "ZiBpc19jb3JyZWN0OgogICAgICAgICAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JP"
    "UkRFUik7IGMuc2V0TGluZVdpZHRoKDEpCiAgICAgICAgICAgICAgICBjLmxpbmUoYngrMC40Km1t"
    "LCBieSsxLjYqbW0sIGJ4KzEuMSptbSwgYnkrMC42Km1tKQogICAgICAgICAgICAgICAgYy5saW5l"
    "KGJ4KzEuMSptbSwgYnkrMC42Km1tLCBieCsyLjcqbW0sIGJ5KzIuNCptbSkKICAgICAgICAgICAg"
    "ICAgIGMuc2V0TGluZVdpZHRoKDAuNSkKICAgICAgICB5IC09IHJvd19oCiAgICByZXR1cm4geSAt"
    "IDIqbW0KCgpkZWYgZHJhd19pbXByX2V2aWRlbmNlX3B1cGlsKGMsIG5fcm93cywgeSk6CiAgICAi"
    "IiJJbXByZXNzaW9uL0V2aWRlbmNlIDItY29sdW1uIHdyaXRlLWluIHRhYmxlIChLUzIgUTM4IHN0"
    "eWxlKS4iIiIKICAgIGhkcl9oID0gOSptbQogICAgcm93X2ggPSAzNCptbQogICAgY29sX2kgPSBD"
    "VyAqIDAuNDAKICAgIGNvbF9lID0gQ1cgKiAwLjYwCiAgICBnYXBfbCA9IDcqbW0KICAgIGMuc2V0"
    "TGluZVdpZHRoKDAuNSkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpCiAgICBjLnNldFN0"
    "cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnJlY3QoTUFSR0lOLCAgICAgICAgIHkgLSBo"
    "ZHJfaCwgY29sX2ksIGhkcl9oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgYy5yZWN0KE1BUkdJTiAr"
    "IGNvbF9pLCB5IC0gaGRyX2gsIGNvbF9lLCBoZHJfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgIGMu"
    "c2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDEw"
    "KQogICAgYy5kcmF3Q2VudHJlZFN0cmluZyhNQVJHSU4gKyBjb2xfaSAvIDIsICAgICAgICAgeSAt"
    "IGhkcl9oICsgMyptbSwgIkltcHJlc3Npb24iKQogICAgYy5kcmF3Q2VudHJlZFN0cmluZyhNQVJH"
    "SU4gKyBjb2xfaSArIGNvbF9lIC8gMiwgeSAtIGhkcl9oICsgMyptbSwgIkV2aWRlbmNlIikKICAg"
    "IHkgLT0gaGRyX2gKICAgIGZvciBfIGluIHJhbmdlKG5fcm93cyk6CiAgICAgICAgYy5zZXRGaWxs"
    "Q29sb3JSR0IoMSwgMSwgMSkKICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUp"
    "CiAgICAgICAgYy5yZWN0KE1BUkdJTiwgICAgICAgICB5IC0gcm93X2gsIGNvbF9pLCByb3dfaCwg"
    "ZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnJlY3QoTUFSR0lOICsgY29sX2ksIHkgLSByb3df"
    "aCwgY29sX2UsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0U3Ryb2tlQ29s"
    "b3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICAgICAgbHlf"
    "aSA9IHkgLSByb3dfaCArIDkqbW0KICAgICAgICBjLmxpbmUoTUFSR0lOICsgMyptbSwgbHlfaSwg"
    "TUFSR0lOICsgY29sX2kgLSAzKm1tLCBseV9pKQogICAgICAgIGZvciBrIGluIHJhbmdlKDMpOgog"
    "ICAgICAgICAgICBseV9lID0geSAtIHJvd19oICsgOSptbSArIGsgKiBnYXBfbAogICAgICAgICAg"
    "ICBjLmxpbmUoTUFSR0lOICsgY29sX2kgKyAzKm1tLCBseV9lLCBNQVJHSU4gKyBDVyAtIDMqbW0s"
    "IGx5X2UpCiAgICAgICAgeSAtPSByb3dfaAogICAgcmV0dXJuIHkgLSAyKm1tCgoKZGVmIGRyYXdf"
    "aW1wcl9ldmlkZW5jZV9hbnN3ZXIoYywgcGFpcnMsIHkpOgogICAgIiIiSW1wcmVzc2lvbi9Fdmlk"
    "ZW5jZSB0YWJsZSB3aXRoIGFuc3dlciB0ZXh0LiIiIgogICAgaGRyX2ggPSA5Km1tCiAgICByb3df"
    "aCA9IDM0Km1tCiAgICBjb2xfaSA9IENXICogMC40MAogICAgY29sX2UgPSBDVyAqIDAuNjAKICAg"
    "IGdhcF9sID0gNyptbQogICAgYy5zZXRMaW5lV2lkdGgoMC41KQogICAgYy5zZXRGaWxsQ29sb3JS"
    "R0IoKkJPWF9CRykKICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgIGMucmVj"
    "dChNQVJHSU4sICAgICAgICAgeSAtIGhkcl9oLCBjb2xfaSwgaGRyX2gsIGZpbGw9MSwgc3Ryb2tl"
    "PTEpCiAgICBjLnJlY3QoTUFSR0lOICsgY29sX2ksIHkgLSBoZHJfaCwgY29sX2UsIGhkcl9oLCBm"
    "aWxsPTEsIHN0cm9rZT0xKQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLnNldEZv"
    "bnQoIkhlbHZldGljYS1Cb2xkIiwgMTApCiAgICBjLmRyYXdDZW50cmVkU3RyaW5nKE1BUkdJTiAr"
    "IGNvbF9pIC8gMiwgICAgICAgICB5IC0gaGRyX2ggKyAzKm1tLCAiSW1wcmVzc2lvbiIpCiAgICBj"
    "LmRyYXdDZW50cmVkU3RyaW5nKE1BUkdJTiArIGNvbF9pICsgY29sX2UgLyAyLCB5IC0gaGRyX2gg"
    "KyAzKm1tLCAiRXZpZGVuY2UiKQogICAgeSAtPSBoZHJfaAogICAgZm9yIGltcHIsIGV2aWQgaW4g"
    "cGFpcnM6CiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAgICBjLnNldFN0"
    "cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgICAgICAgICB5"
    "IC0gcm93X2gsIGNvbF9pLCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnJlY3Qo"
    "TUFSR0lOICsgY29sX2ksIHkgLSByb3dfaCwgY29sX2UsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0x"
    "KQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnNldExp"
    "bmVXaWR0aCgwLjQpCiAgICAgICAgbHlfaSA9IHkgLSByb3dfaCArIDkqbW0KICAgICAgICBjLmxp"
    "bmUoTUFSR0lOICsgMyptbSwgbHlfaSwgTUFSR0lOICsgY29sX2kgLSAzKm1tLCBseV9pKQogICAg"
    "ICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGlj"
    "YS1PYmxpcXVlIiwgOC41KQogICAgICAgIGZvciBrLCBpbCBpbiBlbnVtZXJhdGUod3JhcF90ZXh0"
    "KGMsIGltcHIsICJIZWx2ZXRpY2EtT2JsaXF1ZSIsIDguNSwgY29sX2kgLSA2Km1tKVs6Ml0pOgog"
    "ICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMyptbSwgbHlfaSArIDEqbW0gKyBrICog"
    "NSptbSwgaWwpCiAgICAgICAgZm9yIGsgaW4gcmFuZ2UoMyk6CiAgICAgICAgICAgIGx5X2UgPSB5"
    "IC0gcm93X2ggKyA5Km1tICsgayAqIGdhcF9sCiAgICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JS"
    "R0IoKkdSRVlfTElORSkKICAgICAgICAgICAgYy5saW5lKE1BUkdJTiArIGNvbF9pICsgMyptbSwg"
    "bHlfZSwgTUFSR0lOICsgQ1cgLSAzKm1tLCBseV9lKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1PYmxpcXVlIiwgOC41KQogICAg"
    "ICAgIGZvciBrLCBlbCBpbiBlbnVtZXJhdGUod3JhcF90ZXh0KGMsIGV2aWQsICJIZWx2ZXRpY2Et"
    "T2JsaXF1ZSIsIDguNSwgY29sX2UgLSA2Km1tKVs6M10pOgogICAgICAgICAgICBseV9lID0geSAt"
    "IHJvd19oICsgOSptbSArIGsgKiBnYXBfbAogICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lO"
    "ICsgY29sX2kgKyAzKm1tLCBseV9lICsgMSptbSwgZWwpCiAgICAgICAgeSAtPSByb3dfaAogICAg"
    "cmV0dXJuIHkgLSAyKm1tCgoKCmRlZiBkcmF3X2F0dHJpYl90YWJsZV9wdXBpbChjLCBvcHRpb25z"
    "LCB5KToKICAgICIiIkF0dHJpYnV0aW9uIHRhYmxlIOKAlCB0aWNrIG9uZSBjb2x1bW4gcGVyIHJv"
    "dy4gS1MyIFE4IChKYW1lcy9NYW5keSkgc3R5bGUuCiAgICBvcHRpb25zWzBdID0gbGlzdCBvZiBj"
    "b2x1bW4gaGVhZGVyIHN0cmluZ3M7IG9wdGlvbnNbMTpdID0gc3RhdGVtZW50IHJvd3MuIiIiCiAg"
    "ICBoZWFkZXJzID0gb3B0aW9uc1swXQogICAgcm93cyAgICA9IG9wdGlvbnNbMTpdCiAgICBjb2xf"
    "c3RtdCA9IENXICogMC42MgogICAgbl9jb2xzICAgPSBsZW4oaGVhZGVycykKICAgIGNvbF93ICAg"
    "ID0gKENXIC0gY29sX3N0bXQpIC8gbl9jb2xzCiAgICBoZHJfaCAgICA9IDgqbW0KICAgIHJvd19o"
    "ICAgID0gOSptbQogICAgYm94X3MgICAgPSAzKm1tCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAg"
    "ICAjIERyYXcgaGVhZGVyIGNlbGxzIChyaWdodCBzaWRlIG9ubHkg4oCUIGxlZnQgY2VsbCBibGFu"
    "aykKICAgIGZvciBpLCBoZHIgaW4gZW51bWVyYXRlKGhlYWRlcnMpOgogICAgICAgIGh4ID0gTUFS"
    "R0lOICsgY29sX3N0bXQgKyBpICogY29sX3cKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9Y"
    "X0JHKQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnJl"
    "Y3QoaHgsIHkgLSBoZHJfaCwgY29sX3csIGhkcl9oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJv"
    "bGQiLCA5KQogICAgICAgIGMuZHJhd0NlbnRyZWRTdHJpbmcoaHggKyBjb2xfdyAvIDIsIHkgLSBo"
    "ZHJfaCArIDIuNSptbSwgaGRyKQogICAgeSAtPSBoZHJfaAogICAgZm9yIGksIHN0bXQgaW4gZW51"
    "bWVyYXRlKHJvd3MpOgogICAgICAgIGZpbGwgPSAoMC45NiwgMC45NiwgMC45NikgaWYgaSAlIDIg"
    "PT0gMCBlbHNlICgxLCAxLCAxKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpmaWxsKQogICAg"
    "ICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICBjLnJlY3QoTUFSR0lO"
    "LCB5IC0gcm93X2gsIGNvbF9zdG10LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBj"
    "LnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgIGZvciBqIGluIHJhbmdlKG5fY29scyk6"
    "CiAgICAgICAgICAgIGMucmVjdChNQVJHSU4gKyBjb2xfc3RtdCArIGogKiBjb2xfdywgeSAtIHJv"
    "d19oLCBjb2xfdywgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRGaWxsQ29s"
    "b3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgICAgIHN0"
    "bXRfbGluZXMgPSB3cmFwX3RleHQoYywgc3RtdCwgIkhlbHZldGljYSIsIDksIGNvbF9zdG10IC0g"
    "NCptbSkKICAgICAgICBmb3Igaywgc2wgaW4gZW51bWVyYXRlKHN0bXRfbGluZXNbOjJdKToKICAg"
    "ICAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIDIqbW0sIHkgLSAzLjUqbW0gLSBrICogNC41"
    "Km1tLCBzbCkKICAgICAgICBmb3IgaiBpbiByYW5nZShuX2NvbHMpOgogICAgICAgICAgICBieCA9"
    "IE1BUkdJTiArIGNvbF9zdG10ICsgaiAqIGNvbF93ICsgKGNvbF93IC0gYm94X3MpIC8gMgogICAg"
    "ICAgICAgICBieSA9IHkgLSByb3dfaCAvIDIgLSBib3hfcyAvIDIKICAgICAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjUs"
    "IDAuNSwgMC41KQogICAgICAgICAgICBjLnJlY3QoYngsIGJ5LCBib3hfcywgYm94X3MsIGZpbGw9"
    "MSwgc3Ryb2tlPTEpCiAgICAgICAgeSAtPSByb3dfaAogICAgcmV0dXJuIHkgLSAyKm1tCgoKZGVm"
    "IGRyYXdfYXR0cmliX3RhYmxlX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0X2xpc3QsIHkpOgog"
    "ICAgIiIiQXR0cmlidXRpb24gdGFibGUgd2l0aCBjb3JyZWN0IGNvbHVtbiB0aWNrZWQuIiIiCiAg"
    "ICBoZWFkZXJzID0gb3B0aW9uc1swXQogICAgcm93cyAgICA9IG9wdGlvbnNbMTpdCiAgICBjb2xf"
    "c3RtdCA9IENXICogMC42MgogICAgbl9jb2xzICAgPSBsZW4oaGVhZGVycykKICAgIGNvbF93ICAg"
    "ID0gKENXIC0gY29sX3N0bXQpIC8gbl9jb2xzCiAgICBoZHJfaCAgICA9IDgqbW0KICAgIHJvd19o"
    "ICAgID0gOSptbQogICAgYm94X3MgICAgPSAzKm1tCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAg"
    "ICBmb3IgaSwgaGRyIGluIGVudW1lcmF0ZShoZWFkZXJzKToKICAgICAgICBoeCA9IE1BUkdJTiAr"
    "IGNvbF9zdG10ICsgaSAqIGNvbF93CiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CRykK"
    "ICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICAgICAgYy5yZWN0KGh4"
    "LCB5IC0gaGRyX2gsIGNvbF93LCBoZHJfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNl"
    "dEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwg"
    "OSkKICAgICAgICBjLmRyYXdDZW50cmVkU3RyaW5nKGh4ICsgY29sX3cgLyAyLCB5IC0gaGRyX2gg"
    "KyAyLjUqbW0sIGhkcikKICAgIHkgLT0gaGRyX2gKICAgIGZvciBpLCAoc3RtdCwgY29ycmVjdF9o"
    "ZHIpIGluIGVudW1lcmF0ZSh6aXAocm93cywgY29ycmVjdF9saXN0KSk6CiAgICAgICAgZmlsbCA9"
    "ICgwLjk2LCAwLjk2LCAwLjk2KSBpZiBpICUgMiA9PSAwIGVsc2UgKDEsIDEsIDEpCiAgICAgICAg"
    "Yy5zZXRGaWxsQ29sb3JSR0IoKmZpbGwpCiAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JF"
    "WV9MSU5FKQogICAgICAgIGMucmVjdChNQVJHSU4sIHkgLSByb3dfaCwgY29sX3N0bXQsIHJvd19o"
    "LCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAg"
    "ICAgICAgZm9yIGogaW4gcmFuZ2Uobl9jb2xzKToKICAgICAgICAgICAgYy5yZWN0KE1BUkdJTiAr"
    "IGNvbF9zdG10ICsgaiAqIGNvbF93LCB5IC0gcm93X2gsIGNvbF93LCByb3dfaCwgZmlsbD0xLCBz"
    "dHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICBjLnNldEZv"
    "bnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAgc3RtdF9saW5lcyA9IHdyYXBfdGV4dChjLCBzdG10"
    "LCAiSGVsdmV0aWNhIiwgOSwgY29sX3N0bXQgLSA0Km1tKQogICAgICAgIGZvciBrLCBzbCBpbiBl"
    "bnVtZXJhdGUoc3RtdF9saW5lc1s6Ml0pOgogICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lO"
    "ICsgMiptbSwgeSAtIDMuNSptbSAtIGsgKiA0LjUqbW0sIHNsKQogICAgICAgIGZvciBqLCBoZHIg"
    "aW4gZW51bWVyYXRlKGhlYWRlcnMpOgogICAgICAgICAgICBieCA9IE1BUkdJTiArIGNvbF9zdG10"
    "ICsgaiAqIGNvbF93ICsgKGNvbF93IC0gYm94X3MpIC8gMgogICAgICAgICAgICBieSA9IHkgLSBy"
    "b3dfaCAvIDIgLSBib3hfcyAvIDIKICAgICAgICAgICAgaXNfY29ycmVjdCA9IChoZHIgPT0gY29y"
    "cmVjdF9oZHIpCiAgICAgICAgICAgIGlmIGlzX2NvcnJlY3Q6CiAgICAgICAgICAgICAgICBjLnNl"
    "dEZpbGxDb2xvclJHQigqQk9YX0JHKTsgYy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikK"
    "ICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEs"
    "IDEpOyBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNSwgMC41LCAwLjUpCiAgICAgICAgICAgIGMucmVj"
    "dChieCwgYnksIGJveF9zLCBib3hfcywgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICAgICAgaWYg"
    "aXNfY29ycmVjdDoKICAgICAgICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkJPWF9CT1JE"
    "RVIpOyBjLnNldExpbmVXaWR0aCgxKQogICAgICAgICAgICAgICAgYy5saW5lKGJ4KzAuNCptbSwg"
    "YnkrMS42Km1tLCBieCsxLjEqbW0sIGJ5KzAuNiptbSkKICAgICAgICAgICAgICAgIGMubGluZShi"
    "eCsxLjEqbW0sIGJ5KzAuNiptbSwgYngrMi43Km1tLCBieSsyLjQqbW0pCiAgICAgICAgICAgICAg"
    "ICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICAgICAgeSAtPSByb3dfaAogICAgcmV0dXJuIHkgLSAy"
    "Km1tCgoKZGVmIGRyYXdfdGZfdGFibGVfcHVwaWwoYywgc3RhdGVtZW50cywgeSk6CiAgICAiIiJU"
    "cnVlL0ZhbHNlIG11bHRpLXN0YXRlbWVudCB0YWJsZSDigJQgS1MyIFEyMCBzdHlsZS4iIiIKICAg"
    "IGNvbF9zdG10ID0gQ1cgKiAwLjcyCiAgICBjb2xfdGYgICA9IENXICogMC4xNAogICAgaGRyX2gg"
    "ICAgPSA3Km1tCiAgICByb3dfaCAgICA9IDkqbW0KICAgIGJveF9zICAgID0gMyptbQogICAgYy5z"
    "ZXRMaW5lV2lkdGgoMC41KQogICAgIyBIZWFkZXIKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpCT1hf"
    "QkcpCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnJlY3QoTUFSR0lO"
    "ICsgY29sX3N0bXQsIHkgLSBoZHJfaCwgY29sX3RmICogMiwgaGRyX2gsIGZpbGw9MSwgc3Ryb2tl"
    "PTEpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNh"
    "LUJvbGQiLCA4LjUpCiAgICBjLmRyYXdDZW50cmVkU3RyaW5nKE1BUkdJTiArIGNvbF9zdG10ICsg"
    "Y29sX3RmIC8gMiwgICAgICAgIHkgLSBoZHJfaCArIDIuNSptbSwgIlRydWUiKQogICAgYy5kcmF3"
    "Q2VudHJlZFN0cmluZyhNQVJHSU4gKyBjb2xfc3RtdCArIGNvbF90ZiAqIDEuNSwgICAgICB5IC0g"
    "aGRyX2ggKyAyLjUqbW0sICJGYWxzZSIpCiAgICB5IC09IGhkcl9oCiAgICBmb3IgaSwgc3RtdCBp"
    "biBlbnVtZXJhdGUoc3RhdGVtZW50cyk6CiAgICAgICAgZmlsbF9iZyA9ICgwLjk3LCAwLjk3LCAw"
    "Ljk3KSBpZiBpICUgMiA9PSAwIGVsc2UgKDEsIDEsIDEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JS"
    "R0IoKmZpbGxfYmcpCiAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAg"
    "ICAgIGMucmVjdChNQVJHSU4sIHkgLSByb3dfaCwgY29sX3N0bXQsIHJvd19oLCBmaWxsPTEsIHN0"
    "cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAgICAgICAgYy5yZWN0"
    "KE1BUkdJTiArIGNvbF9zdG10LCB5IC0gcm93X2gsIGNvbF90ZiAqIDIsIHJvd19oLCBmaWxsPTEs"
    "IHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0"
    "Rm9udCgiSGVsdmV0aWNhIiwgOC41KQogICAgICAgIHN0bXRfbGluZXMgPSB3cmFwX3RleHQoYywg"
    "c3RtdCwgIkhlbHZldGljYSIsIDguNSwgY29sX3N0bXQgLSA0Km1tKQogICAgICAgIGZvciBqLCBz"
    "bCBpbiBlbnVtZXJhdGUoc3RtdF9saW5lc1s6Ml0pOgogICAgICAgICAgICBjLmRyYXdTdHJpbmco"
    "TUFSR0lOICsgMiptbSwgeSAtIDMuNSptbSAtIGogKiA0LjUqbW0sIHNsKQogICAgICAgIGZvciBr"
    "IGluIHJhbmdlKDIpOgogICAgICAgICAgICBieCA9IE1BUkdJTiArIGNvbF9zdG10ICsgayAqIGNv"
    "bF90ZiArIChjb2xfdGYgLSBib3hfcykgLyAyCiAgICAgICAgICAgIGJ5ID0geSAtIHJvd19oIC8g"
    "MiAtIGJveF9zIC8gMgogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAg"
    "ICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNSwgMC41LCAwLjUpCiAgICAgICAgICAgIGMu"
    "cmVjdChieCwgYnksIGJveF9zLCBib3hfcywgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICB5IC09"
    "IHJvd19oCiAgICByZXR1cm4geSAtIDIqbW0KCgpkZWYgZHJhd190Zl90YWJsZV9hbnN3ZXIoYywg"
    "c3RhdGVtZW50cywgY29ycmVjdF9saXN0LCB5KToKICAgICIiIlRydWUvRmFsc2UgdGFibGUg4oCU"
    "IGNvcnJlY3QgYm94ZXMgdGlja2VkLiIiIgogICAgY29sX3N0bXQgPSBDVyAqIDAuNzIKICAgIGNv"
    "bF90ZiAgID0gQ1cgKiAwLjE0CiAgICBoZHJfaCAgICA9IDcqbW0KICAgIHJvd19oICAgID0gOSpt"
    "bQogICAgYm94X3MgICAgPSAzKm1tCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLnNldEZp"
    "bGxDb2xvclJHQigqQk9YX0JHKQogICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQog"
    "ICAgYy5yZWN0KE1BUkdJTiArIGNvbF9zdG10LCB5IC0gaGRyX2gsIGNvbF90ZiAqIDIsIGhkcl9o"
    "LCBmaWxsPTEsIHN0cm9rZT0xKQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLnNl"
    "dEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOC41KQogICAgYy5kcmF3Q2VudHJlZFN0cmluZyhNQVJH"
    "SU4gKyBjb2xfc3RtdCArIGNvbF90ZiAvIDIsICAgeSAtIGhkcl9oICsgMi41Km1tLCAiVHJ1ZSIp"
    "CiAgICBjLmRyYXdDZW50cmVkU3RyaW5nKE1BUkdJTiArIGNvbF9zdG10ICsgY29sX3RmICogMS41"
    "LCB5IC0gaGRyX2ggKyAyLjUqbW0sICJGYWxzZSIpCiAgICB5IC09IGhkcl9oCiAgICBmb3IgaSwg"
    "KHN0bXQsIGFucykgaW4gZW51bWVyYXRlKHppcChzdGF0ZW1lbnRzLCBjb3JyZWN0X2xpc3QpKToK"
    "ICAgICAgICBmaWxsX2JnID0gKDAuOTcsIDAuOTcsIDAuOTcpIGlmIGkgJSAyID09IDAgZWxzZSAo"
    "MSwgMSwgMSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqZmlsbF9iZykKICAgICAgICBjLnNl"
    "dFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgeSAtIHJv"
    "d19oLCBjb2xfc3RtdCwgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRGaWxs"
    "Q29sb3JSR0IoMSwgMSwgMSkKICAgICAgICBjLnJlY3QoTUFSR0lOICsgY29sX3N0bXQsIHkgLSBy"
    "b3dfaCwgY29sX3RmICogMiwgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA4LjUpCiAg"
    "ICAgICAgc3RtdF9saW5lcyA9IHdyYXBfdGV4dChjLCBzdG10LCAiSGVsdmV0aWNhIiwgOC41LCBj"
    "b2xfc3RtdCAtIDQqbW0pCiAgICAgICAgZm9yIGosIHNsIGluIGVudW1lcmF0ZShzdG10X2xpbmVz"
    "WzoyXSk6CiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAyKm1tLCB5IC0gMy41Km1t"
    "IC0gaiAqIDQuNSptbSwgc2wpCiAgICAgICAgZm9yIGssIHRmIGluIGVudW1lcmF0ZShbIlRydWUi"
    "LCAiRmFsc2UiXSk6CiAgICAgICAgICAgIGJ4ID0gTUFSR0lOICsgY29sX3N0bXQgKyBrICogY29s"
    "X3RmICsgKGNvbF90ZiAtIGJveF9zKSAvIDIKICAgICAgICAgICAgYnkgPSB5IC0gcm93X2ggLyAy"
    "IC0gYm94X3MgLyAyCiAgICAgICAgICAgIGlzX2FucyA9IChhbnMgPT0gdGYpCiAgICAgICAgICAg"
    "IGlmIGlzX2FuczoKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpCiAg"
    "ICAgICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpCT1hfQk9SREVSKQogICAgICAgICAg"
    "ICBlbHNlOgogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAg"
    "ICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC41LCAwLjUsIDAuNSkKICAgICAgICAgICAg"
    "Yy5yZWN0KGJ4LCBieSwgYm94X3MsIGJveF9zLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgICAg"
    "ICBpZiBpc19hbnM6CiAgICAgICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpCT1hfQk9S"
    "REVSKQogICAgICAgICAgICAgICAgYy5zZXRMaW5lV2lkdGgoMSkKICAgICAgICAgICAgICAgIGMu"
    "bGluZShieCArIDAuNCptbSwgYnkgKyAxLjYqbW0sIGJ4ICsgMS4xKm1tLCBieSArIDAuNiptbSkK"
    "ICAgICAgICAgICAgICAgIGMubGluZShieCArIDEuMSptbSwgYnkgKyAwLjYqbW0sIGJ4ICsgMi43"
    "Km1tLCBieSArIDIuNCptbSkKICAgICAgICAgICAgICAgIGMuc2V0TGluZVdpZHRoKDAuNSkKICAg"
    "ICAgICB5IC09IHJvd19oCiAgICByZXR1cm4geSAtIDIqbW0KCgpkZWYgZHJhd19ldmlkZW5jZV9w"
    "dXBpbChjLCBuX2l0ZW1zLCB5LCBsaW5lc19wZXJfaXRlbT0xKToKICAgICIiIk51bWJlcmVkIGV2"
    "aWRlbmNlIGxpc3Qg4oCUIEtTMiBRNC9ROSBzdHlsZS4iIiIKICAgIGdhcCA9IDYuNSptbQogICAg"
    "Yy5zZXRMaW5lV2lkdGgoMC40KQogICAgZm9yIGkgaW4gcmFuZ2Uobl9pdGVtcyk6CiAgICAgICAg"
    "Yy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0Io"
    "KkRBUkspCiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwgeSwgZiJ7aSArIDF9LiIpCiAgICAg"
    "ICAgZm9yIGogaW4gcmFuZ2UobGluZXNfcGVyX2l0ZW0pOgogICAgICAgICAgICBseSA9IHkgLSAo"
    "aiArIDEpICogZ2FwCiAgICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkK"
    "ICAgICAgICAgICAgYy5saW5lKE1BUkdJTiArIDUqbW0sIGx5LCBNQVJHSU4gKyBDVywgbHkpCiAg"
    "ICAgICAgeSAtPSBsaW5lc19wZXJfaXRlbSAqIGdhcCArIDQqbW0KICAgIHJldHVybiB5CgoKZGVm"
    "IGRyYXdfZXZpZGVuY2VfYW5zd2VyKGMsIGFuc3dlcnMsIHksIGxpbmVzX3Blcl9pdGVtPTEpOgog"
    "ICAgIiIiTnVtYmVyZWQgZXZpZGVuY2UgbGlzdCB3aXRoIGFuc3dlcnMgaW4gZ3JlZW4uIiIiCiAg"
    "ICBnYXAgPSA2LjUqbW0KICAgIGZvciBpLCBhbnMgaW4gZW51bWVyYXRlKGFuc3dlcnMpOgogICAg"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgICAgIGMuc2V0RmlsbENvbG9y"
    "UkdCKCpEQVJLKQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHksIGYie2kgKyAxfS4iKQog"
    "ICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYS1PYmxpcXVlIiwgOC41KQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyA1Km1tLCB5"
    "IC0gZ2FwICsgMiptbSwgYW5zKQogICAgICAgIHkgLT0gbGluZXNfcGVyX2l0ZW0gKiBnYXAgKyA0"
    "Km1tCiAgICByZXR1cm4geQoKCgpkZWYgcV9sYWJlbChjLCBxbnVtLCB0ZXh0LCB5LCBpc19hbnN3"
    "ZXI9RmFsc2UsIGFuc19jb2xvdXI9RmFsc2UpOgogICAgIiIiRHJhdyBxdWVzdGlvbiBsYWJlbC4g"
    "UmV0dXJucyB5IGFmdGVyIHRleHQuIiIiCiAgICBjb2xvdXIgPSBHUkVFTiBpZiBhbnNfY29sb3Vy"
    "IGVsc2UgREFSSwogICAgYy5zZXRGaWxsQ29sb3JSR0IoKmNvbG91cikKICAgIGMuc2V0Rm9udCgi"
    "SGVsdmV0aWNhLUJvbGQiLCA5KQogICAgbGFiZWwgPSBmIntxbnVtWzE6XX0uICIKICAgIGx3ID0g"
    "Yy5zdHJpbmdXaWR0aChsYWJlbCwgIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgIGMuZHJhd1N0cmlu"
    "ZyhNQVJHSU4sIHksIGxhYmVsKQogICAgbGluZXMgPSB3cmFwX3RleHQoYywgdGV4dCwgIkhlbHZl"
    "dGljYS1Cb2xkIiwgOSwgQ1cgLSBsdykKICAgIGZvciBpLCBsaW5lIGluIGVudW1lcmF0ZShsaW5l"
    "cyk6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIGx3LCB5IC0gaSAqICg5ICogMS4zNSks"
    "IGxpbmUpCiAgICByZXR1cm4geSAtIGxlbihsaW5lcykgKiAoOSAqIDEuMzUpIC0gMSptbQoKCmRl"
    "ZiBkcmF3X21jX3B1cGlsKGMsIG9wdGlvbnMsIHkpOgogICAgIiIiNC1jZWxsIE1DIHRhYmxlLCBu"
    "byBoaWdobGlnaHQuIiIiCiAgICBjb2xfdyA9IENXIC8gMgogICAgcm93X2ggPSA2Km1tCiAgICAj"
    "IFR3byByb3dzIG9mIDIKICAgIGZvciByb3cgaW4gcmFuZ2UoMik6CiAgICAgICAgZm9yIGNvbCBp"
    "biByYW5nZSgyKToKICAgICAgICAgICAgaWR4ID0gcm93ICogMiArIGNvbAogICAgICAgICAgICBp"
    "ZiBpZHggPj0gbGVuKG9wdGlvbnMpOgogICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAg"
    "eCA9IE1BUkdJTiArIGNvbCAqIGNvbF93CiAgICAgICAgICAgIHJ5ID0geSAtIHJvdyAqIHJvd19o"
    "CiAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAgICAgICAgICAgIGMuc2V0"
    "U3Ryb2tlQ29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgICAgICAgICAgYy5zZXRMaW5lV2lkdGgo"
    "MC40KQogICAgICAgICAgICBjLnJlY3QoeCwgcnkgLSByb3dfaCwgY29sX3csIHJvd19oLCBmaWxs"
    "PTEsIHN0cm9rZT0xKQogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAg"
    "ICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA4LjUpCiAgICAgICAgICAgIGMuZHJhd1N0cmlu"
    "Zyh4ICsgMiptbSwgcnkgLSByb3dfaCArIDIqbW0sIG9wdGlvbnNbaWR4XSkKICAgIHJldHVybiB5"
    "IC0gMiAqIHJvd19oIC0gMS41Km1tCgoKZGVmIGRyYXdfbWNfYW5zd2VyKGMsIG9wdGlvbnMsIGNv"
    "cnJlY3QsIHkpOgogICAgIiIiNC1jZWxsIE1DIHRhYmxlLCBjb3JyZWN0IGNlbGwgaGlnaGxpZ2h0"
    "ZWQgZ3JlZW4uIiIiCiAgICBjb2xfdyA9IENXIC8gMgogICAgcm93X2ggPSA2Km1tCiAgICBmb3Ig"
    "cm93IGluIHJhbmdlKDIpOgogICAgICAgIGZvciBjb2wgaW4gcmFuZ2UoMik6CiAgICAgICAgICAg"
    "IGlkeCA9IHJvdyAqIDIgKyBjb2wKICAgICAgICAgICAgaWYgaWR4ID49IGxlbihvcHRpb25zKToK"
    "ICAgICAgICAgICAgICAgIGJyZWFrCiAgICAgICAgICAgIHggPSBNQVJHSU4gKyBjb2wgKiBjb2xf"
    "dwogICAgICAgICAgICByeSA9IHkgLSByb3cgKiByb3dfaAogICAgICAgICAgICBpc19jb3JyZWN0"
    "ID0gb3B0aW9uc1tpZHhdID09IGNvcnJlY3QKICAgICAgICAgICAgaWYgaXNfY29ycmVjdDoKICAg"
    "ICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDAuODUsIDAuOTUsIDAuODUpCiAgICAgICAg"
    "ICAgIGVsc2U6CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAg"
    "ICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNywgMC43LCAwLjcpCiAgICAgICAgICAgIGMu"
    "c2V0TGluZVdpZHRoKDAuNCkKICAgICAgICAgICAgYy5yZWN0KHgsIHJ5IC0gcm93X2gsIGNvbF93"
    "LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICAgICAgaWYgaXNfY29ycmVjdDoKICAg"
    "ICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICAgICAgICAgIGMu"
    "c2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4LjUpCiAgICAgICAgICAgICAgICBjLmRyYXdTdHJp"
    "bmcoeCArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBvcHRpb25zW2lkeF0gKyAiIFx1MjcxMyIp"
    "CiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFS"
    "SykKICAgICAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOC41KQogICAgICAgICAg"
    "ICAgICAgYy5kcmF3U3RyaW5nKHggKyAyKm1tLCByeSAtIHJvd19oICsgMiptbSwgb3B0aW9uc1tp"
    "ZHhdKQogICAgcmV0dXJuIHkgLSAyICogcm93X2ggLSAxLjUqbW0KCgpkZWYgZHJhd19tYXRjaF9w"
    "dXBpbChjLCBwYWlycywgeSk6CiAgICAiIiJNYXRjaCDigJQgY2lyY2xlcyBhdCBjb2x1bW4gZWRn"
    "ZXM7IHB1cGlsIGRyYXdzIGNvbm5lY3RpbmcgbGluZXMuIiIiCiAgICBsdyAgPSBDVyAqIDAuMzAK"
    "ICAgIHJ3ICA9IENXICogMC40OAogICAgZ2FwID0gQ1cgLSBsdyAtIHJ3CiAgICByb3dfaCA9IDkq"
    "bW0KICAgIHIgICAgID0gMi41Km1tCiAgICByaWdodHMgICAgPSBbcmlnaHQgZm9yIF8sIHJpZ2h0"
    "IGluIHBhaXJzXQogICAgc2NyYW1ibGVkID0gcmlnaHRzWzE6XSArIHJpZ2h0c1s6MV0KICAgIGMu"
    "c2V0TGluZVdpZHRoKDAuNCkKICAgIGZvciBpLCAobGVmdCwgXykgaW4gZW51bWVyYXRlKHBhaXJz"
    "KToKICAgICAgICByeSAgICA9IHkgLSBpICogcm93X2gKICAgICAgICBtaWRfeSA9IHJ5IC0gcm93"
    "X2ggLyAyCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC45NiwgMC45NiwgMC45NikKICAgICAg"
    "ICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNywgMC43LCAwLjcpCiAgICAgICAgYy5yZWN0KE1BUkdJ"
    "TiwgcnkgLSByb3dfaCwgbHcsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0"
    "RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5"
    "KQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAyKm1tLCBtaWRfeSAtIDIqbW0sIGxlZnQp"
    "CiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAgICBjLnNldFN0cm9rZUNv"
    "bG9yUkdCKDAuNCwgMC40LCAwLjQpCiAgICAgICAgYy5jaXJjbGUoTUFSR0lOICsgbHcsIG1pZF95"
    "LCByLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIHJ4ID0gTUFSR0lOICsgbHcgKyBnYXAKICAg"
    "ICAgICBjLnNldEZpbGxDb2xvclJHQigwLjk2LCAwLjk2LCAwLjk2KQogICAgICAgIGMuc2V0U3Ry"
    "b2tlQ29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgICAgICBjLnJlY3QocngsIHJ5IC0gcm93X2gs"
    "IHJ3LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigq"
    "REFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3Ry"
    "aW5nKHJ4ICsgciAqIDIgKyAyKm1tLCBtaWRfeSAtIDIqbW0sIHNjcmFtYmxlZFtpXSkKICAgICAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0Io"
    "MC40LCAwLjQsIDAuNCkKICAgICAgICBjLmNpcmNsZShyeCwgbWlkX3ksIHIsIGZpbGw9MSwgc3Ry"
    "b2tlPTEpCiAgICByZXR1cm4geSAtIGxlbihwYWlycykgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBk"
    "cmF3X21hdGNoX2Fuc3dlcihjLCBwYWlycywgeSk6CiAgICAiIiJNYXRjaCDigJQgZmlsbGVkIGNp"
    "cmNsZXMgd2l0aCBsaW5lcyBjb25uZWN0aW5nIGNvcnJlY3QgcGFpcnMuIiIiCiAgICBsdyAgPSBD"
    "VyAqIDAuMzAKICAgIHJ3ICA9IENXICogMC40OAogICAgZ2FwID0gQ1cgLSBsdyAtIHJ3CiAgICBy"
    "b3dfaCA9IDkqbW0KICAgIHIgICAgID0gMi41Km1tCiAgICBuICAgICA9IGxlbihwYWlycykKICAg"
    "IHJpZ2h0cyAgICA9IFtyaWdodCBmb3IgXywgcmlnaHQgaW4gcGFpcnNdCiAgICBzY3JhbWJsZWQg"
    "PSByaWdodHNbMTpdICsgcmlnaHRzWzoxXQogICAgbHggICAgICAgPSBNQVJHSU4gKyBsdwogICAg"
    "cnhfY2lyYyAgPSBNQVJHSU4gKyBsdyArIGdhcAogICAgbGVmdF9jeSAgPSBbeSAtIGkgKiByb3df"
    "aCAtIHJvd19oIC8gMiBmb3IgaSBpbiByYW5nZShuKV0KICAgIHJpZ2h0X2N5ID0gW3kgLSBpICog"
    "cm93X2ggLSByb3dfaCAvIDIgZm9yIGkgaW4gcmFuZ2UobildCiAgICBjLnNldExpbmVXaWR0aCgw"
    "LjQpCiAgICBmb3IgaSwgKGxlZnQsIF8pIGluIGVudW1lcmF0ZShwYWlycyk6CiAgICAgICAgcnkg"
    "ICAgPSB5IC0gaSAqIHJvd19oCiAgICAgICAgbWlkX3kgPSByeSAtIHJvd19oIC8gMgogICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKDAuOTYsIDAuOTYsIDAuOTYpCiAgICAgICAgYy5zZXRTdHJva2VD"
    "b2xvclJHQigwLjcsIDAuNywgMC43KQogICAgICAgIGMucmVjdChNQVJHSU4sIHJ5IC0gcm93X2gs"
    "IGx3LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigq"
    "Qk9YX0JPUkRFUikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgICAg"
    "ICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMiptbSwgbWlkX3kgLSAyKm1tLCBsZWZ0KQogICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQk9SREVSKQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JS"
    "R0IoKkJPWF9CT1JERVIpCiAgICAgICAgYy5jaXJjbGUobHgsIG1pZF95LCByLCBmaWxsPTEsIHN0"
    "cm9rZT0wKQogICAgICAgIHJ4ID0gTUFSR0lOICsgbHcgKyBnYXAKICAgICAgICBjLnNldEZpbGxD"
    "b2xvclJHQigwLjk2LCAwLjk2LCAwLjk2KQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC43"
    "LCAwLjcsIDAuNykKICAgICAgICBjLnJlY3QocngsIHJ5IC0gcm93X2gsIHJ3LCByb3dfaCwgZmls"
    "bD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JPUkRFUikKICAg"
    "ICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkT2JsaXF1ZSIsIDkpCiAgICAgICAgYy5kcmF3"
    "U3RyaW5nKHJ4ICsgciAqIDIgKyAyKm1tLCBtaWRfeSAtIDIqbW0sIHNjcmFtYmxlZFtpXSkKICAg"
    "ICAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JPUkRFUikKICAgICAgICBjLnNldFN0cm9rZUNv"
    "bG9yUkdCKCpCT1hfQk9SREVSKQogICAgICAgIGMuY2lyY2xlKHJ4X2NpcmMsIG1pZF95LCByLCBm"
    "aWxsPTEsIHN0cm9rZT0wKQogICAgYy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikKICAg"
    "IGMuc2V0TGluZVdpZHRoKDEuNSkKICAgIGZvciBpIGluIHJhbmdlKG4pOgogICAgICAgIGogPSAo"
    "aSAtIDEpICUgbgogICAgICAgIGMubGluZShseCArIHIsIGxlZnRfY3lbaV0sIHJ4X2NpcmMgLSBy"
    "LCByaWdodF9jeVtqXSkKICAgIHJldHVybiB5IC0gbiAqIHJvd19oIC0gMS41Km1tCgoKCmRlZiBk"
    "cmF3X2ZpbGwoYywgc2VudGVuY2UsIHksIGlzX2Fuc3dlcj1GYWxzZSwgYW5zd2VyPSIiKToKICAg"
    "ICIiIkRyYXcgZmlsbC1pbi1ibGFuayBzZW50ZW5jZSB3aXRoIHVuZGVybGluZSBibGFua3Mgb3Ig"
    "Z3JlZW4gYW5zd2Vycy4iIiIKICAgIHBhcnRzID0gc2VudGVuY2Uuc3BsaXQoIl9fX19fX19fX19f"
    "X19fIikKICAgIGJsYW5rc19uZWVkZWQgPSBsZW4ocGFydHMpIC0gMQogICAgYW5zd2VycyA9IFth"
    "LnN0cmlwKCkgZm9yIGEgaW4gYW5zd2VyLnNwbGl0KCIvIildIGlmIGFuc3dlciBlbHNlIFtdCiAg"
    "ICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykK"
    "ICAgIHggPSBNQVJHSU4KICAgIGJsYW5rX3cgPSAyOCptbQogICAgZm9yIHBpLCBwYXJ0IGluIGVu"
    "dW1lcmF0ZShwYXJ0cyk6CiAgICAgICAgIyBNZWFzdXJlIGFuZCBkcmF3IHRoZSB0ZXh0IHBhcnQK"
    "ICAgICAgICBwdyA9IGMuc3RyaW5nV2lkdGgocGFydCwgIkhlbHZldGljYSIsIDkpCiAgICAgICAg"
    "Yy5kcmF3U3RyaW5nKHgsIHksIHBhcnQpCiAgICAgICAgeCArPSBwdwogICAgICAgIGlmIHBpIDwg"
    "YmxhbmtzX25lZWRlZDoKICAgICAgICAgICAgaWYgaXNfYW5zd2VyIGFuZCBwaSA8IGxlbihhbnN3"
    "ZXJzKToKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICAg"
    "ICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgICAgICAgICAgICAgYy5k"
    "cmF3U3RyaW5nKHggKyAxKm1tLCB5LCBhbnN3ZXJzW3BpXSkKICAgICAgICAgICAgICAgIHggKz0g"
    "YmxhbmtfdwogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAg"
    "ICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAgICAgIGVsc2U6CiAgICAg"
    "ICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICAgICAgICAgICAg"
    "ICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICAgICAgICAgICAgICBjLmxpbmUoeCwgeSAtIDEqbW0s"
    "IHggKyBibGFua193LCB5IC0gMSptbSkKICAgICAgICAgICAgICAgIHggKz0gYmxhbmtfdwogICAg"
    "cmV0dXJuIHkgLSA1LjUqbW0KCgpkZWYgZHJhd190aWNrX3B1cGlsKGMsIG9wdGlvbnMsIHkpOgog"
    "ICAgIiIiVGljayBvcHRpb25zIHdpdGggc3F1YXJlIGJ1bGxldHMuIiIiCiAgICBjLnNldEZvbnQo"
    "IkhlbHZldGljYSIsIDkpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICMgMiBvciAz"
    "IHBlciByb3cgZGVwZW5kaW5nIG9uIGNvdW50CiAgICAjIENob29zZSBjb2x1bW5zIGJhc2VkIG9u"
    "IG9wdGlvbiBsZW5ndGgKICAgIG1heF9sZW4gPSBtYXgobGVuKG8pIGZvciBvIGluIG9wdGlvbnMp"
    "CiAgICBpZiBtYXhfbGVuID4gMjU6CiAgICAgICAgcGVyX3JvdyA9IDIgICMgbG9uZyBvcHRpb25z"
    "OiAyIHBlciByb3cKICAgIGVsaWYgbGVuKG9wdGlvbnMpID09IDU6CiAgICAgICAgcGVyX3JvdyA9"
    "IDUgICMgNSBzaG9ydCBvcHRpb25zOiBhbGwgb24gb25lIHJvdwogICAgZWxzZToKICAgICAgICBw"
    "ZXJfcm93ID0gNAogICAgY29sX3cgPSBDVyAvIHBlcl9yb3cKICAgIHJvd3MgPSAobGVuKG9wdGlv"
    "bnMpICsgcGVyX3JvdyAtIDEpIC8vIHBlcl9yb3cKICAgIHJvd19oID0gNS41Km1tCiAgICBmb3Ig"
    "aSwgb3B0IGluIGVudW1lcmF0ZShvcHRpb25zKToKICAgICAgICByb3cgPSBpIC8vIHBlcl9yb3cK"
    "ICAgICAgICBjb2wgPSBpICUgcGVyX3JvdwogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBj"
    "b2wgKiBjb2xfdywgeSAtIHJvdyAqIHJvd19oLCBvcHQpCiAgICByZXR1cm4geSAtIHJvd3MgKiBy"
    "b3dfaCAtIDMqbW0KCgpkZWYgZHJhd190aWNrX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5"
    "KToKICAgICIiIlRpY2sgb3B0aW9ucyB3aXRoIGNvcnJlY3Qgb25lcyBpbiBib2xkIGdyZWVuLiIi"
    "IgogICAgbWF4X2xlbiA9IG1heChsZW4obykgZm9yIG8gaW4gb3B0aW9ucykKICAgIGlmIG1heF9s"
    "ZW4gPiAyNToKICAgICAgICBwZXJfcm93ID0gMgogICAgZWxpZiBsZW4ob3B0aW9ucykgPT0gNToK"
    "ICAgICAgICBwZXJfcm93ID0gNQogICAgZWxzZToKICAgICAgICBwZXJfcm93ID0gNAogICAgY29s"
    "X3cgPSBDVyAvIHBlcl9yb3cKICAgIHJvd3MgPSAobGVuKG9wdGlvbnMpICsgcGVyX3JvdyAtIDEp"
    "IC8vIHBlcl9yb3cKICAgIHJvd19oID0gNS41Km1tCiAgICBmb3IgaSwgb3B0IGluIGVudW1lcmF0"
    "ZShvcHRpb25zKToKICAgICAgICByb3cgPSBpIC8vIHBlcl9yb3cKICAgICAgICBjb2wgPSBpICUg"
    "cGVyX3JvdwogICAgICAgIGlmIG9wdCBpbiBjb3JyZWN0OgogICAgICAgICAgICBjLnNldEZpbGxD"
    "b2xvclJHQigqR1JFRU4pCiAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5"
    "KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAg"
    "ICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3RyaW5nKE1B"
    "UkdJTiArIGNvbCAqIGNvbF93LCB5IC0gcm93ICogcm93X2gsIG9wdCkKICAgIHJldHVybiB5IC0g"
    "cm93cyAqIHJvd19oIC0gMyptbQoKCmRlZiBkcmF3X29yZGVyX3B1cGlsKGMsIGV2ZW50cywgeSk6"
    "CiAgICAiIiJLUzItc3R5bGUgc2VxdWVuY2luZyDigJQgdGV4dCBsZWZ0LCBudW1iZXIgYm94IGp1"
    "c3QgYWZ0ZXIgbG9uZ2VzdCBpdGVtLiIiIgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQog"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBib3hfcyA9IDYqbW0KICAgIHJvd19oID0g"
    "MTAqbW0KICAgIG1heF93ID0gbWF4KGMuc3RyaW5nV2lkdGgoZXYsICJIZWx2ZXRpY2EiLCA5KSBm"
    "b3IgZXYgaW4gZXZlbnRzKQogICAgYm94X3ggPSBNQVJHSU4gKyAyKm1tICsgbWF4X3cgKyA0Km1t"
    "CiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBmb3IgZXYgaW4gZXZlbnRzOgogICAgICAgIGMu"
    "c2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAyKm1t"
    "LCB5IC0gcm93X2ggKyAzKm1tLCBldikKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAxLCAx"
    "KQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC40LCAwLjQsIDAuNCkKICAgICAgICBjLnJl"
    "Y3QoYm94X3gsIHkgLSByb3dfaCArIDIqbW0sIGJveF9zLCBib3hfcyAtIDEqbW0sIGZpbGw9MSwg"
    "c3Ryb2tlPTEpCiAgICAgICAgeSAtPSByb3dfaCArIDIqbW0KICAgIHJldHVybiB5IC0gMSptbQoK"
    "CgpkZWYgZHJhd19vcmRlcl9hbnN3ZXIoYywgZXZlbnRzLCBjb3JyZWN0X29yZGVyLCB5KToKICAg"
    "ICIiIktTMi1zdHlsZSBzZXF1ZW5jaW5nIOKAlCBudW1iZXIgYm94IGp1c3QgYWZ0ZXIgbG9uZ2Vz"
    "dCBpdGVtLiIiIgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgYm94X3MgPSA2Km1t"
    "CiAgICByb3dfaCA9IDEwKm1tCiAgICBtYXhfdyA9IG1heChjLnN0cmluZ1dpZHRoKGV2LCAiSGVs"
    "dmV0aWNhIiwgOSkgZm9yIGV2IGluIGV2ZW50cykKICAgIGJveF94ID0gTUFSR0lOICsgMiptbSAr"
    "IG1heF93ICsgNCptbQogICAgYy5zZXRMaW5lV2lkdGgoMC41KQogICAgbnVtcyA9IFtuLnN0cmlw"
    "KCkgZm9yIG4gaW4gc3RyKGNvcnJlY3Rfb3JkZXIpLnNwbGl0KCIsIildCiAgICBmb3IgaSwgKGV2"
    "LCBudW0pIGluIGVudW1lcmF0ZSh6aXAoZXZlbnRzLCBudW1zKSk6CiAgICAgICAgYy5zZXRGaWxs"
    "Q29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIDIqbW0sIHkgLSBy"
    "b3dfaCArIDMqbW0sIGV2KQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpCiAgICAg"
    "ICAgYy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikKICAgICAgICBjLnJlY3QoYm94X3gs"
    "IHkgLSByb3dfaCArIDIqbW0sIGJveF9zLCBib3hfcyAtIDEqbW0sIGZpbGw9MSwgc3Ryb2tlPTEp"
    "CiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CT1JERVIpCiAgICAgICAgYy5zZXRGb250"
    "KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICAgICAgYy5kcmF3Q2VudHJlZFN0cmluZyhib3hfeCAr"
    "IGJveF9zLzIsIHkgLSByb3dfaCArIDQqbW0sIG51bSkKICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYSIsIDkpCiAgICAgICAgeSAtPSByb3dfaCArIDIqbW0KICAgIHJldHVybiB5IC0gMSptbQoK"
    "CgpkZWYgZHJhd193cml0dGVuX2Fuc3dlcihjLCBhbnN3ZXIsIHksIG5fbGluZXM9Myk6CiAgICAi"
    "IiJXcml0dGVuIGFuc3dlcjogYW5zd2VyIGxpbmVzIChwdXBpbCkgb3IgZ3JlZW4gaXRhbGljIHRl"
    "eHQgKGFuc3dlcnMpLiIiIgogICAgaWYgYW5zd2VyOgogICAgICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1PYmxpcXVlIiwgOC41KQogICAg"
    "ICAgIGxpbmVzID0gd3JhcF90ZXh0KGMsIGFuc3dlciwgIkhlbHZldGljYS1PYmxpcXVlIiwgOC41"
    "LCBDVykKICAgICAgICBmb3IgaSwgbGluZSBpbiBlbnVtZXJhdGUobGluZXMpOgogICAgICAgICAg"
    "ICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gKGkgKyAwLjI1KSAqIDUqbW0sIGxpbmUpCiAgICAg"
    "ICAgcmV0dXJuIHkgLSAobGVuKGxpbmVzKSAtIDAuNzUpICogNSptbSAtIDQqbW0KICAgIGVsc2U6"
    "CiAgICAgICAgcmV0dXJuIGFuc3dlcl9saW5lcyhjLCB5ICsgMyptbSwgbl9saW5lcykKCgpkZWYg"
    "cmVuZGVyX3F1ZXN0aW9uKGMsIHEsIHksIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5lcz0zLCBtaW5f"
    "eT0yMCptbSk6CiAgICAiIiJSZW5kZXIgYSBzaW5nbGUgcXVlc3Rpb24uIFJldHVybnMgbmV3IHks"
    "IG9yIE5vbmUgaWYgbm8gcm9vbS4iIiIKICAgIHFudW0sIHF0eXBlLCBxdGV4dCwgb3B0aW9ucywg"
    "Y29ycmVjdCA9IHEKCiAgICAjIEVzdGltYXRlIGhlaWdodAogICAgbGFiZWxfaCA9IGxlbih3cmFw"
    "X3RleHQoYywgcXRleHQuc3BsaXQoJ1xuJylbMF0sICJIZWx2ZXRpY2EtQm9sZCIsIDksIENXIC0g"
    "OCptbSkpICogMTIgKyA0CiAgICBleHRyYSA9IDAKICAgIGlmIHF0eXBlID09ICJtYyI6ICAgICAg"
    "ICAgICAgIGV4dHJhID0gMTQqbW0KICAgIGVsaWYgcXR5cGUgPT0gIm1hdGNoIjogICAgICAgIGV4"
    "dHJhID0gbGVuKG9wdGlvbnMpICogNyptbQogICAgZWxpZiBxdHlwZSBpbiAoInRpY2syIiwidGlj"
    "azMiKTogZXh0cmEgPSAobGVuKG9wdGlvbnMpIC8vIDMgKyAxKSAqIDYqbW0KICAgIGVsaWYgcXR5"
    "cGUgPT0gImZpbGwiOiAgICAgICAgIGV4dHJhID0gNiptbQogICAgZWxpZiBxdHlwZSA9PSAib3Jk"
    "ZXIiOiAgICAgICAgZXh0cmEgPSBsZW4ob3B0aW9ucykgKiA2Km1tCiAgICBlbGlmIHF0eXBlID09"
    "ICJ3cml0dGVuIjogICAgICBleHRyYSA9IG5fbGluZXMgKiA1LjUqbW0KICAgIGVsaWYgcXR5cGUg"
    "PT0gInNob3J0IjogICAgICAgIGV4dHJhID0gNS41Km1tCiAgICBlbGlmIHF0eXBlID09ICJzaG9y"
    "dDIiOiAgICAgICBleHRyYSA9IDExKm1tCiAgICBlbGlmIHF0eXBlID09ICJxdW90ZSI6ICAgICAg"
    "ICBleHRyYSA9IDgqbW0KICAgIGVsaWYgcXR5cGUgPT0gInRydWVfZmFsc2UiOiAgIGV4dHJhID0g"
    "OCptbQogICAgZWxpZiBxdHlwZSA9PSAic2VsZWN0IjogICAgICAgZXh0cmEgPSA1LjUqbW0gKyAo"
    "KGxlbihvcHRpb25zKSsxKS8vMikgKiA2Km1tICsgMiptbQogICAgZWxpZiBxdHlwZSA9PSAidGlj"
    "a192IjogICAgICAgIGV4dHJhID0gNi41Km1tICsgbGVuKG9wdGlvbnMpICogNyptbSArIDEqbW0K"
    "ICAgIGVsaWYgcXR5cGUgPT0gInRmX3RhYmxlIjogICAgICBleHRyYSA9IDcqbW0gKyBsZW4ob3B0"
    "aW9ucykgKiA5Km1tICsgMiptbQogICAgZWxpZiBxdHlwZSA9PSAiZXZpZGVuY2UyIjogICAgIGV4"
    "dHJhID0gMiAqICg2LjUqbW0gKyA0Km1tKQogICAgZWxpZiBxdHlwZSA9PSAiZXZpZGVuY2UyX2V4"
    "dCI6IGV4dHJhID0gMiAqICgyICogNi41Km1tICsgNCptbSkKICAgIGVsaWYgcXR5cGUgPT0gImV2"
    "aWRlbmNlMyI6ICAgICBleHRyYSA9IDMgKiAoNi41Km1tICsgNCptbSkKICAgIGVsaWYgcXR5cGUg"
    "PT0gImF0dHJpYl90YWJsZSI6ICBleHRyYSA9IDgqbW0gKyAobGVuKG9wdGlvbnMpLTEpICogOSpt"
    "bSArIDIqbW0KICAgIGVsaWYgcXR5cGUgPT0gImltcHJfZXZpZGVuY2UiOiBleHRyYSA9IDkqbW0g"
    "KyAob3B0aW9ucyBpZiBpc2luc3RhbmNlKG9wdGlvbnMsIGludCkgZWxzZSAyKSAqIDM0Km1tICsg"
    "MiptbQogICAgdG90YWxfZXN0ID0gbGFiZWxfaCArIGV4dHJhICsgOCptbQoKICAgIGlmIHkgLSB0"
    "b3RhbF9lc3QgPCBtaW5feToKICAgICAgICByZXR1cm4gTm9uZSAgIyBubyByb29tCgogICAgeSAt"
    "PSA1Km1tICAjIHByZS1xdWVzdGlvbiBnYXAg4oCUIHZpc3VhbGx5IGdyb3VwcyBsYWJlbCB3aXRo"
    "IGl0cyBhbnN3ZXIsIG5vdCBwcmV2aW91cyBjb250ZW50CgogICAgIyBEcmF3IHF1ZXN0aW9uIHRl"
    "eHQKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgYy5zZXRGb250KCJIZWx2ZXRpY2Et"
    "Qm9sZCIsIDkpCiAgICBsYWJlbCA9IGYie3FudW1bMTpdfS4gIgogICAgbHcgPSBjLnN0cmluZ1dp"
    "ZHRoKGxhYmVsLCAiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwg"
    "eSwgbGFiZWwpCiAgICBxX2xpbmVzX2FsbCA9IHF0ZXh0LnNwbGl0KCdcbicpCiAgICAjIEZvciBm"
    "aWxsLWluLWJsYW5rIHdpdGggYSBzZXBhcmF0ZSBzZW50ZW5jZSBsaW5lLCBvbmx5IHNob3cgdGhl"
    "IHByb21wdCBhcyB0aGUgbGFiZWwKICAgIGxhYmVsX2xpbmVzX3RleHQgPSBxX2xpbmVzX2FsbFsw"
    "XQogICAgZmlyc3RfbGluZXMgPSB3cmFwX3RleHQoYywgbGFiZWxfbGluZXNfdGV4dCwgIkhlbHZl"
    "dGljYS1Cb2xkIiwgOSwgQ1cgLSBsdykKICAgIGZvciBpLCBsaW5lIGluIGVudW1lcmF0ZShmaXJz"
    "dF9saW5lcyk6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIGx3LCB5IC0gaSAqICg5ICog"
    "MS4zNSksIGxpbmUpCiAgICB5IC09IGxlbihmaXJzdF9saW5lcykgKiAoOSAqIDEuMzUpCiAgICAj"
    "IEZvciBub24tZmlsbCB0eXBlcyB3aXRoIGFkZGl0aW9uYWwgbGluZXMgKG5vdCB1c2VkIGN1cnJl"
    "bnRseSksIGRyYXcgdGhlbQogICAgaWYgcXR5cGUgIT0gImZpbGwiOgogICAgICAgIGZvciBleHRy"
    "YV9saW5lIGluIHFfbGluZXNfYWxsWzE6XToKICAgICAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRp"
    "Y2EiLCA5KQogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAgICAg"
    "Yy5kcmF3U3RyaW5nKE1BUkdJTiwgeSwgZXh0cmFfbGluZSkKICAgICAgICAgICAgeSAtPSA5ICog"
    "MS4zNQogICAgaWYgcXR5cGUgPT0gIm1jIjoKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAg"
    "ICAgIHkgPSBkcmF3X21jX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KQogICAgICAgIGVs"
    "c2U6CiAgICAgICAgICAgIHkgPSBkcmF3X21jX3B1cGlsKGMsIG9wdGlvbnMsIHkpCiAgICAgICAg"
    "eSAtPSAxKm1tICAjIGV4dHJhIGdhcCBhZnRlciBNQyB0YWJsZQoKICAgIGVsaWYgcXR5cGUgPT0g"
    "Im1hdGNoIjoKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBkcmF3X21hdGNo"
    "X2Fuc3dlcihjLCBvcHRpb25zLCB5KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3"
    "X21hdGNoX3B1cGlsKGMsIG9wdGlvbnMsIHkpCiAgICAgICAgeSAtPSAxKm1tICAjIGV4dHJhIGdh"
    "cCBhZnRlciBtYXRjaCB0YWJsZQoKICAgIGVsaWYgcXR5cGUgaW4gKCJ0aWNrMiIsICJ0aWNrMyIp"
    "OgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRyYXdfdGlja19hbnN3ZXIo"
    "Yywgb3B0aW9ucywgY29ycmVjdCwgeSkKICAgICAgICBlbHNlOgogICAgICAgICAgICB5ID0gZHJh"
    "d190aWNrX3B1cGlsKGMsIG9wdGlvbnMsIHkpCgogICAgZWxpZiBxdHlwZSA9PSAiZmlsbCI6CiAg"
    "ICAgICAgIyBUaGUgZmlsbCBzZW50ZW5jZSBpcyB0aGUgbGFzdCBlbGVtZW50IG9mIHFfbGluZXNf"
    "YWxsIChvciBxdGV4dCBpZiBubyBcbikKICAgICAgICBmaWxsX3NlbnRlbmNlID0gcV9saW5lc19h"
    "bGxbLTFdIGlmIGxlbihxX2xpbmVzX2FsbCkgPiAxIGVsc2UgcXRleHQKICAgICAgICB5ID0gZHJh"
    "d19maWxsKGMsIGZpbGxfc2VudGVuY2UsIHksIGlzX2Fuc3dlcj1pc19hbnN3ZXIsIGFuc3dlcj1j"
    "b3JyZWN0IG9yICIiKQoKICAgIGVsaWYgcXR5cGUgPT0gIm9yZGVyIjoKICAgICAgICBpZiBpc19h"
    "bnN3ZXI6CiAgICAgICAgICAgIHkgPSBkcmF3X29yZGVyX2Fuc3dlcihjLCBvcHRpb25zLCBjb3Jy"
    "ZWN0LCB5KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3X29yZGVyX3B1cGlsKGMs"
    "IG9wdGlvbnMsIHkpCgogICAgZWxpZiBxdHlwZSA9PSAid3JpdHRlbiI6CiAgICAgICAgeSA9IGRy"
    "YXdfd3JpdHRlbl9hbnN3ZXIoYywgY29ycmVjdCBpZiBpc19hbnN3ZXIgZWxzZSBOb25lLCB5LCBu"
    "X2xpbmVzPW5fbGluZXMpCgogICAgZWxpZiBxdHlwZSA9PSAic2hvcnQiOgogICAgICAgIHkgPSBk"
    "cmF3X3dyaXR0ZW5fYW5zd2VyKGMsIGNvcnJlY3QgaWYgaXNfYW5zd2VyIGVsc2UgTm9uZSwgeSwg"
    "bl9saW5lcz0xKQoKICAgIGVsaWYgcXR5cGUgPT0gInNob3J0MiI6CiAgICAgICAgeSA9IGRyYXdf"
    "d3JpdHRlbl9hbnN3ZXIoYywgY29ycmVjdCBpZiBpc19hbnN3ZXIgZWxzZSBOb25lLCB5LCBuX2xp"
    "bmVzPTIpCgogICAgZWxpZiBxdHlwZSA9PSAicXVvdGUiOgogICAgICAgIGlmIGlzX2Fuc3dlcjoK"
    "ICAgICAgICAgICAgeSA9IGRyYXdfcXVvdGVfYW5zd2VyKGMsIGNvcnJlY3Qgb3IgIiIsIHkpCiAg"
    "ICAgICAgZWxzZToKICAgICAgICAgICAgeSA9IGRyYXdfcXVvdGVfcHVwaWwoYywgeSkKCiAgICBl"
    "bGlmIHF0eXBlID09ICJ0cnVlX2ZhbHNlIjoKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAg"
    "ICAgIHkgPSBkcmF3X3RydWVfZmFsc2VfYW5zd2VyKGMsIGNvcnJlY3Qgb3IgIlRydWUiLCB5KQog"
    "ICAgICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3X3RydWVfZmFsc2VfcHVwaWwoYywgeSkK"
    "CiAgICBlbGlmIHF0eXBlID09ICJzZWxlY3QiOgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAg"
    "ICAgICAgeSA9IGRyYXdfc2VsZWN0X2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0IGlmIGlzaW5z"
    "dGFuY2UoY29ycmVjdCwgbGlzdCkgZWxzZSBbY29ycmVjdF0sIHkpCiAgICAgICAgZWxzZToKICAg"
    "ICAgICAgICAgeSA9IGRyYXdfc2VsZWN0X3B1cGlsKGMsIG9wdGlvbnMsIHkpCgogICAgZWxpZiBx"
    "dHlwZSA9PSAidGlja192IjoKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBk"
    "cmF3X3RpY2tfdl9hbnN3ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSkKICAgICAgICBlbHNlOgog"
    "ICAgICAgICAgICB5ID0gZHJhd190aWNrX3ZfcHVwaWwoYywgb3B0aW9ucywgY29ycmVjdCwgeSkK"
    "CiAgICBlbGlmIHF0eXBlID09ICJ0Zl90YWJsZSI6CiAgICAgICAgaWYgaXNfYW5zd2VyOgogICAg"
    "ICAgICAgICB5ID0gZHJhd190Zl90YWJsZV9hbnN3ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSkK"
    "ICAgICAgICBlbHNlOgogICAgICAgICAgICB5ID0gZHJhd190Zl90YWJsZV9wdXBpbChjLCBvcHRp"
    "b25zLCB5KQoKICAgIGVsaWYgcXR5cGUgPT0gImV2aWRlbmNlMiI6CiAgICAgICAgaWYgaXNfYW5z"
    "d2VyOgogICAgICAgICAgICB5ID0gZHJhd19ldmlkZW5jZV9hbnN3ZXIoYywgY29ycmVjdCwgeSwg"
    "bGluZXNfcGVyX2l0ZW09MSkKICAgICAgICBlbHNlOgogICAgICAgICAgICB5ID0gZHJhd19ldmlk"
    "ZW5jZV9wdXBpbChjLCAyLCB5LCBsaW5lc19wZXJfaXRlbT0xKQoKICAgIGVsaWYgcXR5cGUgPT0g"
    "ImV2aWRlbmNlMl9leHQiOgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRy"
    "YXdfZXZpZGVuY2VfYW5zd2VyKGMsIGNvcnJlY3QsIHksIGxpbmVzX3Blcl9pdGVtPTIpCiAgICAg"
    "ICAgZWxzZToKICAgICAgICAgICAgeSA9IGRyYXdfZXZpZGVuY2VfcHVwaWwoYywgMiwgeSwgbGlu"
    "ZXNfcGVyX2l0ZW09MikKCiAgICBlbGlmIHF0eXBlID09ICJldmlkZW5jZTMiOgogICAgICAgIGlm"
    "IGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRyYXdfZXZpZGVuY2VfYW5zd2VyKGMsIGNvcnJl"
    "Y3QsIHksIGxpbmVzX3Blcl9pdGVtPTEpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgeSA9IGRy"
    "YXdfZXZpZGVuY2VfcHVwaWwoYywgMywgeSwgbGluZXNfcGVyX2l0ZW09MSkKCiAgICBlbGlmIHF0"
    "eXBlID09ICJhdHRyaWJfdGFibGUiOgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAgICAgICAg"
    "eSA9IGRyYXdfYXR0cmliX3RhYmxlX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KQogICAg"
    "ICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3X2F0dHJpYl90YWJsZV9wdXBpbChjLCBvcHRp"
    "b25zLCB5KQoKICAgIGVsaWYgcXR5cGUgPT0gImltcHJfZXZpZGVuY2UiOgogICAgICAgIG5fcm93"
    "cyA9IG9wdGlvbnMgaWYgaXNpbnN0YW5jZShvcHRpb25zLCBpbnQpIGVsc2UgbGVuKGNvcnJlY3Qp"
    "IGlmIGNvcnJlY3QgZWxzZSAyCiAgICAgICAgaWYgaXNfYW5zd2VyOgogICAgICAgICAgICB5ID0g"
    "ZHJhd19pbXByX2V2aWRlbmNlX2Fuc3dlcihjLCBjb3JyZWN0LCB5KQogICAgICAgIGVsc2U6CiAg"
    "ICAgICAgICAgIHkgPSBkcmF3X2ltcHJfZXZpZGVuY2VfcHVwaWwoYywgbl9yb3dzLCB5KQoKICAg"
    "IHJldHVybiB5IC0gMSptbQoKCmRlZiBidWlsZF9wYWdlKHBhdGgsIGxlc3Nvbl90eXBlLCB0ZXh0"
    "LCBxdWVzdGlvbnMsIGRhdGVfc3RyLCBpc19hbnN3ZXIsIG5fbGluZXMpOgogICAgIiIiQnVpbGQg"
    "YSBzaW5nbGUtcGFnZSBQREYuIiIiCiAgICBjID0gY2FudmFzLkNhbnZhcyhwYXRoLCBwYWdlc2l6"
    "ZT1BNCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQoKICAgIHkgPSBkcmF3X2hlYWRlcihj"
    "LCBsZXNzb25fdHlwZSwgZGF0ZV9zdHIsIEtFWV9RLAogICAgICAgICAgICAgICAgICAgIExGW2xl"
    "c3Nvbl90eXBlXSwgSUNBTltsZXNzb25fdHlwZV1bMF0sIElDQU5bbGVzc29uX3R5cGVdWzFdKQoK"
    "ICAgIHkgPSBkcmF3X3RleHRfYm94KGMsIHRleHQsIHkpCgogICAgbWluX3kgPSAxMiptbQogICAg"
    "Zm9yIHEgaW4gcXVlc3Rpb25zOgogICAgICAgIHJlc3VsdCA9IHJlbmRlcl9xdWVzdGlvbihjLCBx"
    "LCB5LCBpc19hbnN3ZXI9aXNfYW5zd2VyLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICBuX2xpbmVzPW5fbGluZXMsIG1pbl95PW1pbl95KQogICAgICAgIGlmIHJlc3VsdCBpcyBOb25l"
    "OgogICAgICAgICAgICAjIERyb3AgUTcgaWYgbm8gcm9vbSAobGFzdCBxdWVzdGlvbiBpbiBsaXN0"
    "KQogICAgICAgICAgICBicmVhawogICAgICAgIHkgPSByZXN1bHQKCiAgICBjLnNhdmUoKQogICAg"
    "cmV0dXJuIHBhdGgKCgpkZWYgY2hlY2tfcGFnZV9jb3VudChwYXRoKToKICAgIHJlYWRlciA9IFBk"
    "ZlJlYWRlcihwYXRoKQogICAgcmV0dXJuIGxlbihyZWFkZXIucGFnZXMpCgoKZGVmIG1lcmdlX3Bk"
    "ZnMoZmlsZV9saXN0LCBvdXRwdXRfcGF0aCk6CiAgICB3cml0ZXIgPSBQZGZXcml0ZXIoKQogICAg"
    "Zm9yIGYgaW4gZmlsZV9saXN0OgogICAgICAgIGZvciBwYWdlIGluIFBkZlJlYWRlcihmKS5wYWdl"
    "czoKICAgICAgICAgICAgd3JpdGVyLmFkZF9wYWdlKHBhZ2UpCiAgICB3aXRoIG9wZW4ob3V0cHV0"
    "X3BhdGgsICJ3YiIpIGFzIGZoOgogICAgICAgIHdyaXRlci53cml0ZShmaCkKCgojIOKUgOKUgCBC"
    "dWlsZCBhbGwgMTIgaW5kaXZpZHVhbCBQREZzIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAoKbGVzc29u"
    "cyA9IFsKICAgICgiVm9jYWJ1bGFyeSIsIFNURF9WT0MsIFNVUF9WT0MsIFNURF9WT0NfUVMsIFNV"
    "UF9WT0NfUVMsIERBVEVTWyJWb2NhYnVsYXJ5Il0pLAogICAgKCJSZXRyaWV2YWwiLCAgU1REX1JF"
    "VCwgU1VQX1JFVCwgU1REX1JFVF9RUywgU1VQX1JFVF9RUywgREFURVNbIlJldHJpZXZhbCJdKSwK"
    "ICAgICgiSW5mZXJlbmNlIiwgIFNURF9JTkYsIFNVUF9JTkYsIFNURF9JTkZfUVMsIFNVUF9JTkZf"
    "UVMsIERBVEVTWyJJbmZlcmVuY2UiXSksCl0KCmJ1aWx0ID0gewogICAgInN0ZF9wdXBpbCI6IFtd"
    "LCAic3VwX3B1cGlsIjogW10sCiAgICAic3RkX2FucyI6IFtdLCAic3VwX2FucyI6IFtdLAp9Cgpm"
    "b3IgbGVzc29uX3R5cGUsIHN0ZF90ZXh0LCBzdXBfdGV4dCwgc3RkX3FzLCBzdXBfcXMsIGRhdGVf"
    "c3RyIGluIGxlc3NvbnM6CiAgICBsdCA9IGxlc3Nvbl90eXBlCiAgICBwcmludChmIkJ1aWxkaW5n"
    "IHtsdH0uLi4iKQoKICAgICMgU3RhbmRhcmQgcHVwaWwKICAgIHAgPSBmIntPVVRfRElSfS97bHR9"
    "X1N0YW5kYXJkX1B1cGlsLnBkZiIKICAgIGJ1aWxkX3BhZ2UocCwgbHQsIHN0ZF90ZXh0LCBzdGRf"
    "cXMsIGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9MykKICAgIHBhZ2VzID0gY2hl"
    "Y2tfcGFnZV9jb3VudChwKQogICAgaWYgcGFnZXMgPiAxOgogICAgICAgIHByaW50KGYiICBXQVJO"
    "SU5HOiB7bHR9IFN0YW5kYXJkIG92ZXJmbG93cyAoe3BhZ2VzfSBwYWdlcykg4oCUIGRyb3BwaW5n"
    "IFE3IikKICAgICAgICBidWlsZF9wYWdlKHAsIGx0LCBzdGRfdGV4dCwgc3RkX3FzWzotMV0sIGRh"
    "dGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9MykKICAgIHByaW50KGYiICBTdGFuZGFy"
    "ZCBQdXBpbDoge2NoZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAgYnVpbHRbInN0ZF9w"
    "dXBpbCJdLmFwcGVuZChwKQoKICAgICMgU3VwcG9ydGVkIHB1cGlsCiAgICBwID0gZiJ7T1VUX0RJ"
    "Un0ve2x0fV9TdXBwb3J0ZWRfUHVwaWwucGRmIgogICAgYnVpbGRfcGFnZShwLCBsdCwgc3VwX3Rl"
    "eHQsIHN1cF9xcywgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5lcz0yKQogICAgcGFn"
    "ZXMgPSBjaGVja19wYWdlX2NvdW50KHApCiAgICBpZiBwYWdlcyA+IDE6CiAgICAgICAgcHJpbnQo"
    "ZiIgIFdBUk5JTkc6IHtsdH0gU3VwcG9ydGVkIG92ZXJmbG93cyAoe3BhZ2VzfSBwYWdlcykg4oCU"
    "IGRyb3BwaW5nIFE1IikKICAgICAgICBidWlsZF9wYWdlKHAsIGx0LCBzdXBfdGV4dCwgc3VwX3Fz"
    "WzotMV0sIGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9MikKICAgIHByaW50KGYi"
    "ICBTdXBwb3J0ZWQgUHVwaWw6IHtjaGVja19wYWdlX2NvdW50KHApfSBwYWdlKHMpIikKICAgIGJ1"
    "aWx0WyJzdXBfcHVwaWwiXS5hcHBlbmQocCkKCiAgICAjIFN0YW5kYXJkIGFuc3dlcnMKICAgIHAg"
    "PSBmIntPVVRfRElSfS97bHR9X1N0YW5kYXJkX0Fuc3dlcnMucGRmIgogICAgYnVpbGRfcGFnZShw"
    "LCBsdCwgc3RkX3RleHQsIHN0ZF9xcywgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1UcnVlLCBuX2xpbmVz"
    "PTMpCiAgICBwcmludChmIiAgU3RhbmRhcmQgQW5zd2Vyczoge2NoZWNrX3BhZ2VfY291bnQocCl9"
    "IHBhZ2UocykiKQogICAgYnVpbHRbInN0ZF9hbnMiXS5hcHBlbmQocCkKCiAgICAjIFN1cHBvcnRl"
    "ZCBhbnN3ZXJzCiAgICBwID0gZiJ7T1VUX0RJUn0ve2x0fV9TdXBwb3J0ZWRfQW5zd2Vycy5wZGYi"
    "CiAgICBidWlsZF9wYWdlKHAsIGx0LCBzdXBfdGV4dCwgc3VwX3FzLCBkYXRlX3N0ciwgaXNfYW5z"
    "d2VyPVRydWUsIG5fbGluZXM9MikKICAgIHByaW50KGYiICBTdXBwb3J0ZWQgQW5zd2Vyczoge2No"
    "ZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAgYnVpbHRbInN1cF9hbnMiXS5hcHBlbmQo"
    "cCkKCnByaW50KCJcbk1lcmdpbmcuLi4iKQoKIyBTdGFuZGFyZCBQdXBpbDogVm9jICsgUmV0ICsg"
    "SW5mCm1lcmdlX3BkZnMoYnVpbHRbInN0ZF9wdXBpbCJdLAogICAgICAgICAgICIvbW50L3VzZXIt"
    "ZGF0YS9vdXRwdXRzL1Q1VzJfU3RhbmRhcmRfUHVwaWwucGRmIikKCiMgU3VwcG9ydGVkIFB1cGls"
    "OiBWb2MgKyBSZXQgKyBJbmYKbWVyZ2VfcGRmcyhidWlsdFsic3VwX3B1cGlsIl0sCiAgICAgICAg"
    "ICAgIi9tbnQvdXNlci1kYXRhL291dHB1dHMvVDVXMl9TdXBwb3J0ZWRfUHVwaWwucGRmIikKCiMg"
    "QWxsIEFuc3dlcnM6IFZvYyBTdGQsIFZvYyBTdXAsIFJldCBTdGQsIFJldCBTdXAsIEluZiBTdGQs"
    "IEluZiBTdXAKYW5zX29yZGVyID0gW10KZm9yIGkgaW4gcmFuZ2UoMyk6CiAgICBhbnNfb3JkZXIu"
    "YXBwZW5kKGJ1aWx0WyJzdGRfYW5zIl1baV0pCiAgICBhbnNfb3JkZXIuYXBwZW5kKGJ1aWx0WyJz"
    "dXBfYW5zIl1baV0pCm1lcmdlX3BkZnMoYW5zX29yZGVyLAogICAgICAgICAgICIvbW50L3VzZXIt"
    "ZGF0YS9vdXRwdXRzL1Q1VzJfQWxsX0Fuc3dlcnMucGRmIikKCiMgQ2xlYW4gdXAgaW5kaXZpZHVh"
    "bCBmaWxlcwppbXBvcnQgc2h1dGlsCnNodXRpbC5ybXRyZWUoT1VUX0RJUikKCnByaW50KCJEb25l"
    "LiIpCnByaW50KCIgIFQ1VzJfU3RhbmRhcmRfUHVwaWwucGRmOiIsIFBkZlJlYWRlcigiL21udC91"
    "c2VyLWRhdGEvb3V0cHV0cy9UNVcyX1N0YW5kYXJkX1B1cGlsLnBkZiIpLnBhZ2VzLl9fbGVuX18o"
    "KSwgInBhZ2VzIikKcHJpbnQoIiAgVDVXMl9TdXBwb3J0ZWRfUHVwaWwucGRmOiIsIFBkZlJlYWRl"
    "cigiL21udC91c2VyLWRhdGEvb3V0cHV0cy9UNVcyX1N1cHBvcnRlZF9QdXBpbC5wZGYiKS5wYWdl"
    "cy5fX2xlbl9fKCksICJwYWdlcyIpCnByaW50KCIgIFQ1VzJfQWxsX0Fuc3dlcnMucGRmOiIsIFBk"
    "ZlJlYWRlcigiL21udC91c2VyLWRhdGEvb3V0cHV0cy9UNVcyX0FsbF9BbnN3ZXJzLnBkZiIpLnBh"
    "Z2VzLl9fbGVuX18oKSwgInBhZ2VzIikK"
)

_SCRIPT_B64["replace_reading_pptx"] = (
    "IiIiClQ1VzIgUFBUWCBidWlsZGVyIOKAlCByZXBsYWNlcyBUNVcxIGNvbnRlbnQgaW4gZnJlc2hseSB1"
    "bnBhY2tlZCBYTUwuCldvcmtzIGRpcmVjdGx5IHdpdGggcmF3IFhNTCBzdHJpbmdzIG1hdGNoaW5nIHRo"
    "ZSBmaWxlIGVuY29kaW5nIGV4YWN0bHkuCiIiIgppbXBvcnQgc3lzLCByZSwgaHRtbApzeXMucGF0aC5p"
    "bnNlcnQoMCwgJy9ob21lL2NsYXVkZScpCmZyb20gdDV3Ml9jb250ZW50IGltcG9ydCAqCgpVTlBBQ0tF"
    "RCA9ICcvaG9tZS9jbGF1ZGUvdDV3Ml91bnBhY2tlZC9wcHQvc2xpZGVzJwoKCmRlZiByZWFkX3NsaWRl"
    "KG4pOgogICAgd2l0aCBvcGVuKGYne1VOUEFDS0VEfS9zbGlkZXtufS54bWwnLCBlbmNvZGluZz0ndXRm"
    "LTgnKSBhcyBmOgogICAgICAgIHJldHVybiBmLnJlYWQoKQoKCmRlZiB3cml0ZV9zbGlkZShuLCB4bWwp"
    "OgogICAgd2l0aCBvcGVuKGYne1VOUEFDS0VEfS9zbGlkZXtufS54bWwnLCAndycsIGVuY29kaW5nPSd1"
    "dGYtOCcpIGFzIGY6CiAgICAgICAgZi53cml0ZSh4bWwpCgoKZGVmIHRvX3htbCh0ZXh0KToKICAgICIi"
    "IkVuY29kZSBwbGFpbiB1bmljb2RlIHRvIFhNTCBtYXRjaGluZyBQUFRYIGZpbGUgc3R5bGUuCiAgICBF"
    "bSBkYXNoZXMgc3RheSBhcyBsaXRlcmFsIHVuaWNvZGU7IGN1cmx5IHF1b3Rlcy9hcG9zdHJvcGhlcyBi"
    "ZWNvbWUgZW50aXRpZXMuIiIiCiAgICByZXR1cm4gKHRleHQKICAgICAgICAgICAgLnJlcGxhY2UoJyYn"
    "LCAnJmFtcDsnKQogICAgICAgICAgICAucmVwbGFjZSgnXHUyMDFjJywgJyYjeDIwMUM7JykKICAgICAg"
    "ICAgICAgLnJlcGxhY2UoJ1x1MjAxZCcsICcmI3gyMDFEOycpCiAgICAgICAgICAgIC5yZXBsYWNlKCdc"
    "dTIwMTgnLCAnJiN4MjAxODsnKQogICAgICAgICAgICAucmVwbGFjZSgnXHUyMDE5JywgJyYjeDIwMTk7"
    "JykpCgoKZGVmIGdldF9ydW5fdGV4dCh4bWwsIHNlYXJjaF9zdGFydD0nJyk6CiAgICAiIiJFeHRyYWN0"
    "IHRoZSB0ZXh0IGluc2lkZSB0aGUgPGE6dD4gdGFnIHRoYXQgY29udGFpbnMgc2VhcmNoX3N0YXJ0LiIi"
    "IgogICAgaWR4ID0geG1sLmZpbmQoc2VhcmNoX3N0YXJ0KQogICAgaWYgaWR4ID09IC0xOgogICAgICAg"
    "IHJldHVybiBOb25lCiAgICAjIEZpbmQgdGhlIG9wZW5pbmcgPGE6dD4gYmVmb3JlIHRoaXMgcG9zaXRp"
    "b24KICAgIHRfc3RhcnQgPSB4bWwucmZpbmQoJzxhOnQ+JywgMCwgaWR4KQogICAgdF9lbmQgPSB4bWwu"
    "ZmluZCgnPC9hOnQ+JywgaWR4KQogICAgaWYgdF9zdGFydCA9PSAtMSBvciB0X2VuZCA9PSAtMToKICAg"
    "ICAgICByZXR1cm4gTm9uZQogICAgcmV0dXJuIHhtbFt0X3N0YXJ0ICsgNTogdF9lbmRdCgoKZGVmIHJl"
    "cGxhY2VfcnVuKHhtbCwgb2xkX3JhdywgbmV3X3JhdywgY291bnQ9MSk6CiAgICAiIiJSZXBsYWNlIG9s"
    "ZF9yYXcgd2l0aCBuZXdfcmF3IGluc2lkZSA8YTp0PiB0YWdzLiBvbGRfcmF3IGlzIHRoZSBleGFjdAog"
    "ICAgc3RyaW5nIGFzIGl0IGFwcGVhcnMgaW4gdGhlIFhNTCBmaWxlIChhbHJlYWR5IFhNTC1lbmNvZGVk"
    "KS4iIiIKICAgIGlmIG9sZF9yYXcgbm90IGluIHhtbDoKICAgICAgICBwcmludChmJyAgV0FSTklORzog"
    "bm90IGZvdW5kOiB7b2xkX3Jhd1s6NjBdIXJ9JykKICAgICAgICByZXR1cm4geG1sCiAgICByZXR1cm4g"
    "eG1sLnJlcGxhY2Uob2xkX3JhdywgbmV3X3JhdywgY291bnQpCgoKZGVmIHJlcGxhY2VfdGFnX3RleHQo"
    "eG1sLCBvbGRfcGxhaW4sIG5ld19wbGFpbiwgY291bnQ9MSk6CiAgICAiIiJSZXBsYWNlIHRleHQgYnkg"
    "ZW5jb2RpbmcgYm90aCBvbGQgYW5kIG5ldyB0byBYTUwgZmlyc3QuIiIiCiAgICBvbGRfeG1sID0gdG9f"
    "eG1sKG9sZF9wbGFpbikKICAgIG5ld194bWwgPSB0b194bWwobmV3X3BsYWluKQogICAgcmV0dXJuIHJl"
    "cGxhY2VfcnVuKHhtbCwgb2xkX3htbCwgbmV3X3htbCwgY291bnQpCgoKIyDilIDilIAgRXh0cmFjdCBU"
    "NVcxIHJhdyB0ZXh0cyBkaXJlY3RseSBmcm9tIHRoZSBYTUwgZmlsZXMg4pSA4pSA4pSA4pSA4pSA4pSA"
    "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSACiMgVGhp"
    "cyBhdm9pZHMgYW55IGVuY29kaW5nIGd1ZXNzd29yayDigJQgd2UgcmVhZCB3aGF0J3MgYWN0dWFsbHkg"
    "aW4gdGhlIGZpbGUuCgpkZWYgZXh0cmFjdF9hdF90ZXh0KHhtbCwgaGludCk6CiAgICAiIiJGaW5kIHRo"
    "ZSA8YTp0PiBjb250ZW50IGNvbnRhaW5pbmcgaGludC4gUmV0dXJucyByYXcgWE1MLWVuY29kZWQgc3Ry"
    "aW5nLiIiIgogICAgdCA9IGdldF9ydW5fdGV4dCh4bWwsIGhpbnQpCiAgICBpZiB0IGlzIE5vbmU6CiAg"
    "ICAgICAgIyBoaW50IG1pZ2h0IGJlIFhNTC1lbmNvZGVkCiAgICAgICAgdCA9IGdldF9ydW5fdGV4dCh4"
    "bWwsIHRvX3htbChoaW50KSkKICAgIHJldHVybiB0CgoKIyDilIDilIAgTGVzc29uIGRlZmluaXRpb25z"
    "IOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAoKU0xJREVTID0g"
    "ewogICAgJ1ZvY2FidWxhcnknOiB7J3RpdGxlJzogMiwgICd2b2NhYic6IDQsICAnd3JpdGU1JzogNSwg"
    "ICdyZWFkJzogNiwgICdsbyc6IDcsICAncHEnOiA4fSwKICAgICdSZXRyaWV2YWwnOiAgeyd0aXRsZSc6"
    "IDksICAndm9jYWInOiAxMSwgJ3dyaXRlNSc6IDEyLCAncmVhZCc6IDEzLCAnbG8nOiAxNCwgJ3BxJzog"
    "MTV9LAogICAgJ0luZmVyZW5jZSc6ICB7J3RpdGxlJzogMTYsICd2b2NhYic6IDE4LCAnd3JpdGU1Jzog"
    "MTksICdyZWFkJzogMjAsICdsbyc6IDIxLCAncHEnOiAyMn0sCn0KClQ1VzFfREFZUyA9IHsnVm9jYWJ1"
    "bGFyeSc6ICdNb25kYXknLCAnUmV0cmlldmFsJzogJ1R1ZXNkYXknLCAnSW5mZXJlbmNlJzogJ1dlZG5l"
    "c2RheSd9ClQ1VzJfREFZUyA9IHsnVm9jYWJ1bGFyeSc6ICdUdWVzZGF5JywgJ1JldHJpZXZhbCc6ICdU"
    "aHVyc2RheScsICdJbmZlcmVuY2UnOiAnRnJpZGF5J30KClQ1VzFfVk9DQUIgPSB7CiAgICAnVm9jYWJ1"
    "bGFyeSc6IFsKICAgICAgICAoJ2RpYWxvZ3VlJywgICAndGhlIHdvcmRzIHNwb2tlbiBiZXR3ZWVuIGNo"
    "YXJhY3RlcnMgaW4gYSBzdG9yeScpLAogICAgICAgICgncGVyc2lzdGVudCcsICdrZWVwaW5nIG9uIHRy"
    "eWluZyBhbmQgbm90IGdpdmluZyB1cCwgZXZlbiB3aGVuIGl0IGlzIGRpZmZpY3VsdCcpLAogICAgICAg"
    "ICgnc3VzcGljaW91cycsICdmZWVsaW5nIHRoYXQgc29tZXRoaW5nIGlzIHdyb25nIG9yIHRoYXQgc29t"
    "ZW9uZSBpcyBub3QgYmVpbmcgdHJ1dGhmdWwnKSwKICAgICAgICAoJ3JlcGV0aXRpb24nLCAnd2hlbiBz"
    "b21ldGhpbmcgaXMgc2FpZCBvciBkb25lIGFnYWluIGFuZCBhZ2FpbicpLAogICAgICAgICgncmV2ZWFs"
    "JywgICAgICd0byBzaG93IG9yIG1ha2Uga25vd24gc29tZXRoaW5nIHRoYXQgd2FzIGhpZGRlbicpLAog"
    "ICAgXSwKICAgICdSZXRyaWV2YWwnOiBbCiAgICAgICAgKCdwYXR0ZXJuJywgICAnYSByZXBlYXRlZCBk"
    "ZXNpZ24gb3Igc2VxdWVuY2UgdGhhdCBoZWxwcyB1cyBub3RpY2Ugd2hlbiBzb21ldGhpbmcgY2hhbmdl"
    "cycpLAogICAgICAgICgnZGVueScsICAgICAgJ3RvIHNheSB0aGF0IHNvbWV0aGluZyBpcyBub3QgdHJ1"
    "ZSBvciB0aGF0IHlvdSBkaWQgbm90IGRvIHNvbWV0aGluZycpLAogICAgICAgICgncG9saXRlbHknLCAg"
    "J2luIGEga2luZCBhbmQgcmVzcGVjdGZ1bCB3YXknKSwKICAgICAgICAoJ3Bhbmlja2VkJywgICdzdWRk"
    "ZW5seSBmZWVsaW5nIHZlcnkgd29ycmllZCBvciBmcmlnaHRlbmVkLCBvZnRlbiBjYXVzaW5nIGEgcnVz"
    "aGVkIHJlYWN0aW9uJyksCiAgICAgICAgKCdob3BlbGVzcycsICAnZmVlbGluZyB0aGF0IHRoZXJlIGlz"
    "IG5vIGNoYW5jZSBvZiB0aGluZ3MgZ2V0dGluZyBiZXR0ZXInKSwKICAgIF0sCiAgICAnSW5mZXJlbmNl"
    "JzogWwogICAgICAgICgndGVjaG5pcXVlJywgICdhIHBhcnRpY3VsYXIgd2F5IG9mIGRvaW5nIHNvbWV0"
    "aGluZywgZXNwZWNpYWxseSBpbiB3cml0aW5nIG9yIGFydCcpLAogICAgICAgICgnaW5mZXInLCAgICAg"
    "ICd0byB3b3JrIG91dCBzb21ldGhpbmcgdGhhdCBpcyBub3Qgc2FpZCBkaXJlY3RseSwgdXNpbmcgY2x1"
    "ZXMnKSwKICAgICAgICAoJ29taXNzaW9uJywgICAnd2hlbiBzb21ldGhpbmcgaXMgZGVsaWJlcmF0ZWx5"
    "IGxlZnQgb3V0IG9yIG5vdCBpbmNsdWRlZCcpLAogICAgICAgICgnZWNobycsICAgICAgICd3aGVuIHNv"
    "bWV0aGluZyBpcyByZXBlYXRlZCBpbiBhIHdheSB0aGF0IHJlbWluZHMgeW91IG9mIHNvbWV0aGluZyBl"
    "YXJsaWVyJyksCiAgICAgICAgKCdpbXByZXNzaW9uJywgJ3RoZSBmZWVsaW5nIG9yIGlkZWEgeW91IGFy"
    "ZSBsZWZ0IHdpdGggYWZ0ZXIgcmVhZGluZyBvciBzZWVpbmcgc29tZXRoaW5nJyksCiAgICBdLAp9CgpU"
    "NVcyX1ZPQ0FCID0gewogICAgJ1ZvY2FidWxhcnknOiBWT0NBQl9WT0MsCiAgICAnUmV0cmlldmFsJzog"
    "IFZPQ0FCX1JFVCwKICAgICdJbmZlcmVuY2UnOiAgVk9DQUJfSU5GLAp9CgpUNVcxX0ZPQ1VTID0geydW"
    "b2NhYnVsYXJ5JzogJ2RpYWxvZ3VlJywgJ1JldHJpZXZhbCc6ICdwYXR0ZXJuJywgJ0luZmVyZW5jZSc6"
    "ICdpbmZlcid9ClQ1VzJfRk9DVVMgPSB7J1ZvY2FidWxhcnknOiBGT0NVU19XT1JEX1ZPQywgJ1JldHJp"
    "ZXZhbCc6IEZPQ1VTX1dPUkRfUkVULCAnSW5mZXJlbmNlJzogRk9DVVNfV09SRF9JTkZ9CgpUNVcyX1RF"
    "WFRTID0geydWb2NhYnVsYXJ5JzogU1REX1ZPQywgJ1JldHJpZXZhbCc6IFNURF9SRVQsICdJbmZlcmVu"
    "Y2UnOiBTVERfSU5GfQoKVDVXMV9SRUFEX0lOU1RSID0gewogICAgJ1JldHJpZXZhbCc6ICdGbHVlbmN5"
    "IGZvY3VzJywgICAjIHBhcnRpYWwgbWF0Y2gg4oCUIGVub3VnaCB0byBmaW5kIGl0CiAgICAnSW5mZXJl"
    "bmNlJzogJ0ZsdWVuY3kgZm9jdXMgXHUyMDEzIEVjaG8gcmVhZCcsCn0KVDVXMl9SRUFEX0lOU1RSID0g"
    "ewogICAgJ1JldHJpZXZhbCc6ICdGbHVlbmN5IGZvY3VzIFx1MjAxMyBWb2x1bWUuICBUYWtlIHR1cm5z"
    "IHJlYWRpbmcgYWxvdWQgdG8gdGhlIHdob2xlIGNsYXNzLiAgUmVtZW1iZXIgdG8gcG9zaXRpb24geW91"
    "cnNlbGYgYW5kIHB1c2ggeW91ciB2b2ljZSBzbyBldmVyeW9uZSBjYW4gaGVhci4nLAogICAgJ0luZmVy"
    "ZW5jZSc6ICdGbHVlbmN5IGZvY3VzIFx1MjAxMyBFY2hvIHJlYWQnLAp9CgojIFQ1VzEgcHJhY3RpY2Ug"
    "USB0ZXh0IGZyYWdtZW50cyAoYXMgdGhleSBhcHBlYXIgcGxhaW4g4oCUIHdpbGwgYmUgWE1MLWVuY29k"
    "ZWQgZm9yIHNlYXJjaCkKVDVXMV9QUSA9IHsKICAgICdWb2NhYnVsYXJ5JzogewogICAgICAgICdxMSc6"
    "ICdUaGUgdGV4dCBzYXlzIEJlYXIgbm90aWNlZCBzb21ldGhpbmcgXHUyMDE4c3VzcGljaW91c1x1MjAx"
    "OSBhYm91dCB0aGUgcmFiYml0LiBXaGF0IGRvZXMgc3VzcGljaW91cyBzdWdnZXN0IGFib3V0IGhvdycs"
    "CiAgICAgICAgJ2ExJzogJ0l0IHN1Z2dlc3RzIEJlYXIgZmVsdCB1bmVhc3kgYW5kIGJlZ2FuIHRvIHNl"
    "bnNlIHRoYXQgc29tZXRoaW5nIHdhcyBub3QgcmlnaHQgYWJvdXQgdGhlIHJhYmJpdFx1MjAxOXMgYW5z"
    "d2VyLicsCiAgICAgICAgJ3EyJzogJ1RoZSB0ZXh0IHNheXMgZXZlcnkgd29yZCBtYXR0ZXJzIGluIHRo"
    "ZSBkaWFsb2d1ZS4gV2hhdCBkb2VzIHRoaXMgc3VnZ2VzdCBhYm91dCB0aGUgd3JpdGVyXHUyMDE5cyB1"
    "c2Ugb2YgbGFuZ3VhZ2U/JywKICAgICAgICAnYTInOiAnSXQgc3VnZ2VzdHMgdGhlIHdyaXRlciBoYXMg"
    "Y2hvc2VuIGVhY2ggd29yZCBjYXJlZnVsbHkgc28gdGhhdCBzbWFsbCBkZXRhaWxzIGdpdmUgdGhlIHJl"
    "YWRlciBpbXBvcnRhbnQgY2x1ZXMuJywKICAgIH0sCiAgICAnUmV0cmlldmFsJzogewogICAgICAgICdx"
    "MSc6ICdXaGF0IHF1ZXN0aW9uIGRvZXMgQmVhciBhc2sgZXZlcnkgYW5pbWFsIGhlIG1lZXRzIGluIHRo"
    "ZSBmb3Jlc3Q/JywKICAgICAgICAnYTEnOiAnQmVhciBhc2tzIGV2ZXJ5IGFuaW1hbCB0aGUgc2FtZSBx"
    "dWVzdGlvbjogXHUyMDFjSGF2ZSB5b3Ugc2VlbiBteSBoYXQ/XHUyMDFkJywKICAgICAgICAncTInOiAn"
    "SG93IGlzIHRoZSByYWJiaXRcdTIwMTlzIGFuc3dlciBkaWZmZXJlbnQgZnJvbSB0aGUgb3RoZXIgYW5p"
    "bWFsc1x1MjAxOSBhbnN3ZXJzPycsCiAgICAgICAgJ2EyJzogJ1RoZSBvdGhlciBhbmltYWxzIGdpdmUg"
    "c2hvcnQsIGNhbG0gcmVwbGllcy4gVGhlIHJhYmJpdCBzYXlzIFx1MjAxY05vLiBXaHkgYXJlIHlvdSBh"
    "c2tpbmcgbWU/IEkgd291bGQgbmV2ZXIgc3RlYWwgYSBoYXQuIEkgZG8gbm90IGV2ZW4gbGlrZSBoYXRz"
    "Llx1MjAxZCBOb2JvZHkgZWxzZSBtZW50aW9uZWQgc3RlYWxpbmcsIGxpa2luZyBoYXRzIG9yIGJlaW5n"
    "IGFza2VkIGFnYWluLicsCiAgICB9LAogICAgJ0luZmVyZW5jZSc6IHsKICAgICAgICAncTEnOiAnQmVh"
    "clx1MjAxOXMgYW5zd2VyIHRvIHRoZSBzcXVpcnJlbCBzb3VuZHMgYWxtb3N0IGV4YWN0bHkgbGlrZSB0"
    "aGUgcmFiYml0XHUyMDE5cyBlYXJsaWVyIGFuc3dlci4gV2h5IGRvZXMgdGhlIHdyaXRlcicsCiAgICAg"
    "ICAgJ2ExJzogJ1RoZSB3cml0ZXIgdXNlcyB0aGlzIHRvIHNob3cgdGhhdCBCZWFyIGlzIG5vdyBoaWRp"
    "bmcgc29tZXRoaW5nLCBqdXN0IGFzIHRoZSByYWJiaXQgd2FzIGhpZGluZyBzb21ldGhpbmcuIFRoZSBl"
    "Y2hvIG9mIHRoZSByYWJiaXRcdTIwMTlzIHdvcmRzIHJldmVhbHMgQmVhclx1MjAxOXMgZ3VpbHQuJywK"
    "ICAgICAgICAncTInOiAnV2hhdCB0ZWNobmlxdWUgZG9lcyB0aGUgd3JpdGVyIHVzZSB0byBtYWtlIHRo"
    "ZSBlbmRpbmcgcG93ZXJmdWw/IFVzZSBldmlkZW5jZSBmcm9tIHRoZSB0ZXh0LicsCiAgICAgICAgJ2Ey"
    "JzogJ1RoZSB3cml0ZXIgdXNlcyBvbWlzc2lvbiBcdTIwMTQgbGVhdmluZyBvdXQgd2hhdCBoYXBwZW5l"
    "ZCB0byB0aGUgcmFiYml0LiBUaGUgdGV4dCBzYXlzIHRoZSB3cml0ZXIgbmV2ZXIgdGVsbHMgdXMgZGly"
    "ZWN0bHkuIFRoaXMgbWFrZXMgdGhlIHJlYWRlciBpbmZlciB0aGUgZW5kaW5nIGZyb20gdGhlIGNsdWVz"
    "LCB3aGljaCBtYWtlcyBpdCBtb3JlIHBvd2VyZnVsLicsCiAgICB9LAp9CgpUNVcyX1BRID0gewogICAg"
    "J1ZvY2FidWxhcnknOiB7J3ExJzogV0VfRE9fVk9DWzBdWzBdLCAnYTEnOiBXRV9ET19WT0NbMF1bMV0s"
    "CiAgICAgICAgICAgICAgICAgICAncTInOiBXRV9ET19WT0NbMV1bMF0sICdhMic6IFdFX0RPX1ZPQ1sx"
    "XVsxXX0sCiAgICAnUmV0cmlldmFsJzogIHsncTEnOiBXRV9ET19SRVRbMF1bMF0sICdhMSc6IFdFX0RP"
    "X1JFVFswXVsxXSwKICAgICAgICAgICAgICAgICAgICdxMic6IFdFX0RPX1JFVFsxXVswXSwgJ2EyJzog"
    "V0VfRE9fUkVUWzFdWzFdfSwKICAgICdJbmZlcmVuY2UnOiAgeydxMSc6IFdFX0RPX0lORlswXVswXSwg"
    "J2ExJzogV0VfRE9fSU5GWzBdWzFdLAogICAgICAgICAgICAgICAgICAgJ3EyJzogV0VfRE9fSU5GWzFd"
    "WzBdLCAnYTInOiBXRV9ET19JTkZbMV1bMV19LAp9CgoKIyDilIDilIAgTWFpbiByZXBsYWNlbWVudCBs"
    "b29wIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAoKZm9yIGxlc3NvbiBpbiBb"
    "J1ZvY2FidWxhcnknLCAnUmV0cmlldmFsJywgJ0luZmVyZW5jZSddOgogICAgcyA9IFNMSURFU1tsZXNz"
    "b25dCiAgICBwcmludChmJ1xu4pSA4pSAIHtsZXNzb259IOKUgOKUgCcpCgogICAgIyBUaXRsZSBzbGlk"
    "ZTogZGF5IG5hbWUKICAgIHhtbCA9IHJlYWRfc2xpZGUoc1sndGl0bGUnXSkKICAgIHhtbCA9IHJlcGxh"
    "Y2VfcnVuKHhtbCwgVDVXMV9EQVlTW2xlc3Nvbl0sIFQ1VzJfREFZU1tsZXNzb25dKQogICAgd3JpdGVf"
    "c2xpZGUoc1sndGl0bGUnXSwgeG1sKQogICAgcHJpbnQoZicgIFRpdGxlOiB7VDVXMV9EQVlTW2xlc3Nv"
    "bl19IOKGkiB7VDVXMl9EQVlTW2xlc3Nvbl19JykKCiAgICAjIFZvY2FiIGhpZGRlbiBzbGlkZTogNSB3"
    "b3JkL2RlZmluaXRpb24gcGFpcnMKICAgIHhtbCA9IHJlYWRfc2xpZGUoc1sndm9jYWInXSkKICAgIGZv"
    "ciAob3csIG9kKSwgKG53LCBuZCkgaW4gemlwKFQ1VzFfVk9DQUJbbGVzc29uXSwgVDVXMl9WT0NBQlts"
    "ZXNzb25dKToKICAgICAgICB4bWwgPSByZXBsYWNlX3RhZ190ZXh0KHhtbCwgb3csIG53KQogICAgICAg"
    "IHhtbCA9IHJlcGxhY2VfdGFnX3RleHQoeG1sLCBvZCwgbmQpCiAgICAgICAgcHJpbnQoZicgIHtvdyFy"
    "fSDihpIge253IXJ9JykKICAgIHdyaXRlX3NsaWRlKHNbJ3ZvY2FiJ10sIHhtbCkKCiAgICAjIFdyaXRl"
    "LWl0LTUtdGltZXMgc2xpZGU6IGZvY3VzIHdvcmQgKGFwcGVhcnMgdHdpY2Ug4oCUIGluIHRhYmxlIGFu"
    "ZCBzcGlkZXIpCiAgICB4bWwgPSByZWFkX3NsaWRlKHNbJ3dyaXRlNSddKQogICAgb2xkX2YgPSBUNVcx"
    "X0ZPQ1VTW2xlc3Nvbl0KICAgIG5ld19mID0gVDVXMl9GT0NVU1tsZXNzb25dCiAgICAjIFJlcGxhY2Ug"
    "QUxMIG9jY3VycmVuY2VzCiAgICBjb3VudCA9IHhtbC5jb3VudChmJzxhOnQ+e29sZF9mfTwvYTp0Picp"
    "CiAgICB4bWwgPSB4bWwucmVwbGFjZShmJzxhOnQ+e29sZF9mfTwvYTp0PicsIGYnPGE6dD57bmV3X2Z9"
    "PC9hOnQ+JykKICAgIHdyaXRlX3NsaWRlKHNbJ3dyaXRlNSddLCB4bWwpCiAgICBwcmludChmJyAgRm9j"
    "dXMgd29yZDoge29sZF9mIXJ9IOKGkiB7bmV3X2Yhcn0gKHtjb3VudH0gb2NjdXJyZW5jZXMpJykKCiAg"
    "ICAjIEluZGVwZW5kZW50IFJlYWQgc2xpZGU6IGV4dHJhY3QgdGV4dCArIHJlYWRpbmcgaW5zdHJ1Y3Rp"
    "b24KICAgIHhtbCA9IHJlYWRfc2xpZGUoc1sncmVhZCddKQogICAgIyBFeHRyYWN0IHRoZSBUNVcxIHRl"
    "eHQgYXMgaXQgYXBwZWFycyByYXcgaW4gdGhlIFhNTAogICAgIyBGaW5kIGl0IGJ5IHNlYXJjaGluZyBm"
    "b3IgdGhlIHN0YXJ0CiAgICB0MV9oaW50cyA9IHsKICAgICAgICAnVm9jYWJ1bGFyeSc6ICdCZWFyIGhh"
    "ZCBsb3N0IGhpcyBoYXQnLAogICAgICAgICdSZXRyaWV2YWwnOiAnSW4gdGhlIHN0b3J5IEkgV2FudCBN"
    "eSBIYXQgQmFjaywgQmVhciBhc2tzIG1hbnknLAogICAgICAgICdJbmZlcmVuY2UnOiAnQXQgdGhlIGVu"
    "ZCBvZiB0aGUgc3RvcnksIEJlYXIgZmluZHMgdGhlIHJhYmJpdC4gVGhlIHdyaXRlciBkb2VzIG5vdCBk"
    "ZXNjcmliZScsCiAgICB9CiAgICBoaW50ID0gdDFfaGludHNbbGVzc29uXQogICAgdDFfcmF3ID0gZXh0"
    "cmFjdF9hdF90ZXh0KHhtbCwgaGludCkKICAgIGlmIHQxX3JhdzoKICAgICAgICB0Ml9yYXcgPSB0b194"
    "bWwoVDVXMl9URVhUU1tsZXNzb25dKQogICAgICAgIHhtbCA9IHhtbC5yZXBsYWNlKHQxX3JhdywgdDJf"
    "cmF3LCAxKQogICAgICAgIHByaW50KGYnICBUZXh0OiByZXBsYWNlZCAoe2xlbih0MV9yYXcpfSDihpIg"
    "e2xlbih0Ml9yYXcpfSBjaGFycyknKQogICAgZWxzZToKICAgICAgICBwcmludChmJyAgV0FSTklORzog"
    "Y291bGQgbm90IGZpbmQgZXh0cmFjdCB0ZXh0IGZvciB7bGVzc29ufScpCgogICAgIyBSZWFkaW5nIGlu"
    "c3RydWN0aW9uIChSZXRyaWV2YWwgYW5kIEluZmVyZW5jZSBvbmx5KQogICAgaWYgbGVzc29uID09ICdS"
    "ZXRyaWV2YWwnOgogICAgICAgICMgRmluZCB0aGUgZmx1ZW5jeSBmb2N1cyBpbnN0cnVjdGlvbgogICAg"
    "ICAgIGZpX2hpbnQgPSAnRmx1ZW5jeSBmb2N1cycKICAgICAgICBmaV9yYXcgPSBleHRyYWN0X2F0X3Rl"
    "eHQoeG1sLCBmaV9oaW50KQogICAgICAgIGlmIGZpX3JhdzoKICAgICAgICAgICAgeG1sID0geG1sLnJl"
    "cGxhY2UoZmlfcmF3LCB0b194bWwoVDVXMl9SRUFEX0lOU1RSWydSZXRyaWV2YWwnXSksIDEpCiAgICAg"
    "ICAgICAgIHByaW50KGYnICBGbHVlbmN5IGluc3RydWN0aW9uIHVwZGF0ZWQnKQoKICAgIHdyaXRlX3Ns"
    "aWRlKHNbJ3JlYWQnXSwgeG1sKQoKICAgICMgUHJhY3RpY2UgUSBzbGlkZTogUTEsIEExLCBRMiwgQTIs"
    "IGV4dHJhY3QKICAgIHhtbCA9IHJlYWRfc2xpZGUoc1sncHEnXSkKICAgIG9sZF9wcSA9IFQ1VzFfUFFb"
    "bGVzc29uXQogICAgbmV3X3BxID0gVDVXMl9QUVtsZXNzb25dCgogICAgIyBRMSAobWF5IGJlIHRydW5j"
    "YXRlZCBpbiBYTUwg4oCUIHNlYXJjaCBmb3Igc3RhcnQgZnJhZ21lbnQpCiAgICBxMV9yYXcgPSBleHRy"
    "YWN0X2F0X3RleHQoeG1sLCB0b194bWwob2xkX3BxWydxMSddWzo0MF0pKQogICAgaWYgcTFfcmF3Ogog"
    "ICAgICAgIHhtbCA9IHhtbC5yZXBsYWNlKHExX3JhdywgdG9feG1sKG5ld19wcVsncTEnXSksIDEpCiAg"
    "ICAgICAgcHJpbnQoZicgIFBRIFExIHJlcGxhY2VkJykKICAgIGVsc2U6CiAgICAgICAgcHJpbnQoZicg"
    "IFdBUk5JTkc6IFBRIFExIG5vdCBmb3VuZCcpCgogICAgYTFfcmF3ID0gZXh0cmFjdF9hdF90ZXh0KHht"
    "bCwgdG9feG1sKG9sZF9wcVsnYTEnXVs6NDBdKSkKICAgIGlmIGExX3JhdzoKICAgICAgICB4bWwgPSB4"
    "bWwucmVwbGFjZShhMV9yYXcsIHRvX3htbChuZXdfcHFbJ2ExJ10pLCAxKQogICAgICAgIHByaW50KGYn"
    "ICBQUSBBMSByZXBsYWNlZCcpCiAgICBlbHNlOgogICAgICAgIHByaW50KGYnICBXQVJOSU5HOiBQUSBB"
    "MSBub3QgZm91bmQnKQoKICAgIHEyX3JhdyA9IGV4dHJhY3RfYXRfdGV4dCh4bWwsIHRvX3htbChvbGRf"
    "cHFbJ3EyJ11bOjQwXSkpCiAgICBpZiBxMl9yYXc6CiAgICAgICAgeG1sID0geG1sLnJlcGxhY2UocTJf"
    "cmF3LCB0b194bWwobmV3X3BxWydxMiddKSwgMSkKICAgICAgICBwcmludChmJyAgUFEgUTIgcmVwbGFj"
    "ZWQnKQogICAgZWxzZToKICAgICAgICBwcmludChmJyAgV0FSTklORzogUFEgUTIgbm90IGZvdW5kJykK"
    "CiAgICBhMl9yYXcgPSBleHRyYWN0X2F0X3RleHQoeG1sLCB0b194bWwob2xkX3BxWydhMiddWzo0MF0p"
    "KQogICAgaWYgYTJfcmF3OgogICAgICAgIHhtbCA9IHhtbC5yZXBsYWNlKGEyX3JhdywgdG9feG1sKG5l"
    "d19wcVsnYTInXSksIDEpCiAgICAgICAgcHJpbnQoZicgIFBRIEEyIHJlcGxhY2VkJykKICAgIGVsc2U6"
    "CiAgICAgICAgcHJpbnQoZicgIFdBUk5JTkc6IFBRIEEyIG5vdCBmb3VuZCcpCgogICAgIyBFeHRyYWN0"
    "IHRleHQgaW4gUFEgc2xpZGUKICAgIHQxX3JhdyA9IGV4dHJhY3RfYXRfdGV4dCh4bWwsIGhpbnQpCiAg"
    "ICBpZiB0MV9yYXc6CiAgICAgICAgeG1sID0geG1sLnJlcGxhY2UodDFfcmF3LCB0b194bWwoVDVXMl9U"
    "RVhUU1tsZXNzb25dKSwgMSkKICAgICAgICBwcmludChmJyAgUFEgZXh0cmFjdCByZXBsYWNlZCcpCgog"
    "ICAgd3JpdGVfc2xpZGUoc1sncHEnXSwgeG1sKQoKcHJpbnQoJ1xuQWxsIGRvbmUuJykK"
)


_SCRIPT_B64["slide_finishing_fixes"] = (
    "IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiIKc2xpZGVfZmluaXNoaW5nX2ZpeGVz"
    "LnB5IOKAlCBBcHBseSBwZXJtYW5lbnQgZml4ZXMgdG8gYSBCZWluZy1hLVJlYWRl"
    "ciB1bnBhY2tlZCBzbGlkZSBkZWNrLgoKUnVuIHRoaXMgQUZURVIgY29udGVudCBy"
    "ZXBsYWNlbWVudCBhbmQgQkVGT1JFIHBhY2svY2xlYW4uIEl0IGFkZHJlc3NlcyBy"
    "ZWN1cnJpbmcKdGVtcGxhdGUgYnVncyB0aGF0IHdvdWxkIG90aGVyd2lzZSBuZWVk"
    "IG1hbnVhbCByZXBhaXIgZXZlcnkgd2VlazoKCjEuIFNsaWRlIDEzIChSZXRyaWV2"
    "YWwgUmVhZCkg4oCUIHJlbW92ZXMgdGhlIG9ycGhhbiBvdmVyc2l6ZWQgdGl0bGUg"
    "cnVuCiAgIGluaGVyaXRpbmcgc3o9NDQwMCBmcm9tIGRlZlJQci4gV2l0aG91dCB0"
    "aGlzIGZpeCB0aGUgZmx1ZW5jeSBpbnN0cnVjdGlvbgogICBhcHBlYXJzIGFzIGEg"
    "Z2lhbnQgaGVhZGluZyBhdCB0aGUgdG9wIG9mIHRoZSBzbGlkZS4KCjIuIEV4dHJh"
    "Y3QgdGV4dGJveCBmb250IG5vcm1hbGlzYXRpb24g4oCUIGV2ZXJ5IFJlYWQgYW5k"
    "IFBRIHNsaWRlIGV4dHJhY3QKICAgKHNsaWRlcyA2LCA4LCAxMywgMTUsIDIwLCAy"
    "MikgaXMgZm9yY2VkIHRvIHN6PTIyMDAgd2l0aCBhdXRvZml0IHNocmlua2FnZQog"
    "ICBzdHJpcHBlZC4gV2l0aG91dCB0aGlzIGZpeCB0aGUgUFEgZXh0cmFjdHMgcmVu"
    "ZGVyIHNtYWxsZXIgdGhhbiB0aGUgUmVhZAogICBleHRyYWN0cyB3aGVuIHRoZSB1"
    "bmRlcmx5aW5nIGJveGVzIGhhdmUgZGlmZmVyZW50IGN5IG9yIGF1dG9maXQgc2V0"
    "dGluZ3MuCgozLiBTcGlkZXIgZGlhZ3JhbSBmb2N1cyB3b3JkIGNlbnRyaW5nIChz"
    "bGlkZXMgNSwgMTIsIDE5KSDigJQgdGhlIHN0YW5kYWxvbmUKICAgZm9jdXMtd29y"
    "ZCB0ZXh0Ym94IGluICdPdGhlciBsaW5rZWQgd29yZHMnIGlzIHdpZGVuZWQgYW5k"
    "IHJlLWFuY2hvcmVkCiAgIHNvIHRoZSB3b3JkIHN0YXlzIGNlbnRyZWQgb24gdGhl"
    "IHNwaWRlciBsaW5lIGludGVyc2VjdGlvbiByZWdhcmRsZXNzIG9mCiAgIHdvcmQg"
    "bGVuZ3RoLiBXaXRob3V0IHRoaXMgZml4IHNob3J0ZXIgd29yZHMgc2l0IGxlZnQt"
    "b2YtY2VudHJlLgoKNC4gT3ZhbCBzaGFwZSB2ZXJ0aWNhbCBhbGlnbm1lbnQg4oCU"
    "IGV2ZXJ5IDxhOmJvZHlQcj4gb24gYW4gb3ZhbCBzaGFwZSBpcwogICBmb3JjZWQg"
    "dG8gYW5jaG9yPSJjdHIiIHNvIGNpcmNsZSB0ZXh0IGFsd2F5cyBzaXRzIG1pZGRs"
    "ZS1hbGlnbmVkLgogICBXaXRob3V0IHRoaXMgZml4IHNvbWUgJ0ZsdWVuY3kgJiBF"
    "eHByZXNzaW9uJyAvIGJhZGdlIGNpcmNsZXMgcmVuZGVyCiAgIHRvcC1hbGlnbmVk"
    "LgoKNS4gVGl0bGUgc2xpZGUgZGF5LW5hbWUgbGF5b3V0IChzbGlkZXMgMiwgOSwg"
    "MTYpIOKAlCB0aGUgZGF5IG5hbWUgaXMgZW5sYXJnZWQKICAgdG8gc3o9ODgwMCBh"
    "bmQgcmVwb3NpdGlvbmVkIGJlbG93ICdMZXNzb24gTiAtIFR5cGUnLCBhbmQgJ0Jl"
    "aW5nIGEgUmVhZGVyJyAvCiAgICdMZXNzb24gTicgYXJlIHNoaWZ0ZWQgdXAgdG8g"
    "bWFrZSByb29tLiBUaGlzIG1ha2VzIGVhY2ggbGVzc29uIGRheSBlYXN5CiAgIHRv"
    "IGxvY2F0ZSB3aGVuIHNjcm9sbGluZyB0aGUgZGVjay4KClVzYWdlOgogICAgcHl0"
    "aG9uMyBzbGlkZV9maW5pc2hpbmdfZml4ZXMucHkgL3BhdGgvdG8vdW5wYWNrZWQv"
    "CiIiIgppbXBvcnQgcmUsIG9zLCBzeXMKClVOUEFDS0VEID0gc3lzLmFyZ3ZbMV0g"
    "aWYgbGVuKHN5cy5hcmd2KSA+IDEgZWxzZSAnL2hvbWUvY2xhdWRlL3Q1dzNfdW5w"
    "YWNrZWQvJwpTTElERVMgPSBvcy5wYXRoLmpvaW4oVU5QQUNLRUQsICdwcHQnLCAn"
    "c2xpZGVzJykKCiMg4pSA4pSAIEZpeCAxOiBvdmVyc2l6ZWQgZmx1ZW5jeSB0aXRs"
    "ZSBvbiBSZXRyaWV2YWwgUmVhZCBzbGlkZSDilIDilIAKZGVmIGZpeF9yZXRyaWV2"
    "YWxfaHVnZV90aXRsZSgpOgogICAgcGF0aCA9IG9zLnBhdGguam9pbihTTElERVMs"
    "ICdzbGlkZTEzLnhtbCcpCiAgICBpZiBub3Qgb3MucGF0aC5leGlzdHMocGF0aCk6"
    "CiAgICAgICAgcmV0dXJuCiAgICB3aXRoIG9wZW4ocGF0aCkgYXMgZjoKICAgICAg"
    "ICB4ID0gZi5yZWFkKCkKICAgIG0gPSByZS5zZWFyY2gocic8cDpzcD4oPzooPyE8"
    "L3A6c3A+KS4pKj9uYW1lPSJUaXRsZSAxIig/Oig/ITwvcDpzcD4pLikqPzwvcDpz"
    "cD4nLAogICAgICAgICAgICAgICAgICB4LCByZS5ET1RBTEwpCiAgICBpZiBub3Qg"
    "bToKICAgICAgICByZXR1cm4KICAgIHRpdGxlX3NwID0gbS5ncm91cCgwKQogICAg"
    "YmFkID0gcmUuY29tcGlsZSgKICAgICAgICByJzxhOnI+XHMqPGE6clByIGxhbmc9"
    "ImVuLUdCIlxzKi8+XHMqPGE6dD5GbHVlbmN5IGZvY3VzW148XSo8L2E6dD5ccyo8"
    "L2E6cj4nLAogICAgICAgIHJlLkRPVEFMTAogICAgKQogICAgZml4ZWQgPSBiYWQu"
    "c3ViKCcnLCB0aXRsZV9zcCwgY291bnQ9MSkKICAgIGlmIGZpeGVkICE9IHRpdGxl"
    "X3NwOgogICAgICAgIHggPSB4LnJlcGxhY2UodGl0bGVfc3AsIGZpeGVkKQogICAg"
    "ICAgIHdpdGggb3BlbihwYXRoLCAndycpIGFzIGY6CiAgICAgICAgICAgIGYud3Jp"
    "dGUoeCkKICAgICAgICBwcmludCgnICBGaXggMTogcmVtb3ZlZCBodWdlIHRpdGxl"
    "IHJ1biBmcm9tIHNsaWRlIDEzJykKCiMg4pSA4pSAIEZpeCAyOiBleHRyYWN0IHRl"
    "eHRib3ggZm9udCBzaXplIG5vcm1hbGlzYXRpb24g4pSA4pSACkVYVFJBQ1RfU0xJ"
    "REVTID0gWzYsIDgsIDEzLCAxNSwgMjAsIDIyXQpUQVJHRVRfRVhUUkFDVF9TWiA9"
    "ICcyMjAwJwoKZGVmIGZpeF9leHRyYWN0X3NpemVzKCk6CiAgICBmb3IgbiBpbiBF"
    "WFRSQUNUX1NMSURFUzoKICAgICAgICBwYXRoID0gb3MucGF0aC5qb2luKFNMSURF"
    "UywgZidzbGlkZXtufS54bWwnKQogICAgICAgIGlmIG5vdCBvcy5wYXRoLmV4aXN0"
    "cyhwYXRoKToKICAgICAgICAgICAgY29udGludWUKICAgICAgICB3aXRoIG9wZW4o"
    "cGF0aCkgYXMgZjoKICAgICAgICAgICAgeCA9IGYucmVhZCgpCiAgICAgICAgb3Jp"
    "Z2luYWwgPSB4CiAgICAgICAgc3BfcmUgPSByZS5jb21waWxlKHInPHA6c3A+Lio/"
    "PC9wOnNwPicsIHJlLkRPVEFMTCkKICAgICAgICBmb3Igc3AgaW4gc3BfcmUuZmlu"
    "ZGFsbCh4KToKICAgICAgICAgICAgdGV4dHMgPSByZS5maW5kYWxsKHInPGE6dD4o"
    "W148XSopPC9hOnQ+Jywgc3ApCiAgICAgICAgICAgIGlzX2V4dHJhY3QgPSBhbnko"
    "CiAgICAgICAgICAgICAgICBsZW4odCkgPiAyMDAgYW5kIGFueShrdyBpbiB0Lmxv"
    "d2VyKCkgZm9yIGt3IGluCiAgICAgICAgICAgICAgICAgICAgKCdzb3VuZCcsICdk"
    "cnVtJywgJ2VhcmRydW0nLCAndmlicmF0ZScsICd3YXZlJywgJ2JlYXInLCAncmFi"
    "Yml0JykpCiAgICAgICAgICAgICAgICBmb3IgdCBpbiB0ZXh0cwogICAgICAgICAg"
    "ICApCiAgICAgICAgICAgIGlmIG5vdCBpc19leHRyYWN0OgogICAgICAgICAgICAg"
    "ICAgY29udGludWUKICAgICAgICAgICAgbmV3X3NwID0gc3AKICAgICAgICAgICAg"
    "bmV3X3NwID0gcmUuc3ViKAogICAgICAgICAgICAgICAgcic8YTpub3JtQXV0b2Zp"
    "dFxzK2ZvbnRTY2FsZT0iXGQrIlxzK2xuU3BjUmVkdWN0aW9uPSJcZCsiXHMqLz4n"
    "LAogICAgICAgICAgICAgICAgJzxhOm5vcm1BdXRvZml0Lz4nLCBuZXdfc3AKICAg"
    "ICAgICAgICAgKQogICAgICAgICAgICBuZXdfc3AgPSByZS5zdWIocidzej0iXGQr"
    "IicsIGYnc3o9IntUQVJHRVRfRVhUUkFDVF9TWn0iJywgbmV3X3NwKQogICAgICAg"
    "ICAgICBpZiBuZXdfc3AgIT0gc3A6CiAgICAgICAgICAgICAgICB4ID0geC5yZXBs"
    "YWNlKHNwLCBuZXdfc3ApCiAgICAgICAgaWYgeCAhPSBvcmlnaW5hbDoKICAgICAg"
    "ICAgICAgd2l0aCBvcGVuKHBhdGgsICd3JykgYXMgZjoKICAgICAgICAgICAgICAg"
    "IGYud3JpdGUoeCkKICAgICAgICAgICAgcHJpbnQoZicgIEZpeCAyOiBub3JtYWxp"
    "c2VkIGV4dHJhY3Qgc2l6ZSBvbiBzbGlkZSB7bn0nKQoKIyDilIDilIAgRml4IDM6"
    "IHNwaWRlciBmb2N1cyB3b3JkIGNlbnRyaW5nIOKUgOKUgApXUklURTVfU0xJREVT"
    "ID0gWzUsIDEyLCAxOV0KTkVXX0ZPQ1VTX0NYID0gMjQwMDAwMApORVdfRk9DVVNf"
    "Q1kgPSA0ODAwMDAKCmRlZiBmaXhfZm9jdXNfd29yZF9jZW50cmluZygpOgogICAg"
    "Zm9yIG4gaW4gV1JJVEU1X1NMSURFUzoKICAgICAgICBwYXRoID0gb3MucGF0aC5q"
    "b2luKFNMSURFUywgZidzbGlkZXtufS54bWwnKQogICAgICAgIGlmIG5vdCBvcy5w"
    "YXRoLmV4aXN0cyhwYXRoKToKICAgICAgICAgICAgY29udGludWUKICAgICAgICB3"
    "aXRoIG9wZW4ocGF0aCkgYXMgZjoKICAgICAgICAgICAgeCA9IGYucmVhZCgpCiAg"
    "ICAgICAgc3BfcmUgPSByZS5jb21waWxlKHInPHA6c3A+Lio/PC9wOnNwPicsIHJl"
    "LkRPVEFMTCkKICAgICAgICBmb3Igc3AgaW4gc3BfcmUuZmluZGFsbCh4KToKICAg"
    "ICAgICAgICAgdGV4dHMgPSByZS5maW5kYWxsKHInPGE6dD4oW148XSopPC9hOnQ+"
    "Jywgc3ApCiAgICAgICAgICAgIGlmIGxlbih0ZXh0cykgPT0gMSBhbmQgdGV4dHNb"
    "MF0uc3RyaXAoKSBhbmQgXAogICAgICAgICAgICAgICAnc3BBdXRvRml0JyBpbiBz"
    "cCBhbmQgJ3dyYXA9Im5vbmUiJyBpbiBzcDoKICAgICAgICAgICAgICAgIG9mZl9t"
    "ID0gcmUuc2VhcmNoKHInPGE6b2ZmIHg9IihcZCspIiB5PSIoXGQrKSInLCBzcCkK"
    "ICAgICAgICAgICAgICAgIGV4dF9tID0gcmUuc2VhcmNoKHInPGE6ZXh0IGN4PSIo"
    "XGQrKSIgY3k9IihcZCspIicsIHNwKQogICAgICAgICAgICAgICAgaWYgbm90IChv"
    "ZmZfbSBhbmQgZXh0X20pOgogICAgICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAg"
    "ICAgICAgICAgICAgICBveCwgb3kgPSBtYXAoaW50LCBvZmZfbS5ncm91cHMoKSkK"
    "ICAgICAgICAgICAgICAgIG9jeCwgb2N5ID0gbWFwKGludCwgZXh0X20uZ3JvdXBz"
    "KCkpCiAgICAgICAgICAgICAgICBjeF9jZW50cmUgPSBveCArIG9jeCAvLyAyCiAg"
    "ICAgICAgICAgICAgICBjeV9jZW50cmUgPSBveSArIG9jeSAvLyAyCiAgICAgICAg"
    "ICAgICAgICBuZXdfeF9vZmYgPSBjeF9jZW50cmUgLSBORVdfRk9DVVNfQ1ggLy8g"
    "MgogICAgICAgICAgICAgICAgbmV3X3lfb2ZmID0gY3lfY2VudHJlIC0gTkVXX0ZP"
    "Q1VTX0NZIC8vIDIKICAgICAgICAgICAgICAgIGZpeGVkID0gc3AKICAgICAgICAg"
    "ICAgICAgIGZpeGVkID0gcmUuc3ViKAogICAgICAgICAgICAgICAgICAgIHInPGE6"
    "b2ZmIHg9IlxkKyIgeT0iXGQrIi8+JywKICAgICAgICAgICAgICAgICAgICBmJzxh"
    "Om9mZiB4PSJ7bmV3X3hfb2ZmfSIgeT0ie25ld195X29mZn0iLz4nLCBmaXhlZCwg"
    "Y291bnQ9MQogICAgICAgICAgICAgICAgKQogICAgICAgICAgICAgICAgZml4ZWQg"
    "PSByZS5zdWIoCiAgICAgICAgICAgICAgICAgICAgcic8YTpleHQgY3g9IlxkKyIg"
    "Y3k9IlxkKyIvPicsCiAgICAgICAgICAgICAgICAgICAgZic8YTpleHQgY3g9IntO"
    "RVdfRk9DVVNfQ1h9IiBjeT0ie05FV19GT0NVU19DWX0iLz4nLAogICAgICAgICAg"
    "ICAgICAgICAgIGZpeGVkLCBjb3VudD0xCiAgICAgICAgICAgICAgICApCiAgICAg"
    "ICAgICAgICAgICBmaXhlZCA9IHJlLnN1YigKICAgICAgICAgICAgICAgICAgICBy"
    "JzxhOmJvZHlQcltePl0qPlxzKjxhOnNwQXV0b0ZpdC8+XHMqPC9hOmJvZHlQcj4n"
    "LAogICAgICAgICAgICAgICAgICAgICc8YTpib2R5UHIgd3JhcD0ic3F1YXJlIiBy"
    "dGxDb2w9IjAiIGFuY2hvcj0iY3RyIi8+JywgZml4ZWQKICAgICAgICAgICAgICAg"
    "ICkKICAgICAgICAgICAgICAgIGZpeGVkID0gcmUuc3ViKAogICAgICAgICAgICAg"
    "ICAgICAgIHInPGE6cD5ccyo8YTpyPicsCiAgICAgICAgICAgICAgICAgICAgJzxh"
    "OnA+PGE6cFByIGFsZ249ImN0ciIvPjxhOnI+JywgZml4ZWQsIGNvdW50PTEKICAg"
    "ICAgICAgICAgICAgICkKICAgICAgICAgICAgICAgIGlmIGZpeGVkICE9IHNwOgog"
    "ICAgICAgICAgICAgICAgICAgIHggPSB4LnJlcGxhY2Uoc3AsIGZpeGVkKQogICAg"
    "ICAgICAgICAgICAgICAgIHdpdGggb3BlbihwYXRoLCAndycpIGFzIGY6CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIGYud3JpdGUoeCkKICAgICAgICAgICAgICAgICAg"
    "ICBwcmludChmJyAgRml4IDM6IGNlbnRyZWQgZm9jdXMgd29yZCAie3RleHRzWzBd"
    "fSIgb24gc2xpZGUge259JykKICAgICAgICAgICAgICAgIGJyZWFrCgojIOKUgOKU"
    "gCBGaXggNDogb3ZhbCBhbmNob3I9Y3RyIOKUgOKUgApkZWYgZml4X292YWxfYW5j"
    "aG9ycygpOgogICAgZm9yIGZuIGluIG9zLmxpc3RkaXIoU0xJREVTKToKICAgICAg"
    "ICBpZiBub3QgKGZuLnN0YXJ0c3dpdGgoJ3NsaWRlJykgYW5kIGZuLmVuZHN3aXRo"
    "KCcueG1sJykpOgogICAgICAgICAgICBjb250aW51ZQogICAgICAgIHBhdGggPSBv"
    "cy5wYXRoLmpvaW4oU0xJREVTLCBmbikKICAgICAgICB3aXRoIG9wZW4ocGF0aCkg"
    "YXMgZjoKICAgICAgICAgICAgeCA9IGYucmVhZCgpCiAgICAgICAgb3JpZ2luYWwg"
    "PSB4CiAgICAgICAgc3BfcmUgPSByZS5jb21waWxlKHInPHA6c3A+Lio/PC9wOnNw"
    "PicsIHJlLkRPVEFMTCkKICAgICAgICBmb3Igc3AgaW4gc3BfcmUuZmluZGFsbCh4"
    "KToKICAgICAgICAgICAgaXNfb3ZhbCA9ICdwcnN0PSJlbGxpcHNlIicgaW4gc3Ag"
    "b3IgJ25hbWU9Ik92YWwnIGluIHNwCiAgICAgICAgICAgIGhhc190ZXh0ID0gYm9v"
    "bChyZS5zZWFyY2gocic8YTp0PltePF0rPC9hOnQ+Jywgc3ApKQogICAgICAgICAg"
    "ICBpZiBub3QgKGlzX292YWwgYW5kIGhhc190ZXh0KToKICAgICAgICAgICAgICAg"
    "IGNvbnRpbnVlCiAgICAgICAgICAgIG5ld19zcCA9IHNwCiAgICAgICAgICAgIGlm"
    "IHJlLnNlYXJjaChyJzxhOmJvZHlQcltePl0qYW5jaG9yPSJcdysiJywgbmV3X3Nw"
    "KToKICAgICAgICAgICAgICAgIG5ld19zcCA9IHJlLnN1YihyJyg8YTpib2R5UHJb"
    "Xj5dKj8pYW5jaG9yPSJcdysiJywKICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICByJ1wxYW5jaG9yPSJjdHIiJywgbmV3X3NwLCBjb3VudD0xKQogICAgICAg"
    "ICAgICBlbHNlOgogICAgICAgICAgICAgICAgbmV3X3NwID0gcmUuc3ViKHInKDxh"
    "OmJvZHlQcig/OltePl0qPykpKC8/PiknLAogICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAgIHInXDEgYW5jaG9yPSJjdHIiXDInLCBuZXdfc3AsIGNvdW50PTEp"
    "CiAgICAgICAgICAgIGlmIG5ld19zcCAhPSBzcDoKICAgICAgICAgICAgICAgIHgg"
    "PSB4LnJlcGxhY2Uoc3AsIG5ld19zcCkKICAgICAgICBpZiB4ICE9IG9yaWdpbmFs"
    "OgogICAgICAgICAgICB3aXRoIG9wZW4ocGF0aCwgJ3cnKSBhcyBmOgogICAgICAg"
    "ICAgICAgICAgZi53cml0ZSh4KQogICAgICAgICAgICBwcmludChmJyAgRml4IDQ6"
    "IGZvcmNlZCBhbmNob3I9Y3RyIG9uIG92YWxzIGluIHtmbn0nKQoKIyDilIDilIAg"
    "Rml4IDU6IHRpdGxlIHNsaWRlIGRheS1uYW1lIGxheW91dCDilIDilIAKVElUTEVf"
    "U0xJREVTID0gezI6ICdUdWVzZGF5JywgOTogJ1RodXJzZGF5JywgMTY6ICdGcmlk"
    "YXknfQpORVdfVElUTEVfWSA9ICcyMDE3NDc3JyAgICMgQmVpbmcgYSBSZWFkZXIg"
    "eQpORVdfTEVTU09OX1kgPSAnNDU1MjE0MScgICMgTGVzc29uIE4gLSBUeXBlIHkK"
    "REFZX1ggPSAnNDQyMzU3NycKREFZX1kgPSAnNTE5OTYxMCcKREFZX0NYID0gJzMz"
    "Mjk3NTgnCkRBWV9DWSA9ICcxNDQ2NTUwJwpEQVlfU1ogPSAnODgwMCcKCmRlZiBm"
    "aXhfdGl0bGVfZGF5X2xheW91dCgpOgogICAgZm9yIG4sIGRheV9uYW1lIGluIFRJ"
    "VExFX1NMSURFUy5pdGVtcygpOgogICAgICAgIHBhdGggPSBvcy5wYXRoLmpvaW4o"
    "U0xJREVTLCBmJ3NsaWRle259LnhtbCcpCiAgICAgICAgaWYgbm90IG9zLnBhdGgu"
    "ZXhpc3RzKHBhdGgpOgogICAgICAgICAgICBjb250aW51ZQogICAgICAgIHdpdGgg"
    "b3BlbihwYXRoKSBhcyBmOgogICAgICAgICAgICB4ID0gZi5yZWFkKCkKCiAgICAg"
    "ICAgc3BfcmUgPSByZS5jb21waWxlKHInPHA6c3A+Lio/PC9wOnNwPicsIHJlLkRP"
    "VEFMTCkKCiAgICAgICAgZm9yIHNwIGluIHNwX3JlLmZpbmRhbGwoeCk6CiAgICAg"
    "ICAgICAgIHRleHRzID0gcmUuZmluZGFsbChyJzxhOnQ+KFtePF0qKTwvYTp0Pics"
    "IHNwKQogICAgICAgICAgICBjbGVhbiA9IFt0IGZvciB0IGluIHRleHRzIGlmIHQu"
    "c3RyaXAoKV0KICAgICAgICAgICAgaWYgbm90IGNsZWFuOgogICAgICAgICAgICAg"
    "ICAgY29udGludWUKCiAgICAgICAgICAgICMgMSkgVGl0bGUgMSAoQmVpbmcgYSBS"
    "ZWFkZXIpOiBtb3ZlIHkgdG8gTkVXX1RJVExFX1kKICAgICAgICAgICAgaWYgJ0Jl"
    "aW5nIGEgUmVhZGVyJyBpbiBjbGVhbjoKICAgICAgICAgICAgICAgIGZpeGVkID0g"
    "cmUuc3ViKAogICAgICAgICAgICAgICAgICAgIHInKDxhOm9mZiB4PSItP1xkKyIg"
    "eT0iKS0/XGQrKCIpJywKICAgICAgICAgICAgICAgICAgICBsYW1iZGEgbTogbS5n"
    "cm91cCgxKSArIE5FV19USVRMRV9ZICsgbS5ncm91cCgyKSwKICAgICAgICAgICAg"
    "ICAgICAgICBzcCwgY291bnQ9MQogICAgICAgICAgICAgICAgKQogICAgICAgICAg"
    "ICAgICAgaWYgZml4ZWQgIT0gc3A6CiAgICAgICAgICAgICAgICAgICAgeCA9IHgu"
    "cmVwbGFjZShzcCwgZml4ZWQpCgogICAgICAgICAgICAjIDIpIExlc3NvbiBOIC0g"
    "VHlwZTogbW92ZSB5IHRvIE5FV19MRVNTT05fWQogICAgICAgICAgICBlbGlmIGFu"
    "eSgnTGVzc29uJyBpbiB0IGFuZCAnIC0gJyBpbiB0IGZvciB0IGluIGNsZWFuKToK"
    "ICAgICAgICAgICAgICAgIGZpeGVkID0gcmUuc3ViKAogICAgICAgICAgICAgICAg"
    "ICAgIHInKDxhOm9mZiB4PSItP1xkKyIgeT0iKS0/XGQrKCIpJywKICAgICAgICAg"
    "ICAgICAgICAgICBsYW1iZGEgbTogbS5ncm91cCgxKSArIE5FV19MRVNTT05fWSAr"
    "IG0uZ3JvdXAoMiksCiAgICAgICAgICAgICAgICAgICAgc3AsIGNvdW50PTEKICAg"
    "ICAgICAgICAgICAgICkKICAgICAgICAgICAgICAgIGlmIGZpeGVkICE9IHNwOgog"
    "ICAgICAgICAgICAgICAgICAgIHggPSB4LnJlcGxhY2Uoc3AsIGZpeGVkKQoKICAg"
    "ICAgICAgICAgIyAzKSBEYXkgdGV4dDogZW5sYXJnZSBhbmQgcmVwb3NpdGlvbgog"
    "ICAgICAgICAgICBlbGlmIGNsZWFuID09IFtkYXlfbmFtZV06CiAgICAgICAgICAg"
    "ICAgICBmaXhlZCA9IHNwCiAgICAgICAgICAgICAgICBmaXhlZCA9IHJlLnN1YigK"
    "ICAgICAgICAgICAgICAgICAgICByJzxhOm9mZiB4PSItP1xkKyIgeT0iLT9cZCsi"
    "Lz4nLAogICAgICAgICAgICAgICAgICAgIGYnPGE6b2ZmIHg9IntEQVlfWH0iIHk9"
    "IntEQVlfWX0iLz4nLAogICAgICAgICAgICAgICAgICAgIGZpeGVkLCBjb3VudD0x"
    "CiAgICAgICAgICAgICAgICApCiAgICAgICAgICAgICAgICBmaXhlZCA9IHJlLnN1"
    "YigKICAgICAgICAgICAgICAgICAgICByJzxhOmV4dCBjeD0iXGQrIiBjeT0iXGQr"
    "Ii8+JywKICAgICAgICAgICAgICAgICAgICBmJzxhOmV4dCBjeD0ie0RBWV9DWH0i"
    "IGN5PSJ7REFZX0NZfSIvPicsCiAgICAgICAgICAgICAgICAgICAgZml4ZWQsIGNv"
    "dW50PTEKICAgICAgICAgICAgICAgICkKICAgICAgICAgICAgICAgICMgQ2VudHJl"
    "IGFsaWdubWVudCBpbiBwUHIKICAgICAgICAgICAgICAgIGlmIHJlLnNlYXJjaChy"
    "JzxhOnBQclteL10qLz4nLCBmaXhlZCk6CiAgICAgICAgICAgICAgICAgICAgZml4"
    "ZWQgPSByZS5zdWIoCiAgICAgICAgICAgICAgICAgICAgICAgIHInPGE6cFByKFte"
    "L10qKS8+JywKICAgICAgICAgICAgICAgICAgICAgICAgbGFtYmRhIG06ICc8YTpw"
    "UHInICsgbS5ncm91cCgxKSArICgnIGFsZ249ImN0ciInIGlmICdhbGduPScgbm90"
    "IGluIG0uZ3JvdXAoMSkgZWxzZSAnJykgKyAnLz4nLAogICAgICAgICAgICAgICAg"
    "ICAgICAgICBmaXhlZCwgY291bnQ9MQogICAgICAgICAgICAgICAgICAgICkKICAg"
    "ICAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICAgICAgZml4ZWQgPSBy"
    "ZS5zdWIoCiAgICAgICAgICAgICAgICAgICAgICAgIHInKDxhOnA+KVxzKig8YTpy"
    "PiknLAogICAgICAgICAgICAgICAgICAgICAgICByJ1wxPGE6cFByIGFsZ249ImN0"
    "ciIvPlwyJywgZml4ZWQsIGNvdW50PTEKICAgICAgICAgICAgICAgICAgICApCiAg"
    "ICAgICAgICAgICAgICAjIEZvcmNlIHN6PURBWV9TWiBvbiByUHIKICAgICAgICAg"
    "ICAgICAgIGlmIHJlLnNlYXJjaChyJzxhOnJQclteL10qc3o9IlxkKyInLCBmaXhl"
    "ZCk6CiAgICAgICAgICAgICAgICAgICAgZml4ZWQgPSByZS5zdWIoCiAgICAgICAg"
    "ICAgICAgICAgICAgICAgIHInKDxhOnJQcltePl0qPylzej0iXGQrIicsCiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIGYnXFwxc3o9IntEQVlfU1p9IicsIGZpeGVkLCBj"
    "b3VudD0xCiAgICAgICAgICAgICAgICAgICAgKQogICAgICAgICAgICAgICAgZWxz"
    "ZToKICAgICAgICAgICAgICAgICAgICBmaXhlZCA9IHJlLnN1YigKICAgICAgICAg"
    "ICAgICAgICAgICAgICAgcic8YTpyUHIgbGFuZz0iZW4tR0IiXHMqLz4nLAogICAg"
    "ICAgICAgICAgICAgICAgICAgICBmJzxhOnJQciBsYW5nPSJlbi1HQiIgc3o9IntE"
    "QVlfU1p9Ii8+JywKICAgICAgICAgICAgICAgICAgICAgICAgZml4ZWQsIGNvdW50"
    "PTEKICAgICAgICAgICAgICAgICAgICApCiAgICAgICAgICAgICAgICAjIGFuY2hv"
    "cj1jdHIKICAgICAgICAgICAgICAgIGlmIHJlLnNlYXJjaChyJzxhOmJvZHlQclte"
    "Pl0qYW5jaG9yPScsIGZpeGVkKToKICAgICAgICAgICAgICAgICAgICBmaXhlZCA9"
    "IHJlLnN1YigKICAgICAgICAgICAgICAgICAgICAgICAgcicoPGE6Ym9keVByW14+"
    "XSo/KWFuY2hvcj0iXHcrIicsCiAgICAgICAgICAgICAgICAgICAgICAgIHInXDFh"
    "bmNob3I9ImN0ciInLCBmaXhlZCwgY291bnQ9MQogICAgICAgICAgICAgICAgICAg"
    "ICkKICAgICAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICAgICAgZml4"
    "ZWQgPSByZS5zdWIoCiAgICAgICAgICAgICAgICAgICAgICAgIHInKDxhOmJvZHlQ"
    "cig/OltePl0qPykpKC8/PiknLAogICAgICAgICAgICAgICAgICAgICAgICByJ1wx"
    "IGFuY2hvcj0iY3RyIlwyJywgZml4ZWQsIGNvdW50PTEKICAgICAgICAgICAgICAg"
    "ICAgICApCiAgICAgICAgICAgICAgICBpZiBmaXhlZCAhPSBzcDoKICAgICAgICAg"
    "ICAgICAgICAgICB4ID0geC5yZXBsYWNlKHNwLCBmaXhlZCkKCiAgICAgICAgd2l0"
    "aCBvcGVuKHBhdGgsICd3JykgYXMgZjoKICAgICAgICAgICAgZi53cml0ZSh4KQog"
    "ICAgICAgIHByaW50KGYnICBGaXggNTogZW5sYXJnZWQgZGF5ICJ7ZGF5X25hbWV9"
    "IiBvbiBzbGlkZSB7bn0nKQoKaWYgX19uYW1lX18gPT0gJ19fbWFpbl9fJzoKICAg"
    "IHByaW50KCdBcHBseWluZyBzbGlkZSBmaW5pc2hpbmcgZml4ZXMuLi4nKQogICAg"
    "Zml4X3JldHJpZXZhbF9odWdlX3RpdGxlKCkKICAgIGZpeF9leHRyYWN0X3NpemVz"
    "KCkKICAgIGZpeF9mb2N1c193b3JkX2NlbnRyaW5nKCkKICAgIGZpeF9vdmFsX2Fu"
    "Y2hvcnMoKQogICAgZml4X3RpdGxlX2RheV9sYXlvdXQoKQogICAgcHJpbnQoJ0Rv"
    "bmUuJykK"
)


os.makedirs('/home/claude', exist_ok=True)
for name, b64_parts in _SCRIPT_B64.items():
    b64 = b64_parts if isinstance(b64_parts, str) else ''.join(b64_parts)
    with open(f'/home/claude/{name}.py', 'wb') as f:
        f.write(base64.b64decode(b64))
    print(f"Extracted {name}.py")
```

Run the above block in a bash_tool python3 call at session start. The scripts will be at:
- `/home/claude/build_reading_pdfs.py` — PDF builder (ReportLab)
- `/home/claude/replace_reading_pptx.py` — PPTX XML replacement script
- `/home/claude/slide_finishing_fixes.py` — MANDATORY post-replacement template repair (see Step 5b)

The previous week's PPTX must still be provided by Innes as a project file or upload — it cannot be embedded here due to size.
