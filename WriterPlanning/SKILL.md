---
name: writer-planning-overview-and-lesson-sequence
description: "Plan a full writing/author/writer enquiry unit for Year 4. Use this skill whenever Innes says \"plan my writing enquiry\", \"plan a writer enquiry\", \"plan an author enquiry\", \"plan a writing unit\", \"plan a writing sequence\", or anything similar. Also trigger when he says \"I need to plan writing for next term/week/unit\" or uploads a new book and mentions writing. Produces TWO outputs: (1) a PPTX summary in the school's planning format and (2) a detailed DOCX with lesson-by-lesson I Do / We Do / You Do breakdown and Learning Objectives per lesson. Always use this skill — do not produce ad hoc planning tables instead."
---

# Personal Writing Sequence Planner

## Purpose

Produces two complementary planning documents for a Year 4 writing/author/writer enquiry unit at Wallscourt Farm Academy:

1. **PPTX Summary** — matches the school's exact planning format: phases (Immerse / Have-a-Go / Challenge), lesson sequence grid, writing skills differentiation table (A/Y/O/D), and unit metadata (Key Question, Challenge outcome, Purpose, Audience).
2. **DOCX Detailed Plan** — lesson-by-lesson breakdown with Learning Objectives (WALT / Why / I will show this by) and I Do / We Do / You Do structure, with a Resources section per lesson.

---

## Step 1: Gather Inputs via Dialogue

Do NOT assume any inputs. Ask Innes for the following, grouped logically. Ask all at once to avoid back-and-forth:

```
To plan your writing enquiry, I need a few details:

1. The text — title and author
2. Number of lessons — how many in the full sequence?
3. Writing foci — what are the main writing skills? (e.g. dialogue punctuation, figurative language, cohesion)
4. Key question — the enquiry question framing the unit (I can suggest one if needed)
5. Final outcome / Challenge — what will children produce?
6. Audience and purpose — who is the writing for, and what is its purpose?
7. NC links — specific objectives to flag? (I can infer these if you prefer)
8. Why this text? — short rationale (optional)
9. Any known lesson content — specific ideas for lessons, or generate the full sequence?
```

Once inputs are gathered, **propose Key Question, Challenge outcome, and NC links** if not provided, and ask Innes to confirm before continuing.

---

## Step 2: Plan the Lesson Sequence

### Phase Structure

Every unit uses exactly three phases in this order:

| Phase | Purpose | Typical split (14-lesson unit) |
|-------|---------|-------------------------------|
| **Immerse** | Exploring the text; reading for writing; building vocabulary and understanding | L1–4 (4 lessons) |
| **Have-a-Go** | Practising new and prior writing skills in shorter focused tasks | L5–7 (3 lessons) |
| **Challenge** | Extended independent writing; edit and revise; share and reflect | L8–14 (7 lessons) |

For a 14-lesson unit the typical split is **4 + 3 + 7**. Adjust proportionally for other lengths (e.g. 10-lesson unit: 3+3+4).

### Lesson Content Principles

- Each lesson has a single, clear Learning Focus (LF)
- Immerse: text exploration, reading like a writer, vocabulary, text features, initial skill identification
- Have-a-Go: one focused skill per lesson, modelled → guided → independent practice
- Challenge: model text analysis (1 lesson), planning (1), writing (2–3, max 3 per school guidance), editing/revising (1), sharing and reflection (1)
- **No best-copy / publishing lesson** — this is not a good use of learning time. The final lesson is sharing and reflection only.
- **I Do / We Do / You Do** is NOT rigidly linear:
  - May start with You Do (cold task, diagnostic, exploratory discussion)
  - May cycle multiple times within one lesson
  - You Do may be collaborative — this supports access
  - Label clearly when sequence varies: "You Do (first)", "We Do (sharing)", "You Do (editing)", etc.

---

## Step 3: Generate PPTX Summary

Read `/mnt/skills/public/pptx/SKILL.md` before starting.

### CRITICAL: Use the Template — Do NOT Build from Scratch

The school's planning PPTX uses theme colours, specific table structures, images and fonts that cannot be reliably reproduced from scratch. Always use the template approach:

