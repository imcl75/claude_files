# Enquiry Lesson Builder Skill

Builds complete Being a Scientist lesson PPTXs from an enquiry description.
Produces one PPTX per lesson with flexible, pedagogy-driven slide layouts
and AI-generated images embedded throughout.

---

## Trigger phrases

"build my science enquiry", "make my science lessons", "plan a science unit",
"science enquiry for [topic]", "build lessons for [topic]", or any description
of a science enquiry unit.

---

## Workflow (four stages)

### Stage 1 — Dialogue

Ask Innes for the following if not already provided:

- **Key question** — e.g. "Can materials change their state?"
- **Challenge** — the enquiry outcome, e.g. "Create a scientific report about how materials change"
- **Number of lessons** — typically 4–6
- **Science strand** — materials / physics / biology / chemistry / earth science
- **Disciplinary focus** — which Working Scientifically skills this enquiry emphasises
- **Writing outcome** — what pupils write at the end (report, explanation, argument, etc.)

Do NOT ask what slides to include. Claude decides that.

---

### Stage 2 — Generate the MTP

Generate the Medium Term Plan as a JSON object following the schema below.
Present it to Innes as a readable summary (not raw JSON) — lesson titles, LOs,
and a brief description of each slide's purpose and layout.

**Before presenting:** check the CLF Curriculum Progression Summary (project knowledge)
for prior learning and cross-curricular links. Reference these in recall slides
and tib statements.

---

### Stage 3 — Image generation

For every slide in the MTP that has a layout other than `text_only`:
1. Determine the correct tool: **dall-e** for diagrams, particle models,
   labelled science illustrations; **Higgsfield** for photographic scenes,
   real-world contexts, atmospheric images.
2. Generate each image using the appropriate tool.
3. Download the image URL to disk:
   ```bash
   curl -L "<url>" -o /tmp/enquiry_images/L{lesson_num}_S{slide_num}_I{img_num}.png
   ```
4. Add the local path to the JSON: `"path": "/tmp/enquiry_images/L1_S3_I0.png"`

Generate all images before presenting the MTP for confirmation. Show Innes
a summary of what was generated. He can request regenerations before confirming.

**Image prompt rules:**
- Every prompt ends with: `no watermarks, no borders, no decorative frames,
  no text overlaid, suitable for primary school classroom display`
- For dall-e: `educational diagram for children aged 8–9, clear and accurate`
- For Higgsfield: `children's illustration style` or `photorealistic` as appropriate
- For grids (image_grid layout): all prompts in a grid share a consistent
  style suffix so the grid looks like a coherent set
- Never generate images of identifiable real people or children

---

### Stage 4 — Build

Once Innes confirms the MTP:

```bash
cd /home/claude/enquiry-builder

# Save the confirmed MTP JSON
python3 -c "import json; json.dump(<mtp>, open('confirmed_mtp.json','w'), indent=2)"

# Validate
python3 generate_mtp.py confirmed_mtp.json --check-images

# Build each lesson
for lesson in confirmed_mtp['lessons']:
    python3 << 'EOF'
import json
lesson = <lesson_data>
with open(f'/tmp/lesson_{lesson["number"]}.json', 'w') as f:
    json.dump(lesson, f, indent=2)
EOF
    python3 build_science_lesson.py /tmp/lesson_N.json /tmp/lesson_N.pptx /tmp/enquiry_images
done

# Package
zip -j /mnt/user-data/outputs/TxWy_Science_[Topic]_Lessons.zip /tmp/lesson_*.pptx
```

Render and QA all slides via LibreOffice + PyMuPDF before delivering.
Deliver as a single zip via present_files.

---

## MTP JSON schema

