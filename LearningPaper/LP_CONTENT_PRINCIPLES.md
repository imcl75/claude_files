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

---

## Pupil-page readability pass (sizes, label scale, write-line spacing)

Confirmed as standing rules by Innes (11 Jul 2026), same T6W7 L1 LP, after
seeing a first readability pass in real PowerPoint. All four are
mechanical/structural, not one-off content choices - apply to every LP.

**Learning label must be scaled down from the pipeline's natural render.**
`label_builder.build_enquiry_label()` always embeds the label at its fixed
natural width (`LL_W`, ~3.9"). At that size, on an A4 LP, it reads as too
large relative to the rest of the page. Innes's own resize landed on
~70.7% of natural width/height (aspect ratio preserved) - resize the
embedded picture after calling the builder (grab the shape it just added,
scale `left`/`top`/`width`/`height` together) rather than assuming the
natural size is correct. See `LABEL_SCALE` in `build_t6w7_l1_lp.py`.

**Pupil-page text must be sized for children reading their own paper, not
compressed to fit.** Marking station stays compact (it's for the teacher).
Pupil page confirmed target sizes from Innes's own edit: section headings
14-16pt, instructions 10.5-12pt, table header/cell text 10pt, word bank
12pt. These aren't hard limits for every LP (content volume varies) but
are the reference point - if a pupil-page LP is coming out smaller than
this without a specific reason, it's probably wrong.

**Any writing-line block needs a full line-gap of clearance before the
first line, not just after it.** The gap between lines (0.8cm / 0.315")
must also be the minimum gap between the preceding instruction text and
the first line itself - otherwise there's no room to actually write on
that first line, it sits directly under the text above it.

**Fill the page - don't leave the bottom third blank.** If content ends
partway down an A4 page with clear empty space below, that's a signal
sizes are too small or spacing too tight, not that the LP is "done".
Bigger pupil-page text and a bigger reference image (per the two rules
above) should be the first things tried before adding more content just
to fill space.

**Table rows must grow for content that wraps, not clip it.** A fixed row
height chosen for the common case (most material names fit one line) will
clip a longer name's second line at the larger pupil-page font size (e.g.
"Balloon (filled with air)" wrapping to two lines). Row height should be
`max(base_row_height, wrap_line_count * line_height + padding)`, computed
per row, not a single fixed value applied to every row. This is the same
category of bug as `force_shrink_to_fit`'s original fontScale issue in
`lib_ooxml.py` and the earlier heading/instruction/word-bank fixes in this
same file - a fixed box size for text whose wrap count wasn't checked.

**12pt is the default reading size on a pupil-facing LP.** Confirmed by
Innes (11 Jul 2026): 12pt is comfortable for a Y4 pupil reading their own
paper. Smaller sizes are fine for short/compact content (table headers,
brief cell labels) where space genuinely requires it, but never for
extended instructional text or prose - those default to 12pt, not
whatever happens to fit. `instruction()` in `build_t6w7_l1_lp.py` defaults
to `size_pt=12` for exactly this reason - don't override it smaller
without a real space constraint forcing it.

---

## QA limitation: no real Twinkl Cursive Looped font in this environment

Found 11 Jul 2026, same T6W7 L1 LP session. There is no Twinkl Cursive
Looped font file anywhere in the repo, and it isn't installed on the
sandbox system either (`fc-list` finds nothing). Every LibreOffice-based
QA render (`libreoffice --headless --convert-to pdf` then screenshot) is
therefore rendering LP body text in a substitute font, not the real one -
and the substitute has been observed to be wider, causing text to appear
to wrap when it doesn't in Innes's actual PowerPoint.

Confirmed directly: "Balloon (filled with air)" (25 characters) wraps to
two lines in every LibreOffice QA render of the T6W7 L1 LP's material
column (10pt, 1.74" wide), but Innes's own PowerPoint screenshot shows it
fitting on one line. The wrap-estimate heuristic in `_wrap_line_count()`
was recalibrated against this real evidence (ratio 0.52 -> 0.46), but the
LibreOffice screenshots themselves will keep showing the old, wider
wrapping regardless of that fix, because the substitute font hasn't
changed.

**Practical implication**: LibreOffice QA screenshots remain useful for
checking gross layout - are things positioned sensibly, is there an
obvious overlap, does the page fill reasonably - but are NOT reliable
evidence for whether a specific line of Twinkl Cursive Looped text fits
in a specific box width. For that specific question, real evidence from
Innes's own PowerPoint (a screenshot, or a file he's edited) is the only
trustworthy source. Don't re-litigate a wrap/fit call based on a
LibreOffice render alone if Innes has already shown real-PowerPoint
evidence to the contrary - the render is wrong, not his evidence.
