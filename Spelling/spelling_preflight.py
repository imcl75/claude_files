#!/usr/bin/env python3
"""
spelling_preflight.py — Pre-build validator for Spelling Shed lesson.json.

Run this BEFORE any build step (before node slides-template.js).
Catches content problems that would produce broken, missing or trivial slides.

Usage:
    python3 spelling_preflight.py lesson.json
    python3 spelling_preflight.py                 # looks for /home/claude/lesson.json

Exit 0 = all clear. Exit 1 = errors found (block the build).
"""

import json, os, sys, re

MAX_BASEFORM_CHARS   = 12
MAX_DEFINITION_CHARS = 70
REQUIRED_WORDS       = 10
REQUIRED_LP_VN_PAIRS = 6
REQUIRED_LP_DEFS     = 5
REQUIRED_SPELL_DATA  = 5


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load_lesson(path):
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"lesson.json is not valid JSON: {e}"
    except FileNotFoundError:
        return None, f"File not found: {path}"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_required_top_keys(lesson, errors, warnings):
    required = [
        'code', 'rule', 'stage', 'objective', 'lpDay', 'lpSideBType',
        'words', 'clozeOrder', 'defs', 'sentences',
        'syllableCounts', 'phonemes', 'wordMaps',
        'starter', 'etymology', 'wordSort', 'spellData',
        'wordShed', 'morphMatrix',
        'lpVerbNounName', 'lpVerbNounInstr', 'lpVerbNoun',
        'lpDefMatchName', 'lpDefMatchInstr', 'lpDefinitions', 'lpDefMatchAnswers',
        'thisWeeksWordsQ', 'thisWeeksWordsPrompt', 'thisWeeksWordsExplanation',
        'wordSortQ',
    ]
    for k in required:
        if k not in lesson:
            errors.append(f"Missing required key: '{k}'")


def check_words(lesson, errors, warnings):
    words = lesson.get('words', [])
    if not isinstance(words, list):
        errors.append("'words' must be a list"); return
    if len(words) != REQUIRED_WORDS:
        errors.append(f"'words' must have exactly {REQUIRED_WORDS} entries, got {len(words)}")
    for i, w in enumerate(words):
        if not isinstance(w, str) or not w.strip():
            errors.append(f"'words[{i}]' is empty or not a string")
        elif w != w.lower():
            warnings.append(f"'words[{i}]' = {w!r} — words should be lowercase")


def check_cloze_order(lesson, errors, warnings):
    words    = lesson.get('words', [])
    cloze    = lesson.get('clozeOrder', [])

    if not isinstance(cloze, list):
        errors.append("'clozeOrder' must be a list"); return
    if len(cloze) != len(words):
        errors.append(f"'clozeOrder' must have {len(words)} entries (same as words), got {len(cloze)}")
        return

    # Check no word is at the same position as its sentence
    collisions = [
        f"position {i}: words[{i}]={words[i]!r} == clozeOrder[{i}]={cloze[i]!r}"
        for i in range(len(words))
        if i < len(cloze) and words[i] == cloze[i]
    ]
    if collisions:
        errors.append(
            "clozeOrder collision — pupils see word next to its own sentence (activity is trivial):\n"
            + "\n  ".join(collisions)
        )

    # Check clozeOrder contains exactly the same words as words (just shuffled)
    if sorted(words) != sorted(cloze):
        errors.append("clozeOrder must contain exactly the same words as 'words', just in a different order")


def check_defs_and_sentences(lesson, errors, warnings):
    words = lesson.get('words', [])
    defs  = lesson.get('defs', [])
    sents = lesson.get('sentences', {})

    if not isinstance(defs, list):
        errors.append("'defs' must be a list"); return
    if len(defs) != len(words):
        errors.append(f"'defs' must have {len(words)} entries, got {len(defs)}")
    for i, d in enumerate(defs):
        if not isinstance(d, str) or not d.strip():
            errors.append(f"'defs[{i}]' is empty")

    if not isinstance(sents, dict):
        errors.append("'sentences' must be a dict keyed by word"); return
    words_needing_sents = lesson.get('words', [])[:6]
    for w in words_needing_sents:
        if w not in sents:
            errors.append(f"'sentences' has no entry for word '{w}' (first 6 words need sentences)")
        elif not isinstance(sents[w], str) or not sents[w].strip():
            errors.append(f"Sentence for '{w}' is empty or not a string")