1. Ask Innes for a previous planning PPTX to use as a template, or use one from context if available
2. Unpack: `python3 scripts/office/unpack.py template.pptx unpacked/`
3. Edit `ppt/slides/slide1.xml` to update content
4. Repack: `python3 scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

If no template is available, proceed with python-pptx but flag that the output will differ visually from the school format.

### Slide Structure (landscape, 9906000 × 6858000 EMU / ~10.83" × 7.50")

#### A. Unit Metadata Table (Table 10)
- Position: (216198, 52745) EMU | Size: 7463065 × 961651 EMU
- 4 rows × 2 cols | Col widths: [1682752, 5780313]
- Rows: Key Question / Challenge / Purpose (of writing) / Audience (of writing)

#### B. Writing Skills Differentiation Table (Table 1)
- Position: (220980, 1083860) EMU | Size: 9436646 × 2895600 EMU
- 7 rows × 5 cols | Col widths: [1701437, 1589863, 2089509, 1905000, 2150837]
- Row 0: "Writing Skills / Taken from the Writing Framework" header
- Row 1: column labels (blank | A | Y | O | D)
- Rows 2+: one row per writing focus with A/Y/O/D descriptors
- A = At an Earlier Stage | Y = Yet to be on track | O = On track | D = Greater Depth

#### C. Phase Label Table (Table 27)
- Position: (1371915, 3979460) EMU | Size: 8285712 × 153822 EMU
- 1 row × 5 cols | Phase labels at cols 0, 2, 4: Immerse / Have-a-Go / Challenge

#### D. Lesson Sequence Grid (Table 6)
- Position: (216198, 3930923) EMU | Size: 9435706 × 2898596 EMU
- 4 rows × 6 cols | Col widths: [1677847, **116840** (thin divider), 1782990, 2002972, 2088928, 1766129]
- Row 0: "Lesson Sequence" header
- Rows 1–3: lessons per the grid below

**Lesson grid layout (col 1 is a thin visual divider ~0.13"):**

| | Col 0 | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 |
|---|---|---|---|---|---|---|
| Row 1 | L1 | *(divider)* | L2 | L3 | L4 | *(empty)* |
| Row 2 | L5 | L6 | *(empty)* | L7 | L8 | L9 |
| Row 3 | L10 | L11 | *(empty)* | L12 | L13 | L14 |

**Phase fill colours (exact hex from school template):**
- Immerse (L1–4): `F2CFEE` (pink/lilac)
- Have-a-Go (L5–7): `DAF2D0` (light green)
- Challenge (L8–14): `CAEFFB` (light blue)

**Each lesson cell text:**
```
Lesson [N]             ← u="sng" (underlined), sz=800
LF: [To...]            ← u="none", sz=800
[1–2 sentence summary] ← u="none", sz=800
```
All runs: `b="0"`, `i="0"`, `lang="en-GB"`, `schemeClr val="tx1"`

**Merging / splitting cells:** Use `gridSpan="N"` to span columns; `hMerge="1"` as placeholder. To split a merged cell, remove `gridSpan` and replace `hMerge` with a proper `<a:tc>` element.

---

## Step 4: Generate DOCX Detailed Plan

Read `/mnt/skills/public/docx/SKILL.md` before writing any code.
Use the `docx` npm package (Node.js): `npm install docx`.

### Page Setup
Landscape A4 in docx-js: `width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE`.
Margins: 720 DXA (0.5") each side → content width ≈ 15398 DXA.

### Section 1: Unit Overview Table

| Field | Content |
|-------|---------|
| Text | Title and author |
| Key Question | [value] |
| Final Outcome | [value] |
| Writing Foci | Numbered list with bullet sub-skills |
| NC Links | Bulleted objectives |
| Why This Text? | Short rationale |
| Phase Structure | Immerse (L1–X) / Have-a-Go (LX–Y) / Challenge (LY–end) with one-line description each |
| Duration | X weeks / Y lessons |
| Teacher Note | ⚠ Model text must be prepared in advance for the Challenge analysis lesson |

### Section 2: Lesson Plans

For each lesson:

```
[Lesson heading — dark blue, with phase badge]

LO table (3 rows × 2 cols):
  We are learning to:         | [WALT — specific, starts with a verb]
  We are learning this because| [1–2 sentences, links to final outcome or real purpose]
  I will show this by:        | [observable — visible in the book or on the page]

Overview paragraph (2–3 sentences)

Lesson detail table (3 cols: Phase | Activity | Teacher notes)
  Phase labels: I Do / We Do / You Do / You Do (first) / etc.

Resources table (2 cols: Teaching resources | Independent task resources)
```

### Phase Badge Colours (DOCX only)
- Immerse: fill `D5E8D4`, text `1A5C1A`
- Have-a-Go: fill `FFF2CC`, text `7D5C00`
- Challenge: fill `DAE8FC`, text `0D3D91`

---

## Step 4b — Fix OOXML issues (prevents PowerPoint repair dialog)

The unpack/repack approach manipulates the PPTX ZIP directly. This introduces OOXML problems that trigger PowerPoint's repair dialog: non-standard media filenames, notesSlide back-references, empty `<a:r>` runs, and a missing theme2.xml. Run this after repacking, before presenting.

```python
import re, urllib.request, os, subprocess

with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)

if not os.path.exists('/home/claude/fix_pptx_ooxml.py'):
    url = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/fix_pptx_ooxml.py'
    req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=20) as r:
        open('/home/claude/fix_pptx_ooxml.py', 'wb').write(r.read())

# Replace output.pptx with the actual repacked filename
subprocess.run(['python3', '/home/claude/fix_pptx_ooxml.py', '/home/claude/output.pptx'], check=True)
```

---

## Step 5: Present Outputs

Use `present_files` to share both files. Briefly note:
- Phase split used (e.g. "Immerse: L1–4, Have-a-Go: L5–7, Challenge: L8–14")
- Writing foci covered
- Any assumptions made for review

---

## School Reference

| Term | Meaning |
|------|---------|
| LF | Learning Focus = Learning Objective |
| Immerse | Phase 1 — exploring text, reading for writing |
| Have-a-Go | Phase 2 — practising individual skills in shorter tasks |
| Challenge | Phase 3 — extended write, edit, share and reflect (no publishing) |
| A | At an Earlier Stage (1+ year below Y4) |
| Y | Yet to be on track (securing Y3, working into Y4) |
| O | On track (within Y4 curriculum) |
| D | Greater Depth (applying Y4 skills with confidence) |
| WALT | We Are Learning To |
| I/We/You Do | Gradual release model — not always linear |

## Notes

- Writing unit runs alongside Being a Reader lessons — planned separately
- Model text for Challenge analysis lesson must be teacher-written — flag prominently in both outputs
- Lessons typically 45–60 minutes
- Max 3 "write" lessons in Challenge phase (school guidance)
- Editing/revising may be distributed across Challenge lessons
- **Final lesson = sharing and reflection only. No best copy.**