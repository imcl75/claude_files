---
name: being-a-reader
description: "Create a full week of Being a Reader reading comprehension resources for Y4 or Y5. Use this skill whenever Innes asks for reading lessons, Being a Reader lessons, reading comprehension resources, vocabulary/retrieval/inference lessons, or says things like 'make this week's reading', 'create the reading for next week', 'Being a Reader for [text]', 'reading lessons linked to [book]'. Also trigger when he uploads content and mentions reading questions, comprehension questions, or refers to the three-lesson reading cycle. This skill produces 5 files: 3 PDFs (Standard Pupil, Supported Pupil, All Answers), 1 PPTX (teaching slides), and 1 XLSX (content data file). Always use this skill even for partial requests like 'just the PDFs' or 'just the PPTX' — the skill handles selective output. Always ask year group (Y4/Y5) at session start."
---

# Being a Reader Skill

## Overview

Being a Reader is Innes's weekly reading comprehension system. Each week produces **5 files** from a single set of content:

1. **XLSX** — master data file (all content in structured table)
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

The previous week's PPTX must be supplied by Innes (project file or upload) — it cannot be embedded here due to size. Ask for it if not provided.

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
- Use at least 3 different question formats per lesson
- Fluency target (both year groups): **90 wpm** (texts become more challenging; rate stays constant)
- See `references/question-types.md` for all format specifications

### Y5 Progression Table (use TERM to select the right row)

Pupils start Y5 at broadly Y4 standard. Do not jump calibration — step up only at the term boundaries below.

| Term | Extract length (std) | Extract length (sup) | Vocabulary | Question demand |
|------|---------------------|---------------------|------------|-----------------|
| T1 | 200–220 words | 130–145 words | Tier 2, Y4-level; familiar register | Q1–Q5 as Y4; Q6–Q7 begin to ask for a reason or short justification |
| T2 | 210–240 words | 135–150 words | Tier 2, slightly less familiar words | Q6–Q7 require a full sentence with evidence |
| T3 | 230–260 words | 145–160 words | Tier 2; one word per lesson that stretches | Q4–Q7 expect 2 sentences; first inference question about author purpose |
| T4 | 250–270 words | 155–165 words | Tier 2 mix, higher register overall | Q5–Q7 need 2–3 sentences; inference includes effect on reader |
| T5 | 260–280 words | 160–175 words | Tier 2 with occasional Tier 3 for standard | Q6–Q7 require extended response; at least one question weighs two interpretations |
| T6 | 270–300 words | 165–180 words | Tier 2/3 mix for standard | Full Y5 demand — bias, purpose, ambiguity expected at Q5–Q7 |

**How to apply:** at Step 1, collect `TERM` (T1–T6) alongside `YEAR_GROUP`. For Y4, ignore this table.

### We Do Questions (PPTX Practice Q slide)

