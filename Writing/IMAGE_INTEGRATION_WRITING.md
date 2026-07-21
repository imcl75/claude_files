# Image Integration — Writing Lessons, LPs and Resources
*Reference for a new Claude session. Read this before starting any image work
in the writing lesson pipeline.*
*Last updated: 2026-07-21*

---

## Context

The writing lesson pipeline produces three types of output:

| Output | Builder | Format |
|---|---|---|
| Lesson slide decks | `Writing/build_lesson.py` | PPTX |
| Learning Papers (LPs) | `learning-paper` skill | PPTX (portrait A4) |
| Writing resources (toolkits, boxing-up grids, model texts) | individual `build_*.py` scripts | PDF (via ReportLab) or PPTX |

**Current state:** Image support exists in the Enquiry Builder pipeline
(`EnquiryBuilder/image_layouts.py`, `image_slide` slide type). It does NOT yet
exist natively in the writing lesson pipeline. This document explains how to
add it and how to use it consistently across all three output types.

---

## 1. Image generation tools

Two tools are available. Choose based on what the image needs to look like.

| Tool | Use for | Notes |
|---|---|---|
| **Higgsfield** (`mcp__a2127951…__generate_image`, model `nano_banana_pro`) | Photographs, realistic scenes, people, objects in context, book-style illustrations | 1:1 for grid items; 16:9 for landscape/full-slide. Download CDN URLs immediately via `job_display` — they expire. |
| **DALL-E** (`mcp__dall-e__generate_image`) | Diagrams, labelled illustrations, simpler educational artwork, charts | Use `fast` quality to avoid timeouts. Do not run more than 2 in parallel. |

**Decision rule:**
- "Show what something looks like in the real world" → Higgsfield
- "Show how something works, label a diagram, create a simple illustration" → DALL-E
- "Stimulus image for creative writing (child needs to imagine a scene)" → Higgsfield
- "Grammar or punctuation example with visual layout" → DALL-E

**Before generating:** confirm image slots for the whole lesson first. Batch
generate before running the build script — not mid-build.

**After generating:** save each image locally:
```python
import urllib.request
urllib.request.urlretrieve(cdn_url, '/sessions/optimistic-serene-galileo/mnt/outputs/img_L{N}_{slot}.png')
```

---

## 2. Image layouts (from EnquiryBuilder/image_layouts.py)

Ten layouts are available. The implementation lives in the repo at
`EnquiryBuilder/image_layouts.py`. Fetch this file before building any
image slide.

```python
import re, urllib.request, os
with open('/mnt/skills/user/github-sync/SKILL.md') as f:
    TOKEN = re.search(r'GITHUB_TOKEN:\s*(\S+)', f.read()).group(1)

for fname in ['image_layouts.py', 'lib_ooxml.py']:
    dest = f'/sessions/optimistic-serene-galileo/{fname}'
    if not os.path.exists(dest):
        url = f'https://raw.githubusercontent.com/imcl75/claude_files/main/EnquiryBuilder/{fname}'
        req = urllib.request.Request(url, headers={'Authorization': f'token {TOKEN}'})
        with urllib.request.urlopen(req, timeout=15) as r:
            open(dest, 'wb').write(r.read())
```

### Layout reference

| `layout_key` | Images needed | Best use in writing lessons |
|---|---|---|
| `A_full_bleed` | 1 | Title/cover mood image; full-screen stimulus for writing cold task or hook |
| `B1_hero_image_left` | 1 | One image left, task/prompt text right — good for You Do stimulus |
| `B2_hero_2images_left` | 2 | Two images stacked left, text right — compare two characters or settings |
| `B3_hero_2images_right` | 2 | Text left, two images right — text-heavy We Do with supporting visuals |
| `C_supporting_illustration` | 1 | Main text dominant, image right with caption — I Do with reference image |
| `D_diagram_focus` | 1 | Large diagram/image ~2/3 width, labels/notes right — grammar diagram or text structure map |
| `gallery_5row` | 5 | Five images in a row — vocabulary images, character study, setting choices |
| `gallery_6x2` | 12 | Twelve images — rarely needed in writing; maybe word/phrase sorting |
| `gallery_1wide` | 1 | Single landscape image spanning full width — panoramic setting stimulus |
| `concept_cartoon` | 1 | Central image with 3 speech bubbles — writing discussion starter |

### Choosing a layout

