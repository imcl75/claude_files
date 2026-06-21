#!/usr/bin/env python3
"""South America blank annotation map — clean rewrite."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import numpy as np
import os

# ── Data ─────────────────────────────────────────────────────────────
cache = '/tmp/ne_countries/'
shp   = [f for f in os.listdir(cache) if f.endswith('.shp')][0]
world = gpd.read_file(cache + shp)
sa    = world[world['CONTINENT'] == 'South America'].copy()

SA_COLS = {
    'Brazil':   '#B3D9F2',
    'Ecuador':  '#F2D9B3',
    'Chile':    '#D9F2B3',
    'Bolivia':  '#F2B3D9',
    'Colombia': '#D9B3F2',
}
OTHER = '#EDE8DC'
OCEAN = '#C8DFF0'
BLUE  = '#1798d3'
NAVY  = '#12558A'

BOUNDS = (-82, -56, -35, 13)

# ── Figure layout ─────────────────────────────────────────────────────
# Map: slightly inset so arrow-lines have room to extend into margins
fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
ax  = fig.add_axes([0.14, 0.22, 0.72, 0.74])   # map
ax_b = fig.add_axes([0.02, 0.01, 0.96, 0.20])  # task panel

# ── Map ───────────────────────────────────────────────────────────────
ax.set_facecolor(OCEAN)
ax.set_xlim(BOUNDS[0], BOUNDS[2])
ax.set_ylim(BOUNDS[1], BOUNDS[3])
ax.axis('off')

for _, row in sa.iterrows():
    name = row['NAME']
    col  = SA_COLS.get(name, OTHER)
    ew   = 1.3 if name in SA_COLS else 0.4
    ec   = '#333333' if name in SA_COLS else '#AAAAAA'
    gpd.GeoSeries([row.geometry]).plot(ax=ax, color=col, edgecolor=ec, linewidth=ew)

# ── Equator and Tropic of Capricorn (no labels) ───────────────────────
xs = np.linspace(BOUNDS[0], BOUNDS[2], 300)
ax.plot(xs, [0]*300,     '#CC3333', lw=1.1, ls='-',  zorder=4)
ax.plot(xs, [-23.5]*300, '#CC6600', lw=1.1, ls='--', zorder=4)

# ── Title ─────────────────────────────────────────────────────────────
fig.text(0.5, 0.965, 'South America',
         fontsize=17, fontweight='bold', color=BLUE,
         ha='center', va='top', fontfamily='DejaVu Sans')

# ── Arrow-lines: pupils write country name ON the line ────────────────
# Left side: long horizontal arrow from left margin (-90) to country west edge
# Right side: long horizontal arrow from right margin (-27) to Brazil east edge
# annotation_clip=False so lines extend into the white page margins

AW_L = dict(arrowstyle='->', color='#222222', lw=1.0)
AW_R = dict(arrowstyle='->', color='#222222', lw=1.0)

def left_arr(x_tip, lat, x_tail=-90.5):
    ax.annotate('', xy=(x_tip, lat), xytext=(x_tail, lat),
                arrowprops=AW_L, zorder=7, annotation_clip=False)

def right_arr(x_tip, lat, x_tail=-26.5):
    ax.annotate('', xy=(x_tip, lat), xytext=(x_tail, lat),
                arrowprops=AW_R, zorder=7, annotation_clip=False)

left_arr(-77.0,   4.0)   # Colombia
left_arr(-80.0,  -1.5)   # Ecuador
left_arr(-64.5, -17.0)   # Bolivia
left_arr(-70.0, -37.0)   # Chile
right_arr(-35.8, -10.0)  # Brazil

# Equator / Tropic: extend lines into right margin for labelling
ax.plot([-35.8, -26.5], [0.0,    0.0],    '#CC3333', lw=0.9, zorder=7, clip_on=False)
ax.plot([-35.8, -26.5], [-23.5, -23.5],   '#CC6600', lw=0.9, zorder=7, clip_on=False)

# ── 8-point compass rose — drawn, pupils label each point ─────────────
cr_l, cr_b = -49.5, 5.0
cr_w, cr_h = 7.5, 7.5
cx = cr_l + cr_w / 2   # -45.75
cy = cr_b + cr_h / 2   #  8.75



# Draw compass rose — 4 filled cardinal diamonds + 4 intercardinal lines
R_CARD  = 2.65   # length of N/S/E/W diamond tips from centre
R_INTER = 1.75   # length of NE/SE/SW/NW line tips
W_CARD  = 0.38   # half-width of cardinal diamonds

for i in range(8):
    # Angle in degrees: N=90, NE=45, E=0, SE=-45 ... going anticlockwise in maths
    angle = 90 - i * 45
    rad   = np.radians(angle)
    is_cardinal = (i % 2 == 0)

    if is_cardinal:
        # Filled black diamond pointing outward
        r    = R_CARD
        tip  = (cx + r * np.cos(rad),       cy + r * np.sin(rad))
        perp = np.radians(angle + 90)
        lft  = (cx + W_CARD * np.cos(perp), cy + W_CARD * np.sin(perp))
        rgt  = (cx - W_CARD * np.cos(perp), cy - W_CARD * np.sin(perp))
        bk   = (cx - 0.18 * np.cos(rad),    cy - 0.18 * np.sin(rad))
        ax.fill([tip[0], lft[0], bk[0], rgt[0]],
                [tip[1], lft[1], bk[1], rgt[1]],
                color='#222222', zorder=10, clip_on=False)
    else:
        # Thin grey line + small filled dot at tip
        r     = R_INTER
        x_tip = cx + r * np.cos(rad)
        y_tip = cy + r * np.sin(rad)
        ax.plot([cx, x_tip], [cy, y_tip],
                color='#555555', lw=1.0, zorder=9, clip_on=False)
        ax.add_patch(plt.Circle((x_tip, y_tip), 0.15,
                                color='#555555', zorder=10, clip_on=False))

# Centre ring
ax.add_patch(plt.Circle((cx, cy), 0.28, color='#333333', zorder=11, clip_on=False))
ax.add_patch(plt.Circle((cx, cy), 0.14, color='white',   zorder=12, clip_on=False))

# ── Scale bar ─────────────────────────────────────────────────────────
sb_x, sb_y = -81.5, -52.5
ax.plot([sb_x, sb_x+9], [sb_y, sb_y], '#333333', lw=2.0)
ax.plot([sb_x]*2,    [sb_y-0.6, sb_y+0.6], '#333333', lw=2.0)
ax.plot([sb_x+9]*2,  [sb_y-0.6, sb_y+0.6], '#333333', lw=2.0)
ax.text(sb_x+4.5, sb_y-2.2, '0        1,000 km',
        fontsize=8, ha='center', color='#333333', fontfamily='DejaVu Sans')

# ── Task panel ────────────────────────────────────────────────────────
ax_b.set_xlim(0, 1)
ax_b.set_ylim(0, 1)
ax_b.axis('off')

ax_b.add_patch(mpatches.FancyBboxPatch(
    (0.01, 0.04), 0.98, 0.93,
    boxstyle='square,pad=0', lw=1.8,
    edgecolor=BLUE, facecolor='#F0F8FF'))

ax_b.text(0.5, 0.88,
          'Label the map using your lesson slides.',
          fontsize=13, fontweight='bold', color=NAVY,
          ha='center', va='center', fontfamily='DejaVu Sans')

task_lines = [
    '1.  Write the name of each highlighted country on its arrow line.',
    '2.  Write the name of the red line and the orange dashed line on their lines.',
    '3.  Label each of the points on the compass.',
]
for i, text in enumerate(task_lines):
    ax_b.text(0.05, 0.66 - i*0.19, text,
              fontsize=11, color='#222222',
              ha='left', va='center', fontfamily='DejaVu Sans')

ax_b.text(0.5, 0.16, 'Word bank:',
          fontsize=10, fontweight='bold', color=NAVY,
          ha='center', va='center', fontfamily='DejaVu Sans')
ax_b.text(0.5, 0.07,
          'Brazil     Ecuador     Chile     Bolivia     Colombia',
          fontsize=12, color='#222222',
          ha='center', va='center', fontfamily='DejaVu Sans')

# ── Save ─────────────────────────────────────────────────────────────
out = '/mnt/user-data/outputs/T6W4_-_South_America_Map_-_Print_Resource.pdf'
plt.savefig(out, format='pdf', bbox_inches='tight', dpi=200, facecolor='white')
print('Saved:', out)
