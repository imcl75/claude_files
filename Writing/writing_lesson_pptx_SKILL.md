---
name: writing-lesson-pptx
description: >
  Generates writing lesson PowerPoint slides for Wallscourt Farm Academy
  (Year 4 or Year 5) in the exact school template format. Use this skill
  whenever Innes asks to "make lesson slides", "build lesson [N]", "create the
  writers slides", "make my writing lesson for [topic]", or provides a writing
  sequence planning document and wants lesson slides. Also trigger when he says
  things like "next lesson" or "lesson 3 slides" in the context of an ongoing
  writing unit. Always use this skill — do not attempt to build writing lesson
  slides ad hoc.
---

# Writing Lesson PPTX Skill

## ⚠ DELIVERY GATE — CANNOT BE SKIPPED

No file may be passed to `present_files` until ALL of the following have been
completed and confirmed in this session:

1. **Slides JSON authored and reviewed** — show Innes the slide list in chat; get
   explicit confirmation before running the build.
2. **Preflight passed** — `build_lesson.py` runs `preflight_validate()` automatically.
   If it exits with code 2, fix all errors and rebuild. Do not proceed past a preflight
   failure.
3. **One-slide preview rendered and approved** — after building, convert to PDF and
   render the **LO slide only** (slide 3) to PNG. Show it in chat. Wait for Innes to
   say "looks good" or equivalent before rendering the rest.
4. **Full QA render** — once approved, render all slides. Inspect every slide.
5. **`validate_pptx_layout.py --strict` exits 0** — `build_lesson.py` runs this
   automatically at the end. If it reports ERRORS, fix and rebuild before delivering.
6. **No placeholder text remaining** — run
   `extract-text output.pptx | grep -iE "\bINSERT|\bTODO|\bPLACEHOLDER"` and confirm
   empty output.

If any gate fails, fix and re-run. Do not call `present_files` until all six pass.

---

## Known bugs fixed (2026-07-07)

- **`build_lo` slide lookup** — previously read `slide2.xml` by filename, which is the
  blank KC wheel (Layout 17). Now scans by layout ref to find Layout 5 (Learning Focus).
  If you see a blank or wrong LO slide, this was the cause. Ensure you are using the
  latest `build_lesson.py` from GitHub.
- **Layout-mismatch detection** — `validate_pptx_layout.py` now catches slides built on
  the wrong layout (e.g. photo slides on the Learning Review layout). If you get a
  LAYOUT-MISMATCH error, change the layout ref in `rels_str()` for that slide type.
- **Layout 5 placeholder widths** — all seven text placeholders on the Learning Focus
  layout (idx 10/13/14/15/16/17/18) were narrower than their visual containers by
  0.46–0.77 inches. Long LO text (particularly ISB) overflowed the rounded rectangle.
  Fixed in `writing_lesson_base.pptx` (2026-07-07). `validate_base_template.py` now
  catches this class of error on any future template change.

---

## Session start — base template check (run before first build)

```bash
python3 /home/claude/validate_base_template.py \
    /home/claude/writing_lesson_base.pptx --strict
```

If it reports PLACEHOLDER-OVERFLOW errors, do not build — fix the template first.
The corrected template is at `Writing/assets/writing_lesson_base.pptx` in GitHub.

---

Produces fully formatted writing lesson slide decks for WFA in the exact school
template established through the I Want My Hat Back unit (T5W1).

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
| Book cover image | Ask: "Please upload the front cover image for this book." |
| Carry-over slides | Ask: "Are there any slides from a previous lesson that need to appear in this one? If so, please upload the PPTX they come from and tell me which slide." |

Do not proceed to Step 2 until you have the planning doc, lesson number(s),
term/week reference, and book cover image. Carry-over slides are optional.

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
    → image slides where a generated or sourced image is the stimulus
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
| Teacher shows a physical book page | `book_page` |
| Generated or sourced image IS the stimulus | `image_slide` |
| Reference slide from prior lesson (checklist etc.) | `rules` |

**book_page vs image_slide** — the key distinction:
- Use `book_page` when the teacher MUST show the physical book (the children need to
  see the actual page, the layout, the illustrations as Klassen drew them).
- Use `image_slide` when a generated, sourced, or uploaded image is the learning
  stimulus — the image lives on the slide permanently and the teacher does not need
  to switch away from the deck to show it.
