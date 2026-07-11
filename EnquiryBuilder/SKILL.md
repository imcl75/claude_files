---
name: enquiry-lesson-builder
description: >
  Builds complete Being a Scientist lesson PPTXs from an enquiry description.
  Use when Innes says "build my science enquiry", "make my science lessons",
  "plan a science unit", "science enquiry for [topic]", "build lessons for
  [topic]", or describes a science enquiry unit. Produces one PPTX per lesson
  with flexible, pedagogy-driven slide layouts and AI-generated images.
  Triggers: "build my science enquiry", "make science lessons", "plan a
  science unit", "science enquiry", "build lessons for".
---

# Enquiry Lesson Builder Skill

Builds complete Being a Scientist lesson PPTXs from an enquiry description.

---

## CRITICAL RULES — do not deviate from these

These were all learned through hard QA failure. Violating any of them will cause crashes, broken animations, or wrong content.

### PPTX structure rules
- **Never clone content slides** — I Do, We Do, You Do, discussion, activity slides must be built from scratch using `fresh_slide(work, layout_name)`. Cloning pulls in media and shapes from the source enquiry.
- **Badges come from slide layouts** — never add I do / We do / You do badges programmatically.
- **Layout resolution by name, not filename** — `slideLayout3.xml` means different things in different template files. Always resolve by layout NAME against the work directory.
- **Atomic rId replacement** — use a single regex pass: `re.sub(r'(r:(?:embed|id|link))="([^"]+)"', sub, xml)`. Never use sequential `.replace()` calls — cascading replacement corrupts image mapping.
- **No matplotlib for scientific illustrations** — use Higgsfield (`nano_banana_pro`) for all objects, scenes, and people. Matplotlib is only for particle model diagrams and charts.
- **Images need background removal** if placed on coloured slide backgrounds — use `rembg` or Higgsfield background removal.
- **fix_pptx_ooxml must run on every output before delivery** — especially Fix #6 (SharePoint metadata strip). Files saved via SharePoint/Teams carry `customXml/` parts that cause persistent repair dialogs. Also check `ppt/_rels/presentation.xml.rels` for stray customXml refs (not just `_rels/.rels`).

### Animation rules
- **Clean `<p:seq>` only** — no hide-at-start `<p:par>` blocks. PowerPoint handles initial hiding of `clickEffect` entry animations automatically. Explicit hide-at-start pars create "TRIGGER: UNNAMED" in PowerPoint's animation pane.
- Correct root node: `<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">`
- Each click step: outer par with `<p:cond evt="onBegin" delay="indefinite"/>`, inner par with `nodeType="clickEffect"`
- For body paragraph animation: use `<p:bldLst><p:bldP spid="ID" grpId="0" build="p"/></p:bldLst>`

### Image generation
- Use **Higgsfield** (`nano_banana_pro` model) for all educational illustrations and photorealistic content.
- Use **dall-e** only if Higgsfield is unavailable — dall-e times out frequently.
- Images do not persist between sessions. Re-download via `job_display` CDN URLs while the session is open, or regenerate fresh next session.
- Never use placeholder coloured boxes in delivered files.

---

## Slide structure for L1 of a new enquiry

Every L1 follows this exact order:

| # | Slide type | Source |
|---|-----------|--------|
| 1 | KQ Cover | Clone sci_template slide 2, remove TextBox 19, set TextBox 16 to KQ |
| 2 | Being a Scientist | Clone from missing-sci.pptx slide 1 (Areas of Study + Skills wheel) |
| 3 | Discipline slide | Clone from missing-sci.pptx: slide 2 = Biology, slide 3 = Physics, slide 4 = Chemistry, slide 5 = Earth & Space. Show ONLY the one matching the enquiry strand |
| 4 | LO | Clone KQ_LO.pptx slide 1, set TextBox 38/39/40, animate each on click |
| 5–N | Content slides | Build fresh from layouts (see below) |
| N-1 | Concept cartoon | Clone from missing-sci.pptx slide 6 as a TEMPLATE, then update text and central image for this specific enquiry's misconception |
| N | Learning review | Clone sci_example slide 17, set Bubble1/2/3 |

**Note:** The concept cartoon from missing-sci slide 6 contains a light/cat example — this is a template. ALWAYS replace learner statements and the central image with content relevant to the current enquiry. Do not leave the cat/light content in a States of Matter or any other non-Light enquiry.

### Content slide order (within L5–N)
Standard L1 sequence after LO:
1. We Do — recall/hook (text_only layout)
2. We Do — image grid (we_do_blank layout + 2×4 images)
3. I Do — particle/diagram slide (i_do_blank layout)
4. You Do — provocation image (you_do_ind_blank layout)
5. You Do — task instructions (you_do_ind layout)

