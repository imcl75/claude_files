# Enquiry Builder — Transfer Doc

The session that wrote this transfer doc was called "Session 9". This new session must therefore be named "Session 10" — rename it now before doing anything else.

---

STEP 0 (MANDATORY — before reading anything): Set up the context monitor. Call send_later with delay_minutes=20 and this exact message: __CONTEXT_MONITOR__

STEP 1: Read the brain doc from the Claude project ("2) Enquiry Builder").

STEP 2: Clone the repo using the clone command in the brain doc.
(Token is in the brain doc — do NOT put it in this transfer doc.)

STEP 3: Ask Innes what he wants to work on. The natural next task is building the image variant scripts. Here is what Session 9 established:

WHAT IS READY:
- All 9 image layout variants are fully analysed. Every EMU position, spid, font size and animation model is in the brain doc under "Image Variant Slide Layout Specs".
- Animation rule 14 in the brain doc covers the image slide animation model (consecutive pRg indices, withEffect for simultaneous reveals, special cases for horiz_small_squares and horiz_small_squares_2row).
- Innes confirmed: background and frame required on image slides; Geographer icon on every image slide (inject explicitly — not auto from layout); caption optional; all 4 teaching phase types need all 9 layouts (36 combinations); image sourcing via /image-generation skill; font sizes from the reference.

WHAT HAS NOT BEEN DONE YET:
- No image variant builder scripts exist. No code was written in Session 9.
- MTP JSON schema needs updating to include image fields (paths, captions, aspect ratios) — discuss with Innes before touching the schema.
- The reference PPTX used for analysis was image_layout_samples_v2IM.pptx. It is not in the repo.

SUGGESTED STARTING POINT FOR SESSION 10:
Ask Innes which teaching phase type to start with (i_do image variants is the logical first) and which image layout variant to tackle first. Build, test and get sign-off one variant at a time before moving to the next.

CURRENT REPO COMMIT: 826e279 (no new commits in Session 9 — no code was written).
