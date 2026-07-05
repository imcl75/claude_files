---
name: enquiry-lp
description: >
  Create enquiry-based learning papers (LPs) as ReportLab PDFs for any subject
  across any year group. Covers Geography, History, Science and Computing as
  primary subjects; Music, Art, Citizenship and DT in scope. Always produces
  both standard and adapted versions automatically. Adapted LPs differ in HOW
  the child responds and the scaffolding provided — not just in content
  difficulty. Use this skill whenever Innes asks for an enquiry LP, a subject
  learning paper, a worksheet for history/geography/science/computing, or any
  standalone pupil task sheet for an enquiry subject.
---

# Enquiry LP Skill

Produces two-page A4 ReportLab PDFs (pupil sheet + marking station) for enquiry
subjects. Standard and adapted versions are always built together. This skill
does NOT cover maths LPs — those use the maths-complete-planning-and-resources
skill with its own builder.

---

## Session Start Checklist

Run these steps in order before writing any LP content.

**Step 1 — Read the ReportLab rules skill**
```
view /mnt/skills/user/reportlab-pdf-creation/SKILL.md
```
Non-negotiable. All coordinate and layout rules live there.

**Step 2 — Install dependencies**
```bash
pip install reportlab pymupdf --break-system-packages -q
```

**Step 3 — Fetch the reference builder**
The file `build_l456_lps_v2.py` is in the GitHub repo under `Geography/`.
Use the github-sync skill fetch pattern if not present at `/home/claude/build_l456_lps_v2.py`.
All helper functions in this skill are extracted from that file verbatim.

**Step 4 — CLF prior learning check**
Search the CLF Curriculum Progression document at
`/mnt/project/CLF_Curriculum_Progression_Summary_v3_3.pdf` for the subject
and year group before designing any LP content. Extract:
- What prior learning the pupils have had
- Any cross-curricular links relevant to the lesson
- The vocabulary progression expected at this stage
State what you found before proposing LP content. Never skip this check.

**Step 5 — Confirm with Innes**
Before building, confirm: subject, year group, lesson number within the
enquiry sequence, key question, learning focus, I can statements, date, and
whether a Higgsfield image is wanted. If the LP must align to a teaching
deck, ask for the You Do slide content so Part B matches exactly.

---

## Year Group Colours

Use the correct WFA year group colour throughout (label bar, section heads,
table headers, word bank borders).

| Year | Colour hex | RGB tuple |
|------|-----------|-----------|
| Y1   | `#e57d24` | `(0xe5/255, 0x7d/255, 0x24/255)` |
| Y2   | `#2bae62` | `(0x2b/255, 0xae/255, 0x62/255)` |
| Y3   | `#c0157b` | `(0xc0/255, 0x15/255, 0x7b/255)` |
| Y4   | `#1798d3` | `(0x17/255, 0x98/255, 0xd3/255)` |
| Y5   | `#e57d24` | `(0xe5/255, 0x7d/255, 0x24/255)` |
| Y6   | `#2bae62` | `(0x2b/255, 0xae/255, 0x62/255)` |

Assign the colour to `THEME` and use it wherever `BLUE` / `ORANGE` appear in
the helpers below. The word bank accent colour is always one stop warmer:
use ORANGE for a blue-themed LP, BLUE for an orange-themed one. For Y6
green-themed LPs use ORANGE as the accent.

---

## Page Constants

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

W, H = A4          # 595.28 x 841.89 pt
M    = 35          # margin (all sides)
CW   = W - 2*M    # 525.28 pt content width
```

---

## Helper Functions (verbatim — do not modify geometry)

These are extracted from `build_l456_lps_v2.py` and have been verified.
Copy them exactly into every LP builder script.

```python
DARK  = (0.10, 0.10, 0.10)
GREY  = (0.45, 0.45, 0.45)
LGREY = (0.80, 0.80, 0.80)
CREAM = (0.996, 0.976, 0.910)
GREEN = (0x27/255, 0xae/255, 0x60/255)  # marking station only

def sf(c, rgb): c.setFillColorRGB(*rgb)
def ss(c, rgb): c.setStrokeColorRGB(*rgb)


