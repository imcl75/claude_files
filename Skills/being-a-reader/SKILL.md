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

Matches the staff labels tool format. The label tool source at
`https://staff.wallscourt-farm-academy.co.uk/learning-labels/index.html`
is the canonical reference.

```
DD/MM/YYYY          [reader icon 7mm]
                         reader
Key Question
Are England and Brazil different?     (bold, underlined, dark blue)
LF: [learning focus]
I can [statement 1]
I can [statement 2]
─────────────────────────────────────────────────────────────────────
```

- **Date** (`DD/MM/YYYY`): top-left, 8pt plain
- **Reader icon**: top-right, 7mm × 7mm; "reader" label (6pt) centred below it
- **NO day-name text** alongside the icon — it collides with the icon and must be omitted
- **"Key Question"**: bold 8pt, on its own line below the date/icon row
- **Key question title**: bold 9.5pt, underlined, dark blue (`#2c2c6c`)
- **LF and I can lines**: plain 8pt
- **Bottom divider**: thin grey line, 0.5pt, full page width

See `draw_header()` in `build_reading_pdfs.py`.

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

The reader icon is fetched from the staff labels tool at session start. If no PPTX is available, use this fallback:

```python
import base64, os

READER_ICON_B64 = (
    "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"
)

icon_path = '/home/claude/reader_icon_saved.png'
if not os.path.exists(icon_path):
    with open(icon_path, 'wb') as f:
        f.write(base64.b64decode(READER_ICON_B64))

# Also try to extract from PPTX if available (preferred — higher resolution):
# import zipfile
# with zipfile.ZipFile('PREVIOUS_WEEK.pptx') as z:
#     with open('reader_icon_saved.png', 'wb') as f:
#         f.write(z.read('ppt/media/image2.png'))
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
    "YywgbGVzc29uX3R5cGUsIGRhdGVfc3RyLCBrZXlfcSwgbGYsIGljYW4xLCBpY2FuMik6CiAgICAiIiIK"
    "ICAgIERyYXdzIHRoZSByZWFkaW5nIExQIGxlYXJuaW5nIGxhYmVsIGhlYWRlci4KICAgIE1hdGNoZXMg"
    "dGhlIHN0YWZmIGxhYmVscyB0b29sIGZvcm1hdCBleGFjdGx5OgogICAgICAtIERhdGUgdG9wLWxlZnQg"
    "KHNtYWxsLCA4cHQpCiAgICAgIC0gUmVhZGVyIGljb24gdG9wLXJpZ2h0ICg3bW0pIHdpdGggJ3JlYWRl"
    "cicgbGFiZWwgYmVsb3cgaXQKICAgICAgLSAnS2V5IFF1ZXN0aW9uJyBib2xkIGxhYmVsIG9uIGl0cyBv"
    "d24gbGluZQogICAgICAtIEtleSBxdWVzdGlvbiBib2xkICsgdW5kZXJsaW5lZCBpbiBkYXJrIGJsdWUK"
    "ICAgICAgLSBMRiBsaW5lCiAgICAgIC0gVHdvICdJIGNhbicgbGluZXMKICAgICAgLSBHcmV5IGRpdmlk"
    "ZXIKICAgIFJldHVybnMgeSBwb3NpdGlvbiBiZWxvdyBkaXZpZGVyLgogICAgIiIiCiAgICB5ID0gSCAt"
    "IE1BUkdJTgoKICAgICMgSWNvbiBkaW1lbnNpb25zIOKAlCBtYXRjaCBsYWJlbCB0b29sICgyOHB4IOKJ"
    "iCA3bW0pCiAgICBJQ09OX1NaID0gNyAqIG1tCiAgICBpY29uX3ggPSBNQVJHSU4gKyBDVyAtIElDT05f"
    "U1oKICAgIGljb25feSA9IHkgLSBJQ09OX1NaCgogICAgIyAtLS0gRGF0ZSB0b3AtbGVmdCAtLS0KICAg"
    "IGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOCkKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAg"
    "ZGF5LCBkYXRlID0gZGF0ZV9zdHIKICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHkgLSAzLjUgKiBtbSwg"
    "ZGF0ZSkKCiAgICAjIC0tLSBSZWFkZXIgaWNvbiB0b3AtcmlnaHQgKG5vIGRheSB0ZXh0IGFsb25nc2lk"
    "ZSDigJQgYXZvaWRzIGNvbGxpc2lvbikgLS0tCiAgICB0cnk6CiAgICAgICAgYy5kcmF3SW1hZ2UoSUNP"
    "Tl9QQVRILCBpY29uX3gsIGljb25feSwKICAgICAgICAgICAgICAgICAgICB3aWR0aD1JQ09OX1NaLCBo"
    "ZWlnaHQ9SUNPTl9TWiwKICAgICAgICAgICAgICAgICAgICBtYXNrPSdhdXRvJywgcHJlc2VydmVBc3Bl"
    "Y3RSYXRpbz1UcnVlKQogICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICBwYXNzCgogICAgIyAicmVh"
    "ZGVyIiBjZW50cmVkIGJlbG93IGljb24KICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgNikKICAgIGMu"
    "c2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgYy5kcmF3Q2VudHJlZFN0cmluZyhpY29uX3ggKyBJQ09O"
    "X1NaIC8gMiwgaWNvbl95IC0gMi41ICogbW0sICJyZWFkZXIiKQoKICAgICMgTW92ZSB5IGJlbG93IGlj"
    "b24gKyAicmVhZGVyIiBsYWJlbAogICAgeSAtPSBJQ09OX1NaICsgNCAqIG1tCgogICAgIyAtLS0gIktl"
    "eSBRdWVzdGlvbiIgYm9sZCBsYWJlbCAtLS0KICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4"
    "KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0g"
    "MyAqIG1tLCAiS2V5IFF1ZXN0aW9uIikKICAgIHkgLT0gNCAqIG1tCgogICAgIyAtLS0gS2V5IHF1ZXN0"
    "aW9uIOKAlCBib2xkLCB1bmRlcmxpbmVkLCBkYXJrIGJsdWUgLS0tCiAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYS1Cb2xkIiwgOS41KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CT1JERVIpCiAgICBjLmRy"
    "YXdTdHJpbmcoTUFSR0lOLCB5IC0gMy41ICogbW0sIGtleV9xKQogICAga3FfdyA9IGMuc3RyaW5nV2lk"
    "dGgoa2V5X3EsICJIZWx2ZXRpY2EtQm9sZCIsIDkuNSkKICAgIGMuc2V0TGluZVdpZHRoKDAuNSkKICAg"
    "IGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkJPWF9CT1JERVIpCiAgICBjLmxpbmUoTUFSR0lOLCB5IC0gNC41"
    "ICogbW0sIE1BUkdJTiArIGtxX3csIHkgLSA0LjUgKiBtbSkKICAgIHkgLT0gNS41ICogbW0KCiAgICAj"
    "IC0tLSBMRiBsaW5lIC0tLQogICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA4KQogICAgYy5zZXRGaWxs"
    "Q29sb3JSR0IoKkRBUkspCiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5IC0gMyAqIG1tLCBsZikKICAg"
    "IHkgLT0gNCAqIG1tCgogICAgIyAtLS0gSSBjYW4gbGluZXMgLS0tCiAgICBjLmRyYXdTdHJpbmcoTUFS"
    "R0lOLCB5IC0gMyAqIG1tLCBpY2FuMSkKICAgIHkgLT0gNCAqIG1tCiAgICBjLmRyYXdTdHJpbmcoTUFS"
    "R0lOLCB5IC0gMyAqIG1tLCBpY2FuMikKICAgIHkgLT0gNCAqIG1tCgogICAgIyAtLS0gQm90dG9tIGdy"
    "ZXkgZGl2aWRlciAtLS0KICAgIGMuc2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgIGMuc2V0"
    "TGluZVdpZHRoKDAuNSkKICAgIGMubGluZShNQVJHSU4sIHksIE1BUkdJTiArIENXLCB5KQogICAgeSAt"
    "PSAzICogbW0KCiAgICByZXR1cm4geQoKCmRlZiB3cmFwX3RleHQoYywgdGV4dCwgZm9udCwgc2l6ZSwg"
    "bWF4X3cpOgogICAgIiIiV3JhcCB0ZXh0IHRvIGxpbmVzIGZpdHRpbmcgbWF4X3cuIFJldHVybnMgbGlz"
    "dCBvZiBsaW5lcy4iIiIKICAgIHdvcmRzID0gdGV4dC5zcGxpdCgpCiAgICBsaW5lcywgbGluZSA9IFtd"
    "LCAnJwogICAgZm9yIHcgaW4gd29yZHM6CiAgICAgICAgdGVzdCA9IChsaW5lICsgJyAnICsgdykuc3Ry"
    "aXAoKQogICAgICAgIGlmIGMuc3RyaW5nV2lkdGgodGVzdCwgZm9udCwgc2l6ZSkgPD0gbWF4X3c6CiAg"
    "ICAgICAgICAgIGxpbmUgPSB0ZXN0CiAgICAgICAgZWxzZToKICAgICAgICAgICAgaWYgbGluZToKICAg"
    "ICAgICAgICAgICAgIGxpbmVzLmFwcGVuZChsaW5lKQogICAgICAgICAgICBsaW5lID0gdwogICAgaWYg"
    "bGluZToKICAgICAgICBsaW5lcy5hcHBlbmQobGluZSkKICAgIHJldHVybiBsaW5lcyBvciBbJyddCgoK"
    "ZGVmIGRyYXdfdGV4dF9ib3goYywgdGV4dCwgeV90b3AsIGZvbnRfc2l6ZT0xMC41KToKICAgICIiIkRy"
    "YXcgdGhlIHJlYWRpbmcgdGV4dCBib3guIFJldHVybnMgeSBhZnRlciBib3guIiIiCiAgICBsaW5lcyA9"
    "IHdyYXBfdGV4dChjLCB0ZXh0LCAiSGVsdmV0aWNhIiwgZm9udF9zaXplLCBDVyAtIDYqbW0pCiAgICBs"
    "aW5lX2ggPSBmb250X3NpemUgKiAxLjQKICAgIGJveF9oID0gbGVuKGxpbmVzKSAqIGxpbmVfaCArIDUq"
    "bW0KCiAgICAjIEJveAogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkJPWF9CRykKICAgIGMuc2V0U3Ryb2tl"
    "Q29sb3JSR0IoKkJPWF9CT1JERVIpCiAgICBjLnNldExpbmVXaWR0aCgwLjgpCiAgICBjLnJvdW5kUmVj"
    "dChNQVJHSU4sIHlfdG9wIC0gYm94X2gsIENXLCBib3hfaCwgMiptbSwgZmlsbD0xLCBzdHJva2U9MSkK"
    "CiAgICAjIFRleHQKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgYy5zZXRGb250KCJIZWx2"
    "ZXRpY2EiLCBmb250X3NpemUpCiAgICB0eSA9IHlfdG9wIC0gMyptbSAtIGZvbnRfc2l6ZSAqIDAuNzIK"
    "ICAgIGZvciBsaW5lIGluIGxpbmVzOgogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAzKm1tLCB0"
    "eSwgbGluZSkKICAgICAgICB0eSAtPSBsaW5lX2gKCiAgICByZXR1cm4geV90b3AgLSBib3hfaCAtIDMq"
    "bW0KCgpkZWYgYW5zd2VyX2xpbmVzKGMsIHksIG4sIGdhcD02LjUqbW0pOgogICAgIiIiRHJhdyBuIHNv"
    "bGlkIGFuc3dlciBsaW5lcy4gUmV0dXJucyB5IGFmdGVyIGxpbmVzLiIiIgogICAgYy5zZXRTdHJva2VD"
    "b2xvclJHQigqR1JFWV9MSU5FKQogICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAgZm9yIGkgaW4gcmFu"
    "Z2Uobik6CiAgICAgICAgbHkgPSB5IC0gKGkgKyAxKSAqIGdhcAogICAgICAgIGMubGluZShNQVJHSU4s"
    "IGx5LCBNQVJHSU4gKyBDVywgbHkpCiAgICByZXR1cm4geSAtIG4gKiBnYXAgLSAyKm1tCgoKZGVmIHFf"
    "bGFiZWwoYywgcW51bSwgdGV4dCwgeSwgaXNfYW5zd2VyPUZhbHNlLCBhbnNfY29sb3VyPUZhbHNlKToK"
    "ICAgICIiIkRyYXcgcXVlc3Rpb24gbGFiZWwuIFJldHVybnMgeSBhZnRlciB0ZXh0LiIiIgogICAgY29s"
    "b3VyID0gR1JFRU4gaWYgYW5zX2NvbG91ciBlbHNlIERBUksKICAgIGMuc2V0RmlsbENvbG9yUkdCKCpj"
    "b2xvdXIpCiAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgIGxhYmVsID0gZiJ7cW51"
    "bVsxOl19LiAiCiAgICBsdyA9IGMuc3RyaW5nV2lkdGgobGFiZWwsICJIZWx2ZXRpY2EtQm9sZCIsIDkp"
    "CiAgICBjLmRyYXdTdHJpbmcoTUFSR0lOLCB5LCBsYWJlbCkKICAgIGxpbmVzID0gd3JhcF90ZXh0KGMs"
    "IHRleHQsICJIZWx2ZXRpY2EtQm9sZCIsIDksIENXIC0gbHcpCiAgICBmb3IgaSwgbGluZSBpbiBlbnVt"
    "ZXJhdGUobGluZXMpOgogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBsdywgeSAtIGkgKiAoOSAq"
    "IDEuMzUpLCBsaW5lKQogICAgcmV0dXJuIHkgLSBsZW4obGluZXMpICogKDkgKiAxLjM1KSAtIDEqbW0K"
    "CgpkZWYgZHJhd19tY19wdXBpbChjLCBvcHRpb25zLCB5KToKICAgICIiIjQtY2VsbCBNQyB0YWJsZSwg"
    "bm8gaGlnaGxpZ2h0LiIiIgogICAgY29sX3cgPSBDVyAvIDIKICAgIHJvd19oID0gNiptbQogICAgIyBU"
    "d28gcm93cyBvZiAyCiAgICBmb3Igcm93IGluIHJhbmdlKDIpOgogICAgICAgIGZvciBjb2wgaW4gcmFu"
    "Z2UoMik6CiAgICAgICAgICAgIGlkeCA9IHJvdyAqIDIgKyBjb2wKICAgICAgICAgICAgaWYgaWR4ID49"
    "IGxlbihvcHRpb25zKToKICAgICAgICAgICAgICAgIGJyZWFrCiAgICAgICAgICAgIHggPSBNQVJHSU4g"
    "KyBjb2wgKiBjb2xfdwogICAgICAgICAgICByeSA9IHkgLSByb3cgKiByb3dfaAogICAgICAgICAgICBj"
    "LnNldEZpbGxDb2xvclJHQigxLCAxLCAxKQogICAgICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAu"
    "NywgMC43LCAwLjcpCiAgICAgICAgICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICAgICAgICAgYy5y"
    "ZWN0KHgsIHJ5IC0gcm93X2gsIGNvbF93LCByb3dfaCwgZmlsbD0xLCBzdHJva2U9MSkKICAgICAgICAg"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNh"
    "IiwgOC41KQogICAgICAgICAgICBjLmRyYXdTdHJpbmcoeCArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1t"
    "LCBvcHRpb25zW2lkeF0pCiAgICByZXR1cm4geSAtIDIgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBkcmF3"
    "X21jX2Fuc3dlcihjLCBvcHRpb25zLCBjb3JyZWN0LCB5KToKICAgICIiIjQtY2VsbCBNQyB0YWJsZSwg"
    "Y29ycmVjdCBjZWxsIGhpZ2hsaWdodGVkIGdyZWVuLiIiIgogICAgY29sX3cgPSBDVyAvIDIKICAgIHJv"
    "d19oID0gNiptbQogICAgZm9yIHJvdyBpbiByYW5nZSgyKToKICAgICAgICBmb3IgY29sIGluIHJhbmdl"
    "KDIpOgogICAgICAgICAgICBpZHggPSByb3cgKiAyICsgY29sCiAgICAgICAgICAgIGlmIGlkeCA+PSBs"
    "ZW4ob3B0aW9ucyk6CiAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICB4ID0gTUFSR0lOICsg"
    "Y29sICogY29sX3cKICAgICAgICAgICAgcnkgPSB5IC0gcm93ICogcm93X2gKICAgICAgICAgICAgaXNf"
    "Y29ycmVjdCA9IG9wdGlvbnNbaWR4XSA9PSBjb3JyZWN0CiAgICAgICAgICAgIGlmIGlzX2NvcnJlY3Q6"
    "CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigwLjg1LCAwLjk1LCAwLjg1KQogICAgICAg"
    "ICAgICBlbHNlOgogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMSwgMSwgMSkKICAgICAg"
    "ICAgICAgYy5zZXRTdHJva2VDb2xvclJHQigwLjcsIDAuNywgMC43KQogICAgICAgICAgICBjLnNldExp"
    "bmVXaWR0aCgwLjQpCiAgICAgICAgICAgIGMucmVjdCh4LCByeSAtIHJvd19oLCBjb2xfdywgcm93X2gs"
    "IGZpbGw9MSwgc3Ryb2tlPTEpCiAgICAgICAgICAgIGlmIGlzX2NvcnJlY3Q6CiAgICAgICAgICAgICAg"
    "ICBjLnNldEZpbGxDb2xvclJHQigqR1JFRU4pCiAgICAgICAgICAgICAgICBjLnNldEZvbnQoIkhlbHZl"
    "dGljYS1Cb2xkIiwgOC41KQogICAgICAgICAgICAgICAgYy5kcmF3U3RyaW5nKHggKyAyKm1tLCByeSAt"
    "IHJvd19oICsgMiptbSwgb3B0aW9uc1tpZHhdICsgIiBcdTI3MTMiKQogICAgICAgICAgICBlbHNlOgog"
    "ICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgICAgICBjLnNl"
    "dEZvbnQoIkhlbHZldGljYSIsIDguNSkKICAgICAgICAgICAgICAgIGMuZHJhd1N0cmluZyh4ICsgMipt"
    "bSwgcnkgLSByb3dfaCArIDIqbW0sIG9wdGlvbnNbaWR4XSkKICAgIHJldHVybiB5IC0gMiAqIHJvd19o"
    "IC0gMS41Km1tCgoKZGVmIGRyYXdfbWF0Y2hfcHVwaWwoYywgcGFpcnMsIHkpOgogICAgIiIiTWF0Y2gg"
    "dGFibGUg4oCUIGxlZnQgd29yZHMsIGdhcCwgcmlnaHQgZGVmaW5pdGlvbnMgKHNjcmFtYmxlZCkuIiIi"
    "CiAgICBsdyA9IENXICogMC4yOAogICAgcncgPSBDVyAqIDAuNDgKICAgIGdhcCA9IENXIC0gbHcgLSBy"
    "dyAgIyAyNCUgZ2FwIGluIG1pZGRsZQogICAgcm93X2ggPSA3Km1tCiAgICBjLnNldFN0cm9rZUNvbG9y"
    "UkdCKDAuNywgMC43LCAwLjcpCiAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICAjIFNjcmFtYmxlIHJp"
    "Z2h0IGNvbHVtbgogICAgcmlnaHRzID0gW3IgZm9yIF8sIHIgaW4gcGFpcnNdCiAgICBzY3JhbWJsZWQg"
    "PSByaWdodHNbMTpdICsgcmlnaHRzWzoxXQogICAgZm9yIGksIChsZWZ0LCBfKSBpbiBlbnVtZXJhdGUo"
    "cGFpcnMpOgogICAgICAgIHJ5ID0geSAtIGkgKiByb3dfaAogICAgICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KDAuOTYsIDAuOTYsIDAuOTYpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgcnkgLSByb3dfaCwgbHcsIHJv"
    "d19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAg"
    "ICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhLUJvbGQiLCA4LjUpCiAgICAgICAgYy5kcmF3U3RyaW5nKE1B"
    "UkdJTiArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBsZWZ0KQogICAgICAgIHJ4ID0gTUFSR0lOICsg"
    "bHcgKyBnYXAKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigwLjk2LCAwLjk2LCAwLjk2KQogICAgICAg"
    "IGMucmVjdChyeCwgcnkgLSByb3dfaCwgcncsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAg"
    "IGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQogICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOC41"
    "KQogICAgICAgIGMuZHJhd1N0cmluZyhyeCArIDIqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBzY3JhbWJs"
    "ZWRbaV0pCiAgICByZXR1cm4geSAtIGxlbihwYWlycykgKiByb3dfaCAtIDEuNSptbQoKCmRlZiBkcmF3"
    "X21hdGNoX2Fuc3dlcihjLCBwYWlycywgeSk6CiAgICAiIiJNYXRjaCB0YWJsZSB3aXRoIGdyZWVuIGNv"
    "bm5lY3RvcnMuIiIiCiAgICBsdyA9IENXICogMC4yOAogICAgcncgPSBDVyAqIDAuNDgKICAgIGdhcCA9"
    "IENXIC0gbHcgLSBydwogICAgcm93X2ggPSA3Km1tCiAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNywg"
    "MC43LCAwLjcpCiAgICBjLnNldExpbmVXaWR0aCgwLjQpCiAgICBmb3IgaSwgKGxlZnQsIHJpZ2h0KSBp"
    "biBlbnVtZXJhdGUocGFpcnMpOgogICAgICAgIHJ5ID0geSAtIGkgKiByb3dfaAogICAgICAgIGMuc2V0"
    "RmlsbENvbG9yUkdCKDAuOTYsIDAuOTYsIDAuOTYpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgcnkgLSBy"
    "b3dfaCwgbHcsIHJvd19oLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOC41KQogICAgICAgIGMu"
    "ZHJhd1N0cmluZyhNQVJHSU4gKyAyKm1tLCByeSAtIHJvd19oICsgMiptbSwgbGVmdCkKICAgICAgICBy"
    "eCA9IE1BUkdJTiArIGx3ICsgZ2FwCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC44NSwgMC45NSwg"
    "MC44NSkKICAgICAgICBjLnJlY3QocngsIHJ5IC0gcm93X2gsIHJ3LCByb3dfaCwgZmlsbD0xLCBzdHJv"
    "a2U9MSkKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqR1JFRU4pCiAgICAgICAgYy5zZXRGb250KCJI"
    "ZWx2ZXRpY2EtQm9sZE9ibGlxdWUiLCA4LjUpCiAgICAgICAgYy5kcmF3U3RyaW5nKHJ4ICsgMiptbSwg"
    "cnkgLSByb3dfaCArIDIqbW0sICJcdTIwMTRcdTI1YTAgICIgKyByaWdodCkKICAgIHJldHVybiB5IC0g"
    "bGVuKHBhaXJzKSAqIHJvd19oIC0gMS41Km1tCgoKZGVmIGRyYXdfZmlsbChjLCBzZW50ZW5jZSwgeSwg"
    "aXNfYW5zd2VyPUZhbHNlLCBhbnN3ZXI9IiIpOgogICAgIiIiRHJhdyBmaWxsLWluLWJsYW5rIHNlbnRl"
    "bmNlIHdpdGggdW5kZXJsaW5lIGJsYW5rcyBvciBncmVlbiBhbnN3ZXJzLiIiIgogICAgcGFydHMgPSBz"
    "ZW50ZW5jZS5zcGxpdCgiX19fX19fX19fX19fX18iKQogICAgYmxhbmtzX25lZWRlZCA9IGxlbihwYXJ0"
    "cykgLSAxCiAgICBhbnN3ZXJzID0gW2Euc3RyaXAoKSBmb3IgYSBpbiBhbnN3ZXIuc3BsaXQoIi8iKV0g"
    "aWYgYW5zd2VyIGVsc2UgW10KICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgIGMuc2V0Rmls"
    "bENvbG9yUkdCKCpEQVJLKQogICAgeCA9IE1BUkdJTgogICAgYmxhbmtfdyA9IDI4Km1tCiAgICBmb3Ig"
    "cGksIHBhcnQgaW4gZW51bWVyYXRlKHBhcnRzKToKICAgICAgICAjIE1lYXN1cmUgYW5kIGRyYXcgdGhl"
    "IHRleHQgcGFydAogICAgICAgIHB3ID0gYy5zdHJpbmdXaWR0aChwYXJ0LCAiSGVsdmV0aWNhIiwgOSkK"
    "ICAgICAgICBjLmRyYXdTdHJpbmcoeCwgeSwgcGFydCkKICAgICAgICB4ICs9IHB3CiAgICAgICAgaWYg"
    "cGkgPCBibGFua3NfbmVlZGVkOgogICAgICAgICAgICBpZiBpc19hbnN3ZXIgYW5kIHBpIDwgbGVuKGFu"
    "c3dlcnMpOgogICAgICAgICAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoKkdSRUVOKQogICAgICAgICAg"
    "ICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICAgICAgICAgICAgICBjLmRyYXdT"
    "dHJpbmcoeCArIDEqbW0sIHksIGFuc3dlcnNbcGldKQogICAgICAgICAgICAgICAgeCArPSBibGFua193"
    "CiAgICAgICAgICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgICAgICAgICAgICAgIGMu"
    "c2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGMu"
    "c2V0U3Ryb2tlQ29sb3JSR0IoKkdSRVlfTElORSkKICAgICAgICAgICAgICAgIGMuc2V0TGluZVdpZHRo"
    "KDAuNSkKICAgICAgICAgICAgICAgIGMubGluZSh4LCB5IC0gMSptbSwgeCArIGJsYW5rX3csIHkgLSAx"
    "Km1tKQogICAgICAgICAgICAgICAgeCArPSBibGFua193CiAgICByZXR1cm4geSAtIDUuNSptbQoKCmRl"
    "ZiBkcmF3X3RpY2tfcHVwaWwoYywgb3B0aW9ucywgeSk6CiAgICAiIiJUaWNrIG9wdGlvbnMgd2l0aCBz"
    "cXVhcmUgYnVsbGV0cy4iIiIKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgIGMuc2V0Rmls"
    "bENvbG9yUkdCKCpEQVJLKQogICAgIyAyIG9yIDMgcGVyIHJvdyBkZXBlbmRpbmcgb24gY291bnQKICAg"
    "ICMgQ2hvb3NlIGNvbHVtbnMgYmFzZWQgb24gb3B0aW9uIGxlbmd0aAogICAgbWF4X2xlbiA9IG1heChs"
    "ZW4obykgZm9yIG8gaW4gb3B0aW9ucykKICAgIGlmIG1heF9sZW4gPiAyNToKICAgICAgICBwZXJfcm93"
    "ID0gMiAgIyBsb25nIG9wdGlvbnM6IDIgcGVyIHJvdwogICAgZWxpZiBsZW4ob3B0aW9ucykgPT0gNToK"
    "ICAgICAgICBwZXJfcm93ID0gNSAgIyA1IHNob3J0IG9wdGlvbnM6IGFsbCBvbiBvbmUgcm93CiAgICBl"
    "bHNlOgogICAgICAgIHBlcl9yb3cgPSA0CiAgICBjb2xfdyA9IENXIC8gcGVyX3JvdwogICAgcm93cyA9"
    "IChsZW4ob3B0aW9ucykgKyBwZXJfcm93IC0gMSkgLy8gcGVyX3JvdwogICAgcm93X2ggPSA1LjUqbW0K"
    "ICAgIGZvciBpLCBvcHQgaW4gZW51bWVyYXRlKG9wdGlvbnMpOgogICAgICAgIHJvdyA9IGkgLy8gcGVy"
    "X3JvdwogICAgICAgIGNvbCA9IGkgJSBwZXJfcm93CiAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiAr"
    "IGNvbCAqIGNvbF93LCB5IC0gcm93ICogcm93X2gsIG9wdCkKICAgIHJldHVybiB5IC0gcm93cyAqIHJv"
    "d19oIC0gMyptbQoKCmRlZiBkcmF3X3RpY2tfYW5zd2VyKGMsIG9wdGlvbnMsIGNvcnJlY3QsIHkpOgog"
    "ICAgIiIiVGljayBvcHRpb25zIHdpdGggY29ycmVjdCBvbmVzIGluIGJvbGQgZ3JlZW4uIiIiCiAgICBt"
    "YXhfbGVuID0gbWF4KGxlbihvKSBmb3IgbyBpbiBvcHRpb25zKQogICAgaWYgbWF4X2xlbiA+IDI1Ogog"
    "ICAgICAgIHBlcl9yb3cgPSAyCiAgICBlbGlmIGxlbihvcHRpb25zKSA9PSA1OgogICAgICAgIHBlcl9y"
    "b3cgPSA1CiAgICBlbHNlOgogICAgICAgIHBlcl9yb3cgPSA0CiAgICBjb2xfdyA9IENXIC8gcGVyX3Jv"
    "dwogICAgcm93cyA9IChsZW4ob3B0aW9ucykgKyBwZXJfcm93IC0gMSkgLy8gcGVyX3JvdwogICAgcm93"
    "X2ggPSA1LjUqbW0KICAgIGZvciBpLCBvcHQgaW4gZW51bWVyYXRlKG9wdGlvbnMpOgogICAgICAgIHJv"
    "dyA9IGkgLy8gcGVyX3JvdwogICAgICAgIGNvbCA9IGkgJSBwZXJfcm93CiAgICAgICAgaWYgb3B0IGlu"
    "IGNvcnJlY3Q6CiAgICAgICAgICAgIGMuc2V0RmlsbENvbG9yUkdCKCpHUkVFTikKICAgICAgICAgICAg"
    "Yy5zZXRGb250KCJIZWx2ZXRpY2EtQm9sZCIsIDkpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgYy5z"
    "ZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkK"
    "ICAgICAgICBjLmRyYXdTdHJpbmcoTUFSR0lOICsgY29sICogY29sX3csIHkgLSByb3cgKiByb3dfaCwg"
    "b3B0KQogICAgcmV0dXJuIHkgLSByb3dzICogcm93X2ggLSAzKm1tCgoKZGVmIGRyYXdfb3JkZXJfcHVw"
    "aWwoYywgZXZlbnRzLCB5KToKICAgICIiIk51bWJlcmVkIG9yZGVyaW5nIHF1ZXN0aW9uLiIiIgogICAg"
    "Yy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5KQogICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICBy"
    "b3dfaCA9IDUuNSptbQogICAgZm9yIGksIGV2IGluIGVudW1lcmF0ZShldmVudHMpOgogICAgICAgIHJ5"
    "ID0geSAtIGkgKiByb3dfaAogICAgICAgIGMuc2V0TGluZVdpZHRoKDAuNCkKICAgICAgICBjLnNldFN0"
    "cm9rZUNvbG9yUkdCKDAuNywgMC43LCAwLjcpCiAgICAgICAgYy5yZWN0KE1BUkdJTiwgcnkgLSByb3df"
    "aCArIDEqbW0sIDgqbW0sIDQqbW0sIGZpbGw9MCwgc3Ryb2tlPTEpCiAgICAgICAgYy5kcmF3U3RyaW5n"
    "KE1BUkdJTiArIDEwKm1tLCByeSAtIHJvd19oICsgMiptbSwgZXYpCiAgICByZXR1cm4geSAtIGxlbihl"
    "dmVudHMpICogcm93X2ggLSAxLjUqbW0KCgpkZWYgZHJhd19vcmRlcl9hbnN3ZXIoYywgZXZlbnRzLCBj"
    "b3JyZWN0X29yZGVyLCB5KToKICAgICIiIk51bWJlcmVkIG9yZGVyaW5nIHF1ZXN0aW9uIHdpdGggYW5z"
    "d2Vycy4iIiIKICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgIHJvd19oID0gNS41Km1tCiAg"
    "ICBmb3IgaSwgKGV2LCBudW0pIGluIGVudW1lcmF0ZSh6aXAoZXZlbnRzLCBjb3JyZWN0X29yZGVyKSk6"
    "CiAgICAgICAgcnkgPSB5IC0gaSAqIHJvd19oCiAgICAgICAgYy5zZXRGaWxsQ29sb3JSR0IoMC44NSwg"
    "MC45NSwgMC44NSkKICAgICAgICBjLnNldFN0cm9rZUNvbG9yUkdCKDAuNywgMC43LCAwLjcpCiAgICAg"
    "ICAgYy5zZXRMaW5lV2lkdGgoMC40KQogICAgICAgIGMucmVjdChNQVJHSU4sIHJ5IC0gcm93X2ggKyAx"
    "Km1tLCA4Km1tLCA0Km1tLCBmaWxsPTEsIHN0cm9rZT0xKQogICAgICAgIGMuc2V0RmlsbENvbG9yUkdC"
    "KCpHUkVFTikKICAgICAgICBjLnNldEZvbnQoIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgICAgICBjLmRy"
    "YXdDZW50cmVkU3RyaW5nKE1BUkdJTiArIDQqbW0sIHJ5IC0gcm93X2ggKyAyKm1tLCBudW0pCiAgICAg"
    "ICAgYy5zZXRGaWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgYy5zZXRGb250KCJIZWx2ZXRpY2EiLCA5"
    "KQogICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyAxMCptbSwgcnkgLSByb3dfaCArIDIqbW0sIGV2"
    "KQogICAgcmV0dXJuIHkgLSBsZW4oZXZlbnRzKSAqIHJvd19oIC0gMS41Km1tCgoKZGVmIGRyYXdfd3Jp"
    "dHRlbl9hbnN3ZXIoYywgYW5zd2VyLCB5LCBuX2xpbmVzPTMpOgogICAgIiIiV3JpdHRlbiBhbnN3ZXI6"
    "IGFuc3dlciBsaW5lcyAocHVwaWwpIG9yIGdyZWVuIGl0YWxpYyB0ZXh0IChhbnN3ZXJzKS4iIiIKICAg"
    "IGlmIGFuc3dlcjoKICAgICAgICBjLnNldEZpbGxDb2xvclJHQigqR1JFRU4pCiAgICAgICAgYy5zZXRG"
    "b250KCJIZWx2ZXRpY2EtT2JsaXF1ZSIsIDguNSkKICAgICAgICBsaW5lcyA9IHdyYXBfdGV4dChjLCBh"
    "bnN3ZXIsICJIZWx2ZXRpY2EtT2JsaXF1ZSIsIDguNSwgQ1cpCiAgICAgICAgZm9yIGksIGxpbmUgaW4g"
    "ZW51bWVyYXRlKGxpbmVzKToKICAgICAgICAgICAgYy5kcmF3U3RyaW5nKE1BUkdJTiwgeSAtIChpICsg"
    "MSkgKiA1Km1tLCBsaW5lKQogICAgICAgIHJldHVybiB5IC0gbGVuKGxpbmVzKSAqIDUqbW0gLSA0Km1t"
    "CiAgICBlbHNlOgogICAgICAgIHJldHVybiBhbnN3ZXJfbGluZXMoYywgeSwgbl9saW5lcykKCgpkZWYg"
    "cmVuZGVyX3F1ZXN0aW9uKGMsIHEsIHksIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5lcz0zLCBtaW5feT0y"
    "MCptbSk6CiAgICAiIiJSZW5kZXIgYSBzaW5nbGUgcXVlc3Rpb24uIFJldHVybnMgbmV3IHksIG9yIE5v"
    "bmUgaWYgbm8gcm9vbS4iIiIKICAgIHFudW0sIHF0eXBlLCBxdGV4dCwgb3B0aW9ucywgY29ycmVjdCA9"
    "IHEKCiAgICAjIEVzdGltYXRlIGhlaWdodAogICAgbGFiZWxfaCA9IGxlbih3cmFwX3RleHQoYywgcXRl"
    "eHQuc3BsaXQoJ1xuJylbMF0sICJIZWx2ZXRpY2EtQm9sZCIsIDksIENXIC0gOCptbSkpICogMTIgKyA0"
    "CiAgICBleHRyYSA9IDAKICAgIGlmIHF0eXBlID09ICJtYyI6ICAgICAgICAgICAgIGV4dHJhID0gMTQq"
    "bW0KICAgIGVsaWYgcXR5cGUgPT0gIm1hdGNoIjogICAgICAgIGV4dHJhID0gbGVuKG9wdGlvbnMpICog"
    "NyptbQogICAgZWxpZiBxdHlwZSBpbiAoInRpY2syIiwidGljazMiKTogZXh0cmEgPSAobGVuKG9wdGlv"
    "bnMpIC8vIDMgKyAxKSAqIDYqbW0KICAgIGVsaWYgcXR5cGUgPT0gImZpbGwiOiAgICAgICAgIGV4dHJh"
    "ID0gNiptbQogICAgZWxpZiBxdHlwZSA9PSAib3JkZXIiOiAgICAgICAgZXh0cmEgPSBsZW4ob3B0aW9u"
    "cykgKiA2Km1tCiAgICBlbGlmIHF0eXBlID09ICJ3cml0dGVuIjogICAgICBleHRyYSA9IG5fbGluZXMg"
    "KiA1LjUqbW0KICAgIHRvdGFsX2VzdCA9IGxhYmVsX2ggKyBleHRyYSArIDMqbW0KCiAgICBpZiB5IC0g"
    "dG90YWxfZXN0IDwgbWluX3k6CiAgICAgICAgcmV0dXJuIE5vbmUgICMgbm8gcm9vbQoKICAgICMgRHJh"
    "dyBxdWVzdGlvbiB0ZXh0CiAgICBjLnNldEZpbGxDb2xvclJHQigqREFSSykKICAgIGMuc2V0Rm9udCgi"
    "SGVsdmV0aWNhLUJvbGQiLCA5KQogICAgbGFiZWwgPSBmIntxbnVtWzE6XX0uICIKICAgIGx3ID0gYy5z"
    "dHJpbmdXaWR0aChsYWJlbCwgIkhlbHZldGljYS1Cb2xkIiwgOSkKICAgIGMuZHJhd1N0cmluZyhNQVJH"
    "SU4sIHksIGxhYmVsKQogICAgcV9saW5lc19hbGwgPSBxdGV4dC5zcGxpdCgnXG4nKQogICAgIyBGb3Ig"
    "ZmlsbC1pbi1ibGFuayB3aXRoIGEgc2VwYXJhdGUgc2VudGVuY2UgbGluZSwgb25seSBzaG93IHRoZSBw"
    "cm9tcHQgYXMgdGhlIGxhYmVsCiAgICBsYWJlbF9saW5lc190ZXh0ID0gcV9saW5lc19hbGxbMF0KICAg"
    "IGZpcnN0X2xpbmVzID0gd3JhcF90ZXh0KGMsIGxhYmVsX2xpbmVzX3RleHQsICJIZWx2ZXRpY2EtQm9s"
    "ZCIsIDksIENXIC0gbHcpCiAgICBmb3IgaSwgbGluZSBpbiBlbnVtZXJhdGUoZmlyc3RfbGluZXMpOgog"
    "ICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4gKyBsdywgeSAtIGkgKiAoOSAqIDEuMzUpLCBsaW5lKQog"
    "ICAgeSAtPSBsZW4oZmlyc3RfbGluZXMpICogKDkgKiAxLjM1KQogICAgIyBGb3Igbm9uLWZpbGwgdHlw"
    "ZXMgd2l0aCBhZGRpdGlvbmFsIGxpbmVzIChub3QgdXNlZCBjdXJyZW50bHkpLCBkcmF3IHRoZW0KICAg"
    "IGlmIHF0eXBlICE9ICJmaWxsIjoKICAgICAgICBmb3IgZXh0cmFfbGluZSBpbiBxX2xpbmVzX2FsbFsx"
    "Ol06CiAgICAgICAgICAgIGMuc2V0Rm9udCgiSGVsdmV0aWNhIiwgOSkKICAgICAgICAgICAgYy5zZXRG"
    "aWxsQ29sb3JSR0IoKkRBUkspCiAgICAgICAgICAgIGMuZHJhd1N0cmluZyhNQVJHSU4sIHksIGV4dHJh"
    "X2xpbmUpCiAgICAgICAgICAgIHkgLT0gOSAqIDEuMzUKICAgIHkgLT0gMSptbQoKICAgIGlmIHF0eXBl"
    "ID09ICJtYyI6CiAgICAgICAgaWYgaXNfYW5zd2VyOgogICAgICAgICAgICB5ID0gZHJhd19tY19hbnN3"
    "ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSkKICAgICAgICBlbHNlOgogICAgICAgICAgICB5ID0gZHJh"
    "d19tY19wdXBpbChjLCBvcHRpb25zLCB5KQogICAgICAgIHkgLT0gMSptbSAgIyBleHRyYSBnYXAgYWZ0"
    "ZXIgTUMgdGFibGUKCiAgICBlbGlmIHF0eXBlID09ICJtYXRjaCI6CiAgICAgICAgaWYgaXNfYW5zd2Vy"
    "OgogICAgICAgICAgICB5ID0gZHJhd19tYXRjaF9hbnN3ZXIoYywgb3B0aW9ucywgeSkKICAgICAgICBl"
    "bHNlOgogICAgICAgICAgICB5ID0gZHJhd19tYXRjaF9wdXBpbChjLCBvcHRpb25zLCB5KQogICAgICAg"
    "IHkgLT0gMSptbSAgIyBleHRyYSBnYXAgYWZ0ZXIgbWF0Y2ggdGFibGUKCiAgICBlbGlmIHF0eXBlIGlu"
    "ICgidGljazIiLCAidGljazMiKToKICAgICAgICBpZiBpc19hbnN3ZXI6CiAgICAgICAgICAgIHkgPSBk"
    "cmF3X3RpY2tfYW5zd2VyKGMsIG9wdGlvbnMsIGNvcnJlY3QsIHkpCiAgICAgICAgZWxzZToKICAgICAg"
    "ICAgICAgeSA9IGRyYXdfdGlja19wdXBpbChjLCBvcHRpb25zLCB5KQoKICAgIGVsaWYgcXR5cGUgPT0g"
    "ImZpbGwiOgogICAgICAgICMgVGhlIGZpbGwgc2VudGVuY2UgaXMgdGhlIGxhc3QgZWxlbWVudCBvZiBx"
    "X2xpbmVzX2FsbCAob3IgcXRleHQgaWYgbm8gXG4pCiAgICAgICAgZmlsbF9zZW50ZW5jZSA9IHFfbGlu"
    "ZXNfYWxsWy0xXSBpZiBsZW4ocV9saW5lc19hbGwpID4gMSBlbHNlIHF0ZXh0CiAgICAgICAgeSA9IGRy"
    "YXdfZmlsbChjLCBmaWxsX3NlbnRlbmNlLCB5LCBpc19hbnN3ZXI9aXNfYW5zd2VyLCBhbnN3ZXI9Y29y"
    "cmVjdCBvciAiIikKCiAgICBlbGlmIHF0eXBlID09ICJvcmRlciI6CiAgICAgICAgaWYgaXNfYW5zd2Vy"
    "OgogICAgICAgICAgICB5ID0gZHJhd19vcmRlcl9hbnN3ZXIoYywgb3B0aW9ucywgY29ycmVjdCwgeSkK"
    "ICAgICAgICBlbHNlOgogICAgICAgICAgICB5ID0gZHJhd19vcmRlcl9wdXBpbChjLCBvcHRpb25zLCB5"
    "KQoKICAgIGVsaWYgcXR5cGUgPT0gIndyaXR0ZW4iOgogICAgICAgIHkgPSBkcmF3X3dyaXR0ZW5fYW5z"
    "d2VyKGMsIGNvcnJlY3QgaWYgaXNfYW5zd2VyIGVsc2UgTm9uZSwgeSwgbl9saW5lcz1uX2xpbmVzKQoK"
    "ICAgIHJldHVybiB5IC0gMyptbQoKCmRlZiBidWlsZF9wYWdlKHBhdGgsIGxlc3Nvbl90eXBlLCB0ZXh0"
    "LCBxdWVzdGlvbnMsIGRhdGVfc3RyLCBpc19hbnN3ZXIsIG5fbGluZXMpOgogICAgIiIiQnVpbGQgYSBz"
    "aW5nbGUtcGFnZSBQREYuIiIiCiAgICBjID0gY2FudmFzLkNhbnZhcyhwYXRoLCBwYWdlc2l6ZT1BNCkK"
    "ICAgIGMuc2V0RmlsbENvbG9yUkdCKCpEQVJLKQoKICAgIHkgPSBkcmF3X2hlYWRlcihjLCBsZXNzb25f"
    "dHlwZSwgZGF0ZV9zdHIsIEtFWV9RLAogICAgICAgICAgICAgICAgICAgIExGW2xlc3Nvbl90eXBlXSwg"
    "SUNBTltsZXNzb25fdHlwZV1bMF0sIElDQU5bbGVzc29uX3R5cGVdWzFdKQoKICAgIHkgPSBkcmF3X3Rl"
    "eHRfYm94KGMsIHRleHQsIHkpCgogICAgbWluX3kgPSAxMiptbQogICAgZm9yIHEgaW4gcXVlc3Rpb25z"
    "OgogICAgICAgIHJlc3VsdCA9IHJlbmRlcl9xdWVzdGlvbihjLCBxLCB5LCBpc19hbnN3ZXI9aXNfYW5z"
    "d2VyLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBuX2xpbmVzPW5fbGluZXMsIG1pbl95"
    "PW1pbl95KQogICAgICAgIGlmIHJlc3VsdCBpcyBOb25lOgogICAgICAgICAgICAjIERyb3AgUTcgaWYg"
    "bm8gcm9vbSAobGFzdCBxdWVzdGlvbiBpbiBsaXN0KQogICAgICAgICAgICBicmVhawogICAgICAgIHkg"
    "PSByZXN1bHQKCiAgICBjLnNhdmUoKQogICAgcmV0dXJuIHBhdGgKCgpkZWYgY2hlY2tfcGFnZV9jb3Vu"
    "dChwYXRoKToKICAgIHJlYWRlciA9IFBkZlJlYWRlcihwYXRoKQogICAgcmV0dXJuIGxlbihyZWFkZXIu"
    "cGFnZXMpCgoKZGVmIG1lcmdlX3BkZnMoZmlsZV9saXN0LCBvdXRwdXRfcGF0aCk6CiAgICB3cml0ZXIg"
    "PSBQZGZXcml0ZXIoKQogICAgZm9yIGYgaW4gZmlsZV9saXN0OgogICAgICAgIGZvciBwYWdlIGluIFBk"
    "ZlJlYWRlcihmKS5wYWdlczoKICAgICAgICAgICAgd3JpdGVyLmFkZF9wYWdlKHBhZ2UpCiAgICB3aXRo"
    "IG9wZW4ob3V0cHV0X3BhdGgsICJ3YiIpIGFzIGZoOgogICAgICAgIHdyaXRlci53cml0ZShmaCkKCgoj"
    "IOKUgOKUgCBCdWlsZCBhbGwgMTIgaW5kaXZpZHVhbCBQREZzIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKU"
    "gOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAoKbGVzc29u"
    "cyA9IFsKICAgICgiVm9jYWJ1bGFyeSIsIFNURF9WT0MsIFNVUF9WT0MsIFNURF9WT0NfUVMsIFNVUF9W"
    "T0NfUVMsIERBVEVTWyJWb2NhYnVsYXJ5Il0pLAogICAgKCJSZXRyaWV2YWwiLCAgU1REX1JFVCwgU1VQ"
    "X1JFVCwgU1REX1JFVF9RUywgU1VQX1JFVF9RUywgREFURVNbIlJldHJpZXZhbCJdKSwKICAgICgiSW5m"
    "ZXJlbmNlIiwgIFNURF9JTkYsIFNVUF9JTkYsIFNURF9JTkZfUVMsIFNVUF9JTkZfUVMsIERBVEVTWyJJ"
    "bmZlcmVuY2UiXSksCl0KCmJ1aWx0ID0gewogICAgInN0ZF9wdXBpbCI6IFtdLCAic3VwX3B1cGlsIjog"
    "W10sCiAgICAic3RkX2FucyI6IFtdLCAic3VwX2FucyI6IFtdLAp9Cgpmb3IgbGVzc29uX3R5cGUsIHN0"
    "ZF90ZXh0LCBzdXBfdGV4dCwgc3RkX3FzLCBzdXBfcXMsIGRhdGVfc3RyIGluIGxlc3NvbnM6CiAgICBs"
    "dCA9IGxlc3Nvbl90eXBlCiAgICBwcmludChmIkJ1aWxkaW5nIHtsdH0uLi4iKQoKICAgICMgU3RhbmRh"
    "cmQgcHVwaWwKICAgIHAgPSBmIntPVVRfRElSfS97bHR9X1N0YW5kYXJkX1B1cGlsLnBkZiIKICAgIGJ1"
    "aWxkX3BhZ2UocCwgbHQsIHN0ZF90ZXh0LCBzdGRfcXMsIGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2Us"
    "IG5fbGluZXM9MykKICAgIHBhZ2VzID0gY2hlY2tfcGFnZV9jb3VudChwKQogICAgaWYgcGFnZXMgPiAx"
    "OgogICAgICAgIHByaW50KGYiICBXQVJOSU5HOiB7bHR9IFN0YW5kYXJkIG92ZXJmbG93cyAoe3BhZ2Vz"
    "fSBwYWdlcykg4oCUIGRyb3BwaW5nIFE3IikKICAgICAgICBidWlsZF9wYWdlKHAsIGx0LCBzdGRfdGV4"
    "dCwgc3RkX3FzWzotMV0sIGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9MykKICAgIHBy"
    "aW50KGYiICBTdGFuZGFyZCBQdXBpbDoge2NoZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAg"
    "YnVpbHRbInN0ZF9wdXBpbCJdLmFwcGVuZChwKQoKICAgICMgU3VwcG9ydGVkIHB1cGlsCiAgICBwID0g"
    "ZiJ7T1VUX0RJUn0ve2x0fV9TdXBwb3J0ZWRfUHVwaWwucGRmIgogICAgYnVpbGRfcGFnZShwLCBsdCwg"
    "c3VwX3RleHQsIHN1cF9xcywgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1GYWxzZSwgbl9saW5lcz0yKQogICAg"
    "cGFnZXMgPSBjaGVja19wYWdlX2NvdW50KHApCiAgICBpZiBwYWdlcyA+IDE6CiAgICAgICAgcHJpbnQo"
    "ZiIgIFdBUk5JTkc6IHtsdH0gU3VwcG9ydGVkIG92ZXJmbG93cyAoe3BhZ2VzfSBwYWdlcykg4oCUIGRy"
    "b3BwaW5nIFE1IikKICAgICAgICBidWlsZF9wYWdlKHAsIGx0LCBzdXBfdGV4dCwgc3VwX3FzWzotMV0s"
    "IGRhdGVfc3RyLCBpc19hbnN3ZXI9RmFsc2UsIG5fbGluZXM9MikKICAgIHByaW50KGYiICBTdXBwb3J0"
    "ZWQgUHVwaWw6IHtjaGVja19wYWdlX2NvdW50KHApfSBwYWdlKHMpIikKICAgIGJ1aWx0WyJzdXBfcHVw"
    "aWwiXS5hcHBlbmQocCkKCiAgICAjIFN0YW5kYXJkIGFuc3dlcnMKICAgIHAgPSBmIntPVVRfRElSfS97"
    "bHR9X1N0YW5kYXJkX0Fuc3dlcnMucGRmIgogICAgYnVpbGRfcGFnZShwLCBsdCwgc3RkX3RleHQsIHN0"
    "ZF9xcywgZGF0ZV9zdHIsIGlzX2Fuc3dlcj1UcnVlLCBuX2xpbmVzPTMpCiAgICBwcmludChmIiAgU3Rh"
    "bmRhcmQgQW5zd2Vyczoge2NoZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAgYnVpbHRbInN0"
    "ZF9hbnMiXS5hcHBlbmQocCkKCiAgICAjIFN1cHBvcnRlZCBhbnN3ZXJzCiAgICBwID0gZiJ7T1VUX0RJ"
    "Un0ve2x0fV9TdXBwb3J0ZWRfQW5zd2Vycy5wZGYiCiAgICBidWlsZF9wYWdlKHAsIGx0LCBzdXBfdGV4"
    "dCwgc3VwX3FzLCBkYXRlX3N0ciwgaXNfYW5zd2VyPVRydWUsIG5fbGluZXM9MikKICAgIHByaW50KGYi"
    "ICBTdXBwb3J0ZWQgQW5zd2Vyczoge2NoZWNrX3BhZ2VfY291bnQocCl9IHBhZ2UocykiKQogICAgYnVp"
    "bHRbInN1cF9hbnMiXS5hcHBlbmQocCkKCnByaW50KCJcbk1lcmdpbmcuLi4iKQoKIyBTdGFuZGFyZCBQ"
    "dXBpbDogVm9jICsgUmV0ICsgSW5mCm1lcmdlX3BkZnMoYnVpbHRbInN0ZF9wdXBpbCJdLAogICAgICAg"
    "ICAgICIvbW50L3VzZXItZGF0YS9vdXRwdXRzL1Q1VzJfU3RhbmRhcmRfUHVwaWwucGRmIikKCiMgU3Vw"
    "cG9ydGVkIFB1cGlsOiBWb2MgKyBSZXQgKyBJbmYKbWVyZ2VfcGRmcyhidWlsdFsic3VwX3B1cGlsIl0s"
    "CiAgICAgICAgICAgIi9tbnQvdXNlci1kYXRhL291dHB1dHMvVDVXMl9TdXBwb3J0ZWRfUHVwaWwucGRm"
    "IikKCiMgQWxsIEFuc3dlcnM6IFZvYyBTdGQsIFZvYyBTdXAsIFJldCBTdGQsIFJldCBTdXAsIEluZiBT"
    "dGQsIEluZiBTdXAKYW5zX29yZGVyID0gW10KZm9yIGkgaW4gcmFuZ2UoMyk6CiAgICBhbnNfb3JkZXIu"
    "YXBwZW5kKGJ1aWx0WyJzdGRfYW5zIl1baV0pCiAgICBhbnNfb3JkZXIuYXBwZW5kKGJ1aWx0WyJzdXBf"
    "YW5zIl1baV0pCm1lcmdlX3BkZnMoYW5zX29yZGVyLAogICAgICAgICAgICIvbW50L3VzZXItZGF0YS9v"
    "dXRwdXRzL1Q1VzJfQWxsX0Fuc3dlcnMucGRmIikKCiMgQ2xlYW4gdXAgaW5kaXZpZHVhbCBmaWxlcwpp"
    "bXBvcnQgc2h1dGlsCnNodXRpbC5ybXRyZWUoT1VUX0RJUikKCnByaW50KCJEb25lLiIpCnByaW50KCIg"
    "IFQ1VzJfU3RhbmRhcmRfUHVwaWwucGRmOiIsIFBkZlJlYWRlcigiL21udC91c2VyLWRhdGEvb3V0cHV0"
    "cy9UNVcyX1N0YW5kYXJkX1B1cGlsLnBkZiIpLnBhZ2VzLl9fbGVuX18oKSwgInBhZ2VzIikKcHJpbnQo"
    "IiAgVDVXMl9TdXBwb3J0ZWRfUHVwaWwucGRmOiIsIFBkZlJlYWRlcigiL21udC91c2VyLWRhdGEvb3V0"
    "cHV0cy9UNVcyX1N1cHBvcnRlZF9QdXBpbC5wZGYiKS5wYWdlcy5fX2xlbl9fKCksICJwYWdlcyIpCnBy"
    "aW50KCIgIFQ1VzJfQWxsX0Fuc3dlcnMucGRmOiIsIFBkZlJlYWRlcigiL21udC91c2VyLWRhdGEvb3V0"
    "cHV0cy9UNVcyX0FsbF9BbnN3ZXJzLnBkZiIpLnBhZ2VzLl9fbGVuX18oKSwgInBhZ2VzIikK"
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
