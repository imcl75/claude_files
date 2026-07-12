#!/usr/bin/env python3
"""
build_science_lesson.py (v4) - MTP-JSON-driven Science enquiry lesson builder.

Replaces build_l1_final.py (hardcoded, L1-only, no verification) and
build_science_lesson.py v3 (data-driven but cloned slides by hardcoded index
into template files that have since been renamed/renumbered).

Usage: python3 build_science_lesson.py <mtp_json> <templates_dir> <out_pptx> <manifest_out>
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Also ensure /tmp/t6w7 is on path when this script lives elsewhere (e.g. outputs dir)
if os.path.isdir('/tmp/t6w7') and '/tmp/t6w7' not in sys.path:
    sys.path.insert(0, '/tmp/t6w7')
from lib_ooxml import (
    P, A, unzip, rezip, clear_slides, build_layout_map, src_dir,
    find_slide_by_anchor, clone, fresh, get_spTree, save,
    title_sp, body_sp, tbox, add_img, grid_geometry, animate,
    find_sp, get_sp_id, get_shape_id_by_name, set_text, delete_shapes_by_id, delete_shape_by_name,
    replace_image, find_pic_id_by_name, force_shrink_to_fit, strip_orphaned_media,
    clamp_callout_tail, strip_timing, extract_image_by_shape_name,
    xr, xw, xp, ex, SW, SH,
)
import science_registry as REG

# ── Sandbox compatibility patch ──────────────────────────────────────────────
# Python PID is always 3 in this sandbox. lib_ooxml.src_dir caches template
# extractions at /tmp/src_{pid}_{stem}, but those paths are owned by 'nobody'
# from previous sessions and can't be deleted or overwritten. Redirect to
# /sessions/ (ext4, 3.3 GB free, full permissions).
import lib_ooxml as _lo_mod
from pathlib import Path as _Path
_SESSION_TMP = '/sessions/admiring-sleepy-wozniak'
_lo_src_cache = {}

def _patched_src_dir(pptx, k=None):
    k = k or pptx
    if k not in _lo_src_cache:
        dst = f'{_SESSION_TMP}/src_{os.getpid()}_{_Path(pptx).stem}'
        _lo_mod.unzip(pptx, dst)
        _lo_src_cache[k] = dst
    return _lo_src_cache[k]

_lo_mod.src_dir = _patched_src_dir
src_dir = _patched_src_dir  # rebind the already-imported name

# Also patch rezip: FUSE mount blocks os.remove() on existing files.
# zipfile.ZipFile with mode "w" truncates-and-overwrites, so the remove is redundant.
_orig_rezip = _lo_mod.rezip
def _patched_rezip(src, dst):
    import zipfile, os, shutil
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, src))
    shutil.rmtree(src, ignore_errors=True)
_lo_mod.rezip = _patched_rezip
rezip = _patched_rezip  # rebind the already-imported name
# ─────────────────────────────────────────────────────────────────────────────



def build_being_a_scientist(work, templates, spec):
    # Round 5 (11 Jul 2026): now sourced from KQ_and_BeingAScientist.pptx, a
    # SmartArt-free file Innes prepared himself (converted the fragile Areas
    # of Study / Skills wheel SmartArt diagrams to flat images). That source
    # slide already carries its own title ("Being a Scientist", TitleBeing
    # shape) and its own scientist icon (ScientistIcon shape) baked in, so
    # unlike the old Being_a_Scientist_slide_deck.pptx slide 3 this needs no
    # synthesised title textbox and no icon copied in from elsewhere - a
    # plain clone is enough, the same pattern as build_discipline(). See
    # science_registry.py's BEING_A_SCIENTIST_* comments for the full
    # history of why this changed (it was the cause of a real PowerPoint
    # crash on the old source).
    pptx = templates[REG.COMPONENTS['being_a_scientist']['template']]
    sn = find_slide_by_anchor(pptx, REG.BEING_A_SCIENTIST_ANCHOR, REG.BEING_A_SCIENTIST_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    return sp


def build_kq_challenge(work, templates, spec):
    pptx = templates[REG.COMPONENTS['kq_challenge']['template']]
    sn = find_slide_by_anchor(pptx, REG.KQ_CHALLENGE_ANCHOR, REG.KQ_CHALLENGE_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    delete_shapes_by_id(sp, REG.KQ_CHALLENGE_STRIP_IDS)
    delete_shape_by_name(sp, REG.KQ_CHALLENGE_STRIP_NAME)
    has_challenge = bool(spec.get('challenge'))
    if not has_challenge:
        # No investigation/written outcome this enquiry (confirmed against
        # the MTP). Delete the whole challenge box rather than set_text() to
        # an empty string - found by rendering that set_text() with an empty
        # challenge still left "Our Challenge is:" showing on its own with
        # nothing after it, which looks unfinished rather than genuinely
        # absent. Removing the shape is what "not included in the cloud"
        # (Innes's own words) actually requires.
        delete_shape_by_name(sp, REG.KQ_CHALLENGE_TASK_SHAPE_NAME)
    tree = xr(sp)
    kq_shape = find_sp(tree, REG.KQ_CHALLENGE_KQ_SHAPE_NAME)
    if kq_shape is None:
        raise RuntimeError(f"kq_challenge: expected shape '{REG.KQ_CHALLENGE_KQ_SHAPE_NAME}' not found - template drift")
    set_text(kq_shape, spec['key_question'])
    if has_challenge:
        task_shape = find_sp(tree, REG.KQ_CHALLENGE_TASK_SHAPE_NAME)
        if task_shape is None:
            raise RuntimeError(f"kq_challenge: expected shape '{REG.KQ_CHALLENGE_TASK_SHAPE_NAME}' not found - template drift")
        set_text(task_shape, f"Our Challenge is: \n{spec['challenge']}")
    xw(tree, sp)
    return sp


def build_discipline(work, templates, spec):
    strand = spec['strand']
    if strand not in REG.DISCIPLINE_ANCHORS:
        raise ValueError(f"Unknown science strand '{strand}'. Must be one of {list(REG.DISCIPLINE_ANCHORS)}")
    pptx = templates[REG.COMPONENTS['discipline']['template']]
    sn = find_slide_by_anchor(pptx, REG.DISCIPLINE_ANCHORS[strand], REG.DISCIPLINE_HINTS[strand])
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    strip_timing(sp)
    # Round 8 (11 Jul 2026): the raw source's own animation genuinely has a
    # clickEffect/spTgt mismatch (11:37 on Chemistry) so strip_timing() above
    # is still correct as a first step - but Innes's ground-truth file shows
    # he rebuilt a clean, working animation on this slide rather than leaving
    # it silent. Replace the stripped timing with the confirmed shape list
    # for this strand, where one exists.
    steps = REG.DISCIPLINE_ANIMATION_SHAPE_NAMES.get(strand)
    if steps:
        tree = xr(sp)
        id_steps = []
        for step_names in steps:
            ids = []
            for name in step_names:
                sid = get_shape_id_by_name(tree, name)
                if sid is None:
                    raise RuntimeError(f"discipline ({strand}): expected animated shape '{name}' not found - template drift")
                ids.append(sid)
            id_steps.append(ids)
        animate(sp, id_steps)
    return sp


def build_lo(work, templates, spec):
    pptx = templates[REG.COMPONENTS['lo']['template']]
    sn = find_slide_by_anchor(pptx, REG.COMPONENTS['lo']['anchor'], REG.COMPONENTS['lo']['hint'])
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    delete_shapes_by_id(sp, REG.LO_STALE_GROUP_IDS)
    tree = xr(sp)
    for name, val in [('Title 27', spec['key_question']), ('TextBox 38', spec['lo']),
                       ('TextBox 39', spec['tib']), ('TextBox 40', spec['isb'])]:
        s = find_sp(tree, name)
        if s is not None:
            set_text(s, val)
        else:
            raise RuntimeError(f"LO slide: expected shape '{name}' not found after stripping stale group - "
                                f"template may have drifted again, check REG.LO_STALE_GROUP_IDS")
    xw(tree, sp)
    tree = xr(sp)
    ids = [get_sp_id(tree, n) for n in ('TextBox 38', 'TextBox 39', 'TextBox 40')]
    if not all(ids):
        raise RuntimeError("LO slide: could not resolve shape ids for animation after text edit")
    animate(sp, [[i] for i in ids])
    return sp


def build_concept_cartoon(work, templates, spec):
    pptx = templates[REG.COMPONENTS['concept_cartoon']['template']]
    sn = find_slide_by_anchor(pptx, REG.CONCEPT_CARTOON_ANCHOR, REG.CONCEPT_CARTOON_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    tree = xr(sp)
    title_shape = find_sp(tree, REG.CONCEPT_CARTOON_TITLE_SHAPE_NAME)
    if title_shape is not None and spec.get('title'):
        set_text(title_shape, spec['title'])
    learners = spec['learners']
    if len(learners) != 3:
        raise ValueError("concept_cartoon requires exactly 3 learners (A/B/C)")
    for bubble_name, learner in zip(REG.CONCEPT_CARTOON_BUBBLE_NAMES, learners):
        s = find_sp(tree, bubble_name)
        if s is None:
            raise RuntimeError(f"concept_cartoon: expected speech bubble '{bubble_name}' not found - template drift")
        set_text(s, learner['statement'])
        # The bubble box size is fixed (sized for the template's own text) -
        # a longer lesson-specific statement must shrink to fit, not overflow
        # past the bubble edge into whatever sits below it.
        force_shrink_to_fit(s)
    xw(tree, sp)
    for bubble_name in REG.CONCEPT_CARTOON_BUBBLE_NAMES:
        clamp_callout_tail(sp, bubble_name)
    # Replace the central scene image - this is the one part of the template
    # that is always topic-specific (it ships as a cat/light illustration).
    tree = xr(sp)
    pic_id = find_pic_id_by_name(tree, REG.CONCEPT_CARTOON_CENTRAL_IMAGE_SHAPE_NAME)
    if pic_id is None:
        raise RuntimeError("concept_cartoon: central image shape not found - template drift")
    if not spec.get('image_path') or not os.path.exists(spec['image_path']):
        raise RuntimeError(f"concept_cartoon: image_path '{spec.get('image_path')}' missing - "
                            f"refusing to deliver a concept cartoon with the template's cat/light image still showing")
    replace_image(sp, rp, work, pic_id, spec['image_path'])
    # Round 8 (11 Jul 2026): click-reveal each learner's avatar, speech
    # bubble and "Learner X" label together, one learner at a time (A, then
    # B, then C) - found missing entirely by diffing Innes's ground-truth
    # repaired file. See REG.CONCEPT_CARTOON_ANIMATION_STEPS.
    tree = xr(sp)
    id_steps = []
    for step_names in REG.CONCEPT_CARTOON_ANIMATION_STEPS:
        ids = []
        for name in step_names:
            sid = get_shape_id_by_name(tree, name)
            if sid is None:
                raise RuntimeError(f"concept_cartoon: expected animated shape '{name}' not found - template drift")
            ids.append(sid)
        id_steps.append(ids)
    animate(sp, id_steps)
    return sp


def build_learning_review(work, templates, spec):
    pptx = templates[REG.COMPONENTS['learning_review']['template']]
    sn = find_slide_by_anchor(pptx, REG.LEARNING_REVIEW_ANCHOR, REG.LEARNING_REVIEW_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    tree = xr(sp)
    starters = spec['starters']
    bmap = {'Bubble1': 0, 'Bubble2': 1, 'Bubble3': 2}
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            nm = el.get('name', '')
            if nm in bmap:
                set_text(s, starters[bmap[nm]]); break
    xw(tree, sp)
    return sp


def build_wedo_hook(work, spec):
    # Round 8 (11 Jul 2026): Round 7 reverted this to body_sp() (the real
    # Content Placeholder) based on a guess about what "use the templates"
    # meant. Wrong guess, confirmed by diffing Innes's own ground-truth
    # repaired file directly: its slide 5 keeps exactly this function's
    # Round-6 per-bullet TextBox structure (same shape names, same
    # positions/sizes/font size down to the EMU) and only ever had its
    # animation timing fixed. Reverted back to per-bullet tbox() - this is
    # what "use the templates" was NOT about, at least not on this slide
    # type. See SKILL.md Round 8 for the full correction record.
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1750000 + i * 1350000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 700000, by, SW - 1400000, 1250000, sz=2200, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp


def build_wedo_grid(work, spec):
    # Round 8 (11 Jul 2026): switched from 'We do - Blank' to 'We do' - a
    # much bigger finding than it looks. Checking which layout each of
    # Innes's ground-truth slides actually points at (not just its shapes)
    # showed every content slide type uses the NON-blank layout variant,
    # including the grid/image ones this skill had assumed needed '-Blank'.
    # The non-blank layout's unused Content/Media placeholders stay empty
    # (they show as "Click to add text" prompts only in PowerPoint's Normal
    # edit view, never in Slide Show or print/PDF output) - cosmetic in the
    # editor, not a rendering bug, but matching Innes's actual file exactly
    # rather than my own assumption about which layout "should" be used.
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    items = spec['items']
    n = len(items)
    cols = 4 if n > 4 else n
    rows = -(-n // cols)  # ceil
    cells = grid_geometry(cols, rows)
    sid = 10
    for (cx, cy, cw, ch, iw, ih, lh), item in zip(cells, items):
        img_path = item['image_path']
        if not os.path.exists(img_path):
            raise RuntimeError(f"wedo_grid: image_path '{img_path}' does not exist - "
                                f"refusing to deliver a slide with a missing image")
        add_img(sp, rp, work, img_path, cx + 40000, cy + 20000, iw, ih, sid); sid += 1
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, item['label'], cx, cy + ih + 40000, cw, lh,
                         sz=1600, bold=True, color='1A3A5C', align='ctr')); save(t2, sp); sid += 1
    return sp


def build_ido_diagram(work, spec):
    # Round 8: switched from 'I Do - Blank' to 'I do' - see build_wedo_grid()
    # for why (confirmed against Innes's ground-truth slide 7's own layout
    # relationship, not assumed).
    sp, rp = fresh(work, 'I do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT, bold=True))
    save(t, sp)
    if spec.get('image_path'):
        if not os.path.exists(spec['image_path']):
            raise RuntimeError(f"ido_diagram: image_path '{spec['image_path']}' does not exist")
        add_img(sp, rp, work, spec['image_path'], 5400000, 1600000, 6500000, 4800000, 3)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1550000 + i * 1540000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 180000, by, 5000000, 1500000, sz=1900, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp


def build_youdo_provocation(work, spec):
    # Round 8: switched from 'You do Ind - Blank' to 'You do Ind' - see
    # build_wedo_grid() for why (confirmed against Innes's ground-truth
    # slide 8's own layout relationship).
    sp, rp = fresh(work, 'You do Ind')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    if not os.path.exists(spec['image_path']):
        raise RuntimeError(f"youdo_provocation: image_path '{spec['image_path']}' does not exist")
    add_img(sp, rp, work, spec['image_path'], 838200, 1700000, 10515600, 4900000, 3)
    return sp


def build_youdo_task(work, spec):
    # Round 8: same reversion as build_wedo_hook() above - confirmed against
    # Innes's ground-truth file that slide 9 also keeps the per-bullet
    # TextBox structure, positions matching exactly.
    sp, rp = fresh(work, 'You do Ind')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    sid = 10; groups = []
    for i, bullet in enumerate(spec['bullets']):
        by = 1750000 + i * 1150000
        t2, st2 = get_spTree(sp)
        st2.append(tbox(sid, bullet, 700000, by, SW - 1400000, 1050000, sz=2000, color='1A3A5C', align='l'))
        save(t2, sp); groups.append([sid]); sid += 1
    animate(sp, groups)
    return sp


DISPATCH = {
    'being_a_scientist':  lambda work, templates, layouts, spec: build_being_a_scientist(work, templates, spec),
    'kq_challenge':       lambda work, templates, layouts, spec: build_kq_challenge(work, templates, spec),
    'discipline':         lambda work, templates, layouts, spec: build_discipline(work, templates, spec),
    'lo':                 lambda work, templates, layouts, spec: build_lo(work, templates, spec),
    'wedo_hook':          lambda work, templates, layouts, spec: build_wedo_hook(work, spec),
    'wedo_grid':          lambda work, templates, layouts, spec: build_wedo_grid(work, spec),
    'ido_diagram':        lambda work, templates, layouts, spec: build_ido_diagram(work, spec),
    'youdo_provocation':  lambda work, templates, layouts, spec: build_youdo_provocation(work, spec),
    'youdo_task':         lambda work, templates, layouts, spec: build_youdo_task(work, spec),
    'concept_cartoon':    lambda work, templates, layouts, spec: build_concept_cartoon(work, templates, spec),
    'learning_review':    lambda work, templates, layouts, spec: build_learning_review(work, templates, spec),
}


def build_lesson(mtp_path, templates_dir, out_path, manifest_path):
    with open(mtp_path) as f:
        mtp = json.load(f)
    lesson = mtp['lesson']
    slides_spec = lesson['slides']

    # 1. Validate every requested type is known and every required field present
    for entry in slides_spec:
        t = entry['type']
        if t not in REG.COMPONENTS:
            raise ValueError(f"Unknown slide type '{t}' in lesson plan. Known types: {list(REG.COMPONENTS)}")
        for field in REG.COMPONENTS[t]['fields']:
            if field not in entry and field not in lesson:
                raise ValueError(f"Slide type '{t}' is missing required field '{field}'")

    # 2. Validate required components are present at least once
    present_types = {e['type'] for e in slides_spec}
    missing = REG.REQUIRED_TYPES - present_types
    if missing:
        raise ValueError(f"Lesson plan is missing required slide types: {sorted(missing)}")

    templates = {k: os.path.join(templates_dir, v) for k, v in REG.TEMPLATE_FILES.items()}
    for k, p in templates.items():
        if not os.path.exists(p):
            raise FileNotFoundError(f"Template '{k}' not found at {p}")

    # Was a fixed '/tmp/build_work' - collided with stale leftover directories
    # from unrelated processes in some sandboxes (owned by a different user,
    # un-removable). PID-scoped so each build gets a fresh, unique path.
    
    work = f'/sessions/admiring-sleepy-wozniak/bsl_{os.getpid()}_work'
    unzip(templates['science_example'], work)
    clear_slides(work)
    build_layout_map(work)
    import lib_ooxml as _lib
    for k, v in REG.CONTENT_LAYOUTS.items():
        if v not in _lib._work_layouts:
            raise RuntimeError(f"Layout '{v}' not found in work presentation - layout names in "
                                f"science-example.pptx may have changed")

    for k in templates.values():
        src_dir(k)

    manifest = []
    for i, entry in enumerate(slides_spec, 1):
        t = entry['type']
        # merge lesson-level fields (key_question/lo/tib/isb) with per-slide spec
        merged = {**{k: lesson[k] for k in ('key_question', 'lo', 'tib', 'isb') if k in lesson}, **entry}
        print(f"  [{i}] {t}")
        sp = DISPATCH[t](work, templates, REG.CONTENT_LAYOUTS, merged)
        manifest.append({'output_index': i, 'type': t, 'slide_xml': os.path.basename(sp)})

    r = subprocess.run(['python3', '/mnt/skills/public/pptx/scripts/clean.py', work],
                        capture_output=True, text=True)
    if r.returncode != 0 and r.stderr.strip():
        print(f"  clean.py stderr (non-fatal, continuing): {r.stderr.strip()[:300]}")

    removed = strip_orphaned_media(work)
    if removed:
        print(f"  stripped {len(removed)} orphaned media file(s) no relationship referenced: {removed}")

    rezip(work, out_path)
    with open(manifest_path, 'w') as f:
        json.dump({'mtp': mtp_path, 'slides': manifest}, f, indent=2)
    print(f"\n-> {out_path} ({os.path.getsize(out_path):,} bytes), manifest -> {manifest_path}")

    # ── Fix OOXML issues (SharePoint metadata strip, customXml, etc.) ────
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    fix_script = next(
        (p for p in [
            os.path.join(_this_dir, 'fix_pptx_ooxml.py'),
            '/tmp/t6w7/fix_pptx_ooxml.py',
        ] if os.path.exists(p)), None
    )
    if fix_script:
        r_fix = subprocess.run(['python3', fix_script, out_path], capture_output=True, text=True)
        if r_fix.returncode != 0:
            print(f'  fix_pptx_ooxml warning: {r_fix.stderr.strip()[:200]}')
        else:
            print('  fix_pptx_ooxml: OK')
    else:
        print('  fix_pptx_ooxml.py not found — skipping fix (file may show repair dialog)')

    # ── Verify (hard gate — must PASS before LP is built) ────────────────
    verify_script = next(
        (p for p in [
            os.path.join(_this_dir, 'verify_lesson.py'),
            '/tmp/t6w7/verify_lesson.py',
        ] if os.path.exists(p)), None
    )
    if verify_script:
        r_ver = subprocess.run(
            ['python3', verify_script, out_path, mtp_path, manifest_path],
            capture_output=True, text=True
        )
        print(r_ver.stdout.strip())
        if r_ver.returncode != 0:
            print('VERIFY FAILED — LP not built. Fix issues above and re-run.')
            sys.exit(1)
    else:
        print('  verify_lesson.py not found — skipping verification')

    # ── Build LP (only if lesson JSON contains an lp spec) ───────────────
    lp_spec = mtp.get('lesson', {}).get('lp')
    if lp_spec is None:
        print("  No 'lp' key in lesson JSON — skipping LP build")
    else:
        lp_path = os.path.splitext(out_path)[0] + ' LP.pptx'
        # Find build_lp.py: same dir as this script first, then outputs dir, then /tmp/t6w7
        build_lp_script = next(
            (p for p in [
                os.path.join(_this_dir, 'build_lp.py'),
                '/sessions/admiring-sleepy-wozniak/mnt/outputs/build_lp.py',
                '/tmp/t6w7/build_lp.py',
            ] if os.path.exists(p)), None
        )
        if build_lp_script is None:
            print('  build_lp.py not found — skipping LP build')
        else:
            lp_mod_dir = os.path.dirname(build_lp_script)
            if lp_mod_dir not in sys.path:
                sys.path.insert(0, lp_mod_dir)
            # Find resource_base: directory containing ll_assets/
            _rb_candidates = [
                os.path.dirname(os.path.abspath(mtp_path)),
                _this_dir,
                '/tmp/t6w7',
            ]
            resource_base = next(
                (c for c in _rb_candidates if os.path.isdir(os.path.join(c, 'll_assets'))),
                '/tmp/t6w7'
            )
            from build_lp import build_lp
            build_lp(mtp_path, lp_path, resource_base=resource_base)

    return out_path, manifest_path


if __name__ == '__main__':
    mtp_path, templates_dir, out_path, manifest_path = sys.argv[1:5]
    build_lesson(mtp_path, templates_dir, out_path, manifest_path)
