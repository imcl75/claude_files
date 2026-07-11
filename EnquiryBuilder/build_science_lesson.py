#!/usr/bin/env python3
"""
build_science_lesson.py (v4) - MTP-JSON-driven Science enquiry lesson builder.

Replaces build_l1_final.py (hardcoded, L1-only, no verification) and
build_science_lesson.py v3 (data-driven but cloned slides by hardcoded index
into template files that have since been renamed/renumbered).

Usage: python3 build_science_lesson.py <mtp_json> <templates_dir> <out_pptx> <manifest_out>
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from lib_ooxml import (
    P, A, unzip, rezip, clear_slides, build_layout_map, src_dir,
    find_slide_by_anchor, clone, fresh, get_spTree, save,
    title_sp, body_sp, tbox, add_img, grid_geometry, animate,
    find_sp, get_sp_id, set_text, delete_shapes_by_id, delete_shape_by_name,
    replace_image, find_pic_id_by_name, force_shrink_to_fit, strip_orphaned_media,
    clamp_callout_tail, strip_timing, extract_image_by_shape_name,
    xr, xw, xp, ex, SW, SH,
)
import science_registry as REG


def build_being_a_scientist(work, templates, spec):
    pptx = templates[REG.COMPONENTS['being_a_scientist']['template']]
    sn = find_slide_by_anchor(pptx, REG.BEING_A_SCIENTIST_ANCHOR, REG.BEING_A_SCIENTIST_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    # This source slide (the Areas of Study / Skills wheel diagrams) carries
    # no title of its own and no icon - both need adding, per SKILL.md's
    # long-standing decision that was never actually implemented until now.
    # A placeholder title_sp() inherits its position from whatever layout
    # this slide's own source uses, which is NOT necessarily clear of the
    # diagram content - confirmed by render: it landed directly on top of
    # the "Areas of Study" label. Use an explicit fixed position at the very
    # top of the slide instead, well above where either diagram starts
    # (diagrams begin around y=2.3in / 2119651 EMU on this source slide).
    t, st = get_spTree(sp)
    st.append(tbox(50, 'Being a Scientist', 400000, 100000, SW - 800000, 700000,
                    sz=3200, bold=True, color='1A3A5C', align='l', name='Title 50'))
    save(t, sp)
    icon_tmp = '/tmp/scientist_icon.png'
    extract_image_by_shape_name(pptx, REG.BEING_A_SCIENTIST_ICON_SOURCE_SLIDE,
                                 REG.BEING_A_SCIENTIST_ICON_SHAPE_NAME, icon_tmp)
    add_img(sp, rp, work, icon_tmp, 150000, SH - 1300000, 1100000, 1100000, 51)
    return sp


def build_kq_challenge(work, templates, spec):
    pptx = templates[REG.COMPONENTS['kq_challenge']['template']]
    sn = find_slide_by_anchor(pptx, REG.KQ_CHALLENGE_ANCHOR, REG.KQ_CHALLENGE_HINT)
    sp, rp = clone(work, pptx, sn, copy_hdphoto=True)
    delete_shapes_by_id(sp, REG.KQ_CHALLENGE_STRIP_IDS)
    delete_shape_by_name(sp, REG.KQ_CHALLENGE_STRIP_NAME)
    tree = xr(sp)
    kq_shape = find_sp(tree, REG.KQ_CHALLENGE_KQ_SHAPE_NAME)
    if kq_shape is None:
        raise RuntimeError(f"kq_challenge: expected shape '{REG.KQ_CHALLENGE_KQ_SHAPE_NAME}' not found - template drift")
    set_text(kq_shape, spec['key_question'])
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
    # The source discipline slides carry a pre-existing animation with a
    # clickEffect/spTgt count mismatch (confirmed on the Chemistry slide:
    # 11 vs 37) - broken in the original artwork, not introduced here.
    # Strip it rather than deliver malformed click behaviour.
    strip_timing(sp)
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
    sp, rp = fresh(work, 'We do')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    st.append(body_sp(3, spec['bullets']))
    save(t, sp)
    animate(sp, [[3]])  # single reveal of the whole content placeholder on first click
    return sp


def build_wedo_grid(work, spec):
    sp, rp = fresh(work, 'We do - Blank')
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
    sp, rp = fresh(work, 'I Do - Blank')
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
    sp, rp = fresh(work, 'You do Ind - Blank')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    save(t, sp)
    if not os.path.exists(spec['image_path']):
        raise RuntimeError(f"youdo_provocation: image_path '{spec['image_path']}' does not exist")
    add_img(sp, rp, work, spec['image_path'], 838200, 1700000, 10515600, 4900000, 3)
    return sp


def build_youdo_task(work, spec):
    sp, rp = fresh(work, 'You do Ind')
    t, st = get_spTree(sp)
    st.append(title_sp(2, spec['title'], REG.TITLE_FONT))
    st.append(body_sp(3, spec['bullets']))
    save(t, sp)
    animate(sp, [[3]])
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

    work = '/tmp/build_work'
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
    return out_path, manifest_path


if __name__ == '__main__':
    mtp_path, templates_dir, out_path, manifest_path = sys.argv[1:5]
    build_lesson(mtp_path, templates_dir, out_path, manifest_path)
