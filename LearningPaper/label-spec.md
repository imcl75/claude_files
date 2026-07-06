# WFA Learning Label Specification
# Source of truth: https://staff.wallscourt-farm-academy.co.uk/learning-labels/

This file defines the **exact** measurements and font sizes for all WFA learning labels.
Do not deviate from these values. Every field is derived directly from the LL tool source.

---

## 1. Sticker sheet (Avery 99×42mm DOCX — 12 labels per sheet)

Use `generate_wfa_labels.py` (in `Shared/` on GitHub, fetched to `/home/claude/`).

```bash
# Mathematician (maths):
python3 generate_wfa_labels.py --mode mathematician \
    --date "DD/MM/YYYY" --topic "Statistics" \
    --lf "draw a line graph." \
    --ican1 "draw and label axes." --ican2 "plot points." \
    --out T6W7_L20_Mon_Labels.docx

# Enquiry (geographer / historian / scientist / etc.):
python3 generate_wfa_labels.py --mode geographer \
    --date "DD/MM/YYYY" \
    --question "Are England and Brazil different?" \
    --lf "compare human geography features." \
    --ican1 "identify human geography features." \
    --ican2 "compare two countries." \
    --out T6W7_L4_Mon_Labels.docx

# Batch from maths pipeline JSON:
python3 generate_wfa_labels.py --json /home/claude/labels_data.json 20 21 22
```

### Sticker label DOCX measurements (all DXA, 1 inch = 1440 DXA)

| Component        | DXA value | Inches |
|-----------------|-----------|--------|
| Page width      | 11905     | 8.268" |
| Page height     | 16837     | 11.693" |
| Margin top      | 1215      | 0.844" |
| Margin bottom   | 820       | 0.569" |
| Margin left     | 389       | 0.270" |
| Margin right    | 446       | 0.310" |
| Outer table W   | 11376     | 7.900" |
| Label cell W    | 5616      | 3.900" |
| Gap cell W      | 144       | 0.100" |
| Row height      | 2399      | 1.666" |
| Cell margin top | 141       | 0.098" |
| Cell margin L/R | 115       | 0.080" |
| Inner table W   | 5386      | 3.740" |
| Left col W      | 4386      | 3.046" |
| Icon col W      | 1000      | 0.694" |

### Font sizes (Calibri, all modes use these exactly)

| Element         | Half-pts | Points | Style            |
|----------------|----------|--------|-----------------|
| **ENQUIRY**    |          |        |                 |
| Date           | 16       | 8pt    | normal           |
| "Key Question" | 16       | 8pt    | bold             |
| Question text  | 20       | 10pt   | bold, underline  |
| LF             | 18       | 9pt    | normal           |
| I can (×2)     | 16       | 8pt    | normal           |
| Subject caption| 13       | 6.5pt  | normal, right    |
| **MATHEMATICIAN** |       |        |                 |
| Date           | 20       | 10pt   | normal           |
| Topic          | 26       | 13pt   | bold, underline  |
| LF             | 22       | 11pt   | normal           |
| I can (×2)     | 18       | 9pt    | normal           |
| Subject caption| 13       | 6.5pt  | normal, right    |

### Line spacing
- All text paragraphs: `w:line="280" w:lineRule="auto"` (1.167× single)
- Icon image paragraph: `w:line="720" w:lineRule="exact"` (exactly 36pt), `after=20`

### Icon pixel dimensions (screen px at 96dpi, from LL tool ICON_DIMS)

| Subject            | Key                  | W  | H  |
|--------------------|---------------------|----|----|
| Citizen            | Citizen              | 38 | 38 |
| Designer           | Designer             | 38 | 35 |
| Artist             | artist               | 38 | 37 |
| Athlete            | athlete              | 37 | 38 |
| Computer Scientist | computer_scientist   | 38 | 35 |
| Geographer         | geographer           | 38 | 37 |
| Historian          | historian            | 38 | 26 |
| Linguist           | linguist             | 38 | 37 |
| Mathematician      | mathematician        | 38 | 33 |
| Musician           | musician             | 38 | 36 |
| Reader             | reader               | 32 | 38 |
| Scientist          | scientist            | 38 | 27 |
| Writer             | writer               | 38 | 37 |

