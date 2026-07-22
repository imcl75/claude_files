# History Lesson PPTX — Visual Specification
# Extracted from: historyexample_MASTER.pptx (Mayan Civilisation enquiry)
# Session 17 — 2026-07-22
# STATUS: DRAFT — awaiting confirmation from Innes

---

## CRITICAL: The Colour Variable Rule

Every lesson deck is built in a **Substantive Concept colour**.  
In this master deck the concept is **Civilisation** → colour `#FFC000` (amber/gold).

**Do not hardcode `#FFC000`.**  
Use a variable called `CONCEPT_COLOUR` throughout the builder.  
Set it from the enquiry's `substantive_concept_colour` field before building any slide.

The concept colour drives:
- Every `Frame` background fill on every layout
- The bottom accent bar (`Shape 1`) on every lesson slide
- The border bar on the What/Why/How layout
- The KWL table header cell fill (via `scheme:accent5` + tint — keep as scheme ref, let theme resolve)

The complementary light tint used in the What/Why/How cloud callouts and rounded rectangles
is `#FFF3CC` (very light amber). If `CONCEPT_COLOUR` changes, compute the tint programmatically
or define a second variable `CONCEPT_COLOUR_LIGHT` (at ~10% of the base colour on white).

---

## Canvas

| Property | Value |
|---|---|
| Width | 12,192,000 EMU (13.333 in / 960 pt) |
| Height | 6,858,000 EMU (7.5 in / 540 pt) |
| Aspect | 16:9 widescreen |
| Slide size type | Standard widescreen (13.333" × 7.5") |

---

## Master Background

Master background fill: `#FFF3CC` (very light amber — almost cream)

### Master Title Style (from txStyles)
- Font size: 4400 (44 pt)
- Colour: `scheme:tx1` (dark navy/black from theme)
- Font family: `+mj-lt` (major Latin — resolves to **Aptos Display**)

### Master Body Style (from txStyles)
- Level 1: 2800 (28 pt), colour: `scheme:tx1`, font: `+mn-lt` (minor Latin → **Aptos**)
- Level 2: 2400 (24 pt), same
- Level 3: 2000 (20 pt), same

---

## Theme Colour Palette (from theme1.xml)

| Token | Hex | Description |
|---|---|---|
| `dk1` / `tx1` | `#000000` (sysClr windowText) | Primary text — renders as very dark navy in context |
| `lt1` | `#FFFFFF` (sysClr window) | White |
| `dk2` | `#0E2841` | Dark navy (used widely as explicit body text colour) |
| `lt2` | `#E8E8E8` | Light grey |
| `accent1` | `#156082` | Dark teal blue |
| `accent2` | `#E97132` | Orange |
| `accent3` | `#196B24` | Dark green |
| `accent4` | `#0F9ED5` | Sky blue |
| `accent5` | `#A02B93` | Purple |
| `accent6` | `#4EA72E` | Bright green |

### Explicit colours used in this deck (direct hex, not scheme refs)

| Hex | Usage |
|---|---|
| `#FFC000` | **CONCEPT_COLOUR** — frame fills, bottom bars |
| `#FFF3CC` | Light tint of concept colour — cloud callouts, rounded rects on What/Why/How |
| `#AB8000` | Dark tint of concept colour — bottom border strip on What/Why/How |
| `#0E2841` | Body text (explicit, same as dk2) |
| `#F19551` | Slide type labels (Vocab, Learning Review, Recap Quiz title, Concepts label) |
| `#00B050` | Correct answer tick colour (Recap Quiz) |
| `#FFC7B3` | Peach — timeline row fills (Year 1, Year 5) |
| `#F892BB` | Pink — timeline row fill (Year 3) |
| `#F2CFEE` | Light purple/pink tint (KWL table body cells, alpha 27843) |

---

## Custom Fonts Used

