---
name: enquiry-lesson-builder
description: >
  Builds complete Being a Scientist lesson PPTXs from an enquiry description.
  Use when Innes says "build my science enquiry", "make my science lessons",
  "plan a science unit", "science enquiry for [topic]", "build lessons for
  [topic]", or describes a science enquiry unit. Produces one PPTX per lesson,
  composed from a lesson plan rather than filled into one fixed template, with
  every build checked by an automated verifier before delivery.
  Triggers: "build my science enquiry", "make science lessons", "plan a
  science unit", "science enquiry", "build lessons for".
---

# Enquiry Lesson Builder Skill (Science)

Builds Being a Scientist lesson PPTXs by composing named slide components
from an MTP lesson plan, not by filling text into one fixed 11-slide
template. Rebuilt 11 July 2026 after an audit found the previous two builder
generations diverged from SKILL.md's own rules and from each other — see
"Architecture history" at the bottom for what was wrong and why.

Scope note: this skill currently covers Science only. History and Geography
enquiries are a planned extension (`lib_ooxml.py` is subject-agnostic on
purpose so a `history_registry.py` / `geography_registry.py` can plug in
later without touching the OOXML layer) but are NOT built yet — do not use
this skill for those subjects. Learning-paper generation for the same lesson
is a separate skill (`enquiry-lp`) and is not yet wired into this workflow —
run it as a second step.

---

## How a lesson is built (read this before touching the code)

1. A lesson is an **MTP JSON** object with an ordered `slides` list. Each
   entry is `{"type": "<component type>", ...content fields...}`.
2. Every possible `type` is declared once in `science_registry.py`'s
   `COMPONENTS` dict, tagged `required` / `optional` / `repeatable`. The
   orchestrator (`build_science_lesson.py`) validates the lesson plan against
   this registry BEFORE building anything: unknown types are rejected,
   missing required fields are rejected, missing required component types
   (being_a_scientist / discipline / lo / learning_review) are
   rejected. This is what lets a lesson plan compose a different-shaped deck
   — omit the concept cartoon, run two `wedo_grid` slides back to back,
   whatever the lesson actually calls for — instead of always producing one
   fixed structure with the content swapped out.
3. Each component type is either:
   - **clone_*** — copied from a template file's slide, located by searching
     the template for an anchor text string (never a hardcoded slide index —
     see "Why anchor resolution, not index" below), then overridden with
     this lesson's content in the specific shapes that must always change.
   - **fresh** — built from a named layout with content placed at fixed,
     pre-computed coordinates (`grid_geometry()` etc.), so slides can't
     overlap by construction rather than by luck.
4. `verify_lesson.py` runs on every build and is a hard gate — see
   "Verification" below. A file that fails verification is not delivered.

---

## Workflow

### Stage 1 — Gather MTP inputs
Ask for: key question, science strand, number of lessons, disciplinary focus
per lesson, LO/TIB/ISB per lesson, day/session per lesson, and for each
lesson which content slides it needs (a lesson doesn't have to include every
component type — decide with Innes based on what the lesson actually needs,
referring to the CLF Curriculum Progression Summary for prior learning and
cross-curricular links).

**Never invent this content without getting it confirmed by Innes.**
Round 3 audit (July 2026) found that `t6w7_l1.json`'s key question,
LO/TIB/ISB, We Do grid, You Do provocation, particle-model diagram and
concept-cartoon statements were all written by an earlier Claude session as
placeholder content while the build pipeline was broken, then silently
treated as ground truth by every session since. A follow-up correction
wrongly assumed a docx Innes then uploaded was his own external planning
document and saved it as ground truth (`T6W7_draft_A_NOT_IN_USE.md`) — it
turned out that document was *also* Claude-authored, from a different prior
session, never confirmed by Innes either. A second Claude-authored plan
(pasted from another chat) turned out to be the one Innes actually wanted,
confirmed 2026-07-11, now saved at `EnquiryBuilder/mtp/T6W7_MTP.md`.

The lesson: `generate_mtp.py` validates an MTP JSON's structure; it does not
and must not author the content, and neither should Claude in chat without
Innes explicitly signing off on it. A plan existing as a file, even one that
looks authoritative, is not the same as Innes having confirmed it. Before
building from any MTP: check whether Innes has explicitly confirmed it
(ask if unclear), and check `EnquiryBuilder/mtp/` for one already marked
CONFIRMED before assuming a new one is needed.

