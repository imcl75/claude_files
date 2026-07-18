# Transfer: Y5 Astronomy enquiry builder — knowledge organiser + supporting resources

**Generated:** 2026-07-18
**Originating focus:** Building the Y5 Astronomy science enquiry builder at WFA — advancing past LP assignment to implement knowledge organiser and supporting resources outputs.
**Skill in use:** enquiry-lesson-builder

---

## Status

LP assignment workflow (Task 8) is complete and pushed to repo. SKILL.md for the
enquiry-lesson-builder skill has been updated (Innes will paste it in manually via
Settings > Capabilities). Now at the start of Task 9 (knowledge organiser builder).
Task 10 (supporting resources) follows after.

## What's been produced

- `EnquiryBuilder/build_lp.py` — final, pushed. Three-level schema, named output per child, cohort support via `load_class_lp_groups` / `class_config_for` / `build_lp_cohort_output`. Update-workflow comment block above `load_class_lp_groups`.
- `EnquiryBuilder/class_lp_groups.json` — final, pushed. Real Y5 2026-27 cohort data: 5IM (30 children: 24S / 6A / 0FA) and 5LS (30 children: 26S / 1A / 3FA).
- `EnquiryBuilder/mtp/y5_astronomy_mtp.json` — in repo. MTP with L1 lp block complete. L2–L14 lp blocks still to add (deferred — doing KO and resources first).
- `outputs/SKILL.md` — updated version for Innes to paste in manually. Key changes: Differentiation section now references class_lp_groups.json; class_lp_groups.json added to source files table; Outstanding issue #1 (schema update) removed; issues renumbered.

## Decisions locked in

- School vocabulary rules: "learning" not "lesson/work/task"; "children" not "pupils/students"; "home zone" not "class"
- LP word banks are shuffled on render so order doesn't give away cloze answers
- Empty further_adapted list (e.g. 5IM) silently skips that level — no error, no empty file
- Standard count is always derived (class_size − adapted − further_adapted), never stored
- Y5 colour: `#e57d24`
- Repo: `imcl75/claude_files`. All enquiry builder files live under `EnquiryBuilder/`
- GitHub token lives in the github-sync SKILL.md — never expose in output, filter `token|pat|password` from all git push output

## Y5 2026-27 cohort (for reference)

```json
{
  "classes": [
    {
      "name": "5IM", "teacher": "Innes McLean", "class_size": 30,
      "adapted": ["Asimenia Chatzinathanail","Bailey Silvers","Reggie Greenwood","Roland Farago","Samuel Nutt","Teddie Richards"],
      "further_adapted": []
    },
    {
      "name": "5LS", "teacher": "", "class_size": 30,
      "adapted": ["Daisy Chase-Williams"],
      "further_adapted": ["Adnan Sadat","Callum Teddy","Hope Dempsey"]
    }
  ]
}
```

## Task 9 — Knowledge organiser (NEXT)

A4 PDF per enquiry. Given once at or near the start of the enquiry; children may add to it as it progresses. Format must be consistent across enquiries so children become familiar with it.

Proposed layout (awaiting Innes confirmation on vocab question — see Open questions):
- Header bar: school/Y5 colour, enquiry title, key question
- Key facts: numbered list (6–8 items)
- Key skills: short bullet list
- Vocabulary: two-column table (word | definition)
- My notes: blank space at the bottom for children to add to

**Open question before building:** should vocabulary definitions be pre-filled from day one, or left blank for children to discover/fill in as the enquiry progresses?

MTP JSON schema addition needed at enquiry level:
```json
"knowledge_organiser": {
  "key_facts": ["...", "..."],
  "key_skills": ["...", "..."],
  "vocabulary": [
    {"word": "universe", "definition": "everything that exists — all space, matter and energy"}
  ]
}
```

Builder: ReportLab A4 PDF. Read the `reportlab-pdf-creation` skill before building — it contains critical layout rules from past QA failures. Output: one PDF per enquiry, named `KO_[enquiry_slug].pdf`. Generated once when the first lesson is built.

## Task 10 — Supporting resources (after Task 9)

Per-lesson printable resources (sort cards, word cards, picture sets, statement sorts etc.). Defined in MTP JSON per lesson under a `resources` array:
```json
"resources": [
  {
    "type": "sort_cards",
    "title": "Scale of the Universe",
    "items": ["Atom", "Human", "Earth", "Solar System", "Galaxy", "Universe"],
    "instructions": "Cut out and arrange from smallest to largest."
  }
]
```

Types to support: `sort_cards`, `picture_set`, `word_cards`, `statement_sort`, `source_extract`.
Output: one PDF per resource per lesson. ReportLab. Read the `reportlab-pdf-creation` skill before building.

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `EnquiryBuilder/build_lp.py` | Final, in repo | No — fetch from repo |
| `EnquiryBuilder/class_lp_groups.json` | Final, in repo | No — fetch from repo |
| `EnquiryBuilder/mtp/y5_astronomy_mtp.json` | In repo, L1 lp block only | No — fetch from repo |
| `outputs/SKILL.md` | Innes pastes in manually | No — delivered this session |

## Open questions / blockers

- **KO vocabulary:** pre-filled definitions from day one, or blank for children to fill in? Must be resolved before building the KO PDF.
- **lp blocks L2–L14:** not yet added to y5_astronomy_mtp.json. Deferred until after KO and resources are done.
- **LP preview injection into teaching slides:** not yet implemented (Outstanding issue in SKILL.md). `Maths/inject_lp_previews.py` is the model.
- **Images not yet generated** for any lesson — full end-to-end build of Astronomy PPTXs still outstanding.

## Immediate next step

Ask Innes whether KO vocabulary definitions should be pre-filled or left blank. Once answered, add the `knowledge_organiser` block to `y5_astronomy_mtp.json`, read the `reportlab-pdf-creation` skill, then build `build_ko.py` and generate the Astronomy KO PDF.
