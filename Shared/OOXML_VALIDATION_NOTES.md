# OOXML validation notes

Reference for any skill that hand-builds or edits `.pptx` XML by direct zip
manipulation (not via python-pptx or a real save from PowerPoint). Every
entry here was confirmed against real PowerPoint on Innes's Mac, not
guessed - either PowerPoint's repair dialog fired and the cause was traced
by diffing against his own PowerPoint-repaired file, or PowerPoint's repair
silently rewrote/stripped the construct, which is itself proof the original
was invalid rather than just a value it disagreed with.

Check this file before writing new XML-generation code. `fix_pptx_ooxml.py`
in this folder applies most of these fixes automatically as a post-process
- run it on any hand-built pptx before delivery regardless.

---

## Confirmed invalid constructs

**`<p14:sectionLst>` ghost slide ids.** The Sections panel data in
`presentation.xml` lists slide membership by `sldId`. If a source template
copied into a build's working directory once had a different, larger slide
set, its `sectionLst` can carry ids that no longer exist in the real
`<p:sldIdLst>`. PowerPoint validates every sectionLst id against the real
slide list on open and repairs on any that don't resolve. Fix: strip ids
not present in `sldIdLst`; reclaim any real id left with no section by
appending it to the last section in deck order. `fix_pptx_ooxml.py` Fix #8.

**`docProps/app.xml` stale summary metadata.** `<Slides>`, `<Notes>`,
`<HiddenSlides>` counts and the `HeadingPairs`/`TitlesOfParts` vt:vector
pair must match the real assembled package. If these are carried over
unmodified from a working-directory source file, PowerPoint cross-validates
them against the actual package on open and treats a mismatch as
corruption. Fix: regenerate from the real slide/notes/hidden counts and
real per-slide titles. `fix_pptx_ooxml.py` Fix #7.

**`<a:normAutofit fontScale="N">` stacked on an already-fitted `sz`.**
PowerPoint renders text at `rPr/sz * fontScale`, not `sz` alone. If you
compute an exact fitting font size yourself and write it directly onto
every run's `rPr/sz`, do not also set `fontScale` - that applies the same
shrink a second time. Only set `fontScale` if `rPr/sz` still holds the
original/nominal size and `fontScale` alone represents the current shrink.
This isn't a repair-dialog trigger (PowerPoint renders it fine) but it is a
real visible bug: text displays far smaller than the box has room for.
`lib_ooxml.py` `force_shrink_to_fit()`; strip via `fix_pptx_ooxml.py`
Fix #9.

**`<a:masterClr/>` is not a real OOXML element.** The correct empty
element inside `<p:clrMapOvr>` for "use the master's own colour map" is
`<a:masterClrMapping/>`. Confirmed by its own correct, untouched use
elsewhere in the same package (every slideLayout and notesSlide), and by
PowerPoint's repair silently rewriting `masterClr` → `masterClrMapping` on
every affected slide - a rewrite, not a value correction, meaning the
original didn't parse as valid content at all. `fix_pptx_ooxml.py`
Fix #10a.

**`autofit="normAutofit"` is not a valid attribute of `<a:bodyPr>`.**
`CT_TextBodyProperties` has no `autofit` attribute. Autofit is only ever
expressed as a child element: `<a:normAutofit/>`, `<a:noAutofit/>`, or
`<a:spAutoFit/>`. PowerPoint's repair silently stripped the attribute
entirely on every affected slide rather than reinterpreting it. Fix:
`<a:bodyPr wrap="square"><a:normAutofit/></a:bodyPr>`, never an attribute.
`fix_pptx_ooxml.py` Fix #10b.

**Non-standard media filenames.** Media parts should be named
`imageN.ext` inside `ppt/media/`. Other names (e.g. `conn_col.emf`) can
trigger repair. Rename and update every `_rels` reference that points to
the old name. `fix_pptx_ooxml.py` Fix #1.

**notesSlide back-references after slide renumbering.** A notesSlide's
own `_rels` file must point at the slide that actually owns it, not a
stale slide number left over from an earlier renumbering pass.
`fix_pptx_ooxml.py` Fix #2.

