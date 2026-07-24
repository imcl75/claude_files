# Enquiry Builder Transfer Doc

The session that wrote this transfer doc was called "Session 21". This new session must therefore be named "Session 22" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project (project doc: `claude/enquiry-builder-brain.md`).

STEP 2: Clone the repo fresh (token is in the brain doc — do NOT use a token from this transfer doc):
```
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
```

STEP 3: Ask Innes what he wants to work on:

* Review history_demo_invasion.pptx and sign off Phase 10 (the deck was delivered at the end of Session 21 — ELP block positions corrected, SP year-band colours confirmed correct, commit 51884e6)
* Science builder (Phase 9)
* Phase 2 — learning papers
* Something else

State at end of Session 21: ELP block positions corrected — 14-position grid derived from Innes's corrected 8IM.pptx, x-spacing=2492900 EMU, y-spacing=1212473 EMU. POS_CONNECTIONS x updated 833846→1018123. SP year-band colours investigated and confirmed correct (hardcoded RGB fills in hist_concepts.pptx, not a scheme colour issue). Demo deck rebuilt and delivered at commit 51884e6. Awaiting Innes sign-off on history_demo_invasion.pptx to pass Phase 10 gate.
