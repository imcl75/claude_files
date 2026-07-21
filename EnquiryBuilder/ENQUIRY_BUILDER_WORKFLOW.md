# Enquiry Builder — New Enquiry Workflow
*Run this form at the start of every new enquiry. Follow each block in order.*
*Last updated: 2026-07-21*
*Default year group: **Y5** (Innes is teaching Year 5 from September 2026)*

### Input types
- 🔘 **Choice** — use `AskUserQuestion` (fixed options, presented as a form)
- ✏️ **Free text** — ask as a plain question; Innes types the answer
- ☑️ **Multi-select** — use `AskUserQuestion` with `multiSelect: true`

---

## What the pipeline produces

| Output | Format | Built by |
|---|---|---|
| MTP JSON | `.json` file | Claude (this form → JSON) |
| Lesson PPTX decks | `.pptx` per lesson | `build_science/history/geography_lesson.py` |
| Learning Papers | `.pptx` per lesson | `learning-paper` skill, run per lesson |
| LP handouts | `.pdf` per lesson | PDF export of the LP PPTX |
| Image / source pack | folder of images | Gathered by teacher; paths supplied to MTP |
| Knowledge Organiser | `.pdf` A4 | `knowledge-organiser` skill |
| Top 10 vocabulary | embedded in KO + MTP | Gathered in Block 3 below |

---

## CLF CURRICULUM CHECK — mandatory before any content is drafted

Run this immediately after Block 1 (subject and year group confirmed). Do not suggest vocabulary, KO content or any lesson content before completing this step.

### Document paths (knowledge source)

| Subject | Document |
|---|---|
| History | `/mnt/.projects/019ce895-59c7-71c2-b81d-5e89f848fb8d/docs/CLF Primary Curriculum Historians July 2026.md` |
| Science | `/mnt/.projects/019ce895-59c7-71c2-b81d-5e89f848fb8d/docs/CLF Primary Curriculum Scientists July 2026.md` |
| Geography | `/mnt/.projects/019ce895-59c7-71c2-b81d-5e89f848fb8d/docs/CLF Primary Curriculum Geographers July 2026.md` |
| Writing (History) | `/mnt/.projects/019ce895-59c7-71c2-b81d-5e89f848fb8d/docs/CLF Primary Curriculum Writers July 2026.md` |

Also available: `CLF Primary Curriculum Mathematicans July 2026.md`, `Artists`, `Musicians`, `Computer Scientists`, `Citizens`, `MFL`, `Designers`, `Athletes`, `Readers`, `RE`.

### What to extract

Read the document and locate the correct year group section. Extract and record:

1. **Required enquiry topics** — what the CLF specifies this year group must study in this subject. Confirm the requested topic is listed; if it is not, flag this to Innes before proceeding.
2. **Prior learning** — what children will have already studied in previous year groups that connects to this topic. Note key vocabulary, concepts and knowledge they bring in.
3. **CLF vocabulary** — the specific subject vocabulary the curriculum lists for this year group and topic. These seed Block 3 (top 10 vocabulary).
4. **CLF knowledge content** — the factual knowledge and skills the curriculum specifies. These shape lesson content, building blocks and KO facts.
5. **Cross-curricular links** — any connections to other subjects noted in the curriculum (e.g. History links to Writing, Geography, RE).

### Year 5 curriculum overview (reference)

| Subject | Enquiry 1 | Enquiry 2 |
|---|---|---|
| History | Roman Empire — its impact on Britain (43 BC–AD 410) | Ancient Egypt — New Kingdom (1520 BC–1075 BC) + Old Kingdom |
| Science | TBC — check Scientists doc | TBC |
| Geography | TBC — check Geographers doc | TBC |

**Y5 prior learning (History):** Y4 = Mayan Civilisation (civilisation concept) + Anglo-Saxon and Viking struggle for the Kingdom of England (invasion/monarchy concepts). Y3 = Changes in Britain from the Stone Age to the Iron Age, Ancient Egypt (Y3 intro level).

> ⚠️ If the requested topic is not in the CLF for this year group, stop and confirm with Innes before continuing.

---

## BLOCK 1 — Subject and top-level setup

Ask these first, every time.

