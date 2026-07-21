"""
restore_history_assets.py
─────────────────────────
Run this at the start of ANY cloud session that will use the History builder.
It pulls History/assets/ from the GitHub repo into /home/claude/assets/ so
build_history_lesson.py can find all PNGs without touching Innes's Mac.

Usage:
    python restore_history_assets.py

The repo is the single source of truth for all History builder assets.
If an asset is missing from the repo it must be committed there first
(see ASSET RULES in github-sync SKILL.md).
"""

import os
import re
import shutil
import subprocess
import sys

# ── Config ────────────────────────────────────────────────────────────────────
SKILL_PATH = '/root/.claude/skills/github-sync/SKILL.md'
DEST_ROOT  = '/home/claude/assets'
REPO_SUBDIR = 'History/assets'   # path inside the repo

# ── Read credentials from skill file ─────────────────────────────────────────
try:
    with open(SKILL_PATH) as f:
        skill_text = f.read()
except FileNotFoundError:
    sys.exit(f'ERROR: Cannot read {SKILL_PATH} — is the github-sync skill installed?')

TOKEN  = re.search(r'GITHUB_TOKEN:\s*(\S+)', skill_text).group(1)
REPO   = re.search(r'GITHUB_REPO:\s*(\S+)',  skill_text).group(1)
USER   = re.search(r'GITHUB_USER:\s*(\S+)',  skill_text).group(1)
REMOTE = f'https://{USER}:{TOKEN}@github.com/{REPO}.git'

# ── Clone repo ────────────────────────────────────────────────────────────────
clone_dir = '/home/claude/_repo_assets_restore'
if os.path.exists(clone_dir):
    shutil.rmtree(clone_dir)

print('Fetching assets from repo...')
r = subprocess.run(
    ['git', 'clone', '--depth=1', REMOTE, clone_dir],
    capture_output=True, text=True
)
if r.returncode != 0:
    sys.exit(f'ERROR: git clone failed:\n{r.stderr.replace(TOKEN, "***")}')

# ── Copy assets ───────────────────────────────────────────────────────────────
src = os.path.join(clone_dir, REPO_SUBDIR)
if not os.path.isdir(src):
    sys.exit(f'ERROR: {REPO_SUBDIR} not found in repo — assets may not have been committed yet.')

if os.path.exists(DEST_ROOT):
    shutil.rmtree(DEST_ROOT)
shutil.copytree(src, DEST_ROOT)

# ── Clean up clone ────────────────────────────────────────────────────────────
shutil.rmtree(clone_dir)

# ── Report ────────────────────────────────────────────────────────────────────
total = sum(len(files) for _, _, files in os.walk(DEST_ROOT))
print(f'Assets restored: {total} files → {DEST_ROOT}')
print('history_registry.py will auto-discover them at build time.')
