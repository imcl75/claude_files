# Transfer: Y5 Astronomy enquiry — LP build, preview injection, resources

**Generated:** 2026-07-17
**Originating focus:** Completing the enquiry lesson builder for Y5 Astronomy: LP generation, LP preview injection into teaching slides, supporting resources, knowledge organiser, vocab poster.
**Skill in use:** enquiry-lesson-builder

---

## Status

The enquiry lesson builder has been significantly extended this session. `build_science_lesson.py` v5 (1202 lines, unified 14-lesson builder with programmatic atom model) is in the repo. The Y5 Astronomy MTP is fully specified (14 lessons, full teaching sequence, 4–5 quiz questions, 37 images, three-level LP content model per lesson). The SKILL.md has been updated to cover LP building, supporting resources, knowledge organiser, and vocab poster. A vocab poster HTML for Astronomy has been built and 10 images generated locally.

The next major build block is LP generation, preview injection, and end-to-end test.

---

## What's been produced

- `EnquiryBuilder/build_science_lesson.py` — v5, in repo. 1202 lines. Atom model fully programmatic (no missing-sci.pptx dependency). Handles all 14 lesson types.
- `EnquiryBuilder/mtp/y5_astronomy_mtp.json` — in repo. Full 14-lesson MTP with teaching sequence, vocab, quiz (4–5 questions), images array, and lp block (standard/adapted/further_adapted per lesson).
- `EnquiryBuilder/y5_astronomy_mtp.docx` — in repo. Full Word MTP with teaching sequences, concept cartoon, image requirements table (37 images), per-lesson LP summary.
- `EnquiryBuilder/build_lp.py` — already in repo from prior session. Reads `lp` key from lesson JSON. Needs schema update (see below).
- `EnquiryBuilder/science_registry.py` — in repo, 262 lines, fully populated. Not empty as earlier session summary suggested.
- `EnquiryBuilder/lib_ooxml.py` — in repo.
- `~/Pictures/claude-images/vocab_sci_universe.png` through `vocab_sci_classify.png` — 10 images on Innes's local machine only. NOT in repo (images don't go in git).
- `outputs/vocab_poster_science_astronomy.html` — A3 landscape HTML vocab poster. References local image paths. Innes has a copy.
- `outputs/SKILL.md` — updated enquiry-lesson-builder SKILL.md, ready to paste over existing skill in Claude Settings → Capabilities.
- `outputs/science_reference_UPDATED.md` — updated `references/science.md`, ready to paste over existing file in same skill.

---

## Decisions locked in

- **No missing-sci.pptx dependency** — all slides built programmatically. Zero file uploads required for a build session.
- **Three-level LP differentiation** — Standard (full demand) / Adapted (cloze, starters, matching, word banks) / Further adapted (much simpler: cut-and-stick, circle, matching only). Not A/Y/O/D.
- **LP preview injection into teaching slides** — like maths does. LPs must be built BEFORE teaching PPTXs. LP page 1 (task) PNG goes into the You Do teaching slide. LP page 2 (marking station) PNG optionally added as a follow-on slide. Model to follow: `Maths/inject_lp_previews.py` in repo.
- **Supporting resources** (sorting cards, image sets, source extracts, timeline strips) are part of the enquiry build and specified per lesson in the MTP JSON `resources` array.
- **Knowledge organiser** — one per enquiry, A3 landscape HTML, built from `knowledge_organiser` block in MTP JSON.
- **Vocab poster** — one per enquiry, A3 landscape HTML, 5×2 grid. Science prefix `vocab_sci_`. DALL-E `fast` quality, max 2 in parallel.
- **DALL-E parallel limit** — max 2 simultaneous requests. 3 causes timeouts.
- **Y5 colour** — `#e57d24`.

## Specific user requirements

> "i dont want you to rely on the long term availability of local files. The files need to be kept in the git repo."

> "for science PPTX you have solidly built example decks — i worry that I will give you missing-sci and it contains lots of things that have changed since it was built. I think you should be creating the 'master' PPTXs from all the finalised agreed PPTX definitions we've been working on."

> "Adapted might offer more support on the learning paper or provide a task which gives the learner support (for example a cloze rather than a paragraph, matching activities etc). It would be good to build an option for a 3rd level of adaptation which makes a much simpler learning paper for specific children who are at a much earlier stage."

> "it would be good for the slides to have the capability (which the maths skill has) of being able to add an image of the learning paper into the enquiry lesson slides so it shows the children the LP on the screen. The marking station (version with answers / model answers) could also be added."

> "i would like to think about resources which need to be created as part of the overall process which support the learning (e.g. a set of images which are used in an activity for sorting). These need to be created as part of the enquiry lesson process."

> "creating knowledge organisers for each enquiry based on key knowledge, skills and information which will support children throughout the enquiry, and which they might add to themselves."

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `EnquiryBuilder/build_science_lesson.py` | v5, final | No — in repo |
| `EnquiryBuilder/build_lp.py` | In repo, needs schema update for 3-level | No — in repo |
| `EnquiryBuilder/science_registry.py` | In repo, populated (262 lines) | No — in repo |
| `EnquiryBuilder/lib_ooxml.py` | In repo | No — in repo |
| `EnquiryBuilder/mtp/y5_astronomy_mtp.json` | Final, in repo | No — in repo |
| `Maths/inject_lp_previews.py` | In repo — model for LP preview injection | No — in repo |
| `outputs/SKILL.md` | Ready to paste into Claude Settings | User action required |
| `outputs/science_reference_UPDATED.md` | Ready to paste into Claude Settings | User action required |

---

## Schema: new MTP lp block (what build_lp.py needs to handle)

The MTP JSON `lp` block per lesson now looks like:

```json
"lp": {
  "recording": "lp",
  "type": "annotate_diagram",
  "standard": {
    "title": "LP title",
    "elements": [
      {"type": "instruction", "text": "..."},
      {"type": "diagram", "description": "pre-drawn diagram with N blank labels"},
      {"type": "answer_lines", "count": 3, "label": "Question text"},
      {"type": "word_bank", "words": ["word1", "word2"]}
    ]
  },
  "adapted": {
    "title": "LP title",
    "changes": "What is different from standard",
    "elements": [...]
  },
  "further_adapted": {
    "title": "LP title",
    "changes": "What is different",
    "elements": [...]
  }
}
```

Element types: `instruction`, `diagram`, `timeline_diagram`, `answer_lines`, `word_bank`, `sentence_starter`, `table`, `graph_axes`, `cloze`, `matching`, `image`, `sorting_record`.

---

## Open questions / blockers

- `build_lp.py` in repo was written for an older, single-level LP schema. Its `lp` key structure needs inspection before updating — compare what it currently expects vs the new three-level schema.
- Y5 Astronomy MTP images not yet generated (37 images). This is a blocking step before PPTXs can be built.
- Supporting resources builder: not yet coded. Design is specified in SKILL.md `resources` array section.
- Knowledge organiser builder: not yet coded. Specified in SKILL.md section 8.
- Innes still needs to paste SKILL.md and science_reference_UPDATED.md into Claude Settings to update the live skill.

---

## Immediate next step

Fetch `build_lp.py` from the repo, read its current schema expectations, then update it to handle the three-level (standard/adapted/further_adapted) MTP structure. In parallel, read `Maths/inject_lp_previews.py` and design the equivalent function for the enquiry builder — where LP page 1 and page 2 PNGs are injected into the You Do slide of the teaching PPTX. Once both are drafted, run an end-to-end test of L1 using `EnquiryBuilder/mtp/y5_astronomy_mtp.json`.