Two questions per lesson shown with answers on the PPTX Practice Questions slide. These are representative questions (usually conceptually similar to Q1 and Q2) crafted specifically for whole-class modelling, not necessarily identical to the worksheet questions.

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
    "IiIiClQ1VzIgUERGIGJ1aWxkZXIg4oCUIG1hdGNoZXMgVDVXMSBsYXlvdXQgZXhhY3RseS4KUHJvZHVj"
    "ZXMgMTIgaW5kaXZpZHVhbCBQREZzIHRoZW4gbWVyZ2VzIGludG8gMy4KIiIiCmltcG9ydCBzeXMKc3lz"
    "LnBhdGguaW5zZXJ0KDAsICcvaG9tZS9jbGF1ZGUnKQpmcm9tIHQ1dzJfY29udGVudCBpbXBvcnQgKgoK"
    "ZnJvbSByZXBvcnRsYWIubGliLnBhZ2VzaXplcyBpbXBvcnQgQTQKZnJvbSByZXBvcnRsYWIucGRmZ2Vu"
    "IGltcG9ydCBjYW52YXMKZnJvbSByZXBvcnRsYWIubGliLnVuaXRzIGltcG9ydCBtbQpmcm9tIHB5cGRm"
    "IGltcG9ydCBQZGZSZWFkZXIsIFBkZldyaXRlcgppbXBvcnQgb3MKClcsIEggPSBBNApNQVJHSU4gPSA4"
    "ICogbW0KQ1cgPSBXIC0gMiAqIE1BUkdJTiAgIyBjb250ZW50IHdpZHRoCgojIENvbG91cnMgbWF0Y2hp"
    "bmcgVDVXMQpCT1hfQk9SREVSID0gKDAuMTczLCAwLjE3MywgMC40MjQpICAgIyAjMmMyYzZjCkJPWF9C"
    "RyAgICAgPSAoMC45NDEsIDAuOTQxLCAwLjk3MykgICAjICNmMGYwZjgKR1JFRU4gICAgICA9ICgwLjEw"
    "MiwgMC40NzgsIDAuMTAyKSAgICMgIzFhN2ExYQpEQVJLICAgICAgID0gKDAuMTMzLCAwLjEzMywgMC4x"
    "MzMpCkdSRVlfTElORSAgPSAoMC42LCAwLjYsIDAuNikKCklDT05fUEFUSCA9ICIvaG9tZS9jbGF1ZGUv"
    "cmVhZGVyX2ljb25fc2F2ZWQucG5nIgpPVVRfRElSICAgPSAiL2hvbWUvY2xhdWRlL3BkZnNfaW5kaXZp"
    "ZHVhbCIKb3MubWFrZWRpcnMoT1VUX0RJUiwgZXhpc3Rfb2s9VHJ1ZSkKCgpkZWYgZHJhd19oZWFkZXIo"
    "YywgbGVzc29uX3R5cGUsIGRhdGVfc3RyLCBrZXlfcSwgbGYsIGljYW4xLCBpY2FuMik6CiAgICAiIiJE"
    "cmF3IHRoZSBsZWFybmluZyBsYWJlbCBoZWFkZXIuIFJldHVybnMgeSBhZnRlciBoZWFkZXIuIiIiCiAg"
    "ICB5ID0gSCAtIE1BUkdJTgoKICAgICMgUm93IDE6ICJLZXkgUXVlc3Rpb24iIFtpY29uXSBkYXRlIOKA"
    "lCBhbGwgb24gb25lIGxpbmUgbGVmdC10by1yaWdodAogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9s"
    "ZCIsIDgpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4s"
    "IHkgLSA1Km1tLCAiS2V5IFF1ZXN0aW9uIikKICAgIGljb25feCA9IE1BUkdJTiArIDI2Km1tCiAgICB0"
    "cnk6CiAgICAgICAgYy5kcmF3SW1hZ2UoSUNPTl9QQVRILCBpY29uX3gsIHkgLSA3Km1tLCB3aWR0aD03"
    "Km1tLCBoZWlnaHQ9NyptbSwKICAgICAgICAgICAgICAgICAgICBtYXNrPSdhdXRvJywgcHJlc2VydmVB"
    "c3BlY3RSYXRpbz1UcnVlKQogICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICBwYXNzCiAgICAjIERh"
    "dGUgaW1tZWRpYXRlbHkgYWZ0ZXIgaWNvbgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA4KQogICAg"
    "ZGF5LCBkYXRlID0gZGF0ZV9zdHIKICAgIGMuZHJhd1N0cmluZyhpY29uX3ggKyA4Km1tLCB5IC0gNSpt"
    "bSwgZiJ7ZGF5fSB7ZGF0ZX0iKQogICAgeSAtPSA3Km1tCgogICAgIyBEaXZpZGVyCiAgICBjLnNldFN0"
    "cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnNldExpbmVXaWR0aCgwLjMpCiAgICBjLmxpbmUo"
    "TUFSR0lOLCB5LCBNQVJHSU4gKyBDVywgeSkKICAgIHkgLT0gMSptbQoKICAgICMgS2V5IHF1ZXN0aW9u"
    "IOKAlCB1bmRlcmxpbmVkLCBib2xkLCBkYXJrIGJsdWUKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJv"
    "bGQiLCAxMCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKDAuMTczLCAwLjE3MywgMC40MjQpCiAgICBjLmRy"
    "YXdTdHJpbmcoTUFSR0lOLCB5IC0gNCptbSwga2V5X3EpCiAgICBrcV93ID0gYy5zdHJpbmdXaWR0aChr"
    "ZXlfcSwgIkhlbHZldGljYS1Cb2xkIiwgMTApCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLnNl"
    "dFN0cm9rZUNvbG9yUkdCKDAuMTczLCAwLjE3MywgMC40MjQpCiAgICBjLmxpbmUoTUFSR0lOLCB5IC0g"
    "NSptbSwgTUFSR0lOICsga3FfdywgeSAtIDUqbW0pCiAgICB5IC09IDYqbW0KCiAgICAjIExGIGxpbmUK"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQog"
    "ICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwgeSAtIDMuNSptbSwgbGYpCiAgICB5IC09IDQuNSptbQoKICAg"
    "ICMgSSBjYW4gbGluZXMKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHkgLSAzLjUqbW0sIGljYW4xKQog"
    "ICAgeSAtPSA0Km1tCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gMy41Km1tLCBpY2FuMikKICAg"
    "IHkgLT0gNC41Km1tCgogICAgIyBEaXZpZGVyCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJ"
    "TkUpCiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLmxpbmUoTUFSR0lOLCB5LCBNQVJHSU4gKyBD"
    "VywgeSkKICAgIHkgLT0gMiptbQoKICAgIHJldHVybiB5CgoKZGVmIHdyYXBfdGV4dChjLCB0ZXh0LCBm"
    "b250LCBzaXplLCBtYXhfdyk6CiAgICAiIiJXcmFwIHRleHQgdG8gbGluZXMgZml0dGluZyBtYXhfdy4g"
    "UmV0dXJucyBsaXN0IG9mIGxpbmVzLiIiIgogICAgd29yZHMgPSB0ZXh0LnNwbGl0KCkKICAgIGxpbmVz"
    "LCBsaW5lID0gW10sICcnCiAgICBmb3IgdyBpbiB3b3JkczoKICAgICAgICB0ZXN0ID0gKGxpbmUgKyAn"
    "ICcgKyB3KS5zdHJpcCgpCiAgICAgICAgaWYgYy5zdHJpbmdXaWR0aCh0ZXN0LCBmb250LCBzaXplKSA8"
    "PSBtYXhfdzoKICAgICAgICAgICAgbGluZSA9IHRlc3QKICAgICAgICBlbHNlOgogICAgICAgICAgICBp"
    "ZiBsaW5lOgogICAgICAgICAgICAgICAgbGluZXMuYXBwZW5kKGxpbmUpCiAgICAgICAgICAgIGxpbmUg"
    "PSB3CiAgICBpZiBsaW5lOgogICAgICAgIGxpbmVzLmFwcGVuZChsaW5lKQogICAgcmV0dXJuIGxpbmVz"
    "IG9yIFsnJ10KCgpkZWYgZHJhd190ZXh0X2JveChjLCB0ZXh0LCB5X3RvcCwgZm9udF9zaXplPTEwLjUp"
    "OgogICAgIiIiRHJhdyB0aGUgcmVhZGluZyB0ZXh0IGJveC4gUmV0dXJucyB5IGFmdGVyIGJveC4iIiIK"
    "ICAgIGxpbmVzID0gd3JhcF90ZXh0KGMsIHRleHQsICJIZWx2ZXRpY2EiLCBmb250X3NpemUsIENXIC0g"
    "NiptbSkKICAgIGxpbmVfaCA9IGZvbnRfc2l6ZSAqIDEuNAogICAgYm94X2ggPSBsZW4obGluZXMpICog"
    "bGluZV9oICsgNSptbQoKICAgICMgQm94CiAgICBjLnNldEZpbGxDb2xvclJHQigqQk9YX0JHKQogICAg"
    "Yy5zZXRTdHJva2VDb2xvclJHQigqQk9YX0JPUkRFUikKICAgIGMuc2V0TGluZVdpZHRoKDAuOCkKICAg"
    "IGMucm91bmRSZWN0KE1BUkdJTiwgeV90b3AgLSBib3hfaCwgQ1csIGJveF9oLCAyKm1tLCBmaWxsPTEs"
    "IHN0cm9rZT0xKQoKICAgICMgVGV4dAogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLnNl"
    "dEZvbnQoIkhlbHZldGljYSIsIGZvbnRfc2l6ZSkKICAgIHR5ID0geV90b3AgLSAzKm1tIC0gZm9udF9z"
    "aXplICogMC43MgogICAgZm9yIGxpbmUgaW4gbGluZXM6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJ"
    "TiArIDMqbW0sIHR5LCBsaW5lKQogICAgICAgIHR5IC09IGxpbmVfaAoKICAgIHJldHVybiB5X3RvcCAt"
    "IGJveF9oIC0gMyptbQoKCmRlZiBhbnN3ZXJfbGluZXMoYywgeSwgbiwgZ2FwPTYuNSptbSk6CiAgICAi"
    "IiJEcmF3IG4gc29saWQgYW5zd2VyIGxpbmVzLiBSZXR1cm5zIHkgYWZ0ZXIgbGluZXMuIiIiCiAgICBj"
    "LnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICBm"
    "b3IgaSBpbiByYW5nZShuKToKICAgICAgICBseSA9IHkgLSAoaSArIDEpICogZ2FwCiAgICAgICAgYy5s"
    "aW5lKE1BUkdJTiwgbHksIE1BUkdJTiArIENXLCBseSkKICAgIHJldHVybiB5IC0gbiAqIGdhcCAtIDIq"
    "bW0KCgpkZWYgcV9sYWJlbChjLCBxbnVtLCB0ZXh0LCB5LCBpc19hbnN3ZXI9RmFsc2UsIGFuc19jb2xv"
    "dXI9RmFsc2UpOgogICAgIiIiRHJhdyBxdWVzdGlvbiBsYWJlbC4gUmV0dXJucyB5IGFmdGVyIHRleHQu"
    "IiIiCiAgICBjb2xvdXIgPSBHUkVFTiBpZiBhbnNfY29sb3VyIGVsc2UgREFSSwogICAgYy5zZXRGaWxs"
    "Q29sb3JSR0IoKmNvbG91cikKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgbGFi"
    "ZWwgPSBmIntxbnVtWzE6XX0uICIKICAgIGx3ID0gYy5zdHJpbmdXaWR0aChsYWJlbCwgIkhlbHZldGlj"
    "YS1Cb2xkIiwgOSkKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHksIGxhYmVsKQogICAgbGluZXMgPSB3"
    "cmFwX3RleHQoYywgdGV4dCwgIkhlbHZldGljYS1Cb2xkIiwgOSwgQ1cgLSBsdykKICAgIGZvciBpLCBs"
    "aW5lIGluIGVudW1lcmF0ZShsaW5lcyk6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIGx3LCB5"
    "IC0gaSAqICg5ICogMS4zNSksIGxpbmUpCiAgICByZXR1cm4geSAtIGxlbihsaW5lcykgKiAoOSAqIDEu"
    "MzUpIC0gMSptbQoKCmRlZiBkcmF3X21jX3B1cGlsKGMsIG9wdGlvbnMsIHkpOgogICAgIiIiNC1jZWxs"
    "IE1DIHRhYmxlLCBubyBoaWdobGlnaHQuIiIiCiAgICBjb2xfdyA9IENXIC8gMgogICAgcm93X2ggPSA2"
    "Km1tCiAgICAjIFR3byByb3dzIG9mIDIKICAgIGZvciByb3cgaW4gcmFuZ2UoMik6CiAgICAgICAgZm9y"
    "IGNvbCBpbiByYW5nZSgyKToKICAgICAgICAgICAgaWR4ID0gcm93ICogMiArIGNvbAogICAgICAgICAg"
    "ICBpZiBpZHggPj0gbGVuKG9wdGlvbnMpOgogICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAg"
    "eCA9IE1BUkdJTiArIGNvbCAqIGNvbF93CiAgICAgICAgICAgIHJ5ID0geSAtIHJvdyAqIHJvd19oCiAg"
    "ICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEsIDEpCiAgICAgICAgICAgIGMuc2V0U3Ryb2tl"
    "Q29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgICAgICAgICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAg"
    "ICAgICAgICBjLnJlY3QoeCwgcnkgLSByb3dfaCwgY29sX3csIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0x"
    "KQogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAgICAgYy5zZXRGb250"
    "KCJIZWx2ZXRpY2EiLCA4LjUpCiAgICAgICAgICAgIGMuZHJhd1N0cmluZyh4ICsgMiptbSwgcnkgLSBy"
    "b3dfaCArIDIqbW0sIG9wdGlvbnNbaWR4XSkKICAgIHJldHVybiB5IC0gMiAqIHJvd19oIC0gMS41Km1t"
    "CgoKZGVmIGRyYXdfbWNfYW5zd2VyKGMsIG9wdGlvbnMsIGNvcnJlY3QsIHkpOgogICAgIiIiNC1jZWxs"
    "IE1DIHRhYmxlLCBjb3JyZWN0IGNlbGwgaGlnaGxpZ2h0ZWQgZ3JlZW4uIiIiCiAgICBjb2xfdyA9IENX"
    "IC8gMgogICAgcm93X2ggPSA2Km1tCiAgICBmb3Igcm93IGluIHJhbmdlKDIpOgogICAgICAgIGZvciBj"
    "b2wgaW4gcmFuZ2UoMik6CiAgICAgICAgICAgIGlkeCA9IHJvdyAqIDIgKyBjb2wKICAgICAgICAgICAg"
    "aWYgaWR4ID49IGxlbihvcHRpb25zKToKICAgICAgICAgICAgICAgIGJyZWFrCiAgICAgICAgICAgIHgg"
    "PSBNQVJHSU4gKyBjb2wgKiBjb2xfdwogICAgICAgICAgICByeSA9IHkgLSByb3cgKiByb3dfaAogICAg"
    "ICAgICAgICBpc19jb3JyZWN0ID0gb3B0aW9uc1tpZHhdID09IGNvcnJlY3QKICAgICAgICAgICAgaWYg"
    "aXNfY29ycmVjdDoKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDAuODUsIDAuOTUsIDAu"
    "ODUpCiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigxLCAx"
    "LCAxKQogICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNywgMC43LCAwLjcpCiAgICAgICAg"
    "ICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICAgICAgICAgYy5yZWN0KHgsIHJ5IC0gcm93X2gsIGNv"
    "bF93LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICAgICAgaWYgaXNfY29ycmVjdDoKICAg"
    "ICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICAgICAgICAgIGMuc2V0"
    "Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4LjUpCiAgICAgICAgICAgICAgICBjLmRyYXdTdHJpbmcoeCAr"
    "IDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBvcHRpb25zW2lkeF0gKyAiIFx1MjcxMyIpCiAgICAgICAg"
    "ICAgIGVsc2U6CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAg"
    "ICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOC41KQogICAgICAgICAgICAgICAgYy5kcmF3U3Ry"
    "aW5nKHggKyAyKm1tLCByeSAtIHJvd19oICsgMiptbSwgb3B0aW9uc1tpZHhdKQogICAgcmV0dXJuIHkg"
    "LSAyICogcm93X2ggLSAxLjUqbW0KCgpkZWYgZHJhd19tYXRjaF9wdXBpbChjLCBwYWlycywgeSk6CiAg"
    "ICAiIiJNYXRjaCB0YWJsZSDigJQgbGVmdCB3b3JkcywgZ2FwLCByaWdodCBkZWZpbml0aW9ucyAoc2Ny"
    "YW1ibGVkKS4iIiIKICAgIGx3ID0gQ1cgKiAwLjI4CiAgICBydyA9IENXICogMC40OAogICAgZ2FwID0g"
    "Q1cgLSBsdyAtIHJ3ICAjIDI0JSBnYXAgaW4gbWlkZGxlCiAgICByb3dfaCA9IDcqbW0KICAgIGMuc2V0"
    "U3Ryb2tlQ29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICMg"
    "U2NyYW1ibGUgcmlnaHQgY29sdW1uCiAgICByaWdodHMgPSBbciBmb3IgXywgciBpbiBwYWlyc10KICAg"
    "IHNjcmFtYmxlZCA9IHJpZ2h0c1sxOl0gKyByaWdodHNbOjFdCiAgICBmb3IgaSwgKGxlZnQsIF8pIGlu"
    "IGVudW1lcmF0ZShwYWlycyk6CiAgICAgICAgcnkgPSB5IC0gaSAqIHJvd19oCiAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoMC45NiwgMC45NiwgMC45NikKICAgICAgICBjLnJlY3QoTUFSR0lOLCByeSAtIHJv"
    "d19oLCBsdywgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0Io"
    "KkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDguNSkKICAgICAgICBjLmRy"
    "YXdTdHJpbmcoTUFSR0lOICsgMiptbSwgcnkgLSByb3dfaCArIDIqbW0sIGxlZnQpCiAgICAgICAgcngg"
    "PSBNQVJHSU4gKyBsdyArIGdhcAogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDAuOTYsIDAuOTYsIDAu"
    "OTYpCiAgICAgICAgYy5yZWN0KHJ4LCByeSAtIHJvd19oLCBydywgcm93X2gsIGZpbGw9MSwgc3Ryb2tl"
    "PTEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2"
    "ZXRpY2EiLCA4LjUpCiAgICAgICAgYy5kcmF3U3RyaW5nKHJ4ICsgMiptbSwgcnkgLSByb3dfaCArIDIq"
    "bW0sIHNjcmFtYmxlZFtpXSkKICAgIHJldHVybiB5IC0gbGVuKHBhaXJzKSAqIHJvd19oIC0gMS41Km1t"
    "CgoKZGVmIGRyYXdfbWF0Y2hfYW5zd2VyKGMsIHBhaXJzLCB5KToKICAgICIiIk1hdGNoIHRhYmxlIHdp"
    "dGggZ3JlZW4gY29ubmVjdG9ycy4iIiIKICAgIGx3ID0gQ1cgKiAwLjI4CiAgICBydyA9IENXICogMC40"
    "OAogICAgZ2FwID0gQ1cgLSBsdyAtIHJ3CiAgICByb3dfaCA9IDcqbW0KICAgIGMuc2V0U3Ryb2tlQ29s"
    "b3JSR0IoMC43LCAwLjcsIDAuNykKICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgIGZvciBpLCAobGVm"
    "dCwgcmlnaHQpIGluIGVudW1lcmF0ZShwYWlycyk6CiAgICAgICAgcnkgPSB5IC0gaSAqIHJvd19oCiAg"
    "ICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC45NiwgMC45NiwgMC45NikKICAgICAgICBjLnJlY3QoTUFS"
    "R0lOLCByeSAtIHJvd19oLCBsdywgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4LjUp"
    "CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBsZWZ0"
    "KQogICAgICAgIHJ4ID0gTUFSR0lOICsgbHcgKyBnYXAKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigw"
    "Ljg1LCAwLjk1LCAwLjg1KQogICAgICAgIGMucmVjdChyeCwgcnkgLSByb3dfaCwgcncsIHJvd19oLCBm"
    "aWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICBj"
    "LnNldEZvbnQoIkhlbHZldGljYS1Cb2xkT2JsaXF1ZSIsIDguNSkKICAgICAgICBjLmRyYXdTdHJpbmco"
    "cnggKyAyKm1tLCByeSAtIHJvd19oICsgMiptbSwgIlx1MjAxNFx1MjVhMCAgIiArIHJpZ2h0KQogICAg"
    "cmV0dXJuIHkgLSBsZW4ocGFpcnMpICogcm93X2ggLSAxLjUqbW0KCgpkZWYgZHJhd19maWxsKGMsIHNl"
    "bnRlbmNlLCB5LCBpc19hbnN3ZXI9RmFsc2UsIGFuc3dlcj0iIik6CiAgICAiIiJEcmF3IGZpbGwtaW4t"
    "Ymxhbmsgc2VudGVuY2Ugd2l0aCB1bmRlcmxpbmUgYmxhbmtzIG9yIGdyZWVuIGFuc3dlcnMuIiIiCiAg"
    "ICBwYXJ0cyA9IHNlbnRlbmNlLnNwbGl0KCJfX19fX19fX19fX19fXyIpCiAgICBibGFua3NfbmVlZGVk"
    "ID0gbGVuKHBhcnRzKSAtIDEKICAgIGFuc3dlcnMgPSBbYS5zdHJpcCgpIGZvciBhIGluIGFuc3dlci5z"
    "cGxpdCgiLyIpXSBpZiBhbnN3ZXIgZWxzZSBbXQogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQog"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICB4ID0gTUFSR0lOCiAgICBibGFua193ID0gMjgq"
    "bW0KICAgIGZvciBwaSwgcGFydCBpbiBlbnVtZXJhdGUocGFydHMpOgogICAgICAgICMgTWVhc3VyZSBh"
    "bmQgZHJhdyB0aGUgdGV4dCBwYXJ0CiAgICAgICAgcHcgPSBjLnN0cmluZ1dpZHRoKHBhcnQsICJIZWx2"
    "ZXRpY2EiLCA5KQogICAgICAgIGMuZHJhd1N0cmluZyh4LCB5LCBwYXJ0KQogICAgICAgIHggKz0gcHcK"
    "ICAgICAgICBpZiBwaSA8IGJsYW5rc19uZWVkZWQ6CiAgICAgICAgICAgIGlmIGlzX2Fuc3dlciBhbmQg"
    "cGkgPCBsZW4oYW5zd2Vycyk6CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqR1JFRU4p"
    "CiAgICAgICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgICAgICAgICAg"
    "ICAgIGMuZHJhd1N0cmluZyh4ICsgMSptbSwgeSwgYW5zd2Vyc1twaV0pCiAgICAgICAgICAgICAgICB4"
    "ICs9IGJsYW5rX3cKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAg"
    "ICAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgICAgICAgICBlbHNlOgogICAgICAg"
    "ICAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigqR1JFWV9MSU5FKQogICAgICAgICAgICAgICAgYy5z"
    "ZXRMaW5lV2lkdGgoMC41KQogICAgICAgICAgICAgICAgYy5saW5lKHgsIHkgLSAxKm1tLCB4ICsgYmxh"
    "bmtfdywgeSAtIDEqbW0pCiAgICAgICAgICAgICAgICB4ICs9IGJsYW5rX3cKICAgIHJldHVybiB5IC0g"
    "NS41Km1tCgoKZGVmIGRyYXdfdGlja19wdXBpbChjLCBvcHRpb25zLCB5KToKICAgICIiIlRpY2sgb3B0"
    "aW9ucyB3aXRoIHNxdWFyZSBidWxsZXRzLiIiIgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQog"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAjIDIgb3IgMyBwZXIgcm93IGRlcGVuZGluZyBv"
    "biBjb3VudAogICAgIyBDaG9vc2UgY29sdW1ucyBiYXNlZCBvbiBvcHRpb24gbGVuZ3RoCiAgICBtYXhf"
    "bGVuID0gbWF4KGxlbihvKSBmb3IgbyBpbiBvcHRpb25zKQogICAgaWYgbWF4X2xlbiA+IDI1OgogICAg"
    "ICAgIHBlcl9yb3cgPSAyICAjIGxvbmcgb3B0aW9uczogMiBwZXIgcm93CiAgICBlbGlmIGxlbihvcHRp"
    "b25zKSA9PSA1OgogICAgICAgIHBlcl9yb3cgPSA1ICAjIDUgc2hvcnQgb3B0aW9uczogYWxsIG9uIG9u"
    "ZSByb3cKICAgIGVsc2U6CiAgICAgICAgcGVyX3JvdyA9IDQKICAgIGNvbF93ID0gQ1cgLyBwZXJfcm93"
    "CiAgICByb3dzID0gKGxlbihvcHRpb25zKSArIHBlcl9yb3cgLSAxKSAvLyBwZXJfcm93CiAgICByb3df"
    "aCA9IDUuNSptbQogICAgZm9yIGksIG9wdCBpbiBlbnVtZXJhdGUob3B0aW9ucyk6CiAgICAgICAgcm93"
    "ID0gaSAvLyBwZXJfcm93CiAgICAgICAgY29sID0gaSAlIHBlcl9yb3cKICAgICAgICBjLmRyYXdTdHJp"
    "bmcoTUFSR0lOICsgY29sICogY29sX3csIHkgLSByb3cgKiByb3dfaCwgb3B0KQogICAgcmV0dXJuIHkg"
    "LSByb3dzICogcm93X2ggLSAzKm1tCgoKZGVmIGRyYXdfdGlja19hbnN3ZXIoYywgb3B0aW9ucywgY29y"
    "cmVjdCwgeSk6CiAgICAiIiJUaWNrIG9wdGlvbnMgd2l0aCBjb3JyZWN0IG9uZXMgaW4gYm9sZCBncmVl"
    "bi4iIiIKICAgIG1heF9sZW4gPSBtYXgobGVuKG8pIGZvciBvIGluIG9wdGlvbnMpCiAgICBpZiBtYXhf"
    "bGVuID4gMjU6CiAgICAgICAgcGVyX3JvdyA9IDIKICAgIGVsaWYgbGVuKG9wdGlvbnMpID09IDU6CiAg"
    "ICAgICAgcGVyX3JvdyA9IDUKICAgIGVsc2U6CiAgICAgICAgcGVyX3JvdyA9IDQKICAgIGNvbF93ID0g"
    "Q1cgLyBwZXJfcm93CiAgICByb3dzID0gKGxlbihvcHRpb25zKSArIHBlcl9yb3cgLSAxKSAvLyBwZXJf"
    "cm93CiAgICByb3dfaCA9IDUuNSptbQogICAgZm9yIGksIG9wdCBpbiBlbnVtZXJhdGUob3B0aW9ucyk6"
    "CiAgICAgICAgcm93ID0gaSAvLyBwZXJfcm93CiAgICAgICAgY29sID0gaSAlIHBlcl9yb3cKICAgICAg"
    "ICBpZiBvcHQgaW4gY29ycmVjdDoKICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQog"
    "ICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgICAgICBlbHNlOgogICAg"
    "ICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAgICAgYy5zZXRGb250KCJIZWx2"
    "ZXRpY2EiLCA5KQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBjb2wgKiBjb2xfdywgeSAtIHJv"
    "dyAqIHJvd19oLCBvcHQpCiAgICByZXR1cm4geSAtIHJvd3MgKiByb3dfaCAtIDMqbW0KCgpkZWYgZHJh"
    "d19vcmRlcl9wdXBpbChjLCBldmVudHMsIHkpOgogICAgIiIiTnVtYmVyZWQgb3JkZXJpbmcgcXVlc3Rp"
    "b24uIiIiCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICBjLnNldEZpbGxDb2xvclJHQigq"
    "REFSSykKICAgIHJvd19oID0gNS41Km1tCiAgICBmb3IgaSwgZXYgaW4gZW51bWVyYXRlKGV2ZW50cyk6"
    "CiAgICAgICAgcnkgPSB5IC0gaSAqIHJvd19oCiAgICAgICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAg"
    "ICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgICAgICBjLnJlY3QoTUFSR0lO"
    "LCByeSAtIHJvd19oICsgMSptbSwgOCptbSwgNCptbSwgZmlsbD0wLCBzdHJva2U9MSkKICAgICAgICBj"
    "LmRyYXdTdHJpbmcoTUFSR0lOICsgMTAqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBldikKICAgIHJldHVy"
    "biB5IC0gbGVuKGV2ZW50cykgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBkcmF3X29yZGVyX2Fuc3dlcihj"
    "LCBldmVudHMsIGNvcnJlY3Rfb3JkZXIsIHkpOgogICAgIiIiTnVtYmVyZWQgb3JkZXJpbmcgcXVlc3Rp"
    "b24gd2l0aCBhbnN3ZXJzLiIiIgogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgcm93X2gg"
    "PSA1LjUqbW0KICAgIGZvciBpLCAoZXYsIG51bSkgaW4gZW51bWVyYXRlKHppcChldmVudHMsIGNvcnJl"
    "Y3Rfb3JkZXIpKToKICAgICAgICByeSA9IHkgLSBpICogcm93X2gKICAgICAgICBjLnNldEZpbGxDb2xv"
    "clJHQigwLjg1LCAwLjk1LCAwLjg1KQogICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC43LCAwLjcs"
    "IDAuNykKICAgICAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgcnkg"
    "LSByb3dfaCArIDEqbW0sIDgqbW0sIDQqbW0sIGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQog"
    "ICAgICAgIGMuZHJhd0NlbnRyZWRTdHJpbmcoTUFSR0lOICsgNCptbSwgcnkgLSByb3dfaCArIDIqbW0s"
    "IG51bSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICBjLnNldEZvbnQoIkhl"
    "bHZldGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIDEwKm1tLCByeSAtIHJvd19o"
    "ICsgMiptbSwgZXYpCiAgICByZXR1cm4geSAtIGxlbihldmVudHMpICogcm93X2ggLSAxLjUqbW0KCgpk"
    "ZWYgZHJhd193cml0dGVuX2Fuc3dlcihjLCBhbnN3ZXIsIHksIG5fbGluZXM9Myk6CiAgICAiIiJXcml0"
    "dGVuIGFuc3dlcjogYW5zd2VyIGxpbmVzIChwdXBpbCkgb3IgZ3JlZW4gaXRhbGljIHRleHQgKGFuc3dl"
    "cnMpLiIiIgogICAgaWYgYW5zd2VyOgogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAg"
    "ICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1PYmxpcXVlIiwgOC41KQogICAgICAgIGxpbmVzID0gd3Jh"
    "cF90ZXh0KGMsIGFuc3dlciwgIkhlbHZldGljYS1PYmxpcXVlIiwgOC41LCBDVykKICAgICAgICBmb3Ig"
    "aSwgbGluZSBpbiBlbnVtZXJhdGUobGluZXMpOgogICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lO"
    "LCB5IC0gKGkgKyAxKSAqIDUqbW0sIGxpbmUpCiAgICAgICAgcmV0dXJuIHkgLSBsZW4obGluZXMpICog"
    "NSptbSAtIDQqbW0KICAgIGVsc2U6CiAgICAgICAgcmV0dXJuIGFuc3dlcl9saW5lcyhjLCB5LCBuX2xp"
    "bmVzKQoKCmRlZiByZW5kZXJfcXVlc3Rpb24oYywgcSwgeSwgaXNfYW5zd2VyPUZhbHNlLCBuX2xpbmVz"
    "PTMsIG1pbl95PTIwKm1tKToKICAgICIiIlJlbmRlciBhIHNpbmdsZSBxdWVzdGlvbi4gUmV0dXJucyBu"
    "ZXcgeSwgb3IgTm9uZSBpZiBubyByb29tLiIiIgogICAgcW51bSwgcXR5cGUsIHF0ZXh0LCBvcHRpb25z"
    "LCBjb3JyZWN0ID0gcQoKICAgICMgRXN0aW1hdGUgaGVpZ2h0CiAgICBsYWJlbF9oID0gbGVuKHdyYXBf"
    "dGV4dChjLCBxdGV4dC5zcGxpdCgnXG4nKVswXSwgIkhlbHZldGljYS1Cb2xkIiwgOSwgQ1cgLSA4Km1t"
    "KSkgKiAxMiArIDQKICAgIGV4dHJhID0gMAogICAgaWYgcXR5cGUgPT0gIm1jIjogICAgICAgICAgICAg"
    "ZXh0cmEgPSAxNCptbQogICAgZWxpZiBxdHlwZSA9PSAibWF0Y2giOiAgICAgICAgZXh0cmEgPSBsZW4o"
    "b3B0aW9ucykgKiA3Km1tCiAgICBlbGlmIHF0eXBlIGluICgidGljazIiLCJ0aWNrMyIpOiBleHRyYSA9"
    "IChsZW4ob3B0aW9ucykgLy8gMyArIDEpICogNiptbQogICAgZWxpZiBxdHlwZSA9PSAiZmlsbCI6ICAg"
    "ICAgICAgZXh0cmEgPSA2Km1tCiAgICBlbGlmIHF0eXBlID09ICJvcmRlciI6ICAgICAgICBleHRyYSA9"
    "IGxlbihvcHRpb25zKSAqIDYqbW0KICAgIGVsaWYgcXR5cGUgPT0gIndyaXR0ZW4iOiAgICAgIGV4dHJh"
    "ID0gbl9saW5lcyAqIDUuNSptbQogICAgdG90YWxfZXN0ID0gbGFiZWxfaCArIGV4dHJhICsgMyptbQoK"
    "ICAgIGlmIHkgLSB0b3RhbF9lc3QgPCBtaW5feToKICAgICAgICByZXR1cm4gTm9uZSAgIyBubyByb29t"
    "CgogICAgIyBEcmF3IHF1ZXN0aW9uIHRleHQKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAg"
    "Yy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICBsYWJlbCA9IGYie3FudW1bMTpdfS4gIgog"
    "ICAgbHcgPSBjLnN0cmluZ1dpZHRoKGxhYmVsLCAiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgYy5kcmF3"
    "U3RyaW5nKE1BUkdJTiwgeSwgbGFiZWwpCiAgICBxX2xpbmVzX2FsbCA9IHF0ZXh0LnNwbGl0KCdcbicp"
    "CiAgICAjIEZvciBmaWxsLWluLWJsYW5rIHdpdGggYSBzZXBhcmF0ZSBzZW50ZW5jZSBsaW5lLCBvbmx5"
    "IHNob3cgdGhlIHByb21wdCBhcyB0aGUgbGFiZWwKICAgIGxhYmVsX2xpbmVzX3RleHQgPSBxX2xpbmVz"
    "X2FsbFswXQogICAgZmlyc3RfbGluZXMgPSB3cmFwX3RleHQoYywgbGFiZWxfbGluZXNfdGV4dCwgIkhl"
    "bHZldGljYS1Cb2xkIiwgOSwgQ1cgLSBsdykKICAgIGZvciBpLCBsaW5lIGluIGVudW1lcmF0ZShmaXJz"
    "dF9saW5lcyk6CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIGx3LCB5IC0gaSAqICg5ICogMS4z"
    "NSksIGxpbmUpCiAgICB5IC09IGxlbihmaXJzdF9saW5lcykgKiAoOSAqIDEuMzUpCiAgICAjIEZvciBu"
    "b24tZmlsbCB0eXBlcyB3aXRoIGFkZGl0aW9uYWwgbGluZXMgKG5vdCB1c2VkIGN1cnJlbnRseSksIGRy"
    "YXcgdGhlbQogICAgaWYgcXR5cGUgIT0gImZpbGwiOgogICAgICAgIGZvciBleHRyYV9saW5lIGluIHFf"
    "bGluZXNfYWxsWzE6XToKICAgICAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgICAg"
    "ICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJ"
    "TiwgeSwgZXh0cmFfbGluZSkKICAgICAgICAgICAgeSAtPSA5ICogMS4zNQogICAgeSAtPSAxKm1tCgog"
    "ICAgaWYgcXR5cGUgPT0gIm1jIjoKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBk"
    "cmF3X21jX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KQogICAgICAgIGVsc2U6CiAgICAgICAg"
    "ICAgIHkgPSBkcmF3X21jX3B1cGlsKGMsIG9wdGlvbnMsIHkpCiAgICAgICAgeSAtPSAxKm1tICAjIGV4"
    "dHJhIGdhcCBhZnRlciBNQyB0YWJsZQoKICAgIGVsaWYgcXR5cGUgPT0gIm1hdGNoIjoKICAgICAgICBp"
    "ZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBkcmF3X21hdGNoX2Fuc3dlcihjLCBvcHRpb25zLCB5"
    "KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3X21hdGNoX3B1cGlsKGMsIG9wdGlvbnMs"
    "IHkpCiAgICAgICAgeSAtPSAxKm1tICAjIGV4dHJhIGdhcCBhZnRlciBtYXRjaCB0YWJsZQoKICAgIGVs"
    "aWYgcXR5cGUgaW4gKCJ0aWNrMiIsICJ0aWNrMyIpOgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAg"
    "ICAgICAgeSA9IGRyYXdfdGlja19hbnN3ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSkKICAgICAgICBl"
    "bHNlOgogICAgICAgICAgICB5ID0gZHJhd190aWNrX3B1cGlsKGMsIG9wdGlvbnMsIHkpCgogICAgZWxp"
    "ZiBxdHlwZSA9PSAiZmlsbCI6CiAgICAgICAgIyBUaGUgZmlsbCBzZW50ZW5jZSBpcyB0aGUgbGFzdCBl"
    "bGVtZW50IG9mIHFfbGluZXNfYWxsIChvciBxdGV4dCBpZiBubyBcbikKICAgICAgICBmaWxsX3NlbnRl"
    "bmNlID0gcV9saW5lc19hbGxbLTFdIGlmIGxlbihxX2xpbmVzX2FsbCkgPiAxIGVsc2UgcXRleHQKICAg"
    "ICAgICB5ID0gZHJhd19maWxsKGMsIGZpbGxfc2VudGVuY2UsIHksIGlzX2Fuc3dlcj1pc19hbnN3ZXIs"
    "IGFuc3dlcj1jb3JyZWN0IG9yICIiKQoKICAgIGVsaWYgcXR5cGUgPT0gIm9yZGVyIjoKICAgICAgICBp"
    "ZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBkcmF3X29yZGVyX2Fuc3dlcihjLCBvcHRpb25zLCBj"
    "b3JyZWN0LCB5KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHkgPSBkcmF3X29yZGVyX3B1cGlsKGMs"
    "IG9wdGlvbnMsIHkpCgogICAgZWxpZiBxdHlwZSA9PSAid3JpdHRlbiI6CiAgICAgICAgeSA9IGRyYXdf"
    "d3JpdHRlbl9hbnN3ZXIoYywgY29ycmVjdCBpZiBpc19hbnN3ZXIgZWxzZSBOb25lLCB5LCBuX2xpbmVz"
    "PW5fbGluZXMpCgogICAgcmV0dXJuIHkgLSAzKm1tCgoKZGVmIGJ1aWxkX3BhZ2UocGF0aCwgbGVzc29u"
    "X3R5cGUsIHRleHQsIHF1ZXN0aW9ucywgZGF0ZV9zdHIsIGlzX2Fuc3dlciwgbl9saW5lcyk6CiAgICAi"
    "IiJCdWlsZCBhIHNpbmdsZS1wYWdlIFBERi4iIiIKICAgIGMgPSBjYW52YXMuQ2FudmFzKHBhdGgsIHBh"
    "Z2VzaXplPUE0KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCgogICAgeSA9IGRyYXdfaGVhZGVy"
    "KGMsIGxlc3Nvbl90eXBlLCBkYXRlX3N0ciwgS0VZX1EsCiAgICAgICAgICAgICAgICAgICAgTEZbbGVz"
    "c29uX3R5cGVdLCBJQ0FOW2xlc3Nvbl90eXBlXVswXSwgSUNBTltsZXNzb25fdHlwZV1bMV0pCgogICAg"
    "eSA9IGRyYXdfdGV4dF9ib3goYywgdGV4dCwgeSkKCiAgICBtaW5feSA9IDEyKm1tCiAgICBmb3IgcSBp"
    "biBxdWVzdGlvbnM6CiAgICAgICAgcmVzdWx0ID0gcmVuZGVyX3F1ZXN0aW9uKGMsIHEsIHksIGlzX2Fu"
    "c3dlcj1pc19hbnN3ZXIsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIG5fbGluZXM9bl9s"
    "aW5lcywgbWluX3k9bWluX3kpCiAgICAgICAgaWYgcmVzdWx0IGlzIE5vbmU6CiAgICAgICAgICAgICMg"
    "RHJvcCBRNyBpZiBubyByb29tIChsYXN0IHF1ZXN0aW9uIGluIGxpc3QpCiAgICAgICAgICAgIGJyZWFr"
    "CiAgICAgICAgeSA9IHJlc3VsdAoKICAgIGMuc2F2ZSgpCiAgICByZXR1cm4gcGF0aAoKCmRlZiBjaGVj"
    "a19wYWdlX2NvdW50KHBhdGgpOgogICAgcmVhZGVyID0gUGRmUmVhZGVyKHBhdGgpCiAgICByZXR1cm4g"
    "bGVuKHJlYWRlci5wYWdlcykKCgpkZWYgbWVyZ2VfcGRmcyhmaWxlX2xpc3QsIG91dHB1dF9wYXRoKToK"
    "ICAgIHdyaXRlciA9IFBkZldyaXRlcigpCiAgICBmb3IgZiBpbiBmaWxlX2xpc3Q6CiAgICAgICAgZm9y"
    "IHBhZ2UgaW4gUGRmUmVhZGVyKGYpLnBhZ2VzOgogICAgICAgICAgICB3cml0ZXIuYWRkX3BhZ2UocGFn"
    "ZSkKICAgIHdpdGggb3BlbihvdXRwdXRfcGF0aCwgIndiIikgYXMgZmg6CiAgICAgICAgd3JpdGVyLndy"
    "aXRlKGZoKQoKCiMg4pSA4pSAIEJ1aWxkIGFsbCAxMiBpbmRpdmlkdWFsIFBERnMg4pSA4pSA4pSA4pSA"
    "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
    "4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA"
    "4pSACgpsZXNzb25zID0gWwogICAgKCJWb2NhYnVsYXJ5IiwgU1REX1ZPQywgU1VQX1ZPQywgU1REX1ZP"
    "Q19RUywgU1VQX1ZPQ19RUywgREFURVNbIlZvY2FidWxhcnkiXSksCiAgICAoIlJldHJpZXZhbCIsICBT"
    "VERfUkVULCBTVVBfUkVULCBTVERfUkVUX1FTLCBTVVBfUkVUX1FTLCBEQVRFU1siUmV0cmlldmFsIl0p"
    "LAogICAgKCJJbmZlcmVuY2UiLCAgU1REX0lORiwgU1VQX0lORiwgU1REX0lORl9RUywgU1VQX0lORl9R"
    "UywgREFURVNbIkluZmVyZW5jZSJdKSwKXQoKYnVpbHQgPSB7CiAgICAic3RkX3B1cGlsIjogW10sICJz"
    "dXBfcHVwaWwiOiBbXSwKICAgICJzdGRfYW5zIjogW10sICJzdXBfYW5zIjogW10sCn0KCmZvciBsZXNz"
    "b25fdHlwZSwgc3RkX3RleHQsIHN1cF90ZXh0LCBzdGRfcXMsIHN1cF9xcywgZGF0ZV9zdHIgaW4gbGVz"
    "c29uczoKICAgIGx0ID0gbGVzc29uX3R5cGUKICAgIHByaW50KGYiQnVpbGRpbmcge2x0fS4uLiIpCgog"
    "ICAgIyBTdGFuZGFyZCBwdXBpbAogICAgcCA9IGYie09VVF9ESVJ9L3tsdH1fU3RhbmRhcmRfUHVwaWwu"
    "cGRmIgogICAgYnVpbGRfcGFnZShwLCBsdCwgc3RkX3RleHQsIHN0ZF9xcywgZGF0ZV9zdHIsIGlzX2Fu"
    "c3dlcj1GYWxzZSwgbl9saW5lcz0zKQogICAgcGFnZXMgPSBjaGVja19wYWdlX2NvdW50KHApCiAgICBp"
    "ZiBwYWdlcyA+IDE6CiAgICAgICAgcHJpbnQoZiIgIFdBUk5JTkc6IHtsdH0gU3RhbmRhcmQgb3ZlcmZs"
    "b3dzICh7cGFnZXN9IHBhZ2VzKSDigJQgZHJvcHBpbmcgUTciKQogICAgICAgIGJ1aWxkX3BhZ2UocCwg"
    "bHQsIHN0ZF90ZXh0LCBzdGRfcXNbOi0xXSwgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5l"
    "cz0zKQogICAgcHJpbnQoZiIgIFN0YW5kYXJkIFB1cGlsOiB7Y2hlY2tfcGFnZV9jb3VudChwKX0gcGFn"
    "ZShzKSIpCiAgICBidWlsdFsic3RkX3B1cGlsIl0uYXBwZW5kKHApCgogICAgIyBTdXBwb3J0ZWQgcHVw"
    "aWwKICAgIHAgPSBmIntPVVRfRElSfS97bHR9X1N1cHBvcnRlZF9QdXBpbC5wZGYiCiAgICBidWlsZF9w"
    "YWdlKHAsIGx0LCBzdXBfdGV4dCwgc3VwX3FzLCBkYXRlX3N0ciwgaXNfYW5zd2VyPUZhbHNlLCBuX2xp"
    "bmVzPTIpCiAgICBwYWdlcyA9IGNoZWNrX3BhZ2VfY291bnQocCkKICAgIGlmIHBhZ2VzID4gMToKICAg"
    "ICAgICBwcmludChmIiAgV0FSTklORzoge2x0fSBTdXBwb3J0ZWQgb3ZlcmZsb3dzICh7cGFnZXN9IHBh"
    "Z2VzKSDigJQgZHJvcHBpbmcgUTUiKQogICAgICAgIGJ1aWxkX3BhZ2UocCwgbHQsIHN1cF90ZXh0LCBz"
    "dXBfcXNbOi0xXSwgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5lcz0yKQogICAgcHJpbnQo"
    "ZiIgIFN1cHBvcnRlZCBQdXBpbDoge2NoZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAgYnVp"
    "bHRbInN1cF9wdXBpbCJdLmFwcGVuZChwKQoKICAgICMgU3RhbmRhcmQgYW5zd2VycwogICAgcCA9IGYi"
    "e09VVF9ESVJ9L3tsdH1fU3RhbmRhcmRfQW5zd2Vycy5wZGYiCiAgICBidWlsZF9wYWdlKHAsIGx0LCBz"
    "dGRfdGV4dCwgc3RkX3FzLCBkYXRlX3N0ciwgaXNfYW5zd2VyPVRydWUsIG5fbGluZXM9MykKICAgIHBy"
    "aW50KGYiICBTdGFuZGFyZCBBbnN3ZXJzOiB7Y2hlY2tfcGFnZV9jb3VudChwKX0gcGFnZShzKSIpCiAg"
    "ICBidWlsdFsic3RkX2FucyJdLmFwcGVuZChwKQoKICAgICMgU3VwcG9ydGVkIGFuc3dlcnMKICAgIHAg"
    "PSBmIntPVVRfRElSfS97bHR9X1N1cHBvcnRlZF9BbnN3ZXJzLnBkZiIKICAgIGJ1aWxkX3BhZ2UocCwg"
    "bHQsIHN1cF90ZXh0LCBzdXBfcXMsIGRhdGVfc3RyLCBpc19hbnN3ZXI9VHJ1ZSwgbl9saW5lcz0yKQog"
    "ICAgcHJpbnQoZiIgIFN1cHBvcnRlZCBBbnN3ZXJzOiB7Y2hlY2tfcGFnZV9jb3VudChwKX0gcGFnZShz"
    "KSIpCiAgICBidWlsdFsic3VwX2FucyJdLmFwcGVuZChwKQoKcHJpbnQoIlxuTWVyZ2luZy4uLiIpCgoj"
    "IFN0YW5kYXJkIFB1cGlsOiBWb2MgKyBSZXQgKyBJbmYKbWVyZ2VfcGRmcyhidWlsdFsic3RkX3B1cGls"
    "Il0sCiAgICAgICAgICAgIi9tbnQvdXNlci1kYXRhL291dHB1dHMvVDVXMl9TdGFuZGFyZF9QdXBpbC5w"
    "ZGYiKQoKIyBTdXBwb3J0ZWQgUHVwaWw6IFZvYyArIFJldCArIEluZgptZXJnZV9wZGZzKGJ1aWx0WyJz"
    "dXBfcHVwaWwiXSwKICAgICAgICAgICAiL21udC91c2VyLWRhdGEvb3V0cHV0cy9UNVcyX1N1cHBvcnRl"
    "ZF9QdXBpbC5wZGYiKQoKIyBBbGwgQW5zd2VyczogVm9jIFN0ZCwgVm9jIFN1cCwgUmV0IFN0ZCwgUmV0"
    "IFN1cCwgSW5mIFN0ZCwgSW5mIFN1cAphbnNfb3JkZXIgPSBbXQpmb3IgaSBpbiByYW5nZSgzKToKICAg"
    "IGFuc19vcmRlci5hcHBlbmQoYnVpbHRbInN0ZF9hbnMiXVtpXSkKICAgIGFuc19vcmRlci5hcHBlbmQo"
    "YnVpbHRbInN1cF9hbnMiXVtpXSkKbWVyZ2VfcGRmcyhhbnNfb3JkZXIsCiAgICAgICAgICAgIi9tbnQv"
    "dXNlci1kYXRhL291dHB1dHMvVDVXMl9BbGxfQW5zd2Vycy5wZGYiKQoKIyBDbGVhbiB1cCBpbmRpdmlk"
    "dWFsIGZpbGVzCmltcG9ydCBzaHV0aWwKc2h1dGlsLnJtdHJlZShPVVRfRElSKQoKcHJpbnQoIkRvbmUu"
    "IikKcHJpbnQoIiAgVDVXMl9TdGFuZGFyZF9QdXBpbC5wZGY6IiwgUGRmUmVhZGVyKCIvbW50L3VzZXIt"
    "ZGF0YS9vdXRwdXRzL1Q1VzJfU3RhbmRhcmRfUHVwaWwucGRmIikucGFnZXMuX19sZW5fXygpLCAicGFn"
    "ZXMiKQpwcmludCgiICBUNVcyX1N1cHBvcnRlZF9QdXBpbC5wZGY6IiwgUGRmUmVhZGVyKCIvbW50L3Vz"
    "ZXItZGF0YS9vdXRwdXRzL1Q1VzJfU3VwcG9ydGVkX1B1cGlsLnBkZiIpLnBhZ2VzLl9fbGVuX18oKSwg"
    "InBhZ2VzIikKcHJpbnQoIiAgVDVXMl9BbGxfQW5zd2Vycy5wZGY6IiwgUGRmUmVhZGVyKCIvbW50L3Vz"
    "ZXItZGF0YS9vdXRwdXRzL1Q1VzJfQWxsX0Fuc3dlcnMucGRmIikucGFnZXMuX19sZW5fXygpLCAicGFn"
    "ZXMiKQo="
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