- Never replace a `book_page` with `image_slide` just to add a picture — the choice
  follows from what the lesson actually needs.

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

## Step 4a — Plan image slots (run after Step 4, before Step 5)

After designing the slide sequence, scan the lesson for moments that would benefit
from a generated image. Do this automatically — do not skip it.

### Identification rules

Read the lesson focus and activities. Flag a moment as an image slot candidate when
ANY of these match:

| Signal in the lesson plan | Candidate slot | Layout | Tool |
|--------------------------|----------------|--------|------|
| "Hook", "stimulus", "cold task", "what do you notice?" | We Do hook slide | `A_full_bleed` | Higgsfield |
| Setting description lesson — shared analysis moment | We Do teaching slide | `B1_hero_image_left` | Higgsfield |
| Setting description lesson — independent writing task | You Do stimulus | `gallery_1wide` | Higgsfield |
| Character description lesson | We Do teaching slide | `B1_hero_image_left` | Higgsfield |
| "Compare two settings / characters / objects" | We Do comparison | `B2_hero_2images_left` | Higgsfield (×2) |
| Vocabulary collection / noun hunt / word gathering | We Do vocabulary | `gallery_5row` | Higgsfield (×5) |
| "Grammar diagram", "sentence structure", "annotated example" | I Do model | `D_diagram_focus` | DALL-E |
| "Discussion starter", "who do you agree with?", "book talk" | We Do discussion | `concept_cartoon` | Higgsfield |
| Book cover / author reference in I Do | I Do reference | `C_supporting_illustration` | (use actual cover) |
| Non-book stimulus — painting, artefact, film still, poem image | Any | `A_full_bleed` or `B1_hero_image_left` | Higgsfield |

**When NOT to add image slots:**
- Pure punctuation/grammar correction activities (spot-the-error, fix-it, conversion exercises)
- Lessons built entirely around manipulating book text (converting dialogue, adding reporting clauses to given sentences)
- Any moment where the teacher genuinely needs to show the physical book — keep as `book_page`
- Grammar warm-up cards — always text only, never image slides

### Handling identified candidates

**If no candidates found:** proceed directly to Step 5. No image work needed.

**If one or more candidates found:** present a compact list in chat. One clear question using `AskUserQuestion`:

> Here are the image slots I'd add to this lesson. Shall I generate them before building?
> [list each slot: position, moment, layout, tool, one-line prompt summary]

Options:
- Yes, generate all → draft prompts, generate, then build
- No, skip images → proceed to Step 5 with text-only slides
- Pick specific ones → generate only those, skip the rest

Do not generate any images until Innes confirms.

### Generating confirmed images

1. Generate Higgsfield images first (they take longer). Use `mcp__higgsfield__generate_image`
   with model `nano_banana_pro`, aspect ratio `16:9`.
2. Then generate DALL-E images. Use `mcp__dall-e__generate_image` with
   `quality: "balanced"`, `aspectRatio: "16:9"`, `imageSize: "1K"`.
3. **Download Higgsfield CDN URLs immediately** — they expire. Save to `/home/claude/`:

```python
import urllib.request
urllib.request.urlretrieve(cdn_url, '/home/claude/img_L{N}_{slot}.png')
```

4. Show each image to Innes before building. If one is wrong, regenerate it.
   Do not build the deck with an image Innes hasn't approved.

### Image prompt guidelines

Keep prompts under 150 words. Always include: subject, style, mood,
age-appropriateness note. Higgsfield prompts should be cinematic/photographic
descriptors. DALL-E prompts should specify "educational diagram" or
"educational illustration, primary school style".

**Never include:** named commercial IP, real named living people, children's
faces (safeguarding).

Quick reference for common writing lesson image types:

```
Setting (forest, mysterious):
"Atmospheric ancient forest at dawn, gnarled trees draped in moss, shafts of golden
light cutting through morning mist, winding path disappearing into shadows, cinematic
wide shot, painterly, warm earthy tones, primary school appropriate"

Setting (urban/modern):
"Busy Victorian street at dusk, gas lamps glowing, cobblestones glistening after rain,
horse-drawn carriages, figures in silhouette, atmospheric, cinematic, 16:9"

Character (adventurous child):
"Illustration of a determined 10-year-old in adventure clothing standing at the edge
of an ancient forest, digital painterly style, warm colours, 1:1 square crop"

Grammar diagram (fronted adverbial):
"Educational diagram for primary school: a sentence split into two colour-coded
sections — fronted adverbial clause in blue on the left, main clause in orange on the
right, clear labels, white background, clean layout, no decorative borders"

Vocabulary grid (5 images for noun hunt):
"Five separate photographic images for a primary school vocabulary activity: [list the
five subjects]. Square crop, clean background, vibrant colours, primary school appropriate"
```

