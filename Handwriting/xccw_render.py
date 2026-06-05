"""
xccw_render.py — Shared XCCW Cursive Join Rule Utility
=======================================================
Wallscourt Farm Academy / Year 4 Maple

This module is the single source of truth for XCCW font-switching logic.
Import it into any WFA skill that needs to render XCCW cursive text via
ReportLab, rather than reimplementing the rule independently.

XCCW JOIN RULE
--------------
The XCCW Joined font family has two variants per style:

  4a  — standard join (used after most letters, and always for the first
        character of a word)
  4b  — top-exit join (used when the PREVIOUS character is one of: o r v w x)

These five letters exit at the top of the letter body, so the next letter
must start from the top rather than the baseline join point.  Using the
wrong variant produces a visually broken join in the pupil's handwriting.

Font names used by ReportLab (must match registered TTFont names):
  Dotted:  XCCW_Joined_Dotted_4a  /  XCCW_Joined_Dotted_4b
  Solid:   XCCW_Joined_4a         /  XCCW_Joined_4b

USAGE
-----
  from xccw_render import xccw_font_for, draw_xccw, xccw_text_width, TOP_EXIT

  # Which font variant for a single character?
  font_name = xccw_font_for(ch='a', prev='r', solid=False)

  # Draw a full word/string on a ReportLab canvas (fonts must already be
  # registered — see handwriting_sheet.py for _ensure_fonts() pattern):
  draw_xccw(canvas, x=50, y=200, text='river', size=26, solid=False)

  # Measure width without drawing:
  w = xccw_text_width('river', solid=False, size=26)

NOTE: Font registration (embedding the base64 TTF data and calling
pdfmetrics.registerFont) must happen before calling draw_xccw.  The
canonical implementation of this is _ensure_fonts() in handwriting_sheet.py.
Other skills that use this module but do not import handwriting_sheet must
register the fonts themselves.
"""

# ── Join rule constant ─────────────────────────────────────────────────────────

TOP_EXIT = frozenset('orvwx')
"""
The five letters whose pen stroke exits at the top of the letter body.
The character AFTER any of these must use the 4b font variant.
This set should never be modified — it reflects the physical design of the
XCCW Joined typeface.
"""

# ── Font name helpers ──────────────────────────────────────────────────────────

def xccw_font_for(ch, prev, solid=False):
    """
    Return the correct XCCW ReportLab font name for a character.

    Parameters
    ----------
    ch : str
        The character being rendered (not used in the decision, but
        included for call-site clarity and future extensibility).
    prev : str or None
        The character immediately before ch in the word/string.
        Pass None (or '') for the first character of a word.
    solid : bool
        False → dotted variant (practice tracing).
        True  → solid variant (teacher model / display).

    Returns
    -------
    str
        One of: 'XCCW_Joined_Dotted_4a', 'XCCW_Joined_Dotted_4b',
                'XCCW_Joined_4a', 'XCCW_Joined_4b'
    """
    use_4b = bool(prev) and prev.lower() in TOP_EXIT
    if solid:
        return 'XCCW_Joined_4b' if use_4b else 'XCCW_Joined_4a'
    return 'XCCW_Joined_Dotted_4b' if use_4b else 'XCCW_Joined_Dotted_4a'


# ── Drawing helper ─────────────────────────────────────────────────────────────

def draw_xccw(canvas, x, y, text, size=26, solid=False, colour_rgb=None):
    """
    Draw an XCCW cursive string on a ReportLab canvas, applying the correct
    4a/4b font variant character by character.

    Parameters
    ----------
    canvas : reportlab.pdfgen.canvas.Canvas
        Active canvas to draw on.
    x : float
        Left edge of the first character, in points.
    y : float
        Baseline y-coordinate, in points.
    text : str
        The text to render.  Spaces are rendered with 4a regardless of
        the character before them (a space resets the join context for
        the following letter, which will therefore also use 4a).
    size : float
        Font size in points.  Default 26pt matches WFA handwriting sheets.
    solid : bool
        False → dotted tracing font.  True → solid display font.
    colour_rgb : tuple of three floats in [0,1], or None
        Fill colour as (R, G, B).  Defaults to WFA navy (14/255, 40/255, 65/255).

    Notes
    -----
    Fonts must already be registered with ReportLab before calling this
    function.  Call handwriting_sheet._ensure_fonts() if using alongside
    that module, or register the four XCCW font names yourself.
    """
    if colour_rgb is None:
        colour_rgb = (14/255, 40/255, 65/255)  # WFA navy

    canvas.setFillColorRGB(*colour_rgb)

    prev = None
    for ch in text:
        font = xccw_font_for(ch, prev, solid=solid)
        canvas.setFont(font, size)
        canvas.drawString(x, y, ch)
        x += canvas.stringWidth(ch, font, size)
        # A space resets join context — the letter after a space is always 4a
        prev = None if ch == ' ' else ch


