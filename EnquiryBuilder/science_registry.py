#!/usr/bin/env python3
"""
science_registry.py - component registry for the Science strand of the
enquiry-lesson-builder. Subject-specific; the orchestrator (build_science_lesson.py)
and the low-level plumbing (lib_ooxml.py) are subject-agnostic so History and
Geography can get their own registry module later without touching this one
or the OOXML layer.

Every slide TYPE the MTP JSON can request is declared here with:
  - presence:   'required' | 'optional' | 'repeatable'
  - mode:       'clone_verbatim' | 'clone_override' | 'fresh'
  - fields:     the MTP JSON fields this type consumes
This is what lets a lesson plan compose a deck (include/omit/repeat slides)
instead of the builder always producing one fixed template.
"""

TITLE_FONT = 'Twinkl Cursive Looped Light'
WFA_Y4_BLUE = '1798D3'   # school colour spec: Year 4 / Maple Learning Zone

# Filenames as they actually exist in EnquiryBuilder/templates/ right now.
# (Confirmed by direct inspection 11 Jul 2026 - do not trust old commit
# messages or old SKILL.md prose, both have drifted from reality before.)
TEMPLATE_FILES = {
    'being_a_scientist_deck': 'Being_a_Scientist_slide_deck.pptx',  # 4 discipline slides + concept cartoon template only now - see kq_being_scientist below for why kq_challenge/being_a_scientist moved out
    'science_example':        'science-example.pptx',               # I do/We do/You do layouts + Learning Review source
    'kq_lo':                  'KQ_LO.pptx',                         # LO panel source
    'kq_being_scientist':     'KQ_and_BeingAScientist.pptx',        # 2-slide, SmartArt-free source for kq_challenge + being_a_scientist - see note below
}

DISCIPLINE_ANCHORS = {
    'Biology':                  'What is Biology?',
    'Physics':                  'What is Physics?',
    'Chemistry':                'What is Chemistry?',
    'Earth and Space Science':  'What is Earth and Space Science?',
}
DISCIPLINE_HINTS = {'Biology': 4, 'Physics': 5, 'Chemistry': 6, 'Earth and Space Science': 7}

# Round 8 (11 Jul 2026): the discipline slides carry a genuine, working
# animation in the source template (confirmed on the Chemistry slide: 10
# ovals/groups, single click each). An earlier session's Round 2 diagnosis
# found the raw source's clickEffect count (11) didn't match its spTgt
# count (37) and concluded the animation was malformed, so build_discipline
# stripped it entirely on every build. Diffing Innes's ground-truth repaired
# file showed a clean 10-click, 10-target animation on this slide, which he
# must have rebuilt by hand in PowerPoint rather than the raw source being
# fixable by just leaving it alone (the 11:37 mismatch is real - some
# clicks in the raw source group multiple shapes together). Rather than
# reproduce that complexity, this list gives one shape per click, matching
# Innes's own simplified version exactly (order matters - this is click
# order: the two Areas-of-Study ring shapes, the two Skills-wheel shapes,
# then the labelled groups). Confirmed the shape names/ids are identical
# between the raw source and Innes's fixed file (both trace back to this
# skill's own clone() output), so resolving by name is safe.
# Only confirmed for Chemistry so far (the only strand T6W7 needs) - other
# strands fall back to strip_timing() (silence, not guesswork) until each
# is confirmed the same way.
DISCIPLINE_ANIMATION_SHAPE_NAMES = {
    'Chemistry': ['Oval 27', 'Oval 44', 'Oval 26', 'Oval 8',
                  'Group 305', 'Group 5', 'Group 11', 'Group 14', 'Group 17', 'Group 22'],
}

# KQ_LO.pptx slide 1 carries TWO complete, pixel-identical-position LO panels
# stacked on top of each other (confirmed via shape coordinates 11 Jul 2026 -
# ids 6-22 sit at the exact same left/top/w/h as ids 23-41). Group A (ids
# 6-22) is the stale draft: its dynamic content boxes are generic
# "Text Placeholder 33" shapes that never get filled in. Group B (ids 23-41)
# is the live one: it has the real TextBox 38/39/40 content boxes and an
# extra Frame/logo (ids 37,38). Group A must be deleted on every build or the
# delivered slide shows two overlapping LO panels.
LO_STALE_GROUP_IDS = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