def check_starter(lesson, errors, warnings):
    starter = lesson.get('starter', {})
    if not isinstance(starter, dict):
        errors.append("'starter' must be a dict"); return

    per_pair = starter.get('perPairNote', None)
    if per_pair is None:
        errors.append("starter.perPairNote is missing — must be set to \"\" (empty string)")
    elif per_pair != '':
        errors.append(
            f"starter.perPairNote = {per_pair!r} — must be empty string \"\".\n"
            f"  This note appears on EVERY word pair on the answers slide (6 times).\n"
            f"  Move any teaching note into starter.ruleBox instead."
        )

    for key in ['question', 'words', 'answers', 'answerLabel', 'ruleBox']:
        if key not in starter:
            warnings.append(f"starter.{key} is missing")

    starter_words = starter.get('words', [])
    if isinstance(starter_words, list):
        for i, w in enumerate(starter_words):
            if isinstance(w, str) and w != w.lower():
                errors.append(
                    f"starter.words[{i}] = {w!r} — must be lowercase.\n"
                    f"  inject_key_spelling.py uses literal string replacement and will miss UPPERCASE."
                )


def check_etymology(lesson, errors, warnings):
    etym = lesson.get('etymology', {})
    if not isinstance(etym, dict):
        errors.append("'etymology' must be a dict"); return

    base = etym.get('baseForm', '')
    if not base:
        warnings.append("etymology.baseForm is empty")
    elif len(base) > MAX_BASEFORM_CHARS:
        errors.append(
            f"etymology.baseForm = {base!r} is {len(base)} chars "
            f"(max {MAX_BASEFORM_CHARS}). Rendered at 26pt in a 2.5\" box — will overflow."
        )

    if 'word' not in etym:
        errors.append("etymology.word is missing")
    if 'clicks' not in etym:
        warnings.append("etymology.clicks is missing (used for animation reveal)")


def check_word_sort(lesson, errors, warnings):
    ws = lesson.get('wordSort', {})
    if not isinstance(ws, dict):
        errors.append("'wordSort' must be a dict"); return

    for key in ['box1label', 'box1sub', 'box2label', 'box2sub', 'hint', 'answerNote']:
        if not ws.get(key):
            warnings.append(f"wordSort.{key} is missing or empty")

    # verbNoun must be a list of dicts with 'word' and 'eg'
    vn = ws.get('verbNoun', [])
    if not isinstance(vn, list):
        errors.append(
            f"wordSort.verbNoun must be a list of {{word, eg}} objects, got {type(vn).__name__}.\n"
            f"  Plain strings produce 'undefined' on the answers slide."
        )
    else:
        for i, item in enumerate(vn):
            if not isinstance(item, dict):
                errors.append(
                    f"wordSort.verbNoun[{i}] = {item!r} — must be a dict with 'word' and 'eg' keys, "
                    f"not a plain string."
                )
            else:
                for k in ['word', 'eg']:
                    if k not in item:
                        errors.append(f"wordSort.verbNoun[{i}] missing key '{k}'")

    # verbOnly must be a plain list of strings
    vo = ws.get('verbOnly', [])
    if not isinstance(vo, list):
        errors.append(f"wordSort.verbOnly must be a list of strings, got {type(vo).__name__}")
    else:
        for i, item in enumerate(vo):
            if not isinstance(item, str):
                errors.append(f"wordSort.verbOnly[{i}] must be a string, got {type(item).__name__}")


def check_spell_data(lesson, errors, warnings):
    sd = lesson.get('spellData', [])
    if not isinstance(sd, list):
        errors.append("'spellData' must be a list"); return
    if len(sd) != REQUIRED_SPELL_DATA:
        errors.append(f"'spellData' must have {REQUIRED_SPELL_DATA} entries, got {len(sd)}")

    for i, item in enumerate(sd):
        if not isinstance(item, dict):
            errors.append(f"spellData[{i}] must be a dict"); continue
        opts = item.get('opts', [])
        correct = item.get('correct', None)
        if not isinstance(opts, list) or len(opts) != 3:
            errors.append(f"spellData[{i}].opts must be a list of 3 strings, got {opts!r}")
        if correct not in (0, 1, 2):
            errors.append(f"spellData[{i}].correct must be 0, 1 or 2 (column index), got {correct!r}")

    # Check that correct positions are spread across columns — not all in column 0
    if len(sd) == REQUIRED_SPELL_DATA:
        positions = [item.get('correct') for item in sd if isinstance(item, dict)]
        if positions and len(set(positions)) == 1:
            warnings.append(
                f"All {REQUIRED_SPELL_DATA} spellData entries have correct={positions[0]}. "
                f"Randomise the correct-column position across rows to avoid a predictable pattern."
            )


