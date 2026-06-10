# Transfer: T6W2 Spelling Shed — full build complete

**Generated:** 2026-06-10
**Originating focus:** Building T6W2 Spelling Shed resources (3 lessons), fixing LP format, reverse-engineering teaching deck enhancements from Innes's edited Tuesday file, and updating the skill.
**Skill in use:** spelling-shed

---

## Status

T6W2 fully built and delivered. All six files (3 teaching decks + 3 LPs) are final. The C3 Wed teaching deck additionally has three post-build enhancements applied (animated slide 10, section slide, MM answers slide). Skill files updated and pushed to GitHub. Transfer generated at end of session.

---

## What's been produced

- `spelling_shed_slides_CN_Mon.pptx` — Mon -cian lesson, 22 slides, key spelling: *necessary*, final
- `spelling_lp_CN_Mon.pptx` — Mon LP (Find the Root + Match Meaning + Spell Check), final
- `spelling_shed_slides_C2_Tue.pptx` — Tue sorting lesson, 22 slides, key spelling: *height*, final
- `spelling_lp_C2_Tue.pptx` — Tue LP (Spell Check + Match Meaning), final
- `spelling_shed_slides_C3_Wed.pptx` — Wed mixed contrast, **24 slides** (3 post-build additions), key spelling: *strength*, final
- `spelling_lp_C3_Wed.pptx` — Wed LP (Find the Root + Match Meaning + Spell Check), final

All in `/mnt/user-data/outputs/` and backed up on GitHub `imcl75/claude_files/Spelling/`.

---

## Decisions locked in

**T6W2 words:**
- Mon (CN): musician, politician, technician, mathematician, electrician, optician, magician, physician, beautician, paediatrician
- Tue (C2): nation, passion, division, musician, fiction, revision, permission, optician, action, tension
- Wed (C3): station, mansion, expression, technician, fraction, extension, permission, electrician, tension, decision

**LP format (fully resolved this session):**
- 2 slides per LP, portrait A4, two half-A4 halves per slide, cut at 14.85cm
- Side A = Cloze: word labels use `words` list (original order); sentences use `clozeOrder` (shuffled) — **these must never be the same array**
- Side B `"vn_dm_sc"` (Mon/Wed): Find-the-Root left col (6 rows, 0.88cm) + Match-the-Meaning right col (5 rows, 1.056cm) + Spell-Check full-width below (5 rows, 1.292cm)
- Side B `"sc_dm"` (Tue): Spell-Check full-width top + Match-the-Meaning full-width below
- Vertical anchor: `anchor='ctr'` on all row content except definition text (uses `anchor='t'` to prevent wrap overflow)
- Fonts: sentences 11pt, word labels 10.5pt (8.5pt if len>10), spell check options 10.5pt

**Teaching deck post-build additions (applied to C3, should be applied to all future Wed decks and retrofitted where needed):**
1. **Slide 10 animation** — 2-click reveal using EXACT timing XML copied from a working reference file + two-step ID replacement (temp 1000+ placeholder to avoid cascading collisions). bldLst with `animBg="1"` hides shapes on load. root cTn `restart="never"`.
2. **Independent Learning section slide** — inserted after slide 10. See SKILL.md Appendix for exact pixel positions.
3. **MM answers slide** — zip-level clone of MM question slide, answers overlaid (19pt pink #E91E63 bold, 13pt grey #757575 suffix label).

**Terminology locked in:**
- Slide 4 header: **"Today's Words"** (not "This Week's Words") — fixed in `slides-template.js`
- Section slide word list: "Today's words:  [list]"
- `thisWeeksWords*` JSON field names are kept for backward compatibility; their *values* say "today's words"
- File naming: always include day — `spelling_shed_slides_CN_Mon.pptx`, `spelling_lp_CN_Mon.pptx`

---

## Specific user requirements

> "on the cloze — every word is right next to the sentence it goes in. The words should be in a random order not all matching the sentence"

> "in future — always include the day name in the file name"

> "Today's words as these lesson slides always cover a single day"

---

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/spelling-shed/SKILL.md` | **OUTDATED** — updated version delivered as output this session | Save `SKILL.md` from outputs over it |
| `/mnt/skills/user/spelling-shed/references/slides-template.js` | **OUTDATED** — Today's Words fix applied to working copy only | Push updated version from GitHub |
| `imcl75/claude_files/Spelling/lp_builder.py` | Current — v2 with vertical centering + cloze fix | Fetch at session start |
| `imcl75/claude_files/Spelling/slides-template.js` | Current — Today's Words fix applied | Fetch at session start |
| `imcl75/claude_files/Spelling/SKILL_spelling-shed_updated.md` | Current | Reference only |
| `imcl75/claude_files/Spelling/you_do_image.png` | Asset for section slide | Fetch at session start |
| `/mnt/user-data/uploads/2-Tue-spelling_shed_slides_C2.pptx` | Reference — contains working C2 timing XML for animation | Re-upload if doing slide 10 animation for a new lesson |

**Critical:** At the start of any future spelling session, fetch `lp_builder.py` and `slides-template.js` from GitHub. The copies in `/mnt/skills/user/spelling-shed/references/` are outdated.

---

## Open questions / blockers

- T6W3 spelling resources not yet built (W3 theme: -ous family — see T6 plan Excel)
- The post-build enhancements (animation, section slide, MM answers) have only been applied to C3 Wed. The Mon and Tue T6W2 decks do not have them. Innes has not asked for them to be retrofitted.
- Whether to apply the three post-build additions to Mon/Tue decks in future terms needs confirming with Innes.

---

## Immediate next step

If continuing with T6 spelling: build T6W3 using /spelling-shed. Three lessons: Mon=OU (-ous), Tue=IO (-ious/-eous), Wed=GE (keeping e before -ous). Key spelling words from Excel plan: confirm before building. Start by fetching `lp_builder.py` and `slides-template.js` from GitHub.
