#!/usr/bin/env python3
"""
maths_preflight.py — Pre-build validator for WFA maths lesson resources.

Run this BEFORE build_lesson_v3.py. Catches content problems that would produce
wrong, blank or misleading slides, at the point where fixing them is cheap.

Usage:
    python3 maths_preflight.py <lesson_number>        # validate one lesson
    python3 maths_preflight.py <n1> <n2> ...          # validate multiple lessons
    python3 maths_preflight.py --all                  # validate all lessons in plan

Exit code 0 = all clear. Exit code 1 = errors found (block the build).
"""

import json, os, re, sys

# ---------------------------------------------------------------------------
# Paths (match the maths pipeline runtime paths)
# ---------------------------------------------------------------------------
PLAN_PATH        = '/tmp/claude_work/transfer_files/maths_plan_v3.json'
LESSON_DATA_PATH = '/tmp/claude_work/lesson_data.py'
LABELS_DATA_PATH = '/tmp/claude_work/labels_data.json'

# Fallback to /home/claude/ if tmp paths don't exist (used when checking outside a build)
for _attr, _fallback in [
    ('PLAN_PATH',        '/home/claude/maths_plan_v3.json'),
    ('LESSON_DATA_PATH', '/home/claude/lesson_data.py'),
    ('LABELS_DATA_PATH', '/home/claude/labels_data.json'),
]:
    val = globals()[_attr]
    if not os.path.exists(val) and os.path.exists(_fallback):
        globals()[_attr] = _fallback

# ---------------------------------------------------------------------------
# Keywords that indicate a visual should be present on the same slide
# ---------------------------------------------------------------------------
VISUAL_REF_RE = re.compile(
    r'\b(the|this)\s+(bar\s+|line\s+|double\s+bar\s+)?'
    r'(chart|graph|pictogram|table|diagram|image|picture)\b'
    r'|\blooks?\s+at\s+the\b'
    r'|\busing\s+the\s+(chart|graph|data|table|diagram)\b'
    r'|\bfrom\s+the\s+(chart|graph|table|diagram)\b'
    r'|\bread\s+the\s+(chart|graph|table|diagram)\b',
    re.IGNORECASE
)

# Slide types that ARE visual (chart/image rendered on the slide)
VISUAL_SLIDE_TYPES = {'stats_chart', 'symmetry_grid', 'clock', 'number_line', 'fraction_demo'}

# Required keys for each slide type in VISUALS
REQUIRED_KEYS = {
    'spot_the_mistake':   ['error_instruction', 'error_note'],
    'word_problem':       ['problem', 'i_know', 'finding', 'attack'],
    'identify_calculate': ['problem', 'i_know', 'finding', 'attack'],
    'bar_model':          ['problem'],
    'stm_word_problem':   ['problem', 'wrong_working', 'error'],
    'stats_chart':        ['chart_type', 'chart_data', 'questions', 'answers'],
    'column_calc':        ['operation'],
}

# Fields with known max character limits
TEXT_LIMITS = {
    # lesson_data VISUALS fields
    'problem':      200,
    'i_know':       120,
    'finding':      120,
    'attack':       120,
    'wrong_working': 100,
    'error':        120,
}