def learning_label(c, key_q, date, lf, icans, theme):
    """
    WFA learning label — white background throughout.
    theme: RGB tuple for the year group colour.
    Returns y position where content starts.
    """
    y = H - M

    # Line 1: "Key Question" label + date
    sf(c, theme); c.setFont('Helvetica-Bold', 8)
    c.drawString(M, y - 8, 'Key Question')
    sf(c, GREY); c.setFont('Helvetica', 8)
    c.drawRightString(W - M, y - 8, date)

    # Line 2: key question text
    y -= 22
    sf(c, DARK); c.setFont('Helvetica-Bold', 10)
    c.drawString(M, y - 7, key_q)

    # Thin theme underline
    y -= 18
    ss(c, theme); c.setLineWidth(0.75)
    c.line(M, y, W - M, y)
    y -= 12

    # LF line
    sf(c, theme); c.setFont('Helvetica-Bold', 8)
    c.drawString(M, y - 6, f'LF: {lf}')
    y -= 14

    # I can statements
    sf(c, DARK); c.setFont('Helvetica', 8)
    for ican in icans:
        c.drawString(M + 4, y - 6, f'\u2022 {ican}')
        y -= 12

    # Separator
    y -= 6
    ss(c, theme); c.setLineWidth(1.2)
    c.line(M, y, W - M, y)

    return y - 14


def section_head(c, text, y_top, colour):
    sf(c, colour); c.setFont('Helvetica-Bold', 12)
    c.drawString(M, y_top - 10, text)
    y = y_top - 22
    ss(c, colour); c.setLineWidth(1.0)
    c.line(M, y, W - M, y)
    return y - 10


def body(c, text, y_top, sz=9, colour=None, indent=0):
    if colour is None: colour = DARK
    sf(c, colour); c.setFont('Helvetica', sz)
    c.drawString(M + indent, y_top - sz * 0.72 - 2, text)
    return y_top - sz - 6


def body_bold(c, text, y_top, sz=9, colour=None, indent=0):
    if colour is None: colour = DARK
    sf(c, colour); c.setFont('Helvetica-Bold', sz)
    c.drawString(M + indent, y_top - sz * 0.72 - 2, text)
    return y_top - sz - 6


def writing_line(c, y_top, x=None, w=None, theme=None):
    """Single writing line. Returns next y_top."""
    if x is None: x = M
    if w is None: w = CW
    if theme is None: theme = (0.65, 0.80, 0.88)
    ss(c, theme); c.setLineWidth(0.6)
    c.line(x, y_top - 16, x + w, y_top - 16)
    return y_top - 22


def ans_box(c, y_top, box_w=120, row_h=22):
    """Right-aligned answer box. Returns x position of box."""
    x = M + CW - box_w
    y_bot = y_top - row_h
    ss(c, LGREY); sf(c, (1, 1, 1)); c.setLineWidth(0.5)
    c.rect(x, y_bot, box_w, row_h, fill=1, stroke=1)
    return x


ROW_H = 22

def table_header(c, cols, y_top, theme):
    """cols = [(label, width_pt), ...]. Returns y below header."""
    sf(c, theme); ss(c, theme); c.setLineWidth(0.3)
    c.rect(M, y_top - ROW_H, CW, ROW_H, fill=1, stroke=0)
    sf(c, (1, 1, 1)); c.setFont('Helvetica-Bold', 8)
    x = M
    for label, w in cols:
        c.drawString(x + 4, y_top - ROW_H + 7, label)
        x += w
    return y_top - ROW_H


def table_row(c, items, col_widths, y_top, shade=False):
    """Returns y below row."""
    if shade:
        sf(c, (0.96, 0.96, 0.96))
        c.rect(M, y_top - ROW_H, CW, ROW_H, fill=1, stroke=0)
    ss(c, LGREY); c.setLineWidth(0.3)
    c.rect(M, y_top - ROW_H, CW, ROW_H, fill=0, stroke=1)
    sf(c, DARK); c.setFont('Helvetica', 8)
    x = M
    for item, w in zip(items, col_widths):
        c.drawString(x + 4, y_top - ROW_H + 7, item)
        if x + w < M + CW:
            ss(c, LGREY); c.setLineWidth(0.3)
            c.line(x + w, y_top - ROW_H, x + w, y_top)
        x += w
    return y_top - ROW_H


