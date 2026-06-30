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

## LO slide third box (idx14) — known overlap fix

The "I will be successful by…" header text wraps to two lines when long, but the body placeholder for that third box uses the same default y-position as the other two columns, causing overlap. Locked-in fix: apply an explicit override ONLY to the idx=14 placeholder shape — `x=8979945, y=5200000, cx=2559050, cy=984000`. Leave the other two LO boxes (idx10, idx13) on their default inherited position. When writing XML to apply this, never use a generic `<p:sp>...</p:sp>` regex to isolate a single shape if other shapes in the file declare `xmlns:` attributes on their opening tag — the lookahead won't recognise `<p:sp xmlns:p="...">` as a shape boundary and will silently merge multiple shapes into one match. Rebuild the slide's shapes from defined Python functions with the override passed as a parameter to only the target shape, rather than doing a post-hoc string find-and-replace across the whole slide XML.

## Concept-teaching slides need explanation before application

When introducing a new spatial or technical concept (e.g. topography, biome, climate zone), a bare definition followed immediately by a discussion/apply task is not enough. Structure these slides as: (1) plain-language definition, (2) two named real-world examples the children can picture, (3) how to recognise it on a map/image if relevant, (4) only then the application or discussion task. Don't combine vocabulary recall (e.g. quick word/definition pairs for easier terms) with concept-teaching (e.g. topography) on the same slide — split them: a quick vocabulary slide for terms that don't need much unpacking, and a separate, fuller slide for any concept that needs real explanation.

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
