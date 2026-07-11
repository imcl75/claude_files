# Learning paper content principles

Cross-subject rules for what goes ON a learning paper, distinct from
`LearningPaper/label-spec.md` (which governs the label's own measurements)
and the `learning-paper` skill (which governs build mechanics). This file
is about content decisions - what to include and why.

---

## If the text names a resource, put the resource on the page

Confirmed as a standing rule by Innes (11 Jul 2026), from the T6W7 L1
sorting LP: the task text said "using the particle model to help you" but
the particle model diagram itself wasn't anywhere on the page - pupils
were told to use something they couldn't see.

Rule: any instruction, LF, I can statement, or task text that names a
specific resource, model, diagram, map, image, or reference object must
have that resource actually present on the LP - not just named. A pupil
reading the page should never have to recall or imagine the thing they're
told to use.

Applies to (non-exhaustive, check every LP against this):
- "use the particle model" -> include the particle diagram
- "use the map to..." -> include the map, or the relevant extract of it
- "use the timeline to..." -> include the timeline
- "compare using the photos on the board" -> include the photos, not just
  a reference to them being on the board (the board won't be visible when
  the pupil takes work home, or the paper is used for a follow-up session)
- "use the word bank" -> the word bank itself already satisfies this one,
  it's a positive example of the pattern already followed correctly

When the resource is large (e.g. a full map, a big diagram), don't shrink
it illegibly to fit - either crop to the relevant section, or size it at
a legible minimum and let it push other content down, re-checking the
page still fits within the two-slide (pupil + marking station) format
before finalising.

Implementation note: `Science/build_t6w7_l1_lp.py`'s `add_reference_image()`
helper places an image at native aspect ratio capped by a max height,
centred in the content width - a reusable pattern for this.