1. 🔘 **Subject** — `AskUserQuestion`: Science / History / Geography
2. ✏️ **Key question** — the enquiry-framing question (e.g. "What was the impact of the Roman Civilisation?")
3. ✏️ **Topic title** — short label used in filenames (e.g. `roman_civilisation`)
4. 🔘 **Number of lessons** — `AskUserQuestion`: 12 / 13 / 14 / More (if More, ask free text for exact count)
5. ✏️ **Start reference** — term and week (e.g. T2W3)
6. ✏️ **Lesson timetable** — list the days the subject is taught this enquiry, in order, one entry per lesson slot. Repeat a day if two lessons fall in the same week on the same day. E.g. `Tue, Thu` (2 per week) or `Mon, Tue, Tue, Wed, Thu, Thu, Fri` (7 per week).

   From this list Claude computes a `day_label` for every lesson. The label is `{sequence_in_week}{Day}` — the sequence number resets to 1 each new week, and the week reference advances when the list is exhausted. Examples:
   - `Tue, Thu` × 7 lessons from T2W3 → `T2W3_1Tue_L01`, `T2W3_2Thu_L02`, `T2W4_1Tue_L03`, `T2W4_2Thu_L04` …
   - `Mon, Tue, Tue, Wed, Thu, Thu, Fri` × 14 lessons from T1W1 → `T1W1_1Mon_L01` … `T1W1_7Fri_L07`, `T1W2_1Mon_L08` … `T1W2_7Fri_L14`

   Claude writes `day_label` (e.g. `T2W3_1Tue`) and `term_week` (e.g. `T2W3`) per lesson into the MTP JSON.

---

## BLOCK 2 — Subject-specific metadata

Ask the relevant sub-block only.

### Science
- 🔘 **Strand** — `AskUserQuestion`: Biology / Chemistry / Physics / Earth and Space Science *(4 options — fits exactly)*
- ✏️ **Challenge text** — the sub-question shown below the key question on slide 1 (a provocative one-liner, e.g. "Is a virus alive?")

### History
- 🔘 **Concept** — `AskUserQuestion`: civilisation / invasion / empire / monarchy — use "Other" for revolution *(tool max is 4 options; "Other" auto-appears as the fifth)*
  *(drives the colour scheme — all slides for this enquiry use the matching bg/border pair)*
- ✏️ **Challenge / writing outcome** — what will children produce by the end of the enquiry? For History, this is typically a writing outcome (e.g. "To write a non-chronological report to inform about key legacies of the Roman Civilisation"). This shapes LP tasks across the whole sequence, so it must be collected here before the MTP is drafted.
- ✏️ **Writing / text features to practise** — list the specific writing features that need to be woven into the knowledge-building lessons (e.g. "embedded relative clauses, cohesion connectives, variety of sentence structures, organisational features of non-chron reports"). These are mapped to specific lessons thematically when generating the MTP.

  > ⚠️ Do not proceed to Block 3 until both challenge and writing features are confirmed. The lesson sequence cannot be drafted without them.

### Geography
- 🔘 **Substantive concept** — `AskUserQuestion` (two-step):
  - Q1: place_space_scale (Yellow) / human_geography (Peach) / cultural_awareness (Blue) / Other
  - If Other — Q2: physical_geography (Green) / environmental_impact (Purple)
- 🔘 **Do lessons use different substantive concepts?** — `AskUserQuestion`: All the same / Some lessons vary
  - If varies: note the default here; per-lesson overrides captured in Block 5

---

## BLOCK 3 — Enquiry-wide vocabulary (top 10)

These are the 10 key terms for the whole enquiry. They go into the Knowledge Organiser and can seed the lesson vocabulary lists.

For each word:
- Word
- Definition (child-friendly, Y4 level)

*Tip: if unsure, ask Claude to suggest 10 words for the topic and refine from there.*

---

## BLOCK 4 — Knowledge Organiser content

Collect this now so the KO can be generated alongside the lesson decks.

- **5–8 key facts** — concrete, specific facts children should know by the end
- **Key people / places** (if History or Geography)
- **Timeline events** (History only — up to 6)
- **Maps or diagrams needed?** — yes/no; if yes, local image paths
- **Images for the KO** — 1–3 relevant images; local paths or describe for sourcing

---

## MTP DRAFT — generated after Block 4, before Block 5

Once Blocks 1–4 are complete (subject, key question, concept, challenge, writing features, vocabulary, KO content), Claude generates a **full draft MTP JSON** covering all lessons. This includes:
- Lesson titles and building block text for every lesson
- Writing features mapped to specific lessons thematically
- LP task briefs per lesson (note-gathering from ~L6, planning L11, writing L12–14)
- Image prompts for every image slide

