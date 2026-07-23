"""
image_layouts.py
Shared image layout definitions for Science, Geography and History enquiry lesson builders.

Coordinates extracted from image_layout_samples_v2-IM.pptx (Innes's hand-corrected reference).
All values in EMU. Slide canvas = 12192000 × 6858000 EMU.

USAGE
-----
    from image_layouts import LAYOUTS, pick_layout

    coords = LAYOUTS['B1_hero_image_left']
    img    = coords['image']   # {'x': ..., 'y': ..., 'cx': ..., 'cy': ...}

LAYOUT DECISION GUIDE
---------------------
    Image IS the main content   → D_diagram_focus  or  A_full_bleed
    Image EQUAL to text         → B1 / B2 / B3  (split-screen variants)
    Image SUPPORTS the text     → C_supporting_illustration
    Multiple images to sort     → gallery_5row / gallery_6x2 / gallery_1wide
    Provocation / discussion    → concept_cartoon

SUBJECT NOTES
-------------
    Science   — use layout with fresh(work, 'I Do - Blank') etc.
    History   — use layout with fresh(work, 'Blank')
    Geography — use layout with fresh(work, '1_I Do-blank') etc. (or '2_...' per master)
    The badge (I Do / We Do etc.) comes from the slide layout — never add it in code.
"""

# ── Slide A — Full-bleed Background ──────────────────────────────────────────
# Image fills the slide. Semi-transparent banner at bottom carries title + subtitle.
# State-of-being icon sits bottom-right (added by layout — do not add in code).
A_FULL_BLEED = {
    'name':        'A — Full-bleed Background',
    'description': 'Image fills the slide; title in a banner at the bottom.',
    'image':       {'x':    81515, 'y':   88174, 'cx': 12038063, 'cy': 5269826},
    'banner':      {'x':    81516, 'y': 5368633, 'cx': 12028968, 'cy': 1411826},
    'title_box':   {'x':   300000, 'y': 5478000, 'cx': 11592000, 'cy':  553998},
    'subtitle':    {'x':   300000, 'y': 6188000, 'cx': 11592000, 'cy':  353943},
}

# ── Slide B1 — Hero Split (single image left) ─────────────────────────────────
# One large image on the left half; title above, text right.
B1_HERO_IMAGE_LEFT = {
    'name':        'B1 — Hero Split (1 image left)',
    'description': 'Single image left half; title top-left, text right.',
    'title':       {'x':    96057, 'y':   99956, 'cx': 10071847, 'cy':  648000},
    'image':       {'x':   259977, 'y': 1447720, 'cx':  5613400, 'cy': 4356100},
    'text_box':    {'x':  6046528, 'y': 1825625, 'cx':  5885495, 'cy': 3046988},
}

# ── Slide B2 — Hero Split (2 images stacked left) ────────────────────────────
# Two images stacked on the left; title top, text right.
B2_HERO_2IMAGES_LEFT = {
    'name':        'B2 — Hero Split (2 images stacked left)',
    'description': 'Two images stacked left; title top, text right.',
    'title':       {'x':    96057, 'y':  110589, 'cx': 10071847, 'cy':  648000},
    'image_top':   {'x':   371515, 'y':  919624, 'cx':  5473700, 'cy': 2755900},
    'image_bottom':{'x':   371515, 'y': 3847192, 'cx':  5473700, 'cy': 2743200},
    'text_box':    {'x':  6046528, 'y': 1825625, 'cx':  5885495, 'cy': 3046988},
}

# ── Slide B3 — Hero Split (2 images stacked right) ───────────────────────────
# Text/content left; two images stacked on the right.
B3_HERO_2IMAGES_RIGHT = {
    'name':        'B3 — Hero Split (2 images stacked right)',
    'description': 'Text/content left; two images stacked right.',
    'title':       {'x':   246529, 'y':  135257, 'cx': 10071847, 'cy':  641872},
    'text_box':    {'x':   246529, 'y': 1253331, 'cx':  5436642, 'cy': 4351338},
    'image_top':   {'x':  5676821, 'y':  942798, 'cx':  5486400, 'cy': 2743200},
    'image_bottom':{'x':  5683171, 'y': 3818567, 'cx':  5486400, 'cy': 2755900},
}