WB_H = 38

def word_bank(c, words, y_top, theme, label='Word bank'):
    """Cream-filled word bank. Returns y below."""
    ACCENT = (0.9, 0.5, 0.1)   # default warm accent
    sf(c, CREAM); ss(c, theme); c.setLineWidth(1.2)
    c.roundRect(M, y_top - WB_H, CW, WB_H, 5, fill=1, stroke=1)
    sf(c, theme); c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M + 8, y_top - WB_H + 22, f'{label}:')
    lw = c.stringWidth(f'{label}:  ', 'Helvetica-Bold', 8.5)
    sf(c, DARK); c.setFont('Helvetica', 8.5)
    c.drawString(M + 8 + lw, y_top - WB_H + 22, words)
    return y_top - WB_H - 8


def marking_header(c):
    sf(c, GREEN); c.setFont('Helvetica-Bold', 20)
    c.drawString(M, H - M - 14, 'Marking Station')
    ss(c, GREEN); c.setLineWidth(0.8)
    c.line(M, H - M - 24, W - M, H - M - 24)
    return H - M - 40


def answer_row(c, arrow_text, main_text, sub_text, y_top):
    sf(c, GREEN); c.setFont('Helvetica-Bold', 9)
    c.drawString(M, y_top - 8, f'\u2192 {arrow_text}')
    sf(c, DARK); c.setFont('Helvetica', 9)
    c.drawString(M + 60, y_top - 8, main_text)
    if sub_text:
        sf(c, GREY); c.setFont('Helvetica', 8)
        c.drawRightString(W - M, y_top - 8, sub_text)
    return y_top - 16
