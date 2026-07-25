The session that wrote this transfer doc was called "Session 27". This new session must therefore be named "Session 28" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder (Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on:

* Sign off on the science subject_progression PPTX files (4 files delivered at the end of Session 27 — chemistry, earth_and_space, biology, physics). If signed off, mark Phase 9 gate as passed and update brain doc.
* Continue Phase 9 science work (if there are issues with the delivered PPTX files).
* Something else.

State at end of Session 27: Science subject_progression script completely rebuilt from scratch (no sci_concepts.pptx injection). Uses contexts_flasks.png beaker overlay + Y1–Y6.png year-band strips. Both bugs fixed (scientist-icon filename hyphen; XML escaping for ampersands in year text). All 4 concepts (chemistry, earth_and_space, biology, physics) build and save cleanly. Committed ef7ec98. 4 PPTX files delivered to Innes. AWAITING SIGN-OFF.