| Font | Usage |
|---|---|
| **Sassoon Infant Rg** | Concept/timeline body text (sz 1400–4000) — main display font |
| **Twinkl Cursive Looped** | UI labels, slide-type headings, vocab/review headers |
| **Aptos Display** | Master major font (titles fallback) |
| **Aptos** | Master minor font (body fallback) |
| **Wingdings** | Answer tick character `ü` (char=ü, Wingdings = checkmark) |

---

## Slide Inventory — All 14 Slides

| Slide | Layout # | Layout Name | Description |
|---|---|---|---|
| 1 | 1 | Our Key Question is | Key question + challenge statement |
| 2 | 6 | DEFAULT | Full-bleed image title page |
| 3 | 7 | Title and Content | Concepts slide (Substantive Concept + timeline) |
| 4 | 8 | I Do | "Our Enquiry" timeline overview |
| 5 | 5 | What, Why, How | What am I learning / Why / How will I know |
| 6 | 10 | You Do Trio | KWL table (Prior Knowledge / I am curious about…) |
| 7 | 11 | You Do | Recap Quiz |
| 8 | 3 | Vocabulary | Vocabulary list (word/definition pairs) |
| 9 | 8 | I Do | Lesson content — teacher-led |
| 10 | 9 | We Do | Lesson content — shared/guided |
| 11 | 10 | You Do Trio | Lesson content — trio task |
| 12 | 11 | You Do | Lesson content — independent |
| 13 | 6 | DEFAULT | Contextualising image / activity |
| 14 | 12 | Learning_Review | Learning review (3-column exit ticket) |

---

## Slide Layouts — Full Shape Inventory

### Layout 1: "Our Key Question is"

All positions are in EMU.

| Shape | Name | Geometry | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|---|
| Frame | Frame 1 | frame | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full slide amber bg |
| Cloud | Cloud 6 | (cloud shape) | 1665866 | 215038 | 8504851 | 2763090 | #FFFFFF | White cloud for key question |
| Text | TextBox 15 | rect | 10344525 | 1771029 | 1686365 | 242374 | none | "21st Century Learning Skills" sz=975 Sassoon Infant Rg |
| PH | Text Placeholder 17 | — | 3909252 | 1570619 | 5940246 | 1235810 | none | ph idx=10 "Our Challenge is:" sz=2800 bold |
| Text | TextBox 32 | rect | 4365817 | 6100827 | 3760390 | 461665 | none | "Being an Historian" sz=2400 bold Twinkl Cursive Looped |
| PH | Text Placeholder 22 | — | 3505199 | 444500 | 6344297 | 1041890 | none | ph idx=12 key question text |

**Slide 1 overrides (actual slide content):**
- ph idx=12: pos=(3386446, 528729) size=(6344297, 1041890) — key question text
- ph idx=10: pos=(4597738, 1570619) size=(5251759, 1235810) — "Our Challenge is" text

---

### Layout 3: "Vocabulary"

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | Frame 9 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full amber bg |
| TextBox | TextBox 6 | 980975 | 254033 | 3911600 | 707886 | none | "Vocabulary" sz=4000 bold, colour=#F19551, font=Twinkl Cursive Looped |

**Vocabulary slide body (from slide 8):**
- Content Placeholder 1 ph idx=4294967295 (special idx)
- pos=(636588, 1125216) size=(11007725, 5229547)
- Font: **Twinkl Cursive Looped** throughout
- Word/Phrase entries: bold, body text: regular
- Animation: click-reveal by paragraph (pairs reveal on each click)
  - Paragraphs 0→1 (word+def 1), 3→4 (word+def 2), 6→7 (word+def 3), 9→10 (word+def 4), 12→13 (word+def 5)
  - Animation type: `presetID=1 presetClass=entr presetSubtype=0` (Appear)
  - `style.visibility` toggled to `visible` on click
  - Pattern: odd paragraphs (0,1,3,4,6,7,9,10,12,13) revealed in pairs — word first, then on next click the blank spacer row reveals, then next click word 2, etc.

