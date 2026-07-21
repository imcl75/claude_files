"""
verify_repo_assets.py
─────────────────────
Clones the repo fresh and checks every asset path referenced by every
builder against what's actually in the repo. Run this any time you want
to be sure nothing has gone missing.

Usage:
    python verify_repo_assets.py

Exits 0 if everything is present, 1 if anything is missing.
"""

import os, re, sys, shutil, subprocess, json

SKILL_PATH = '/root/.claude/skills/github-sync/SKILL.md'
CLONE_DIR  = '/home/claude/_verify_clone'

# ── Read credentials ──────────────────────────────────────────────────────────
with open(SKILL_PATH) as f:
    skill_text = f.read()
TOKEN  = re.search(r'GITHUB_TOKEN:\s*(\S+)', skill_text).group(1)
REPO   = re.search(r'GITHUB_REPO:\s*(\S+)',  skill_text).group(1)
USER   = re.search(r'GITHUB_USER:\s*(\S+)',  skill_text).group(1)
REMOTE = f'https://{USER}:{TOKEN}@github.com/{REPO}.git'

# ── Fresh clone ───────────────────────────────────────────────────────────────
if os.path.exists(CLONE_DIR):
    shutil.rmtree(CLONE_DIR)

print('Cloning repo for verification...')
r = subprocess.run(['git', 'clone', '--depth=1', REMOTE, CLONE_DIR],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f'Clone failed: {r.stderr.replace(TOKEN, "***")}')
print(f'Cloned to {CLONE_DIR}\n')

R = CLONE_DIR   # repo root
missing = []
checked = 0

def check(path, label):
    global checked
    checked += 1
    full = os.path.join(R, path)
    if not os.path.exists(full):
        missing.append(f'  ✗ [{label}]  {path}')
    return os.path.exists(full)

def section(title):
    print(f'── {title} {"─" * max(0, 55 - len(title))}')

# ─────────────────────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────────────────────
section('History builder')

HIST_BASE  = 'History/assets/Historians'
HIST_STATIC = [
    'hist-icon.png', 'hist-sub-concepts.png', 'Hist-skill.png',
    '21C-skills-KQ-slide.png', '4-children-KQ-slide.png',
]
HIST_BLOCKS = [
    'Hist-block-yellow-questioning-and-understanding.png',
    'Hist-block-peach-chronology.png',
    'Hist-block-pink-sources.png',
    'Hist-block-blue-interpretations.png',
]
HIST_CONCEPTS = {
    'Civilisation': ('civ', range(1,7)),
    'Empire':       ('emp', range(1,7)),
    'Invasion':     ('inv', range(1,7)),
    'Monarchy':     ('mon', range(1,7)),
    'Revolution':   ('rev', range(1,7)),
}
HIST_TEMPLATE = 'EnquiryBuilder/templates/history-example.pptx'

check('History/build_history_lesson.py',  'History builder script')
check('History/history_registry.py',      'History registry')
check('History/restore_history_assets.py','History restore script')
check(HIST_TEMPLATE,                      'History base PPTX')
for f in HIST_STATIC:
    check(f'{HIST_BASE}/{f}', f'History static/{f}')
for f in HIST_BLOCKS:
    check(f'{HIST_BASE}/{f}', f'History block/{f}')
for concept, (prefix, years) in HIST_CONCEPTS.items():
    for y in years:
        fn = f'{prefix}-Y{y}.png'
        check(f'{HIST_BASE}/{concept}/{fn}', f'History concept/{concept}/{fn}')

# ─────────────────────────────────────────────────────────────────────────────
# GEOGRAPHY
# ─────────────────────────────────────────────────────────────────────────────
section('Geography builder')

GEO_BASE = 'Geography/assets'
GEO_ICONS = [
    'geo-concepts.png', 'geo-Place-icon.png', 'geo-space-icon.png',
    'geo-scale-icon.png', 'geo-P-S-S-icon-combined.png',
    'geo-human-geog-icon.png', 'geo-culture-icon.png',
    'geo-physical-geog-icon.png', 'geo-sustain-icon.png', 'Skills.png',
]
GEO_JIGSAWS = [
    'new-Jig-orange-questioning.png', 'new-Jig-green-map-skills.png',
    'new-Jig-blue-concluding.png', 'new-Jig-purple-field-work.png',
    'new-Jig-yellow-observing.png',
]
GEO_CONCEPTS = {
    'Culture':           ('Culture-prog-y{}.png', range(1,7)),
    'Environment':       ('Env-prog-y{}.png',     range(1,7)),
    'Human Geography':   ('Hum-geo-prog-y{}.png', range(1,7)),
    'Physical Geography':('Physical-geo-prog-y{}.png', range(1,7)),
    'Place Space Scale': ('PSS-geo-prog-y{}.png', range(1,7)),
}

check('Geography/build_geography_lesson.py',  'Geography builder script')
check('Geography/geography_registry.py',       'Geography registry')
check('Geography/geographers_template.pptx',   'Geography base PPTX')
check('Geography/jigsaw-animated.pptx',        'Geography jigsaw reference PPTX')
check('Geography/fonts/TwinklCursiveLooped-Regular.ttf', 'Font Regular')
check('Geography/fonts/TwinklCursiveLooped-Light.ttf',   'Font Light')
for f in GEO_ICONS:
    check(f'{GEO_BASE}/{f}', f'Geo icon/{f}')
for f in GEO_JIGSAWS:
    check(f'{GEO_BASE}/Jigsaw Pieces/{f}', f'Geo jigsaw/{f}')
