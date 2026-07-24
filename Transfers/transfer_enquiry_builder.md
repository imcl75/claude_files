The session that wrote this transfer doc was called "Session 9". This new session must therefore be named "Session 10" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
(Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on: The next task is image variant builder scripts. All 9 layout geometries are fully in the brain doc (Image Variant Slide Layout Specs section) and animation rule 14 covers the image slide animation model. No code was written in Session 9 — repo is at commit 826e279. Natural starting point: ask Innes which teaching phase type and which layout variant to build first.
