# Transfer: Home Learning PDF redesign + image-upload feature

**Generated:** 2026-05-25
**Originating focus:** Redesigning the WFA home learning PDF and adding Streamlit image-upload override for maths/reading columns.
**Skill in use:** none (direct repo edits to `wallscourtfarm/spelling-homelearning`)

---

## Status

Design fully approved via four mockup iterations. Final mockup (`HL_Mockup_v4.pdf`) is the locked spec. No code has been changed yet. New chat should proceed straight to building — `pdf_builder.py` rewrite + Streamlit UI additions.

## What's been produced

- `/mnt/user-data/outputs/HL_Mockup_v4.pdf` — final approved design mockup (not needed in new chat — just reference)

## Decisions locked in

**PDF design (replaces current `build_hl_pdf()` output):**
- Header: white background, WFA blue bottom border (2pt). Left: WFA logo (small). After logo: `"Maple Learning Zone — T5W5  ·  Child Name"` on one line (year group + week ref in YG colour bold, separator `·` in dgrey, child name in navy bold). Right-aligned: `"Home Learning due:  Thursday"` in navy bold. Header height: 13mm.
- Outer table border: 2pt, year group colour. Vertical column divider: 1.2pt, year group colour.
- Each column: subject title ("Being a Mathematician" etc) + state icon flush to table top with 2mm padding. Title underlined in YG colour. Icon 8mm, right side of column, vertically centred with title. Thin LGREY separator below title row.
- Content area: **133 × 156mm** per column — FIXED, same every week. Subject and icon selectable per column independently.
- Bottom bars (both columns): plain white, YG top border line only (no fill). Left: TTRockstars QR + label + "Scan to practise your times tables online." Right: Spelling Shed QR + label + "Scan to complete your spelling assignments." Bar height 14mm.
- No footer. Due-day reminder lives in the header.
- Year group colour drives all border/accent colours — parameterised, not hardcoded.

**Image upload feature:**
- Either column can be set to "Upload image" mode instead of Claude-generated.
- Same image applied to all children that week.
- Standard and Adapted each have their own upload slot (checkbox: "Use same image for both" defaults ticked).
- When image mode is active: section title still drawn (with configurable text), state icon still drawn, content image fills the 133×156mm area exactly.
- When Claude-generate mode: existing content generation unchanged.
- If both columns are manual: skip Claude API call entirely.

**Subject/icon flexibility:**
- Both left and right column subjects selectable independently from full set: `mathematician`, `reader`, `scientist`, `historian`, `geographer`, `writer`, `athlete`, `musician`, `artist`, `linguist`, `computer_scientist`, `citizen`, `designer`.
- Section title auto-fills as "Being a [Subject]" but is editable.
- Icons live in `icons/` folder of the repo; all subjects extracted from learning-labels tool and saved as PNGs.

**Configurable per-run settings (Streamlit UI):**
- Due day (e.g. "Thursday") — text input, not dropdown
- Week ref (e.g. "T5W5") — already exists
- Left column: subject selector + title text + mode (generate / upload)
- Right column: same
- Year group colour — could hardcode Y4 for now since app is Y4-only

## Specific user requirements

> "the content area for 'maths' (and all others) can be made taller"
> "the bottom area doesn't need the pale blue - plain white is fine. the blue border does the year group branding and everything being mostly white cuts down on colour printing"
> "if the home learning is about e.g. science then I would want to be able to have the scientist logo... home learning one week could be science and reading or maths and history"
> "the content area sizes (133x156) can stay exactly the same every week - regardless of what the actual content is"

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `wallscourtfarm/spelling-homelearning` → `pdf_builder.py` | needs full redesign of `build_hl_pdf()` | No — fetch via GitHub API |
| `wallscourtfarm/spelling-homelearning` → `hl_generator.py` | needs minor changes (skip API if both manual) | No — fetch via GitHub API |
| `wallscourtfarm/spelling-homelearning` → `app.py` | needs new Streamlit UI sections | No — fetch via GitHub API |
| `wallscourtfarm/spelling-homelearning` → `assets/wfa_logo.jpg` | current | No — in repo |
| `wallscourtfarm/spelling-homelearning` → `icons/` | only has retrieval/vocabulary/inference PNGs currently | Need to upload all subject icons |

**Subject icons to add to repo** — all extracted from `https://staff.wallscourt-farm-academy.co.uk/learning-labels/index.html` (`const ICONS` dict). Keys: `Citizen`, `Designer`, `artist`, `athlete`, `computer_scientist`, `geographer`, `historian`, `linguist`, `mathematician`, `musician`, `reader`, `scientist`, `writer`. Re-extract from that URL at start of new chat and push to `icons/` in the repo.

**GitHub PAT:** `[see Streamlit secrets → GITHUB_TOKEN]`

**Brand colours:**
```
YG (Y4 Maple) = #1798d3 = (23/255, 152/255, 211/255)
NAVY          = #1A3C6E = (26/255, 60/255, 110/255)
```

**Layout constants (locked):**
```python
HEADER_H  = 13mm
GAP_HDR   =  2mm
ICON_SZ   =  8mm
TITLE_PAD =  2mm   # from table top to title row
TITLE_H   = 12mm   # ICON_SZ + 2*TITLE_PAD
TITLE_GAP =  1.5mm
BAR_H     = 14mm
PAD       =  3mm   # inner horizontal column padding
CONTENT_W = 132.5mm  (= col_w - 2*PAD, derived)
CONTENT_H = 155.5mm  (= table_h - TITLE_PAD - TITLE_H - TITLE_GAP - BAR_H, derived)
```

## Open questions / blockers

- TT bar is always on left, Spelling Shed always on right regardless of column subject — confirmed as intentional (habit-building, not subject-linked). No blocker.
- Streamlit app must be public (share.streamlit.io → spelling-homelearning → Settings → Sharing → Public) — may need checking after deploy.

## Immediate next step

1. Re-extract all subject icons from `https://staff.wallscourt-farm-academy.co.uk/learning-labels/index.html` (`const ICONS` dict) and push as PNGs to `wallscourtfarm/spelling-homelearning/icons/` via GitHub API.
2. Fetch current `pdf_builder.py`, `hl_generator.py`, `app.py` from repo.
3. Rewrite `build_hl_pdf()` in `pdf_builder.py` using the locked design spec above.
4. Add Streamlit UI to `app.py`: subject selectors (left + right), due-day text input, image upload per column (std + adapted), "Use same for both" checkbox.
5. Update `hl_generator.py` to skip Claude API call when both columns are in manual mode.
6. Push all three files back to repo and redeploy Streamlit.
