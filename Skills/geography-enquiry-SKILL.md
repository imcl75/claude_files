---
name: geography-enquiry
description: Use this skill whenever building a Being a Geographer lesson deck (PPTX) as part of a CLF geography enquiry for Innes's Y4/Y5 class at WFA. Triggers on "build lesson [N]", "geography lesson", references to an enquiry name (e.g. "Are England and Brazil different?"), or continuing an existing enquiry sequence. Encodes the standard slide structure, locked-in design rules, and lessons learned from Innes's own edits to the T6W4 Brazil/England enquiry.
---

# Geography Enquiry Lesson Build

## Standard slide structure (every lesson)

1. **Teacher Checklist** — hidden, position 1. Resource prep list + speaker notes flags for slides needing physical resources.
2. **Cover** — "Our Key Question is" layout, correct day/date.
3. **Concepts & Skills** — "Being a Geographer" diagram (template default, no edits usually needed).
4. **Connections** — jigsaw slide from `connections_geo.pptx`, current lesson's piece in colour (duotone matches the geography focus colour), completed lessons shown grey/ticked, future lessons greyed with "Coming up" labels.
5. **Engage your prior knowledge** — You Do Trio layout, 3 questions building toward the new content.
6. **LO** — KS2 What/Why/How 3-box panel.
7. **Recap quiz** (lessons 2+ only) — tests the PREVIOUS lesson's content. Mix of: recall (name/describe), true/false, image-ID (e.g. "which shows lines of longitude, 1 or 2?"), and a scale/comparison question where relevant. Click-to-reveal answers. Build this directly after the LO, before any new content.
8. **Vocabulary/concept slide** (when new technical vocabulary is introduced) — define the new term(s) plainly, then set a trio discussion task that gets pupils applying or sorting examples before the I Do formalises it.
9. **I Do** → **We Do × n** → **You Do** — content slides, animated paragraph-by-paragraph reveal.
10. **Learning Review** — 3 speech bubble questions.

Do not carry forward whatever hidden slides happened to exist in the previous lesson's file as the structural "base" without checking their content first. If reusing a previous lesson as a template, strip slides 1 and verify nothing of the previous lesson's actual content survives into the new build unintentionally.

## We Do activities needing real-world image identification

Default to embedding real stock photographs directly on the slide with click-to-reveal labels (numbered images → "Check answers" reveal), not a separate printable card PDF. Innes prefers this format and supplies/sources the photos himself or via PowerPoint's own stock image search — do not build Claude-rendered illustrations as a substitute unless explicitly asked. If a photo-ID activity is needed and no photos are available yet, build the slide structure with clearly marked placeholder image frames and flag to Innes that photos need adding.

## Continuity checks

Before referencing "your map/work from yesterday" or any carried-over resource in a new lesson, verify that resource actually exists from the previous lesson's build. Don't assume continuity — check the previous lesson's LP and deck for what pupils actually produced.

## Colour/master rule

Entire deck uses the geography focus master, not just content slides. Locking colours:
- Place/Space/Scale = yellow
- Physical Geography = green
- Human Geography = red/pink
- Cultural Awareness = lavender
- Environmental = sage

## Animation rule

Every text item reveals on click using visibility-toggle `presetID="1"` pattern: outer `<p:par delay="indefinite">` (click), inner `<p:par delay="0">`, `clickEffect` for the first item in a click group, `withEffect` (sibling) for any item appearing on the same click. Never generate this XML from scratch each time — clone the working pattern from a previous approved lesson.

## Word rules

Never "trickiest" — use "most challenging". Don't assume prior notes exist unless a previous lesson actually produced them.
