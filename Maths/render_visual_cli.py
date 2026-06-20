#!/usr/bin/env python3
"""
render_visual_cli.py — thin CLI wrapper around maths_visuals.render_visual().
Called by build_lp_v3.js via execFileSync.

Usage:
    python3 render_visual_cli.py <output_path> [dpi]
    
    JSON spec is read from stdin.

Exit 0 on success, 1 on failure (error message on stderr).
"""
import sys, json, os

sys.path.insert(0, '/home/claude')

try:
    from maths_visuals import render_visual
except ImportError as e:
    print(f'render_visual_cli: cannot import maths_visuals: {e}', file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 2:
    print('Usage: render_visual_cli.py <output_path> [dpi]', file=sys.stderr)
    sys.exit(1)

output_path = sys.argv[1]
dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 180

try:
    spec = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'render_visual_cli: invalid JSON spec: {e}', file=sys.stderr)
    sys.exit(1)

try:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    render_visual(spec, output_path, dpi)
    print(f'rendered:{output_path}', flush=True)
    sys.exit(0)
except Exception as e:
    print(f'render_visual_cli: render failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