### Stage 2 — Write the MTP JSON
One lesson = one JSON object matching the schema `t6w7_l1.json` uses (that
file's structure — slide order and field names — is a valid worked example;
its *content* is placeholder text with no relation to the confirmed T6W7 MTP
and needs a full rewrite against `EnquiryBuilder/mtp/T6W7_MTP.md` before it
can be trusted as a regression fixture again). Note `T6W7_MTP.md` is a
summary-level plan (LOs, phase headlines, image plan per lesson), not a
full scripted lesson — slide bullet text and provocation wording need
drafting from those headlines and should be checked with Innes before
build, not invented wholesale. Validate every field the chosen component
types require is present — the orchestrator will refuse to build otherwise,
with a specific error naming the missing field.

### Stage 3 — Generate images
For every slide with an `image_path` field: generate via Higgsfield
(`nano_banana_pro` model), 1:1 for grid items, 16:9 for provocation/full-slide
images. Download immediately — Higgsfield CDN URLs do not persist across
sessions. Never point `image_path` at a placeholder; the orchestrator will
raise an error rather than silently deliver a slide with a missing image, but
it cannot tell a genuinely thin/wrong image from a good one — that's a human
check.

### Stage 4 — Build
```
python3 build_science_lesson.py <mtp.json> <templates_dir> <out.pptx> <manifest.json>
python3 fix_pptx_ooxml.py <out.pptx>          # Fix #6 strips SharePoint customXml — always run this
python3 verify_lesson.py <out.pptx> <mtp.json> <manifest.json>
```
If `verify_lesson.py` prints `VERIFY: FAIL`, fix the reported issue and
rebuild. Do not hand-edit the output PPTX to silence a failure — fix the
registry/orchestrator/MTP JSON so the next build is correct too. **A file is
only "delivered" once verification prints `VERIFY: PASS`.**

### Stage 5 — Deliver
Zip and hand over. Mention explicitly if any image is a placeholder rather
than a real generated illustration — never let that be discovered by Innes
after the fact.

---

## Component registry (`science_registry.py`)

There is no separate cover/title slide. Slide 1 of every lesson is the `lo`
component — its source (`KQ_LO.pptx`) already carries "Key Question" as its
own heading above the three learning panels. A standalone cover was built
and then explicitly rejected by Innes (11 Jul 2026, see Architecture history)
— do not reintroduce one.

| type | presence | source |
|---|---|---|
| `lo` | required | clone, anchor `"What am I learning?"` — this is slide 1 |
| `being_a_scientist` | required | clone, anchor `"Being a Scientist"` |
| `discipline` | required | clone, anchor = `"What is {strand}?"` |
| `lo` | required | clone, anchor `"What am I learning?"` |
| `discipline` | required | clone, anchor = `"What is {strand}?"` |
| `wedo_hook` | repeatable | fresh, layout `We do` |
| `wedo_grid` | repeatable | fresh, layout `We do - Blank` |
| `ido_diagram` | repeatable | fresh, layout `I Do - Blank` |
| `youdo_provocation` | repeatable | fresh, layout `You do Ind - Blank` |
| `youdo_task` | repeatable | fresh, layout `You do Ind` |
| `concept_cartoon` | optional | clone, anchor `"turn on the light"` |
| `learning_review` | required | clone, anchor `"Learning Review"` |

Template files, as they actually exist in `EnquiryBuilder/templates/` (verified
11 Jul 2026 — do not trust older commit messages, they refer to filenames
that no longer exist):

- `Being_a_Scientist_slide_deck.pptx` — Being a Scientist wheel (slide 2),
  four discipline slides (slides 4-7: Biology/Physics/Chemistry/Earth&Space),
  concept cartoon template (slide 11). This is the file previous sessions
  called `missing-sci.pptx` and asked Innes to re-upload every session —
  **it is already committed to the repo under this name; stop asking him to
  re-upload it.**