def check_lp_fields(lesson, errors, warnings):
    lp_day = lesson.get('lpDay', '')
    lp_type = lesson.get('lpSideBType', '')

    if lp_day not in ('Mon', 'Tue', 'Wed'):
        errors.append(f"lpDay = {lp_day!r} — must be 'Mon', 'Tue' or 'Wed'")

    if lp_type not in ('vn_dm_sc', 'sc_dm'):
        errors.append(f"lpSideBType = {lp_type!r} — must be 'vn_dm_sc' or 'sc_dm'")

    # LP VerbNoun pairs
    lpvn = lesson.get('lpVerbNoun', [])
    if not isinstance(lpvn, list):
        errors.append("lpVerbNoun must be a list"); return
    if len(lpvn) != REQUIRED_LP_VN_PAIRS:
        errors.append(
            f"lpVerbNoun must have exactly {REQUIRED_LP_VN_PAIRS} pairs (rows), got {len(lpvn)}"
        )
    for i, pair in enumerate(lpvn):
        if not isinstance(pair, list) or len(pair) != 2:
            errors.append(f"lpVerbNoun[{i}] must be [shown, answer], got {pair!r}")

    # LP definitions
    defs = lesson.get('lpDefinitions', [])
    if not isinstance(defs, list):
        errors.append("lpDefinitions must be a list"); return
    if len(defs) != REQUIRED_LP_DEFS:
        errors.append(f"lpDefinitions must have {REQUIRED_LP_DEFS} entries, got {len(defs)}")
    for i, d in enumerate(defs):
        if not isinstance(d, str):
            errors.append(f"lpDefinitions[{i}] must be a string")
        elif len(d) > MAX_DEFINITION_CHARS:
            warnings.append(
                f"lpDefinitions[{i}] is {len(d)} chars (max {MAX_DEFINITION_CHARS}). "
                f"May overflow the 1.056cm row at 9.5pt: {d!r}"
            )

    # LP answers
    answers = lesson.get('lpDefMatchAnswers', [])
    if not isinstance(answers, list):
        errors.append("lpDefMatchAnswers must be a list")
    elif len(answers) != len(defs):
        errors.append(
            f"lpDefMatchAnswers must have {len(defs)} entries (matching lpDefinitions), "
            f"got {len(answers)}"
        )


def check_lp_side_b_consistency(lesson, errors, warnings):
    """Mon/Wed should use vn_dm_sc; Tue should use sc_dm."""
    lp_day  = lesson.get('lpDay', '')
    lp_type = lesson.get('lpSideBType', '')
    expected = {'Mon': 'vn_dm_sc', 'Wed': 'vn_dm_sc', 'Tue': 'sc_dm'}
    if lp_day in expected and lp_type != expected[lp_day]:
        warnings.append(
            f"lpSideBType = {lp_type!r} for {lp_day}. "
            f"Convention: Mon/Wed → 'vn_dm_sc', Tue → 'sc_dm'. "
            f"Override only if content strongly justifies it."
        )


def check_word_maps(lesson, errors, warnings):
    wm = lesson.get('wordMaps', {})
    if not isinstance(wm, dict):
        errors.append("'wordMaps' must be a dict"); return

    wm_words = wm.get('words', [])
    if not isinstance(wm_words, list) or len(wm_words) not in (5, 6):
        warnings.append(
            f"wordMaps.words has {len(wm_words) if isinstance(wm_words, list) else '?'} entries. "
            f"Expected 5–6 (best illustrating the pattern)."
        )

    sylls = wm.get('syllables', {})
    if not isinstance(sylls, dict):
        errors.append("wordMaps.syllables must be a dict"); return

    for word, breakdown in sylls.items():
        if '-' in breakdown and '|' not in breakdown:
            errors.append(
                f"wordMaps.syllables['{word}'] = {breakdown!r} uses hyphen as syllable break. "
                f"Must use pipe '|': e.g. 'poi|son|ous'. "
                f"Hyphens render as literal characters in the template."
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_lesson(path):
    lesson, load_err = load_lesson(path)
    if lesson is None:
        print(f"❌  {load_err}")
        return False

    errors   = []
    warnings = []

    check_required_top_keys(lesson, errors, warnings)
    check_words(lesson, errors, warnings)
    check_cloze_order(lesson, errors, warnings)
    check_defs_and_sentences(lesson, errors, warnings)
    check_starter(lesson, errors, warnings)
    check_etymology(lesson, errors, warnings)
    check_word_sort(lesson, errors, warnings)
    check_spell_data(lesson, errors, warnings)
    check_lp_fields(lesson, errors, warnings)
    check_lp_side_b_consistency(lesson, errors, warnings)
    check_word_maps(lesson, errors, warnings)

    code  = lesson.get('code', '?')
    stage = lesson.get('stage', '?')
    day   = lesson.get('lpDay', '?')

    print(f"\n{'='*65}")
    print(f"WFA Spelling Preflight — {stage} {code} ({day})")
    print(f"{'='*65}")

    if not errors and not warnings:
        print("✅  All checks passed. Safe to build.")
        return True

    if errors:
        print(f"\n❌  ERRORS ({len(errors)}) — fix before building:\n")
        for e in errors:
            print(f"  • {e}\n")

    if warnings:
        print(f"\n⚠️   WARNINGS ({len(warnings)}) — review before building:\n")
        for w in warnings:
            print(f"  • {w}\n")

    print()
    return len(errors) == 0


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lesson.json'
    ok   = validate_lesson(path)
    sys.exit(0 if ok else 1)