Varies for later lessons per MTP.

---

## Workflow

### Stage 1 — Gather MTP inputs
Ask for:
- Key question
- Science strand (Biology / Physics / Chemistry / Earth and Space Science)
- Number of lessons
- Disciplinary focus for each lesson
- LO, TIB, ISB per lesson
- Day and session (a.m./p.m.) per lesson

Do NOT ask what slides to include — decide based on MTP.

### Stage 2 — Generate MTP JSON
Generate the full MTP as JSON (schema below). Present as readable summary. Check CLF Curriculum Progression Summary for prior learning and cross-curricular links.

### Stage 3 — Generate images
For every slide requiring images:
1. Generate via Higgsfield (`nano_banana_pro` model), 1:1 aspect ratio for grid items, 16:9 for provocation/full-slide images.
2. Download CDN URLs immediately after generation — they do not persist across sessions.
3. Remove backgrounds where needed (rembg or Higgsfield background removal).
4. Never deliver a file with placeholder boxes.

### Stage 4 — Build
1. Fetch `build_l1_final.py` from GitHub repo (`EnquiryBuilder/` folder).
2. Run build — each lesson becomes one PPTX.
3. Run `fix_pptx_ooxml.py` on every output.
4. Validate with `/mnt/skills/public/pptx/scripts/office/validate.py`.
5. Render QA via LibreOffice → PyMuPDF. Check every slide.
6. Deliver as zip.

---

## Slide layout map (sci_example.pptx)

| Layout name | File | Use for |
|-------------|------|---------|
| `I do` | slideLayout2.xml | I Do with title + body text |
| `We do` | slideLayout3.xml | We Do with title + body text |
| `You do Ind` | slideLayout5.xml | You Do with title + body text |
| `I Do - Blank` | slideLayout6.xml | I Do with custom image/text layout |
| `We do - Blank` | slideLayout7.xml | We Do with custom image/text layout |
| `You do Ind - Blank` | slideLayout9.xml | You Do with custom image/text layout |
| `Blank` | slideLayout15.xml | No badge — use for cover and LO |

**Always resolve layouts by name, not filename.** sci_template.pptx and KQ_LO.pptx have different layout numbering.

---

## Clone vs fresh slide decision

| Slide | Approach | Source |
|-------|----------|--------|
| KQ cover | Clone | sci_template slide 2 |
| Being a Scientist | Clone (full — handles hdphoto + diagrams) | missing-sci slide 1 |
| Discipline slide | Clone (full) | missing-sci slide 2/3/4/5 |
| LO | Clone (image rels only) | KQ_LO slide 1 |
| Concept cartoon | Clone (full), then update text + image | missing-sci slide 6 |
| Learning review | Clone (image rels only) | sci_example slide 17 |
| All content slides | Fresh from layout | — |

The "full" clone copies image, hdphoto, diagram, and notesSlide rels. The "image only" clone skips hdphoto and notes (avoids LibreOffice rendering issues from .wdp files, and avoids broken notesSlide back-references).

---

## LO slide animation

TextBox 38 (LO), 39 (TIB), 40 (ISB) each appear on a separate click.
Shape IDs in the repaired file: id=39, id=40, id=41 respectively.
Use clean appear animation (no hide-at-start pars):

```xml
<p:timing>
  <p:tnLst>
    <p:par>
      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
        <p:childTnLst>
          <p:seq concurrent="1" nextAc="seek">
            <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
              <p:childTnLst>
                <!-- repeat for each shape: -->
                <p:par>
                  <p:cTn id="N" fill="hold">
                    <p:stCondLst><p:cond evt="onBegin" delay="indefinite"/></p:stCondLst>
                    <p:childTnLst>
                      <p:par>
                        <p:cTn id="N+1" presetID="1" presetClass="entr" presetSubtype="0"
                               fill="hold" grpId="0" nodeType="clickEffect">
                          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                          <p:childTnLst>
                            <p:set>
                              <p:cBhvr>
                                <p:cTn id="N+2" dur="1" fill="hold"/>
                                <p:tgtEl><p:spTgt spid="SP_ID"/></p:tgtEl>
                                <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                              </p:cBhvr>
                              <p:to><p:strVal val="visible"/></p:to>
                            </p:set>
                          </p:childTnLst>
                        </p:cTn>
                      </p:par>
                    </p:childTnLst>
                  </p:cTn>
                </p:par>
              </p:childTnLst>
            </p:cTn>
            <p:prevCondLst><p:cond evt="onPrevClick" delay="0"/></p:prevCondLst>
            <p:nextCondLst><p:cond evt="onNextClick" delay="0"/></p:nextCondLst>
          </p:seq>
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>
```