**Empty `<a:r>` runs in notesSlides.** A pptxgenjs quirk - empty runs
(`<a:r><a:rPr.../><a:t></a:t></a:r>`) in notesSlide XML should be removed
outright. `fix_pptx_ooxml.py` Fix #3.

**notesMaster theme reference must resolve.** If `notesMaster1.xml.rels`
points at `theme/theme1.xml` but the notesMaster actually needs its own
theme part, add `theme2.xml` (a copy) and repoint the relationship, adding
the matching `[Content_Types].xml` override. `fix_pptx_ooxml.py` Fix #4.

**Non-numeric relationship IDs.** Every `Id` in a `.rels` file should be
`rId` followed by digits only. IDs like `rIdKQ` (alphabetic suffix) cause
repair. Rename to the next free numeric `rIdN` and update every reference
to the old id, in both the `.rels` file and the part that uses it.
`fix_pptx_ooxml.py` Fix #5.

**SharePoint/Teams `customXml/` metadata.** Files that passed through
SharePoint or Teams carry `customXml/` parts referencing external schemas
(`schemas.microsoft.com/sharepoint`, `/office/2006/metadata`,
`/office/infopath`) that PowerPoint can never validate, causing persistent
repair on every open. These parts carry no real document content - strip
them entirely, including their relationships in `_rels/.rels` and
`ppt/_rels/presentation.xml.rels`, and their `[Content_Types].xml`
overrides. `fix_pptx_ooxml.py` Fix #6.

**Genuine SmartArt (`ppt/diagrams/`) sourced from certain decks.** Not an
XML-correctness issue - some source SmartArt content crashed PowerPoint
outright on open. Where this happens, swap to an image-based source file
for that content rather than trying to repair the diagram XML.

---

## Confirmed false positive - do not trust

**`diagnose.py`'s "BROKEN RELS" check, for the root `_rels/.rels` file
specifically.** Its base-path computation for relationships declared in
the package-root `.rels` file evaluates to a bare leading slash (`/`),
so it resolves targets like `docProps/app.xml` as `/docProps/app.xml`,
which never matches the zip's real entry name (no leading slash) - and
flags it as broken every time, even in a completely valid package.
Confirmed by running it against two of Innes's own PowerPoint-repaired,
confirmed-working files and getting the identical false positive on both.
This specific check (4 relationships from `_rels/.rels`) should be ignored
until the script itself is fixed; the rest of `diagnose.py` hasn't been
audited to the same standard.

---

## Cosmetic differences seen after PowerPoint's own repair - not defects

When diffing a delivered file against Innes's own PowerPoint-repaired
version of it, these show up every time and are just PowerPoint
reserialising the package, not evidence of anything wrong in the original:

- Media file renumbering (`imageN.ext` renamed to a different `N`) and
  extension changes when duplicate/orphaned media gets pruned.
- notesSlide renumbering (`notesSlide3.xml` → `notesSlide1.xml` etc), with
  matching `_rels` and `[Content_Types].xml` updates - as long as the
  numbering is internally consistent within the delivered file, this is
  not a defect on its own.
- Relationship ID renumbering (`rId27` → `rId2` etc) - PowerPoint
  renumbers to sequential low numbers on save; the numeric value has no
  meaning as long as ids are unique and correctly referenced.
- xmlns attribute declaration order on root elements (e.g. `<p:sld
  xmlns:p=... xmlns:a=...>` vs `xmlns:a=... xmlns:r=... xmlns:p=...`) -
  attribute order has no XML semantic meaning.
- `<p:bldP>` entry order within `<p:bldLst>`, and PowerPoint adding
  `animBg="1"` to entries it decides are background-only animations - a
  live PowerPoint interpretation, not something the build controls.
- XML declaration quote style (`'1.0'` vs `"1.0"`) and numeric character
  reference form (`&#10;` vs `&#xA;`) - both valid, PowerPoint normalises
  on save.

---

*Maintained alongside `EnquiryBuilder/SKILL.md`'s dated Round entries,
which hold the full narrative/evidence for each finding. This file is the
distilled, non-narrative lookup version - update it whenever a Round entry
confirms a new real OOXML rule or a new false positive.*
