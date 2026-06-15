---
name: maths-complete-planning-and-resources
description: >
  THE ONLY skill for all maths planning and resource generation for Year 4 at WFA.
  ALWAYS use this skill — never build maths resources ad hoc.
  Triggers: "maths lessons", "maths planning", "maths slides", "make my maths",
  "build my maths week", "maths plan", "learning papers", "rapid maths",
  "working memory starters", "build T5W1", "build T5W2", "make week N",
  "maths for next week", or any term/week label (T5W2, T5W3 etc) in a maths context.
  Produces: teaching PPTXs with LP previews injected, LP PPTXs,
  Label sheets (sticker or embedded LL — see LP Type rule).
  DO NOT ask Innes to upload anything — all scripts, templates, lesson data and
  the term plan JSON are already at /mnt/skills/user/maths-complete-planning-and-resources/.
  Always start by running Step 1 (environment restore).
---

# Maths Complete Planning and Resources — v3 Pipeline

## ⚠ THIS IS THE ONLY MATHS SKILL — ALWAYS USE IT

Any request involving maths lessons, maths planning, maths slides, learning papers,
rapid maths, working memory starters, or a term/week label in a maths context MUST use
this skill. Never build maths resources without reading and following this file.

## ACTION: WHEN INNES SAYS "BUILD [WEEK]" (e.g. "build T5W1", "make this week's maths")

DO THIS IMMEDIATELY — no questions, no asking for files, no asking which phase:

1. Run the environment restore commands in Step 1 below
2. Check which lessons need data authored (Step 2)
3. Build all teaching PPTXs (Step 3)
4. Build all LPs (Step 4)
5. Generate label sheets (Step 5 — see LP Type rule)
6. Deliver (Step 6)

The JSON plan is at `/mnt/skills/user/maths-complete-planning-and-resources/maths_plan_v3.json`.
All builders, templates, and data files are in that folder. Nothing to upload.

The ONLY input needed from Innes during a build is:
- Rapid Maths topic selections (ask once, at the start)
- Whether the plan has changed since last time

## ACTION: WHEN INNES SAYS "PLAN MY MATHS" or "NEW PLAN FOR TERM"

Only then go to the Phase 1 section further down.

---

## CRITICAL — LP TYPE RULE

Every lesson falls into one of two types. Determine this before building LPs.

**Type A — Write-on-paper LP (pupils write on the sheet)**
Geometry, directions, polygon translation, symmetry, shapes with diagrams, coordinate grids.
Pupils stick the LP into their book.
→ LP gets embedded learning label (LL) top-right, rendered by `injectLabel()`
→ No separate sticker sheet needed

**Type B — Book-based LP (pupils record in their maths books)**
Word problems, calculations, arithmetic reasoning, multistep problems.
The LP is questions to refer to; all working and answers go in the maths book.
→ LP has NO LL
→ Generate a separate 2×6 sticker label sheet: `python3 generate_labels.py [lesson_nums]`

**When unsure:** Ask Innes before building. Do not guess.

Decision shorthand:
- Shapes/grids/diagrams on the page that pupils interact with → Type A
- Questions pupils read and then work in books → Type B

---

## PHASE 1 — Term Planning

### What you need from Innes
- Topic/objectives for the block
- Number of weeks
- Term/week label for week 1
- Any prior learning context

### What to produce

A JSON file (`maths_plan_v[N].json`) structured as an array of lesson objects.
Each lesson object must contain:

```json
{
  "lesson": 1,
  "week": "T5W1",
  "weekIndex": 1,
  "day": "Monday",
  "topic": "Coordinates",
  "li": "Pupils can read and plot coordinates in the first quadrant.",
  "labelTopic": "Geometry - Position and Direction",
  "loText": {
    "walt": "…identify which operation a word problem needs and explain why.",
    "tiob": "…",
    "iwstb": "…"
  },
  "cycle1": {
    "focus": "Reading coordinates",
    "ido": ["Describe what each lesson slide should show..."],
    "slideTitles": {
      "ido": ["Title for I Do slide 1", "Title for I Do slide 2"],
      "wedo": ["We Do slide title"],
      "trios": ["Trios slide title"],
      "independent": ["Independent slide title"]
    },
    "trios": { "task": "...", "challenge": "..." },
    "independent": { "standard": "...", "supported": "...", "stretch": "..." }
  },
  "cycle2": { "...same structure as cycle1..." },
  "spotTheMistake": {
    "slideTitle": "Spot the mistake",
    "concept": "...",
    "errorType": "off_grid | wrong_translation | wrong_reflection_distance | clock_hand_confusion",
    "errorInstruction": "...",
    "errorNote": "...",
    "gridSize": 7,
    "startPoint": [col, row],
    "extraPoints": [[col, row, "error|correct|mirror_v|mirror_h"]]
  },
  "vocabularyFocus": ["word1", "word2", "word3", "word4", "word5"]
}
```

