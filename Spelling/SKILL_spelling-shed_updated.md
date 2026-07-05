---
name: spelling-shed
description: >
  Generates a complete Spelling Shed lesson for Innes McLean's Year 4 class at WFA. Produces
  two PPTX files per lesson: (1) a 23-slide animated teaching deck built with pptxgenjs and a
  Python animation post-processor, and (2) a 2-slide LP (Learning Paper) built with lp_builder.py.
  All files are packaged into a single zip with Teaching/ and LPs/ subfolders and renamed to the
  TxWy - N - Day - filename convention. Use this skill whenever Innes asks to prepare, plan, create
  or build a spelling lesson, spelling slides, or a Spelling Shed lesson for any spelling rule or
  pattern. Also trigger when he mentions spelling words, a spelling rule, or says things like
  "spelling for next week / this term / double consonant / suffix" etc.
---

# Spelling Shed Lesson Generator

Produces two files per lesson, packaged into a single zip for the whole week.

**Zip name:** `TxWy_Spelling.zip` (e.g. `T6W6_Spelling.zip`)

**Zip structure:**
```
T6W6_Spelling.zip
├── Teaching/
│   ├── T6W6 - 1 - Monday - spelling_shed_slides_EY.pptx
│   ├── T6W6 - 2 - Tuesday - spelling_shed_slides_DI.pptx
│   └── T6W6 - 3 - Wednesday - spelling_shed_slides_DE.pptx
└── LPs/
    ├── T6W6 - 1 - Monday - spelling_lp_EY.pptx
    ├── T6W6 - 2 - Tuesday - spelling_lp_DI.pptx
    └── T6W6 - 3 - Wednesday - spelling_lp_DE.pptx
```

**Naming convention:** `TxWy - N - [Full day] - [base filename].pptx`
- `TxWy` = stage from `lesson.json` (e.g. `T6W6`)
- `N` = lesson sequence within the week — 1 for the first lesson taught, 2 for the second, etc., regardless of which day that is
- `[Full day]` = full day name: Monday, Tuesday, Wednesday
- `[base filename]` = `spelling_shed_slides_<CODE>` or `spelling_lp_<CODE>`

**Deliver only the zip.** Never present individual files alongside it.

---

## Workflow

### Step 1 — Clarify the rule

The spelling rule should come from Innes's trigger message.

**If the rule is already clear:** move straight to Step 1b.  
**If not stated:** ask — *"What spelling rule would you like me to prepare a lesson for?"*

### Step 1b — Interview

Ask the following in a single message:

1. **What are the 10 spelling words?**  
   Add: *"Say 'suggest' and I'll propose a set for you to confirm."*
2. **Which day is this lesson?** (Mon / Tue / Wed — needed for the filename)
3. **Is there a Key Spelling word?** (a word from the class key list they are struggling with)
4. **Any specific preferences?** (Word Shed word, Morphology Matrix word, starter format) — *Claude chooses if none given.*

---

### Step 2 — Generate the LESSON object

Read `references/lesson-data-schema.md` for the full specification and worked example.

#### Standard fields

**Lesson code** — 2–3 uppercase letters derived from the rule:
- -cian words → `CN`
- Sorting -tion/-sion/-ssion/-cian → `C2`
- Mixed contrast all four → `C3`
- Y→ILY → `ILY`, Doubling → `DC`, -ous → `OU`, -ious/-eous → `IO`, -ge+ous → `GE`, etc.

**Definitions** — `"When he, she or it [verb]; also, [noun use]."`

**Sentences** — Y4-appropriate, target word appears exactly once, replaceable by a blank.

**Phonemes** — read `references/phoneme-rules.md` before generating. Follow exactly.

**Word Maps words** — 6 of 10, best illustrating the pattern (prefer ≥2 syllables, visible digraphs).

**Word Sort** — two boxes. Adapt labels completely to the rule being taught.

**Spell Check variants** — 2 plausible misspellings per word. Randomise the correct-column position across rows.

**Cloze order** — `clozeOrder` is the order in which SENTENCES appear. It must be shuffled so no word sits in the same position as its entry in `words`. Verify this before writing the JSON.

#### Critical JSON field rules (non-negotiable — causes broken slides if wrong)

