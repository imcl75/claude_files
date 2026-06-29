---
name: being-a-reader
description: "Create a full week of Being a Reader reading comprehension resources. Use this skill whenever Innes asks for reading lessons, Being a Reader lessons, reading comprehension resources, vocabulary/retrieval/inference lessons, or says things like 'make this week's reading', 'create the reading for next week', 'Being a Reader for [text]', 'reading lessons linked to [book]'. Also trigger when he uploads content and mentions reading questions, comprehension questions, or refers to the three-lesson reading cycle. This skill produces 5 files: 3 PDFs (Standard Pupil, Supported Pupil, All Answers), 1 PPTX (teaching slides), and 1 XLSX (content data file). Always use this skill even for partial requests like 'just the PDFs' or 'just the PPTX' — the skill handles selective output."
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
- Standard extract: **200–250 words, single paragraph**
- Supported extract: **130–150 words, single simpler paragraph**
- Embed lesson vocabulary words naturally in the standard extract

### Vocabulary (5 words per lesson, 15 total)

- Tier 2 words, accessible for Y4 (age 8–9)
- Child-friendly definition: one clear sentence
- Focus word (Write it 5 times slide) = the most commonly encountered Tier 2 word
- Never repeat words across weeks on the same topic

### Questions

- Standard: 7 questions. Supported: 5 questions (genuinely easier, not just fewer)
- Questions progress Q1 (easiest) → Q7 (hardest)
- **Q7 is always first to drop** if the page doesn't fit on a single A4
- Y4 calibration: answerable in 1–3 sentences by an 8–9 year old
- Use at least 3 different question formats per lesson
- See `references/question-types.md` for all format specifications

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

```python
BOX_BORDER = (0.173, 0.173, 0.424)   # #2c2c6c — text box border, question labels
BOX_BG     = (0.941, 0.941, 0.973)   # #f0f0f8 — text box background
GREEN      = (0.102, 0.478, 0.102)   # #1a7a1a — answer text
DARK       = (0.133, 0.133, 0.133)   # body text
GREY_LINE  = (0.6, 0.6, 0.6)        # answer lines, table borders
```

### Header Layout — EXACT (do not vary)

```
DD/MM/YYYY                     Day name    [reader icon]
                                            reader
Key Question
Are England and Brazil different?
LF: [learning focus]
I can [statement 1]
I can [statement 2]
─────────────────────────────────────────────────────────
```

- **Row 1 left**: date in numeric format `DD/MM/YYYY`
- **Row 1 right**: day name (e.g. Monday) right-aligned. Reader icon above it at the far right, with "reader" label centred below the icon.
- **"Key Question"**: bold 8pt, on its own line below the icon/date row
- **Key question title**: bold 10pt, underlined, dark blue (`#2c2c6c`)
- **LF and I can lines**: plain 8pt
- **Bottom divider**: thin grey line

```python
# Correct — see draw_header() in build_reading_pdfs.py
# WRONG — do not put Key Question and date on the same line
# WRONG — do not put icon inline between Key Question and date
```

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

**Always clone the previous week's PPTX via XML replacement.** This preserves all animations, images, fonts, and formatting exactly.

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

**After QA:** save the working PPTX as the template for the following week.

---

## Step 7: File Naming and Output

```
{TaWb}_Being_a_Reader.pptx         e.g. T5W2_Being_a_Reader.pptx
Reading_Content_{TaWb}.xlsx        e.g. Reading_Content_T5W2.xlsx
{TaWb}_Standard_Pupil.pdf          e.g. T5W2_Standard_Pupil.pdf
{TaWb}_Supported_Pupil.pdf         e.g. T5W2_Supported_Pupil.pdf
{TaWb}_All_Answers.pdf             e.g. T5W2_All_Answers.pdf
```

Before copying, run the layout validator on the PPTX:

```bash
# Fetch layout validator if not already present
if [ ! -f /home/claude/validate_pptx_layout.py ]; then
    TOKEN=$(grep -ro 'github_pat_[A-Za-z0-9_]*' /mnt/skills/user/github-sync/ 2>/dev/null | head -1 | sed 's/.*://')
    curl -s -H "Authorization: token ${TOKEN}" \
      "https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/validate_pptx_layout.py" \
      -o /home/claude/validate_pptx_layout.py
fi

python3 /home/claude/validate_pptx_layout.py <TaWb_Being_a_Reader.pptx> --warnings
```

Fix any ERRORs, then copy all 5 to `/mnt/user-data/outputs/` and use `present_files`.

---

## Vocabulary Reference

### Words used — I Want My Hat Back topic (do not repeat)

**T5W1:** dialogue, persistent, suspicious, repetition, reveal, pattern, deny, politely, panicked, hopeless, technique, infer, omission, echo, impression

