"""
geography_registry.py — Component definitions and asset paths for the
geography enquiry lesson builder.

Parallel to history_registry.py, with two key differences:
  1. Colours and masters change *per lesson* (keyed on substantive_concept),
     not per enquiry (unlike history where one concept covers all lessons).
  2. Puzzle Pieces replace Building Blocks — pieces are EMF+ image files
     embedded in the Geographer.pptx template.  Colour is applied by swapping
     the r:embed rId on the <p:pic> element, not by filling a rectangle.

Asset paths are absolute paths on Innes's Mac.
"""

# ── Per-lesson master selection ───────────────────────────────────────────────
# Each lesson carries a 'substantive_concept' field in the MTP JSON.
# That determines which slide master (and therefore which background colour
# palette) the lesson's slides use.

# Master index → background/border colours used for overlay fills.
# (The master itself controls the default palette; the builder ALSO applies
# explicit fills for shapes it draws, so these colours need to match the master.)
MASTER_INDICES = {
    'place_space_scale':    0,   # Yellow master
    'human_geography':      1,   # Peach/pink master
    'cultural_awareness':   2,   # Blue master
    'physical_geography':   3,   # Green master  (layout names have '1_' prefix in OOXML)
    'environmental_impact': 4,   # Purple master (layout names have '1_' prefix in OOXML)
}

MASTER_COLOURS = {
    'place_space_scale':    {'bg': 'FFF3CC', 'border': 'FFC000'},   # Yellow
    'human_geography':      {'bg': 'FFCCCC', 'border': 'C05102'},   # Peach
    'cultural_awareness':   {'bg': 'DAE3F3', 'border': '4573C4'},   # Blue
    'physical_geography':   {'bg': 'D5E8D4', 'border': '00AE4B'},   # Green
    'environmental_impact': {'bg': 'CCCCFF', 'border': '7438A5'},   # Purple
}

DEFAULT_SUBSTANTIVE_CONCEPT = 'place_space_scale'

# ── Asset paths ───────────────────────────────────────────────────────────────
ASSETS_ROOT = '/Users/innes/Pictures/PPTX Slide assets/Geographers'

STATIC_ASSETS = {
    'geo_icon':     f'{ASSETS_ROOT}/geo-icon.png',
    'sub_concepts': f'{ASSETS_ROOT}/geo-sub-concepts.png',
    'skill':        f'{ASSETS_ROOT}/Geo-skill.png',
    'skills_21c':   f'{ASSETS_ROOT}/21C-skills-KQ-slide.png',
    'children_kq':  f'{ASSETS_ROOT}/4-children-KQ-slide.png',
    'progression':  f'{ASSETS_ROOT}/geo-progression.png',   # Progression slide image
}

# ── Puzzle piece EMF reference ────────────────────────────────────────────────
# Reference data only — the builder does NOT swap EMFs.
# Puzzle pieces are cloned as a group from slide PUZZLE_SOURCE_SLIDE of the
# template; unneeded groups are deleted.  These entries map skill_focus to the
# EMF filename in geographers_template.pptx and are kept for documentation.
#
# Companion icon PNGs in the template (image11–16.png) don't match the names
# used in geography-example.pptx (image13–22.png) — they were renamed when
# the file was packaged.  Confirmed by XML inspection 2026-07-12.
PUZZLE_PIECE_EMF = {
    'questioning_predicting': {
        'emf':    'image42.emf',  # in geographers_template.pptx
        'colour': 'Orange',
    },
    'observing_recording': {
        'emf':    'image55.emf',  # companion icon: image15.png (confirmed)
        'colour': 'Yellow',
    },
    'field_work': {
        'emf':    'image43.emf',
        'colour': 'Purple',
    },
    'map_skills': {
        'emf':    'image56.emf',
        'colour': 'Green',
    },
    'concluding_communicating': {
        'emf':    'image57.emf',
        'colour': 'Blue',
    },
}

SKILL_DISPLAY_NAMES = {
    'questioning_predicting':   'Questioning & Predicting',
    'observing_recording':      'Observing & Recording',
    'field_work':               'Field Work',
    'map_skills':               'Map Skills',
    'concluding_communicating': 'Concluding & Communicating',
}