### labelTopic — fixed school list

`labelTopic` must be EXACTLY one of these values:

Addition | Addition and Subtraction | Algebra | Calculation | Division |
Fractions | Fractions / Decimals / Percentages | Fractions and Decimals |
Geometry | Geometry - Position and Direction | Indices | Measurement |
Measurement - Time | Multiplication | Multiplicative Reasoning |
Number and Place Value | Ratio and proportion | Revision | Statistics | Subtraction

Map lesson content to the closest match. Examples:
- Operation identification, multistep, mixed ops → Calculation
- × and ÷ word problems → Multiplicative Reasoning
- Money, measure, mass → Measurement
- Coordinate grids, translations, directions → Geometry - Position and Direction

Save as `/home/claude/transfer_files/maths_plan_v[N].json`.
Present and ask Innes to confirm.

---

## PHASE 2 — Week Build

### What you need from Innes
- Which week to build
- Confirmation the plan hasn't changed, OR any updates
- Rapid Maths topics for the week (present multi-select — Place Value always included)

### Step 1 — Restore the environment

```bash
SKILL=/mnt/skills/user/maths-complete-planning-and-resources

# Copy builders and data
cp $SKILL/build_lesson_v3.py /home/claude/
cp $SKILL/lesson_data.py /home/claude/
cp $SKILL/build_lp_v3.js /home/claude/
cp $SKILL/lesson_data.js /home/claude/
cp $SKILL/inject_lp_previews.py /home/claude/
cp $SKILL/generate_labels.py /home/claude/
cp $SKILL/rapid_maths_generator.py /home/claude/
cp $SKILL/working_memory_starters.py /home/claude/

# Copy plan
mkdir -p /home/claude/transfer_files
cp $SKILL/maths_plan_v3.json /home/claude/transfer_files/

# Set up template (assets/ subdirectory in skill folder)
cp $SKILL/assets/template_v3.pptx /home/claude/template.pptx
mkdir -p /home/claude/unpacked/ppt/media
cd /home/claude && unzip -o template.pptx -d unpacked > /dev/null 2>&1

# Extract cloud image from key-question-new.pptx
mkdir -p /home/claude/kq_unpack
cp $SKILL/assets/key-question-new.pptx /home/claude/kq_unpack/
cd /home/claude/kq_unpack && unzip -o key-question-new.pptx > /dev/null 2>&1
cp ppt/media/image7.png /home/claude/unpacked/ppt/media/cloud_kq.png

# Extract LR reference images
mkdir -p /home/claude/lr_unpack
cp $SKILL/assets/LR_slide.pptx /home/claude/lr_unpack/
cd /home/claude/lr_unpack && unzip -o LR_slide.pptx > /dev/null 2>&1
cp ppt/media/image7.png  /home/claude/unpacked/ppt/media/image11.png
cp ppt/media/image8.png  /home/claude/unpacked/ppt/media/image12.png
cp ppt/media/image9.png  /home/claude/unpacked/ppt/media/image13.png
cp ppt/media/image10.png /home/claude/unpacked/ppt/media/image14.png
cp ppt/media/image11.png /home/claude/unpacked/ppt/media/image15.png
cp ppt/media/image12.png /home/claude/unpacked/ppt/media/image16.png
cp ppt/media/image13.png /home/claude/unpacked/ppt/media/image17.png
cp ppt/media/image14.jpg /home/claude/unpacked/ppt/media/image18.png
cp ppt/media/image15.jpg /home/claude/unpacked/ppt/media/image19.png

# Banner images into unpacked media
cp $SKILL/assets/banner_visualise.png /home/claude/unpacked/ppt/media/
cp $SKILL/assets/banner_analyse.png   /home/claude/unpacked/ppt/media/
cp $SKILL/assets/banner_attack.png    /home/claude/unpacked/ppt/media/

# LP assets
mkdir -p /home/claude/lp_assets
[ -f "$SKILL/assets/mathematician_icon.png" ] && cp $SKILL/assets/mathematician_icon.png /home/claude/lp_assets/
cp $SKILL/WFA_Labels_template.docx /home/claude/

# Install node dependencies
npm install pptxgenjs canvas 2>/dev/null

cd /home/claude
```

