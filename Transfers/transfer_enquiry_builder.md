# Enquiry Builder Transfer Doc

The session that wrote this transfer doc was called "Session 23". This new session must therefore be named "Session 24" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project (project doc: `claude/enquiry-builder-brain.md`).

STEP 2: Clone the repo fresh (token is in the brain doc — do NOT use a token from this transfer doc):
```
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
```

STEP 3: Ask Innes what he wants to work on:

* Fix the 4 science slide issues:
  1. subject_progression white background — call set_background(slide, "D9F3D0") after copy_slide_from_pptx() in build_science_subject_progression.py
  2. subject_progression no animations — inspect sci_concepts.pptx XML structure first, then write add_sci_sp_animations()
  3. Jar icons should be school logo + year number, not scientist icon — school logo asset not in repo, need to stage from Mac (/Users/innes/Desktop/Claude Assets/ or /Users/innes/Pictures/PPTX Slide assets/)
  4. WAL PNG quality (SCI_*.png) — orange glow on panel borders and transparent blonde hair — write generate_sci_wal_pngs.py with tighter recolouring tolerance
* Something else

State at end of Session 23: All 14 science slide scripts built and committed (564a110). Chemistry demo deck delivered. Innes identified 4 issues listed above. Phase 9 AWAITING SIGN-OFF.
