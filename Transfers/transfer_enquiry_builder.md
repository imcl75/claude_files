The session that wrote this transfer doc was called "Session 11". This new session must therefore be named "Session 12" — rename it now before doing anything else.

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: `__CONTEXT_MONITOR__`

STEP 1: Read the brain doc from the Claude project.

STEP 2: Clone the repo: git clone https://<TOKEN>@github.com/imcl75/enquiry-builder.git /home/claude/enquiry-builder (Token is in the brain doc.)

STEP 3: Ask Innes what he wants to work on:

* Fix the four issues in the Lesson 7 demo deck — details below
* Something else

Four issues found in Session 13 (continued) screenshot review:

1. Slide 6 (we_are_learning) — grammar: normalise_content() in build_we_are_learning.py auto-capitalises content text. "use fieldwork skills..." becomes "Use fieldwork skills..." which breaks grammatical flow from card headers ("I am learning to... Use fieldwork skills" — capital U is wrong). Fix: find normalise_content() and remove auto-capitalisation so source text stays as written.

2. Slide 7 (lesson_quiz) — content overflow: 5 Q&A pairs with long questions and answers spill below the slide frame. Fix: shorten content in QUIZ_ITEMS in build_lesson7_deck.py — shorter questions, shorter answers, so all 5 pairs fit within the text box.

3. Slide 8 (vocabulary) — content overflow: 5 vocabulary items with long definitions spill below the slide frame. Fix: shorten definitions in VOCAB_ITEMS in build_lesson7_deck.py.

4. Slide 16 (concept_cartoon) — statements massively overflow speech bubbles: Current statements are 11-17 words, far too long for the fixed wedgeRoundRectCallout shapes (sz=2800, roughly 3.5M x 1.3M EMU). Fix: rewrite all 3 CC_STATEMENTS in build_lesson7_deck.py to 8 words maximum. Example rewrites:
   - "When we do fieldwork, we should only record things that match what we expected to find." -> "We should only record expected findings."
   - "Fieldwork is important because it lets us collect evidence we cannot get from a map alone." -> "Fieldwork gives us evidence maps cannot."
   - "Any information we collect during fieldwork is automatically accurate and trustworthy." -> "All fieldwork data is always accurate."

State at end of Session 11: concept_cartoon SIGNED OFF (commit 77b7e30). Phase 1 COMPLETE — all 18 slide types signed off. Complete 17-slide Lesson 7 human_geography deck built (commit 4ac69a2). Four issues found via screenshot review (slides 6, 7, 8, 16). Brain doc updated. Transfer doc written. Next session is Session 12.
