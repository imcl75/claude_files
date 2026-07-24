The session that wrote this transfer doc was called "Session 11". This new session must therefore be named "Session 12" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project ("2) Enquiry Builder").

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
(Token is in the brain doc.)

STEP 3: Ask Innes about concept_cartoon and learning_review slides — what they look like, what they contain, and whether there are reference files or examples. Do NOT write any code, XML, or touch any files until Innes has answered. These are UNKNOWN slide types (hard stop rule).

State at end of Session 11: build_image_teaching_slides.py committed at d46be6a. All 9 image layout variants + full_bleed fully signed off. LIGHT_BAR_CONCEPTS pattern implemented (white text/icon on dark bars; black text/dark icon for place_space_scale gold bar). icon_geo_geographer_white.png added to assets. Brain doc updated with rule 16 (LIGHT_BAR_CONCEPTS) and all image slides marked ✅ fully locked. Phase 1: 16 of 18 slide types done — only concept_cartoon and learning_review remain.
