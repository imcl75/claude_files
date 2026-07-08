---
name: writing-lesson-pptx
description: >
  Generates Year 4 writing lesson PowerPoint slides for Wallscourt Farm Academy
  in the exact school template format. Use this skill whenever Innes asks to
  "make lesson slides", "build lesson [N]", "create the writers slides",
  "make my writing lesson for [topic]", or provides a writing sequence planning
  document and wants lesson slides. Also trigger when he says things like "next
  lesson" or "lesson 3 slides" in the context of an ongoing writing unit.
  Always use this skill — do not attempt to build writing lesson slides ad hoc.
---

# Writing Lesson PPTX Skill

Produces fully formatted writing lesson slide decks for WFA Year 4 in the
exact school template established through the I Want My Hat Back unit (T5W1).

Assets stored in `assets/`:
- `writing_lesson_base.pptx` — pre-patched base PPTX (all layouts corrected,
  invisible timer placeholders in all layouts, school master styling)
- `kc_wheel.png` — hi-res Key Concepts "Being a Writer" wheel slide image

Build script: `scripts/build_lesson.py`

---

## Trigger

Use when Innes provides a writing sequence planning document (`.docx`) and
asks to build one or more lesson slide decks from it. He may ask for a single
lesson, a few lessons, or specify lesson numbers explicitly.

---

## Step 1 — Gather inputs

Ask for anything not already provided:

| Input | How to get it |
|-------|--------------|
| Planning document (`.docx`) | Already uploaded, or ask |
| Which lesson(s) to build | Ask: "Which lesson(s) would you like — e.g. lesson 2, or lessons 2 and 3?" |
| Term and week reference | Ask: "What's the term and week? (e.g. T5W1)" — infer from filename if obvious |
| Book cover image | Fetch automatically from GitHub (`Writing/assets/book_cover.*`). Only ask for upload if the fetch fails (e.g. new unit where planning skill has not yet run). |
| Carry-over slides | Ask: "Are there any slides from a previous lesson that need to appear in this one? If so, please upload the PPTX they come from and tell me which slide." |

Do not proceed to Step 2 until you have the planning doc, lesson number(s),
and term/week reference. Book cover is fetched automatically (see Step 6). Carry-over slides are optional.

---

## Step 2 — Parse the planning document

Read the `.docx` using `pandoc`:

```bash
pandoc <uploaded.docx> -o /home/claude/plan.md && cat /home/claude/plan.md
```