---

### Layout 5: "What, Why, How"

Complex layout with three rounded rectangles and cloud callouts.

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | Frame 3 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full amber bg |
| Border | Rectangle 2 | -5286 | 6765925 | 12197286 | 101600 | `#AB8000` | Dark amber strip at very bottom |
| Counter | TextBox 4 | 11864468 | 6685920 | 335348 | 261610 | none | "60" sz=1100 colour=#AB8000 — timer counter |
| Title | Title 27 ph=title | 1185691 | 300288 | 10515600 | 587374 | none | Key question text, inherits master title style |
| Rounded rect | Rounded Rectangle 21 | 209994 | 1052184 | 3473707 | 5527021 | `#FFF3CC` | Left column (What) |
| Rounded rect | Rounded Rectangle 22 | 4410752 | 1052185 | 3473707 | 5527021 | `#FFF3CC` | Centre column (Why) |
| Rounded rect | Rounded Rectangle 23 | 8522617 | 1018745 | 3473707 | 5560461 | `#FFF3CC` | Right column (How) |
| Arrow | Right Arrow 38 | 3833454 | 4523091 | 457959 | 384048 | scheme:tx1 | Between col 1 and 2 |
| Arrow | Right Arrow 40 | 7946662 | 4523091 | 457959 | 384048 | scheme:tx1 | Between col 2 and 3 |
| Cloud | Cloud Callout 14 | 1642514 | 1326933 | 1913677 | 1215720 | `#FFF3CC` | "What am I learning?" sz=1600 Twinkl Cursive Looped |
| Cloud | Cloud Callout 17 | 5579272 | 1132775 | 2190940 | 1409879 | `#FFF3CC` | "Why am I learning this?" sz=1600 Twinkl Cursive Looped |
| Cloud | Cloud Callout 60 | 9768925 | 1166214 | 2190940 | 1409879 | `#FFF3CC` | "How will I know when I'm there?" sz=1600 Twinkl Cursive Looped |
| Rounded rect | Rounded Rectangle 25 | 337503 | 3815694 | 3218688 | 2629173 | `#FFF3CC` | "I am learning…" sz=2000 Twinkl Cursive Looped |
| Rounded rect | Rounded Rectangle 65 | 4547775 | 3820472 | 3218688 | 2629173 | `#FFF3CC` | "This is so…" sz=2000 Twinkl Cursive Looped |
| Rounded rect | Rounded Rectangle 66 | 8650126 | 3815694 | 3218688 | 2629173 | `#FFF3CC` | "I will be successful by…" sz=2000 Twinkl Cursive Looped |
| PH | Text Placeholder 33 ph=body idx=10 | 698500 | 4522788 | 2559050 | 1698625 | none | "What" content text |
| PH | Text Placeholder 33 ph=body idx=13 | 4877594 | 4522787 | 2559050 | 1698625 | none | "Why" content text |
| PH | Text Placeholder 33 ph=body idx=14 | 8979945 | 4485371 | 2559050 | 1698625 | none | "How" content text |

**Slide 5 override positions for title and text placeholders:**
- Title (ph=title): pos=(inherit) — uses layout default (1185691, 300288)
- ph idx=10: pos=(inherit) — uses layout (698500, 4522788)
- ph idx=13: text content directly in bodyPr — colour #0E2841 (dark navy)
- ph idx=14: sz=2000, colour #0E2841

---

### Layout 6: "DEFAULT"

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | Frame 1 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full amber bg — slide holds full-bleed image only |

**Slide 2**: Contains only a single PIC (full-bleed title image, rId2 → image44.png).  
**Slide 13**: Contains speech-bubble activity shapes (see Slide 13 detail below).

---

### Layout 7: "Title and Content"

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | — | (not in extracted data — likely same as others) | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | |

**Slide 3 (Concepts slide) key shapes:**