- `science-example.pptx` — carries every named content layout (`I do`,
  `We do`, `You do Ind`, `*-Blank` variants, `Blank`) plus the Learning
  Review source slide (slide 17).
- `KQ_LO.pptx` — LO panel source (1 slide).

## Why anchor resolution, not a hardcoded slide index
Confirmed twice now: template files get renamed and internally renumbered
between sessions without every consumer being updated (the old
`sci_template.pptx` / `sci_example.pptx` / `missing-sci.pptx` names in earlier
SKILL.md revisions no longer match anything in the repo; the discipline
slides moved from "slides 1-6" to "slides 2, 4-7" at some point). A script
that clones "slide N" from a template will silently pull the wrong slide the
next time this happens and nobody will notice until the delivered deck is
wrong. `find_slide_by_anchor()` in `lib_ooxml.py` searches the template's
actual text content for a known anchor string and only uses the hardcoded
`hint` index as a fast path it double-checks — if the hint is wrong it
resolves correctly anyway and prints a loud warning so the drift gets fixed
at the source (`science_registry.py`) instead of silently working around it
forever.

## Concept cartoon
The template's central image is a cat-in-a-doorway illustration (a leftover
from a Light unit) and the three speech bubbles carry that unit's text. The
three small "learner" avatar pictures next to the labels are generic child
portraits reused across any topic — confirmed by opening them — and do not
need to change. `build_concept_cartoon()` always overwrites the three speech
bubble texts from the lesson's `learners` field and always replaces the one
named central image (`Picture 7`) with `image_path`; it raises an error
rather than deliver the slide if `image_path` is missing, so the cat/light
template content can never survive into a delivered file by omission.

## LO slide — known duplicate-panel bug
`KQ_LO.pptx` slide 1 carries two complete LO panels at pixel-identical
positions (confirmed by comparing shape coordinates — ids 6-22 sit at the
exact same left/top/width/height as ids 23-41). The first is a stale draft
whose dynamic content boxes are unfilled generic placeholders; the second is
the live one with the real `TextBox 38/39/40` boxes. `build_lo()` deletes the
stale group (`LO_STALE_GROUP_IDS`) before setting text. `verify_lesson.py`
additionally checks for the stale group's tell-tale shape name
(`Text Placeholder 33`) on every build so this cannot silently come back.

## Animation — the hide-at-start bug
The previous "working" builder's animation functions violated this skill's
own documented rule: they emitted an explicit hide-at-start `<p:par>` block
before the click-reveal sequence, which is exactly what produces "TRIGGER:
UNNAMED" in PowerPoint's animation pane. `lib_ooxml.animate()` now emits only
the clean `<p:seq>` pattern (`restart="never"`, no hide block — PowerPoint
hides `clickEffect` entries automatically). `verify_lesson.py` scans the
timing XML of every slide and fails the build if the forbidden pattern or
`restart="whenNotActive"` reappears.

## Repair dialog on open
Caused by `customXml/` parts (SharePoint/Teams metadata) surviving in the
package. `fix_pptx_ooxml.py` Fix #6 strips these — confirmed working: running
it against the T6W7 L1 build removed 9 customXml parts that were genuinely
present. `verify_lesson.py` checks the final zip for any stray `customXml/`
entry and fails the build if Fix #6 was skipped.

---

## Verification (`verify_lesson.py`) — mandatory, not optional

Every build must pass before it is called delivered:

1. Slide type sequence matches the MTP JSON exactly.
2. All `required` component types are present.
3. No banned template text survives anywhere in the file (light/cat concept
   cartoon strings, the stray "insert any other states of being icons" editor
   note, unfilled "Text box" placeholders).
4. Concept cartoon: the three learner statements from the MTP JSON are
   present verbatim, and a real (non-empty) central image exists.
5. LO slide: the stale duplicate panel's tell-tale shape name is absent.
6. Geometric overlap: every pair of same-kind text-bearing shapes on a slide
   is checked for bounding-box overlap (background-panel + caption-inside-it
   pairs are correctly ignored — only same-kind clashes are flagged, which is
   what a real bug looks like).
7. Animation XML has no hide-at-start anti-pattern and the correct root node.
8. Every slide that declared an `image_path` (or grid `items`) has that many
   real picture shapes.