**`starter.perPairNote`** — ALWAYS set to `""` (empty string). The same note appears on every word pair on the starter answers slide, making it repeat 6 times. Put any teaching note in `ruleBox` instead.

**`starter.words` / `starter.answers`** — pass key spelling word to `inject_key_spelling.py` in **lowercase** (e.g. `"favourite"` not `"FAVOURITE"`). The inject script uses literal string replacement.

**`wordSort.verbNoun`** — MUST be an array of `{word: string, eg: string}` objects, NOT plain strings. The template accesses `.word` and `.eg` on each item; plain strings produce "undefined" on the answers slide.

```json
"verbNoun": [
  {"word": "vigorous",  "eg": "vigour → vigorous"},
  {"word": "jealous",   "eg": "French: jalous"},
  {"word": "enormous",  "eg": "Latin: enormis"}
]
```

**`wordSort.verbOnly`** — plain string array (unchanged):
```json
"verbOnly": ["dangerous", "mountainous", "thunderous"]
```

**`wordMaps.syllables`** — use pipe `|` as the syllable break character, NOT hyphen `-`:
```json
"syllables": {
  "poisonous":  "poi|son|ous",
  "dangerous":  "dan|ger|ous",
  "enormous":   "e|nor|mous"
}
```

**`etymology.baseForm`** — keep to **≤12 characters**. This field is rendered at 26pt in a 2.5" box. Longer strings overflow visibly. Use just the root components: `"ē- + norma"`, `"cura"`, `"corage + -ous"`.

#### LP fields (required for lp_builder.py)

```json
"lpDay":            "Mon",           // "Mon" / "Tue" / "Wed"
"lpSideBType":      "vn_dm_sc",      // "vn_dm_sc" (Mon/Wed) or "sc_dm" (Tue)
"lpVerbNounName":   "Find the Root", // Title for VN section
"lpVerbNounInstr":  "Remove the suffix. Write the word or field it comes from.",
"lpVerbNoun": [                      // Exactly 6 pairs [shown, answer]
  ["musician",   "music"],
  ["politician", "politics"],
  ...
],
"lpDefMatchName":   "Match the Meaning",
"lpDefMatchInstr":  "Write the word that matches each meaning.",
"lpDefinitions":    [ ... ],         // Exactly 5 short definitions
"lpDefMatchAnswers":[ ... ]          // 5 answers matching lpDefinitions order
```

**Side B type rules:**
- `"vn_dm_sc"` — VerbNoun/FindRoot column (left, 6 rows) + DefMatch column (right, 5 rows) + SpellCheck full-width below
- `"sc_dm"` — SpellCheck full-width (top) + DefMatch full-width (bottom)

Assign `"vn_dm_sc"` to Mon and Wed; `"sc_dm"` to Tue — unless the lesson content makes a different assignment clearly better.

**VerbNoun section** — adapts to the rule:
- For -cian words: "Find the Root" / "Remove -cian or -ician. Write the word or field it comes from."
- For -ssion words: "Find the Base Verb" / "Remove the suffix. Write the base verb."
- For mixed endings (Wed): "Find the Root" / "Remove the suffix. Write the verb or base word it comes from."

**Definitions** — keep short enough to wrap to at most 2 lines in a 1.056cm row. Avoid definitions longer than ~70 characters.

---

### Step 3 — Write lesson.json and set up templates

Write `/home/claude/lesson.json` — generated fresh for this lesson. Do not reuse any values from previous lessons.

**Restore all scripts from GitHub** (all four are tracked in `imcl75/claude_files/Spelling/`):

```python
import re, os, urllib.request, urllib.parse

with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    skill_text = f.read()
TOKEN    = re.search(r'GITHUB_TOKEN:\s*(\S+)', skill_text).group(1)
RAW_BASE = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Spelling'

files = [
    'slides-template.js',
    'lp_builder.py',
    'animation-injector.py',   # → add_animation.py
    'inject_key_spelling.py',
    'post_process_spelling.py',
    'you_do_image.png',
]
dest_names = {
    'slides-template.js':    'spelling_shed_slides_template.js',
    'animation-injector.py': 'add_animation.py',
}

for fname in files:
    dest = dest_names.get(fname, fname)
    url  = f'{RAW_BASE}/{urllib.parse.quote(fname)}'
    req  = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=15) as r:
        open(f'/home/claude/{dest}', 'wb').write(r.read())
    print(f'Fetched {fname} → /home/claude/{dest}')
```

