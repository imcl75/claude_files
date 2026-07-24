# Enquiry Builder Transfer Doc

The session that wrote this transfer doc was called "Session 22". This new session must therefore be named "Session 23" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project (project doc: `claude/enquiry-builder-brain.md`).

STEP 2: Clone the repo fresh (token is in the brain doc — do NOT use a token from this transfer doc):
```
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
```

STEP 3: Ask Innes what he wants to work on:

* Science builder (Phase 9)
* Phase 2 — learning papers
* Something else

State at end of Session 22: Phase 10 (History builder) SIGNED OFF by Innes. SP year-band colour fix applied — commit 8f018c7. Root cause was schemeClr fills in hist_concepts.pptx year-band grpSp elements resolving against blank Presentation() destination theme (accent6=F79646 orange) instead of source theme (accent6=70AD47 green). Fix: _read_source_theme_accents() reads hist_concepts.pptx theme1.xml; _resolve_scheme_colours() converts all schemeClr fills to hardcoded srgbClr before appending to destination. History demo deck rebuilt (14 slides, invasion) and delivered. Innes signed off with "finally!!!!". All 14 history slide types fully locked. Brain doc updated with corrected animation rule 19 and Phase 10 sign-off.