# ── Slide C — Supporting Illustration ────────────────────────────────────────
# Text body left; image right with optional caption below image.
C_SUPPORTING_ILLUSTRATION = {
    'name':        'C — Supporting Illustration',
    'description': 'Text left, image right with caption below.',
    'title':       {'x':   107632, 'y':  108529, 'cx': 10071847, 'cy':  648000},
    'text_box':    {'x':   200000, 'y': 1825625, 'cx':  5980652, 'cy': 2677656},
    'image':       {'x':  6162700, 'y': 1615880, 'cx':  5829300, 'cy': 4038600},
    'caption':     {'x':  6795115, 'y': 5654480, 'cx':  4745472, 'cy':  276999},
}

# ── Slide D — Diagram Focus ───────────────────────────────────────────────────
# Large image or diagram dominates left; labels / text in a right column.
D_DIAGRAM_FOCUS = {
    'name':        'D — Diagram Focus',
    'description': 'Large image left (2/3 width); text/labels right column.',
    'title':       {'x':   143445, 'y':  118120, 'cx': 10071847, 'cy':  648000},
    'image':       {'x':   251505, 'y': 1567565, 'cx':  8077310, 'cy': 4524315},
    'text_box':    {'x':  8455365, 'y': 1567565, 'cx':  3519855, 'cy': 4524315},
}

# ── Slide Gallery-5 — 5 images in a row ──────────────────────────────────────
# Task/instruction text above; five equally-spaced square images below.
GALLERY_5ROW = {
    'name':        'Gallery — 5 images in a row',
    'description': 'Task text above; 5 square images in a single row below.',
    'title':       {'x':   246529, 'y':  131209, 'cx': 10071847, 'cy':  648000},
    'task_box':    {'x':   246529, 'y': 1825625, 'cx':  7855750, 'cy': 1603375},
    'images': [
        {'x':   373199, 'y': 3319925, 'cx': 2070100, 'cy': 2070100},
        {'x':  2732019, 'y': 3319925, 'cx': 2070100, 'cy': 2070100},
        {'x':  5090839, 'y': 3319925, 'cx': 2070100, 'cy': 2070100},
        {'x':  7449659, 'y': 3319925, 'cx': 2070100, 'cy': 2070100},
        {'x':  9808479, 'y': 3319925, 'cx': 2070100, 'cy': 2070100},
    ],
}