```
Image IS the stimulus (no body text needed)   → A_full_bleed or gallery_1wide
Image supports a teaching point                → C_supporting_illustration
Task prompt + one image                       → B1_hero_image_left
Comparing two things visually                 → B2 or B3
Grammar/structure diagram                     → D_diagram_focus
Multiple images to sort or choose from        → gallery_5row
Discussion starter / book talk                → concept_cartoon
```

---

## 3. Writing lesson slides — adding image_slide support

The writing lesson builder (`Writing/build_lesson.py`) does not currently
handle an `image_slide` type. It needs a new handler added.

### New slide type spec (add to slides JSON)

```json
{
  "type": "image_slide",
  "layout_key": "B1_hero_image_left",
  "badge": "We Do",
  "title": "What can you see in this setting?",
  "text": "Look carefully at the image. What details do you notice? Jot down five precise nouns and three powerful adjectives.",
  "images": ["/sessions/optimistic-serene-galileo/mnt/outputs/img_L3_setting.png"],
  "image_prompts": ["Atmospheric photograph of a foggy ancient forest at dawn — gnarled trees, moss-covered ground, shafts of light. Cinematic, evocative, primary school appropriate."]
}
```

- `images[]` — absolute paths to already-generated image files. If populated, build uses these.
- `image_prompts[]` — generation prompts. If `images[]` is empty, Claude generates images from these prompts BEFORE running the build script. One prompt per image slot required by the layout.
- `badge` — the phase badge: `"I Do"` / `"We Do"` / `"You Do"` / `"You Do (Trio)"`
- `title` — slide title (optional for `A_full_bleed`)
- `text` — body/task text alongside the image (not used for `A_full_bleed`)

### Adding the handler to build_lesson.py

The build script needs a case for `image_slide` in its slide dispatcher.
Fetch `image_layouts.py` and `lib_ooxml.py` from `EnquiryBuilder/` (see §2 above).
Then add to `build_lesson.py`:

```python
from image_layouts import apply_image_layout  # fetched from EnquiryBuilder/

elif slide_spec['type'] == 'image_slide':
    layout_key = slide_spec['layout_key']
    images     = slide_spec.get('images', [])
    text       = slide_spec.get('text', '')
    title      = slide_spec.get('title', '')
    badge      = slide_spec.get('badge', 'We Do')
    
    # apply_image_layout signature: (work, layout_key, images, text, title, badge)
    # work = unpacked PPTX working directory (same pattern as enquiry builder)
    apply_image_layout(work, layout_key, images, text, title, badge)
```

Confirm the exact `apply_image_layout` signature by reading `image_layouts.py`
before adding the handler — parameters may have evolved since this doc was written.

### Typical image_slide uses in writing lessons

| Lesson moment | Layout | Badge | What the image shows |
|---|---|---|---|
| Hook / cold task | `A_full_bleed` | We Do | Evocative scene to spark writing |
| Character study (We Do) | `B1_hero_image_left` | We Do | Character illustration with task text |
| Setting description (You Do) | `gallery_1wide` or `A_full_bleed` | You Do | Landscape/environment |
| Comparing two settings | `B2_hero_2images_left` | We Do | Two contrasting settings |
| Grammar diagram (I Do) | `D_diagram_focus` | I Do | Annotated sentence or text structure |
| Vocabulary grid (We Do) | `gallery_5row` | We Do | Five images representing key words |
| Discussion starter | `concept_cartoon` | We Do | Scene with three children responding |
| Book cover / author reference | `C_supporting_illustration` | I Do | Book cover or author photo |

### Note on book_page slides

The current builder uses `book_page` as a placeholder where the teacher
manually displays a book spread. When a physical class book is in use, keep
`book_page` as-is. Use `image_slide` instead when:
- No physical book is being used (e.g. a film clip, a poem, original stimulus)
- A generated or sourced image IS the stimulus (not a book page)
- You want an image permanently on screen during an activity (not teacher-controlled)

---

## 4. Learning Papers — adding image support

LPs are portrait A4 PPTX files built by the `learning-paper` skill. Images
are inserted using `python-pptx`'s `add_picture()`.

### Pattern for adding an image to an LP slide

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN

# After building the LP slide content, add image:
slide = prs.slides[-1]  # the current LP slide

# Position and size (in EMU — 1 inch = 914400 EMU)
left   = Inches(0.3)   # from left edge
top    = Inches(3.5)   # below task text
width  = Inches(3.2)   # image width
height = Inches(2.4)   # image height (maintain aspect ratio)