Also copy the key spelling template:
```python
import shutil
shutil.copy('/mnt/skills/user/spelling-shed/references/key_spelling_template.pptx',
            '/home/claude/key_spelling_template.pptx')
```

Install dependencies if needed:
```bash
npm list -g pptxgenjs || npm install -g pptxgenjs
pip install python-pptx lxml --break-system-packages -q
```

---

### Step 4 — Build

```bash
cd /home/claude

# Teaching deck
node spelling_shed_slides_template.js           # → spelling_shed_slides_<CODE>.pptx (21 slides)
python3 inject_key_spelling.py "word"           # → prepends key spelling slide → 22 slides
                                                #   IMPORTANT: pass word in lowercase, e.g. "favourite"
python3 add_animation.py                        # → animates slides 4–7, strips phantom CT entries

# Post-build additions (slide 10 animation + Independent Learning section slide)
python3 post_process_spelling.py <CODE>         # → animates slide 10, inserts section slide → 23 slides

# LP
python3 lp_builder.py lesson.json              # → spelling_lp_<CODE>_<Day>.pptx (2 slides)
```

Skip `inject_key_spelling.py` only if no key spelling word was given. `post_process_spelling.py` should always run.

---

### Step 5 — Verify, package and deliver

#### Verify slide counts

```python
from pptx import Presentation

# lessons = list of (code, day_short) for this build
lessons = [('EY', 'Mon'), ('DI', 'Tue'), ('DE', 'Wed')]  # example — adjust to actual

for code, day in lessons:
    for fname, exp in [
        (f'/home/claude/spelling_shed_slides_{code}_{day}.pptx', 23),
        (f'/home/claude/spelling_lp_{code}_{day}.pptx', 2),
    ]:
        p = Presentation(fname)
        n = len(p.slides)
        print(f'{fname}: {n} slides', '✓' if n == exp else f'✗ expected {exp}')
```

Also confirm no blank slides and no tiny files (<600 bytes):

```python
import zipfile, re

for code, day in lessons:
    path = f'/home/claude/spelling_shed_slides_{code}_{day}.pptx'
    from pptx import Presentation
    prs = Presentation(path)
    blank = [i+1 for i, s in enumerate(prs.slides) if len(s.shapes) == 0]
    if blank:
        print(f'  WARNING — blank slides in {code} {day}: {blank}')
    with zipfile.ZipFile(path) as z:
        tiny = [(n, len(z.read(n))) for n in z.namelist()
                if re.match(r'ppt/slides/slide\d+\.xml$', n) and len(z.read(n)) < 600]
        if tiny:
            print(f'  WARNING — tiny slide XML in {code} {day}: {tiny}')
```

#### Package into zip

```python
import zipfile, os, re
from pptx import Presentation

# Populate this from the actual build — code, short day, full day name, sequence number
# Sequence = 1 for first lesson taught that week, 2 for second, 3 for third, regardless of day
lesson_meta = [
    ('EY', 'Mon', 'Monday',    1),
    ('DI', 'Tue', 'Tuesday',   2),
    ('DE', 'Wed', 'Wednesday', 3),
]

# Get stage from the last lesson.json used (all lessons in a week share the same stage)
import json
with open('/home/claude/lesson.json') as f:
    stage = json.load(f).get('stage', 'TxWy')

zip_name  = f'{stage}_Spelling.zip'
zip_path  = f'/mnt/user-data/outputs/{zip_name}'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for code, day_short, day_full, seq in lesson_meta:
        prefix = f'{stage} - {seq} - {day_full}'
        
        teach_src = f'/home/claude/spelling_shed_slides_{code}_{day_short}.pptx'
        lp_src    = f'/home/claude/spelling_lp_{code}_{day_short}.pptx'
        
        if os.path.exists(teach_src):
            zf.write(teach_src, f'Teaching/{prefix} - spelling_shed_slides_{code}.pptx')
            print(f'  + Teaching/{prefix} - spelling_shed_slides_{code}.pptx')
        else:
            print(f'  MISSING: {teach_src}')
        
        if os.path.exists(lp_src):
            zf.write(lp_src, f'LPs/{prefix} - spelling_lp_{code}.pptx')
            print(f'  + LPs/{prefix} - spelling_lp_{code}.pptx')
        else:
            print(f'  MISSING: {lp_src}')

print(f'\nZip: {zip_path}')
```

