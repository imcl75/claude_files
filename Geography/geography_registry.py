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
# Group names differ across masters — confirmed by XML inspection 2026-07-13.
# Group 16 (master 0) is a decorative background element — kept visible.
# Masters 1–4 layouts do not have this decorative group.

# Per-master puzzle piece group names, in position order (pos 1 = bottom-left).
# Keyed by master index (0–4).
PUZZLE_PIECE_GROUPS_BY_MASTER = {
    # Ordering confirmed 2026-07-13 from layout animation spid sequence.
    # pos 1 = bottom-left, reveals first on click.
    0: [
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
        'Group 63',   # pos 12 top
        'Group 59',   # pos 13
        'Group 67',   # pos 14
        'Group 75',   # pos 15 top-right
    ],
    1: [
        'Group 16',   # pos 1  bottom-left  (slideMaster2 — human_geography)
        'Group 8',    # pos 2
        'Group 1',    # pos 3
        'Group 12',   # pos 4
        'Group 22',   # pos 5  bottom-right
        'Group 30',   # pos 6  middle-left
        'Group 26',   # pos 7
        'Group 35',   # pos 8
        'Group 39',   # pos 9
        'Group 43',   # pos 10
        'Group 59',   # pos 11 middle-right
        'Group 51',   # pos 12 top
        'Group 47',   # pos 13
        'Group 55',   # pos 14
        'Group 63',   # pos 15 top-right
    ],
    2: [
        'Group 16',   # pos 1  bottom-left  (slideMaster3 — cultural_awareness)
        'Group 7',    # pos 2
        'Group 1',    # pos 3
        'Group 12',   # pos 4
        'Group 22',   # pos 5  bottom-right
        'Group 30',   # pos 6  middle-left
        'Group 26',   # pos 7
        'Group 35',   # pos 8
        'Group 39',   # pos 9
        'Group 43',   # pos 10
        'Group 59',   # pos 11 middle-right
        'Group 51',   # pos 12 top
        'Group 47',   # pos 13
        'Group 55',   # pos 14
        'Group 63',   # pos 15 top-right
    ],
    3: [
        'Group 16',   # pos 1  bottom-left  (slideMaster4 — physical_geography)
        'Group 7',    # pos 2
        'Group 1',    # pos 3
        'Group 12',   # pos 4
        'Group 22',   # pos 5  bottom-right
        'Group 30',   # pos 6  middle-left
        'Group 26',   # pos 7
        'Group 35',   # pos 8
        'Group 39',   # pos 9
        'Group 43',   # pos 10
        'Group 59',   # pos 11 middle-right
        'Group 51',   # pos 12 top
        'Group 47',   # pos 13
        'Group 55',   # pos 14
        'Group 63',   # pos 15 top-right
    ],
    4: [
        'Group 16',   # pos 1  bottom-left  (slideMaster5 — environmental_impact)
        'Group 7',    # pos 2
        'Group 1',    # pos 3
        'Group 12',   # pos 4
        'Group 22',   # pos 5  bottom-right
        'Group 30',   # pos 6  middle-left
        'Group 26',   # pos 7
        'Group 35',   # pos 8
        'Group 39',   # pos 9
        'Group 43',   # pos 10
        'Group 59',   # pos 11 middle-right
        'Group 51',   # pos 12 top
        'Group 47',   # pos 13
        'Group 55',   # pos 14
        'Group 63',   # pos 15 top-right
    ],
}

# Backwards-compatible alias used by build_geography_lesson (master 0 default)
PUZZLE_PIECE_GROUPS = PUZZLE_PIECE_GROUPS_BY_MASTER[0]

PUZZLE_DECORATIVE_GROUPS = {'Group 16'}   # master 0 only

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

