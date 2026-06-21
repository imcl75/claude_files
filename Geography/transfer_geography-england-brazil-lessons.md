# Transfer: Geography England vs Brazil — lesson decks + learning papers

**Generated:** 2026-06-21
**Originating focus:** Building Being a Geographer lesson slide decks for the Y4 "Are England and Brazil different?" enquiry, then delivering the learning papers.
**Skill in use:** none (manual build — geography skill not yet formalised)

---

## Status

Lesson 1 (Locating Brazil) fully built, iterated through many rounds of review and now approved by Innes. Final file at `/mnt/user-data/outputs/T6W4_L1_Geographers_Locating_Brazil.pptx`. Working directory at `/home/claude/geo_l1_v4/` (unpacked). Lessons 2 and 3 not yet started. Learning papers not yet started.

## What's been produced

- `/mnt/user-data/outputs/T6W4_L1_Geographers_Locating_Brazil.pptx` — **final (approved)**
- `/mnt/user-data/outputs/Geography_Enquiry_England_Brazil.docx` — **final** — 14-lesson plan with geography focus labels per lesson

## Decisions locked in

**Slide structure (every lesson, in order):**
1. Teacher Checklist — hidden slide, position 1, before all pupil-facing slides
2. Oracy Framework — hidden
3. Sentence Stems — hidden
4. Whole Class Feedback — hidden
5. Cover — "Our Key Question is" layout
6. Concepts & Skills — "Being a Geographer" diagram
7. Connections — jigsaw slide (copied from connections_geo.pptx for the relevant focus area)
8. LO — "KS2 What, Why, How" layout (3-box panel)
9. Engage your prior knowledge — "You Do Trio" layout
10. I Do → We Do × n → You Do — content slides
11. Learning Review — 3 speech bubbles

**Colour/master rule:** ENTIRE deck uses the geography focus master, not just content slides. L1 = Place/Space/Scale = yellow (`master[0]`, layout filenames `slideLayout1–14`). Physical Geography = green (`master[2]`). Human Geography = red/pink (`master[1]`). Cultural Awareness = lavender (`master[4]`).

**Animations:** Every text item reveals on click using visibility-toggle `presetID="1"` pattern — exact structure from Innes's working slides (slides 9/10/11 of L1). Structure: outer `<p:par delay="indefinite">` (click), inner `<p:par delay="0">`, `clickEffect` for first item, `withEffect` (sibling) for any item appearing with same click. `prevCondLst`/`nextCondLst` use `evt="onPrev/onNext"` + `<p:sldTgt/>`. Jigsaw pieces and their text labels are `withEffect` pairs.

**Connections slide:** Copy the relevant slide from `connections_geo.pptx` (stored at `/home/claude/connections_geo.pptx`). Slide 1=Physical/green, Slide 2=Place-Space-Scale/yellow, Slide 3=Human/pink, Slide 4=Cultural/lavender, Slide 5=Environmental/sage. Apply yellow duotone (`<a:duotone><a:srgbClr val="FFC000"/><a:prstClr val="white"/>`) to the coloured piece (rId3 in the source). Click sequence: Picture 6 + TextBox 8 FIRST (= TODAY/current lesson), then remaining pairs in positional order. EMF files won't render in LibreOffice — expected, works in PowerPoint.

**Jigsaw click pairs (correct positional order):**
```
Click 1: Picture 6 (id=7, coloured) + TextBox 8 (id=9)   ← TODAY
Click 2: Picture 2 (id=3, grey)     + TextBox 4 (id=5)
Click 3: Picture 11 (id=12, grey)   + TextBox 13 (id=14)
Click 4: Picture 17 (id=18, grey)   + TextBox 18 (id=19)
Click 5: Picture 21 (id=22, grey)   + TextBox 22 (id=23)
Click 6: Picture 24 (id=25, grey)   + TextBox 25 (id=26)
```

**Jigsaw beyond 6 lessons:** NOT yet resolved. For 14-lesson enquiry, agreed approach is to show only the current phase's lessons (3–5 per deck), not all 14. To be designed when building L2+.