slide.shapes.add_picture('/path/to/image.png', left, top, width, height)
```

### LP image conventions

- Images sit below the task text, not beside it (portrait layout is narrow)
- Maximum one image per LP page to keep it uncluttered
- If the LP has two activities (front/back), one image per side maximum
- Image width: 3–4 inches (the LP is 7.5" wide with margins)
- For writing LPs: a stimulus image (character, setting, object) goes at the
  top of the writing lines section to prompt the independent task
- For grammar/punctuation LPs: no image needed — text examples are sufficient

### Specifying LP images in the lesson JSON

Add an optional `lp_image` key to the lesson spec:

```json
{
  "lp_task": "Write three sentences describing the setting using the vocabulary from today.",
  "lp_image": {
    "path": "",
    "prompt": "Atmospheric misty forest at dawn, gnarled ancient trees, shafts of golden light, painterly illustration style, primary school appropriate."
  }
}
```

If `path` is empty, generate the image from `prompt` before building the LP.

---

## 5. Writing resources — adding image support

Writing resources (toolkits, boxing-up grids, model texts, reference mats)
are generated as PDFs using ReportLab.

### Adding an image to a ReportLab PDF

```python
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image as RLImage
from reportlab.lib.units import cm

# In a canvas-based builder:
canvas.drawImage(
    ImageReader('/path/to/image.png'),
    x=1.5*cm,          # left position
    y=canvas._pagesize[1] - 8*cm,  # from bottom — adjust for position
    width=6*cm,
    height=4.5*cm,
    preserveAspectRatio=True,
    mask='auto'         # handles PNG transparency
)

# In a platypus/flowable builder:
img = RLImage('/path/to/image.png', width=6*cm, height=4.5*cm)
story.append(img)
```

### Typical resource image uses

| Resource type | Image use | Typical layout |
|---|---|---|
| Writing toolkit | Book cover top-right corner; author photo | Small (3–4 cm), decorative |
| Boxing-up grid | Model text stimulus image | Medium (5–6 cm), top of grid |
| Model text | Character/setting thumbnail alongside text | 4–5 cm, floated right of text |
| Reference mat | Annotated example sentence as diagram | Full-width diagram (12 cm) |
| Vocabulary display | Word + image per card | 3×3 cm per image in grid |

---

## 6. Session workflow

Follow this order in any session that involves images:

1. **Plan all image slots** — read the lesson plan, identify every slide/LP/resource that needs an image. List them all before generating anything.

2. **Draft image_prompts** — write a clear, specific prompt for each image. Include: subject, style, mood, age-appropriateness, aspect ratio note if important (landscape/portrait/square). For Higgsfield use cinematic/photographic descriptors; for DALL-E use "educational illustration" style.

3. **Confirm with Innes** — show the image slot list and prompts. Ask whether to generate, supply locally, or skip each one.

4. **Generate in batches** — run Higgsfield jobs first (they take longer), then DALL-E. Max 2 DALL-E calls in parallel. Download Higgsfield CDN URLs immediately.

5. **Review generated images** — present each one. Replace any that are wrong before building.

6. **Build slides/LPs/resources** — only now run the build scripts, with all image paths confirmed.

7. **QA the output** — convert to PDF/PNG and inspect image placement, cropping, and text fit around images.

---

## 7. What still needs building

| Gap | What to do |
|---|---|
| `image_slide` handler in `build_lesson.py` | Add handler (see §3). Test with one lesson before rolling out. |
| LP image insertion | Add `lp_image` key handling to the `learning-paper` skill. One image per LP page, below task text. |
| Resource image support | Already possible via ReportLab `drawImage()` — needs adding to specific resource builders as needed, not as a blanket change. |
| `image_layouts.py` path | Currently in `EnquiryBuilder/`. When adding to writing pipeline, fetch from repo at session start — do not copy the file into Writing/. Single source of truth. |

---

## Quick reference — prompts for common writing image types

```
Setting (forest, mysterious):
"Atmospheric ancient forest at dawn, mist between gnarled trees, shafts of golden light,
cinematic wide shot, painterly, evocative, primary school appropriate, 16:9"

Character (child, adventurous):
"Illustration of a brave 10-year-old child in adventure clothing, determined expression,
standing at the edge of a forest, digital painterly style, warm colours, 1:1"

Object (stimulus for description):
"Close-up photograph of a weathered old compass on a wooden table, dramatic side lighting,
high detail, 1:1"

Grammar diagram (sentence structure):
"Simple educational diagram showing a complex sentence split into main clause and subordinate
clause, colour-coded labels, clean white background, primary school style, 16:9"

Book cover (placeholder):
"[Use the actual book cover — do not generate. Scan or photograph the physical book.]"
```