```

---

## Standard vs Adapted — The Core Distinction

**This is not about making things easier. It is about changing the response mode.**

The standard LP requires the pupil to generate and organise their own response.
The adapted LP scaffolds HOW they respond — the cognitive task is similar but the
output method is structured so a pupil who needs more support can access it.

| Standard response mode | Adapted equivalent |
|---|---|
| Open writing frame (write your comparison) | Cloze sentences with gaps |
| Extended explanation paragraph | Tick-box observation frame with sentence starters |
| Fill in the table from recall | Labelling / match exercise (words provided, pupil places them) |
| Analysis question (what does this tell us?) | Structured prompt with sentence opener given |
| Drawing and labelling from description | Part-labelled diagram — pupil adds missing labels from word bank |
| Ranking or sequencing task | Cut-and-stick ordering (describe the items, pupil numbers them) |
| Source evaluation | Guided sentence with yes/no + because prompt |

The content pupils engage with (the images, the text, the stimulus) should be
identical or near-identical between versions. What changes is how they record
their thinking.

**Never:** produce an adapted LP that simply has fewer questions or shorter text.
**Never:** remove an entire task type from the adapted version — find its
scaffolded equivalent.

**Vocabulary support on adapted LPs:**
- Word bank size: 5–7 words (standard: 9–12)
- Only the most important tier-2 and tier-3 vocabulary
- Word bank is always visible during any written response section

---

## Task Type Taxonomy by Lesson Stage

### Stage 1 — Introduction / Prior Knowledge (lesson 1–2 of enquiry)
*Goal: activate what pupils know and establish key vocabulary.*

Standard:
- Short recall table (2–3 col: I already know / I think / I want to find out)
- Vocabulary matching (term → definition)
- Annotated image or map response

Adapted:
- Same table with sentence starters in each cell
- Match with words on one side, definitions on the other (draw a line)
- Part-labelled image with word bank

### Stage 2 — Application / Comparison (lesson 3–5 of enquiry)
*Goal: use new knowledge to make comparisons, classifications or judgements.*

Standard:
- Comparison table (two countries / periods / concepts)
- Description frame with minimum vocabulary requirement
- Evidence sorting task with justification sentence

Adapted:
- Cloze comparison sentences
- Structured description with sentence openers (e.g. "In England, …  In Brazil, …")
- Pre-sorted evidence with tick-box justification

### Stage 3 — Assessment / Extended Response (final lesson)
*Goal: demonstrate sustained understanding through extended writing or
full-cycle task.*

Standard:
- Extended writing frame with vocabulary checklist
- No answer boxes — this is assessed work
- Challenge extension: link to wider concept or prior learning

Adapted:
- Writing frame broken into short guided paragraphs with sentence starters
- Vocabulary checklist still present (pupils tick as they use words)
- Challenge extension: removed (not replaced)

---

## Task Type Taxonomy by Subject

### Geography
- Comparison table (physical / human / environmental rows)
- Map labelling (grid reference, compass direction, land use)
- Land use recording from image evidence
- Description frame (location, climate, topography, land use)
- Before/after image analysis (what changed / cause / impact)
- Environmental impact ranking with justification

### History
- Evidence analysis frame: What? / Who? / When? / Why does this matter?
- Timeline ordering (pupil places events on a pre-drawn line)
- Significance ranking (most → least, with written justification)
- Source evaluation: What does this tell us? / What might be missing?
- Change and continuity: same/different sorting table

### Science
- Predict / Observe / Explain table (3-col, one row per variable or specimen)
- Classification table (sort by characteristic)
- Results recording grid (measurement data)
- Explanation frame: I think this happens because…
- Fair test design: variable / what we change / what we keep the same / what we measure

### Computing (primary "other" subject)
- Algorithm design frame: numbered steps with space to annotate
- Debugging record: error description / what I changed / outcome
- Decomposition table: big problem → sub-problems → solution approach
- Evaluation frame: what worked / what I would change / why
- Data representation: binary / decimal / pixel grid task

### Art / Music / Citizenship / DT (lower priority — use as needed)
- Art: response to stimulus (describe → analyse → evaluate), annotation frame
- Music: listening response (pulse / pitch / tempo / dynamics) with sentence starters
- Citizenship: rights and responsibilities sorting, case study analysis frame
- DT: design criteria checklist, evaluate against criteria frame

---

## Higgsfield Image Decision Rule

Generate a Higgsfield image for the LP when:
- The lesson introduces or references a place, environment, habitat, historical
  setting or physical phenomenon pupils are unlikely to have seen directly
- The image would anchor a Part A observation or evidence task
- Geography and History LPs: strong default to generate
- Science LPs: generate for ecology / habitats / Earth science; skip for
  controlled experiments where a diagram is more appropriate

Do NOT generate a Higgsfield image when:
- The lesson is skills-based (map skills, algorithm design, source analysis
  technique) and a diagram serves better
- The LP already receives images from the teaching deck (e.g. board images
  referenced in task instructions)
- Computing LPs — use a diagram instead

**If generating:**
- Model: `nano_banana_pro`
- Aspect ratio: `16:9`
- Placement: below the learning label, above Part A, full content width,
  height approximately 115 pt (≈ 1.6 inches)
- Prompt style: full narrative sentence describing scene, setting and lighting —
  not keyword list. Example:
  *"A photorealistic aerial view of a vast Amazon rainforest clearing at golden
  hour, showing a sharp boundary between dense green canopy and bare red earth
  where logging has occurred, dramatic clouds overhead."*
- After `job_display`, download via `curl` and embed with `ImageReader`

**Image placement in ReportLab:**
```python
from reportlab.lib.utils import ImageReader
img = ImageReader('/home/claude/lp_image.jpg')
IMG_H = 115
IMG_Y = y - IMG_H          # y is content start from learning_label()
c.drawImage(img, M, IMG_Y, width=CW, height=IMG_H, preserveAspectRatio=True)
y = IMG_Y - 12             # gap below image before Part A
```

---

## LP-to-Deck Alignment Rule

Before writing Part B content, read the teaching deck's You Do slide.
Part B must:
- Use the same task type as the You Do
- Use the same stimulus (same image, same source text, same data)
- Use the same vocabulary list

If no teaching deck exists yet, note in the LP build plan what constraints the
You Do will need to respect, then flag this to Innes.

---

## Enquiry Stage Awareness

Before proposing LP content, establish the lesson number within the enquiry
sequence and apply the correct stage from the taxonomy above. State the stage
explicitly in your build plan confirmation to Innes.

Stages:
- Lesson 1–2 → Stage 1 (Introduction)
- Lesson 3–(n-1) → Stage 2 (Application)
- Final lesson → Stage 3 (Assessment)

---

## LP Structure — Page Layout

### Page 1 (pupil sheet)

```
learning_label()           ← always first
[Higgsfield image]         ← if applicable, immediately below label
Part A heading             ← section_head()
  [task type: vocabulary / recall / evidence]
  [word bank if needed]
