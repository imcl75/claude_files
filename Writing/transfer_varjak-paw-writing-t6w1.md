# Transfer: Varjak Paw Writing Unit T6W1

**Generated:** 2026-05-22
**Originating focus:** Building all teaching slides, learning papers and supporting resources for the T6W1 Varjak Paw writing unit (L1–L6).
**Skill in use:** writing-lesson-pptx (combine_lessons.py, custom rebuild)

---

## Status

All T6W1 teaching slides (L1–L6, 55 slides) and supporting resources are complete and delivered. The combine_lessons.py build pipeline is fully working in `/home/claude/build/`. All supporting PDFs (working wall, station cards, writing support sheets) are built and delivered. No outstanding blockers.

---

## What's been produced

- `/mnt/user-data/outputs/T6W1_Writer.pptx` — 55-slide combined deck L1–L6, final
- `/mnt/user-data/outputs/T6W1_WedAM_Writer_LP.pptx` — L3 learning paper (show fear paragraph), final
- `/mnt/user-data/outputs/T6W1_FriAM_Writer_LP.pptx` — L6 learning paper (ENP practice + rewrite), final
- `/mnt/user-data/outputs/T6W1_Working_Wall.pdf` — 4-page A4 landscape, one category per page, final
- `/mnt/user-data/outputs/T6W1_ThuAM1_Station_Cards.pdf` — 4 A5 station cards for vocab gathering, final
- `/mnt/user-data/outputs/T6W1_ThuAM2_Writing_Support.pdf` — standard writing support (sentence prompts, fronted adverbials, vocabulary), final
- `/mnt/user-data/outputs/T6W1_ThuAM2_Writing_Support_Guided.pdf` — simplified version for less confident writers (guided sentence starters + writing lines), final
- `/mnt/user-data/outputs/T6W1_ThuAM2_Writing_Support_Guided_Turkish.pdf` — Turkish version of the guided sheet (Liberation Sans, full Turkish character support), final

---

## Decisions locked in

**Timetable (T6W1, w/c 1 June 2026):**
- L1 Mon AM — WOW lesson, explore Varjak's world, draw and label
- L2 Mon PM — Atmosphere in a strange new world (reading like a writer)
- L3 Wed AM — Showing character through thoughts and reactions
- L4 Thu AM1 — Vocabulary gathering at stations
- L5 Thu AM2 — Cold task: opening sixty seconds (short burst write)
- L6 Fri AM — Expanded noun phrases

**File naming convention (from this chat, applies to all future writing/enquiry files):**
- Combined weekly deck: `T6W1_Writer.pptx` (no session label)
- Session-specific LPs: `T6W1_WedAM_Writer_LP.pptx`
- Session-specific resources: `T6W1_ThuAM1_Station_Cards.pdf`
- Sessions: MonAM, MonPM, WedAM, ThuAM1, ThuAM2, FriAM (writing/enquiry this term)

**LP decisions for T6W1:**
- L1: No LP — straight to books (learning label: "To explore the world of Varjak Paw and the character at the heart of the story")
- L2: No LP — straight to books (learning label: "To explore how a writer uses language to build atmosphere in an unfamiliar setting")
- L3: LP produced (WedAM_Writer_LP)
- L4: No LP — vocabulary stations and working wall (learning label: "To gather and organise vocabulary for describing a city setting at night")
- L5: No LP — cold task must stay in books (learning label: "To write the opening of Varjak's first night outside the Contessa's house")
- L6: LP produced (FriAM_Writer_LP)

**Key question:** "How does a writer make a reader feel characters' emotions?"
**Challenge:** "Write a powerful narrative and survival guide inspired by Varjak Paw."
**Purpose:** To Entertain | **Audience:** Other Year 4 learners

**Text passages confirmed:**
- L2 (Mon PM): Chapter 8 — "A violent sound cut through his thoughts" through to "the ball of terror in his stomach turned into a heavy lump of despair." Start from "He ventured down the hill…" for the contrast.
- L3 (Wed AM): Chapter 12 — "Far away, but closing in, something shrieked. Something roared." through to "He stood his ground." Give children context: "Varjak has decided the only way to stop a car is to stand in front of it."

**Model paragraphs approved (Y4 punctuation only, no em dashes/colons/semi-colons):**

L3 model (showing fear, Wednesday):
> The door clicked shut behind him. The cold hit first, sharper than he had ever imagined. Varjak pressed himself against the wall, his heart hammering so fast he could feel it in his paws. A sound came from above, metal on metal, high and sudden. Was that what the Vanishings sounded like? He made himself look. The street stretched further than he had ever seen. He watched a man walk past on the other side, too fast and too tall. Then he watched the gap where the man had been.

