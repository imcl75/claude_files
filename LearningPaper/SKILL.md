---
name: learning-paper
description: Create a Year 4 learning paper as a PPTX file. Use this skill whenever Innes asks for a learning paper, LP, worksheet, independent task, or practice questions for any subject. Also trigger when he says things like 'make me an LP for...', 'create a learning paper about...', 'I need a worksheet on...', 'make some questions for...', 'create an independent task for...'. This skill handles maths, writing, and all enquiry subjects (geography, history, science, computing, art, design, music, languages, citizenship, reading). It generates the correct learning label, content, and marking station answer page. Always use this skill for learning papers even for partial requests.
---

# Learning Paper Skill

A learning paper (LP) is a printable worksheet used in Innes's Y4 class. It is always a **PPTX file** with **portrait A4 slides** (7.5" × 10.833").

---

## ⚠️ MANDATORY: Learning Label Build Process

**ALWAYS use `label_builder.py`** — never build the label by hand or from scratch.  
Doing otherwise has repeatedly produced wrong labels (full-width blue bars, wrong fonts, vertical text, overlapping elements). The builder encodes the exact WFA spec. Use it.

### Step 1 — Fetch the builder

```python
import re, os, urllib.request

with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)

if not os.path.exists('/home/claude/label_builder.py'):
    url = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/label_builder.py'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=20) as r:
        open('/home/claude/label_builder.py', 'wb').write(r.read())

import sys; sys.path.insert(0, '/home/claude')
from label_builder import build_enquiry_label, LL_W, LL_H
```

### Step 2 — Fetch the subject icon

Icons live in `/home/claude/ll_icons/{subject_key}.png`. If missing, fetch them:

```python
import os, urllib.request, re, base64

if not os.path.exists('/home/claude/ll_icons/geographer.png'):
    # Fetch generate_wfa_labels.py, which contains fetch_icons_from_tool()
    with open('/mnt/skills/user/github-sync/SKILL.md') as f:
        TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)
    url = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/generate_wfa_labels.py'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=20) as r:
        open('/home/claude/generate_wfa_labels.py', 'wb').write(r.read())
    # Now run the fetch
    import importlib.util
    spec = importlib.util.spec_from_file_location('gwl', '/home/claude/generate_wfa_labels.py')
    gwl = importlib.util.module_from_spec(spec); spec.loader.exec_module(gwl)
    gwl.fetch_icons_from_tool()

ICON_PATH = '/home/claude/ll_icons/{subject_key}.png'
# e.g. '/home/claude/ll_icons/geographer.png'
```

### Step 3 — Call the builder

```python
# Label position on the slide
MARGIN = 0.25   # inches
LBL_X = SW_IN - LL_W - MARGIN   # top-right
LBL_Y = MARGIN

build_enquiry_label(
    slide,
    x        = LBL_X,
    y        = LBL_Y,
    date_str = '06/07/2026',          # DD/MM/YYYY
    key_q    = 'Are England and Brazil different?',
    lf       = 'describe and compare land use in England and Brazil',
    ican1    = 'describe land use in Brazil',
    ican2    = 'compare land use using geographical vocabulary',
    icon_path= ICON_PATH,
)
```

### ⚠️ CRITICAL parameter rules

| Parameter | What to pass | Builder prepends |
|-----------|-------------|-----------------|
| `lf`      | verb phrase only, **no leading "to"** — e.g. `'describe and compare...'` | `'LF: To '` |
| `ican1`   | verb phrase only, **no leading "I can"** — e.g. `'describe land use...'` | `'I can '` |
| `ican2`   | verb phrase only, **no leading "I can"** | `'I can '` |
| `key_q`   | full question with `?` | nothing |
| `date_str`| `'DD/MM/YYYY'` | nothing |

Passing `'to describe...'` produces `'LF: To to describe...'`. Passing `'I can describe...'` produces `'I can I can describe...'`. Both are bugs. Do not do this.

### Content starts below the label

```python
CONT_Y = LBL_Y + LL_H + 0.15   # first content element y position
CONT_X = MARGIN
CONT_W = SW_IN - 2 * MARGIN
```

---

## Subject → Icon Map

| State of being   | `subject_key`      | `icon_path` |
|------------------|--------------------|-------------|
| Geographer       | `geographer`       | `ll_icons/geographer.png` |
| Historian        | `historian`        | `ll_icons/historian.png` |
| Scientist        | `scientist`        | `ll_icons/scientist.png` |
| Mathematician    | `mathematician`    | `ll_icons/mathematician.png` |
| Reader           | `reader`           | `ll_icons/reader.png` |
| Writer           | `writer`           | `ll_icons/writer.png` |
| Artist           | `artist`           | `ll_icons/artist.png` |
| Athlete          | `athlete`          | `ll_icons/athlete.png` |
| Computer Scientist | `computer_scientist` | `ll_icons/computer_scientist.png` |
| Linguist         | `linguist`         | `ll_icons/linguist.png` |
| Musician         | `musician`         | `ll_icons/musician.png` |

All icons are fetched from `https://staff.wallscourt-farm-academy.co.uk/learning-labels/index.html` via `fetch_icons_from_tool()`. They are cached at `/home/claude/ll_icons/`.

---

## What the label looks like (locked)

```
┌─────────────────────────────────────────────┐  2.338" wide
│ 06/07/2026              [globe icon 0.26"]  │  ← top row: date NARROW_W, icon right
│ Key Question            [geographer caption]│
│ Are England and Brazil different?           │  ← bold underline, FULL_W
│ LF: To describe and compare land use...     │  ← 7pt Calibri, FULL_W
│ I can describe land use in Brazil           │  ← 6.5pt Calibri, FULL_W
│ I can compare land use using geo vocabulary │  ← 6.5pt Calibri, FULL_W
└─────────────────────────────────────────────┘  1.021" tall
```