# ── Jigsaw piece assets ───────────────────────────────────────────────────────
#
# JIGSAW_PIECE_POSITIONS: (off_x, off_y, cx, cy) in EMU for each of the 15
# piece slots, in reveal order (slot 1 = bottom-left, revealed first).
# Coordinates extracted from jigsaw-animated.pptx (2026-07-14).
# Same positions used for all masters — the jigsaw layout is universal.
#
JIGSAW_PIECE_POSITIONS = [
    # All positions hand-tuned by Innes McLean 2026-07-15 from jig_v6_L15.pptx.
    # (off_x, off_y, cx, cy) in EMU.  Larger pieces, fully interlocking.
    ( -312726, 3569551, 3437304, 3437304),  # slot  1  bottom-left
    ( 1560881, 3554757, 3446656, 3446656),  # slot  2
    ( 3447222, 3556997, 3446654, 3446654),  # slot  3
    ( 5291717, 3544384, 3550011, 3437303),  # slot  4
    ( 7221656, 3538947, 3437303, 3437303),  # slot  5  bottom-right
    ( -322666, 1691479, 3446656, 3446656),  # slot  6  middle-left
    ( 1547846, 1677908, 3446654, 3446654),  # slot  7
    ( 3382693, 1682081, 3550011, 3437303),  # slot  8
    ( 5333906, 1675668, 3437303, 3437303),  # slot  9
    ( 7205896, 1663481, 3446656, 3446656),  # slot 10
    ( 9090881, 1655639, 3437303, 3437303),  # slot 11  middle-right
    ( 3421196,  -208063, 3446656, 3446656), # slot 12  top-left of top row
    ( 5304404,  -212433, 3446654, 3446654), # slot 13
    ( 7142654,  -202176, 3550011, 3437303), # slot 14
    ( 9087125,  -208042, 3437304, 3437304), # slot 15  top-right
]