Claude presents a brief summary table. Innes reviews and requests any changes before moving to Block 5 (which then only handles per-lesson corrections and additions, not building from scratch).

---

## BLOCK 5 — Lesson data (corrections and additions only)

Run through this block once per lesson.

**Lesson N of [total]**

| Field | Input type | Notes |
|---|---|---|
| Building block text | ✏️ Free text | Short phrase (~5 words) — what this lesson adds to the enquiry wall |
| Skill focus | 🔘 Choice | History: questioning / chronology / sources / interpretations (4 — fits exactly). Science/Geography: group into 4 options + Other (too many for one question) |
| WALT | ✏️ Free text | "I am learning to…" — complete the sentence |
| TIB | ✏️ Free text | "This is because…" — the rationale |
| ISB | ✏️ Free text | "I will show this by…" — the success criterion |
| Vocabulary | ✏️ Free text | 5 words + child-friendly definitions for this lesson's vocab slide |
| Quiz (L2+) | ✏️ Free text | 4–5 question / answer pairs. Skip for lesson 1. |
| LP task | ✏️ Free text | What task will children complete on their learning paper? Brief description. |

**Variable slides for this lesson** — use two `AskUserQuestion` calls:

☑️ **Teaching slides** — `AskUserQuestion` multi-select: I Do / We Do / I Do + We Do / None

☑️ **Learner slides** — `AskUserQuestion` multi-select: You Do (individual) / You Do Trio / Both / Learning Review

☑️ **Special slides** — `AskUserQuestion` multi-select: Image slide / None
  *(Concept cartoons are always built fresh by Claude — never ask whether one exists)*

For each selected slide type, then ask free text:
- ✏️ Title
- ✏️ Content text (for standard slides — split on sentence boundaries for animation)

**For each `image_slide`, run a separate `AskUserQuestion`:**

🔘 **Layout** (two-step — max 4 per question):
- Q1: Full bleed (A) / Hero image left (B1) / Two images left (B2) / Other
- If Other — Q2: Two images right (B3) / Supporting illustration (C) / Diagram focus (D) / Gallery

🔘 **Badge** — `AskUserQuestion`: I Do / We Do / You Do / You Do (Trio)

Then free text:
- ✏️ Title
- ✏️ Text (body/task text alongside the image)
- ✏️ Image prompt (Claude generates the image; leave blank if you have a local file)
- ✏️ Local image path (if you already have the file; leave blank to generate)

---

## BLOCK 6 — Image / source pack

For every `image_slide` identified in Block 5, note what's needed:

| Slide | Image description | Have locally? | Path or search terms |
|---|---|---|---|
| L1 S1 | Roman forum exterior | No | "roman forum ruins photograph" |
| ... | ... | ... | ... |

Claude will flag any image slides where paths are missing before generating the MTP.

---

## BLOCK 6 — Confirm and generate images

Before building, Claude scans the MTP for any `image_slide` entries where `image_prompts` is set and `images` is empty. For each:

1. 🔘 `AskUserQuestion`: Generate this image using AI / I'll supply a local file / Skip this slide
2. If Generate: run the `image-generation` skill with the prompt, save the output, populate `images[]` in the MTP
3. If Supply: ✏️ ask for the local file path

---

## BLOCK 7 — Build

Once the MTP draft is confirmed and images resolved, Claude will:

1. **Generate any AI images** not yet created (from Block 6)
2. **Build lesson PPTXs** — run the subject builder for each lesson in sequence
3. **Run LPs** — trigger the `learning-paper` skill once per lesson using the LP task brief from the MTP
4. **Generate Knowledge Organiser** — run the `knowledge-organiser` skill using Block 3 + Block 4 content
5. **Package outputs** — list all files produced and their locations

> The MTP JSON itself was already generated and confirmed after Block 4. Block 7 is purely the build step.

---

## What is NOT yet automated

| Gap | Status | Notes |
|---|---|---|
| LP auto-generation | Pending | `learning-paper` skill exists; needs wiring into the enquiry builder pipeline |
| LP PDF export | Manual | Export the LP PPTX to PDF in PowerPoint for the printed handout |
| Vocabulary display / poster | Not built | Top 10 vocabulary exists in MTP and KO; no standalone poster output yet |
| Supporting resources builder | Check repo | Earlier session work — verify current state before new enquiry run |

---

## Quick-start prompt (copy this to begin a new enquiry)

> "New enquiry — [subject]. Let's run through the enquiry builder workflow."

Claude will then work through Blocks 1–7 in order.
