---
name: spelling-shed
description: >
  Generates a complete Spelling Shed lesson for Innes McLean's Year 4 class at WFA. Produces
  two PPTX files per lesson: (1) a 22-slide animated teaching deck built with pptxgenjs and a
  Python animation post-processor, and (2) a 2-slide LP (Learning Paper) built with lp_builder.py.
  Use this skill whenever Innes asks to prepare, plan, create or build a spelling lesson, spelling
  slides, or a Spelling Shed lesson for any spelling rule or pattern. Also trigger when he mentions
  spelling words, a spelling rule, or says things like "spelling for next week / this term /
  double consonant / suffix" etc.
---

# Spelling Shed Lesson Generator

Produces two files for every lesson:
- **`spelling_shed_slides_<CODE>_<Day>.pptx`** — 22-slide animated teaching deck (21 + key spelling slide)
- **`spelling_lp_<CODE>_<Day>.pptx`** — 2-slide LP (Learning Paper), half-A4 cut-and-fold format

**File naming rule (non-negotiable):** always include the day name — e.g. `spelling_shed_slides_CN_Mon.pptx`, `spelling_lp_CN_Mon.pptx`.

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
- Y→ILY → `ILY`, Doubling → `DC`, etc.

**Definitions** — `"When he, she or it [verb]; also, [noun use]."`

**Sentences** — Y4-appropriate, target word appears exactly once, replaceable by a blank.

**Phonemes** — read `references/phoneme-rules.md` before generating. Follow exactly.

**Word Maps words** — 6 of 10, best illustrating the pattern (prefer ≥2 syllables, visible digraphs).

**Word Sort** — two boxes. Adapt labels completely to the rule being taught.

**Spell Check variants** — 2 plausible misspellings per word. Randomise the correct-column position across rows.

**Cloze order** — `clozeOrder` is the order in which SENTENCES appear. It must be shuffled so no word sits in the same position as its entry in `words`. Verify this before writing the JSON.

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

**Restore templates from skill folder:**

```bash
python3 << 'EXTRACT'
import zipfile, os, shutil

skill_locations = [
    '/mnt/user-data/uploads/skill-spelling-shed.skill',
    '/mnt/skills/user/spelling-shed/skill-spelling-shed.skill',
]
skill_path = next((p for p in skill_locations if os.path.exists(p)), None)

if skill_path:
    with zipfile.ZipFile(skill_path) as z:
        ref = 'skill-spelling-shed/references/'
        files = {
            'slides-template.js':    'spelling_shed_slides_template.js',
            'animation-injector.py': 'add_animation.py',
            'inject_key_spelling.py':'inject_key_spelling.py',
        }
        for src_name, dest_name in files.items():
            data = z.read(ref + src_name)
            open(f'/home/claude/{dest_name}', 'wb').write(data)
            print(f"Extracted: {dest_name}")
        for asset in ['key_spelling_template.pptx', '1_min_timer.mp4']:
            open(f'/home/claude/{asset}', 'wb').write(z.read(ref + asset))
            print(f"Extracted: {asset}")
else:
    ref = '/mnt/skills/user/spelling-shed/references/'
    for src, dst in {
        'slides-template.js':    'spelling_shed_slides_template.js',
        'animation-injector.py': 'add_animation.py',
        'inject_key_spelling.py':'inject_key_spelling.py',
        'key_spelling_template.pptx':'key_spelling_template.pptx',
        '1_min_timer.mp4':       '1_min_timer.mp4',
    }.items():
        shutil.copy(ref + src, f'/home/claude/{dst}')
        print(f"Copied: {dst}")
EXTRACT
```

**Restore lp_builder.py from GitHub** (it is not in the skill zip — fetch from `imcl75/claude_files`):

```bash
# Read github-sync SKILL.md to get the token, then:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/imcl75/claude_files/contents/Spelling/lp_builder.py" \
| python3 -c "import sys,json,base64; d=json.load(sys.stdin); open('/home/claude/lp_builder.py','wb').write(base64.b64decode(d['content']))"
echo "lp_builder.py restored"
```

If the GitHub fetch fails, recreate lp_builder.py from scratch using the spec in **Appendix: LP Builder Spec** below.

