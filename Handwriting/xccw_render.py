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


# ── Internal helpers ───────────────────────────────────────────────────────────

def _xml_esc(s):
    """XML-escape a string for safe embedding in attribute values or text nodes."""
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;'))


def _split_chunks(text, solid=True):
    """
    Split text into [(chunk, variant_name), ...] applying the 4a/4b join rule.

    Parameters
    ----------
    text : str
    solid : bool
        True  → 'XCCW Joined 4a' / 'XCCW Joined 4b'
        False → 'XCCW Joined Dotted 4a' / 'XCCW Joined Dotted 4b'

    Returns
    -------
    list of (str, str) — (text_chunk, font_variant_name)
    """
    name_4a = 'XCCW Joined 4a'       if solid else 'XCCW Joined Dotted 4a'
    name_4b = 'XCCW Joined 4b'       if solid else 'XCCW Joined Dotted 4b'

    chunks   = []
    current  = ''
    cur_var  = name_4a  # first character always 4a

    for i, ch in enumerate(text):
        # A space resets join context — character after a space is always 4a
        prev = text[i - 1] if i > 0 else None
        if prev == ' ':
            prev = None
        var = name_4b if (prev and prev.lower() in TOP_EXIT) else name_4a

        if not current:
            current = ch
            cur_var = var
        elif var == cur_var:
            current += ch
        else:
            chunks.append((current, cur_var))
            current = ch
            cur_var = var

    if current:
        chunks.append((current, cur_var))

    return chunks


# ── Python string-building helper (for build_lesson_v3.py, writing build_lesson.py) ──

def xccw_p_xml(text, sz_hundredths, bold=False, color_hex='000000',
               align='l', underline=False, solid=True):
    """
    Return a complete <a:p>...</a:p> XML string with correctly split XCCW runs,
    for use in PPTX scripts that build slide XML via string concatenation.

    Parameters
    ----------
    text : str
        The text to render. Empty string produces an empty paragraph.
    sz_hundredths : int
        Font size in hundredths of a point (e.g. 1800 = 18pt, 4000 = 40pt).
    bold : bool
    color_hex : str
        6-character hex colour without '#' (e.g. '000000', '0E2841').
    align : str
        'l', 'ctr', 'r' — maps to PowerPoint paragraph alignment.
    underline : bool
    solid : bool
        True → solid XCCW font (default). False → dotted tracing variant.

    Returns
    -------
    str  — complete <a:p>...</a:p> XML
    """
    b_attr = ' b="1"' if bold else ''
    u_attr = ' u="sng"' if underline else ''
    color_xml = f'<a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>'

    if not text:
        # Empty paragraph — needed for spacing between content
        return (f'<a:p><a:pPr algn="{align}"/>'
                f'<a:endParaRPr lang="en-GB" sz="{sz_hundredths}"{b_attr} dirty="0">'
                f'{color_xml}<a:latin typeface="XCCW Joined 4a"/>'
                f'</a:endParaRPr></a:p>')

    runs = ''
    for chunk, variant in _split_chunks(text, solid=solid):
        runs += (
            f'<a:r>'
            f'<a:rPr lang="en-GB" sz="{sz_hundredths}"{b_attr}{u_attr} dirty="0">'
            f'{color_xml}<a:latin typeface="{variant}"/>'
            f'</a:rPr>'
            f'<a:t>{_xml_esc(chunk)}</a:t>'
            f'</a:r>'
        )

    return f'<a:p><a:pPr algn="{align}"/>{runs}</a:p>'


# ── lxml helper (for working_memory_starters.py and any lxml-based script) ────

def xccw_lxml_runs(parent_para, text, sz_pt, bold=False,
                   color_hex='000000', solid=True):
    """
    Append correctly-joined XCCW <a:r> lxml elements to an existing <a:p> element.

    Call this instead of creating a single <a:r> with one typeface when the font
    should be XCCW. Handles the full 4a/4b split automatically.

    Parameters
    ----------
    parent_para : lxml.etree._Element
        The <a:p> element to append runs to. Must already exist.
    text : str
        Text to render.
    sz_pt : float
        Font size in points (e.g. 40.0). Converted to hundredths internally.
    bold : bool
    color_hex : str
        6-character hex without '#'.
    solid : bool
        True → solid font. False → dotted tracing font.
    """
    from lxml import etree

    A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    def _a(tag):
        return f'{{{A_NS}}}{tag}'

    sz_str = str(int(sz_pt * 100))

    for chunk, variant in _split_chunks(text, solid=solid):
        run = etree.SubElement(parent_para, _a('r'))
        rPr = etree.SubElement(run, _a('rPr'),
                               lang='en-GB',
                               sz=sz_str,
                               b='1' if bold else '0',
                               dirty='0')
        sf = etree.SubElement(rPr, _a('solidFill'))
        etree.SubElement(sf, _a('srgbClr'), val=color_hex)
        etree.SubElement(rPr, _a('latin'), typeface=variant)
        t_el = etree.SubElement(run, _a('t'))
        t_el.text = chunk
