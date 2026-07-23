# Transfer: Enquiry Builder — Session 6 → 7

**The session that wrote this transfer doc was called "Enquiry Builder 6". This new session must therefore be named "Enquiry Builder 7".**

**Generated:** 2026-07-23

---

## Repo state

**Current commit:** `383f7f7`  
**Branch:** main (pushed to origin)  
**Repo:** https://github.com/imcl75/enquiry-builder  
**Clone command:** See brain doc in the claude_files project for the token — do not store it here.

---

## What Session 6 did

### 1. `build_we_are_learning.py` — all positions locked from Innes's corrected PPTX

Innes uploaded a corrected PPTX and manually fixed the slide. Session 6 extracted the XML and locked all positions. Key changes from the previous version:

- Middle panel x: 4410752 → **4366305**
- Arrows: enlarged to 815635×684000, repositioned to y ~3474000 (was small at y ~4523000)
- Text overlays: moved up (y ~4261351, was ~4654641), taller (cy ~1952636, was ~1618259)
- KQ title: cx → 10128517, text colour → black (no solidFill), fontScale="92500" on normAutofit
- Text overlay rPr: sz removed (auto-size), kept black solidFill

### 2. Click-reveal animations added

New `add_wal_animations(slide)` in `build_we_are_learning.py` (commit acfba2c). Taken verbatim from Innes's corrected PPTX:

- Click 1: TextOverlay0 (spid=300, clickEffect, grpId="0") + Arrow1 (spid=6, withEffect)
- Click 2: TextOverlay1 (spid=301, clickEffect, grpId="0") + Arrow2 (spid=7, withEffect)
- Click 3: TextOverlay2 (spid=302, clickEffect, grpId="0") only

Uses `restart="never"` on tmRoot. bldLst entries for spids 300, 301, 302. Arrow IDs 6 and 7 are fixed by the add_image call order in the script.

### 3. All 5 IWBSB card assets replaced (commit 383f7f7)

Innes corrected the IWBSB images (~434KB → ~457KB each). The `/mnt/user-data/uploads/` mount cached the old versions, so a base64 workaround was needed:
1. Use `plugin_desktop-commander` to run Python on the device → base64-encode files → write `.b64` to the LO folder
2. Stage the `.b64` files (different names bypass the cache)
3. Decode in container → write PNGs to repo
4. Delete `.b64` files from device

This is documented in the brain doc under "DEVICE STAGING CACHE BUG".

### 4. 5-slide test deck sent to Innes

`test_wal_5concepts.pptx` — one we_are_learning slide per concept (PSS, HG, PhG, CAD, EIS) with dummy England/Brazil content and working click animations.

---

## Current slide type status

| Slide type | Status |
|---|---|
| `key_question` | ✅ signed off |
| `subject_concepts_skills` | ✅ signed off |
| `subject_progression` | ✅ signed off |
| `enquiry_lesson_progression` | ✅ signed off |
| `we_are_learning` | Built — **awaiting sign-off from Innes** |
| All others | UNKNOWN |

---

## What Session 7 must do first

1. Clone the repo and read the brain doc.
2. Ask Innes if he has reviewed the 5-slide we_are_learning deck. If he has fixes, apply them. If it is signed off, mark it locked in the brain doc.
3. Once signed off, Phase 1 is fully complete. Ask Innes what comes next — more slide types or Phase 2 (learning papers).

---

## Key files

```
scripts/geography/build_we_are_learning.py   ← commit acfba2c
assets/shared/lo/                             ← 23 PNGs at commit 383f7f7
scripts/geography/build_geography_deck.py     ← we_are_learning already in the build loop
```

## Device asset location

LO card assets on Innes's Mac: `/Users/innes/Pictures/PPTX Slide assets/Geographer/LO/`

If assets need replacing again, use the base64 workaround (documented in brain doc).