# ---------------------------------------------------------------------------
# Load plan JSON
# ---------------------------------------------------------------------------
def load_plan():
    if not os.path.exists(PLAN_PATH):
        return None
    with open(PLAN_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Load lesson_data.py as a module
# ---------------------------------------------------------------------------
def load_lesson_data():
    if not os.path.exists(LESSON_DATA_PATH):
        return None, f"lesson_data.py not found at {LESSON_DATA_PATH}"
    import importlib.util
    spec = importlib.util.spec_from_file_location('lesson_data', LESSON_DATA_PATH)
    mod  = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        return None, f"lesson_data.py failed to load: {e}"
    return mod, None


# ---------------------------------------------------------------------------
# Load labels_data.json
# ---------------------------------------------------------------------------
def load_labels():
    if not os.path.exists(LABELS_DATA_PATH):
        return None
    with open(LABELS_DATA_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_stm_gate(lesson_num, visuals, errors, warnings):
    """Both c1_ido2 and c2_ido2 must be present — the STM gate."""
    for key in ['c1_ido2', 'c2_ido2']:
        if key not in visuals:
            errors.append(
                f"L{lesson_num} STM GATE: '{key}' missing from VISUALS. "
                f"Author a Spot the Mistake before building."
            )


def check_required_fields(lesson_num, visuals, errors, warnings):
    """Each visual spec must have its required fields for that slide type."""
    for visual_key, v in visuals.items():
        stype = v.get('slide_type', 'grid')
        req   = REQUIRED_KEYS.get(stype, [])
        for field in req:
            if not v.get(field, ''):
                errors.append(
                    f"L{lesson_num} VISUALS['{visual_key}']: "
                    f"slide_type '{stype}' requires '{field}' but it is missing or empty."
                )


def check_text_limits(lesson_num, visuals, errors, warnings):
    """Flag text fields that exceed their known safe limits."""
    for visual_key, v in visuals.items():
        for field, limit in TEXT_LIMITS.items():
            val = v.get(field, '')
            if isinstance(val, str) and len(val) > limit:
                warnings.append(
                    f"L{lesson_num} VISUALS['{visual_key}'].'{field}': "
                    f"{len(val)} chars (limit {limit}). "
                    f"May overflow its box. Consider splitting: '{val[:60]}...'"
                )


def check_visual_references(lesson_num, visuals, errors, warnings):
    """
    If an stm_word_problem slide references 'the chart/graph/table', it must
    provide a 'chart_image' key so the builder can embed the chart on the right panel.

    This is the fix for the 'looks at the Bristol/Manaus chart' bug (T6W6 L22)
    where the STM problem referenced a chart that was never shown on the slide.
    """
    for visual_key, v in visuals.items():
        stype = v.get('slide_type', 'grid')

        # Only check slide types that don't automatically render a chart
        if stype in VISUAL_SLIDE_TYPES:
            continue

        # Collect all text fields that end up in the slide
        all_text = ' '.join(str(v.get(f, '')) for f in [
            'problem', 'i_know', 'finding', 'attack',
            'wrong_working', 'error', 'title', 'task',
            'error_instruction', 'error_note', 'notes',
        ])

        match = VISUAL_REF_RE.search(all_text)
        if not match:
            continue

        # Text references a visual — does the spec provide a chart_image?
        if not v.get('chart_image'):
            errors.append(
                f"L{lesson_num} VISUALS['{visual_key}'] ({stype}): "
                f"text references '{match.group().strip()}' but no 'chart_image' is provided. "
                f"Add 'chart_image': '/path/to/chart.png' so the builder can embed it. "
                f"Context: '...{all_text[max(0,match.start()-15):match.end()+40].strip()}...'"
            )


def check_trios_chart_refs(lesson_num, plan_lesson, errors, warnings):
    """
    If a trios task text references 'the chart/graph', the plan JSON must have
    trios_charts set so build_trios_slide embeds the chart image.
    """
    for cycle_key in ['c1', 'c2']:
        trios = plan_lesson.get(cycle_key, {}).get('trios', {})
        if not trios:
            continue
        task_text = trios.get('task', '')
        match = VISUAL_REF_RE.search(task_text)
        if match and not plan_lesson.get(cycle_key, {}).get('trios_charts'):
            warnings.append(
                f"L{lesson_num} {cycle_key} trios task references '{match.group().strip()}' "
                f"but trios_charts is not set in the plan JSON. "
                f"The chart will not appear on the Trios slide. "
                f"Add trios_charts: ['c{cycle_key[-1]}_ido1'] or similar."
            )


def check_wm_fields(lesson_num, wm_data, errors, warnings):
    """Working memory data must have all required fields."""
    if not wm_data:
        errors.append(f"L{lesson_num}: wm_data is empty — no working memory slides will be built.")
        return
    required_wm = ['category', 'questions']
    for field in required_wm:
        if field not in wm_data:
            errors.append(f"L{lesson_num} WM: missing '{field}'")
    if 'questions' in wm_data and len(wm_data['questions']) < 4:
        warnings.append(
            f"L{lesson_num} WM: only {len(wm_data['questions'])} questions "
            f"(expected 4). Slides will be built but some Q slots will be empty."
        )


def check_date_consistency(lesson_num, plan_lesson, labels_data, errors, warnings):
    """
    Dates in labels_data.json must match what the plan JSON says for each lesson.
    """
    if not labels_data:
        return
    plan_day = plan_lesson.get('day', '')
    plan_date = plan_lesson.get('date', '')
    labels_entry = labels_data.get(str(lesson_num), {})
    if not labels_entry:
        warnings.append(f"L{lesson_num}: no entry in labels_data.json for lesson {lesson_num}.")
        return
    label_date = labels_entry.get('date', '')
    if plan_date and label_date and plan_date != label_date:
        errors.append(
            f"L{lesson_num}: date mismatch. "
            f"Plan JSON says '{plan_date}', labels_data.json says '{label_date}'. "
            f"Fix both before building — wrong dates print on pupil labels."
        )


def check_vocab(lesson_num, vocab, errors, warnings):
    """Vocab list sanity."""
    if not vocab:
        warnings.append(f"L{lesson_num}: no vocab entries (VOCAB is empty). Vocab slide will be blank.")
        return
    if len(vocab) > 6:
        warnings.append(
            f"L{lesson_num}: {len(vocab)} vocab entries. "
            f"More than 6 may overflow the vocab slide box."
        )


# ---------------------------------------------------------------------------
# Main validate function
# ---------------------------------------------------------------------------

def validate_lesson(lesson_num, plan, lesson_mod, labels_data):
    """
    Validate one lesson number.
    Returns (errors, warnings) — both lists of strings.
    """
    errors   = []
    warnings = []

    # --- Lesson data exists ---
    if lesson_num not in lesson_mod.LESSON_DATA:
        errors.append(f"L{lesson_num}: no entry in LESSON_DATA dict.")
        return errors, warnings

    ld = lesson_mod.LESSON_DATA[lesson_num]

    visuals  = ld.get('visuals', {})
    wm_data  = ld.get('wm', {})
    vocab    = ld.get('vocab', [])

    # --- Plan entry ---
    plan_lesson = None
    if plan:
        for pl in plan.get('lessons', []):
            if pl.get('lesson') == lesson_num:
                plan_lesson = pl
                break
    if not plan_lesson:
        warnings.append(f"L{lesson_num}: no entry found in maths_plan_v3.json.")

    # Run all checks
    check_stm_gate(lesson_num, visuals, errors, warnings)
    check_required_fields(lesson_num, visuals, errors, warnings)
    check_text_limits(lesson_num, visuals, errors, warnings)
    check_visual_references(lesson_num, visuals, errors, warnings)
    check_wm_fields(lesson_num, wm_data, errors, warnings)
    check_vocab(lesson_num, vocab, errors, warnings)

    if plan_lesson:
        check_trios_chart_refs(lesson_num, plan_lesson, errors, warnings)
        check_date_consistency(lesson_num, plan_lesson, labels_data, errors, warnings)

    return errors, warnings


def validate_lessons(lesson_nums):
    """Validate a list of lesson numbers. Prints a report. Returns True if all pass."""
    plan         = load_plan()
    mod, err_msg = load_lesson_data()
    labels_data  = load_labels()

    if mod is None:
        print(f"❌  Cannot load lesson_data.py: {err_msg}")
        return False

    all_errors   = []
    all_warnings = []

    for n in lesson_nums:
        errs, warns = validate_lesson(n, plan, mod, labels_data)
        all_errors   += errs
        all_warnings += warns

    print(f"\n{'='*65}")
    print(f"WFA Maths Preflight — lessons: {lesson_nums}")
    print(f"{'='*65}")

    if not all_errors and not all_warnings:
        print("✅  All checks passed. Safe to build.")
        return True

    if all_errors:
        print(f"\n❌  ERRORS ({len(all_errors)}) — fix before building:\n")
        for e in all_errors:
            print(f"  • {e}")

    if all_warnings:
        print(f"\n⚠️   WARNINGS ({len(all_warnings)}) — review but not blocking:\n")
        for w in all_warnings:
            print(f"  • {w}")

    print()
    return len(all_errors) == 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    args = sys.argv[1:]

    if not args:
        print("Usage: python3 maths_preflight.py <lesson_num> [<lesson_num> ...]")
        print("       python3 maths_preflight.py --all")
        sys.exit(1)

    if '--all' in args:
        plan = load_plan()
        if plan:
            nums = [pl['lesson'] for pl in plan.get('lessons', [])]
        else:
            print("No plan loaded — cannot determine lesson numbers.")
            sys.exit(1)
    else:
        try:
            nums = [int(a) for a in args]
        except ValueError:
            print(f"Invalid lesson number(s): {args}")
            sys.exit(1)

    ok = validate_lessons(nums)
    sys.exit(0 if ok else 1)
