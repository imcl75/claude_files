#!/usr/bin/env python3
"""
etiw_generate.py  -  Every Time I Write PPTX generator (non-interactive)
=========================================================================

Usage (called by Claude, not interactively):
    python etiw_generate.py \
        --template /path/to/easter_etiw.pptx \
        --output /path/to/T5W1_ETIW.pptx \
        --plain "The correct paragraph text here." \
        --spelling "word1, word2, word3" \
        --checklist3 "Have you identified sentences with..." \
        --errors "The <<mispelled>> error paragraph with _______."

All the XML-editing logic is identical to the original interactive script.
Dependencies: standard library only (zipfile, shutil, re, os).
"""

import os
import re
import sys
import shutil
import zipfile
import tempfile
import argparse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GREEN   = "49B949"
RED     = "FF0000"
APOS    = "\u2019"       # right single quotation mark
APOS_X  = "&#x2019;"    # XML entity


# ---------------------------------------------------------------------------
# Low-level XML helpers
# ---------------------------------------------------------------------------

def _xml_escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace(APOS, APOS_X))


def _run(text, colour=None, sz=None, err=False):
    """Return a single <a:r>...</a:r> run."""
    attrs = 'lang="en-GB" dirty="0"'
    if sz:
        attrs += f' sz="{sz}"'
    if err:
        attrs += ' err="1"'

    if colour:
        fill = f"<a:solidFill><a:srgbClr val=\"{colour}\"/></a:solidFill>"
        rpr = f"<a:rPr {attrs}>{fill}</a:rPr>"
    else:
        rpr = f"<a:rPr {attrs}/>"

    safe = _xml_escape(text)
    needs_preserve = (safe != safe.strip()) or ("  " in safe)
    t_attr = ' xml:space="preserve"' if needs_preserve else ""
    return f"<a:r>{rpr}<a:t{t_attr}>{safe}</a:t></a:r>"


def _wrap_para(runs_xml, line_spacing_pct=None):
    """Wrap run strings in <a:p> with buNone."""
    lspc = ""
    if line_spacing_pct:
        lspc = f'<a:lnSpc><a:spcPct val="{line_spacing_pct}"/></a:lnSpc>'
    return (
        f'<a:p>'
        f'<a:pPr marL="0" indent="0">{lspc}<a:buNone/></a:pPr>'
        f"{''.join(runs_xml)}"
        f"</a:p>"
    )


# ---------------------------------------------------------------------------
# Paragraph builders
# ---------------------------------------------------------------------------

def build_punc_pass(plain_text):
    """
    Punctuation pass: highlight GREEN every capital letter, comma,
    full stop, question mark, exclamation mark, and apostrophe.
    Everything else is plain black.
    """
    PUNC_CHARS = set(".,!?")
    runs = []
    i = 0
    while i < len(plain_text):
        ch = plain_text[i]
        if ch in PUNC_CHARS:
            runs.append(_run(ch, GREEN))
            i += 1
        elif ch == APOS:
            runs.append(_run(APOS, GREEN))
            i += 1
        elif ch == '"' or ch == '\u201c' or ch == '\u201d':
            runs.append(_run(ch, GREEN))
            i += 1
        elif ch.isupper():
            runs.append(_run(ch, GREEN))
            i += 1
        else:
            j = i
            while (j < len(plain_text)
                   and plain_text[j] not in PUNC_CHARS
                   and plain_text[j] != APOS
                   and plain_text[j] not in ('"', '\u201c', '\u201d')
                   and not plain_text[j].isupper()):
                j += 1
            runs.append(_run(plain_text[i:j]))
            i = j
    return _wrap_para(runs)


def build_spell_pass(plain_text, spell_words):
    """
    Spelling pass: highlight RED every token that matches a supplied
    spelling-focus word. Matching strips possessive suffixes and is
    case-insensitive. All other tokens are plain black.
    """
    targets = set()
    for w in spell_words:
        base = w.strip().lower()
        targets.add(base)
        stripped = re.sub(r"[\u2019']s?$", "", base)
        targets.add(stripped)

    runs = []
    tokens = re.findall(r"[\w\u2019'-]+|[^\w\u2019'-]+", plain_text)
    for token in tokens:
        norm = token.lower()
        bare = re.sub(r"[\u2019']s?$", "", norm).rstrip(".,!?")
        if norm in targets or bare in targets:
            runs.append(_run(token, RED))
        else:
            runs.append(_run(token))
    return _wrap_para(runs)


def build_error_para(error_text_raw):
    """
    Pupil error paragraph. Caller marks misspelled words with <<angle brackets>>.
    Those words get err="1" and sz="2800". Everything else is plain sz="2800".
    Use plain underscores for blanks: _______.
    """
    parts = re.split(r"(<<[^>]+>>)", error_text_raw)
    runs = []
    for part in parts:
        m = re.match(r"<<(.+?)>>", part)
        if m:
            runs.append(_run(m.group(1), sz="2800", err=True))
        elif part:
            runs.append(_run(part, sz="2800"))
    return _wrap_para(runs, line_spacing_pct="200000")


# ---------------------------------------------------------------------------
# Slide editors
# ---------------------------------------------------------------------------