- **Position**: top-right of slide with 0.25" margin
- **Font**: Calibri throughout (NOT Aptos, NOT Twinkl Cursive Looped)
- **No borders, no coloured boxes, no background fill** on the label
- **Caption "geographer"** (or other subject): `word_wrap=False`, textbox width = `ICO_W + 0.30"`, offset left 0.15" from icon x to centre it

---

## Label spec constants (from label-spec.md)

```python
CM          = 1 / 2.54
LABEL_SCALE = 0.72 * 0.85        # = 0.612
LL_W        = 9.7 * CM * LABEL_SCALE   # = 2.338"
LL_H        = 4.24 * CM * LABEL_SCALE  # = 1.021"
PAD         = 0.04                # inches, all edges
ICO_W       = 0.26                # icon width
ICO_H       = ICO_W * (118/120)  # ≈ 0.257" (aspect ratio of actual PNGs)
NARROW_W    = LL_W - ICO_W - PAD * 3  # text beside icon (date only)
FULL_W      = LL_W - PAD * 2          # full label width

# Row heights
DATE_H  = 0.11    # date line
KQ_H    = 0.12    # "Key Question" label
Q_H     = 0.25    # question text (allows one wrap line)
LF_H    = 0.22    # LF line
ICAN_H  = 0.13    # each I can line
```

---

## Learning Label Types

| Label Set | Subjects | Dimensions |
|-----------|----------|------------|
| Set 1 (Enquiry) | geographer, scientist, historian, artist, musician, designer, citizen, linguist, computer scientist, reader | 2.338" × 1.021" |
| Set 2 (Writer) | Writer, Writing as a [subject] | 7.3" × 1.85" |
| Set 3 (Mathematician) | All maths topics | 2.338" × 1.021" (rendered as PNG) |

Set 1 and Set 3 both use `label_builder.py`.  
Set 2 (Writer) is a different format — see the writing-lesson-pptx skill.

---

## Inputs to Gather

Before generating, confirm:

- **Subject** → determines the icon and state of being caption
- **Date** → DD/MM/YYYY
- **Key Question** → the overarching enquiry question
- **LF** → verb phrase only (no leading "to")
- **I can 1 and 2** → verb phrase only (no leading "I can")
- **Content** → the actual questions/tasks (generate from lesson context if not provided)
- **Adapted version needed?** → default no; ask if not stated

---

## Content Rules

- **Font**: Twinkl Cursive Looped for all content text. Calibri for label only.
- **Answer lines**: solid grey lines, spaced 0.20" apart
- **Answer boxes**: rectangles for number answers in maths
- **Answer page**: titled "Marking Station" in green bold (#4FAD5B). Answers replace answer lines in green.
- **Word bank**: cream fill (#FEF9E7), orange border (#E67E22), "Word bank:" bold orange
- **Section headings**: blue (#1798d3) bold 12pt
- **Instruction text**: dark, 9.5pt
- **No borders on the learning label itself**

---

## Build Method (Python + python-pptx)

The geography enquiry LPs use pure python-pptx (not pptxgenjs). The builder script is `Shared/build_geo_lps_pptx.py` or equivalent subject builder. All LP builders must:

1. Import `build_enquiry_label`, `LL_W`, `LL_H` from `label_builder.py`
2. Use `python-pptx` to create slides (`Presentation()`, `slide_layouts[6]`, clear default shapes)
3. Inject all shapes via `slide.shapes.add_textbox()`, `add_picture()`, `add_shape()`, `add_connector()`
4. Deliver as PPTX (not PDF, not DOCX)

```python
from pptx import Presentation
from pptx.util import Emu

def new_prs(sw_in=7.5, sh_in=10.833):
    prs = Presentation()
    prs.slide_width  = Emu(int(sw_in * 914400))
    prs.slide_height = Emu(int(sh_in * 914400))
    blank = prs.slide_layouts[6]
    prs.slides.add_slide(blank)  # slide 1: pupil page
    prs.slides.add_slide(blank)  # slide 2: marking station
    return prs

def clear_slide(slide):
    sp_tree = slide.shapes._spTree
    for child in list(sp_tree):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('sp','pic','graphicFrame','grpSp','cxnSp'):
            sp_tree.remove(child)
```

---

## File Structure

```
learning-paper/
├── SKILL.md (this file)
└── references/
    └── label-spec.md (measurement source of truth)

GitHub imcl75/claude_files:
├── Shared/label_builder.py       ← THE label builder (always fetch this)
├── Shared/generate_wfa_labels.py ← icon fetcher (fetch_icons_from_tool)
├── LearningPaper/label-spec.md   ← full measurement spec
└── Geography/build_geo_lps_pptx.py ← example enquiry LP builder
```

---

## QA

Always QA render before delivery:
```python
import subprocess, fitz
from PIL import Image
import io

subprocess.run(['libreoffice','--headless','--convert-to','pdf',
    'output.pptx', '--outdir','/tmp/'], capture_output=True, timeout=60)
doc = fitz.open('/tmp/output.pdf')
pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
img = Image.open(io.BytesIO(pix.tobytes('png')))
# Crop top-right to verify label, then full page for content
```

Use **PyMuPDF (fitz)** for rendering — not pdftoppm, not LibreOffice Draw.
