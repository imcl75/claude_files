"""
geography_registry.py — Component definitions and asset paths for the
geography enquiry lesson builder.

All layout names and structure confirmed by direct XML inspection of
Geographer.pptx on 2026-07-12.
"""

# ── Per-lesson master selection ───────────────────────────────────────────────
# substantive_concept → master index (0-based, order from presentation.xml)

MASTER_INDICES = {
    'place_space_scale':    0,   # Yellow  — slideMaster1
    'human_geography':      1,   # Peach   — slideMaster2
    'cultural_awareness':   2,   # Blue    — slideMaster3
    'physical_geography':   3,   # Green   — slideMaster4 (layouts prefixed 1_)
    'environmental_impact': 4,   # Purple  — slideMaster5 (layouts prefixed 1_)
}

DEFAULT_SUBSTANTIVE_CONCEPT = 'place_space_scale'

# Masters 3 and 4 use '1_' prefix on several layout names in their OOXML.
PREFIXED_MASTER_INDICES = {3, 4}


def layout_name_for_master(base_name, master_idx):
    """Return the layout name for a given master — adds '1_' prefix for M3/M4."""
    if master_idx in PREFIXED_MASTER_INDICES:
        return f'1_{base_name}'
    return base_name


# ── Layout names — confirmed by XML inspection 2026-07-12 ────────────────────
#
# All five masters share the same 13 layout names (M3/M4 have 1_ prefix on
# the 4 teaching layouts).
#
# Layouts that exist:
#   Our Key Question is, Concepts & Skills, Puzzle Pieces,
#   KS2 What, Why, How (M0/M1) / What, Why, How (M2/M3/M4),
#   Vocabulary, I Do / 1_I Do, We Do / 1_We Do,
#   You Do Trio / 1_You Do Trio, You Do / 1_You Do,
#   Learning Review Editable, Revisit, Hook, Building Blocks
#
# Layouts that DO NOT exist (documented to prevent confusion):
#   KQ Cover, Progression, KWL, Quiz, Blank, You Do Ind
#
# For slides with no layout (Progression, KWL, Quiz) the builder uses
# the closest available layout as a base.

# LO layout name varies across masters
LO_LAYOUT_BY_MASTER = {
    0: 'KS2 What, Why, How',
    1: 'KS2 What, Why, How',
    2: 'What, Why, How',
    3: 'What, Why, How',
    4: 'What, Why, How',
}


def lo_layout_name(master_idx):
    return LO_LAYOUT_BY_MASTER.get(master_idx, 'KS2 What, Why, How')


# Teaching content layouts — the 1_ prefix applies to M3/M4
TEACHING_LAYOUTS = {
    'i_do':        'I Do',
    'we_do':       'We Do',
    'you_do_trio': 'You Do Trio',
    'you_do':      'You Do',
}


def teaching_layout(slide_type, master_idx):
    base = TEACHING_LAYOUTS.get(slide_type, 'I Do')
    return layout_name_for_master(base, master_idx)


# ── Puzzle Pieces — confirmed structure ──────────────────────────────────────
#
# The Puzzle Pieces layout (slideLayout4 for M0) has 15 piece groups plus
# one decorative group (Group 16).  Confirmed by coordinate inspection:
#
#   Bottom row (pos 1–5,  y≈4.72 in, left→right):
#     Group 24, Group 14, Group 4, Group 20, Group 35
#   Middle row (pos 6–11, y≈2.68 in, left→right):
#     Group 43, Group 39, Group 47, Group 51, Group 55, Group 71
#   Top row    (pos 12–15, y≈0.62 in, left→right):
#     Group 63, Group 59, Group 67, Group 75
#
# Each piece group contains:
#   1. <p:pic> — the EMF+ coloured jigsaw-piece background
#   2. <p:pic> or nested <p:grpSp> — the skill icon
#   3. <p:sp>  — TextBox for puzzle_piece_text
#
# Group 16 is a decorative background element — always kept visible.

PUZZLE_PIECE_GROUPS = [
    'Group 24',   # pos 1  bottom-left
    'Group 14',   # pos 2
    'Group 4',    # pos 3
    'Group 20',   # pos 4
    'Group 35',   # pos 5  bottom-right
    'Group 43',   # pos 6  middle-left
    'Group 39',   # pos 7
    'Group 47',   # pos 8
    'Group 51',   # pos 9
    'Group 55',   # pos 10
    'Group 71',   # pos 11 middle-right
    'Group 63',   # pos 12 top (starts at col 3)
    'Group 59',   # pos 13
    'Group 67',   # pos 14
    'Group 75',   # pos 15 top-right
]

PUZZLE_DECORATIVE_GROUPS = {'Group 16'}

# skill_focus → rId in the Puzzle Pieces LAYOUT's .rels file
# These rIds resolve to the layout's own media files (image12.emf etc.)
# clone_from_layout() remaps these to new slide rIds — use REG values only
# to look up which layout rId to map from.
SKILL_EMF_LAYOUT_RID = {
    'questioning_predicting':   'rId6',   # image12.emf  — Orange
    'observing_recording':      'rId8',   # image14.emf  — Yellow
    'field_work':               'rId10',  # image16.emf  — Purple
    'map_skills':               'rId12',  # image18.emf  — Green
    'concluding_communicating': 'rId15',  # image21.emf  — Blue
}

