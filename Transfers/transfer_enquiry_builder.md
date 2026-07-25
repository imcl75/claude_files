The session that wrote this transfer doc was called "Session 24". This new session must therefore be named "Session 25" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project ("2) Enquiry Builder").

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder (Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on:

* Sign off on the science demo (science_demo_chemistry.pptx delivered end of Session 24) — if it looks correct, Phase 9 gate is passed
* Report issues with the science slides (WAL green hair tint on SCI_iwbsb.png, or anything else) for further fixes
* Something else

State at end of Session 24: All 4 science Phase 9 issues fixed at commit 6b97917. (1) Subject progression white background fixed — set_background("D9F3D0") called after copy_slide_from_pptx(). (2) Click-reveal animations added — 6 pairs, cx-based grpSp detection (wide>4M EMU, icon<1M EMU). (3) Scientist icon blobs replaced with WFA school logo in icon groups. (4) WAL PNGs rewritten with flood-fill recolouring — orange glow eliminated; SCI_iwbsb.png retains slight green hair tint (inherent to image). Updated demo deck delivered. Phase 9 AWAITING SIGN-OFF from Innes.
