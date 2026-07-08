#!/usr/bin/env python3
"""maths_preflight.py — Pre-build validator for WFA maths lessons.
Run before build_lesson_v3.py. Exit 0 = clear. Exit 1 = errors found.
Usage: python3 maths_preflight.py 20 21 22 23   OR   --all
"""
import json, os, re, sys

PLAN_PATH        = "/tmp/claude_work/transfer_files/maths_plan_v3.json"
LESSON_DATA_PATH = "/tmp/claude_work/lesson_data.py"
LABELS_DATA_PATH = "/tmp/claude_work/labels_data.json"

for _a, _fb in [("PLAN_PATH","/home/claude/maths_plan_v3.json"),
                ("LESSON_DATA_PATH","/home/claude/lesson_data.py"),
                ("LABELS_DATA_PATH","/home/claude/labels_data.json")]:
    if not os.path.exists(globals()[_a]) and os.path.exists(_fb): globals()[_a] = _fb

VISUAL_REF_RE = re.compile(
    r"\b(the|this)\s+(bar\s+|line\s+|double\s+bar\s+)?"
    r"(chart|graph|pictogram|table|diagram|image|picture)\b"
    r"|\blooks?\s+at\s+the\b", re.IGNORECASE
)
VISUAL_SLIDE_TYPES = {"stats_chart","symmetry_grid","clock","number_line","fraction_demo"}
TEXT_LIMITS = {"problem":200,"i_know":120,"finding":120,"attack":120,"wrong_working":100,"error":120}
REQUIRED_KEYS = {
    "spot_the_mistake":   ["error_instruction","error_note"],
    "word_problem":       ["problem","i_know","finding","attack"],
    "identify_calculate": ["problem","i_know","finding","attack"],
    "stm_word_problem":   ["problem","wrong_working","error"],
    "stats_chart":        ["chart_type","chart_data","questions","answers"],
}


def load_plan():
    if not os.path.exists(PLAN_PATH): return None
    with open(PLAN_PATH) as f: return json.load(f)

def load_lesson_data():
    if not os.path.exists(LESSON_DATA_PATH): return None, f"Not found: {LESSON_DATA_PATH}"
    import importlib.util
    spec = importlib.util.spec_from_file_location("lesson_data", LESSON_DATA_PATH)
    mod  = importlib.util.module_from_spec(spec)
    try: spec.loader.exec_module(mod); return mod, None
    except Exception as e: return None, str(e)

def load_labels():
    if not os.path.exists(LABELS_DATA_PATH): return None
    with open(LABELS_DATA_PATH) as f: return json.load(f)

def validate_lesson(n, plan, mod, labels):
    errors = []; warnings = []
    if n not in mod.LESSON_DATA:
        return [f"L{n}: no entry in LESSON_DATA"], []
    ld = mod.LESSON_DATA[n]
    visuals = ld.get("visuals", {})
    # STM gate
    for key in ["c1_ido2","c2_ido2"]:
        if key not in visuals:
            errors.append(f"L{n} STM GATE: {key!r} missing from VISUALS.")
    # Required fields
    for vk, v in visuals.items():
        stype = v.get("slide_type","grid")
        for field in REQUIRED_KEYS.get(stype, []):
            if not v.get(field,""):
                errors.append(f"L{n} VISUALS[{vk!r}]: {stype!r} requires {field!r}.")
    # Text limits
    for vk, v in visuals.items():
        for field, limit in TEXT_LIMITS.items():
            val = v.get(field,"")
            if isinstance(val, str) and len(val) > limit:
                warnings.append(f"L{n} VISUALS[{vk!r}].{field!r}: {len(val)} chars > {limit}.")
    # Visual reference check
    for vk, v in visuals.items():
        stype = v.get("slide_type","grid")
        if stype in VISUAL_SLIDE_TYPES: continue
        all_text = " ".join(str(v.get(f,"")) for f in
            ["problem","i_know","finding","attack","wrong_working","error","title","task"])
        m = VISUAL_REF_RE.search(all_text)
        if m and not v.get("chart_image"):
            errors.append(f"L{n} VISUALS[{vk!r}] ({stype}): text references {m.group()!r} but no chart_image.")
    # WM check
    wm = ld.get("wm",{})
    if not wm: errors.append(f"L{n}: wm_data is empty.")
    # Date check
    if labels and plan:
        plan_lesson = next((pl for pl in plan.get("lessons",[]) if pl.get("lesson")==n), None)
        if plan_lesson:
            pd = plan_lesson.get("date",""); ld2 = labels.get(str(n),{}).get("date","")
            if pd and ld2 and pd != ld2:
                errors.append(f"L{n}: date mismatch plan={pd!r} labels={ld2!r}.")
    return errors, warnings

def validate_lessons(nums):
    plan = load_plan(); mod, err = load_lesson_data(); labels = load_labels()
    if mod is None: print(f"Cannot load lesson_data.py: {err}"); return False
    all_e=[]; all_w=[]
    for n in nums:
        e, w = validate_lesson(n, plan, mod, labels)
        all_e += e; all_w += w
    print(f"\n{'='*65}\nWFA Maths Preflight — lessons: {nums}\n{'='*65}")
    if not all_e and not all_w: print("All checks passed."); return True
    if all_e:
        print(f"\nERRORS ({len(all_e)}):\n")
        for e in all_e: print(f"  • {e}")
    if all_w:
        print(f"\nWARNINGS ({len(all_w)}):\n")
        for w in all_w: print(f"  • {w}")
    return len(all_e) == 0

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args: print("Usage: maths_preflight.py <n>... | --all"); sys.exit(1)
    if "--all" in args:
        plan = load_plan()
        nums = [pl["lesson"] for pl in plan.get("lessons",[])] if plan else []
    else:
        try: nums = [int(a) for a in args]
        except ValueError: sys.exit(1)
    sys.exit(0 if validate_lessons(nums) else 1)
