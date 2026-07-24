# Enquiry Builder Transfer Doc

The session that wrote this transfer doc was called "Session 16". This new session must therefore be named "Session 17" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project (project doc: `claude/enquiry-builder-brain.md`).

STEP 2: Clone the repo fresh (token is in the brain doc — do NOT use a token from this transfer doc):
```
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
```

STEP 3: Ask Innes what he wants to work on:

* History deck builder — equivalent of build_lesson7_deck.py for History subject
* Science deck builder — equivalent for Science subject
* Phase 2 — learning papers (three-level differentiated PDFs)
* Something else

State at end of Session 16: Image generation testing COMPLETE and SIGNED OFF. Higgsfield (mcp__higgsfield__generate_image, model nano_banana_pro) confirmed working for all three layout aspect ratios: 16:9 (full_bleed hook slide), 4:3 (hero_left), 1:1 ×5 (horiz_small_squares). dall-e is billing-capped and unavailable — Higgsfield only. Photorealism rule confirmed and documented: scene/photo images must use "photorealistic" in the prompt; no illustration or cartoon language. Diagrams use explicit structural description. Full workflow confirmed: generate → poll job_display → curl rawUrl to container → pass path to build_image_teaching_slide(). Image generation rules added to brain doc (Image Generation section). Phase 1 remains COMPLETE — all 18 slide types signed off, latest code commit 4ac69a2. No new code committed this session. Brain doc updated with image generation rules and proven-working log entry.
