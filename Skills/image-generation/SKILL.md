---
name: image-generation
description: >
  Standalone AI image and diagram generation skill. Use whenever Innes asks to
  "generate an image", "create an image", "make a diagram", "generate a diagram",
  "create a picture of", "illustrate", or any similar request for a standalone
  AI-generated visual. Guides Innes through options to build a precise prompt,
  decides whether to use dall-e (diagrams) or Higgsfield (photographs and
  illustrations), generates the image and presents it. Do NOT use this skill
  when image generation is already embedded in another skill workflow (enquiry
  planner, writing lesson PPTX etc.) — those handle it internally.
---

# Image Generation Skill

Produces a single AI-generated image or diagram by guiding Innes through
structured options, building a precise prompt and calling the correct MCP tool.

---

## Tool decision rule

Make this decision first — it determines everything downstream:

| Request type | Tool |
|---|---|
| Scientific diagrams, particle diagrams, circuit diagrams, labelled anatomy, food chains, states of matter, sound waves, maps, timelines, flowcharts, any image requiring accurate text labels | **dall-e MCP** (`generate_ai_image`, model: `dall-e-3`) |
| Photographs, atmospheric scenes, historical moments, real-world environments, character illustrations, book-themed images, natural landscapes, animals, people in context | **Higgsfield MCP** (`generate_image`, model: `nano_banana_pro`, aspect ratio: `16:9`) |

If the request is ambiguous, ask one question: "Is this a diagram with labels, or more of a scene or illustration?"

---

## Step 1 — Establish the content type

If not already clear from Innes's request, ask:

> "Diagram with labels, or scene / illustration?"

- **Diagram** → dall-e path
- **Scene / illustration** → Higgsfield path

---

## Step 2 — Gather options via multi-select

Present options relevant to the chosen path. Use `ask_user_input_v0` with
`multi_select` where multiple choices are valid, `single_select` where only
one applies. Always include a free-text "Anything else to add?" at the end.

### Higgsfield path — options to present

**Shot type** (single_select):
- Extreme close-up
- Close-up
- Medium shot
- Wide shot
- Bird's eye view
- Low angle
- No preference

**Style** (single_select):
- Photorealistic
- Cinematic film
- Children's illustration
- Oil painting
- Watercolour
- Flat vector / cartoon
- No preference

**Lighting** (single_select):
- Golden hour
- Overcast / diffused
- Dramatic side lighting
- Studio / clean
- Candlelight / warm
- No preference

**Mood** (single_select):
- Calm / peaceful
- Dramatic / tense
- Joyful / playful
- Epic / grand
- Eerie / mysterious
- No preference

**Colour palette** (single_select):
- Warm earthy tones
- Cool blues and greys
- Vivid and saturated
- Muted / desaturated
- Black and white
- No preference

### dall-e path — options to present

**Background** (single_select):
- White / clean
- Light grey
- Transparent (PNG)
- Contextual / natural

**Label style** (single_select):
- Bold clear labels
- No labels — visual only
- Minimal annotations

**Colour scheme** (single_select):
- Full colour
- Two-colour / simplified
- Black and white / greyscale
- School-friendly primaries

**Complexity** (single_select):
- Simple / clean — fewer elements
- Detailed — multiple components

---

## Step 3 — Build the prompt

Construct the full prompt from:
- Innes's subject description
- Selected options
- Any free-text additions

### Higgsfield prompt structure

```
[subject description], [setting/context], [shot type], [lighting] lighting,
[style], [mood] mood, [colour palette] colour palette, [any extras]
```

Do not include: named commercial IP, real named living people, children's
faces (avoid entirely for safeguarding).

Higgsfield constraints:
- No named commercial IP (Minecraft, Sonic, Lego etc.)
- If the topic relates to Callum (Minecraft) or Sam (Lego/Sonic), generate
  thematically similar content without using the brand name:
  - Minecraft → "blocky pixelated game world with square terrain and cube trees"
  - Sonic → "fast blue cartoon hedgehog character"
  - Lego → "colourful plastic building bricks construction scene"

### dall-e prompt structure

```
[subject description], educational diagram for primary school children aged 8-9,
[label style], [colour scheme], [background], [complexity level],
clear and accurate, suitable for classroom display
```

Always append: `no watermarks, no borders, no decorative frames`

---

## Step 4 — Confirm before generating

Show Innes the full assembled prompt and say:

> "Ready to generate. Prompt: [prompt]. Shall I go ahead, or would you like to tweak anything?"

Make this quick — one line. Do not ask if he wants to proceed if his original
request was already specific enough; just show the prompt and generate unless
he says stop.

---

## Step 5 — Generate

### Higgsfield

Call the Higgsfield `generate_image` tool:
- model: `nano_banana_pro`
- aspect_ratio: `16:9`
- prompt: [assembled prompt]

### dall-e

Call the dall-e MCP `generate_ai_image` tool:
- model: `dall-e-3`
- prompt: [assembled prompt]
- size: `1792x1024` for landscape, `1024x1024` for diagrams

---

## Step 6 — Present and offer variations

Show the generated image. Then offer two quick options only:

- "Regenerate with a different variation"
- "Adjust the prompt"

If Innes wants a variation, regenerate with a slightly modified seed or
prompt tweak. If he wants to adjust, go back to Step 3.

Do not offer more than two follow-up options. Do not list all the things
you could do next.

---

## Notes

- Always use British English in any text within prompts.
- For classroom display images, favour clean compositions with strong focal
  points — busy or cluttered outputs are harder to use on a whiteboard.
- For science diagrams, accuracy matters more than style — describe the
  content precisely rather than relying on the model's interpretation.
- If generation fails, report the error message briefly and ask whether to
  retry or try the other tool.
- Credits for Higgsfield are finite — prefer dall-e for iterative diagram
  work where multiple attempts may be needed.