Then call `present_files` with the zip path only. Never present individual PPTX files alongside it.

---

## Critical rules — must be followed every build

### Cloze ordering (non-negotiable)

The cloze activity has two independent columns:

| Left column (word labels) | Right column (sentences) |
|--------------------------|--------------------------|
| Drawn from `words` in **original list order** | Drawn from `clozeOrder` (shuffled) |

**Never use `clozeOrder` for both columns.** If you do, every word sits next to the sentence it belongs to, making the activity trivial.

`clozeOrder` must be shuffled so no word sits in the same position as its entry in `words`. Verify before committing to JSON.

### File naming (non-negotiable)

Working files in `/home/claude/` keep the short-form name (needed by scripts):
- `spelling_shed_slides_CN_Mon.pptx`
- `spelling_lp_CN_Mon.pptx`

Final names inside the zip follow the full convention:
- `Teaching/T6W2 - 1 - Monday - spelling_shed_slides_CN.pptx`
- `LPs/T6W2 - 1 - Monday - spelling_lp_CN.pptx`

Sequence numbers reflect the order lessons are taught that week — Mon=1, Tue=2, Wed=3 in a standard three-lesson week. If the first lesson is on Tuesday (e.g. after school closure), Tuesday gets sequence 1.

### LP vertical alignment

All text within row cells must use `anchor='ctr'` (vertical centre) — except definition text in DefMatch rows, which uses `anchor='t'` (top) to prevent multi-line wrap from bleeding outside the row boundary.

### LP definition length

Keep `lpDefinitions` entries short — max ~70 characters. At 9.5pt in a 1.056cm row, definitions longer than 2 wrapped lines will overflow.

---

## Template fixes (applied June 2026 — already in slides-template.js on GitHub)

The following fixes are baked into the current `slides-template.js`. **Do not revert them** when fetching from GitHub.

| Slide | Problem fixed | Fix applied |
|-------|--------------|-------------|
| Today's Words | Long words (e.g. "mountainous") wrapped onto next cell | Per-cell grid with `cellW * 0.82` fit + `shrinkText: true` |
| Syllable Count | Same wrapping issue | Per-cell grid with `cellW * 0.82` fit + `shrinkText: true` |
| Word Sort blank | Joined word string overflowed 9" width | Per-cell grid — same approach as Today's Words |

If for any reason the template is regenerated from scratch, these must be re-applied to the relevant slides.

---

## Reference Files

| File | Purpose | When to read |
|------|---------|--------------|
| `references/lesson-data-schema.md` | Full JSON schema + worked example | Step 2 — always |
| `references/phoneme-rules.md` | Sound button rules | Step 2 — before phonemes |
| `slides-template.js` → `spelling_shed_slides_template.js` | Teaching deck JS (reads `lesson.json`) | Fetch from GitHub at session start |
| `animation-injector.py` → `add_animation.py` | Animates slides 4–7 | Fetch from GitHub at session start |
| `inject_key_spelling.py` | Prepends Key Spelling slide | Fetch from GitHub at session start |
| `post_process_spelling.py` | Slide 10 animation + section slide | Fetch from GitHub at session start |
| `lp_builder.py` | LP PPTX generator | Fetch from GitHub at session start |
| `you_do_image.png` | Image for section slide | Fetch from GitHub at session start |
| `references/key_spelling_template.pptx` | Template with embedded timer | Copy from skill references |

---

## Output Summary

Deliver a single zip file. Never present individual PPTX files alongside it.

| Zip contents | Slides | Notes |
|---|---|---|
| `Teaching/TxWy - N - [Day] - spelling_shed_slides_<CODE>.pptx` | 23 | 21 base + 1 key spelling + 1 Independent Learning section slide |
| `LPs/TxWy - N - [Day] - spelling_lp_<CODE>.pptx` | 2 | Slide 1 = Side A (cloze), Slide 2 = Side B. Each slide = two identical half-A4 panels (cut line at 14.85cm). |