9. No `customXml/` parts remain (repair-dialog risk).

Run it, read every failure line — it names the slide and the exact reason —
fix the cause, rebuild, re-verify. Do not deliver on a `VERIFY: FAIL`.

---

## LO grammar rules
- **LO**: infinitive verb phrase — "compare and group materials…"
- **TIB**: first person present — "I understand how…" / "I know that…"
- **ISB**: progressive "-ing" — "creating a sorting table…"

## MTP JSON schema
See `t6w7_l1.json` in the repo for a complete, verified worked example
(builds clean, passes all verifier checks bar one noted pre-existing
template cosmetic detail on the Chemistry discipline slide, unrelated to
this skill's build logic — see Architecture history).

---

## Architecture history — what was wrong and why this was rewritten

Audited 11 July 2026 after a session that produced no usable progress despite
extensive feedback. Two prior builder generations existed in the repo and
neither matched what SKILL.md documented:

- `build_science_lesson.py` (v3, earlier generation): data-driven and
  general-purpose in shape, but cloned content slides by hardcoded slide
  index from template files that have since been renamed/renumbered, so its
  source map was stale and it also cloned I Do/We Do/You Do slides wholesale
  — the exact thing this skill's own CRITICAL RULES say never to do, because
  it pulls in unrelated media and shapes from the source slide.
- `build_l1_final.py` (T6W7 generation): fixed the cloning problem correctly
  (content slides built fresh from named layouts) but hardcoded one lesson's
  content inline with no JSON input, so it could only ever produce that one
  lesson, and its own "missing-sci" clone loop dumped all 6 template slides
  in verbatim with zero text override — which is the direct, provable cause
  of the concept cartoon shipping with light/cat content every time. It also
  used the forbidden hide-at-start animation pattern this skill's rules
  already said not to use.

Neither script had any automated check of its own output. QA was "render to
PDF and look at every slide," which is exactly the kind of check that misses
a wrong-but-plausible slide late in a long session.

This rewrite (`lib_ooxml.py` + `science_registry.py` +
`build_science_lesson.py` v4 + `verify_lesson.py`) keeps the proven low-level
OOXML plumbing from `build_l1_final.py` (atomic rId remap, name-based layout
resolution — that machinery was correct) and replaces everything above it
with a lesson-plan-driven, registry-based orchestrator plus a mandatory,
specific, automated verification gate. Every bug found in this audit has a
corresponding named check in `verify_lesson.py` so it cannot silently
regress the way it did across the previous sessions.

Not done yet, deliberately out of scope for this pass (Innes asked to
concentrate on Science first): History and Geography component registries,
and wiring the `enquiry-lp` learning-paper skill into Stage 5 so the full
resource set (deck + LP) comes out of one workflow.

### Round 2 (same day) — real bugs found only by rendering and by testing

The first rebuild above passed its own verifier but still failed for Innes in
real PowerPoint. Two mistakes:

1. **A self-designed cover slide was built and shown to Innes without
   asking first.** Rejected outright — "NEVER add a slide of your own
   design, use my template." Fixed by removing the `cover` type entirely.
   There is no cover: `lo` (KQ_LO.pptx, which already carries "Key Question"
   as its own heading) is slide 1.
2. **Nothing had been rendered and looked at before delivery** — the
   verifier checks structure and text, not what a slide actually looks like.
   Rendering via LibreOffice (`soffice --headless --convert-to pdf` then
   `pdftoppm`) and viewing the output caught: concept-cartoon speech-bubble
   text overflowing its box (the template's bubbles are sized for their
   original short text; a longer lesson-specific statement needs
   `force_shrink_to_fit()` applied after `set_text()` — now done
   automatically for concept cartoon bubbles), and confirmed that the
   speech-bubble/label near-touch on that same slide and a text-frame overlap
   on the Chemistry discipline slide are both present in the **untouched
   original template file** — proven by rendering `Being_a_Scientist_slide_
   deck.pptx` slide 11 directly with zero changes and finding the same
   overlap. These two are template-authoring tightness, not build defects,
   and are not fixable from the build script.

Innes separately supplied `PPTX_Repair_Diagnosis_Guide.md` — a diagnostic
script from a prior session that catalogues 7 known repair-dialog causes
with a working detector for each, plus checks for duplicate shape ids,
`sldIdLst`/slide-count mismatches, animation targets pointing at shapes that
don't exist, and non-numeric relationship ids. Running it against this
skill's output found none of the 7 known causes present (confirmed
`fix_pptx_ooxml.py` already implements all 7, including the SharePoint
customXml strip). It did surface one real, different issue via a
`python-pptx` resave diff: `replace_image()` was leaving the old image
physically in the package after swapping it for a new one — in one case,
the exact cat/light image the concept cartoon was supposed to fully replace
was still sitting in the file, just unreferenced. Fixed with
`strip_orphaned_media()`, now run as the last step before every build is
zipped. The entire diagnostic script (`EnquiryBuilder/diagnose.py`, kept
verbatim from Innes's file) has been folded into `verify_lesson.py` as five
permanent checks so this whole class of bug is checked on every build, not
run manually when something goes wrong.

**Still open:** whether this actually stops PowerPoint's repair dialog has
not been confirmed in real PowerPoint — nothing in this sandbox can trigger
it. If it still happens, the next step is the repaired file back from Innes
to diff against what was delivered, per the diagnosis guide's own
recommended next step when the known-cause checklist comes back clean.

### Round 3 (same day) — wrong source slide and a missing slide type

Innes sent two screenshots proving two more concrete defects, both traced
back to the same class of mistake as Round 1: trusting an anchor match
without checking it landed on the right slide.

1. **`being_a_scientist` was cloning the wrong slide.** The anchor text
   `'Being a Scientist'` matched slide 2 of `Being_a_Scientist_slide_
   deck.pptx` — a caption sitting next to a small icon — instead of slide 3,
   which holds the actual Areas of Study / Skills wheel diagrams Innes
   wanted. Fixed by re-anchoring to `'Areas of Study'`, text unique to
   slide 3. Slide 3 carries no title or icon of its own, so
   `build_being_a_scientist()` now adds both: a title via `tbox()` at fixed
   safe coordinates (an initial attempt used `title_sp()`, which inherits
   the layout's placeholder position and landed directly on top of the
   "Areas of Study" label — caught by rendering, fixed by switching to
   explicit coordinates) and the scientist icon, extracted from slide 2 via
   a new `extract_image_by_shape_name()` helper since slide 3 doesn't carry
   its own copy.
2. **A whole slide type was missing.** Nested inside slide 2's "Group 14"
   sat a KQ + Challenge intro slide with its own key question and challenge
   text boxes, never surfaced as a component because slide 2 had only ever
   been read for its caption. Added as a new `kq_challenge` component,
   cloned from slide 2, with the leftover 21st-Century-Skills content
   removed and `TextBox 16` / `TextBox 17` overridden with the lesson's key
   question and challenge. First strip attempt only removed part of that
   content — a second, separate icon grid (`Group 3`, four nested pictures)
   was still showing in the render, only found by opening the rendered
   PNG and reading "Collaboration" off one of the icons. The strip list now
   includes that group's id.
3. **Deck order was wrong.** Correct L1 order is `being_a_scientist` first,
   `kq_challenge` second, `discipline` third, `lo` fourth, then content
   slides — not `lo` first as Round 2 had it. `t6w7_l1.json` and
   `REQUIRED_TYPES` updated accordingly.

**Confirmed by rendering:** slide 1 has a clean title and icon with no
overlap; slide 2 matches Innes's reference format with the icon grid fully
removed. **Not confirmed:** the Areas of Study / Skills wheel diagrams on
slide 1 are SmartArt, and LibreOffice cannot render SmartArt reliably — it
shows as scattered icons with no colour or labels even though all ten
underlying diagram XML parts (`data1.xml`, `layout1.xml`, `colors1.xml`,
`quickStyle1.xml`, `drawing1.xml` and their `2` variants) are present and
correctly copied by `clone()`. This is a rendering-tool limitation, not a
data-loss bug, but it means the wheel diagrams have not been visually
confirmed correct — only structurally confirmed. Also: the `kq_challenge`
slide only has one avatar image available from the donor slide, not four
like Innes's reference example, which likely drew its extra avatars from
different source material not present in this deck's templates.
