---
name: learning-paper
description: Create a Year 4 learning paper as a PPTX file. Use this skill whenever Innes asks for a learning paper, LP, worksheet, independent task, or practice questions for any subject. Also trigger when he says things like 'make me an LP for...', 'create a learning paper about...', 'I need a worksheet on...', 'make some questions for...', 'create an independent task for...'. This skill handles maths, writing, and all enquiry subjects (geography, history, science, computing, art, design, music, languages, citizenship, reading). It generates the correct learning label, content, and marking station answer page. Always use this skill for learning papers even for partial requests.
---

# Learning Paper Skill

A learning paper (LP) is a printable worksheet used in Innes's Y4 class. It is always a **PPTX file** with **portrait A4 slides** (7.5" × 10.833").

## Quick Start

1. **Read this file** to understand the structure
2. **Determine the subject** to select the correct learning label type
3. **Read `references/label-spec.md`** for exact label construction details
4. **Run `scripts/generate_lp.js`** or build manually using the patterns below

## Learning Label Types

There are three learning label sets. The label type is determined by the subject:

| Label Set | Subjects | Dimensions (at 72% scale) |
|-----------|----------|---------------------------|
| Set 1 (Enquiry) | geographer, scientist, historian, artist, musician, designer, citizen, linguist, computer scientist, reader | 2.75" × 1.20" |
| Set 2 (Writer) | Writer, Writing as a [subject] | 7.3" × 1.85" |
| Set 3 (Mathematician) | All maths topics | 2.75" × 1.20" (rendered as PNG) |

## Inputs to Gather

Before generating, determine these (ask if not obvious from context):

### For all LPs:
- **Subject** → determines the label set and icon
- **Date** → DD/MM/YYYY format (default: today)
- **Key Question** → the overarching enquiry question
- **Learning Focus (LF)** → what they are learning
- **I can statements** → exactly 2 success criteria starting with "I can..."
- **Content** → the actual questions/tasks (generate if not provided)
- **Whether an answer page is needed** → default yes

### Additional for maths:
- **Maths topic area** → from this fixed list: Addition, Algebra, Addition and Subtraction, Calculation, Division, Fractions, Fractions / Decimals / Percentages, Fractions and Decimals, Geometry, Geometry - Position / Direction, Indices, Measurement, Measurement - Time, Multiplication, Multiplicative Reasoning, Number and Place Value, Ratio and proportion, Revision, Statistics, Subtraction
- **Number of copies per page** → 1, 2, 3, 4, or 8 (determined by content size)

### Additional for writing:
- **S-number** → optional (e.g. S1, S2, S3), only include if specified
- **Version** → "Writer" (default) or "Writing as a [subject]" (rare, only when specified)

## Content Rules

- **Font**: Twinkl Cursive Looped for all content text. Aptos for maths symbols (÷, ×, etc.)
- **Fractions**: Always rendered with numerator above denominator (stacked), never side-by-side
- **Answer lines**: Solid lines, spaced 0.8cm apart (matches their writing books)
- **Answer line gap**: Leave enough space between a question and its first answer line for writing. Questions needing longer answers (e.g. "explain why...") should have more lines.
- **Answer boxes**: Use boxes (rectangles) for number answers in maths
- **Answer page**: Titled "Marking Station" in green bold (#4FAD5B). Same layout as question page with answers in green bold replacing answer lines.
- **No borders** on learning labels
- **Dashed separators** between sections (grey, dash type)
- **Dashed cut lines** between repeated copies of the same LP
- **"Glue here"**: Rotated text on right margin for two-sided pages only

## Layout Rules

- **Label consistency**: All labels on a page must have the same orientation (all normal OR all rotated, never mixed)
- **Label rotation**: Only rotate when it creates more space for content. Non-rotated is the default.
- **Repeated copies**: When the same LP appears multiple times on a page (to save paper), each copy needs its own learning label
- **Continuation**: When a second section of the SAME lesson appears below a cut line (not a repeat), it does NOT get a learning label
- **Set 1/3 labels**: Position top-right of the content area
- **Set 2 labels**: Position across the top of the page, centred

## File Structure

```
learning-paper/
├── SKILL.md (this file)
├── assets/ (all icon PNGs, logos, ETIW banner)
│   ├── geographer.png, scientist.png, historian.png, etc.
│   ├── mathematician.png
│   ├── writer.png
│   ├── school_logo_LKS2.png, school_logo.png
│   └── ETIW_LKS2.png
├── scripts/
│   └── generate_lp.js (the main generator)
└── references/
    └── label-spec.md (exact label construction details)
```

## How to Generate

### Sticker label sheets (DOCX, 12 Avery labels per sheet)

Use `generate_wfa_labels.py` (canonical LL tool replicator — always fetch from GitHub):
```python
import re, urllib.request, os
with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    skill_text = f.read()
TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', skill_text).group(1)
REPO  = re.search(r'GITHUB_REPO:\s*(\S+)',  skill_text).group(1)
for filename, folder in [('generate_wfa_labels.py','Shared'), ('WFA_Labels_template.docx','Maths')]:
    local = f'/home/claude/{filename}'
    if not os.path.exists(local):
        url = f'https://raw.githubusercontent.com/{REPO}/main/{folder}/{filename}'
        req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
        with urllib.request.urlopen(req, timeout=30) as r:
            open(local, 'wb').write(r.read())
        print(f'Fetched {filename}')
```

Then generate (enquiry example):
```bash
python3 /home/claude/generate_wfa_labels.py --mode geographer \
    --date "07/07/2026" \
    --question "Are England and Brazil different?" \
    --lf "compare human geography features." \
    --ican1 "identify human geography features." \
    --ican2 "compare two countries." \
    --out T6W7_L4_Mon_Labels.docx
```

### Embedded label in PPTX slide (Option 1: preferred)
Read `references/label-spec.md` for exact PPTX measurements (Section 2: Embedded label).
These values come directly from the LL tool. Use pptxgenjs addText/addImage as in `injectLabel()`.

### Option 2: Build manually with pptxgenjs
Read `references/label-spec.md` for exact measurements, then build using the pptxgenjs code patterns in Section 2 of that file.

### After building — fix OOXML issues (prevents PowerPoint repair dialog)

Run over the generated PPTX before delivering. Addresses four problems introduced by pptxgenjs: non-standard media filenames, notesSlide back-references, empty `<a:r>` runs, and a missing theme2.xml reference.

```python
import re, urllib.request, os

with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)

if not os.path.exists('/home/claude/fix_pptx_ooxml.py'):
    url = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/fix_pptx_ooxml.py'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=20) as r:
        open('/home/claude/fix_pptx_ooxml.py', 'wb').write(r.read())

import subprocess
subprocess.run(['python3', '/home/claude/fix_pptx_ooxml.py', '/home/claude/learning_paper.pptx'], check=True)
# Replace learning_paper.pptx with the actual output filename
```

## Key Technical Notes

- **Slide dimensions**: 7.5" × 10.833" (portrait A4-ish, matching the school's existing files)
- **Set 3 (maths) labels**: Must be rendered as PNG images using node-canvas first, then embedded. This allows rotation when needed.
- **Set 1 icons**: Read PNG dimensions to preserve aspect ratio (some icons are landscape, some portrait). Use `iconImg.readUInt32BE(16)` for width and `readUInt32BE(20)` for height.
- **Font availability**: Twinkl Cursive Looped won't be installed in the build environment. Specify it in the PPTX — it will render correctly on Innes's school machines.
- **All measurements in inches** for pptxgenjs. Use `CM = 1/2.54` to convert.
