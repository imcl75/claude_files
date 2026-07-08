# Transfer: Image generation enhancements for slide decks

**Generated:** 2026-07-08
**Originating focus:** Session-long PPTX quality tooling work, ending with discussion of image generation as an enhancement to writing lesson slides and other decks.
**Skill in use:** image-generation (to be developed/enhanced)

---

## Status

PPTX quality tooling session concluded. All four showcase PPTXs validated and delivered. A number of specific fixes were applied and pushed to GitHub. The last substantive discussion was about integrating AI-generated images into slide decks more systematically — Innes said it's "sort of covered already, but there are improvements to be made."

---

## What was completed this session

- `validate_pptx_layout.py` — arrow TEXT-SPILL exemption + icon/fact collision detection pushed (`858c697a`)
- `working_memory_starters.py` — `no_wrap=True` fix for `word_list` long words (`cf2bbb25`)
- `rapid_maths_generator.py` — 27 shape PNGs embedded as base64; cone rendered via matplotlib Option A (`0d389330`)
- Writing lesson PPTX: fixed Challenge bar overlap (slide 9), speech bubble overflow (slide 11), LO text size (slide 3), Challenge field size (slide 1)
- ETIW showcase: ghost rectangles removed from slides 1 and 2
- Book cover workflow: planning skill now saves cover to GitHub (`Writing/assets/book_cover.*` + manifest); lesson skill auto-fetches it — no re-upload needed for each lesson build
  - `WriterPlanning/SKILL.md` updated (`9bdc78c1`)
  - `Skills/writing-lesson-pptx/SKILL.md` updated (`bef029b6`)

---

## Decisions locked in

- Book cover is uploaded ONCE at planning stage, stored at `Writing/assets/book_cover.{jpg/png}` in GitHub, fetched automatically by lesson builder
- The lesson builder falls back to most-recently-uploaded file in `/mnt/user-data/uploads/` if GitHub fetch fails
- The book cover appears on slide 1 top-left of every writing lesson

---

## The topic for the new chat: image generation in slides

Innes wants to discuss and improve how AI-generated images are integrated into slide decks. Current state:

- The `writing-lesson-pptx` skill has a `context_image` slide type (see SKILL.md lines ~85–115): generates an AI image based on the lesson focus, downloads it to `/home/claude/context_image.png`, embeds it as a full-slide visual hook after the LO slide
- The `image-generation` skill exists as a standalone tool
- Innes's view: "sort of covered already, but there are improvements to be made"

**Known gaps / likely discussion points** (infer from context — confirm with Innes):
- The `context_image` slide is generated once and may not be used consistently
- No systematic way to add generated images to other slide types (we_do, i_do backgrounds, etc.)
- No caching — if the build reruns, a new image is generated (cost + inconsistency)
- No way to inject images into non-writing decks (rapid maths, working memory, spelling, ETIW)
- Image style/prompt quality may be inconsistent across lessons

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `Skills/writing-lesson-pptx/SKILL.md` | Updated this session | No — in GitHub |
| `WriterPlanning/SKILL.md` | Updated this session | No — in GitHub |
| `/mnt/skills/user/image-generation/SKILL.md` | Current — read at session start | No |

---

## Immediate next step

Read `image-generation` SKILL.md to understand current capability, then open the discussion with Innes about where image generation currently hooks into the slide-build pipeline, what's missing, and what the improvements should look like. Start by asking Innes to describe the gaps he has in mind.
