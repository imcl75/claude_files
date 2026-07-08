#!/usr/bin/env python3
"""spelling_preflight.py — Pre-build validator for Spelling Shed lesson.json.
Run BEFORE node spelling_shed_slides_template.js.
Exit 0 = clear. Exit 1 = errors found.
"""
import json, os, sys

MAX_BASEFORM = 12; MAX_DEF = 70; REQ_WORDS = 10; REQ_VN = 6; REQ_DEFS = 5; REQ_SD = 5

def load(path):
    try:
        with open(path) as f: return json.load(f), None
    except Exception as e: return None, str(e)

def validate(path):
    lesson, err = load(path)
    if lesson is None: print(f"Cannot load: {err}"); return False
    errors=[]; warnings=[]
    words = lesson.get("words",[])
    cloze = lesson.get("clozeOrder",[])

    # Required keys
    for k in ["code","rule","stage","lpDay","lpSideBType","words","clozeOrder","defs",
              "starter","etymology","wordSort","spellData","lpVerbNoun","lpDefinitions",
              "lpDefMatchAnswers","thisWeeksWordsQ","wordSortQ"]:
        if k not in lesson: errors.append(f"Missing key: {k!r}")

    # Words count
    if len(words) != REQ_WORDS: errors.append(f"words must have {REQ_WORDS} entries, got {len(words)}")

    # Cloze collisions
    if len(cloze) == len(words):
        cols = [i for i in range(len(words)) if words[i]==cloze[i]]
        if cols: errors.append(f"clozeOrder collision at positions {cols} — word sits next to its own sentence")
        if sorted(words) != sorted(cloze): errors.append("clozeOrder must contain same words as words")

    # Starter
    s = lesson.get("starter",{})
    if isinstance(s.get("perPairNote"), str) and s["perPairNote"] != "":
        errors.append(f"starter.perPairNote={s['perPairNote']!r} must be empty string")
    for w in s.get("words",[]):
        if isinstance(w,str) and w != w.lower():
            errors.append(f"starter.words contains uppercase {w!r} — needs lowercase for inject_key_spelling.py")

    # Etymology
    base = lesson.get("etymology",{}).get("baseForm","")
    if len(base) > MAX_BASEFORM: errors.append(f"etymology.baseForm {base!r} is {len(base)} chars > {MAX_BASEFORM}")

    # wordSort.verbNoun must be list of dicts
    vn = lesson.get("wordSort",{}).get("verbNoun",[])
    if not isinstance(vn, list):
        errors.append(f"wordSort.verbNoun must be list of dicts, got {type(vn).__name__}")
    else:
        for i, item in enumerate(vn):
            if not isinstance(item, dict):
                errors.append(f"wordSort.verbNoun[{i}]={item!r} must be dict with word/eg keys")

    # Syllable breaks
    for word, bd in lesson.get("wordMaps",{}).get("syllables",{}).items():
        if "-" in bd and "|" not in bd:
            errors.append(f"wordMaps.syllables[{word!r}] uses hyphen — must use pipe |")

    # spellData
    sd = lesson.get("spellData",[])
    if len(sd) != REQ_SD: errors.append(f"spellData needs {REQ_SD} entries, got {len(sd)}")
    for i, item in enumerate(sd):
        if not isinstance(item, dict): continue
        if len(item.get("opts",[])) != 3: errors.append(f"spellData[{i}].opts must have 3 items")
        if item.get("correct") not in (0,1,2): errors.append(f"spellData[{i}].correct must be 0/1/2")

    # LP fields
    lpDay = lesson.get("lpDay","")
    if lpDay not in ("Mon","Tue","Wed"): errors.append(f"lpDay={lpDay!r} must be Mon/Tue/Wed")
    if lesson.get("lpSideBType","") not in ("vn_dm_sc","sc_dm"):
        errors.append("lpSideBType must be vn_dm_sc or sc_dm")
    lpvn = lesson.get("lpVerbNoun",[])
    if len(lpvn) != REQ_VN: errors.append(f"lpVerbNoun must have {REQ_VN} pairs, got {len(lpvn)}")
    for i,pair in enumerate(lpvn):
        if not isinstance(pair,list) or len(pair)!=2: errors.append(f"lpVerbNoun[{i}] must be [shown,answer]")
    defs = lesson.get("lpDefinitions",[])
    if len(defs) != REQ_DEFS: errors.append(f"lpDefinitions must have {REQ_DEFS} entries, got {len(defs)}")
    for i,d in enumerate(defs):
        if isinstance(d,str) and len(d)>MAX_DEF: warnings.append(f"lpDefinitions[{i}] {len(d)} chars > {MAX_DEF}")

    code=lesson.get("code","?"); stage=lesson.get("stage","?"); day=lesson.get("lpDay","?")
    print(f"\n{'='*60}\nSpelling Preflight — {stage} {code} ({day})\n{'='*60}")
    if not errors and not warnings: print("All checks passed. Safe to build."); return True
    if errors:
        print(f"\nERRORS ({len(errors)}):\n")
        for e in errors: print(f"  • {e}")
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):\n")
        for w in warnings: print(f"  • {w}")
    return len(errors)==0

if __name__=="__main__":
    path = sys.argv[1] if len(sys.argv)>1 else "/home/claude/lesson.json"
    sys.exit(0 if validate(path) else 1)