def edit_slide2(xml, punc_para, spell_para, checklist_item3):
    """Edit the review slide."""

    # --- Checklist item 3 -------------------------------------------------
    ITEM3_ANCHOR = "Commas after fronted adverbials?"
    idx = xml.find(ITEM3_ANCHOR)
    if idx == -1:
        raise ValueError("Checklist item 3 anchor not found in slide 2.")
    t_start = xml.rfind("<a:t>", 0, idx)
    t_end   = xml.find("</a:t>", idx) + len("</a:t>")
    xml = xml[:t_start] + f"<a:t>{_xml_escape(checklist_item3)}</a:t>" + xml[t_end:]

    # --- Punctuation block (id=20) ----------------------------------------
    anchor_b1 = 'id="20" name="Content Placeholder 2"'
    idx_b1 = xml.find(anchor_b1)
    if idx_b1 == -1:
        raise ValueError("Block 1 anchor (id=20) not found in slide 2.")
    lstyle_end = xml.find("</a:lstStyle>", idx_b1) + len("</a:lstStyle>")
    p_start    = xml.find("<a:p>", lstyle_end)
    p_end      = xml.find("</a:p>", p_start) + len("</a:p>")
    xml = xml[:p_start] + punc_para + xml[p_end:]

    # --- Spelling block (id=18) -------------------------------------------
    anchor_b2 = 'id="18" name="Content Placeholder 2"'
    idx_b2 = xml.find(anchor_b2)
    if idx_b2 == -1:
        raise ValueError("Block 2 anchor (id=18) not found in slide 2.")
    lstyle_end2 = xml.find("</a:lstStyle>", idx_b2) + len("</a:lstStyle>")
    p2_start    = xml.find("<a:p>", lstyle_end2)
    p2_end      = xml.find("</a:p>", p2_start) + len("</a:p>")
    xml = xml[:p2_start] + spell_para + xml[p2_end:]

    return xml


def edit_slide3(xml, plain_text):
    """Replace all three teacher-copy paragraphs."""
    safe = _xml_escape(plain_text)
    new_para = (
        f'<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>'
        f'<a:r><a:rPr lang="en-GB" sz="1800" dirty="0"/>'
        f'<a:t>{safe}</a:t></a:r></a:p>'
    )
    ANCHOR = "church bells began to ring out across the valley"
    spans = []
    search_from = 0
    while True:
        idx = xml.find(ANCHOR, search_from)
        if idx == -1:
            break
        p_start = xml.rfind("<a:p>", 0, idx)
        p_end   = xml.find("</a:p>", idx) + len("</a:p>")
        spans.append((p_start, p_end))
        search_from = p_end
    if not spans:
        raise ValueError("Teacher-copy anchor not found in slide 3.")
    for p_start, p_end in reversed(spans):
        xml = xml[:p_start] + new_para + xml[p_end:]
    print(f"    Slide 3: replaced {len(spans)} column(s).")
    return xml


def edit_slide4(xml, error_para):
    """Replace the pupil error paragraph."""
    idx = xml.find('err="1"')
    if idx == -1:
        raise ValueError("Error-paragraph anchor (err=1) not found in slide 4.")
    p_start = xml.rfind("<a:p>", 0, idx)
    p_end   = xml.find("</a:p>", idx) + len("</a:p>")
    xml = xml[:p_start] + error_para + xml[p_end:]
    return xml


# ---------------------------------------------------------------------------
# PPTX builder
# ---------------------------------------------------------------------------

def build_pptx(template_path, output_path, slide_edits):
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(template_path, "r") as zf:
            zf.extractall(tmp)

        for slide_n, editor in slide_edits.items():
            path = os.path.join(tmp, "ppt", "slides", f"slide{slide_n}.xml")
            with open(path, encoding="utf-8") as f:
                xml = f.read()
            xml = editor(xml)
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(tmp):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    zout.write(fpath, os.path.relpath(fpath, tmp))
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Main (non-interactive, argument-driven)
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ETIW PPTX Generator")
    parser.add_argument("--template", required=True, help="Path to easter_etiw.pptx template")
    parser.add_argument("--output", required=True, help="Output PPTX path")
    parser.add_argument("--plain", required=True, help="Plain correct paragraph (3 sentences)")
    parser.add_argument("--spelling", required=True, help="Comma-separated spelling focus words")
    parser.add_argument("--checklist3", required=True, help="Checklist item 3 text")
    parser.add_argument("--errors", required=True, help="Error paragraph with <<misspellings>> and _______")
    args = parser.parse_args()

    # Normalise apostrophes
    plain = args.plain.replace("'", APOS)

    # Parse spelling words
    spell_words = [w.strip() for w in args.spelling.split(",") if w.strip()]

    # Build XML fragments
    print("Building ETIW PPTX...")
    punc_para  = build_punc_pass(plain)
    spell_para = build_spell_pass(plain, spell_words)
    error_para = build_error_para(args.errors)

    # Wire up editors
    def ed2(xml): return edit_slide2(xml, punc_para, spell_para, args.checklist3)
    def ed3(xml): return edit_slide3(xml, plain)
    def ed4(xml): return edit_slide4(xml, error_para)

    build_pptx(args.template, args.output, {2: ed2, 3: ed3, 4: ed4})
    print(f"  Saved: {args.output}")


if __name__ == "__main__":
    main()
