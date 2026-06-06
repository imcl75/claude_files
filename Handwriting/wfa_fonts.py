"""
wfa_fonts.py — WFA Font Name Constants
=======================================
Wallscourt Farm Academy / Year 4 Maple

Single source of truth for every font name used across WFA resource scripts.
Change a font here and it propagates to all scripts on the next build.

USAGE (Python scripts)
----------------------
    from wfa_fonts import WFA

    # In PPTX string-building scripts (build_lesson_v3.py, writing build_lesson.py):
    sp(..., font=WFA.CURSIVE, ...)

    # In lxml-building scripts (working_memory_starters.py):
    make_rect(..., font=WFA.CURSIVE, ...)

    # When font=WFA.CURSIVE, the script must call xccw_render helpers to generate
    # correctly split 4a/4b runs — see xccw_render.py for xccw_p_xml() and
    # xccw_lxml_runs(). Scripts use WFA.is_xccw(font) to detect this case.

USAGE (JavaScript / pptxgenjs — build_lp_v3.js)
------------------------------------------------
    // Font names are duplicated as JS constants at the top of build_lp_v3.js.
    // The xccwText() helper in that file handles the 4a/4b split for pptxgenjs.

FONT SWAP NOTES
---------------
If you ever need to swap a font:
1. Update the constant here.
2. If swapping to/from XCCW, check xccw_render.py — the split logic lives there.
3. For non-XCCW fonts: check whether the new font has significantly different
   character metrics. Text boxes with fixed dimensions may need resizing.
   Measure width_ratio by comparing a sample string rendered in both fonts.
"""


class _Fonts:
    # ── Cursive / joined handwriting font ─────────────────────────────────────
    # Previously: "Twinkl Cursive Looped Light" / "Twinkl Cursive Looped"
    # Now: XCCW Joined (4a/4b split applied at render time by xccw_render.py)
    #
    # Do NOT use the string below directly as a typeface name — it is a sentinel.
    # Pass it as the `font` argument to sp() / text_box() / make_rect() and those
    # functions will call xccw_p_xml() or xccw_lxml_runs() to generate the correct
    # split runs automatically.
    CURSIVE = '__XCCW__'

    # ── Body / maths font ─────────────────────────────────────────────────────
    # Used for maths symbols (÷, ×, =, etc.) and any non-cursive body text.
    BODY = 'Aptos'

    # ── XCCW raw names (use via xccw_render — not directly in scripts) ────────
    XCCW_SOLID_4A  = 'XCCW Joined 4a'
    XCCW_SOLID_4B  = 'XCCW Joined 4b'
    XCCW_DOTTED_4A = 'XCCW Joined Dotted 4a'
    XCCW_DOTTED_4B = 'XCCW Joined Dotted 4b'

    @staticmethod
    def is_xccw(font_value):
        """Return True if this font value is the XCCW sentinel."""
        return font_value == '__XCCW__'


WFA = _Fonts()