Part B heading             ← section_head()
  [task type: application / comparison / extended response]
  [word bank or vocabulary checklist if needed]
```

### Page 2 (marking station)

```
marking_header()
Part A answers             ← section_head() in GREEN
  answer_row() per item, same order as Part A
  [model answers for open tasks, exact answers for closed tasks]
Part B answers / model
  section_head() in GREEN
  For closed tasks: answer_row() per item
  For extended writing: model paragraph (body() lines, 9pt)
```

---

## File Naming

```
T{term}W{week}_{Day}_L{nn}_{SubjectCode}_{Standard|Adapted}.pdf
```

Examples:
```
T6W4_Mon_L04_Geographers_Standard.pdf
T6W4_Mon_L04_Geographers_Adapted.pdf
T5W2_Thu_L07_Historians_Standard.pdf
T5W2_Thu_L07_Historians_Adapted.pdf
T6W1_Tue_L02_Scientists_Standard.pdf
T6W1_Tue_L02_Scientists_Adapted.pdf
T6W3_Wed_L05_ComputerScientists_Standard.pdf
```

---

## Build Process

1. Confirm all inputs with Innes (see Session Start Checklist step 5)
2. Run CLF prior learning check — state findings
3. Decide Higgsfield image yes/no — if yes, generate before writing builder
4. Write single Python script: `build_{subject}_lp_L{nn}.py`
   - Define all content as data structures at the top (not inline)
   - One function per LP version: `build_standard()`, `build_adapted()`
   - Both called from `if __name__ == '__main__':`
5. Run the script
6. QA render with PyMuPDF (see below)
7. Fix any geometry errors, re-run, re-render
8. Deliver both PDFs — zip only if more than two files

---

## QA Rendering (mandatory)

Use PyMuPDF — not pdftoppm, not LibreOffice. Standard fonts (Helvetica) render
correctly in PyMuPDF only in this environment.

```python
import fitz  # pymupdf

def qa_render(pdf_path, out_dir='/home/claude/qa_renders', dpi=150):
    import os
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        out = os.path.join(out_dir, f'{os.path.basename(pdf_path)}_p{i+1}.png')
        pix.save(out)
    print(f'Rendered {len(doc)} pages → {out_dir}')
```

After rendering, view each PNG and check:
- No text overlaps a box boundary
- No element has less than 12 pt clearance from a box edge
- Large text ascenders stay inside their containers
- Drawing areas are white, not tinted
- No section is mostly empty
- Word bank text is not using the tracing font

---

## CLF Prior Learning Check — Search Pattern

```python
# At session start, search the CLF doc for subject + year group
# Use bash + pdftotext or PyMuPDF text extraction to search

import fitz
doc = fitz.open('/mnt/project/CLF_Curriculum_Progression_Summary_v3_3.pdf')
search_terms = ['Year 4', 'geography']   # adjust per session
results = []
for page in doc:
    text = page.get_text()
    if all(t.lower() in text.lower() for t in search_terms):
        results.append((page.number + 1, text[:800]))

for pg, snippet in results[:5]:
    print(f'--- Page {pg} ---')
    print(snippet)
```

State findings in plain prose before proposing LP content. If cross-curricular
links are found (e.g. geography overlaps with science habitats from earlier in
the year), note them and consider reflecting the link in the LP stimulus or
vocabulary.

---

## Content Consistency Rule

Before writing any LP content, check what has already been taught in this
enquiry sequence. The LP must not duplicate task types or stimulus material
from previous lessons in the same enquiry. If building multiple LPs in one
session, keep a running list of:
- Task types already used (do not repeat the same type in consecutive lessons)
- Vocabulary already introduced (build on it, do not re-introduce as new)
- Images or sources already used (never reuse as the main stimulus)

---

## Non-Duplication with Maths LPs

This skill produces ReportLab PDF LPs only. PPTX-format LPs (maths) use the
separate maths-complete-planning-and-resources skill. Never mix the two — do
not produce enquiry LPs as PPTX, do not produce maths LPs with this skill.
