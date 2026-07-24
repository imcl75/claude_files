The session that wrote this transfer doc was called "Session 11". This new session must therefore be named "Session 12" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
(Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on:
- Build concept_cartoon slides (UNKNOWN — must ask Innes what it looks like and whether there is a reference file before writing any code, XML, or touching any files)
- Build learning_review slides (UNKNOWN — same rule applies)
- Something else

State at end of Session 11: build_image_teaching_slides.py committed at d46be6a. All 37 image variant slides signed off (36 teaching phase + full_bleed). LIGHT_BAR_CONCEPTS pattern implemented (white text/icon on dark bars; black text/dark icon for place_space_scale gold bar). icon_geo_geographer_white.png in assets. Phase 1: 16 of 18 slide types done — only concept_cartoon and learning_review remain.