# ── Puzzle piece layout ───────────────────────────────────────────────────────
# The template (geographers_template.pptx) has exactly 5 puzzle piece groups,
# confirmed by XML inspection 2026-07-12.  Each group (<p:grpSp>) contains one
# EMF (coloured puzzle-piece background), an icon, and a TextBox for the lesson
# focus text.
#
# Build strategy: clone slide PUZZLE_SOURCE_SLIDE (the complete 5-piece slide),
# delete groups for lessons beyond the current one, update TextBox text in each
# kept group with the lesson's focus.  No EMF swapping is needed.

# Slide number (1-based) in the template to clone for the puzzle pieces slide.
# Slide 10 = the complete enquiry summary slide with all 5 pieces.
PUZZLE_SOURCE_SLIDE = 10

# Groups on the puzzle pieces slide that are NOT puzzle pieces.
# These are decorative/photo elements kept on every lesson's slide.
# Group 14 = decorative graphic + speech bubble.
# Group 38 = photo collage (4 JPEG images).
PUZZLE_NON_PIECE_GROUPS = {'Group 14', 'Group 38'}

# Puzzle piece group names in reveal order (piece 1 → piece 5).
# Ordered left-to-right across the bottom row (y≈4 in), then the upper piece.
# Positions confirmed by XML inspection of geographers_template.pptx 2026-07-12:
#   piece 1: Group 31   x≈0 in, y≈4 in  (bottom-left)
#   piece 2: Group 40   x≈2 in, y≈4 in
#   piece 3: Group 32   x≈4 in, y≈4 in
#   piece 4: Group 7    x≈6 in, y≈4 in  (bottom-right)
#   piece 5: Group 39   x≈0 in, y≈2 in  (upper-left)
# For lesson N, the builder shows pieces 1..N and deletes the rest.
PUZZLE_PIECE_GROUP_NAMES = [
    'Group 31',   # piece 1
    'Group 40',   # piece 2
    'Group 32',   # piece 3
    'Group 7',    # piece 4
    'Group 39',   # piece 5
]

# Anchor text to locate the progression slide in Geographer.pptx.
PROGRESSION_SLIDE_ANCHOR = 'progression'

# ── Fonts ─────────────────────────────────────────────────────────────────────
TITLE_FONT = 'Twinkl Cursive Looped'
BODY_FONT  = 'Aptos'

# ── Phase display names ───────────────────────────────────────────────────────
PHASE_NAMES = {1: 'Discover', 2: 'Investigate', 3: 'Communicate'}

# ── Slide type definitions ────────────────────────────────────────────────────
# 'fixed' types are always auto-generated from MTP metadata.
# 'variable' types appear in the lesson's 'slides' array.

FIXED_SLIDE_TYPES = [
    'key_question',
    'concepts_skills',
    'progression',
    'puzzle_pieces',
    'lo',
    'kwl_or_quiz',   # resolves to kwl for L1, recap_quiz for L2+
    'key_vocabulary',
]

VARIABLE_SLIDE_TYPES = ['i_do', 'we_do', 'you_do', 'you_do_trio']

# Layout names expected in Geographer.pptx.
# Masters 3 (physical_geography) and 4 (environmental_impact) use a '1_'
# prefix on their layout names in OOXML (confirmed 2026-07-12).
CONTENT_LAYOUTS = {
    'i_do':       'I do',
    'we_do':      'We do',
    'you_do':     'You do Ind',
    'you_do_trio':'You Do Trio',
    'blank':      'Blank',
}

# Master indices that carry a '1_' prefix on their layout names.
PREFIXED_MASTER_INDICES = {3, 4}

def layout_name_for_master(base_name, master_idx):
    """
    Return the correct layout name for a given master index.
    Masters 3 and 4 use '1_<base_name>' in their OOXML layout names.
    """
    if master_idx in PREFIXED_MASTER_INDICES:
        return f'1_{base_name}'
    return base_name
