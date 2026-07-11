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
    'being_a_scientist_deck': 'Being_a_Scientist_slide_deck.pptx',  # Being a Scientist + 4 discipline slides + concept cartoon template
    'science_example':        'science-example.pptx',               # I do/We do/You do layouts + Learning Review source
    'kq_lo':                  'KQ_LO.pptx',                         # LO panel source
}

DISCIPLINE_ANCHORS = {
    'Biology':                  'What is Biology?',
    'Physics':                  'What is Physics?',
    'Chemistry':                'What is Chemistry?',
    'Earth and Space Science':  'What is Earth and Space Science?',
}
DISCIPLINE_HINTS = {'Biology': 4, 'Physics': 5, 'Chemistry': 6, 'Earth and Space Science': 7}

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

# CORRECTED 11 Jul 2026: the wheel diagrams (Areas of Study circles + Skills
# pie wheel - the actual "Being a Scientist" visual Innes expects) are on
# slide 3, NOT slide 2. The original anchor 'Being a Scientist' matched
# slide 2 because that literal string happens to appear there too (as a
# small caption near an unrelated icon), but slide 2's real content is a
# completely different KQ+Challenge intro block (see kq_challenge below).
# Slide 3 carries no title of its own - one must be added, plus the
# scientist icon, per SKILL.md's long-standing (and previously unimplemented)
# decision: "'Being a Scientist' has title added at top and scientist icon
# bottom left".
BEING_A_SCIENTIST_ANCHOR = 'Areas of Study'
BEING_A_SCIENTIST_HINT = 3
BEING_A_SCIENTIST_ICON_SOURCE_SLIDE = 2   # Picture 18 on slide 2 is the reusable scientist icon
BEING_A_SCIENTIST_ICON_SHAPE_NAME = 'Picture 18'

# kq_challenge: a KQ-in-a-cloud + "Our Challenge is: ..." block, bundled on
# slide 2 alongside unrelated content (a "21st Century Learning Skills" 2x2
# icon grid, and the same stray editor's note found on the old
# being_a_scientist slide). The template's own placeholder content is a
# Planets/Earth-Science example ("How does our planet compare to other
# planets?" / "Design a new planet") left over from a different unit - always
# replace both text boxes. The nested group's own "Key Question" icon and the
# character avatars are generic and reusable, keep them.
KQ_CHALLENGE_ANCHOR = 'Being a Scientist'   # unique to slide 2 (a caption near the bottom icon)
KQ_CHALLENGE_HINT = 2
KQ_CHALLENGE_KQ_SHAPE_NAME = 'TextBox 16'
KQ_CHALLENGE_TASK_SHAPE_NAME = 'TextBox 17'
KQ_CHALLENGE_STRIP_IDS = [4, 11, 12, 13, 14]   # "21st Century Learning Skills" content: id4 is
    # 'Group 3', a grpSp of 4 individual skill-icon images (Independence/
    # Collaboration/Curiosity and Imagination/Resilience - confirmed by opening
    # image2.png, the 'Collaboration' one) that renders as a 2x2 grid top-right.
    # ids 11-14 (TextBox 10 + 3 pictures) are a second, smaller 21st-century-
    # skills cluster near it. Neither belongs on the KQ+Challenge slide.
KQ_CHALLENGE_STRIP_NAME = 'TextBox 19'      # stray editor's note, same one found on the old being_a_scientist source

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
    # Innes: "no cover, slide 1 is the KQ slide" turned out to mean the
    # kq_challenge slide below (a simple KQ + challenge statement), not the
    # detailed lo panel - confirmed 11 Jul 2026 after being shown the correct
    # slide order directly: being_a_scientist, kq_challenge, discipline, lo,
    # then content.
    'being_a_scientist': {
        'presence': 'required', 'mode': 'clone_being_a_scientist',
        'template': 'being_a_scientist_deck', 'anchor': BEING_A_SCIENTIST_ANCHOR, 'hint': BEING_A_SCIENTIST_HINT,
        'fields': [],
    },
    'kq_challenge': {
        'presence': 'required', 'mode': 'clone_kq_challenge',
        'template': 'being_a_scientist_deck', 'anchor': KQ_CHALLENGE_ANCHOR, 'hint': KQ_CHALLENGE_HINT,
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