---

## Post-build additions (handled by post_process_spelling.py)

`post_process_spelling.py` runs after `add_animation.py` and applies two additions to the teaching deck:

### 1. Syllable & Phoneme Map — 2-click animation (slide 10)

Slide 10 shows the word headings, "Syllable Breaks" and "Sound Buttons" labels on load, with everything else hidden. Two click-advance groups reveal content:

- **Click 1** — all three words' syllable-break boxes and syllable counts appear simultaneously
- **Click 2** — all three words' phoneme-map shapes (letter tables, dots, lines) and legends appear simultaneously

**Implementation approach (Y-position classification):**

Shapes on slide 10 are classified by their Y coordinate in EMU:
- Y < 1,100,000 — frame shapes: skip
- "Syllable Breaks" / "Sound Buttons" label text and word heading text — always visible
- 2,200,000 ≤ Y ≤ 2,900,000 — syllable content (boxes + text + counts): **click 1**
- Y ≥ 3,150,000 — phoneme content (tables + dots + lines + legend): **click 2**

pptxgenjs creates duplicate IDs between `<p:sp>` shapes and `<p:graphicFrame>` (table) elements. **Renumber graphicFrame IDs to unique values** before building the timing XML, otherwise PowerPoint cannot target them.

The `<p:bldLst>` block with `animBg="1"` on every animated shape ID hides shapes on load. Root `<p:cTn>` must have `restart="never"`. `<p:cond delay="indefinite"/>` (no `evt` attribute) triggers each group on click advance.

### 2. Independent Learning section slide (insert after slide 10)

Inserted after the Syllable & Phoneme Map worked examples, before independent activities begin.

```
Sky-blue rectangle:   L=0  T=0     W=25.4  H=9.14  fill=#87CEEB
White rectangle:      L=0  T=8.38  W=25.4  H=5.91  fill=#FFFFFF
Green footer:         L=0  T=13.72 W=25.4  H=0.57  fill=#57A657
"Independent Learning": 64pt bold #F4C430, centred, L=0.4 T=0.38 W=24.55 H=3.56
"You do" image:       L=8.18 T=4.41 W=8.4 H=3.49  (you_do_image.png)
"Learning Paper":     18pt #1A1A1A centred, L=8.0 T=8.5 W=9.4 H=0.9
"Today's words: ...": 17pt #1A1A1A centred, lesson words joined by ", ", L=1.27 T=10.5 W=22.86 H=1.9
```

Inserting this slide requires: renaming slides 11+ to 12+, adding a new slide11.xml, updating `presentation.xml` sldIdLst, `ppt/_rels/presentation.xml.rels`, and `[Content_Types].xml`.

### Slide terminology

| Slide label | Text to use |
|-------------|-------------|
| `thisWeeksWords` slide header | **"Today's Words"** (not "This Week's Words") |
| Subtitle questions on Etymology, Syllable Count | "today's words" (lower case) |
| Section slide word list | "Today's words:  [list]" |
| Key Spelling slide | unchanged |

The `thisWeeksWordsQ / Prompt / Explanation` JSON fields keep their names (for backward compatibility) but their values should say "today's words" not "this week's words".

---

## Appendix: LP Builder Spec

Use this if `lp_builder.py` cannot be fetched from GitHub. Recreate the file to match these exact specifications.

### Slide dimensions
- A4 portrait: 21.0 × 29.7 cm
- Cut line: T = 14.85cm (horizontal rule)
- Two identical half-A4 panels per slide: offset=0 (top) and offset=15.1 (bottom)

### Palette
- BLACK `#000000`, GREY `#BBBBBB`, LGREY `#F2F2F2`, DKTEXT `#222222`, MIDGR `#666666`, WHITE `#FFFFFF`

### Header block (per half, at offset)
```
Title:     L=0.45  T=0.25+offset  W=13.668  H=0.5    9.5pt bold
Code·Day:  L=14.118 T=0.25+offset  W=6.432   H=0.5    9.5pt bold  align=RIGHT
Name:      L=0.45  T=0.75+offset  W=12.663  H=0.46   9.0pt
Date:      L=13.113 T=0.75+offset  W=7.437   H=0.46   9.0pt
Black rule:L=0.45  T=1.21+offset  W=20.1    H=0.02   fill=BLACK
```