**LO slide (ph10/ph13/ph14):** Content text strips the redundant prefix — box headers say "I am learning to…" / "This is so…" / "I will be successful by…" so content text starts with the completion only (e.g. "locate Brazil on a world map…"). ph14 position overridden: `y=5200000, cy=984000, x=8979945, cx=2559050`. Font size 1400 (14pt) on all three boxes.

**Word rules:** Never "trickiest" — use "most challenging". Never "and your notes" in L1 (no prior notes exist).

**Teacher checklist:** Hidden slide at position 1 listing map/resource prep requirements. Speaker notes on slides that need physical resources prepared.

**Template files in Claude's working environment:**
- `/home/claude/geographers_template.pptx` — unpacked at `/home/claude/geo_unpacked/` (may need re-extracting)
- `/home/claude/connections_geo.pptx` — unpacked at `/home/claude/conn_unpacked/`
- L1 working dir: `/home/claude/geo_l1_v4/` (unpacked, current state)

## T6W4 lesson schedule

| Lesson | Date | Day | Geography Focus | Master |
|---|---|---|---|---|
| L1 | Tue 23 June | Tuesday | Place, Space & Scale | yellow (`master[0]`) |
| L2 | Wed 24 June | Wednesday | Physical Geography | green (`master[2]`) |
| L3 | Fri 26 June | Friday | Physical Geography | green (`master[2]`) |

## L2 and L3 content (to be built)

**L2 — Physical geography of Brazil: biomes and climate (Wed 24 June)**
- LO: describe Brazil's biomes and climate zone using geographical vocabulary
- Because: physical geography shapes what a country looks like and how people live there
- Success: labelled diagram or structured paragraph explaining Brazil's biomes (desert, tundra, tropical rainforest), climate zone and vegetation belt
- I Do: three Brazilian biomes; tropical climate zone; address misconception "rainforest soil is fertile" (nutrients in vegetation not soil)
- We Do: match biome photo cards to descriptions; locate biomes on Brazil map; class compares results
- You Do: "Brazil's climate is… This is because… The biomes found in Brazil are…"
- LR questions: Which biome covers most of Brazil? Why is the rainforest misconception important? How does Brazil's climate differ from England's?
- Resources to flag: biome photograph cards; Brazil biome map (blank + reference); Y3 Mediterranean recap slides; sentence stem sheet

**L3 — Physical geography of England: climate, biomes and topography (Fri 26 June)**
- LO: describe and compare England's physical geography with Brazil's
- Because: comparison is the core geographical skill in this enquiry
- Success: a written comparison using at least two geographical vocabulary words
- I Do: England's climate (temperate maritime), biomes (temperate deciduous forest, moorland), topography (highlands in north/west, lowlands in south/east)
- We Do 1: use OS map / topographical map on board — find highlands/lowlands; compare latitude with Brazil
- We Do 2: side-by-side comparison table: Brazil vs England (climate / biome / topography)
- You Do: "England is different from Brazil because…" — 2–3 sentences using evidence
- LR questions: What surprised you most about England's physical geography? Why does latitude affect climate? What is one similarity between England and Brazil?
- Resources to flag: topographical map of England for board display; comparison table on LP; Y3 biome definitions available as reference

## Learning papers (not yet started)

Three LPs needed (one per lesson). Standard WFA LP format. Ask Innes at start of new chat:
- Whether LP is standard 2-sided A4 or single-side
- Whether supported version needed for any of the 3 lessons
- Whether Turkish version needed for standard LP

## Open questions / blockers

- Jigsaw connections slide for L2/L3 — what to show when there are more than 6 total lessons. Current plan: show only phase 1 lessons (L1–L3 for T6W4).
- ph14 LO box: y=5200000 pushed quite far down — confirm in PowerPoint that text has enough room and isn't clipped at bottom.
- Geography skill not yet written. Once L1–L3 are approved, formalise the build pattern into a skill.

## Immediate next step

Build L2 deck (Physical Geography / green master). Start from L1's working directory as the template base: copy `/home/claude/geo_l1_v4/` to `/home/claude/geo_l2/`, update all layouts to green (`master[2]`, `slideLayouts 16–30` range — verify exact numbers from template), swap connections slide to `connections_geo.pptx` slide 1 (green/Physical), update all content slides for L2 content, update teacher checklist and speaker notes. Then present for review before building L3.
