# Enquiry Builder Transfer Doc

The session that wrote this transfer doc was called "Session 15". This new session must therefore be named "Session 16" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project (project doc: `claude/enquiry-builder-brain.md`).

STEP 2: Clone the repo fresh (token is in the brain doc — do NOT use a token from this transfer doc):
```
git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder
```

STEP 3: Ask Innes what he wants to work on:

* Image generation — test the /image-generation skill with the lesson 7 demo deck (pick one image layout variant, generate an image at the correct aspect ratio for that layout's slot, place it in the PPTX, confirm it looks right)
* History deck builder — equivalent of build_lesson7_deck.py for History subject
* Science deck builder — equivalent for Science subject
* Something else

State at end of Session 15: Session 15 was a startup-only session — mandatory steps completed (context monitor, repo clone, brain doc read), then the context monitor fired immediately before any substantive work began. Nothing was built or changed. All Phase 1 geography slide types remain fully signed off (latest commit 785b5bf). Brain doc is current as of Session 14. Next action is whatever Innes chooses from the options above.