```json
{
  "enquiry": {
    "subject": "science",
    "key_question": "Can materials change their state?",
    "challenge": "Create a scientific report about how materials change",
    "year_group": "Y4",
    "num_lessons": 5,
    "science_strand": "materials",
    "disciplinary_focus": ["observe_and_measure", "record_and_present"],
    "writing_outcome": "scientific report"
  },
  "lessons": [
    {
      "number": 1,
      "day": "Monday",
      "session": "a.m.",
      "title": "What are the three states of matter?",
      "disciplinary_skill": "observe_and_measure",
      "lo": "identify and describe the properties of solids, liquids and gases",
      "tib": "...",
      "isb": "...",
      "slides": [
        { "type": "cover" },
        { "type": "lo" },
        {
          "type": "recall",
          "left": ["Materials can be sorted by their properties"],
          "right": ["I remember that water can be a solid, liquid or gas"],
          "wonder": "I wonder if all materials can be melted"
        },
        {
          "type": "teaching",
          "mode": "wedo",
          "layout": "image_grid",
          "title": "What do these six substances have in common?",
          "grid": {
            "rows": 2,
            "cols": 3,
            "items": [
              { "label": "Ice",    "prompt": "ice cube, macro photography, white background", "path": "" },
              { "label": "Water",  "prompt": "glass of clear water, white background", "path": "" },
              { "label": "Steam",  "prompt": "steam rising from cup, white background", "path": "" },
              { "label": "Rock",   "prompt": "granite rock, macro, white background", "path": "" },
              { "label": "Honey",  "prompt": "golden honey dripping, white background", "path": "" },
              { "label": "Oxygen", "prompt": "clear glass sphere representing gas, white background", "path": "" }
            ]
          }
        },
        {
          "type": "teaching",
          "mode": "ido",
          "layout": "diagram_annotated",
          "title": "What makes a solid different from a liquid?",
          "images": [
            {
              "prompt": "particle diagram showing solid on left (regular grid of touching circles), liquid in middle (irregular loose circles), gas on right (widely spaced circles), clear labels, white background, educational diagram, primary school",
              "path": ""
            }
          ],
          "bullets": [
            "In a SOLID, particles are packed tightly together and cannot move freely",
            "In a LIQUID, particles are close but can slide past each other",
            "In a GAS, particles move quickly and are spread far apart"
          ]
        },
        {
          "type": "discussion",
          "mode": "wedo",
          "layout": "provocation",
          "title": "Is this a solid, a liquid, or something else?",
          "images": [
            {
              "prompt": "cornflour and water oobleck mixture being squeezed in a hand, dramatic close-up, non-newtonian fluid behaviour visible, white background, photorealistic",
              "path": ""
            }
          ]
        },
        {
          "type": "activity",
          "mode": "youdo",
          "layout": "text_only",
          "title": "Sort the materials",
          "bullets": [
            "Sort the material cards into solid, liquid or gas",
            "Record your sorting in the table on your LP",
            "For each one: give ONE reason for your decision"
          ]
        },
        {
          "type": "learning_review",
          "starters": [
            "I can now explain the difference between a solid and a liquid because…",
            "The most surprising thing I found out today was…",
            "Something I am still wondering about is…"
          ]
        }
      ]
    }
  ]
}
```

---

## Slide type reference

| Type | Always clone from | Key shapes to edit |
|------|------------------|-------------------|
| `cover` | sci_template slide 2 | TextBox 16 (KQ), TextBox 17 (challenge), TextBox 19 (day) |
| `lo` | kq_lo_science_clean.pptx slide 1 | Title 27 (KQ), TextBox 38/39/40 (lo/tib/isb) |
| `recall` | sci_template slide 9 | Text Placeholder 5 (right), Text Placeholder 12 ×2 (left, wonder) |
| `teaching` / `discussion` / `activity` text_only | sci_example slides 13/15/12 | Title ph, body ph |
| `teaching` / `discussion` / `activity` with layout | Fresh blank slide | Via slide_layouts.py |
| `misconception` | sci_example slide 16 | Round Corners 2 (title), Speech Bubbles 19/20/21, TextBox 23/24/25 |
| `fed_in_facts` | sci_template slide 13 | Keep header, add text |
| `quiz` | sci_template slide 14 | Title ph, body ph |
| `learning_review` | sci_example slide 17 | Bubble1, Bubble2, Bubble3 |

---

## Layout variants and when to use them

| Layout | Use when | N images | Tool |
|--------|----------|----------|------|
| `text_only` | Complex multi-point instruction; no visual needed | 0 | — |
| `image_grid` | "What do these X things have in common?" / sorting / classification opener | 4–9 | dall-e or Higgsfield |
| `provocation` | Discussion starter; hook; "What is happening here?"; surprising/striking image | 1 | Higgsfield preferred |
| `comparison` | Before/after; two materials side by side; two learner outcomes; two states | 2–3 | dall-e or Higgsfield |
| `image_right` | Teacher explanation with supporting diagram right | 1 | dall-e |
| `image_left` | Visual leads, supporting text right | 1 | Higgsfield |
| `diagram_annotated` | Scientific diagram with annotation questions around it | 1 | dall-e |

---

## Source files

All at `/home/claude/enquiry-builder/`:
- `build_science_lesson.py` — main builder
- `slide_layouts.py` — flexible layout system
- `generate_mtp.py` — MTP validator
- `sci_template.pptx` — source for cover, recall, quiz, fed_in_facts
- `sci_example.pptx` — source for I Do, We Do, You Do, misconception, learning review
- `kq_lo_science_clean.pptx` — source for LO slide (accent1 removed)
- `assets/` — badge images, pupil images, subject icons

---

## Rules

- The cover slide is ALWAYS first. The LO is ALWAYS second. Learning Review is ALWAYS last.
- Never use sci_template slide 8 (vertical WWH slide) for anything.
- The recall slide only appears when there is genuine prior learning to activate.
- Misconception slides require three clearly distinct learner views — one correct, one partially correct, one common misconception.
- Every enquiry needs at least one `image_grid` or `provocation` slide somewhere in the sequence — lessons with only text slides are not acceptable.
- Image prompts are specific and purposeful. "Science image" is not a prompt.
- For image grids, all items share a consistent visual style directive in the prompt.
- The `tib` statement explains WHY the learning matters in the world, not just in school.
- The `isb` statement describes a concrete, observable success product — not abstract qualities.
