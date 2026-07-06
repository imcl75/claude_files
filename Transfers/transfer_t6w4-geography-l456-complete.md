# Transfer: T6W4 Geography Enquiry L456 — session complete

**Generated:** 2026-07-06
**Originating focus:** Building T6W4 geography enquiry L4-L6 (Human Geography, Map Skills, Environmental Impact) for "Are England and Brazil different?" — including lesson decks, LPs, land use cards, vocabulary card, Higgsfield image generation.
**Skill in use:** geography-enquiry (deck builds), learning-paper (LP builds)

---

## Status

All L4-L6 resources delivered. Final zip `T6W4_L456_Geographers_Complete.zip` (31MB) contains:
- 3 lesson decks (L4 pink/Human, L5 yellow/Map Skills, L6 blue/Environmental)
- 6 LPs as PPTX (correct WFA format)
- Vocabulary card PDF

Land use cards PDF exists in outputs but was not included in final zip — Higgsfield images don't persist between sessions and need regenerating.

---

## What's been produced

- `T6W4_L4_Geographers_Human_Geography.pptx` — final, pink master
- `T6W4_L5_Geographers_Map_Skills.pptx` — final, yellow master (contains Higgsfield Brazil aerial slide)
- `T6W4_L6_Geographers_Environmental_Impact.pptx` — final, blue master (contains Amazon + England before/after image slides)
- `T6W4_LP4_Geographers_Human_Geography.pptx` — final, correct WFA PPTX label format
- `T6W4_LP4_Geographers_Human_Geography_adapted.pptx` — final
- `T6W4_LP5_Geographers_Map_Skills.pptx` — final, includes embedded Westhaven schematic map
- `T6W4_LP5_Geographers_Map_Skills_adapted.pptx` — final
- `T6W4_LP6_Geographers_Environmental_Impact.pptx` — final, vocab checklist in right column
- `T6W4_LP6_Geographers_Environmental_Impact_adapted.pptx` — final

Scripts in GitHub `imcl75/claude_files`:
- `Geography/build_geo_lps_pptx.py` — final LP PPTX builder (correct format)
- `Geography/build_l456_lps_v2.py` — earlier PDF version (do NOT use — wrong format)
- `Geography/build_geo_lesson.py`, `build_geo_l2.py`, `build_geo_l3.py` — deck builders

---

## Decisions locked in

**LP format is always PPTX** — never PDF/ReportLab. This session went through multiple wrong iterations (PDF with custom ReportLab layouts, invented "bordered panel" label). The correct approach is always:
1. Unpack an existing LP PPTX as template base (e.g. `T6W4_LP3_Geographers_England_Comparison_Frame_fixed.pptx`)
2. Update shapes id=4 (date), id=5 (learning label text), id=7 (instruction)
3. Remove all body shapes (id≥8) and inject new content shapes

**Correct WFA learning label structure (Set 1 Enquiry):**
- Position: top-right of slide
- Geographer globe icon (id=3, name="Text 0", text='geographer') — do not touch
- Date (id=4, name="Text 1") — update text only
- Label text (id=5, name="Text 2") — update with 5 paragraphs: "Key Question" (bold underline), question (bold underline), LF (plain), I can 1 (plain), I can 2 (plain)
- All text in Aptos font, sz=650, colour 000000
- **No borders, no coloured boxes, white background throughout**
- Label spec is at `/mnt/skills/user/learning-paper/SKILL.md`

**Teaching slide / LP alignment rule (new — locked in memory):**
Any We Do or I Do slide where the LP task is visually driven must show the same visual on the teaching slide. Two methods:
1. Same Higgsfield image embedded in slide (used correctly for L6 before/after)
2. LP section rendered as PNG snip embedded on slide

**What was missed this session and needs fixing next time:**
- L4 We Do 1 slide: land use card images should appear on screen for modelling (currently text-only)
- L5 We Do 1 slide: Westhaven map should appear on slide so Innes can model grid reference reading

**PyMuPDF (fitz) for QA renders** — not pdftoppm, not LibreOffice Draw. Both fail on standard Helvetica in this environment. `pip install pymupdf --break-system-packages` if not present.

**Zip delivery only** — never present individual files alongside a zip.

---

## Enquiry — lesson structure reference

| L | Date | Master | Conn slide | Focus |
|---|------|--------|-----------|-------|
| L1 | Tue 23 Jun | Yellow | slide2 | Locating Brazil |
| L2 | Wed 24 Jun | Green | slide1 | Brazil Physical Geography |
| L3 | Fri 26 Jun | Green | slide1 | England comparison |
| L4 | Mon 6 Jul | Pink +15 | slide3 | Human Geography |
| L5 | Tue 7 Jul | Yellow +0 | slide2 | Map skills |
| L6 | Wed 8 Jul | Blue +30 | slide5 | Environmental impact |

Layout offset from yellow: Pink=+15, Blue=+30, Green=+45

---

## Pending items

1. **Enquiry-LP skill build** — new session, transfer file already at `Transfers/transfer_enquiry-lp-skill.md` in repo. This is the next priority: build comprehensive skill covering geography, history, science LPs with Higgsfield image integration and correct WFA label format.
2. **Land use cards** — regenerate 12 Higgsfield images and rebuild PDF if needed (script at `Geography/build_l456_lps_v2.py` has `build_land_use_cards()` function, though images need regenerating each session).
3. **L4 We Do 1 teaching slide** — add 2-3 land use card images for modelling.
4. **L5 We Do 1 teaching slide** — embed Westhaven map from LP5 for modelling.
5. **OS map extract for L5 We Do 2** — needs Digimap for Schools (cannot generate).

---

## Key session corrections (do not repeat these mistakes)

- Do NOT build LPs as PDF/ReportLab — always PPTX from existing template
- Do NOT invent new learning label designs — use the established WFA format from the skill
- Do NOT present individual files alongside a zip — zip only
- Do NOT use pdftoppm or LibreOffice Draw for PDF rendering QA — use PyMuPDF (fitz)
- Do NOT generate Higgsfield images for some cards and matplotlib illustrations for others — all or nothing

---

## New standing instructions (captured this session)

> "Be consistent but make sure you are not duplicating content from previous weeks."
> "Use the CLF curriculum progression document to help guide you on prior learning and any cross curricular links which can be made."

CLF curriculum progression summary is at `/mnt/project/CLF_Curriculum_Progression_Summary_v3_3.pdf` — read it before designing any new LP content.

---

## Immediate next step

Start the enquiry-lp skill build session. Read `Transfers/transfer_enquiry-lp-skill.md` from the GitHub repo for the detailed brief. Begin by reading `/mnt/skills/user/reportlab-pdf-creation/SKILL.md` and `/mnt/skills/user/learning-paper/SKILL.md`, then confirm with Innes which "other states of being" subjects need LP support before designing the task type taxonomy.