**T5W2:** courteous, naive, indifferent, emphatic, deceiving, pattern, calm, stands out, suddenly, direct, deliberately, defensive, recognise, guilt, structure

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
    "cmF3IHRoZSBsZWFybmluZyBsYWJlbCBoZWFkZXIgbWF0Y2hpbmcgdGhlIHNjaG9vbCBmb3JtYXQuIFJl"
    "dHVybnMgeSBhZnRlciBoZWFkZXIuIiIiCiAgICB5ID0gSCAtIE1BUkdJTgogICAgZGF5LCBkYXRlID0g"
    "ZGF0ZV9zdHIKCiAgICAjIC0tLSBSb3cgMTogZGF0ZSB0b3AtbGVmdCwgaWNvbiArICJyZWFkZXIiIHRv"
    "cC1yaWdodCAtLS0KICAgIElDT05fU1ogPSA5ICogbW0KICAgIGljb25feCA9IE1BUkdJTiArIENXIC0g"
    "SUNPTl9TWgogICAgaWNvbl95ID0geSAtIElDT05fU1ogLSAxICogbW0KCiAgICAjIERhdGUgdG9wIGxl"
    "ZnQKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJL"
    "KQogICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwgeSAtIDQgKiBtbSwgZGF0ZSkKCiAgICAjIERheSBuYW1l"
    "IHRvcCByaWdodCAodXNlciBwcmVmZXJlbmNlOiBkYXkgb24gcmlnaHQpCiAgICBjLmRyYXdSaWdodFN0"
    "cmluZyhNQVJHSU4gKyBDVywgeSAtIDQgKiBtbSwgZGF5KQoKICAgICMgUmVhZGVyIGljb24g4oCUIHRv"
    "cCByaWdodCwgbGVmdCBvZiB3aGVyZSB0aGUgZGF5IHRleHQgZW5kcywKICAgICMgcG9zaXRpb25lZCBz"
    "byBpdHMgcmlnaHQgZWRnZSBhbGlnbnMgd2l0aCByaWdodCBtYXJnaW4KICAgIHRyeToKICAgICAgICBj"
    "LmRyYXdJbWFnZShJQ09OX1BBVEgsIGljb25feCwgaWNvbl95LAogICAgICAgICAgICAgICAgICAgIHdp"
    "ZHRoPUlDT05fU1osIGhlaWdodD1JQ09OX1NaLAogICAgICAgICAgICAgICAgICAgIG1hc2s9J2F1dG8n"
    "LCBwcmVzZXJ2ZUFzcGVjdFJhdGlvPVRydWUpCiAgICBleGNlcHQgRXhjZXB0aW9uOgogICAgICAgIHBh"
    "c3MKICAgICMgInJlYWRlciIgbGFiZWwgY2VudHJlZCBiZWxvdyB0aGUgaWNvbgogICAgYy5zZXRGb250"
    "KCJIZWx2ZXRpY2EiLCA3KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLmRyYXdDZW50"
    "cmVkU3RyaW5nKGljb25feCArIElDT05fU1ogLyAyLCBpY29uX3kgLSAzICogbW0sICJyZWFkZXIiKQoK"
    "ICAgIHkgLT0gSUNPTl9TWiArIDUgKiBtbSAgIyBtb3ZlIHBhc3QgaWNvbiByb3cKCiAgICAjIC0tLSAi"
    "S2V5IFF1ZXN0aW9uIiBsYWJlbCAtLS0KICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4KQog"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gMyAq"
    "IG1tLCAiS2V5IFF1ZXN0aW9uIikKICAgIHkgLT0gNC41ICogbW0KCiAgICAjIC0tLSBLZXkgcXVlc3Rp"
    "b24g4oCUIGJvbGQsIHVuZGVybGluZWQsIGRhcmsgYmx1ZSAtLS0KICAgIGMuc2V0Rm9udCgiSGVsdmV0"
    "aWNhLUJvbGQiLCAxMCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKDAuMTczLCAwLjE3MywgMC40MjQpCiAg"
    "ICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gNCAqIG1tLCBrZXlfcSkKICAgIGtxX3cgPSBjLnN0cmlu"
    "Z1dpZHRoKGtleV9xLCAiSGVsdmV0aWNhLUJvbGQiLCAxMCkKICAgIGMuc2V0TGluZVdpZHRoKDAuNSkK"
    "ICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC4xNzMsIDAuMTczLCAwLjQyNCkKICAgIGMubGluZShNQVJH"
    "SU4sIHkgLSA1ICogbW0sIE1BUkdJTiArIGtxX3csIHkgLSA1ICogbW0pCiAgICB5IC09IDYgKiBtbQoK"
    "ICAgICMgLS0tIExGIGxpbmUgLS0tCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDgpCiAgICBjLnNl"
    "dEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHkgLSAzLjUgKiBtbSwg"
    "bGYpCiAgICB5IC09IDQuNSAqIG1tCgogICAgIyAtLS0gSSBjYW4gbGluZXMgLS0tCiAgICBjLmRyYXdT"
    "dHJpbmcoTUFSR0lOLCB5IC0gMy41ICogbW0sIGljYW4xKQogICAgeSAtPSA0ICogbW0KICAgIGMuZHJh"
    "d1N0cmluZyhNQVJHSU4sIHkgLSAzLjUgKiBtbSwgaWNhbjIpCiAgICB5IC09IDQuNSAqIG1tCgogICAg"
    "IyAtLS0gQm90dG9tIGRpdmlkZXIgLS0tCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUp"
    "CiAgICBjLnNldExpbmVXaWR0aCgwLjUpCiAgICBjLmxpbmUoTUFSR0lOLCB5LCBNQVJHSU4gKyBDVywg"
    "eSkKICAgIHkgLT0gMiAqIG1tCgogICAgcmV0dXJuIHkKCgpkZWYgd3JhcF90ZXh0KGMsIHRleHQsIGZv"
    "bnQsIHNpemUsIG1heF93KToKICAgICIiIldyYXAgdGV4dCB0byBsaW5lcyBmaXR0aW5nIG1heF93LiBS"
    "ZXR1cm5zIGxpc3Qgb2YgbGluZXMuIiIiCiAgICB3b3JkcyA9IHRleHQuc3BsaXQoKQogICAgbGluZXMs"
    "IGxpbmUgPSBbXSwgJycKICAgIGZvciB3IGluIHdvcmRzOgogICAgICAgIHRlc3QgPSAobGluZSArICcg"
    "JyArIHcpLnN0cmlwKCkKICAgICAgICBpZiBjLnN0cmluZ1dpZHRoKHRlc3QsIGZvbnQsIHNpemUpIDw9"
    "IG1heF93OgogICAgICAgICAgICBsaW5lID0gdGVzdAogICAgICAgIGVsc2U6CiAgICAgICAgICAgIGlm"
    "IGxpbmU6CiAgICAgICAgICAgICAgICBsaW5lcy5hcHBlbmQobGluZSkKICAgICAgICAgICAgbGluZSA9"
    "IHcKICAgIGlmIGxpbmU6CiAgICAgICAgbGluZXMuYXBwZW5kKGxpbmUpCiAgICByZXR1cm4gbGluZXMg"
    "b3IgWycnXQoKCmRlZiBkcmF3X3RleHRfYm94KGMsIHRleHQsIHlfdG9wLCBmb250X3NpemU9MTAuNSk6"
    "CiAgICAiIiJEcmF3IHRoZSByZWFkaW5nIHRleHQgYm94LiBSZXR1cm5zIHkgYWZ0ZXIgYm94LiIiIgog"
    "ICAgbGluZXMgPSB3cmFwX3RleHQoYywgdGV4dCwgIkhlbHZldGljYSIsIGZvbnRfc2l6ZSwgQ1cgLSA2"
    "Km1tKQogICAgbGluZV9oID0gZm9udF9zaXplICogMS40CiAgICBib3hfaCA9IGxlbihsaW5lcykgKiBs"
    "aW5lX2ggKyA1Km1tCgogICAgIyBCb3gKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpCT1hfQkcpCiAgICBj"
    "LnNldFN0cm9rZUNvbG9yUkdCKCpCT1hfQk9SREVSKQogICAgYy5zZXRMaW5lV2lkdGgoMC44KQogICAg"
    "Yy5yb3VuZFJlY3QoTUFSR0lOLCB5X3RvcCAtIGJveF9oLCBDVywgYm94X2gsIDIqbW0sIGZpbGw9MSwg"
    "c3Ryb2tlPTEpCgogICAgIyBUZXh0CiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuc2V0"
    "Rm9udCgiSGVsdmV0aWNhIiwgZm9udF9zaXplKQogICAgdHkgPSB5X3RvcCAtIDMqbW0gLSBmb250X3Np"
    "emUgKiAwLjcyCiAgICBmb3IgbGluZSBpbiBsaW5lczoKICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lO"
    "ICsgMyptbSwgdHksIGxpbmUpCiAgICAgICAgdHkgLT0gbGluZV9oCgogICAgcmV0dXJuIHlfdG9wIC0g"
    "Ym94X2ggLSAzKm1tCgoKZGVmIGFuc3dlcl9saW5lcyhjLCB5LCBuLCBnYXA9Ni41Km1tKToKICAgICIi"
    "IkRyYXcgbiBzb2xpZCBhbnN3ZXIgbGluZXMuIFJldHVybnMgeSBhZnRlciBsaW5lcy4iIiIKICAgIGMu"
    "c2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgIGZv"
    "ciBpIGluIHJhbmdlKG4pOgogICAgICAgIGx5ID0geSAtIChpICsgMSkgKiBnYXAKICAgICAgICBjLmxp"
    "bmUoTUFSR0lOLCBseSwgTUFSR0lOICsgQ1csIGx5KQogICAgcmV0dXJuIHkgLSBuICogZ2FwIC0gMipt"
    "bQoKCmRlZiBxX2xhYmVsKGMsIHFudW0sIHRleHQsIHksIGlzX2Fuc3dlcj1GYWxzZSwgYW5zX2NvbG91"
    "cj1GYWxzZSk6CiAgICAiIiJEcmF3IHF1ZXN0aW9uIGxhYmVsLiBSZXR1cm5zIHkgYWZ0ZXIgdGV4dC4i"
    "IiIKICAgIGNvbG91ciA9IEdSRUVOIGlmIGFuc19jb2xvdXIgZWxzZSBEQVJLCiAgICBjLnNldEZpbGxD"
    "b2xvclJHQigqY29sb3VyKQogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICBsYWJl"
    "bCA9IGYie3FudW1bMTpdfS4gIgogICAgbHcgPSBjLnN0cmluZ1dpZHRoKGxhYmVsLCAiSGVsdmV0aWNh"
    "LUJvbGQiLCA5KQogICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwgeSwgbGFiZWwpCiAgICBsaW5lcyA9IHdy"
    "YXBfdGV4dChjLCB0ZXh0LCAiSGVsdmV0aWNhLUJvbGQiLCA5LCBDVyAtIGx3KQogICAgZm9yIGksIGxp"
    "bmUgaW4gZW51bWVyYXRlKGxpbmVzKToKICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgbHcsIHkg"
    "LSBpICogKDkgKiAxLjM1KSwgbGluZSkKICAgIHJldHVybiB5IC0gbGVuKGxpbmVzKSAqICg5ICogMS4z"
    "NSkgLSAxKm1tCgoKZGVmIGRyYXdfbWNfcHVwaWwoYywgb3B0aW9ucywgeSk6CiAgICAiIiI0LWNlbGwg"
    "TUMgdGFibGUsIG5vIGhpZ2hsaWdodC4iIiIKICAgIGNvbF93ID0gQ1cgLyAyCiAgICByb3dfaCA9IDYq"
    "bW0KICAgICMgVHdvIHJvd3Mgb2YgMgogICAgZm9yIHJvdyBpbiByYW5nZSgyKToKICAgICAgICBmb3Ig"
    "Y29sIGluIHJhbmdlKDIpOgogICAgICAgICAgICBpZHggPSByb3cgKiAyICsgY29sCiAgICAgICAgICAg"
    "IGlmIGlkeCA+PSBsZW4ob3B0aW9ucyk6CiAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICB4"
    "ID0gTUFSR0lOICsgY29sICogY29sX3cKICAgICAgICAgICAgcnkgPSB5IC0gcm93ICogcm93X2gKICAg"
    "ICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAgICAgICAgYy5zZXRTdHJva2VD"
    "b2xvclJHQigwLjcsIDAuNywgMC43KQogICAgICAgICAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICAg"
    "ICAgICAgIGMucmVjdCh4LCByeSAtIHJvd19oLCBjb2xfdywgcm93X2gsIGZpbGw9MSwgc3Ryb2tlPTEp"
    "CiAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgICAgICBjLnNldEZvbnQo"
    "IkhlbHZldGljYSIsIDguNSkKICAgICAgICAgICAgYy5kcmF3U3RyaW5nKHggKyAyKm1tLCByeSAtIHJv"
    "d19oICsgMiptbSwgb3B0aW9uc1tpZHhdKQogICAgcmV0dXJuIHkgLSAyICogcm93X2ggLSAxLjUqbW0K"
    "CgpkZWYgZHJhd19tY19hbnN3ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSk6CiAgICAiIiI0LWNlbGwg"
    "TUMgdGFibGUsIGNvcnJlY3QgY2VsbCBoaWdobGlnaHRlZCBncmVlbi4iIiIKICAgIGNvbF93ID0gQ1cg"
    "LyAyCiAgICByb3dfaCA9IDYqbW0KICAgIGZvciByb3cgaW4gcmFuZ2UoMik6CiAgICAgICAgZm9yIGNv"
    "bCBpbiByYW5nZSgyKToKICAgICAgICAgICAgaWR4ID0gcm93ICogMiArIGNvbAogICAgICAgICAgICBp"
    "ZiBpZHggPj0gbGVuKG9wdGlvbnMpOgogICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAgeCA9"
    "IE1BUkdJTiArIGNvbCAqIGNvbF93CiAgICAgICAgICAgIHJ5ID0geSAtIHJvdyAqIHJvd19oCiAgICAg"
    "ICAgICAgIGlzX2NvcnJlY3QgPSBvcHRpb25zW2lkeF0gPT0gY29ycmVjdAogICAgICAgICAgICBpZiBp"
    "c19jb3JyZWN0OgogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC44NSwgMC45NSwgMC44"
    "NSkKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDEsIDEs"
    "IDEpCiAgICAgICAgICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoMC43LCAwLjcsIDAuNykKICAgICAgICAg"
    "ICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAgICAgICAgICBjLnJlY3QoeCwgcnkgLSByb3dfaCwgY29s"
    "X3csIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgICAgICBpZiBpc19jb3JyZWN0OgogICAg"
    "ICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgICAgICAgICAgYy5zZXRG"
    "b250KCJIZWx2ZXRpY2EtQm9sZCIsIDguNSkKICAgICAgICAgICAgICAgIGMuZHJhd1N0cmluZyh4ICsg"
    "MiptbSwgcnkgLSByb3dfaCArIDIqbW0sIG9wdGlvbnNbaWR4XSArICIgXHUyNzEzIikKICAgICAgICAg"
    "ICAgZWxzZToKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgICAg"
    "ICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA4LjUpCiAgICAgICAgICAgICAgICBjLmRyYXdTdHJp"
    "bmcoeCArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBvcHRpb25zW2lkeF0pCiAgICByZXR1cm4geSAt"
    "IDIgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBkcmF3X21hdGNoX3B1cGlsKGMsIHBhaXJzLCB5KToKICAg"
    "ICIiIk1hdGNoIHRhYmxlIOKAlCBsZWZ0IHdvcmRzLCBnYXAsIHJpZ2h0IGRlZmluaXRpb25zIChzY3Jh"
    "bWJsZWQpLiIiIgogICAgbHcgPSBDVyAqIDAuMjgKICAgIHJ3ID0gQ1cgKiAwLjQ4CiAgICBnYXAgPSBD"
    "VyAtIGx3IC0gcncgICMgMjQlIGdhcCBpbiBtaWRkbGUKICAgIHJvd19oID0gNyptbQogICAgYy5zZXRT"
    "dHJva2VDb2xvclJHQigwLjcsIDAuNywgMC43KQogICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAgIyBT"
    "Y3JhbWJsZSByaWdodCBjb2x1bW4KICAgIHJpZ2h0cyA9IFtyIGZvciBfLCByIGluIHBhaXJzXQogICAg"
    "c2NyYW1ibGVkID0gcmlnaHRzWzE6XSArIHJpZ2h0c1s6MV0KICAgIGZvciBpLCAobGVmdCwgXykgaW4g"
    "ZW51bWVyYXRlKHBhaXJzKToKICAgICAgICByeSA9IHkgLSBpICogcm93X2gKICAgICAgICBjLnNldEZp"
    "bGxDb2xvclJHQigwLjk2LCAwLjk2LCAwLjk2KQogICAgICAgIGMucmVjdChNQVJHSU4sIHJ5IC0gcm93"
    "X2gsIGx3LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigq"
    "REFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOC41KQogICAgICAgIGMuZHJh"
    "d1N0cmluZyhNQVJHSU4gKyAyKm1tLCByeSAtIHJvd19oICsgMiptbSwgbGVmdCkKICAgICAgICByeCA9"
    "IE1BUkdJTiArIGx3ICsgZ2FwCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC45NiwgMC45NiwgMC45"
    "NikKICAgICAgICBjLnJlY3QocngsIHJ5IC0gcm93X2gsIHJ3LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9"
    "MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYSIsIDguNSkKICAgICAgICBjLmRyYXdTdHJpbmcocnggKyAyKm1tLCByeSAtIHJvd19oICsgMipt"
    "bSwgc2NyYW1ibGVkW2ldKQogICAgcmV0dXJuIHkgLSBsZW4ocGFpcnMpICogcm93X2ggLSAxLjUqbW0K"
    "CgpkZWYgZHJhd19tYXRjaF9hbnN3ZXIoYywgcGFpcnMsIHkpOgogICAgIiIiTWF0Y2ggdGFibGUgd2l0"
    "aCBncmVlbiBjb25uZWN0b3JzLiIiIgogICAgbHcgPSBDVyAqIDAuMjgKICAgIHJ3ID0gQ1cgKiAwLjQ4"
    "CiAgICBnYXAgPSBDVyAtIGx3IC0gcncKICAgIHJvd19oID0gNyptbQogICAgYy5zZXRTdHJva2VDb2xv"
    "clJHQigwLjcsIDAuNywgMC43KQogICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAgZm9yIGksIChsZWZ0"
    "LCByaWdodCkgaW4gZW51bWVyYXRlKHBhaXJzKToKICAgICAgICByeSA9IHkgLSBpICogcm93X2gKICAg"
    "ICAgICBjLnNldEZpbGxDb2xvclJHQigwLjk2LCAwLjk2LCAwLjk2KQogICAgICAgIGMucmVjdChNQVJH"
    "SU4sIHJ5IC0gcm93X2gsIGx3LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZp"
    "bGxDb2xvclJHQigqR1JFRU4pCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDguNSkK"
    "ICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMiptbSwgcnkgLSByb3dfaCArIDIqbW0sIGxlZnQp"
    "CiAgICAgICAgcnggPSBNQVJHSU4gKyBsdyArIGdhcAogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKDAu"
    "ODUsIDAuOTUsIDAuODUpCiAgICAgICAgYy5yZWN0KHJ4LCByeSAtIHJvd19oLCBydywgcm93X2gsIGZp"
    "bGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgIGMu"
    "c2V0Rm9udCgiSGVsdmV0aWNhLUJvbGRPYmxpcXVlIiwgOC41KQogICAgICAgIGMuZHJhd1N0cmluZyhy"
    "eCArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCAiXHUyMDE0XHUyNWEwICAiICsgcmlnaHQpCiAgICBy"
    "ZXR1cm4geSAtIGxlbihwYWlycykgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBkcmF3X2ZpbGwoYywgc2Vu"
    "dGVuY2UsIHksIGlzX2Fuc3dlcj1GYWxzZSwgYW5zd2VyPSIiKToKICAgICIiIkRyYXcgZmlsbC1pbi1i"
    "bGFuayBzZW50ZW5jZSB3aXRoIHVuZGVybGluZSBibGFua3Mgb3IgZ3JlZW4gYW5zd2Vycy4iIiIKICAg"
    "IHBhcnRzID0gc2VudGVuY2Uuc3BsaXQoIl9fX19fX19fX19fX19fIikKICAgIGJsYW5rc19uZWVkZWQg"
    "PSBsZW4ocGFydHMpIC0gMQogICAgYW5zd2VycyA9IFthLnN0cmlwKCkgZm9yIGEgaW4gYW5zd2VyLnNw"
    "bGl0KCIvIildIGlmIGFuc3dlciBlbHNlIFtdCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIHggPSBNQVJHSU4KICAgIGJsYW5rX3cgPSAyOCpt"
    "bQogICAgZm9yIHBpLCBwYXJ0IGluIGVudW1lcmF0ZShwYXJ0cyk6CiAgICAgICAgIyBNZWFzdXJlIGFu"
    "ZCBkcmF3IHRoZSB0ZXh0IHBhcnQKICAgICAgICBwdyA9IGMuc3RyaW5nV2lkdGgocGFydCwgIkhlbHZl"
    "dGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3RyaW5nKHgsIHksIHBhcnQpCiAgICAgICAgeCArPSBwdwog"
    "ICAgICAgIGlmIHBpIDwgYmxhbmtzX25lZWRlZDoKICAgICAgICAgICAgaWYgaXNfYW5zd2VyIGFuZCBw"
    "aSA8IGxlbihhbnN3ZXJzKToKICAgICAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikK"
    "ICAgICAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgICAgICAgICAg"
    "ICAgYy5kcmF3U3RyaW5nKHggKyAxKm1tLCB5LCBhbnN3ZXJzW3BpXSkKICAgICAgICAgICAgICAgIHgg"
    "Kz0gYmxhbmtfdwogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAg"
    "ICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAgICAgIGVsc2U6CiAgICAgICAg"
    "ICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKCpHUkVZX0xJTkUpCiAgICAgICAgICAgICAgICBjLnNl"
    "dExpbmVXaWR0aCgwLjUpCiAgICAgICAgICAgICAgICBjLmxpbmUoeCwgeSAtIDEqbW0sIHggKyBibGFu"
    "a193LCB5IC0gMSptbSkKICAgICAgICAgICAgICAgIHggKz0gYmxhbmtfdwogICAgcmV0dXJuIHkgLSA1"
    "LjUqbW0KCgpkZWYgZHJhd190aWNrX3B1cGlsKGMsIG9wdGlvbnMsIHkpOgogICAgIiIiVGljayBvcHRp"
    "b25zIHdpdGggc3F1YXJlIGJ1bGxldHMuIiIiCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICMgMiBvciAzIHBlciByb3cgZGVwZW5kaW5nIG9u"
    "IGNvdW50CiAgICAjIENob29zZSBjb2x1bW5zIGJhc2VkIG9uIG9wdGlvbiBsZW5ndGgKICAgIG1heF9s"
    "ZW4gPSBtYXgobGVuKG8pIGZvciBvIGluIG9wdGlvbnMpCiAgICBpZiBtYXhfbGVuID4gMjU6CiAgICAg"
    "ICAgcGVyX3JvdyA9IDIgICMgbG9uZyBvcHRpb25zOiAyIHBlciByb3cKICAgIGVsaWYgbGVuKG9wdGlv"
    "bnMpID09IDU6CiAgICAgICAgcGVyX3JvdyA9IDUgICMgNSBzaG9ydCBvcHRpb25zOiBhbGwgb24gb25l"
    "IHJvdwogICAgZWxzZToKICAgICAgICBwZXJfcm93ID0gNAogICAgY29sX3cgPSBDVyAvIHBlcl9yb3cK"
    "ICAgIHJvd3MgPSAobGVuKG9wdGlvbnMpICsgcGVyX3JvdyAtIDEpIC8vIHBlcl9yb3cKICAgIHJvd19o"
    "ID0gNS41Km1tCiAgICBmb3IgaSwgb3B0IGluIGVudW1lcmF0ZShvcHRpb25zKToKICAgICAgICByb3cg"
    "PSBpIC8vIHBlcl9yb3cKICAgICAgICBjb2wgPSBpICUgcGVyX3JvdwogICAgICAgIGMuZHJhd1N0cmlu"
    "ZyhNQVJHSU4gKyBjb2wgKiBjb2xfdywgeSAtIHJvdyAqIHJvd19oLCBvcHQpCiAgICByZXR1cm4geSAt"
    "IHJvd3MgKiByb3dfaCAtIDMqbW0KCgpkZWYgZHJhd190aWNrX2Fuc3dlcihjLCBvcHRpb25zLCBjb3Jy"
    "ZWN0LCB5KToKICAgICIiIlRpY2sgb3B0aW9ucyB3aXRoIGNvcnJlY3Qgb25lcyBpbiBib2xkIGdyZWVu"
    "LiIiIgogICAgbWF4X2xlbiA9IG1heChsZW4obykgZm9yIG8gaW4gb3B0aW9ucykKICAgIGlmIG1heF9s"
    "ZW4gPiAyNToKICAgICAgICBwZXJfcm93ID0gMgogICAgZWxpZiBsZW4ob3B0aW9ucykgPT0gNToKICAg"
    "ICAgICBwZXJfcm93ID0gNQogICAgZWxzZToKICAgICAgICBwZXJfcm93ID0gNAogICAgY29sX3cgPSBD"
    "VyAvIHBlcl9yb3cKICAgIHJvd3MgPSAobGVuKG9wdGlvbnMpICsgcGVyX3JvdyAtIDEpIC8vIHBlcl9y"
    "b3cKICAgIHJvd19oID0gNS41Km1tCiAgICBmb3IgaSwgb3B0IGluIGVudW1lcmF0ZShvcHRpb25zKToK"
    "ICAgICAgICByb3cgPSBpIC8vIHBlcl9yb3cKICAgICAgICBjb2wgPSBpICUgcGVyX3JvdwogICAgICAg"
    "IGlmIG9wdCBpbiBjb3JyZWN0OgogICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqR1JFRU4pCiAg"
    "ICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA5KQogICAgICAgIGVsc2U6CiAgICAg"
    "ICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYSIsIDkpCiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiArIGNvbCAqIGNvbF93LCB5IC0gcm93"
    "ICogcm93X2gsIG9wdCkKICAgIHJldHVybiB5IC0gcm93cyAqIHJvd19oIC0gMyptbQoKCmRlZiBkcmF3"
    "X29yZGVyX3B1cGlsKGMsIGV2ZW50cywgeSk6CiAgICAiIiJOdW1iZXJlZCBvcmRlcmluZyBxdWVzdGlv"
    "bi4iIiIKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpE"
    "QVJLKQogICAgcm93X2ggPSA1LjUqbW0KICAgIGZvciBpLCBldiBpbiBlbnVtZXJhdGUoZXZlbnRzKToK"
    "ICAgICAgICByeSA9IHkgLSBpICogcm93X2gKICAgICAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICAg"
    "ICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjcsIDAuNywgMC43KQogICAgICAgIGMucmVjdChNQVJHSU4s"
    "IHJ5IC0gcm93X2ggKyAxKm1tLCA4Km1tLCA0Km1tLCBmaWxsPTAsIHN0cm9rZT0xKQogICAgICAgIGMu"
    "ZHJhd1N0cmluZyhNQVJHSU4gKyAxMCptbSwgcnkgLSByb3dfaCArIDIqbW0sIGV2KQogICAgcmV0dXJu"
    "IHkgLSBsZW4oZXZlbnRzKSAqIHJvd19oIC0gMS41Km1tCgoKZGVmIGRyYXdfb3JkZXJfYW5zd2VyKGMs"
    "IGV2ZW50cywgY29ycmVjdF9vcmRlciwgeSk6CiAgICAiIiJOdW1iZXJlZCBvcmRlcmluZyBxdWVzdGlv"
    "biB3aXRoIGFuc3dlcnMuIiIiCiAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICByb3dfaCA9"
    "IDUuNSptbQogICAgZm9yIGksIChldiwgbnVtKSBpbiBlbnVtZXJhdGUoemlwKGV2ZW50cywgY29ycmVj"
    "dF9vcmRlcikpOgogICAgICAgIHJ5ID0geSAtIGkgKiByb3dfaAogICAgICAgIGMuc2V0RmlsbENvbG9y"
    "UkdCKDAuODUsIDAuOTUsIDAuODUpCiAgICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjcsIDAuNywg"
    "MC43KQogICAgICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICAgICBjLnJlY3QoTUFSR0lOLCByeSAt"
    "IHJvd19oICsgMSptbSwgOCptbSwgNCptbSwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICBjLnNldEZp"
    "bGxDb2xvclJHQigqR1JFRU4pCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAg"
    "ICAgICAgYy5kcmF3Q2VudHJlZFN0cmluZyhNQVJHSU4gKyA0Km1tLCByeSAtIHJvd19oICsgMiptbSwg"
    "bnVtKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0Rm9udCgiSGVs"
    "dmV0aWNhIiwgOSkKICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgMTAqbW0sIHJ5IC0gcm93X2gg"
    "KyAyKm1tLCBldikKICAgIHJldHVybiB5IC0gbGVuKGV2ZW50cykgKiByb3dfaCAtIDEuNSptbQoKCmRl"
    "ZiBkcmF3X3dyaXR0ZW5fYW5zd2VyKGMsIGFuc3dlciwgeSwgbl9saW5lcz0zKToKICAgICIiIldyaXR0"
    "ZW4gYW5zd2VyOiBhbnN3ZXIgbGluZXMgKHB1cGlsKSBvciBncmVlbiBpdGFsaWMgdGV4dCAoYW5zd2Vy"
    "cykuIiIiCiAgICBpZiBhbnN3ZXI6CiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQogICAg"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLU9ibGlxdWUiLCA4LjUpCiAgICAgICAgbGluZXMgPSB3cmFw"
    "X3RleHQoYywgYW5zd2VyLCAiSGVsdmV0aWNhLU9ibGlxdWUiLCA4LjUsIENXKQogICAgICAgIGZvciBp"
    "LCBsaW5lIGluIGVudW1lcmF0ZShsaW5lcyk6CiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4s"
    "IHkgLSAoaSArIDEpICogNSptbSwgbGluZSkKICAgICAgICByZXR1cm4geSAtIGxlbihsaW5lcykgKiA1"
    "Km1tIC0gNCptbQogICAgZWxzZToKICAgICAgICByZXR1cm4gYW5zd2VyX2xpbmVzKGMsIHksIG5fbGlu"
    "ZXMpCgoKZGVmIHJlbmRlcl9xdWVzdGlvbihjLCBxLCB5LCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9"
    "MywgbWluX3k9MjAqbW0pOgogICAgIiIiUmVuZGVyIGEgc2luZ2xlIHF1ZXN0aW9uLiBSZXR1cm5zIG5l"
    "dyB5LCBvciBOb25lIGlmIG5vIHJvb20uIiIiCiAgICBxbnVtLCBxdHlwZSwgcXRleHQsIG9wdGlvbnMs"
    "IGNvcnJlY3QgPSBxCgogICAgIyBFc3RpbWF0ZSBoZWlnaHQKICAgIGxhYmVsX2ggPSBsZW4od3JhcF90"
    "ZXh0KGMsIHF0ZXh0LnNwbGl0KCdcbicpWzBdLCAiSGVsdmV0aWNhLUJvbGQiLCA5LCBDVyAtIDgqbW0p"
    "KSAqIDEyICsgNAogICAgZXh0cmEgPSAwCiAgICBpZiBxdHlwZSA9PSAibWMiOiAgICAgICAgICAgICBl"
    "eHRyYSA9IDE0Km1tCiAgICBlbGlmIHF0eXBlID09ICJtYXRjaCI6ICAgICAgICBleHRyYSA9IGxlbihv"
    "cHRpb25zKSAqIDcqbW0KICAgIGVsaWYgcXR5cGUgaW4gKCJ0aWNrMiIsInRpY2szIik6IGV4dHJhID0g"
    "KGxlbihvcHRpb25zKSAvLyAzICsgMSkgKiA2Km1tCiAgICBlbGlmIHF0eXBlID09ICJmaWxsIjogICAg"
    "ICAgICBleHRyYSA9IDYqbW0KICAgIGVsaWYgcXR5cGUgPT0gIm9yZGVyIjogICAgICAgIGV4dHJhID0g"
    "bGVuKG9wdGlvbnMpICogNiptbQogICAgZWxpZiBxdHlwZSA9PSAid3JpdHRlbiI6ICAgICAgZXh0cmEg"
    "PSBuX2xpbmVzICogNS41Km1tCiAgICB0b3RhbF9lc3QgPSBsYWJlbF9oICsgZXh0cmEgKyAzKm1tCgog"
    "ICAgaWYgeSAtIHRvdGFsX2VzdCA8IG1pbl95OgogICAgICAgIHJldHVybiBOb25lICAjIG5vIHJvb20K"
    "CiAgICAjIERyYXcgcXVlc3Rpb24gdGV4dAogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBj"
    "LnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgIGxhYmVsID0gZiJ7cW51bVsxOl19LiAiCiAg"
    "ICBsdyA9IGMuc3RyaW5nV2lkdGgobGFiZWwsICJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICBjLmRyYXdT"
    "dHJpbmcoTUFSR0lOLCB5LCBsYWJlbCkKICAgIHFfbGluZXNfYWxsID0gcXRleHQuc3BsaXQoJ1xuJykK"
    "ICAgICMgRm9yIGZpbGwtaW4tYmxhbmsgd2l0aCBhIHNlcGFyYXRlIHNlbnRlbmNlIGxpbmUsIG9ubHkg"
    "c2hvdyB0aGUgcHJvbXB0IGFzIHRoZSBsYWJlbAogICAgbGFiZWxfbGluZXNfdGV4dCA9IHFfbGluZXNf"
    "YWxsWzBdCiAgICBmaXJzdF9saW5lcyA9IHdyYXBfdGV4dChjLCBsYWJlbF9saW5lc190ZXh0LCAiSGVs"
    "dmV0aWNhLUJvbGQiLCA5LCBDVyAtIGx3KQogICAgZm9yIGksIGxpbmUgaW4gZW51bWVyYXRlKGZpcnN0"
    "X2xpbmVzKToKICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgbHcsIHkgLSBpICogKDkgKiAxLjM1"
    "KSwgbGluZSkKICAgIHkgLT0gbGVuKGZpcnN0X2xpbmVzKSAqICg5ICogMS4zNSkKICAgICMgRm9yIG5v"
    "bi1maWxsIHR5cGVzIHdpdGggYWRkaXRpb25hbCBsaW5lcyAobm90IHVzZWQgY3VycmVudGx5KSwgZHJh"
    "dyB0aGVtCiAgICBpZiBxdHlwZSAhPSAiZmlsbCI6CiAgICAgICAgZm9yIGV4dHJhX2xpbmUgaW4gcV9s"
    "aW5lc19hbGxbMTpdOgogICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYSIsIDkpCiAgICAgICAg"
    "ICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lO"
    "LCB5LCBleHRyYV9saW5lKQogICAgICAgICAgICB5IC09IDkgKiAxLjM1CiAgICB5IC09IDEqbW0KCiAg"
    "ICBpZiBxdHlwZSA9PSAibWMiOgogICAgICAgIGlmIGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRy"
    "YXdfbWNfYW5zd2VyKGMsIG9wdGlvbnMsIGNvcnJlY3QsIHkpCiAgICAgICAgZWxzZToKICAgICAgICAg"
    "ICAgeSA9IGRyYXdfbWNfcHVwaWwoYywgb3B0aW9ucywgeSkKICAgICAgICB5IC09IDEqbW0gICMgZXh0"
    "cmEgZ2FwIGFmdGVyIE1DIHRhYmxlCgogICAgZWxpZiBxdHlwZSA9PSAibWF0Y2giOgogICAgICAgIGlm"
    "IGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRyYXdfbWF0Y2hfYW5zd2VyKGMsIG9wdGlvbnMsIHkp"
    "CiAgICAgICAgZWxzZToKICAgICAgICAgICAgeSA9IGRyYXdfbWF0Y2hfcHVwaWwoYywgb3B0aW9ucywg"
    "eSkKICAgICAgICB5IC09IDEqbW0gICMgZXh0cmEgZ2FwIGFmdGVyIG1hdGNoIHRhYmxlCgogICAgZWxp"
    "ZiBxdHlwZSBpbiAoInRpY2syIiwgInRpY2szIik6CiAgICAgICAgaWYgaXNfYW5zd2VyOgogICAgICAg"
    "ICAgICB5ID0gZHJhd190aWNrX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KQogICAgICAgIGVs"
    "c2U6CiAgICAgICAgICAgIHkgPSBkcmF3X3RpY2tfcHVwaWwoYywgb3B0aW9ucywgeSkKCiAgICBlbGlm"
    "IHF0eXBlID09ICJmaWxsIjoKICAgICAgICAjIFRoZSBmaWxsIHNlbnRlbmNlIGlzIHRoZSBsYXN0IGVs"
    "ZW1lbnQgb2YgcV9saW5lc19hbGwgKG9yIHF0ZXh0IGlmIG5vIFxuKQogICAgICAgIGZpbGxfc2VudGVu"
    "Y2UgPSBxX2xpbmVzX2FsbFstMV0gaWYgbGVuKHFfbGluZXNfYWxsKSA+IDEgZWxzZSBxdGV4dAogICAg"
    "ICAgIHkgPSBkcmF3X2ZpbGwoYywgZmlsbF9zZW50ZW5jZSwgeSwgaXNfYW5zd2VyPWlzX2Fuc3dlciwg"
    "YW5zd2VyPWNvcnJlY3Qgb3IgIiIpCgogICAgZWxpZiBxdHlwZSA9PSAib3JkZXIiOgogICAgICAgIGlm"
    "IGlzX2Fuc3dlcjoKICAgICAgICAgICAgeSA9IGRyYXdfb3JkZXJfYW5zd2VyKGMsIG9wdGlvbnMsIGNv"
    "cnJlY3QsIHkpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgeSA9IGRyYXdfb3JkZXJfcHVwaWwoYywg"
    "b3B0aW9ucywgeSkKCiAgICBlbGlmIHF0eXBlID09ICJ3cml0dGVuIjoKICAgICAgICB5ID0gZHJhd193"
    "cml0dGVuX2Fuc3dlcihjLCBjb3JyZWN0IGlmIGlzX2Fuc3dlciBlbHNlIE5vbmUsIHksIG5fbGluZXM9"
    "bl9saW5lcykKCiAgICByZXR1cm4geSAtIDMqbW0KCgpkZWYgYnVpbGRfcGFnZShwYXRoLCBsZXNzb25f"
    "dHlwZSwgdGV4dCwgcXVlc3Rpb25zLCBkYXRlX3N0ciwgaXNfYW5zd2VyLCBuX2xpbmVzKToKICAgICIi"
    "IkJ1aWxkIGEgc2luZ2xlLXBhZ2UgUERGLiIiIgogICAgYyA9IGNhbnZhcy5DYW52YXMocGF0aCwgcGFn"
    "ZXNpemU9QTQpCiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKCiAgICB5ID0gZHJhd19oZWFkZXIo"
    "YywgbGVzc29uX3R5cGUsIGRhdGVfc3RyLCBLRVlfUSwKICAgICAgICAgICAgICAgICAgICBMRltsZXNz"
    "b25fdHlwZV0sIElDQU5bbGVzc29uX3R5cGVdWzBdLCBJQ0FOW2xlc3Nvbl90eXBlXVsxXSkKCiAgICB5"
    "ID0gZHJhd190ZXh0X2JveChjLCB0ZXh0LCB5KQoKICAgIG1pbl95ID0gMTIqbW0KICAgIGZvciBxIGlu"
    "IHF1ZXN0aW9uczoKICAgICAgICByZXN1bHQgPSByZW5kZXJfcXVlc3Rpb24oYywgcSwgeSwgaXNfYW5z"
    "d2VyPWlzX2Fuc3dlciwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbl9saW5lcz1uX2xp"
    "bmVzLCBtaW5feT1taW5feSkKICAgICAgICBpZiByZXN1bHQgaXMgTm9uZToKICAgICAgICAgICAgIyBE"
    "cm9wIFE3IGlmIG5vIHJvb20gKGxhc3QgcXVlc3Rpb24gaW4gbGlzdCkKICAgICAgICAgICAgYnJlYWsK"
    "ICAgICAgICB5ID0gcmVzdWx0CgogICAgYy5zYXZlKCkKICAgIHJldHVybiBwYXRoCgoKZGVmIGNoZWNr"
    "X3BhZ2VfY291bnQocGF0aCk6CiAgICByZWFkZXIgPSBQZGZSZWFkZXIocGF0aCkKICAgIHJldHVybiBs"
    "ZW4ocmVhZGVyLnBhZ2VzKQoKCmRlZiBtZXJnZV9wZGZzKGZpbGVfbGlzdCwgb3V0cHV0X3BhdGgpOgog"
    "ICAgd3JpdGVyID0gUGRmV3JpdGVyKCkKICAgIGZvciBmIGluIGZpbGVfbGlzdDoKICAgICAgICBmb3Ig"
    "cGFnZSBpbiBQZGZSZWFkZXIoZikucGFnZXM6CiAgICAgICAgICAgIHdyaXRlci5hZGRfcGFnZShwYWdl"
    "KQogICAgd2l0aCBvcGVuKG91dHB1dF9wYXRoLCAid2IiKSBhcyBmaDoKICAgICAgICB3cml0ZXIud3Jp"
    "dGUoZmgpCgoKIyDilIDilIAgQnVpbGQgYWxsIDEyIGluZGl2aWR1YWwgUERGcyDilIDilIDilIDilIDi"
    "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
    "lIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDi"
    "lIAKCmxlc3NvbnMgPSBbCiAgICAoIlZvY2FidWxhcnkiLCBTVERfVk9DLCBTVVBfVk9DLCBTVERfVk9D"
    "X1FTLCBTVVBfVk9DX1FTLCBEQVRFU1siVm9jYWJ1bGFyeSJdKSwKICAgICgiUmV0cmlldmFsIiwgIFNU"
    "RF9SRVQsIFNVUF9SRVQsIFNURF9SRVRfUVMsIFNVUF9SRVRfUVMsIERBVEVTWyJSZXRyaWV2YWwiXSks"
    "CiAgICAoIkluZmVyZW5jZSIsICBTVERfSU5GLCBTVVBfSU5GLCBTVERfSU5GX1FTLCBTVVBfSU5GX1FT"
    "LCBEQVRFU1siSW5mZXJlbmNlIl0pLApdCgpidWlsdCA9IHsKICAgICJzdGRfcHVwaWwiOiBbXSwgInN1"
    "cF9wdXBpbCI6IFtdLAogICAgInN0ZF9hbnMiOiBbXSwgInN1cF9hbnMiOiBbXSwKfQoKZm9yIGxlc3Nv"
    "bl90eXBlLCBzdGRfdGV4dCwgc3VwX3RleHQsIHN0ZF9xcywgc3VwX3FzLCBkYXRlX3N0ciBpbiBsZXNz"
    "b25zOgogICAgbHQgPSBsZXNzb25fdHlwZQogICAgcHJpbnQoZiJCdWlsZGluZyB7bHR9Li4uIikKCiAg"
    "ICAjIFN0YW5kYXJkIHB1cGlsCiAgICBwID0gZiJ7T1VUX0RJUn0ve2x0fV9TdGFuZGFyZF9QdXBpbC5w"
    "ZGYiCiAgICBidWlsZF9wYWdlKHAsIGx0LCBzdGRfdGV4dCwgc3RkX3FzLCBkYXRlX3N0ciwgaXNfYW5z"
    "d2VyPUZhbHNlLCBuX2xpbmVzPTMpCiAgICBwYWdlcyA9IGNoZWNrX3BhZ2VfY291bnQocCkKICAgIGlm"
    "IHBhZ2VzID4gMToKICAgICAgICBwcmludChmIiAgV0FSTklORzoge2x0fSBTdGFuZGFyZCBvdmVyZmxv"
    "d3MgKHtwYWdlc30gcGFnZXMpIOKAlCBkcm9wcGluZyBRNyIpCiAgICAgICAgYnVpbGRfcGFnZShwLCBs"
    "dCwgc3RkX3RleHQsIHN0ZF9xc1s6LTFdLCBkYXRlX3N0ciwgaXNfYW5zd2VyPUZhbHNlLCBuX2xpbmVz"
    "PTMpCiAgICBwcmludChmIiAgU3RhbmRhcmQgUHVwaWw6IHtjaGVja19wYWdlX2NvdW50KHApfSBwYWdl"
    "KHMpIikKICAgIGJ1aWx0WyJzdGRfcHVwaWwiXS5hcHBlbmQocCkKCiAgICAjIFN1cHBvcnRlZCBwdXBp"
    "bAogICAgcCA9IGYie09VVF9ESVJ9L3tsdH1fU3VwcG9ydGVkX1B1cGlsLnBkZiIKICAgIGJ1aWxkX3Bh"
    "Z2UocCwgbHQsIHN1cF90ZXh0LCBzdXBfcXMsIGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGlu"
    "ZXM9MikKICAgIHBhZ2VzID0gY2hlY2tfcGFnZV9jb3VudChwKQogICAgaWYgcGFnZXMgPiAxOgogICAg"
    "ICAgIHByaW50KGYiICBXQVJOSU5HOiB7bHR9IFN1cHBvcnRlZCBvdmVyZmxvd3MgKHtwYWdlc30gcGFn"
    "ZXMpIOKAlCBkcm9wcGluZyBRNSIpCiAgICAgICAgYnVpbGRfcGFnZShwLCBsdCwgc3VwX3RleHQsIHN1"
    "cF9xc1s6LTFdLCBkYXRlX3N0ciwgaXNfYW5zd2VyPUZhbHNlLCBuX2xpbmVzPTIpCiAgICBwcmludChm"
    "IiAgU3VwcG9ydGVkIFB1cGlsOiB7Y2hlY2tfcGFnZV9jb3VudChwKX0gcGFnZShzKSIpCiAgICBidWls"
    "dFsic3VwX3B1cGlsIl0uYXBwZW5kKHApCgogICAgIyBTdGFuZGFyZCBhbnN3ZXJzCiAgICBwID0gZiJ7"
    "T1VUX0RJUn0ve2x0fV9TdGFuZGFyZF9BbnN3ZXJzLnBkZiIKICAgIGJ1aWxkX3BhZ2UocCwgbHQsIHN0"
    "ZF90ZXh0LCBzdGRfcXMsIGRhdGVfc3RyLCBpc19hbnN3ZXI9VHJ1ZSwgbl9saW5lcz0zKQogICAgcHJp"
    "bnQoZiIgIFN0YW5kYXJkIEFuc3dlcnM6IHtjaGVja19wYWdlX2NvdW50KHApfSBwYWdlKHMpIikKICAg"
    "IGJ1aWx0WyJzdGRfYW5zIl0uYXBwZW5kKHApCgogICAgIyBTdXBwb3J0ZWQgYW5zd2VycwogICAgcCA9"
    "IGYie09VVF9ESVJ9L3tsdH1fU3VwcG9ydGVkX0Fuc3dlcnMucGRmIgogICAgYnVpbGRfcGFnZShwLCBs"
    "dCwgc3VwX3RleHQsIHN1cF9xcywgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1UcnVlLCBuX2xpbmVzPTIpCiAg"
    "ICBwcmludChmIiAgU3VwcG9ydGVkIEFuc3dlcnM6IHtjaGVja19wYWdlX2NvdW50KHApfSBwYWdlKHMp"
    "IikKICAgIGJ1aWx0WyJzdXBfYW5zIl0uYXBwZW5kKHApCgpwcmludCgiXG5NZXJnaW5nLi4uIikKCiMg"
    "U3RhbmRhcmQgUHVwaWw6IFZvYyArIFJldCArIEluZgptZXJnZV9wZGZzKGJ1aWx0WyJzdGRfcHVwaWwi"
    "XSwKICAgICAgICAgICAiL21udC91c2VyLWRhdGEvb3V0cHV0cy9UNVcyX1N0YW5kYXJkX1B1cGlsLnBk"
    "ZiIpCgojIFN1cHBvcnRlZCBQdXBpbDogVm9jICsgUmV0ICsgSW5mCm1lcmdlX3BkZnMoYnVpbHRbInN1"
    "cF9wdXBpbCJdLAogICAgICAgICAgICIvbW50L3VzZXItZGF0YS9vdXRwdXRzL1Q1VzJfU3VwcG9ydGVk"
    "X1B1cGlsLnBkZiIpCgojIEFsbCBBbnN3ZXJzOiBWb2MgU3RkLCBWb2MgU3VwLCBSZXQgU3RkLCBSZXQg"
    "U3VwLCBJbmYgU3RkLCBJbmYgU3VwCmFuc19vcmRlciA9IFtdCmZvciBpIGluIHJhbmdlKDMpOgogICAg"
    "YW5zX29yZGVyLmFwcGVuZChidWlsdFsic3RkX2FucyJdW2ldKQogICAgYW5zX29yZGVyLmFwcGVuZChi"
    "dWlsdFsic3VwX2FucyJdW2ldKQptZXJnZV9wZGZzKGFuc19vcmRlciwKICAgICAgICAgICAiL21udC91"
    "c2VyLWRhdGEvb3V0cHV0cy9UNVcyX0FsbF9BbnN3ZXJzLnBkZiIpCgojIENsZWFuIHVwIGluZGl2aWR1"
    "YWwgZmlsZXMKaW1wb3J0IHNodXRpbApzaHV0aWwucm10cmVlKE9VVF9ESVIpCgpwcmludCgiRG9uZS4i"
    "KQpwcmludCgiICBUNVcyX1N0YW5kYXJkX1B1cGlsLnBkZjoiLCBQZGZSZWFkZXIoIi9tbnQvdXNlci1k"
    "YXRhL291dHB1dHMvVDVXMl9TdGFuZGFyZF9QdXBpbC5wZGYiKS5wYWdlcy5fX2xlbl9fKCksICJwYWdl"
    "cyIpCnByaW50KCIgIFQ1VzJfU3VwcG9ydGVkX1B1cGlsLnBkZjoiLCBQZGZSZWFkZXIoIi9tbnQvdXNl"
    "ci1kYXRhL291dHB1dHMvVDVXMl9TdXBwb3J0ZWRfUHVwaWwucGRmIikucGFnZXMuX19sZW5fXygpLCAi"
    "cGFnZXMiKQpwcmludCgiICBUNVcyX0FsbF9BbnN3ZXJzLnBkZjoiLCBQZGZSZWFkZXIoIi9tbnQvdXNl"
    "ci1kYXRhL291dHB1dHMvVDVXMl9BbGxfQW5zd2Vycy5wZGYiKS5wYWdlcy5fX2xlbl9fKCksICJwYWdl"
    "cyIpCg=="
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
