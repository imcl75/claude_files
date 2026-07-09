# Transfer: T6W7 States of Matter Science Enquiry — L1 complete, L2–L5 to build

**Generated:** 2026-07-05
**Originating focus:** Building 5-lesson "Being a Scientist" enquiry — "How can scientists observe solids, liquids and gases changing states of matter?" — for T6W7 (wc 13 July, Y4 Maple).
**Skill in use:** None (manual build — no dedicated science enquiry PPTX skill exists yet)

---

## Status

L1 (Monday 13 July) is complete and approved: lesson PPTX v6, LP PPTX, planning DOCX all delivered. The session had significant iteration on the PPTX slides — layout, image placement, and LP format were all corrected. L2–L5 still to build. Adapted LP for L1 was started as a PDF but has been superseded by the PPTX format — a new adapted PPTX LP for L1 has NOT yet been built.

---

## What's been produced

- `/mnt/user-data/outputs/T6W7_States_of_Matter_Enquiry_Plan.docx` — full 5-lesson planning document, final
- `/mnt/user-data/outputs/T6W7_Mon_L1_Scientists_States_of_Matter.pptx` — L1 lesson deck, final (v6)
- `/mnt/user-data/outputs/T6W7_Mon_L1_LP_Standard.pptx` — L1 LP (standard), final
- `/mnt/user-data/outputs/T6W7_Mon_L1_LP_Adapted.pdf` — L1 LP (adapted), SUPERSEDED — do not use; must rebuild as PPTX

---

## Decisions locked in

