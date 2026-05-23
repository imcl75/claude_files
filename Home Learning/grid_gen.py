"""
grid_gen.py — WFA Home Learning grid generator
Saves /home/claude/grid_a5.png (185x185 pt at 150dpi)

EDIT THE ELEMENTS LIST EACH WEEK then run:
    python3 /home/claude/grid_gen.py

Element format:
    ('point',   (x, y),           label,         colour)
    ('arrow',   (x1,y1), (x2,y2), label_or_None, colour)
    ('triangle',(x1,y1),(x2,y2),(x3,y3), label_or_None, fill, edge)
    ('rect',    (x1,y1),(x2,y2),  label_or_None, fill, edge)
    ('star',    (x, y),           label,          colour)
    ('polygon', [(x,y),...],      label_or_None,  fill, edge)
    ('label',   (x, y),           text,           colour)
    ('hline',   y,                colour)   -- horizontal mirror line
    ('vline',   x,                colour)   -- vertical mirror line

Grid is always 10x10 (standard) unless GRID_SIZE overridden.
Set GRID_SIZE = 6 for adapted version.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

# ─── CONFIG ──────────────────────────────────────────────────────────────────

GRID_SIZE  = 10          # 10 for standard, 6 for adapted
OUTPUT     = '/home/claude/grid_a5.png'
DPI        = 150
PT_SIZE    = 185         # output size in points → 185/72*150 ≈ 385 px

# ~~~ ELEMENTS: REPLACE EACH WEEK ~~~
ELEMENTS = [
    ('point',    (2, 3),          'A',   '#1a3c8e'),
    ('point',    (7, 8),          'B',   '#1a3c8e'),
    ('arrow',    (1, 5), (4, 5),  'P→Q', '#c0392b'),
    ('triangle', (4,6),(6,8),(4,8), None, '#d5e8d4', '#2e6b3e'),
    ('star',     (7, 1),          'S',   '#e67e22'),
]
# ~~~ END ELEMENTS ~~~


# ─── DRAWING ─────────────────────────────────────────────────────────────────

def star_polygon(cx, cy, n=5, r_outer=0.3, r_inner=0.12):
    """Return vertices of an n-pointed star centred at (cx,cy)."""
    pts = []
    for i in range(2 * n):
        angle = math.pi / n * i - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts

import math

def draw_grid(elements, grid_size=10):
    px = PT_SIZE / 72 * DPI
    fig, ax = plt.subplots(figsize=(px/DPI, px/DPI), dpi=DPI)

    # Grid lines
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_aspect('equal')
    ax.set_xticks(range(grid_size + 1))
    ax.set_yticks(range(grid_size + 1))
    ax.tick_params(labelsize=5.5, length=2, pad=1)
    ax.grid(True, color='#b0b0b0', linewidth=0.5, zorder=0)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color('#606060')

    for el in elements:
        kind = el[0]

        if kind == 'point':
            _, (x, y), label, col = el
            ax.plot(x, y, 'o', color=col, markersize=5, zorder=5)
            ax.annotate(label, (x, y), textcoords='offset points',
                        xytext=(4, 4), fontsize=6.5, color=col,
                        fontweight='bold', zorder=6)

        elif kind == 'arrow':
            _, (x1,y1), (x2,y2), label, col = el
            ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                        arrowprops=dict(arrowstyle='->', color=col,
                                        lw=1.5), zorder=5)
            if label:
                mx, my = (x1+x2)/2, (y1+y2)/2
                ax.text(mx, my+0.25, label, fontsize=5.5, color=col,
                        ha='center', zorder=6)

        elif kind == 'triangle':
            _, p1, p2, p3, label, fill, edge = el
            tri = plt.Polygon([p1,p2,p3], closed=True,
                              facecolor=fill, edgecolor=edge,
                              linewidth=1.2, alpha=0.6, zorder=3)
            ax.add_patch(tri)
            if label:
                cx = (p1[0]+p2[0]+p3[0])/3
                cy = (p1[1]+p2[1]+p3[1])/3
                ax.text(cx, cy, label, fontsize=5.5, color=edge,
                        ha='center', va='center', zorder=4)

        elif kind == 'rect':
            _, (x1,y1), (x2,y2), label, fill, edge = el
            rect = plt.Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)],
                               closed=True, facecolor=fill, edgecolor=edge,
                               linewidth=1.2, alpha=0.6, zorder=3)
            ax.add_patch(rect)
            if label:
                ax.text((x1+x2)/2, (y1+y2)/2, label, fontsize=5.5,
                        color=edge, ha='center', va='center', zorder=4)

        elif kind == 'star':
            _, (cx, cy), label, col = el
            pts = star_polygon(cx, cy)
            star = plt.Polygon(pts, closed=True, facecolor=col,
                               edgecolor=col, linewidth=0.8,
                               alpha=0.85, zorder=4)
            ax.add_patch(star)
            if label:
                ax.annotate(label, (cx, cy), textcoords='offset points',
                            xytext=(6, 4), fontsize=6.5, color=col,
                            fontweight='bold', zorder=5)

        elif kind == 'polygon':
            _, verts, label, fill, edge = el
            poly = plt.Polygon(verts, closed=True, facecolor=fill,
                               edgecolor=edge, linewidth=1.2,
                               alpha=0.6, zorder=3)
            ax.add_patch(poly)
            if label:
                cx = sum(v[0] for v in verts) / len(verts)
                cy = sum(v[1] for v in verts) / len(verts)
                ax.text(cx, cy, label, fontsize=5.5, color=edge,
                        ha='center', va='center', zorder=4)

        elif kind == 'label':
            _, (x, y), text, col = el
            ax.text(x, y, text, fontsize=6, color=col,
                    ha='center', va='center', zorder=6,
                    fontweight='bold')

        elif kind == 'hline':
            _, y, col = el
            ax.axhline(y=y, color=col, linewidth=1.5,
                       linestyle='--', zorder=4)

        elif kind == 'vline':
            _, x, col = el
            ax.axvline(x=x, color=col, linewidth=1.5,
                       linestyle='--', zorder=4)

    plt.tight_layout(pad=0)
    plt.savefig(OUTPUT, dpi=DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Saved {OUTPUT}")


if __name__ == '__main__':
    draw_grid(ELEMENTS, GRID_SIZE)