| Shape | x | y | cx | cy | Fill | Font | Text |
|---|---|---|---|---|---|---|---|
| Frame 6 (full bg) | 0 | 0 | 12192000 | 6858000 | `#FFC000` | — | — |
| TextBox 7 (concept label) | 942338 | 254033 | 3911600 | 707886 | none | Sassoon Infant Rg sz=4000 b=1 col=#F19551 | "Civilisation" |
| TextBox 50 (definition) | 144316 | 961919 | 3205508 | 738664 | none | Sassoon Infant Rg sz=1400 | Definition text |
| PIC (timeline image) | (pos from rels) | — | — | — | — | — | Background timeline graphic |

**Timeline groups (Groups 202–206, 137):**  
Six groups stacked vertically representing history curriculum years 1–6.
Each group row runs from ~y=646450 to y=5778184 (top to bottom = Y6 to Y1).

Timeline row structure (each group):
- A horizontal rounded rectangle for the timeline bar
- Numbered circle (Y1–Y6)
- Year label text box
- Knowledge context text box
- Coloured "flag" marker indicating the current enquiry position

**Timeline row colours (era colour coding):**

| Year | Era(s) | Colour |
|---|---|---|
| Y1 | Within living memory | `#FFC7B3` (peach) |
| Y2 | Victorian era | `scheme:accent6` (#4EA72E green) |
| Y3 | Tudors & Stuarts, European Explorers | `#F892BB` (pink) |
| Y4 | Anglo Saxons & Vikings, Maya Civilisation | `scheme:accent5` (#A02B93 purple) |
| Y5 | Roman Empire, Ancient Egyptian | `#FFC7B3` (peach again) |
| Y6 | Ancient Egyptian, Stone Age | `scheme:accent6` (green again) |

---

### Layout 8: "I Do"

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | Frame 6 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full amber bg |
| Title PH | Title 1 ph=title | 246528 | 365125 | 10071847 | 1325563 | none | Slide title |
| Content PH | Content Placeholder 2 ph=body idx=1 | 246528 | 1825625 | 11685495 | 4351338 | none | Main content |

---

### Layout 9: "We Do"

Identical structure to Layout 8, different Frame name (Frame 3 vs Frame 6). No visual difference in builder terms — same positions.

| Shape | x | y | cx | cy | Fill |
|---|---|---|---|---|---|
| Frame 3 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` |
| Title PH | 246528 | 365125 | 10071847 | 1325563 | none |
| Content PH idx=1 | 246528 | 1825625 | 11685495 | 4351338 | none |

---

### Layout 10: "You Do Trio"

Same structure as layouts 8/9. Frame 3 fill=`CONCEPT_COLOUR`.

**Slide 6 (KWL table) uses this layout.**  
Content is a 2-column table (graphicFrame, not a plain shape):
- Table pos=(253207, 1921381) size=(11685586, 4585843)
- Col 1 width: 5842793, Col 2 width: 5842793
- Header row height: 509013
  - Cell fill: `scheme:accent5` lightened (lumMod=20000 lumOff=80000) — light purple
  - Header text: "Prior Knowledge and Skill" / "I am curious about…"
  - Font: Twinkl Cursive Looped, sz=2800, b=0
  - Alignment: centre
- Body row height: 4067683
  - Cell fill: `#F2CFEE` alpha=27843 — very light purple tint
  - Content: blank (children write in)

**Slide 11 (You Do Trio lesson slide) has content placeholder override:**
- Content Placeholder 6 ph idx=1 pos=(238012, 1612400) size=(11685495, 2644623)

---

### Layout 11: "You Do"

Same structure as layouts 8/9/10. Frame 3 fill=`CONCEPT_COLOUR`.

**Slide 7 (Recap Quiz) uses this layout:**

Bottom accent bar (Shape 1): x=0, y=6729984, cx=12191695, cy=128016, fill=`CONCEPT_COLOUR`  
Text container (Text 3): x=548640, y=960120, cx=10972800, cy=5669280, noFill, not used for quiz content  
Title 5 (ph=title) override: pos=(259977, 152400) size=(10071847, 648000)  
  - Text: e.g. "Recap Quiz"  
  - Font: bold, colour=`#F19551`  
Content Placeholder 6 (ph idx=1) override: pos=(259977, 1280160) size=(11685495, 5084698)  
  - Paragraph structure per question (5 questions):  
    - Question para: marL=514350 indent=-514350, buAutoNum type=arabicPeriod, colour=#0E2841  
    - Answer para (lvl=1): buFont=Wingdings char=ü (checkmark), colour=#00B050  
    - Blank spacer para (lvl=1): buNone, 8pt  
  - Animation: click-reveal per paragraph pair (question visible on click, answer on next click)
  - See Animation section below.

**Slide 12 (You Do lesson slide) has content placeholder override:**
- Content Placeholder 6 ph idx=1 pos=(246528, 1528743) size=(11685495, 4351338)

---

### Layout 12: "Learning_Review"

| Shape | Name | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|---|
| Frame | Frame 1 | 0 | 0 | 12192000 | 6858000 | `CONCEPT_COLOUR` | Full amber bg |
| TextBox | TextBox 47 | 980975 | 254033 | 3911600 | 707886 | none | "Learning Review" sz=4000 bold col=#F19551 Twinkl Cursive Looped |
| Box 1 | TextBox 5 | 331625 | 1054834 | 3599387 | 1328023 | scheme:accent2 (#E97132 orange) | First exit-ticket question box |
| Box 2 | TextBox 6 | 4324958 | 1067463 | 3599387 | 1328023 | scheme:accent5 (#A02B93 purple) | Second exit-ticket question box |
| Box 3 | TextBox 7 | 8290560 | 1941004 | 3596185 | 1328023 | scheme:accent6 (#4EA72E green) | Third exit-ticket question box |
| PH | Text Placeholder 51 ph idx=15 | 4457372 | 1165793 | 3295650 | 1084263 | none | Question text for box 2 |
| PH | Text Placeholder 51 ph idx=16 | 8495972 | 2042093 | 3295650 | 1084263 | none | Question text for box 3 |
| PH | Text Placeholder 51 ph idx=17 | 431472 | 1165793 | 3295650 | 1084263 | none | Question text for box 1 |
| Timer PH | Content Placeholder 5 ph idx=13 | 10948086 | 6299573 | 1111992 | 404362 | none | Timer placeholder |

**Slide 14 overrides:** All placeholders inherit layout positions (no overrides).  
Slide 14 ph mapping: idx=13 (image/timer), idx=15 (Q2), idx=16 (Q3), idx=17 (Q1).

---

## Common Lesson Slide Structure (Slides 6–12)

Every lesson slide (KWL, Quiz, Vocabulary, I Do, We Do, You Do Trio, You Do) shares:

### Bottom Accent Bar (Shape 1)
```
name:    Shape 1
geometry: rect
x:       0
y:       6729984
cx:      12191695
cy:      128016
fill:    CONCEPT_COLOUR
border:  w=12700 solid CONCEPT_COLOUR
```
This is a slim coloured strip at the very bottom of the slide.
Total slide height = 6858000. Bar starts at 6858000 − 128016 = 6729984. ✓

### Text Container (Text 3) — visible on slides 6, 7, 9, 10, 11, 12
```
name:    Text 3
geometry: rect
fill:    noFill
border:  none (empty <a:ln/>)
```
Two variants observed:
- **Wide/tall** (slides 6, 7): x=548640, y=960120, cx=10972800, cy=5669280
- **Standard** (slides 9–12): x=457200, y=1690688, cx=11247120, cy=4892992

The "Wide" variant is used for slides whose content starts higher (Quiz, KWL).  
The "Standard" variant is used for I Do / We Do / You Do slides where title sits above.

Default bullet in "Text 3": • bullet char, sz=1600, marL=342900 indent=-342900, spcAft=600pts

### Title Placeholder (Title 5, ph type=title)
On lesson slides the title comes from the layout:
- Layout default: (246528, 365125) size=(10071847, 1325563)
- Slide 7 explicit override: (259977, 152400) size=(10071847, 648000) — for Recap Quiz

### Content Placeholder (ph idx=1)
Content placeholders vary by slide:
- Slide 7 (Recap Quiz): (259977, 1280160) 11685495×5084698
- Slide 11 (You Do Trio): (238012, 1612400) 11685495×2644623
- Slide 12 (You Do): (246528, 1528743) 11685495×4351338
- Slides 9, 10: inherit layout default (246528, 1825625) 11685495×4351338

---

## Slide 13 Detail — Contextualising Activity (DEFAULT layout)

This is a custom one-off activity slide. Not a reusable template from layouts.

| Shape | x | y | cx | cy | Fill | Notes |
|---|---|---|---|---|---|---|
| Rectangle (image placeholder) | 5098473 | 1874982 | 3112654 | 3214338 | none | "Image" label — holds a photo |
| Rounded rect title bar | 612053 | 224176 | 9655840 | 815920 | none | sz=3600 colour=#002060 bold — debate question |
| Speech bubble 1 | 1575198 | 1264272 | 3762612 | 1341859 | none | "Statement one" sz=2800 |
| Speech bubble 2 | 8344733 | 2681662 | 3543300 | 1480162 | none | "Statement two" sz=2800 |
| Speech bubble 3 | 2230051 | 5251345 | 4433639 | 1229887 | none | "Statement three" sz=2800 |
| Learner A label | 366623 | 2810160 | 1155060 | 369332 | none | "Learner A" |
| Learner B label | 10267893 | 2105456 | 1155060 | 369332 | none | "Learner B" |
| PIC: avatar A | rId2 | — | — | — | — | Child avatar image |
| PIC: avatar B | rId4 | — | — | — | — | Child avatar image |
| PIC: source image | rId6 | — | — | — | — | Activity/topic image |
| GROUP: title banner group | — | — | — | — | — | Contains rounded rect + text |

---

## Animation Specification

### Pattern: Click-Reveal (Appear Effect)
Used on: Vocabulary slide (slide 8), Recap Quiz (slide 7)

Each revealed element uses:
```xml
<p:cTn presetID="1" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect">
  <p:set>
    <p:tgtEl><p:spTgt spid="[shape_id]"><p:txEl><p:pRg st="[N]" end="[N]"/></p:txEl></p:spTgt></p:tgtEl>
    <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
    <p:to><p:strVal val="visible"/></p:to>
  </p:set>
```

**No `grpId` or `bldLst` elements** — this is raw sequential click animation, not a build list.

**All paragraphs are initially hidden** (`style.visibility` = hidden by default for animated paragraphs).

### Recap Quiz animation paragraph sequence (slide 7, spid=7):
- Click 1: paragraph 0 (Question 1 visible)
- Click 2: paragraph 1 (Answer 1 visible)
- Click 3: paragraph 3 (Question 2 visible) — para 2 is blank spacer, skip
- Click 4: paragraph 4 (Answer 2 visible)
- Click 5: paragraph 6 (Question 3 visible)
- Click 6: paragraph 7 (Answer 3 visible)
- Click 7: paragraph 9 (Question 4 visible)
- Click 8: paragraph 10 (Answer 4 visible)
- Click 9: paragraph 12 (Question 5 visible)
- Click 10: paragraph 13 (Answer 5 visible)

Total: 10 click events (5 questions + 5 answers)

### Vocabulary animation paragraph sequence (slide 8, spid=2):
Same pattern — 10 click events (5 word/def pairs, blank spacer paras skipped).

---

## How to Build a Lesson Slide (Python/python-pptx guide)

### Step 1: Set CONCEPT_COLOUR
```python
CONCEPT_COLOUR = enquiry["substantive_concept_colour"]   # e.g. "#FFC000"
CONCEPT_COLOUR_RGB = RGBColor.from_string(CONCEPT_COLOUR.lstrip("#"))
```

### Step 2: Add slide from correct layout
```python
layout_map = {
    "our_key_question": prs.slide_layouts[0],   # slideLayout1
    "default":          prs.slide_layouts[5],   # slideLayout6
    "concepts":         prs.slide_layouts[6],   # slideLayout7
    "i_do":            prs.slide_layouts[7],    # slideLayout8
    "we_do":           prs.slide_layouts[8],    # slideLayout9
    "you_do_trio":     prs.slide_layouts[9],    # slideLayout10
    "you_do":          prs.slide_layouts[10],   # slideLayout11
    "vocabulary":      prs.slide_layouts[2],    # slideLayout3
    "what_why_how":    prs.slide_layouts[4],    # slideLayout5
    "kwl":             prs.slide_layouts[9],    # slideLayout10
    "recap_quiz":      prs.slide_layouts[10],   # slideLayout11
    "learning_review": prs.slide_layouts[11],   # slideLayout12
}
slide = prs.slides.add_slide(layout_map["i_do"])
```

> **Note**: python-pptx indexes layouts 0-based. Layout file `slideLayout1.xml` = index 0.

### Step 3: Add bottom accent bar to every lesson slide
```python
from pptx.util import Emu
from pptx.dml.color import RGBColor

shapes = slide.shapes
bar = shapes.add_shape(
    MSO_SHAPE_TYPE.RECTANGLE,
    Emu(0), Emu(6729984), Emu(12191695), Emu(128016)
)
bar.fill.solid()
bar.fill.fore_color.rgb = CONCEPT_COLOUR_RGB
bar.line.color.rgb = CONCEPT_COLOUR_RGB
bar.line.width = Emu(12700)
bar.name = "Shape 1"
```

### Step 4: Add Text 3 container (for slides 9–12)
```python
txt = shapes.add_textbox(Emu(457200), Emu(1690688), Emu(11247120), Emu(4892992))
txt.name = "Text 3"
tf = txt.text_frame
tf.word_wrap = True
# Default: bullet •, sz=16pt
p = tf.paragraphs[0]
p.text = ""
# Set bullet manually via XML
```

### Step 5: Title via placeholder
```python
for ph in slide.placeholders:
    if ph.placeholder_format.type == PP_PLACEHOLDER.TITLE:
        ph.text = lesson["title"]
        run = ph.text_frame.paragraphs[0].runs[0]
        run.font.size = Pt(28)   # or let layout inherit
```

---

## Colour Parameterisation by Substantive Concept

When building a deck, look up the enquiry's `substantive_concept` and map to a colour.  
The enquiry data should carry a `substantive_concept_colour` field.

Known concept/colour from this master:
- **Civilisation** → `#FFC000` (amber/gold)

Additional concepts and their colours are not defined in this spec — they must be provided
by the data file or confirmed separately. Do not guess colours for other concepts.

---

## Fonts Note

The deck uses **Sassoon Infant Rg** and **Twinkl Cursive Looped** — these are non-standard
commercial fonts. When building with python-pptx:
- Embed the font reference exactly as in the XML: `typeface="Sassoon Infant Rg"` and `typeface="Twinkl Cursive Looped"`
- python-pptx will insert the typeface name into the XML even if the font is not installed on the build machine
- The font will display correctly when opened on a machine (or in PowerPoint) that has those fonts installed
- Do NOT substitute a different font — the visual match depends on exact font name matching

---

## Files from this spec
- Source PPTX: `historyexample_MASTER.pptx`
- Unzipped: `/home/claude/history_pptx/`
- Spec: `claude/visual-spec-history.md` (this file)

---
*Last updated: 2026-07-22 — Session 17*