Extract for each requested lesson:
- **Focus / learning objective** (the lesson's main skill)
- **Activities** (Hook, Revisit, Teach, Practise, Challenge sections)
- **Resources listed**

The planning doc table rows follow this pattern:

| Lesson | Focus | Activities | Resources |
|--------|-------|------------|-----------|

---

## Step 2a — Generate a context image

After parsing the planning doc, generate one AI image to use as a context or hook slide. This runs automatically — do not ask Innes whether to do it.

### Decision rule

| Content type | Tool to use |
|---|---|
| Scientific diagrams, particle diagrams, circuit diagrams, labelled anatomy, states of matter, sound waves, food chains, structural cross-sections | dall-e MCP (`generate_ai_image`) |
| Atmospheric scene-setting, real-world environments, historical moments, characters in context, book-themed illustrations, natural landscapes | Higgsfield MCP (`generate_image`, model: `nano_banana_pro`, aspect ratio: `16:9`) |

Writing lessons are almost always book-themed or character-driven → default to Higgsfield unless the lesson focus is explicitly a science diagram or labelled structure.

### Prompt construction

Build the prompt from the book title, lesson focus and the intended slide purpose. Aim for something that would work as a full-slide background or a large visual hook. Examples:

- Lesson on speech punctuation in a forest-themed book: *"a fox and a bear in a woodland clearing, early morning light filtering through trees, children's storybook illustration style, warm and inviting, white background"*
- Lesson on descriptive writing about a city: *"a busy Victorian street market at dusk, warm gaslight glow, cinematic wide shot, painterly illustration style"*

### Download and store

After generation, download the image to `/home/claude/context_image.png`:

```bash
curl -L -o /home/claude/context_image.png "<image_url_from_tool>"
```

This image is available for embedding via the `context_image` slide type in Step 5.

### context_image slide type

Add a `context_image` slide entry to the JSON immediately after the LO slide (position 4):

```json
{"type": "context_image",
 "image_path": "/home/claude/context_image.png",
 "caption": "Short optional caption — omit if the image speaks for itself"}
```

If image generation fails for any reason, skip silently and continue without it — do not block the build.

---

## Step 3 — Determine the day/time

Lessons follow this fixed weekly schedule (repeat for week 2):

| Lesson | Day/Session |
|--------|-------------|
| 1 | Monday AM |
| 2 | Tuesday AM |
| 3 | Tuesday PM |
| 4 | Wednesday AM |
| 5 | Thursday AM |
| 6 | Friday AM |
| 7 | Friday PM |
| 8 | Monday AM |
| (continues...) | |

---

## Step 4 — Design the slide sequence

Every lesson deck follows this **fixed structure**:

```
1.  Cover slide           (school enquiry cover — day/time shown)
2.  Key Concepts slide    (fixed Being a Writer wheel — never changes)
3.  LO slide              (3-panel: I am learning to / This is so / I will be successful by)
4.  Grammar Warm-Up       (You Do — 3-card activity linked to lesson focus)
5+. Teaching slides       (mix of We Do, I Do, You Do as plan dictates)
    → book page placeholders where the teacher shows a page spread
    → carry-over reference slides if applicable (e.g. checklist from prior lesson)
N.  Learning Review       (3 speech-bubble questions)
```

### Slide type rules

**Cover** — Always slide 1. Day/session from table above.

**Key Concepts** — Always slide 2. Uses `assets/kc_wheel.png`. No timer needed
(full-slide image).

**LO slide** — Always slide 3. Three panels:
- WAL ("I am learning to…"): verb phrase, child-facing, ≤85 chars
- TIB ("This is so…"): why it matters, ≤100 chars  
- ISB ("I will be successful by…"): observable task starting with -ing verb, ≤110 chars

**Grammar Warm-Up** — Always slide 4. You Do badge. Three cards (A/B/C or 1/2/3).
Each lesson should have a DIFFERENT warm-up FORMAT from the previous lesson —
do not repeat A/B/C spot-the-speech vs Fix-It vs True/False in consecutive lessons.
Keep it tightly linked to the lesson's grammar focus.

**Teaching slides** — derive from the lesson activities. Map like this:

| Activity type | Slide type |
|--------------|------------|
| Teacher models / explains explicitly | `i_do` |
| Whole class discussion / shared analysis | `we_do` |
| Pairs/trios task | `you_do_trio` |
| Independent practice | `you_do` |
| Show book page | `book_page` |
| Reference slide from prior lesson (checklist etc.) | `rules` |

**Book page slides** — placeholder slides (blank layout). Label clearly:
e.g. `"Bear and Fox — display the double-page spread"`.

**Carry-over slides** — if Innes uploads a prior lesson PPTX and says "include
slide 30" (for example), extract that slide's raw XML and pass it as a `rules`
type slide. Strip the slide number from the source; keep content verbatim.

**Learning Review** — always last slide. Three questions in speech bubbles.
Write questions that:
- Q1 (orange): reflect on a challenge or difficulty from today
- Q2 (blue): deepen understanding of the concept
- Q3 (green): connect to their own writing/learning

---

## Step 5 — Build the slides JSON

Compose the slide specification as a JSON list. Example for a speech
punctuation lesson:

```json
[
  {"type": "cover",  "day": "Tuesday AM"},
  {"type": "kc"},
  {"type": "lo",
   "wal": "write speech using inverted commas, capital letters and correct end punctuation",
   "tib": "I can punctuate dialogue accurately so that my writing is clear for the reader.",
   "isb": "converting dialogue from the book into correctly punctuated direct speech."},
  {"type": "warmup",
   "title": "Grammar Warm-Up",
   "subtitle": "What is the mistake? Can you spot the error in each sentence?",
   "cards": [
     {"label": "Sentence 1", "lines": ["\"have you seen my hat?\" asked the bear.", "", "Spot the error!"]},
     {"label": "Sentence 2", "lines": ["\"Have you seen my hat? asked the bear.", "", "Spot the error!"]},
     {"label": "Sentence 3", "lines": ["\u201cHave you seen my hat\u201d? asked the bear.", "", "Spot the error!"]}
   ]},
  {"type": "we_do",
   "title": "Let\u2019s remind ourselves\u2026",
   "lines": [
     "Klassen doesn\u2019t use inverted commas in his book,",
     "but when we write speech, we always need them.",
     "",
     "Here is the Bear and Fox conversation from the story:",
     "",
     "Have you seen my hat?",
     "No. I have not seen any hats around here.",
     "OK. Thank you anyway.",
     "",
     "What needs to change before this counts as correctly written speech?"
   ]},
  {"type": "book_page", "label": "Bear and Fox"},
  {"type": "i_do",
   "title": "Adding speech punctuation",
   "left_label": "Klassen\u2019s text (no inverted commas)",
   "left_lines":  ["Have you seen my hat?", "", "No. I have not seen any hats around here.", "", "OK. Thank you anyway."],
   "right_label": "With speech punctuation",
   "right_lines": ["\u201cHave you seen my hat?\u201d asked the bear.", "", "\u201cNo. I have not seen any hats around here,\u201d", "replied the fox.", "", "\u201cOK. Thank you anyway,\u201d said the bear."]},
  {"type": "we_do",
   "title": "Let\u2019s convert this together.",
   "lines": ["Convert the Bear and Turtle conversation into correctly punctuated direct speech.",
             "", "Have you seen my hat?",
             "I haven\u2019t seen anything all day. I have been trying to climb this rock.",
             "Would you like me to lift you on top of it?",
             "Yes, please.", "", "Think: who is speaking each time? What punctuation is needed?"]},
  {"type": "book_page", "label": "Bear and Turtle"},
  {"type": "we_do",
   "title": "How did we do?",
   "lines": ["\u201cHave you seen my hat?\u201d asked the bear.", "",
             "\u201cI haven\u2019t seen anything all day. I have been trying to climb this rock,\u201d said the turtle.", "",
             "\u201cWould you like me to lift you on top of it?\u201d asked the bear.", "",
             "\u201cYes, please,\u201d said the turtle."]},
  {"type": "you_do_trio",
   "lines": ["Convert the Bear and Snake conversation into correctly punctuated direct speech.", "",
             "Have you seen my hat?",
             "I saw a hat once. It was blue and round.",
             "My hat doesn\u2019t look like that. Thank you anyway.", "",
             "Remember to:", "  \u2022  add inverted commas around what is said",
             "  \u2022  use a capital letter at the start of speech",
             "  \u2022  put punctuation inside the closing inverted comma",
             "  \u2022  add a reporting clause to show who is speaking", "",
             "Peer check: swap with your partner and check using the speech punctuation checklist."]},
  {"type": "book_page", "label": "Bear and Snake"},
  {"type": "you_do",
   "title": "Now try on your own.",
   "lines": ["Have you seen my hat?", "I saw a hat once. It was blue and round.",
             "My hat doesn\u2019t look like that. Thank you anyway."],
   "challenge": "choose a different speech verb for each line \u2014 not just \u2018said\u2019."},
  {"type": "learning_review",
   "q1": "Which speech punctuation rule did you find trickiest today?",
   "q2": "How does using inverted commas help the reader?",
   "q3": "Which piece of speech you wrote today are you most pleased with?"}
]
```

Save the JSON to `/home/claude/slides.json`.

---

## Step 6 — Run the build script

Copy assets to working directory:

```bash
SKILL_DIR="/mnt/skills/user/writing-lesson-pptx"
cp "$SKILL_DIR/assets/writing_lesson_base.pptx" /home/claude/
cp "$SKILL_DIR/assets/kc_wheel.png" /home/claude/
```

Fetch the book cover from GitHub (saved there by the planning skill):

```python
import re, urllib.request, os, json, base64, glob

with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)

# Read manifest to find the correct extension
manifest_url = 'https://raw.githubusercontent.com/imcl75/claude_files/main/Writing/assets/book_cover_manifest.txt'
req = urllib.request.Request(manifest_url, headers={'Authorization': f'token {TOKEN}'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        github_path = r.read().decode().strip()  # e.g. Writing/assets/book_cover.jpg
    ext = os.path.splitext(github_path)[1]
    cover_url = f'https://raw.githubusercontent.com/imcl75/claude_files/main/{github_path}'
    req2 = urllib.request.Request(cover_url, headers={'Authorization': f'token {TOKEN}'})
    with urllib.request.urlopen(req2, timeout=15) as r:
        cover_bytes = r.read()
    cover_local = f'/home/claude/book_cover{ext}'
    with open(cover_local, 'wb') as f:
        f.write(cover_bytes)
    print(f"Book cover fetched from GitHub: {cover_local} ({len(cover_bytes)//1024}KB)")
except Exception as e:
    # Fallback: use most recently uploaded image file
    print(f"GitHub fetch failed ({e}), falling back to uploads folder.")
    candidates = sorted(
        glob.glob('/mnt/user-data/uploads/*.jpg') +
        glob.glob('/mnt/user-data/uploads/*.jpeg') +
        glob.glob('/mnt/user-data/uploads/*.png'),
        key=os.path.getmtime, reverse=True
    )
    if not candidates:
        raise FileNotFoundError("No book cover found — please upload the book cover image.")
    cover_local = candidates[0]
    print(f"Using uploaded cover: {cover_local}")
```

Run the build:

```bash
python3 "$SKILL_DIR/scripts/build_lesson.py" \
  --base    /home/claude/writing_lesson_base.pptx \
  --kc      /home/claude/kc_wheel.png \
  --cover   $cover_local \
  --term    <N>  \
  --week    <N>  \
  --lesson  <N>  \
  --topic   "<ShortTopic>"  \
  --out     /home/claude \
  --slides-json /home/claude/slides.json
```

The script prints `OUTPUT: <path>`. Note the path — you need it for the next step.

---

## Step 6a — Fix OOXML issues

The build script manipulates the PPTX as a raw ZIP (unzip → edit XML → repack). This can
leave non-standard media filenames inherited from the WFA template (e.g. `conn_col.emf`,
`conn_icon.png`) that trigger PowerPoint's repair dialog on certain slide layouts.

Run the shared fixer immediately after building, before QA:

```bash
# Fetch fixer from GitHub if not already present
if [ ! -f /home/claude/fix_pptx_ooxml.py ]; then
    TOKEN=$(grep -ro 'github_pat_[A-Za-z0-9_]*' /mnt/skills/user/github-sync/ 2>/dev/null | head -1 | sed 's/.*://')
    curl -s -H "Authorization: token ${TOKEN}" \
      "https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/fix_pptx_ooxml.py" \
      -o /home/claude/fix_pptx_ooxml.py
fi

python3 /home/claude/fix_pptx_ooxml.py <output_path_from_build>
```

Replace `<output_path_from_build>` with the path printed by the build script above. The
fixer is a no-op if no issues are found, so it is safe to run every time.

Then run the layout validator on the same file:

```bash
# Fetch layout validator if not already present
if [ ! -f /home/claude/validate_pptx_layout.py ]; then
    TOKEN=$(grep -ro 'github_pat_[A-Za-z0-9_]*' /mnt/skills/user/github-sync/ 2>/dev/null | head -1 | sed 's/.*://')
    curl -s -H "Authorization: token ${TOKEN}" \
      "https://raw.githubusercontent.com/imcl75/claude_files/main/Shared/validate_pptx_layout.py" \
      -o /home/claude/validate_pptx_layout.py
fi

python3 /home/claude/validate_pptx_layout.py <output_path_from_build> --warnings
```

The validator prints any off-canvas, text-spill or collision errors. Fix and rebuild if
any ERRORs appear — warnings are advisory only.

---

## Step 7 — QA

Convert to images and inspect:

```bash
python /mnt/skills/public/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf <output.pptx>
pdftoppm -jpeg -r 120 <output.pdf> qa_slide
ls qa_slide-*.jpg
```

View each slide image and check:
- Cover: correct day, correct book cover in top-left placeholder
- Key Concepts: wheel displays correctly (full-slide image)
- LO: all three panels populated, text fits
- Warm-up: three cards, correct colours, content readable
- Teaching slides: correct phase badge (I do/We do/You do), content fits
- Book placeholders: clear label text
- Learning Review: three distinct questions in speech bubbles
- Timer placeholder: visible as empty box in edit mode (bottom right), not visible in slideshow

Fix any issues, rebuild, re-render until clean. Only then copy to outputs.

---

## Output naming

```
T[term]W[week]_-_Lesson_[N]_-_Writers_-_[Topic].pptx
```

Examples:
- `T5W1_-_Lesson_2_-_Writers_-_Speech_Punctuation.pptx`
- `T5W1_-_Lesson_3_-_Writers_-_Reporting_Clauses.pptx`

Topic label: use 2–3 words from the lesson focus, title case, underscores for spaces.

---

## Carry-over slide workflow

If Innes says "include the checklist from lesson 2":

1. Identify the uploaded PPTX and slide number
2. Unpack it: `unzip <pptx> -d /home/claude/prev_lesson/`
3. Read the slide XML: `cat /home/claude/prev_lesson/ppt/slides/slide<N>.xml`
4. Read its rels: `cat /home/claude/prev_lesson/ppt/slides/_rels/slide<N>.xml.rels`
5. If the slide has images, copy those from `prev_lesson/ppt/media/` to
   the build's media directory (the build script handles this for `rules` slides
   when you pass `source_slide_rels`)
6. Add a `rules` entry to the slides JSON:
```json
{"type": "rules",
 "source_slide_xml":  "<full XML string>",
 "source_slide_rels": "<full rels string>"}
```

Note: the build script will inject a timer placeholder onto the carried-over
slide if one isn't already present.

---

## Key content principles

These were established during the I Want My Hat Back unit and must carry through
every future writing lesson:

- **Learner language**: child-facing, plain words, no jargon in LO panels
- **Phase labels in titles**: never include "I do:", "We do:", "You do:" in slide
  titles — the phase badge icon does that job
- **You Do Trio**: no title text — delete the title placeholder entirely,
  extend the body box to 28.35 × 17.22 cm starting at y=365125
- **Grammar Warm-Up**: different format each lesson; 3 cards; linked to grammar
  focus; avoid repeating the same exercise type in consecutive lessons
- **Book page slides**: always include one before the slide that refers to that
  spread; label clearly so Innes knows which spread to display
- **Slide text length**: normAutofit is set on all body placeholders; text will
  shrink to fit; but keep content concise — a slide is a prompt, not a handout
- **British English throughout**: spelling, vocabulary, punctuation conventions
- **No em dashes in slide content** (use commas or restructure)