# Concept cartoon (Being_a_Scientist_slide_deck.pptx slide 11, anchor-resolved).
# Confirmed by direct image inspection 11 Jul 2026: the 3 small "learner"
# avatar pictures (ids 9, 15, 17, 19 depending on deck) are generic child
# portraits reused across any concept cartoon topic - keep them. Only the
# large central scene image (id resolved by name 'Picture 7' at build time)
# is topic-specific (in the template it's a cat-in-a-doorway illustration for
# the Light unit) and must always be replaced. The 3 speech-bubble text boxes
# must always be overwritten with the current enquiry's learner statements -
# never left as the light/cat template text.
CONCEPT_CARTOON_ANCHOR = 'turn on the light'
CONCEPT_CARTOON_HINT = 11
CONCEPT_CARTOON_CENTRAL_IMAGE_SHAPE_NAME = 'Picture 7'
CONCEPT_CARTOON_TITLE_SHAPE_NAME = 'Rectangle: Rounded Corners 2'
CONCEPT_CARTOON_BUBBLE_NAMES = [
    'Speech Bubble: Rectangle with Corners Rounded 19',  # near Learner A
    'Speech Bubble: Rectangle with Corners Rounded 21',  # near Learner B
    'Speech Bubble: Rectangle with Corners Rounded 20',  # near Learner C
]
# Round 8 (11 Jul 2026): the three learner avatar portraits, click-animated
# one at a time (A, then B, then C) - found missing entirely from this
# skill's build by diffing Innes's ground-truth repaired file, which has a
# <p:timing> block on this slide that this skill never generated. Confirmed
# by position (each picture sits directly above its matching Learner A/B/C
# label) which picture is which learner's avatar.
CONCEPT_CARTOON_AVATAR_NAMES = ['Picture 8', 'Picture 16', 'Picture 14']  # order: Learner A, B, C

# Text that must NEVER survive into a delivered file, from ANY template on
# ANY subject. If the override logic has a bug, this is the last line of
# defence and it's what verify_lesson.py blacklists.
BANNED_TEMPLATE_TEXT = [
    "turn on the light",
    "eyes",  # "...they shine in the dark" / "eyes – they shine"
    "white cat in the dark room",
    "Insert any other states of being icons",
    "Click to edit Master text styles",
    "Text box",  # literal unfilled "Text box" placeholder runs in KQ_LO Group B if ever left unset
]

# SUPERSEDED 11 Jul 2026 (Round 5) - kept only as a historical note, no
# longer read by build_being_a_scientist(). The wheel diagrams on
# Being_a_Scientist_slide_deck.pptx slide 3 (Areas of Study circles + Skills
# pie wheel) are genuine PowerPoint SmartArt (ppt/diagrams/, confirmed the
# only slide in that file with a diagramData relationship). A delivered L1
# built from this slide crashed Innes's real PowerPoint (EXC_BAD_INSTRUCTION
# in SmartArt/OfficeArt frames, per the crash log he sent) - LibreOffice
# rendering did NOT catch this, it silently mis-renders SmartArt instead of
# crashing, so the QA pipeline had a blind spot for this whole defect class.
# Innes had already solved this in a previous session by converting the two
# diagrams to flat images and rebuilding both this slide and kq_challenge as
# a clean 2-slide file - that file (KQ_and_BeingAScientist.pptx, see
# kq_being_scientist below) is now the source for both components. Do not
# revert to Being_a_Scientist_slide_deck.pptx for either of these two
# components - it still contains the crash-causing SmartArt on slide 3, only
# the discipline slides and concept_cartoon slide are safe to keep sourcing
# from it (confirmed 11 Jul 2026: no diagramData relationship on slides
# 4-12).
BEING_A_SCIENTIST_ANCHOR_OLD_UNUSED = 'Areas of Study'
BEING_A_SCIENTIST_HINT_OLD_UNUSED = 3

# kq_challenge + being_a_scientist (Round 5, 11 Jul 2026): both now sourced
# from KQ_and_BeingAScientist.pptx, the SmartArt-free 2-slide file Innes
# prepared and uploaded. Confirmed by direct inspection - zero
# ppt/diagrams/ content in this file at all.
#   Slide 1 = kq_challenge ("KQ_cloud"): Cloud 1 (background), a "21st
#     Century Learning Skills" 2x2 icon group (Group 3 / TextBox 10 +
#     pictures) which Innes's own reference screenshot confirms DOES belong
#     on this slide (Round 3/4's assumption that this content should be
#     stripped was wrong - nothing is stripped from this source now, see
#     KQ_CHALLENGE_STRIP_IDS below), a "Being a Scientist" caption
#     (TextBox 8), and the KQ text itself in TextBox 16 inside a nested
#     group, with TextBox 17 as the (currently empty) challenge box -
#     these two shape names happen to match the constants already used by
#     build_kq_challenge(), so that function needed no code change.
#   Slide 2 = being_a_scientist: now just 4 shapes total - two flat
#     pictures (AreasOfStudy, Skills) replacing the old SmartArt, a
#     ScientistIcon picture, and a TitleBeing text box already reading
#     "Being a Scientist". The title and icon are baked in, so
#     build_being_a_scientist() no longer needs to synthesise a title
#     textbox or extract/copy an icon from another slide - it now just
#     clones this slide directly, the same pattern as build_discipline().
# Anchor note: both slides contain the text "Being a Scientist" (slide 1 via
# TextBox 8, slide 2 via TitleBeing), so being_a_scientist's anchor relies on
# its hint (2) rather than uniqueness - find_slide_by_anchor() checks the
# hinted slide first and only falls back to a full search (with a loud
# warning) if the hint is wrong. kq_challenge instead anchors on "21st
# Century Learning Skills", which is unique to slide 1, so it doesn't depend
# on the hint being correct.
BEING_A_SCIENTIST_ANCHOR = 'Being a Scientist'
BEING_A_SCIENTIST_HINT = 2