Install dependencies if needed:
```bash
npm list -g pptxgenjs || npm install -g pptxgenjs
pip install python-pptx --break-system-packages -q
```

---

### Step 4 — Build

```bash
cd /home/claude

# Teaching deck
node spelling_shed_slides_template.js           # → spelling_shed_slides_<CODE>.pptx (21 slides)
python3 inject_key_spelling.py "WORD"           # → prepends key spelling slide → 22 slides
python3 add_animation.py                        # → animates slides 4–7, strips phantom CT entries

# LP
python3 lp_builder.py lesson.json              # → spelling_lp_<CODE>_<Day>.pptx (2 slides)
```

Skip `inject_key_spelling.py` only if no key spelling word was given.

---

### Step 5 — Verify, rename and deliver

```bash
python3 -c "
from pptx import Presentation
CODE = 'XX'   # replace
DAY  = 'Mon'  # replace
for f, exp in [
    (f'spelling_shed_slides_{CODE}.pptx', 22),
    (f'spelling_lp_{CODE}_{DAY}.pptx', 2),
]:
    p = Presentation(f)
    n = len(p.slides)
    print(f'{f}: {n} slides', '✓' if n==exp else f'✗ expected {exp}')
"

# Rename teaching deck to include day
mv spelling_shed_slides_<CODE>.pptx spelling_shed_slides_<CODE>_<Day>.pptx

cp spelling_shed_slides_<CODE>_<Day>.pptx /mnt/user-data/outputs/
cp spelling_lp_<CODE>_<Day>.pptx         /mnt/user-data/outputs/
```

---

## Critical rules — must be followed every build

### Cloze ordering (non-negotiable)

The cloze activity has two independent columns:

| Left column (word labels) | Right column (sentences) |
|--------------------------|--------------------------|
| Drawn from `words` in **original list order** | Drawn from `clozeOrder` (shuffled) |

**Never use `clozeOrder` for both columns.** If you do, every word sits next to the sentence it belongs to, making the activity trivial.

In `draw_cloze_half()`:
```python
label_words = lesson["words"]       # original order — for left column labels
sent_words  = lesson["clozeOrder"]  # shuffled order — for right column sentences
for i in range(len(label_words)):
    label    = label_words[i]
    sent_key = sent_words[i]
    ...
```

`clozeOrder` must be shuffled so no word sits in the same position as its entry in `words`. Verify before committing to JSON.

### File naming (non-negotiable)

Always include the day name in both output files:
- `spelling_shed_slides_CN_Mon.pptx`
- `spelling_lp_CN_Mon.pptx`

### LP vertical alignment

All text within row cells must use `anchor='ctr'` (vertical centre) — except definition text in DefMatch rows, which uses `anchor='t'` (top) to prevent multi-line wrap from bleeding outside the row boundary.

### LP definition length

Keep `lpDefinitions` entries short — max ~70 characters. At 9.5pt in a 1.056cm row, definitions longer than 2 wrapped lines will overflow.

---

## Reference Files

| File | Purpose | When to read |
|------|---------|--------------|
| `references/lesson-data-schema.md` | Full JSON schema + worked example | Step 2 — always |
| `references/phoneme-rules.md` | Sound button rules | Step 2 — before phonemes |
| `references/slides-template.js` | Teaching deck JS (reads `lesson.json`) | Step 3 — copy only |
| `references/animation-injector.py` | Post-processor for animations | Step 3 — copy only |
| `references/inject_key_spelling.py` | Prepends Key Spelling slide | Step 4 — if key word given |
| `references/key_spelling_template.pptx` | Template with embedded timer | Step 4 — read by inject script |
| `lp_builder.py` | LP PPTX generator (fetch from GitHub, not in skill zip) | Step 3 — fetch or recreate |

---

## Output Summary

| File | Slides | Notes |
|------|--------|-------|
| `spelling_shed_slides_<CODE>_<Day>.pptx` | 22 | Animated teaching deck. 22 slides = 21 base + 1 key spelling slide. |
| `spelling_lp_<CODE>_<Day>.pptx` | 2 | LP: Slide 1 = Side A (cloze), Slide 2 = Side B. Each slide = two identical half-A4 panels (cut line at 14.85cm). |

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