### Cut line
```
Text "✂  cut here":  L=9.0  T=14.65  W=3.0  H=0.36  6.5pt  colour=GREY  align=CENTRE
Rule:                L=0.0  T=14.85  W=21.0 H=0.02  fill=GREY
```

### Side A — Cloze (Slide 1)
```
Instruction: L=0.45 T=1.31+off W=20.1 H=0.46  10pt bold
Grey rule:   L=0.45 T=1.77+off W=20.1 H=0.02  fill=GREY
Outer box:   L=0.45 T=1.84+off W=20.1 H=12.83 line=0.5pt GREY
Divider:     L=2.85 T=1.84+off W=0.02 H=12.83 fill=GREY

10 rows, ROW_H=1.283cm:
  row_top = 1.84 + i*1.283 + offset
  Separator (i>0): L=0.45 T=row_top W=20.1 H=0.02 fill=GREY
  Alt background (i odd): L=0.45 T=row_top W=20.1 H=1.283 fill=LGREY
  Word label:  L=0.63 T=row_top W=2.04 H=1.283  10.5pt bold (8.5pt if len>10)  v_anchor='ctr'
  Sentence:    L=3.03 T=row_top W=17.42 H=1.283  11pt  colour=DKTEXT  v_anchor='ctr'

CRITICAL — word labels and sentences use DIFFERENT source arrays:
  label_words[i] = lesson["words"][i]          ← original list order
  sent_key[i]    = lesson["clozeOrder"][i]      ← shuffled order
```

### Side B — vn_dm_sc (Slide 2, Mon/Wed)
```
Section headers at T=1.31+offset, two columns (L=0.45 and L=10.65, each W=9.9):
  Title:  H=0.36  10pt bold
  Instr:  H=0.28  8.5pt  colour=MIDGR
  Rule:   H=0.02  fill=GREY
  Box starts at T=1.31+0.66=1.97+offset ≈ T=2.02

VN box (left):  L=0.45  T=2.02+off  W=9.9  H=5.28 (6 rows × 0.88)  line=0.5pt GREY
VN divider:     L=3.45  T=2.02+off  W=0.02 H=5.28  fill=GREY
VN rows (ROW_H=0.88): word at L+0.14 W=2.72 10.5pt bold v_anchor='ctr';
                       arrow "→" at L+3.14 W=0.75 10.5pt MIDGR v_anchor='ctr'

DM box (right): L=10.65 T=2.02+off  W=9.9  H=5.28 (5 rows × 1.056)  line=0.5pt GREY
DM rows (ROW_H=1.056):
  Number: L+0.1  W=0.6  9.5pt bold   v_anchor='ctr'
  Def:    L+0.75 W=5.84 9.5pt DKTEXT v_anchor='t'   ← TOP anchor, not centre
  (right ~40% is implicit writing space)

SC separator: T = 2.02 + 6*0.88 + 0.1 = 7.40 + offset
SC section header: same pattern as above (10pt bold title, 8.5pt instr)
SC box: T = SC_sep + 0.76 + offset, W=20.1, H=6.46 (5 rows × 1.292)

SC rows (ROW_H=1.292):
  Number: L=0.55 W=0.5 9.5pt bold v_anchor='ctr'
  3 option boxes: W=6.3867 H=1.132 each, at X=[1.09, 7.5567, 14.0233]
    Box: fill=WHITE line=0.5pt GREY
    Text: L=bx+0.12 W=6.2467 10.5pt DKTEXT v_anchor='ctr'
```

### Side B — sc_dm (Slide 2, Tue)
```
SC section at T=1.31+offset (same header pattern as above)
SC box: T=1.97+offset H=6.46 (5 rows × 1.292)

DM separator: T = 1.97 + 6.46 + 0.1 + offset
DM header: same pattern (10pt bold, 8.5pt instr)
DM box: T = DM_sep + 0.76 + offset, W=20.1, H=5.28 (5 rows × 1.056)
DM rows (full width): number at L=0.55; def text at L=1.15 W=12.06 v_anchor='t'
```