# ── Width measurement ──────────────────────────────────────────────────────────

def xccw_text_width(text, solid=False, size=26):
    """
    Return the rendered width (in points) of a string in XCCW cursive,
    applying the correct 4a/4b variants throughout.

    Requires fonts to be registered (same constraint as draw_xccw).

    Parameters
    ----------
    text : str
    solid : bool
    size : float

    Returns
    -------
    float
        Total width in points.
    """
    from reportlab.pdfbase import pdfmetrics

    total = 0.0
    prev = None
    for ch in text:
        font = xccw_font_for(ch, prev, solid=solid)
        total += pdfmetrics.stringWidth(ch, font, size)
        prev = None if ch == ' ' else ch
    return total


# ── Quick reference ────────────────────────────────────────────────────────────

RULE_SUMMARY = """
XCCW Join Rule (quick reference)
---------------------------------
  Top-exit letters: o  r  v  w  x
  When the PREVIOUS character is one of these five, the NEXT character
  uses font variant 4b.  All other characters use 4a.
  The first character of every word always uses 4a.
  A space resets the context — the character after a space uses 4a.

  Dotted fonts:  XCCW_Joined_Dotted_4a  /  XCCW_Joined_Dotted_4b
  Solid fonts:   XCCW_Joined_4a         /  XCCW_Joined_4b
"""


# ── PPTX XML helpers ───────────────────────────────────────────────────────────

def xccw_pptx_runs(text, rpr_template, solid=False):
    """
    Generate correctly-joined XCCW runs as PPTX XML for a text string.

    A PPTX text run uses a single typeface for the whole run.  To get correct
    XCCW joins, any character that follows a top-exit letter (o r v w x) must
    be in a separate run using the 4b font variant.  This function splits the
    text into the minimum number of runs needed and returns them as XML.

    Parameters
    ----------
    text : str
        The word or phrase to render.
    rpr_template : str
        A complete `<a:rPr ...>...</a:rPr>` XML string from the slide's
        existing run, with the typeface attribute included.  The function
        replaces the typeface name with 4a or 4b as required and wraps each
        segment in `<a:r>...</a:r>`.
    solid : bool
        False → dotted variant names (XCCW Joined Dotted 4a/4b).
        True  → solid variant names (XCCW Joined 4a/4b).

    Returns
    -------
    str
        One or more `<a:r>` elements as a single XML string, ready to replace
        the original single run in the slide XML.

    Example
    -------
        rpr = '<a:rPr lang="en-GB" sz="3200" b="0"><a:solidFill>' \\
              '<a:schemeClr val="tx1"/></a:solidFill>' \\
              '<a:latin typeface="XCCW Joined 4a" .../></a:rPr>'
        runs_xml = xccw_pptx_runs('cautious', rpr)
        # Returns three <a:r> elements:
        #   cautio → 4a,  u → 4b,  s → 4a
    """
    import re as _re

    if solid:
        name_4a, name_4b = 'XCCW Joined 4a', 'XCCW Joined 4b'
    else:
        name_4a, name_4b = 'XCCW Joined Dotted 4a', 'XCCW Joined Dotted 4b'

    # Split text into chunks, each sharing the same variant
    chunks = []   # list of (text_chunk, variant_name)
    current = ''
    current_var = name_4a  # first character always 4a

    for i, ch in enumerate(text):
        prev = text[i - 1] if i > 0 else None
        # Space resets join context
        if prev == ' ':
            prev = None
        var = name_4b if (prev and prev.lower() in TOP_EXIT) else name_4a

        if i == 0 or var == current_var:
            current += ch
            current_var = var
        else:
            chunks.append((current, current_var))
            current = ch
            current_var = var

    if current:
        chunks.append((current, current_var))

    # Build XML runs
    parts = []
    for chunk_text, variant in chunks:
        # Swap the typeface name in the rPr template
        rpr = _re.sub(
            r'typeface="[^"]*XCCW[^"]*"',
            f'typeface="{variant}"',
            rpr_template
        )
        parts.append(f'<a:r>{rpr}<a:t>{chunk_text}</a:t></a:r>')

    return '\n'.join(parts)


def needs_xccw_split(text):
    """
    Return True if text contains a character that follows a top-exit letter,
    meaning a single PPTX run with one XCCW typeface will produce a wrong join.

    Use this as a quick check before calling xccw_pptx_runs.
    """
    for i in range(1, len(text)):
        prev = text[i - 1]
        if prev != ' ' and prev.lower() in TOP_EXIT:
            return True
    return False
