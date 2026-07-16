"""
history_registry.py - Component definitions and asset paths for the history enquiry lesson builder.
Parallel to science_registry.py.

Asset paths are absolute paths on Innes's Mac.
"""

# ── Concept colour scheme ─────────────────────────────────────────────────────
CONCEPT_COLOURS = {
    'civilisation': {'bg': 'FFF2CC', 'border': 'FFC000'},
    'invasion':     {'bg': 'FFEBEB', 'border': 'C05102'},
    'empire':       {'bg': 'EFEFFF', 'border': '7438A5'},
    'monarchy':     {'bg': 'E2F0D9', 'border': '00AE4B'},
    'revolution':   {'bg': 'DAE3F3', 'border': '4573C4'},
}

# ── Asset paths ───────────────────────────────────────────────────────────────
ASSETS_ROOT = '/Users/innes/Pictures/PPTX Slide assets/Historians'

STATIC_ASSETS = {
    'hist_icon':    f'{ASSETS_ROOT}/hist-icon.png',
    'sub_concepts': f'{ASSETS_ROOT}/hist-sub-concepts.png',
    'skill':        f'{ASSETS_ROOT}/Hist-skill.png',
    'skills_21c':   f'{ASSETS_ROOT}/21C-skills-KQ-slide.png',
    'children_kq':  f'{ASSETS_ROOT}/4-children-KQ-slide.png',
}

# Concept card images: concept → (folder_name, image_prefix)
# Images: ASSETS_ROOT/folder/prefix-Y1.png … prefix-Y6.png
CONCEPT_CARD_SPECS = {
    'civilisation': ('Civilisation', 'civ'),
    'invasion':     ('Invasion',     'inv'),
    'empire':       ('Empire',       'emp'),
    'monarchy':     ('Monarchy',     'mon'),
    'revolution':   ('Revolution',   'rev'),
}

# Building block brick images keyed by skill_focus value in lesson JSON
BUILDING_BLOCK_PNGS = {
    'questioning':     f'{ASSETS_ROOT}/Hist-block-yellow-questioning-and-understanding.png',
    'chronology':      f'{ASSETS_ROOT}/Hist-block-peach-chronology.png',
    'sources':         f'{ASSETS_ROOT}/Hist-block-pink-sources.png',
    'interpretations': f'{ASSETS_ROOT}/Hist-block-blue-interpretations.png',
}

SKILL_DISPLAY_NAMES = {
    'questioning':     'Questioning & Understanding',
    'chronology':      'Chronology',
    'sources':         'Sources & Evidence',
    'interpretations': 'Interpretations',
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
TITLE_FONT = 'Twinkl Cursive Looped'
BODY_FONT  = 'Aptos'

# ── Phase display names ───────────────────────────────────────────────────────
PHASE_NAMES = {1: 'Discover', 2: 'Investigate', 3: 'Communicate'}

# ── Brick wall layout (4/3/4/3, bottom to top) ───────────────────────────────
# Row order: row 0 is the bottom row (first 4 bricks), row 3 is top (last 3)
BRICK_WALL_ROWS = [4, 3, 4, 3]   # number of bricks per row, bottom → top

# ── Slide type definitions ────────────────────────────────────────────────────
# Used for validation before building. 'fixed' types are always auto-generated
# from MTP metadata and are never listed in the lesson's 'slides' array.
# 'variable' types appear in the 'slides' array.

FIXED_SLIDE_TYPES = [
    'key_question',
    'concepts_skills',
    'concept_card',
    'building_blocks',
    'lo',
    'kwl_or_quiz',   # resolves to kwl for L1, recap_quiz for L2+
    'key_vocabulary',
]

VARIABLE_SLIDE_TYPES = ['i_do', 'we_do', 'you_do', 'you_do_trio', 'concept_cartoon']

# Layout names expected in the base PPTX (same as science-example.pptx)
CONTENT_LAYOUTS = {
    'i_do':       'I do',
    'we_do':      'We do',
    'you_do':     'You do Ind',
    'you_do_trio':'You Do Trio',
    'blank':      'Blank',
}

# ── Concept Cartoon ───────────────────────────────────────────────────────────
# Shared with Science — template lives in Being_a_Scientist_slide_deck.pptx.
# Pass the PPTX path via mtp['concept_cartoon_pptx'].
CONCEPT_CARTOON_ANCHOR                  = 'turn on the light'
CONCEPT_CARTOON_HINT                    = 11
CONCEPT_CARTOON_CENTRAL_IMAGE_SHAPE_NAME= 'Picture 7'
CONCEPT_CARTOON_TITLE_SHAPE_NAME        = 'Rectangle: Rounded Corners 2'
CONCEPT_CARTOON_BUBBLE_NAMES = [
    'Speech Bubble: Rectangle with Corners Rounded 19',
    'Speech Bubble: Rectangle with Corners Rounded 21',
    'Speech Bubble: Rectangle with Corners Rounded 20',
]
CONCEPT_CARTOON_ANIMATION_STEPS = [
    ['Picture 8',  'TextBox 23', 'Speech Bubble: Rectangle with Corners Rounded 19'],
    ['Picture 16', 'Speech Bubble: Rectangle with Corners Rounded 21', 'TextBox 24'],
    ['Picture 14', 'Speech Bubble: Rectangle with Corners Rounded 20', 'TextBox 25'],
]