# ── Slide Gallery-6x2 — 6×2 grid (12 images) ────────────────────────────────
# Compact task text above; twelve images in two rows of six.
GALLERY_6X2 = {
    'name':        'Gallery — 6×2 grid (12 images)',
    'description': 'Task text above; 12 images in two rows of 6.',
    'title':       {'x':   246529, 'y':  161372, 'cx': 10071847, 'cy':  699746},
    'task_box':    {'x':   246528, 'y': 1024630, 'cx': 10899891, 'cy': 2020618},
    'images': [
        # Row 1
        {'x':   556627, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        {'x':  2482729, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        {'x':  4408831, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        {'x':  6334933, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        {'x':  8261035, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        {'x': 10187137, 'y': 3208760, 'cx': 1587500, 'cy': 1574800},
        # Row 2
        {'x':   556627, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
        {'x':  2482729, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
        {'x':  4408831, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
        {'x':  6334933, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
        {'x':  8261035, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
        {'x': 10187137, 'y': 4947072, 'cx': 1587500, 'cy': 1574800},
    ],
}

# ── Slide Gallery-1wide — single wide image below text ───────────────────────
# Task/instruction text above; one landscape image spanning the full width below.
GALLERY_1WIDE = {
    'name':        'Gallery — 1 wide image below',
    'description': 'Task text above; single full-width image below.',
    'title':       {'x':   150830, 'y':  152475, 'cx': 10071847, 'cy':  613070},
    'task_box':    {'x':   246528, 'y': 1544939, 'cx': 11065472, 'cy': 1603375},
    'image':       {'x':   246527, 'y': 3340330, 'cx': 11605047, 'cy': 2308115},
}

# ── Slide Concept Cartoon ─────────────────────────────────────────────────────
# Central image with three character speech bubbles: A top-left, B top-right,
# C bottom-centre. Used as a provocation / discussion starter (NOT a replacement
# for the existing 'Who do you agree with?' slide — this is a separate layout).
CONCEPT_CARTOON = {
    'name':        'Concept Cartoon',
    'description': 'Central image; 3 speech-bubble characters (A top-left, B top-right, C bottom-centre).',
    'title':       {'x':   246528, 'y':  121489, 'cx': 10071847, 'cy':  648000},
    'central_image':{'x': 3987800, 'y': 1329159, 'cx':  4216400, 'cy': 3505200},
    # Bubble rectangles
    'bubble_a':    {'x':   250000, 'y': 1198927, 'cx':  3500000, 'cy': 1700000},
    'bubble_b':    {'x':  8442000, 'y': 1823960, 'cx':  3500000, 'cy': 1700000},
    'bubble_c':    {'x':  4196000, 'y': 5109610, 'cx':  3800000, 'cy': 1360000},
    # Text boxes (inset 100 000 EMU from bubble edges)
    'text_a':      {'x':   350000, 'y': 1298927, 'cx':  3300000, 'cy': 1500000},
    'text_b':      {'x':  8542000, 'y': 1923960, 'cx':  3300000, 'cy': 1500000},
    'text_c':      {'x':  4296000, 'y': 5209610, 'cx':  3600000, 'cy': 1160000},
}

# ── Master lookup dict ────────────────────────────────────────────────────────
LAYOUTS = {
    'A_full_bleed':              A_FULL_BLEED,
    'B1_hero_image_left':        B1_HERO_IMAGE_LEFT,
    'B2_hero_2images_left':      B2_HERO_2IMAGES_LEFT,
    'B3_hero_2images_right':     B3_HERO_2IMAGES_RIGHT,
    'C_supporting_illustration': C_SUPPORTING_ILLUSTRATION,
    'D_diagram_focus':           D_DIAGRAM_FOCUS,
    'gallery_5row':              GALLERY_5ROW,
    'gallery_6x2':               GALLERY_6X2,
    'gallery_1wide':             GALLERY_1WIDE,
    'concept_cartoon':           CONCEPT_CARTOON,
}


def get_layout(key):
    """Return the coordinate dict for *key*. Raises ValueError if not found."""
    if key not in LAYOUTS:
        raise ValueError(
            f"Unknown layout {key!r}. "
            f"Available: {', '.join(LAYOUTS)}"
        )
    return LAYOUTS[key]


def pick_layout(n_images, has_text=True, image_role='equal'):
    """
    Suggest a layout key from basic intent signals.

    n_images   — how many images the slide has
    has_text   — whether the slide carries body text alongside the image(s)
    image_role — 'main'      → image is the main content  (→ D or A)
                 'equal'     → image and text share equal weight  (→ B)
                 'support'   → image supports the text  (→ C)
                 'provoke'   → discussion starter  (→ concept_cartoon)

    Returns a layout key string. For gallery layouts (n_images > 2) returns
    the closest match; caller should always verify with Innes if unsure.
    """
    if image_role == 'provoke':
        return 'concept_cartoon'
    if n_images == 12:
        return 'gallery_6x2'
    if n_images == 5:
        return 'gallery_5row'
    if n_images == 1 and not has_text:
        return 'gallery_1wide'
    if n_images >= 3:
        return 'gallery_5row'  # fallback — caller should check
    if image_role == 'main':
        return 'D_diagram_focus'
    if image_role == 'support':
        return 'C_supporting_illustration'
    if n_images == 2:
        return 'B2_hero_2images_left'  # default for 2-image split
    # Default single-image split
    return 'B1_hero_image_left'