---

## Step 5 — Build the slides JSON

Compose the slide specification as a JSON list. The full set of valid slide types is:

```
cover | kc | lo | warmup | we_do | i_do | you_do | you_do_trio |
book_page | image_slide | rules | learning_review
```

### image_slide spec

```json
{
  "type": "image_slide",
  "layout_key": "B1_hero_image_left",
  "badge": "We Do",
  "title": "What do you notice about this setting?",
  "text": "Look carefully at the image.\n\nJot down five precise nouns.\nAdd a powerful adjective to each one.",
  "images": ["/home/claude/img_L3_setting.png"],
  "image_prompts": ["Atmospheric ancient forest at dawn..."]
}
```

**Fields:**
- `layout_key` — one of the 10 layouts below
- `badge` — `"I Do"` / `"We Do"` / `"You Do"` / `"You Do (Trio)"`
- `title` — slide title (optional for `A_full_bleed`)
- `text` — body/task text alongside image; use `\n` for line breaks
- `images` — list of absolute paths to generated image files. Populate these BEFORE building.
- `image_prompts` — generation prompts (for reference/documentation only at build time — images must already be generated and paths in `images[]`)
- `bubbles` — (concept_cartoon only) list of 3 speech-bubble strings: `["Child A says...", "Child B says...", "Child C says..."]`

**Layout keys and their use in writing lessons:**

| `layout_key` | Images | Best use |
|---|---|---|
| `A_full_bleed` | 1 | Hook / cold task — full-screen evocative scene |
| `B1_hero_image_left` | 1 | Setting or character stimulus — one image left, task text right |
| `B2_hero_2images_left` | 2 | Comparing two settings, characters or objects |
| `B3_hero_2images_right` | 2 | Text-heavy We Do with two supporting visuals right |
| `C_supporting_illustration` | 1 | I Do with reference image (book cover, author photo) |
| `D_diagram_focus` | 1 | Grammar/sentence structure diagram — large image, notes right |
| `gallery_5row` | 5 | Vocabulary collection — 5 images representing key nouns/words |
| `gallery_6x2` | 12 | Rarely needed — large word/image sorting activity |
| `gallery_1wide` | 1 | Setting for independent writing — full-width panoramic image |
| `concept_cartoon` | 1 | Discussion starter — central image with 3 speech bubbles |

**Important:** `images[]` must be populated before running the build script.
If you have only `image_prompts` and no images yet, go back to Step 4a and
generate the images first. The build script does not generate images — it only
embeds paths you provide.

### Example JSON with image_slide (setting description lesson)

```json
[
  {"type": "cover", "day": "Wednesday AM"},
  {"type": "kc"},
  {"type": "lo",
   "wal": "write a setting description using precise nouns and powerful adjectives",
   "tib": "precise vocabulary helps the reader picture exactly where a story takes place",
   "isb": "writing three sentences about a forest setting using today's vocabulary"},
  {"type": "warmup",
   "title": "Grammar Warm-Up",
   "subtitle": "Upgrade the noun phrase. How many adjectives can you add?",
   "cards": [
     {"label": "A", "lines": ["the tree", "", "→ the _____ , _____ tree"]},
     {"label": "B", "lines": ["the path", "", "→ the _____ , _____ path"]},
     {"label": "C", "lines": ["the light", "", "→ the _____ , _____ light"]}
   ]},
  {"type": "image_slide",
   "layout_key": "A_full_bleed",
   "badge": "We Do",
   "title": "What can you see?",
   "text": "",
   "images": ["/home/claude/img_L1_hook.png"],
   "image_prompts": ["Atmospheric ancient forest at dawn, cinematic, wide shot, primary school appropriate"]},
  {"type": "we_do",
   "title": "Let's collect some vocabulary.",
   "lines": ["Look at the image. Call out what you notice.", "", "Nouns: what things can you see?", "Adjectives: what do they look and feel like?", "Verbs: what is happening?"]},
  {"type": "image_slide",
   "layout_key": "B1_hero_image_left",
   "badge": "We Do",
   "title": "Build a noun phrase.",
   "text": "Choose one object from the forest.\n\nBuild the best noun phrase you can:\n  the [adjective], [adjective] [noun]\n\nCan you add a relative clause?",
   "images": ["/home/claude/img_L1_hook.png"],
   "image_prompts": []},
  {"type": "image_slide",
   "layout_key": "gallery_1wide",
   "badge": "You Do",
   "title": "Write your setting description.",
   "text": "Use the vocabulary you collected. Aim for at least three sentences.\nVary your sentence openers.",
   "images": ["/home/claude/img_L1_hook.png"],
   "image_prompts": []},
  {"type": "learning_review",
   "q1": "Which noun phrase from today are you most pleased with?",
   "q2": "Why do precise adjectives make a setting feel more real to the reader?",
   "q3": "Which part of your description would you most like to improve?"}
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

# Cover image will already be at /mnt/user-data/uploads/<filename>
# Identify it:
ls /mnt/user-data/uploads/
```

