The session that wrote this transfer doc was called "Session 16". This new session must therefore be named "Session 17" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project "2) Enquiry Builder".

STEP 2: Clone the repo using the clone command from the brain doc. (Token is in the brain doc — do not paste it here.)

STEP 3: Ask Innes what he wants to work on:

* Phase 11 — image variant builders for Science and History (36 combinations per subject: all 9 image layouts × 4 teaching phases). Geography's `build_image_teaching_slides.py` is the reference — science and history versions should be near-identical, substituting subject icon, colour map, and icon positions. No new geometry decisions needed.
* Something else.

State at end of Session 28: Phase 9 (Science) signed off by Innes. All 14 science slide types confirmed. SP pixel-perfect: flask=vector group XML (flask_group.xml, 57K), oval fill=schemeClr bg1 lumMod 95000, per-concept overrides locked, description font=Twinkl Cursive Looped 16pt. Latest commit: 2b55366. Brain doc updated. Phase 11 (image variants for Science & History) is the natural next step.