### Step 2 — Check lesson_data.py and lesson_data.js

For each lesson in the week, both data files must have entries.

```bash
python3 -c "
from lesson_data import LESSON_DATA
import json
with open('transfer_files/maths_plan_v3.json') as f: plan = json.load(f)
week = 'T5W2'  # replace
lessons = [l for l in plan['lessons'] if l['week'] == week]
for l in lessons:
    ln = l['lesson']
    print(f'L{ln} ({l[\"day\"]}): {\"✓\" if ln in LESSON_DATA else \"✗ MISSING\"}')"

node -e "
const data = require('./lesson_data.js');
[9,10,11,12].forEach(ln => {  // replace with actual lesson numbers
  console.log('L' + ln + ': ' + (data[ln] ? '✓' : '✗ MISSING'));
});"
```

If any lesson is missing, author it before building (see Authoring sections).

### Step 3 — Build teaching slides

```bash
cd /home/claude
python3 build_lesson_v3.py [lesson_number]
```

Produces: `{week}_L{N}_Teaching.pptx`
Fix any ⚠ pre-flight warnings before proceeding.

### Step 4 — Build LPs

```bash
node build_lp_v3.js [lesson_number]
```

Produces: `{week}_L{N}_LP.pptx` (arithmetic type: 6 slides; geometry type: 3 slides)

`build_lp_v3.js` automatically writes/updates `/home/claude/labels_data.json` on each build.

### Step 5 — Labels

Determine LP type for each lesson (see LP TYPE RULE above), then:

**Type A (write-on-paper):** LL is already embedded in the LP by `injectLabel()`. Done.

**Type B (book-based):** Generate the sticker sheet after all LPs are built:

```bash
python3 generate_labels.py [lesson_number] [lesson_number] ...
# e.g. python3 generate_labels.py 9 10 11 12
```

Produces one DOCX per lesson: `{week}_L{N}_{day}_Labels.docx`
Each file: 12 identical Avery 99×42mm labels, Calibri fonts, school format.
Innes prints and cuts — pupils stick in their maths book.

### Step 6 — Inject LP previews and deliver

```bash
cd /home/claude
python3 inject_lp_previews.py [lesson_number]
```

Then copy all output files to `/mnt/user-data/outputs/` and call `present_files`.

---

## Learning Label (LL) Format

### Embedded LL (Type A LPs — `injectLabel()`)

Called by `build_lp_v3.js` automatically for geometry/directions/polygon lesson types.

Layout (top-right of LP slide, LL_W × LL_H):
- Icon top-right (mathematician PNG)
- Date: Calibri 7pt
- Topic: Calibri 9pt bold underlined (beside icon)
- LF: Calibri 7pt full width
- I can 1: Calibri 6.5pt
- I can 2: Calibri 6.5pt
- No border

### Sticker sheet (Type B LPs — `generate_labels.py`)

Uses `WFA_Labels_template.docx` as the base template (raw XML replacement, preserving all
Calibri fonts and formatting). Replaces the five placeholder text strings in each of the
12 label cells.

Template placeholder values (do not change these in lesson data):
- `15/06/2026` → `label["date"]`
- `Calculation` → `label["topic"]` (must be from fixed school list)
- `LF: To identify which operation is required to solve a problem.` → `label["lf"]`
- `I can identify the operation and clauclate using a suitable method` → `label["ican1"]`
- `I can solve problems involving the four operations` → `label["ican2"]`

The template itself must not be modified. If a new template is needed (school format change),
save the new reference DOCX as `WFA_Labels_template.docx` in the skill folder.

---

## Authoring LP Data (lesson_data.js)

Each lesson needs an entry keyed by lesson number. The entry has different structures
depending on LP type.

### iCan rules (all types)
- Short single phrases: "I can [verb phrase]"
- No colons, no subordinate clauses, no "then..." additions
- Child-friendly language — no jargon (avoid "signal words", "efficient strategy", etc.)
- Maximum ~50 characters per statement
- Good: "I can plot a point by moving right and up from the origin."
- Good: "I can find clues in a word problem to choose the right calculation."
- Bad: "I can follow the two-step routine: identify the operation, then calculate."

### LP type: arithmetic (word problems / calculations)