---

## LO grammar rules

- **LO** (TextBox 38): infinitive verb phrase — "compare and group materials…"
- **TIB** (TextBox 39): first person present — "I understand how…" / "I know that…"
- **ISB** (TextBox 40): progressive "-ing" — "creating a sorting table…"

---

## Concept cartoon rules

- ALWAYS specific to the current enquiry's science content.
- Three learner views: one common misconception, one partially correct, one scientifically accurate.
- Central image: relevant photorealistic stimulus from Higgsfield.
- The missing-sci.pptx slide 6 is a TEMPLATE ONLY — always replace all content.

---

## fix_pptx_ooxml.py

Run on every PPTX before delivery. Now includes Fix #6: SharePoint metadata strip.
Located at `Shared/fix_pptx_ooxml.py` in the GitHub repo.

Fix #6 strips `customXml/` parts and their relationships from both `_rels/.rels` AND `ppt/_rels/presentation.xml.rels`. Files saved via SharePoint/Teams carry these parts; they cause persistent repair dialogs in PowerPoint that no other fix resolves.

---

## Source files

All scripts at `imcl75/claude_files` on GitHub. Fetch fresh at session start.

- `EnquiryBuilder/build_l1_final.py` — L1 builder (current working version from T6W7 session)
- `Shared/fix_pptx_ooxml.py` — post-processing fixer including Fix #6
- `EnquiryBuilder/templates/sci_template.pptx` — cover, recall source
- `EnquiryBuilder/templates/sci_example.pptx` — I Do, We Do, You Do, learning review source
- `EnquiryBuilder/templates/KQ_LO.pptx` — LO slide source
- `missing-sci.pptx` — Being a Scientist, discipline slides, concept cartoon template (Innes must re-upload each session; not in repo)

---

## MTP JSON schema

```json
{
  "enquiry": {
    "key_question": "Can materials change their state?",
    "science_strand": "Chemistry",
    "year_group": "Y4",
    "num_lessons": 5,
    "disciplinary_focus": ["observe_measure", "record_present", "conclude"]
  },
  "lessons": [
    {
      "number": 1,
      "day": "Monday",
      "session": "a.m.",
      "lo": "infinitive verb phrase",
      "tib": "I understand/I know that…",
      "isb": "progressive -ing verb phrase",
      "concept_cartoon": {
        "title": "Who do you agree with and why?",
        "learners": [
          {"name": "Learner A", "statement": "common misconception"},
          {"name": "Learner B", "statement": "partially correct"},
          {"name": "Learner C", "statement": "scientifically accurate"}
        ],
        "image_prompt": "relevant states of matter stimulus image"
      },
      "slides": [
        {"type": "cover"},
        {"type": "being_a_scientist"},
        {"type": "discipline", "strand": "Chemistry"},
        {"type": "lo"},
        {"type": "wedo_hook", "title": "…", "bullets": ["…"]},
        {"type": "wedo_grid", "title": "…", "items": [
          {"label": "Ice", "path": ""},
          {"label": "Water", "path": ""},
          {"label": "Steam (water vapour)", "path": ""},
          {"label": "Wood", "path": ""},
          {"label": "Sand", "path": ""},
          {"label": "Milk", "path": ""},
          {"label": "Balloon (filled with air)", "path": ""},
          {"label": "Honey", "path": ""}
        ]},
        {"type": "ido_diagram", "title": "…", "bullets": ["…", "…", "…"], "image_path": ""},
        {"type": "youdo_provocation", "title": "…", "image_path": ""},
        {"type": "youdo_task", "title": "…", "bullets": ["…"]},
        {"type": "concept_cartoon"},
        {"type": "learning_review", "starters": ["…", "…", "…"]}
      ]
    }
  ]
}
```

---

## Outstanding issues from T6W7 session (July 2026)

1. **Concept cartoon on slide 10** still has light/cat content from missing-sci template. Needs States of Matter learner statements and a relevant image (sand pouring, oobleck, etc.) — quick text edit in PowerPoint or request update.
2. **Skill needs a proper `build_science_lesson.py`** that reads the MTP JSON and generates all lessons. `build_l1_final.py` only handles L1 structure. L2–L5 not yet built.
3. **Discipline slide selection** must be driven by `science_strand` in MTP — only the relevant discipline slide should appear, not all four.
4. **Dynamic concept cartoon** generation from MTP `concept_cartoon` data not yet implemented.
5. **Repair dialog** (PowerPoint on open) was traced to SharePoint customXml metadata. Fix #6 in `fix_pptx_ooxml.py` strips this. However the repaired PPTX Innes provided still shows the dialog — another session is exploring root cause further.