L5 model (cold task, Thursday AM2 — Innes's own paragraph):
> As Varjak stood on top of the wall catching his breath, his ears were filled with a million new sounds. Wailing alarms, shouting voices, roaring and screeching filled his ears. The city was alive with bright lights of every colour. They flashed and pulsed. The air was different too. The cool air of the garden had been replaced by the hot, smoky air of this new world. It caught in Varjak's throat. This is it he thought. He found that he was shivering. Was it cold or fear or excitement? Below him, he saw life like he never seen before. Thoughts raced through his mind. Where would he go? What would he find? Would he find a dog? Would he make it back? His heart pounded in his chest and his fur bristled as he prepared to enter the Outside.

**4-sentence plan for supported writers (L3):**
1. A sound hits Varjak before he can see anything. What does his body do straight away? (physical reaction)
2. He creeps closer and sees the creatures. What does he notice about them? (what he notices)
3. His body stops working. Keep it short. (short sentence + physical reaction)
4. A thought goes through his head. (internal thought — try putting it as a question)

**Working wall and station card colours:**
- Sights → #1798d3 (blue)
- Sounds → #c0157b (pink)
- Smells → #2bae62 (green)
- Feelings/reactions → #e57d24 (orange)
- Working wall pages use matching colours to station cards

**Build pipeline (all scripts in `/home/claude/build/`):**
- `combine_lessons.py` — builds combined Writer PPTX from JSON lesson files; takes --source, --kc, --cover, --key-question, --challenge, --purpose, --audience, --term, --week, --out, --json args
- `working_wall.py` — builds working wall PDF and station cards PDF
- `writing_support.py` — builds standard writing support PDF
- `writing_support_guided.py` — builds guided writing support PDF
- `writing_support_guided_turkish.py` — builds Turkish guided support PDF

**Source assets in `/home/claude/`:**
- `T5W1_source.pptx` — extracted from T5W1 writer deck, used as slide template source
- `kc_wheel.png` — image75.png from T5W1 (3688×2076, "Being a Writer" KC wheel)
- `varjak_cover.png` — Varjak Paw cover extracted from Varjak_Paw_Writing_Overview.pptx

**Slide JSON files in `/home/claude/`:**
- `slides_L1.json` through `slides_L6.json` — all finalised

---

## Specific user requirements

> "can all file names from now on contain the name and session (where relevant) instead of the lesson number? e.g. T6W1 l4 station cards would become T6W1 Thu AM1 station cards. As a reminder lessons for writing and enquiry this term will be Monday AM, Monday PM, Wednesday AM, Thursday AM1, Thursday AM2, Friday AM"

> "LPs should be the standard WFA format with the correct writer learning label. If no LP is needed for a lesson - and everything will be straight into books that's fine - let me know so i can make the correct learning labels."

> "when you refer to a resource in the slides, you should be providing me with that resource for use in the lessons"

Writing/enquiry timetable this term: MonAM, MonPM, WedAM, ThuAM1, ThuAM2, FriAM.

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/home/claude/T5W1_source.pptx` | in container — template source | No (rebuilds from base_extract if lost) |
| `/home/claude/kc_wheel.png` | in container | No |
| `/home/claude/varjak_cover.png` | in container | No |
| `/home/claude/slides_L1.json`–`slides_L6.json` | in container, finalised | No |
| `/home/claude/build/combine_lessons.py` | in container, working | No |
| `/mnt/user-data/uploads/Varjak_Paw_Writing_Sequence.docx` | available | No |
| `/mnt/user-data/uploads/Varjak-Paw_OCR.pdf` | available | No |
| `/mnt/skills/user/writing-lesson-pptx/SKILL.md` | SKILL.md only — no scripts in skill folder | No scripts; use combine_lessons.py instead |

---

## Open questions / blockers

- T6W1 is complete. Next session will be T6W2 (w/c 8 June) covering L7–L12 (Have-a-Go phase continues through to end of Have-a-Go).
- The writing sequence DOCX covers all 21 lessons — consult it for L7 onwards content.
- No blockers. Environment restore needed at start of new session (check `/home/claude/build/combine_lessons.py` exists; if not, it resets between sessions and must be rebuilt from the SKILL.md or re-uploaded).

---

## Immediate next step

At session start: run `ls /home/claude/build/combine_lessons.py` to confirm the build environment is intact. If missing, tell Innes the container has reset and ask him to confirm what he needs next (T6W2 build, or other resource). Then ask which week/session to build next and consult Varjak_Paw_Writing_Sequence.docx for the lesson content.