```javascript
N: {
  iCan: ['I can [short phrase].', 'I can [short phrase].'],
  lp1: {
    title: 'Short title from school topic list',
    type: 'arithmetic',
    instruction: 'Brief instruction for pupils.',
    questions: [
      { q: 'Word problem or calculation text', answer: 'Answer string' },
      // 3–4 questions; word problems > 50 chars trigger word-problem strip layout
      // calculations <= 50 chars trigger 10-strip calculation layout
    ],
    goingFurther: 'Optional challenge task (full-width box at bottom).',
  },
  lp2: { ...same structure, different questions... },
  adaptedSupport: {
    lp1Questions: [ ...2 simpler questions... ],
    lp2Questions: [ ...1–2 simpler questions... ],
    hint1: 'Step-by-step scaffold text\n1. ...\n2. ...',
    hint2: 'Remember: ... brief reminder ...',
  },
}
```

**Word problem LP layout (maxQLen > 50):**
- One question per strip, repeated to fill page
- No "A:" answer line — pupils record in maths book
- Full slide width (no label column)
- Going further: full-width purple box at bottom
- Marking station: answer shown in green text at bottom of each strip

**Calculation LP layout (maxQLen ≤ 50):**
- 10 strips, 2-column grid (or 1 column if ≤ 2 questions)
- Going further: full-width footer box

**Adapted LP (right column hints):**
- 2 questions in left column (full height — no answer line)
- Right column: hint1 box (Step-by-step, blue) + hint2 box (Remember, white)
- Hints start from top — no label image

### LP type: directions (L1 style)

```javascript
N: {
  iCan: ['I can...', 'I can...'],
  lp1: {
    title: '...',
    questions: [{start:[c,r], end:[c,r], answer:'N right, N up'}, ...],
    goingFurther: '...',
  },
  lp2: { ...same... },
  adaptedSupport: {
    lp1Questions: [...],
    lp2Questions: [...],
    workedExample1: {start:[c,r], end:[c,r], answer:'...'},  // DIFFERENT from questions
    workedExample2: {start:[c,r], end:[c,r], answer:'...'},
    hint1: '...', hint2: '...',
  },
}
```

### LP type: polygon_translation (L2+ style)

```javascript
N: {
  iCan: ['I can...', 'I can...'],
  lp1: {
    title: '...',
    gridSize: 7,
    type: 'polygon_translation',
    questions: [
      { shape:[[c,r],...], labels:['A','B',...], translation:[dc,dr], answer:'N right, N up' },
    ],
    instruction: '...',
    goingFurther: '...',
  },
  lp2: { ... },
  adaptedSupport: {
    lp1Questions: [...],
    lp2Questions: [...],
    workedExample1: { shape:[...], labels:[...], translation:[dc,dr], answer:'...' },
    workedExample2: { ... },
    hint1: '...', hint2: '...',
  },
}
```

### Critical LP rules (all types)
- Adapted worked examples MUST use different coordinates/shapes from questions
- Adapted versions have no going further — only hint boxes
- Word problem iCan statements: short, child-friendly, no jargon, no colons

---

## Authoring Lesson Data (lesson_data.py)

### Working Memory types by day

| Day | Type | Format |
|-----|------|--------|
| Mon | Numbers | [n1, n2, n3, ...] horizontal |
| Tue | Words | ['word1', 'word2', ...] horizontal |
| Wed | Emojis | ['🌟','🎯',...] sz=60 bottom-aligned horizontal |
| Thu | Sentences with emojis | vertical stack with Q&A |

### Spot the Mistake rules
- Always author BOTH c1_ido2 AND c2_ido2
- Generic title only: "Spot the mistake" (never reveals the answer)
- Prompting caption never reveals answer
- Explanation in speaker notes
- Wrong attempt uses `polygon_b_color: 'RED'`

### slide_type data structures

**`slide_type: 'column_calc'`** (arithmetic teaching)
```python
{
    'slide_type': 'column_calc',
    'calc': '6 × 4 =',            # calculation displayed left
    'context_lines': [             # context box right
        'There are 6 bags.',
        'Each bag holds 4 oranges.',
        'Signal word: "each" → equal groups → ×',
    ],
    'caption': '...',
    'notes': '...',
}
```

**`slide_type: 'grid_translate'`** (coordinate/translation)
```python
{
    'slide_type': 'grid_translate',
    'gridSize': 7,
    'squares_a': [(c, r), ...],
    'squares_b': [(c, r), ...],
    'mirror_col': 3,
    'points': [(col, row, 'Label', 'HexColor'), ...],
    'animate_labels': ['Label'],
    'caption': '...',
    'notes': '...',
}
```

**`slide_type: 'clock'`**
```python
{
    'clocks': [{'hour': H, 'minute': M, 'label': 'text', 'show_digital': False}],
    'caption': '...',
    'sentence_stem': '...',
    'notes': '...',
}
```