- **Science PPTX template source:** `/home/claude/science_template.pptx` — the Sound enquiry L2 deck uploaded by Innes. L1 built by cloning this and modifying slides 10–21 in-place using python-pptx text replacement + pptx.add_picture().
- **Slide structure (L1):** Cover → KQ/Challenge → Areas of Study → KO → LO → I Do → We Do → You Do → LP preview → Learning Review. L2–L5 drop KQ/Areas/KO — keep: Cover → Recap Quiz → LO → I Do → We Do → You Do → LP preview → Learning Review.
- **LP format:** PPTX, 7.5" × 10.833" portrait A4. Set 1 (Enquiry/Scientist) LL top-right (2.75" × 1.20"). Scientist icon from media of science template. Twinkl Cursive Looped font for content. Ruled lines (0.8cm spacing), no coloured writing fills. Blue (#1798d3) section headers only.
- **LP builder:** pptxgenjs (`/home/claude/build_l1_lp.js` — reference for L2–L5 LP builds)
- **Higgsfield images:** Background removal via local rembg library — `remove(input_bytes)` → RGBA PNG → embed in PPTX. DO NOT use plain Higgsfield PNG without removing background (white box problem on green slide).
- **KO:** Built via ReportLab → PNG → embedded as full-slide image. v2 script at `/home/claude/ko_v2.pdf` and `/home/claude/ko_v2.png` (landscape A4, L1 content). L2–L5 need their own KO images updated with lesson-relevant content.
- **Concept cartoon slide:** Higgsfield image with background removed via rembg. Position in clear central strip: L=5.90" T=2.79" W=3.10" H=1.73". Speech bubbles must be SHORT (≤ ~50 chars) to fit within the 28pt Sassoon text boxes.
- **Challenge text on KQ slide:** Short phrase only — never mentions a specific lesson number, never asks pupils to do something right now. E.g. "to investigate which materials keep ice frozen for longest".
- **Key lesson parameters already planned** — see planning DOCX. Summary per lesson:

| Lesson | Day | LF | SC1 | SC2 |
|--------|-----|----|-----|-----|
| L1 | Mon 13 July | sort and group materials as solids, liquids or gases | describe properties of each state | sort materials correctly |
| L2 | Tue 14 July | observe materials changing state when heated or cooled | explain what happens to water at 0°C | use a thermometer to record temperature in °C |
| L3 | Wed 15 July | describe evaporation and boiling | describe difference between evaporation and boiling | record temperature data in a table and bar chart |
| L4 | Thu 16 July | observe and explain condensation | explain where water on a cold glass comes from | connect condensation to the water cycle |
| L5 | Fri 17 July | plan and carry out a fair test about changing state | record results in a table and bar chart | write a conclusion that answers the enquiry question |

- **Recap quizzes (L2–L5):** 5 questions per lesson on previous lesson's content. See planning DOCX for full question sets.
- **KWL:** Opened in L1 (K and W columns only). L column completed in L5. Do not add L column to L1 slide deck.
- **Colour:** Y4 = `#1798d3`. This is the ONLY theme colour for LP and all elements. No invented palettes.

---

## Specific user requirements

> "scrsh1 = messy. LP doesnt look like it's my school's LPs - no Learning label, weird colours etc."

> "the LP needs to look like the normal school LPs, start again on that. dont use coloured areas for writing, use lines for writing, get the LL right."

> "Why not keep the higgsfield image on the concept cartoon, get rid of the nonsense white box and make it work."

> "you need to stop just forcing the content into the layout and make the layout work for the content."

**Critical lesson:** Before placing ANY image or text box on a slide, map every existing shape's exact coordinates (use `shape.left.emu/914400`, `shape.top.emu/914400`, `shape.width.emu/914400`, `shape.height.emu/914400`). Blind `add_picture()` calls without this map will cause overlap. This was the root failure on L1 and must not repeat.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| Science template PPTX | Was uploaded as `/mnt/user-data/uploads/1783278093455_T5W3_Sound_L2_Lesson.pptx` | **Yes — re-upload at start of new chat** |
| `/home/claude/science_template.pptx` | Unpacked to `/home/claude/science_unpacked/` last session | Not persisted — re-unpack from re-uploaded template |
| `/home/claude/scientist_icon.png` | Extracted from template media (image18.png, 103×80px, magnifying glass figure) | Rebuild from template media |
| `/home/claude/build_l1_lp.js` | Working pptxgenjs LP builder for L1 — adapt for L2–L5 | Not persisted — re-fetch from planning or recreate |
| `/home/claude/hf_concept_rembg.png` | rembg-processed concept cartoon image for L1 | Not persisted — redo rembg from CDN URL if needed |
| `/home/claude/ko_v2.png` | L1 knowledge organiser PNG (1684×1191) | Not persisted — rebuild from ko_v2 script |
| `/mnt/user-data/outputs/T6W7_States_of_Matter_Enquiry_Plan.docx` | Final — all 5 lesson plans with I Do/We Do/You Do, A/Y/O/D grid | No |
| `/mnt/user-data/outputs/T6W7_Mon_L1_Scientists_States_of_Matter.pptx` | L1 final | No |
| `/mnt/user-data/outputs/T6W7_Mon_L1_LP_Standard.pptx` | L1 standard LP final | No |

---

## Higgsfield CDN URLs (L1 session)

- I Do image (solid/liquid/gas studio photo): `https://d8j0ntlcm91z4.cloudfront.net/user_3DXmej230yNOYKUglSaBcSdN1y2/hf_20260705_200028_d0656a29-6758-49c0-b5e7-1fcd55a62867.png`
- Concept cartoon image (melting/evaporation/condensation): `https://d8j0ntlcm91z4.cloudfront.net/user_3DXmej230yNOYKUglSaBcSdN1y2/hf_20260705_200034_942abc8f-7cba-4f94-a2b7-1fb3e765ebfe.png`

These may expire. If so, regenerate via Higgsfield with same prompts.

---

## L2 Recap Quiz (from planning doc)

Q1: Which state of matter keeps its own shape? A) gas B) liquid C) solid → C
Q2: True or false: a liquid always takes the shape of its container → true
Q3: Which of these is a gas? A) ice B) milk C) air → C
Q4: Sand looks like it flows — is it a solid or a liquid? → solid
Q5: Name one property of a liquid → flows / pours / takes shape of container

---

## Open questions / blockers

- Adapted LP for L1 still needs rebuilding as PPTX (the PDF version is wrong format/style). Can be done at start of next session or when building L2.
- No dedicated science enquiry PPTX skill exists — each lesson is being built by cloning and patching the Sound template. Consider whether a skill should be written after L2 is approved.
- Subject wheel on the template slide (originally Physics for Sound) was not changed for L1 — states of matter is Chemistry. This should be addressed in L2 if that slide is being kept.

---

## Immediate next step

Start L2 (Tuesday 14 July — melting and freezing). Build in this order:
1. Re-upload the Sound enquiry L2 PPTX so the template is available.
2. Clone and modify slides for L2: Cover (say "Tuesday"), Recap Quiz (L1 content, 5 questions listed above), LO (L2 LF/SC1/SC2), I Do (thermometer reading + Higgsfield image of ice/thermometer), We Do (observing ice cubes melting), You Do (complete LP).
3. Generate Higgsfield images needed: close-up thermometer reading, ice cube melting on a tray.
4. Build L2 LP PPTX adapting the L1 LP builder — different KQ (same), LF (observe changing state), content: cycle diagram labelling + true/false statements + one sentence.
5. Deliver both as a pair.

Map every existing shape's coordinates before placing any new content on a slide.
