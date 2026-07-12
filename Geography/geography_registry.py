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

# ── Puzzle piece EMF mapping ──────────────────────────────────────────────────
# Each puzzle piece shape in the template references one of these EMF files
# via its r:embed rId.  rId values are from the ORIGINAL Geographer.pptx
# puzzle-pieces slide rels file (confirmed by visual inspection, 2026-07-12).
# After clone(), these rIds are remapped — use the emf/icon filenames to
# re-identify them in the work directory.
#
# 'emf_src' is the path to the EMF file ON INNES'S MAC (from the template).
# The builder uses Geographer.pptx as the source; these paths are only
# needed when embedding fresh copies (e.g. for a non-template build path).
PUZZLE_PIECE_EMF = {
    'questioning_predicting': {
        'src_rId':  'rId6',
        'src_emf':  'image12.emf',
        'src_icon': 'image13.png',
        'colour':   'Orange',
        'emf_src':  f'{ASSETS_ROOT}/puzzle/piece_questioning_predicting.emf',
    },
    'observing_recording': {
        'src_rId':  'rId8',
        'src_emf':  'image14.emf',
        'src_icon': 'image15.png',
        'colour':   'Yellow',
        'emf_src':  f'{ASSETS_ROOT}/puzzle/piece_observing_recording.emf',
    },
    'field_work': {
        'src_rId':  'rId10',
        'src_emf':  'image16.emf',
        'src_icon': 'image17.svg',
        'colour':   'Purple',
        'emf_src':  f'{ASSETS_ROOT}/puzzle/piece_field_work.emf',
    },
    'map_skills': {
        'src_rId':  'rId12',
        'src_emf':  'image18.emf',
        'src_icon': 'image20.png',
        'colour':   'Green',
        'emf_src':  f'{ASSETS_ROOT}/puzzle/piece_map_skills.emf',
    },
    'concluding_communicating': {
        'src_rId':  'rId15',
        'src_emf':  'image21.emf',
        'src_icon': 'image22.png',
        'colour':   'Blue',
        'emf_src':  f'{ASSETS_ROOT}/puzzle/piece_concluding_communicating.emf',
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
# 15 pieces total arranged in three rows: 5 (bottom), 6 (middle), 4 (top).
# This matches the arrangement confirmed from the Geographer.pptx template.
PUZZLE_PIECE_ROWS = [5, 6, 4]   # pieces per row, bottom → top

# Shape names for the 15 puzzle pieces in the template's puzzle-pieces slide,
# ordered from piece 1 (bottom-left) across and up.
# TODO: verify these names by inspecting Geographer.pptx slide XML directly.
# Typical naming convention based on PowerPoint's default auto-naming:
PUZZLE_PIECE_SHAPE_NAMES = [
    # Row 0 (bottom, 5 pieces) — pieces 1-5
    'Piece1', 'Piece2', 'Piece3', 'Piece4', 'Piece5',
    # Row 1 (middle, 6 pieces) — pieces 6-11
    'Piece6', 'Piece7', 'Piece8', 'Piece9', 'Piece10', 'Piece11',
    # Row 2 (top, 4 pieces) — pieces 12-15
    'Piece12', 'Piece13', 'Piece14', 'Piece15',
]

# Anchor text to locate the puzzle-pieces slide in Geographer.pptx.
# This is the text that find_slide_by_anchor() searches for.
# TODO: confirm by opening geography-example.pptx and reading slide text.
PUZZLE_PIECES_SLIDE_ANCHOR = 'puzzle'

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