SKILL_DISPLAY_NAMES = {
    'questioning_predicting':   'Questioning & Predicting',
    'observing_recording':      'Observing & Recording',
    'field_work':               'Field Work',
    'map_skills':               'Map Skills',
    'concluding_communicating': 'Concluding & Communicating',
}

# ── Placeholder indices — confirmed by XML inspection 2026-07-12 ─────────────
#
# Our Key Question is:
#   PH idx=10  — key question text body
#
# KS2 What, Why, How / What, Why, How (same across all masters):
#   PH idx=0   — title (date line)
#   PH idx=10  — WALT body
#   PH idx=13  — TIB body
#   PH idx=14  — ISB body
#
# Vocabulary:
#   PH idx=10  — content body (word/definition pairs)
#
# I Do, We Do, You Do Trio, You Do:
#   PH idx=0   — title
#   PH idx=1   — content body
#
# Learning Review Editable:
#   PH idx=10  — question 1
#   PH idx=11  — question 2
#   PH idx=12  — question 3
#
# Hook (used for KWL and Quiz — no dedicated layout exists):
#   PH idx=0   — title
#   PH idx=1   — content body

# ── Asset paths ───────────────────────────────────────────────────────────────
ASSETS_ROOT = '/Users/innes/Pictures/PPTX Slide assets/Geographer'


# ── Per-concept progression strips ────────────────────────────────────────────
# 6 strip images per concept, one per year group (Y1–Y6), animated on click.
# Stored in concept-specific subfolders under ASSETS_ROOT.
#
# Folder / filename structure (confirmed from disk 2026-07-13):
#   Place Space Scale/PSS-geo-prog-y{N}.png
#   Human Geography/Hum-geo-prog-y{N}.png
#   Culture/Culture-prog-y{N}.png
#   Physical Geography/Physical-geo-prog-y{N}.png
#   Environment/Env-prog-y{N}.png

PROGRESSION_STRIP_FOLDERS = {
    'place_space_scale':    ('Place Space Scale', 'PSS-geo-prog-y{}.png'),
    'human_geography':      ('Human Geography',   'Hum-geo-prog-y{}.png'),
    'cultural_awareness':   ('Culture',           'Culture-prog-y{}.png'),
    'physical_geography':   ('Physical Geography','Physical-geo-prog-y{}.png'),
    'environmental_impact': ('Environment',       'Env-prog-y{}.png'),
}

def progression_strip_path(substantive_concept, year_group):
    """Return the path for a concept's year-group strip image (year_group = 1–6)."""
    folder, template = PROGRESSION_STRIP_FOLDERS.get(
        substantive_concept,
        ('', f'geo-prog-{substantive_concept}-y{{}}.png')
    )
    filename = template.format(year_group)
    return f'{ASSETS_ROOT}/{folder}/{filename}' if folder else f'{ASSETS_ROOT}/{filename}'


# ── Concept titles (used on the progression slide header) ────────────────────
CONCEPT_TITLES = {
    'place_space_scale':    'Place, space and scale',
    'human_geography':      'Human Geography',
    'cultural_awareness':   'Cultural awareness & diversity',
    'physical_geography':   'Physical Geography',
    'environmental_impact': 'Environmental impact and sustainability',
}

# ── Concept icons and definition text ────────────────────────────────────────
# Each entry is a list of (icon_filename, definition_text) tuples.
# Place, Space & Scale has three separate icons with their own definitions;
# the other concepts each have one icon.
CONCEPT_ICON_DATA = {
    'place_space_scale': [
        (
            'geo-Place-icon.png',
            'Places are areas that have been defined by a given name.',
        ),
        (
            'geo-space-icon.png',
            'Space is about the importance of places and the way people '
            'organise where we live.',
        ),
        (
            'geo-scale-icon.png',
            "Scale is when we 'zoom-in and zoom-out' to explore local, "
            'regional and global patterns and connections.',
        ),
    ],
    'human_geography': [
        (
            'geo-human-geog-icon.png',
            'Human geography is the study of how people live, use and change '
            'places. This includes towns, cities, jobs, transport and how '
            'humans affect the environment.',
        ),
    ],
    'cultural_awareness': [
        (
            'geo-culture-icon.png',
            'Culture is the ideas, customs, behaviours and way of life of a '
            'group of people. We can make links between the physical and human '
            'geography of a place and how this affects the culture of the '
            'people living there.',
        ),
    ],
    'physical_geography': [
        (
            'geo-physical-geog-icon.png',
            'Physical geography is the study of the natural features and '
            'processes of the Earth, such as land, water, weather and climate, '
            'and how they change our world.',
        ),
    ],
    'environmental_impact': [
        (
            'geo-sustain-icon.png',
            'Sustainability is about the environment and whether it can '
            'continue to support humans and the lives of other living creatures '
            'in the future. It involves the interaction between physical and '
            'human environments and the effect they have on each other. When '
            'we are Being a Geographer, we think about what is natural and '
            'what is man-made in our environment, and how we can live more '
            'sustainably.',
        ),
    ],
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
TITLE_FONT = 'Twinkl Cursive Looped'
BODY_FONT  = 'Aptos'

# ── Slide type lists ──────────────────────────────────────────────────────────
FIXED_SLIDE_TYPES = [
    'kq_cover',
    'concepts_skills',
    'progression',
    'puzzle_pieces',
    'lo',
    'kwl_or_quiz',
    'vocabulary',
]

VARIABLE_SLIDE_TYPES = [
    'i_do', 'we_do', 'you_do_trio', 'you_do', 'learning_review',
]
