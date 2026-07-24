The session that wrote this transfer doc was called "Session 10". This new session must therefore be named "Session 11" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project ("2) Enquiry Builder").

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
(Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on:
- Sign off the image variant slides (5 PPTXs delivered in Session 10 — one per concept colour, 11 slides each, including full_bleed with concept-coloured bar). Repo is at commit 4c7e61a.
- Any further corrections to build_image_teaching_slides.py
- Move on to another task

State at end of Session 10: build_image_teaching_slides.py is committed at 4c7e61a. All 9 image layout variants + full_bleed are built. Animation ID collision bug fixed (shape id=10 reserved for Title). Full_bleed bar colour uses concept dark colour (not hardcoded gold). 5 PPTXs delivered, awaiting Innes sign-off.