# skill_focus → PNG filename under ASSETS_ROOT/Jigsaw Pieces/
# New pieces remade by Innes (2026-07-14): identical shape, one colour per skill.
SKILL_JIGSAW_PNG = {
    'questioning_predicting':   'new-Jig-orange-questioning.png',
    'observing_recording':      'new-Jig-yellow-observing.png',
    'field_work':               'new-Jig-purple-field-work.png',
    'map_skills':               'new-Jig-green-map-skills.png',
    'concluding_communicating': 'new-Jig-blue-concluding.png',
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
# Resolution order:
#   1. Sandbox session mount (glob)
#   2. Innes's Mac local path
#   3. GitHub repo cache — downloaded on demand to /tmp/geo_assets/
import glob as _glob, os as _os, sys as _sys

_ASSETS_CANDIDATES = [
    '/sessions/*/mnt/Geographer',
    '/Users/innes/Pictures/PPTX Slide assets/Geographer',
]
_LOCAL_ASSETS_ROOT = next(
    (p for _pat in _ASSETS_CANDIDATES
       for p in _glob.glob(_pat) if _os.path.isdir(p)),
    None,
)

# Cache dir used when local assets not available
_GEO_CACHE = '/tmp/geo_assets'
_GEO_REPO_ASSET_PREFIX = 'Geography/assets'
_GEO_REPO = 'imcl75/claude_files'
_GEO_RAW_BASE = f'https://raw.githubusercontent.com/{_GEO_REPO}/main'

def _geo_token():
    """Read GitHub token from github-sync SKILL.md."""
    import re as _re
    candidates = [
        '/mnt/skills/user/github-sync/SKILL.md',
        '/sessions/exciting-cool-cray/mnt/.claude/skills/github-sync/SKILL.md',
        '/var/folders/7w/tbn3l_nd3pj08rjjyfvc31d80000gn/T/claude-hostloop-plugins/20f3261227b068eb/skills/github-sync/SKILL.md',
    ]
    # Also glob for any session path
    candidates += _glob.glob('/sessions/*/mnt/.claude/skills/github-sync/SKILL.md')
    for path in candidates:
        if _os.path.exists(path):
            with open(path) as _f:
                m = _re.search(r'GITHUB_TOKEN:\s*(\S+)', _f.read())
                if m:
                    return m.group(1)
    return None

def ensure_asset(rel_path):
    """
    Return the local filesystem path to a Geographer asset.

    Checks in order:
      1. ASSETS_ROOT (local Mac or sandbox mount)
      2. /tmp/geo_assets cache
      3. GitHub repo — downloads and caches on first use

    rel_path is relative to ASSETS_ROOT, e.g.
      'geo-physical-geog-icon.png'
      'Jigsaw Pieces/new-Jig-orange-questioning.png'
      'Physical Geography/Physical-geo-prog-y4.png'
    """
    import urllib.request as _ur, urllib.parse as _up

    # 1. Local
    if _LOCAL_ASSETS_ROOT:
        local = _os.path.join(_LOCAL_ASSETS_ROOT, rel_path)
        if _os.path.exists(local):
            return local

    # 2. Cache hit
    cached = _os.path.join(_GEO_CACHE, rel_path)
    if _os.path.exists(cached):
        return cached

    # 3. Fetch from GitHub
    token = _geo_token()
    if not token:
        print(f'  NOTE: no GitHub token — cannot fetch asset {rel_path}', file=_sys.stderr)
        return None

    parts = [_up.quote(p) for p in rel_path.replace('\\', '/').split('/')]
    url = f'{_GEO_RAW_BASE}/{_GEO_REPO_ASSET_PREFIX}/{"/".join(parts)}'
    _os.makedirs(_os.path.dirname(cached), exist_ok=True)
    try:
        req = _ur.Request(url, headers={'Authorization': f'token {token}'})
        with _ur.urlopen(req, timeout=20) as _r:
            with open(cached, 'wb') as _out:
                _out.write(_r.read())
        print(f'  [asset] fetched {rel_path} ({_os.path.getsize(cached):,}b)', file=_sys.stderr)
        return cached
    except Exception as _e:
        print(f'  NOTE: could not fetch asset {rel_path}: {_e}', file=_sys.stderr)
        return None

# ASSETS_ROOT: kept for backwards compat — points to local if available, else cache dir
ASSETS_ROOT = _LOCAL_ASSETS_ROOT or _GEO_CACHE


def install_render_fonts():
    """
    Install Twinkl Cursive Looped as a system font so LibreOffice (and any
    other render tool) uses the real font rather than a fallback.

    Must be called before any slide→image render step.  Safe to call multiple
    times — exits silently if the font is already installed.

    Fonts live in the repo at Geography/fonts/; ensure_asset() fetches them
    if not available locally.
    """
    import subprocess as _sp
    import shutil as _sh

    font_dir = _os.path.expanduser('~/.fonts')
    target = _os.path.join(font_dir, 'TwinklCursiveLooped-Regular.ttf')

    if _os.path.exists(target):
        return  # already installed this session

    font_path = ensure_asset('fonts/TwinklCursiveLooped-Regular.ttf')
    if not font_path:
        print('  NOTE: Twinkl Cursive Looped TTF not available — renders will use fallback font',
              file=_sys.stderr)
        return

    _os.makedirs(font_dir, exist_ok=True)
    _sh.copy2(font_path, target)
    try:
        _sp.run(['fc-cache', '-f', font_dir], check=True,
                capture_output=True, timeout=15)
        print(f'  [font] installed Twinkl Cursive Looped → {target}', file=_sys.stderr)
    except Exception as _e:
        print(f'  NOTE: fc-cache failed: {_e}', file=_sys.stderr)


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
    """Return a local path to the strip image, fetching from GitHub if needed."""
    folder, template = PROGRESSION_STRIP_FOLDERS.get(
        substantive_concept,
        ('', f'geo-prog-{substantive_concept}-y{{}}.png')
    )
    filename = template.format(year_group)
    rel = f'{folder}/{filename}' if folder else filename
    return ensure_asset(rel)


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