Pixel to inches: `px / 96`. Pixel to EMU: `px × 9525`.

---

## 2. Embedded label in PPTX slide (Set 1 / Set 3)

Used by `build_lp_v3.js` (`injectLabel()`) and should be used by the learning-paper skill.
These are NOT the same sizes as the sticker sheet — they are scaled to fit the PPTX slide.

### Scale factor
```javascript
LABEL_SCALE = 0.72 × 0.85 = 0.612
CM = 1/2.54 = 0.3937 in/cm
LL_W = 9.7 × CM × LABEL_SCALE = 2.338 inches
LL_H = 4.24 × CM × LABEL_SCALE = 1.021 inches
```

### pptxgenjs measurements (all in inches)

| Element    | Value  | Notes                           |
|-----------|--------|---------------------------------|
| Total W   | 2.338" | LL_W                            |
| Total H   | 1.021" | LL_H                            |
| Padding   | 0.04"  | PAD, used for all edges         |
| Icon W    | 0.26"  | ICO_W                           |
| Icon H    | 0.224" | ICO_W × 103/120 ≈ 0.26 × 0.858 |
| Narrow W  | LL_W − ICO_W − PAD×3 | beside icon |
| Full W    | LL_W − PAD×2          | full width  |

### Font sizes (embedded PPTX label, Calibri)

| Element | Size  | Style        |
|---------|-------|--------------|
| Date    | 7pt   | normal       |
| Topic   | 9pt   | bold, underline |
| LF      | 7pt   | normal       |
| I can   | 6.5pt | normal       |

### pptxgenjs element heights

| Element | Height |
|---------|--------|
| Date    | 0.11"  |
| Topic   | 0.23"  |
| LF      | 0.22"  |
| I can 1 | 0.13"  |
| I can 2 | 0.13"  |

### Position on PPTX slide
The label is positioned at top-right of the content area.
`injectLabel(slide, x, y)` — caller supplies x and y.

For **Type A maths LP** (write-on-paper):
```javascript
const LL_X = SLIDE_W - LL_W - MARGIN;   // right edge minus margin
const LL_Y = MARGIN;                      // top
```

For **enquiry LP** in the learning-paper skill, use the same pattern:
- Place top-right of slide, within margins
- Do NOT put a border on the label
- Icon goes top-right within the label box (beside date/question)

---

## 3. File locations

| File                          | GitHub path                        | Local path                    |
|-------------------------------|-----------------------------------|-------------------------------|
| `generate_wfa_labels.py`      | `Shared/generate_wfa_labels.py`   | `/home/claude/`               |
| `WFA_Labels_template.docx`    | `Maths/WFA_Labels_template.docx`  | `/home/claude/`               |
| Icons (all subjects)          | Fetched from LL tool on first run | `/home/claude/ll_icons/`      |
| Mathematician icon            | In template DOCX automatically    | `/home/claude/lp_assets/`     |

The FILE_MAP in github-sync tracks `generate_wfa_labels.py` and `WFA_Labels_template.docx`.
Both are auto-fetched on session start.

---

## 4. Text content rules (for all label types)

- LF line: `LF: To {lf_text}` — verb phrase only after "To" (no capital)
- I can: `I can {ican_text}` — verb phrase only (no capital after "I can")
- Subject caption under icon: lowercase (see SUBJECT_LABELS in generate_wfa_labels.py)
- Date: `DD/MM/YYYY` format

**Topic list for mathematician labels** (must be exact):
Addition, Addition and Subtraction, Algebra, Calculation, Division, Fractions,
Fractions / Decimals / Percentages, Fractions and Decimals, Geometry,
Geometry - Position / Direction, Indices, Measurement, Measurement - Time,
Multiplication, Multiplicative Reasoning, Number and Place Value,
Ratio and proportion, Revision, Statistics, Subtraction