KQ_CHALLENGE_ANCHOR = '21st Century Learning Skills'   # unique to slide 1
KQ_CHALLENGE_HINT = 1
KQ_CHALLENGE_KQ_SHAPE_NAME = 'TextBox 16'
KQ_CHALLENGE_TASK_SHAPE_NAME = 'TextBox 17'
KQ_CHALLENGE_STRIP_IDS = []   # nothing to strip from this source - the 21st
    # Century Learning Skills content is meant to stay (see note above)
KQ_CHALLENGE_STRIP_NAME = ''  # no stray editor's note on this source

LEARNING_REVIEW_ANCHOR = 'Learning Review'
LEARNING_REVIEW_HINT = 17

CONTENT_LAYOUTS = {
    'We do':              'We do',
    'We do - Blank':       'We do - Blank',
    'I Do - Blank':        'I Do - Blank',
    'You do Ind - Blank':  'You do Ind - Blank',
    'You do Ind':          'You do Ind',
}

# ── Component registry ──────────────────────────────────────────────────────
# presence: required (must appear exactly the shape the lesson calls for, at
#   least once), optional (may be omitted by the lesson plan), repeatable
#   (may appear 0-N times, in any position the lesson plan specifies).
COMPONENTS = {
    # ORDER — corrected 11 Jul 2026, superseding an earlier same-day "fix"
    # that had this backwards. Confirmed directly against two screenshots
    # Innes sent of his own reference deck: slide 1 is the KQ + Skills-icon
    # slide (kq_challenge below - Innes calls it "KQ_cloud"), slide 2 is the
    # Areas of Study / Skills wheel (being_a_scientist below). Correct order:
    # kq_challenge (KQ_cloud), being_a_scientist, discipline, lo, then
    # content. Do not trust the previous comment here or Architecture
    # History "Round 3" below, which both stated the reverse - see "Round 4"
    # in SKILL.md for the correction record.
    # kq_challenge's `challenge` field is only used when the enquiry has an
    # investigation/written outcome. When it doesn't (as in T6W7), leave
    # `challenge` empty/omitted so no challenge text renders in the cloud.
    'being_a_scientist': {
        'presence': 'required', 'mode': 'clone_being_a_scientist',
        'template': 'kq_being_scientist', 'anchor': BEING_A_SCIENTIST_ANCHOR, 'hint': BEING_A_SCIENTIST_HINT,
        'fields': [],
    },
    'kq_challenge': {
        'presence': 'required', 'mode': 'clone_kq_challenge',
        'template': 'kq_being_scientist', 'anchor': KQ_CHALLENGE_ANCHOR, 'hint': KQ_CHALLENGE_HINT,
        'fields': ['key_question', 'challenge'],
    },
    'discipline': {
        'presence': 'required', 'mode': 'clone_discipline',
        'template': 'being_a_scientist_deck',
        'fields': ['strand'],
    },
    'lo': {
        'presence': 'required', 'mode': 'clone_lo',
        'template': 'kq_lo', 'anchor': 'What am I learning?', 'hint': 1,
        'fields': ['key_question', 'lo', 'tib', 'isb'],
    },
    'wedo_hook': {
        'presence': 'repeatable', 'mode': 'fresh', 'layout': 'We do',
        'fields': ['title', 'bullets'],
    },
    'wedo_grid': {
        'presence': 'repeatable', 'mode': 'fresh_grid', 'layout': 'We do - Blank',
        'fields': ['title', 'items'],  # items: list of {label, image_path}, any length (grid auto-sizes)
    },
    'ido_diagram': {
        'presence': 'repeatable', 'mode': 'fresh', 'layout': 'I Do - Blank',
        'fields': ['title', 'bullets', 'image_path'],
    },
    'youdo_provocation': {
        'presence': 'repeatable', 'mode': 'fresh', 'layout': 'You do Ind - Blank',
        'fields': ['title', 'image_path'],
    },
    'youdo_task': {
        'presence': 'repeatable', 'mode': 'fresh', 'layout': 'You do Ind',
        'fields': ['title', 'bullets'],
    },
    'concept_cartoon': {
        'presence': 'optional', 'mode': 'clone_concept_cartoon',
        'template': 'being_a_scientist_deck', 'anchor': CONCEPT_CARTOON_ANCHOR, 'hint': CONCEPT_CARTOON_HINT,
        'fields': ['title', 'learners', 'image_path'],
    },
    'learning_review': {
        'presence': 'required', 'mode': 'clone_learning_review',
        'template': 'science_example', 'anchor': LEARNING_REVIEW_ANCHOR, 'hint': LEARNING_REVIEW_HINT,
        'fields': ['starters'],
    },
}

REQUIRED_TYPES = {t for t, spec in COMPONENTS.items() if spec['presence'] == 'required'}