for concept, (tmpl, years) in GEO_CONCEPTS.items():
    for y in years:
        fn = tmpl.format(y)
        check(f'{GEO_BASE}/{concept}/{fn}', f'Geo concept/{concept}/{fn}')

# ─────────────────────────────────────────────────────────────────────────────
# MATHS
# ─────────────────────────────────────────────────────────────────────────────
section('Maths builder')

MATHS_ASSETS = [
    'Maths/assets/template_v3.pptx',
    'Maths/assets/KQ_Slide_template.pptx',
    'Maths/assets/LR_slide.pptx',
    'Maths/assets/Working_Memory_Template.pptx',
    'Maths/assets/rapid_maths_TEMPLATE.pptx',
    'Maths/assets/key-question-new.pptx',
    'Maths/assets/4 children KQ slide.png',
    'Maths/assets/cloud KQ slide.png',
    'Maths/assets/KQ key icon.png',
    'Maths/assets/maths-icon.png',
    'Maths/assets/banner_analyse.png',
    'Maths/assets/banner_attack.png',
    'Maths/assets/banner_visualise.png',
    'Maths/assets/i do icon.png',
    'Maths/assets/we do icon.png',
    'Maths/assets/you do icon.png',
    'Maths/assets/you do trio icon.png',
    'Maths/WFA_Labels_template.docx',
]
for f in MATHS_ASSETS:
    check(f, f'Maths/{os.path.basename(f)}')

# ─────────────────────────────────────────────────────────────────────────────
# ENQUIRY BUILDER (Science)
# ─────────────────────────────────────────────────────────────────────────────
section('EnquiryBuilder / Science')

for f in [
    'EnquiryBuilder/build_science_lesson.py',
    'EnquiryBuilder/science_registry.py',
    'EnquiryBuilder/lib_ooxml.py',
    'EnquiryBuilder/image_layouts.py',
    'EnquiryBuilder/templates/science-example.pptx',
    'EnquiryBuilder/templates/Being_a_Scientist_slide_deck.pptx',
    'EnquiryBuilder/templates/KQ_LO.pptx',
    'EnquiryBuilder/templates/KQ_and_BeingAScientist.pptx',
    'EnquiryBuilder/quiz_recap_template.pptx',
]:
    check(f, f'EnquiryBuilder/{os.path.basename(f)}')

# ─────────────────────────────────────────────────────────────────────────────
# SHARED ASSETS
# ─────────────────────────────────────────────────────────────────────────────
section('Shared assets')

for f in [
    'Assets/Shared/21C-skills-KQ-slide.png',
    'Assets/Shared/4-children-KQ-slide.png',
    'Assets/Shared/cloud-KQ-slide.png',
    'Assets/Shared/KQ-key-and-text-KQ-slide.png',
    'Assets/Shared/areas-of-study.png',
    'Assets/Shared/geographer-icon.png',
    'Assets/Shared/scientist-icon.png',
    'Assets/Shared/sci-skills.png',
    'Shared/badges/badge_ido.png',
    'Shared/badges/badge_wedo.png',
    'Shared/badges/badge_youdo_ind.png',
    'Shared/badges/badge_youdo_trio.png',
]:
    check(f, f'Shared/{os.path.basename(f)}')

# ─────────────────────────────────────────────────────────────────────────────
# LEARNING PAPER
# ─────────────────────────────────────────────────────────────────────────────
section('Learning Paper')

for f in [
    'LearningPaper/etiw_assets/ETIW-LKS2-Y3-Y4.png',
    'LearningPaper/etiw_assets/ETIW-UKS2-Y5-Y6.png',
    'LearningPaper/etiw_assets/ETIW-Y1.png',
    'LearningPaper/etiw_assets/ETIW-Y2.png',
    'LearningPaper/etiw_assets/writer-icon.png',
    'LearningPaper/ll_assets/icon_historian.png',
    'LearningPaper/ll_assets/icon_geographer.png',
    'LearningPaper/ll_assets/icon_scientist.png',
    'LearningPaper/ll_assets/icon_mathematician.png',
    'LearningPaper/ll_assets/school_logo.png',
]:
    check(f, f'LearningPaper/{os.path.basename(f)}')

# ─────────────────────────────────────────────────────────────────────────────
# WRITING / SPELLING / READING
# ─────────────────────────────────────────────────────────────────────────────
section('Writing / Spelling / Reading')

for f in [
    'Writing/assets/writing_lesson_base.pptx',
    'Spelling/key_spelling_template.pptx',
    'Reading/BeingAReader_Template.pptx',
]:
    check(f, f'Other/{os.path.basename(f)}')

# ─────────────────────────────────────────────────────────────────────────────
# DOCS
# ─────────────────────────────────────────────────────────────────────────────
section('Documentation')
check('ASSET_REGISTRY.md', 'ASSET_REGISTRY.md')
check('EnquiryBuilder/ENQUIRY_BUILDER_WORKFLOW.md', 'ENQUIRY_BUILDER_WORKFLOW.md')
check('EnquiryBuilder/MTP_schema_reference.md', 'MTP_schema_reference.md')

# ─────────────────────────────────────────────────────────────────────────────
# RESULT
# ─────────────────────────────────────────────────────────────────────────────
print()
print('═' * 60)
print(f'Checked {checked} files')
if missing:
    print(f'\n❌  {len(missing)} MISSING:')
    for m in missing:
        print(m)
    shutil.rmtree(CLONE_DIR, ignore_errors=True)
    sys.exit(1)
else:
    print(f'\n✅  All {checked} files present in repo.')
    shutil.rmtree(CLONE_DIR, ignore_errors=True)
    sys.exit(0)
