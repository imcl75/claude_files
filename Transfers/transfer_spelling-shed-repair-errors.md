# Transfer: Spelling-shed PPTX repair errors — ongoing investigation

**Generated:** 2026-07-05
**Originating focus:** PPTX repair errors from multiple skills; naming convention extension; fix_pptx_ooxml.py maintenance.
**Skill in use:** spelling-shed (primary), maths-complete-planning-and-resources (secondary)

---

## Status

Repair errors from spelling-shed PPTXs are NOT fully resolved. `fix_pptx_ooxml.py` has been updated and the spelling-shed SKILL.md now calls it — but Innes reports errors persisting even with the latest skill version. Root cause of the remaining errors has not yet been identified.

A substantial amount of related work was also completed this session (see below).

---

## What's been produced

- `/mnt/skills/user/spelling-shed/SKILL.md` — updated: now calls fix_pptx_ooxml.py in Step 5, before packaging. Pushed to GitHub (SHA: a1e5af09). Packaged as `spelling-shed.skill` for reinstall.
- `/Users/innes/Downloads/spsh-rep/spelling-shed.skill` — install-ready .skill zip (save skill button)
- `/mnt/skills/user/maths-complete-planning-and-resources/SKILL.md` — packaged as `maths-complete-planning-and-resources.skill` (already presented previous session)
- `Shared/fix_pptx_ooxml.py` on GitHub — updated with Fix #5: non-numeric rIds (e.g. `rIdKQ`)
- `Maths/build_lesson_v3.py` on GitHub — fixed: no longer generates `rIdKQ`, now generates numeric rIds
- `Shared/naming-convention.md` on GitHub — new canonical naming reference for all WFA skills
- T6W6 Teaching PPTXs (4 files) — fixed and returned (rIdKQ root cause)
- `Spelling/SKILL.md` on GitHub — naming updated: `{TxWy} - {N} - {DayName} - SpellingTeaching.pptx` etc.
- `Skills/being-a-reader-SKILL.md` on GitHub — naming updated: `{TxWy} - ReaderTeaching.pptx` etc.
- `Writing/build_lesson.py` on GitHub — updated with `--day` and `--day-num` args, new naming convention

---

## Decisions locked in

- WFA naming convention: `{TxWy} - {N} - {DayName} - {SubjectType}.{ext}` for day-specific files; `{TxWy} - {Subject}{Type}.{ext}` for week-level files (Being a Reader, enquiry)
- `fix_pptx_ooxml.py` is the shared post-processor for all PPTX-producing skills — lives at `Shared/fix_pptx_ooxml.py` on GitHub, cached at `/home/claude/fix_pptx_ooxml.py`
- The fixer must run **after generation, before packaging**, in every skill that produces PPTXs
- GitHub token: read from `/mnt/skills/user/github-sync/SKILL.md` — never ask Innes

---

## The repair error problem — current state

### What fix_pptx_ooxml.py currently fixes (5 fixes)
1. Non-standard media names (e.g. `media1.mp4`)
2. notesSlide back-references (wrong `../slides/slideN.xml` paths)
3. Empty `<a:r>` runs
4. notesMaster theme1→theme2 reference
5. Missing `theme2.xml`
6. *(new this session)* Non-numeric rIds (e.g. `rIdKQ`)

### What's still broken
Innes reports repair dialogs **still appearing** even when using the updated skill (which now calls the fixer). The exact nature of the remaining errors is **unknown** — they haven't been diagnosed yet. Possible causes not yet ruled out:
- The fixer is being fetched/run correctly but there are additional OOXML issues it doesn't cover
- The fixer is not actually running (script path issue, silent failure)
- New issues introduced by recent spelling-shed restructure (zip subfolder output: `Teaching/` and `LPs/` subdirs)
- The glob `spelling_shed_slides_*.pptx` in the fixer call may not match files if naming changed

### Critical suspicion
The spelling-shed SKILL.md fixer step uses:
```bash
python3 /home/claude/fix_pptx_ooxml.py /home/claude/spelling_shed_slides_*.pptx
```
But if the build script now names files differently (e.g. with the new `{TxWy} - {N} - {DayName} - SpellingTeaching.pptx` convention), this glob won't match anything. The fixer would silently do nothing.

---

## Immediate next step

1. Ask Innes to share a broken spelling-shed PPTX from a recent build
2. Run it through `fix_pptx_ooxml.py` manually and check if the fixer actually does anything
3. Also check what filenames the build script is actually producing in `/home/claude/` — confirm whether the glob in the SKILL.md fixer step matches them
4. If the glob is wrong, update the SKILL.md fixer step to use the correct pattern
5. If the fixer runs but errors persist, extract the PPTX and inspect `ppt/_rels/presentation.xml.rels` and `ppt/presentation.xml` for remaining anomalies

## Files in play

| Path | State | Re-upload needed? |
|------|-------|-------------------|
| `/mnt/skills/user/spelling-shed/SKILL.md` | Updated, current | No |
| `Shared/fix_pptx_ooxml.py` on GitHub | Current (Fix #5 added) | No — fetched by skills |
| Any broken spelling PPTX from Innes | Needed for diagnosis | **Yes — upload in new chat** |

## Open questions / blockers

- What specific repair errors is PowerPoint reporting? (XML corruption dialog? Missing parts? Media? Rels?)
- Is the fixer glob matching the actual output filenames from the build script?
- Did the recent zip subfolder restructure change where/when files are on disk when the fixer runs?