**Before running the build**, confirm every `image_slide` in `slides.json` has
its `images[]` array populated with valid file paths. If any are empty, generate
the missing images now (see Step 4a). The build script will silently skip missing
images but the resulting slide will have no image in it.

Run the build:

```bash
python3 "$SKILL_DIR/scripts/build_lesson.py" \
  --base    /home/claude/writing_lesson_base.pptx \
  --kc      /home/claude/kc_wheel.png \
  --cover   /mnt/user-data/uploads/<cover_image_filename> \
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

## Step 7 — QA (mandatory — cannot be skipped)

`build_lesson.py` runs `validate_pptx_layout.py --strict` automatically at build time.
If it reports errors, fix before proceeding.

Then render all slides for visual inspection:

```bash
python3 /mnt/skills/public/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf <output.pptx>
rm -f qa_slide-*.jpg
pdftoppm -jpeg -r 120 <output.pdf> qa_slide
ls qa_slide-*.jpg
```

View every slide and check all of the following. **Do not skip any.**

| Slide | What to check |
|-------|--------------|
| Cover | Correct day. Book cover image present, not broken. |
| Key Concepts | Wheel fills the full slide. No white border or cropping. |
| LO | All three panels populated with actual text (not blank or placeholder). Text fits — no overflow. |
| Warm-up | Three cards visible. Correct colours (dark blue / amber / purple headers). Content readable. |
| Teaching slides | Correct phase badge for each type. Content fits its box. No text spilling outside shape. |
| **image_slide** | Image visible and not missing (blank slide = path was wrong). Image fills its region without gross distortion. Title and task text legible. Correct badge (We Do / You Do etc.). Timer placeholder present bottom-right. |
| **image_slide (gallery_5row)** | All 5 images present and in the correct row positions. Task text above images is readable. |
| **image_slide (A_full_bleed)** | Image fills the full slide. Title banner readable at bottom. No image clipping. |
| **image_slide (concept_cartoon)** | Central image present. Speech bubble text legible. Three bubbles populated. |
| Book placeholders | Clear label text. Slide is clearly a placeholder, not mistaken for content. |
| Learning Review | Three distinct questions in the three speech bubbles. No placeholder text. |
| All slides | No shape extends beyond the slide boundary. No overlapping elements. No layout decoration bleeding through. |

If **any** check fails: fix the issue, rebuild, re-render the affected slides. Do not deliver until all pass. Only then copy to `/mnt/user-data/outputs/` and call `present_files`.

---

## Output naming

```
T[term]W[week]_-_Lesson_[N]_-_Writers_-_[Topic].pptx
```

Examples:
- `T5W1_-_Lesson_2_-_Writers_-_Speech_Punctuation.pptx`
- `T5W1_-_Lesson_3_-_Writers_-_Reporting_Clauses.pptx`
- `T1W1_-_Lesson_4_-_Writers_-_Setting_Description.pptx`

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
- **Image slides**: the image is the stimulus — write task text that directs the
  children's attention to specific features of the image; keep task text short
  (3–5 lines max); the image should do the heavy lifting
- **Slide text length**: normAutofit is set on all body placeholders; text will
  shrink to fit; but keep content concise — a slide is a prompt, not a handout
- **British English throughout**: spelling, vocabulary, punctuation conventions
- **No em dashes in slide content** (use commas or restructure)