---

## Pre-flight Check

Runs automatically at end of every `build_lesson_v3.py` call.
Checks: text overflow, box height, out-of-bounds shapes, WM type rule.

- `✓ No layout issues detected` → proceed
- `⚠ N issue(s) found` → fix before delivering

---

## Key technical constants

| Constant | Value |
|----------|-------|
| Slide dimensions | 13.333" × 7.5" |
| Background colour | `DEECF8` |
| Border colour | `FFC000` |
| Accent colour | `156082` |
| Teaching panel | x=0.40" y=1.45" w=7.00" h=5.80" |
| Shape A colour | `1F4E79` (dark blue) |
| Shape B colour | `E8642A` (orange) |
| Mirror line colour | `7030A0` (purple) |
| Answer text colour | `1A5C2A` (green) |
| Display font | Twinkl Cursive Looped Light |
| Maths/label font | Aptos |
| LP slide size | 7.5" × 10.833" (A4 portrait) |
| LP cut line | y = 5.4165" (MID_Y) |
| LL_W | 9.7 × 0.72 × 0.85 × (1/2.54)" ≈ 2.337" |
| LL_H | 4.24 × 0.72 × 0.85 × (1/2.54)" ≈ 1.021" |

---

## File naming conventions

| File | Pattern |
|------|---------|
| Teaching PPTX | `{TxWy}_L{N}_{day}_Teaching.pptx` |
| LP PPTX | `{TxWy}_L{N}_{day}_LP.pptx` |
| Label sticker sheet | `{TxWy}_L{N}_{day}_Labels.docx` |
| Rapid Maths | `Rapid_Maths_{TxWy}.pptx` |
| Working Memory | `Working_Memory_{TxWy}.pptx` |
| Term plan JSON | `maths_plan_v{N}.json` |

---

## What Innes provides vs what Claude decides

**Innes provides:**
- Which week to build
- Plan updates (missed lessons, concepts to revisit)
- Rapid Maths topic selections
- LP type clarification if genuinely ambiguous

**Claude decides autonomously:**
- LP type (A or B) — ask only if genuinely ambiguous
- labelTopic mapping from lesson content
- Visual coordinate choices, clock times, symmetry patterns, number line markers
- WM sequences and Q&A questions
- RM questions (5 per lesson)
- Vocabulary definitions
- LP question difficulty progression
- iCan statements (short, child-friendly, no jargon)
- Scaffold aids for adapted slides

---

## Dependency files

All in `/mnt/skills/user/maths-complete-planning-and-resources/`:

| File | Role |
|------|------|
| `build_lesson_v3.py` | Teaching PPTX builder |
| `lesson_data.py` | Visual/WM/RM/vocab data |
| `build_lp_v3.js` | LP builder — `injectLabel()` for Type A, no LL for Type B; writes `labels_data.json` |
| `lesson_data.js` | LP question data |
| `inject_lp_previews.py` | Injects LP previews into teaching slides |
| `generate_labels.py` | Produces sticker DOCX for Type B lessons |
| `maths_plan_v3.json` | Term plan JSON (includes `labelTopic` per lesson) |
| `WFA_Labels_template.docx` | Reference sticker template (do not modify) |
| `assets/template_v3.pptx` | WFA slide template |
| `assets/key-question-new.pptx` | Key question cloud image source |
| `assets/LR_slide.pptx` | Learning review character/icon image source |
| `assets/mathematician_icon.png` | Icon for LP labels |
| `Working_Memory_Template.pptx` | WM starter template |
| `rapid_maths_TEMPLATE.pptx` | Rapid maths template |
| `rapid_maths_generator.py` | Rapid maths builder |
| `working_memory_starters.py` | Working memory builder |

---

## Saving updates

When data files or builders are modified, copy back to skill folder AND push to GitHub before ending the session:

```bash
SKILL=/mnt/skills/user/maths-complete-planning-and-resources

# Scripts
cp /home/claude/build_lesson_v3.py  $SKILL/
cp /home/claude/build_lp_v3.js      $SKILL/
cp /home/claude/lesson_data.py      $SKILL/
cp /home/claude/lesson_data.js      $SKILL/
cp /home/claude/inject_lp_previews.py $SKILL/
cp /home/claude/generate_labels.py  $SKILL/
cp /home/claude/transfer_files/maths_plan_v3.json $SKILL/

# Then run github-sync skill (push mode) to sync to imcl75/claude_files
```
