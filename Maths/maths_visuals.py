"""
maths_visuals.py — WFA Maths Visual Rendering Library v1.0
============================================================
Renders mathematical representations as PNG images for embedding
in teaching slides (build_lesson_v3.py) and learning papers (build_lp_v3.js).

Usage:
    from maths_visuals import render_visual
    path = render_visual({'type': 'pv_counter_chart', ...}, 'output.png')

All renderers accept a spec dict and an output_path string.
Optional dpi parameter (default 150 for slides, use 200+ for print LPs).
"""

import os, math, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyBboxPatch, FancyArrowPatch, Wedge
from matplotlib.path import Path
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
warnings.filterwarnings('ignore')

# ─── COLOUR PALETTE ──────────────────────────────────────────────────────────

# Place value — counter colours used in ALL contexts (headers + counters)
PV = {
    'M':   '#8B1A00',
    'HTH': '#C84400',
    'TTH': '#E06010',
    'TH':  '#2565AE',   # thousands  — blue
    'H':   '#2E8B3A',   # hundreds   — green
    'T':   '#D4A800',   # tens       — amber
    'O':   '#C83030',   # ones       — red
    't':   '#4BAEE0',   # tenths     — blue
    'h':   '#82CBF0',   # hundredths — lighter blue
    'th':  '#B8E2F8',   # thousandths
    '.':   '#B0B0B0',   # decimal point column
}

PV_TEXT = {
    'M': 'white', 'HTH': 'white', 'TTH': 'white',
    'TH': 'white', 'H': 'white', 'T': '#1A1A1A',
    'O': 'white', 't': 'white', 'h': '#1A1A1A', 'th': '#1A1A1A',
    '.': 'white',
}

PV_LONG = {
    'M': 'Millions', 'HTH': 'Hundred\nThousands', 'TTH': 'Ten\nThousands',
    'TH': 'Thousands', 'H': 'Hundreds', 'T': 'Tens', 'O': 'Ones',
    't': 'tenths', 'h': 'hundredths', 'th': 'thousandths', '.': '.',
}

# Standard column ordering (left → right)
PV_ORDER = ['M', 'HTH', 'TTH', 'TH', 'H', 'T', 'O', '.', 't', 'h', 'th']

# General colours
SHAPE_A     = '#1F4E79'
SHAPE_B     = '#E8642A'
SHAPE_C     = '#7030A0'
SHAPE_D     = '#375623'
ANSWER_GRN  = '#1A5C2A'
SLIDE_BG    = '#DEECF8'
ARRAY_COLS  = ['#4A90D9', '#E8A030', '#8040B0', '#2EA050', '#D03050']
LIGHT_GREY  = '#E8E8E8'
MID_GREY    = '#A0A0A0'
DARK        = '#1A1A1A'
WHITE       = '#FFFFFF'
FRACTION_BLUE   = '#4A90D9'
FRACTION_ORANGE = '#E8A030'
FRACTION_PURPLE = '#8040B0'
FRACTION_GREEN  = '#2EA050'

# ─── CORE UTILITIES ──────────────────────────────────────────────────────────

def _save(fig, path, dpi):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none', pad_inches=0.05)
    plt.close(fig)
    return path

def _font(size, weight='normal', family='DejaVu Sans'):
    return {'fontsize': size, 'fontweight': weight, 'fontfamily': family}

def render_visual(spec, output_path, dpi=150):
    """Main entry point — dispatches to the correct renderer."""
    t = spec.get('type')
    _DISPATCH = {
        'pv_counter_chart':     _pv_counter_chart,
        'pv_chart_header':      _pv_chart_header,
        'dienes':               _dienes,
        'number_line':          _number_line,
        'part_whole':           _part_whole,
        'bar_model':            _bar_model,
        'array':                _array,
        'which_answer':         _which_answer,
        'fraction_bar':         _fraction_bar,
        'equivalence_bars':     _equivalence_bars,
        'equivalence_arrows':   _equivalence_arrows,
        'hundred_square':       _hundred_square,
        'ten_strip':            _ten_strip,
        'fraction_number_line': _fraction_number_line,
        'fraction_shape':       _fraction_shape,
        'fraction_set':         _fraction_set,
        'fraction_circles':     _fraction_circles,
        'coordinate_grid':      _coordinate_grid,
        'angle_figure':         _angle_figure,
        'angle_figure_set':     _angle_figure_set,
        'triangle_angles':      _triangle_angles,
        'polygon':              _polygon,
        'shape_3d_iso':         _shape_3d_iso,
        'shape_3d_net':         _shape_3d_net,
        'venn_diagram':         _venn_diagram,
        'carroll_diagram':      _carroll_diagram,
        'tally_chart':          _tally_chart,
        'bar_chart':            _bar_chart,
        'line_graph':           _line_graph,
        'pie_chart':            _pie_chart,
        'timetable':            _timetable,
    }
    if t not in _DISPATCH:
        raise ValueError(f"Unknown visual type '{t}'. Available: {sorted(_DISPATCH)}")
    return _DISPATCH[t](spec, output_path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PLACE VALUE — COUNTER CHART
# ═══════════════════════════════════════════════════════════════════════════════

def _pv_counter_chart(spec, path, dpi):
    """
    Spec:
        columns:       list e.g. ['TH','H','T','O']  (default ['TH','H','T','O'])
        rows:          list of dicts  e.g. [{'TH':2,'H':0,'T':5,'O':4}, ...]
        show_digit_row: bool  — show digit summary row at bottom (default True)
        exchange_from:  dict  — highlight exchange e.g. {'O':10} shows 10 ones
                                with arrow indicating regrouping
    """
    cols   = spec.get('columns', ['TH', 'H', 'T', 'O'])
    rows   = spec.get('rows', [{'TH': 1, 'H': 2, 'T': 3, 'O': 4}])
    show_d = spec.get('show_digit_row', True)
    n_rows = len(rows)

    # Decimal point column is a narrow separator, not a place value
    CELL_W  = 1.4
    DOT_W   = 0.42   # much narrower
    cell_h  = 1.5
    header_h = 0.55
    digit_h  = 0.60

    def _cw(col): return DOT_W if col == '.' else CELL_W

    col_widths = [_cw(c) for c in cols]
    total_w = sum(col_widths)
    total_h = header_h + n_rows * cell_h + (digit_h if show_d else 0)

    fig, ax = plt.subplots(figsize=(total_w, total_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, total_h)
    ax.axis('off')

    # ── Header row
    x = 0.0
    for col in cols:
        cw = _cw(col)
        if col == '.':
            rect = mpatches.FancyBboxPatch(
                (x, total_h - header_h), cw, header_h,
                boxstyle='square,pad=0', linewidth=1.5,
                edgecolor='#444', facecolor=PV['.'])
            ax.add_patch(rect)
            ax.text(x + cw/2, total_h - header_h/2, '.',
                    ha='center', va='center', color='white',
                    fontsize=22, fontweight='bold')
        else:
            rect = mpatches.FancyBboxPatch(
                (x, total_h - header_h), cw, header_h,
                boxstyle='square,pad=0', linewidth=1.5,
                edgecolor='#444', facecolor=PV[col])
            ax.add_patch(rect)
            ax.text(x + cw/2, total_h - header_h/2,
                    PV_LONG.get(col, col),
                    ha='center', va='center', color=PV_TEXT[col],
                    fontsize=11, fontweight='bold', linespacing=1.2)
        x += cw

    # ── Counter rows
    for ri, row_data in enumerate(rows):
        y_bottom = total_h - header_h - (ri + 1) * cell_h
        x = 0.0
        for col in cols:
            cw = _cw(col)
            if col == '.':
                # Thin grey separator column — just a dot, no counters
                rect = mpatches.FancyBboxPatch(
                    (x, y_bottom), cw, cell_h,
                    boxstyle='square,pad=0', linewidth=0.8,
                    edgecolor='#AAA', facecolor='#EBEBEB')
                ax.add_patch(rect)
                ax.text(x + cw/2, y_bottom + cell_h/2, '.',
                        ha='center', va='center', color='#777',
                        fontsize=18, fontweight='bold')
            else:
                rect = mpatches.FancyBboxPatch(
                    (x, y_bottom), cw, cell_h,
                    boxstyle='square,pad=0', linewidth=1.2,
                    edgecolor='#888', facecolor='#D8EAF8')
                ax.add_patch(rect)
                count = row_data.get(col, 0)
                _draw_counters(ax, x, y_bottom, cw, cell_h, count, col)
            x += cw

    # ── Digit summary row — no digit for '.' column
    if show_d:
        digit_values = {col: sum(r.get(col, 0) for r in rows)
                        for col in cols if col != '.'}
        y_bottom = 0.0
        x = 0.0
        for col in cols:
            cw = _cw(col)
            rect = mpatches.FancyBboxPatch(
                (x, y_bottom), cw, digit_h,
                boxstyle='square,pad=0', linewidth=1.5,
                edgecolor='#444', facecolor=WHITE)
            ax.add_patch(rect)
            if col == '.':
                ax.text(x + cw/2, y_bottom + digit_h/2, '.',
                        ha='center', va='center', color='#777',
                        fontsize=22, fontweight='bold')
            else:
                ax.text(x + cw/2, y_bottom + digit_h/2,
                        str(digit_values.get(col, 0)),
                        ha='center', va='center', color=DARK,
                        fontsize=22, fontweight='bold')
            x += cw

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _draw_counters(ax, x0, y0, cw, ch, count, col):
    """Draw up to 9 counters in a cell, arranged in a 3×3 grid."""
    if count == 0:
        return
    count = min(count, 9)
    colour = PV[col]
    tcolour = PV_TEXT.get(col, 'white')
    label = PV_LONG.get(col, col).replace('\n', '')
    # Short value labels for counters
    val_labels = {
        'M': 'M', 'HTH': '100K', 'TTH': '10K',
        'TH': '1,000', 'H': '100', 'T': '10', 'O': '1',
        't': '0.1', 'h': '0.01', 'th': '0.001',
    }
    lbl = val_labels.get(col, col)

    # Layout: rows of 3, bottom-aligned
    r = math.ceil(count / 3)
    c_per_row = min(count, 3)
    radius = min(cw / (2 * c_per_row + 1.5), ch / (2 * r + 1.5)) * 0.85
    radius = min(radius, 0.28)

    placed = 0
    for row in range(r - 1, -1, -1):
        n_this_row = min(3, count - placed)
        # Center the row horizontally
        row_y = y0 + ch * 0.15 + row * (radius * 2.3)
        for ci2 in range(n_this_row):
            cx = x0 + cw * (ci2 + 0.5) / n_this_row + cw / (2 * n_this_row) * (1 - n_this_row/3)
            # Better horizontal spacing
            cx = x0 + cw / 2 + (ci2 - (n_this_row - 1) / 2) * (radius * 2.3)
            cy = row_y + radius
            circle = plt.Circle((cx, cy), radius,
                                 color=colour, zorder=3, linewidth=0.8,
                                 edgecolor='#333333')
            ax.add_patch(circle)
            fsize = max(4, radius * 28)
            ax.text(cx, cy, lbl, ha='center', va='center',
                    fontsize=min(fsize, 7), fontweight='bold',
                    color=tcolour, zorder=4, linespacing=1.0)
            placed += 1


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PV CHART HEADER (empty grid for pupils to fill in)
# ═══════════════════════════════════════════════════════════════════════════════

def _pv_chart_header(spec, path, dpi):
    """
    Spec:
        columns:  list e.g. ['TH','H','T','O'] or include '.' for decimal point
        n_rows:   number of empty data rows (default 2)
        show_long_names: bool (default True) — show full name below abbreviation
    """
    cols      = spec.get('columns', ['TH', 'H', 'T', 'O'])
    n_rows    = spec.get('n_rows', 2)
    show_long = spec.get('show_long_names', True)

    # Decimal point column is narrower
    col_widths = [0.6 if c == '.' else 1.6 for c in cols]
    total_w = sum(col_widths)
    header_h = 0.9 if show_long else 0.55
    row_h    = 1.2
    total_h  = header_h + n_rows * row_h

    fig, ax = plt.subplots(figsize=(total_w, total_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, total_h)
    ax.axis('off')

    x = 0
    for ci, col in enumerate(cols):
        cw = col_widths[ci]
        is_decimal_pt = (col == '.')

        # Header cell
        rect = mpatches.FancyBboxPatch(
            (x, total_h - header_h), cw, header_h,
            boxstyle='square,pad=0', linewidth=1.5,
            edgecolor='#444', facecolor=PV[col])
        ax.add_patch(rect)

        if is_decimal_pt:
            ax.text(x + cw/2, total_h - header_h/2, '.',
                    ha='center', va='center', color='white',
                    fontsize=18, fontweight='bold')
        else:
            # Abbreviation (large)
            abbrv = col if col not in ('TH',) else 'Th'
            if show_long:
                ax.text(x + cw/2, total_h - header_h * 0.35, abbrv,
                        ha='center', va='center', color=PV_TEXT[col],
                        fontsize=16, fontweight='bold')
                long_name = PV_LONG.get(col, col).replace('\n', ' ')
                ax.text(x + cw/2, total_h - header_h * 0.78, long_name,
                        ha='center', va='center', color=PV_TEXT[col],
                        fontsize=7.5, fontweight='normal')
            else:
                ax.text(x + cw/2, total_h - header_h/2, abbrv,
                        ha='center', va='center', color=PV_TEXT[col],
                        fontsize=16, fontweight='bold')

        # Data rows
        for ri in range(n_rows):
            y_bottom = total_h - header_h - (ri + 1) * row_h
            rect = mpatches.FancyBboxPatch(
                (x, y_bottom), cw, row_h,
                boxstyle='square,pad=0', linewidth=1.0,
                edgecolor='#888', facecolor=WHITE)
            ax.add_patch(rect)
        x += cw

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DIENES BLOCKS (2D flat representation)
# ═══════════════════════════════════════════════════════════════════════════════

def _dienes(spec, path, dpi):
    """
    Spec:
        TH: int  (0–9)  — thousands cubes
        H:  int  (0–9)  — hundreds flats
        T:  int  (0–9)  — tens rods
        O:  int  (0–9)  — ones units
        layout: 'horizontal' | 'grouped'  (default 'horizontal')
    """
    th = spec.get('TH', 0)
    h  = spec.get('H', 0)
    t  = spec.get('T', 0)
    o  = spec.get('O', 0)

    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.set_aspect('equal')
    ax.axis('off')

    x = 0.1
    y_base = 0.1
    gap = 0.12

    # Thousands — 10×10 square with inner grid
    for _ in range(th):
        _dienes_thousand(ax, x, y_base, 1.8)
        x += 1.8 + gap * 2

    # Hundreds — 10×10 grid flat
    for _ in range(h):
        _dienes_hundred(ax, x, y_base, 1.4)
        x += 1.4 + gap

    # Tens — tall rod (10 units)
    for _ in range(t):
        _dienes_ten(ax, x, y_base, 0.18, 1.4)
        x += 0.18 + gap * 0.8

    # Ones — small squares
    ones_per_row = 5
    o_x, o_y = x, y_base
    for i in range(o):
        _dienes_one(ax, o_x, o_y, 0.18)
        o_x += 0.18 + gap * 0.5
        if (i + 1) % ones_per_row == 0:
            o_x = x
            o_y += 0.18 + gap * 0.5

    total_x = x + (ones_per_row * (0.18 + gap * 0.5)) + 0.5
    ax.set_xlim(-0.05, max(total_x, 1))
    ax.set_ylim(-0.05, 2.0)
    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _dienes_thousand(ax, x, y, size):
    """Draw a thousands cube as large 10×10 block with 1,000 label."""
    c = PV['TH']
    rect = plt.Rectangle((x, y), size, size,
                          facecolor=c, edgecolor='#1A3A5A', linewidth=1.2)
    ax.add_patch(rect)
    n = 10
    s = size / n
    for i in range(1, n):
        ax.plot([x + i*s, x + i*s], [y, y + size], color='#1A3A5A', lw=0.4)
        ax.plot([x, x + size], [y + i*s, y + i*s], color='#1A3A5A', lw=0.4)
    # Label in centre — makes clear this is 1,000 not a 10×10 array
    ax.text(x + size/2, y + size/2, '1,000',
            ha='center', va='center', color='white',
            fontsize=max(7, size * 6), fontweight='bold')


def _dienes_hundred(ax, x, y, size):
    """Draw a hundreds flat as 10×10 grid."""
    c = PV['H']
    rect = plt.Rectangle((x, y), size, size,
                          facecolor=c, edgecolor='#1A4A2A', linewidth=1.2)
    ax.add_patch(rect)
    n = 10
    s = size / n
    for i in range(1, n):
        ax.plot([x + i*s, x + i*s], [y, y + size], color='#1A4A2A', lw=0.4)
        ax.plot([x, x + size], [y + i*s, y + i*s], color='#1A4A2A', lw=0.4)


def _dienes_ten(ax, x, y, w, h):
    """Draw a tens rod as a tall thin rectangle with 10 divisions."""
    c = PV['T']
    rect = plt.Rectangle((x, y), w, h,
                          facecolor=c, edgecolor='#8A6A00', linewidth=1.0)
    ax.add_patch(rect)
    s = h / 10
    for i in range(1, 10):
        ax.plot([x, x + w], [y + i*s, y + i*s], color='#8A6A00', lw=0.5)


def _dienes_one(ax, x, y, size):
    """Draw a ones unit as a small square."""
    c = PV['O']
    rect = plt.Rectangle((x, y), size, size,
                          facecolor=c, edgecolor='#8A1A1A', linewidth=0.8)
    ax.add_patch(rect)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. NUMBER LINE
# ═══════════════════════════════════════════════════════════════════════════════

def _number_line(spec, path, dpi):
    """
    Spec:
        start:          number (default 0)
        end:            number (default 10)
        step:           tick interval (default auto)
        labelled_points: list of {value, label, color} — points to mark
        jumps:          list of {start, end, label, color} — arcs above the line
        x_marker:       value — position of X marker (fraction/rounding questions)
        open_line:      bool — no tick marks, just arrows (default False)
        minor_ticks:    int  — number of minor ticks between major (default 0)
    """
    start = spec.get('start', 0)
    end   = spec.get('end', 10)
    step  = spec.get('step', None)
    pts   = spec.get('labelled_points', [])
    jumps = spec.get('jumps', [])
    x_mk  = spec.get('x_marker', None)
    open_l = spec.get('open_line', False)
    minor  = spec.get('minor_ticks', 0)

    if step is None:
        rng = end - start
        for s in [1, 2, 5, 10, 25, 50, 100, 0.1, 0.25, 0.5, 1/4, 1/2]:
            if 4 <= rng / s <= 12:
                step = s
                break
        if step is None:
            step = rng / 8

    fig, ax = plt.subplots(figsize=(8, 1.8 + (0.6 if jumps else 0)))
    ax.set_xlim(start - (end - start) * 0.06, end + (end - start) * 0.06)
    # ylim needs headroom for arcs
    _max_arc = 0.0
    if jumps:
        _span = max(end - start, 1)
        _max_arc = max(min((j['end']-j['start']) / _span * 1.2 + 0.18, 0.72)
                       for j in jumps)
    ax.set_ylim(-0.55, 0.6 + _max_arc + 0.25)
    ax.axis('off')

    y_line = 0

    # Main line with arrows
    ax.annotate('', xy=(end + (end - start) * 0.04, y_line),
                xytext=(start - (end - start) * 0.04, y_line),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2.0))

    # Major ticks and labels
    if not open_l:
        v = start
        while v <= end + 1e-9:
            ax.plot([v, v], [y_line - 0.12, y_line + 0.12],
                    color=DARK, lw=1.5)
            ax.text(v, y_line - 0.25, _fmt_number(v),
                    ha='center', va='top', fontsize=11, color=DARK)
            if minor > 0:
                for m in range(1, minor + 1):
                    mv = v + step * m / (minor + 1)
                    if mv < end + 1e-9:
                        ax.plot([mv, mv], [y_line - 0.07, y_line + 0.07],
                                color=MID_GREY, lw=0.8)
            v = round(v + step, 10)

    # X marker
    if x_mk is not None:
        ax.plot([x_mk, x_mk], [y_line - 0.18, y_line + 0.18],
                color=DARK, lw=1.5)
        # Draw X symbol
        s = 0.1
        ax.plot([x_mk - s, x_mk + s], [y_line + 0.22, y_line + 0.42],
                color='#C08000', lw=2.5)
        ax.plot([x_mk + s, x_mk - s], [y_line + 0.22, y_line + 0.42],
                color='#C08000', lw=2.5)

    # Labelled points
    for pt in pts:
        v = pt['value']
        col = pt.get('color', SHAPE_A)
        lbl = pt.get('label', _fmt_number(v))
        circle = plt.Circle((v, y_line), 0.08, color=col, zorder=5)
        ax.add_patch(circle)
        ax.text(v, y_line + 0.22, lbl,
                ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=col)

    # Jumps — proper quadratic bezier arcs, labels at arc peak
    x_span = max(end - start, 1)
    # Work out max arc height so we can set ylim correctly
    max_arc_h = 0.0
    for j in jumps:
        jd = j['end'] - j['start']
        ah = min(jd / x_span * 1.2 + 0.18, 0.72)
        max_arc_h = max(max_arc_h, ah)

    for j in jumps:
        jstart = j['start']
        jend   = j['end']
        jlbl   = j.get('label', '')
        jcol   = j.get('color', SHAPE_B)
        mid_x  = (jstart + jend) / 2
        jd     = jend - jstart
        arc_h  = min(jd / x_span * 1.2 + 0.18, 0.72)

        # Quadratic bezier: P0 = start, P1 = apex control, P2 = end
        t  = np.linspace(0, 1, 120)
        p0 = np.array([jstart, y_line + 0.12])
        p1 = np.array([mid_x,  y_line + 0.12 + arc_h])
        p2 = np.array([jend,   y_line + 0.12])
        pts = (((1-t)**2)[:,None]*p0
               + (2*t*(1-t))[:,None]*p1
               + (t**2)[:,None]*p2)

        # Draw arc body (stop a few pts before end to leave room for arrow)
        cut = 10
        ax.plot(pts[:-cut, 0], pts[:-cut, 1],
                color=jcol, lw=2.0, solid_capstyle='round', zorder=4)

        # Arrow head at landing point
        ax.annotate('',
                    xy=(pts[-1, 0], pts[-1, 1]),
                    xytext=(pts[-cut-2, 0], pts[-cut-2, 1]),
                    arrowprops=dict(arrowstyle='->', color=jcol,
                                   lw=2.0, mutation_scale=14),
                    zorder=5)

        # Label exactly at arc peak
        if jlbl:
            ax.text(mid_x, y_line + 0.12 + arc_h + 0.06, jlbl,
                    ha='center', va='bottom', fontsize=10,
                    color=jcol, fontweight='bold', zorder=6)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _fmt_number(v):
    """Format a number cleanly — int if whole, decimal if not."""
    if isinstance(v, str):
        return v
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    # Try simple fractions
    from fractions import Fraction
    f = Fraction(v).limit_denominator(20)
    if abs(float(f) - v) < 1e-9 and f.denominator > 1:
        if f.numerator > f.denominator:
            whole = f.numerator // f.denominator
            rem   = f.numerator % f.denominator
            return f'{whole}½' if f.denominator == 2 else f'{whole} {rem}/{f.denominator}'
        return f'{f.numerator}/{f.denominator}'
    return f'{v:.2f}'.rstrip('0').rstrip('.')


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PART-WHOLE MODEL
# ═══════════════════════════════════════════════════════════════════════════════

def _part_whole(spec, path, dpi):
    """
    Spec:
        whole:  value (string or number) — top circle
        parts:  list of values — bottom circles
        title:  optional string above
        show_labels: bool (default True)
    """
    whole = spec.get('whole', '?')
    parts = spec.get('parts', ['?', '?'])
    title = spec.get('title', '')
    n = len(parts)

    fig_w = max(n * 1.6, 3.5)
    fig, ax = plt.subplots(figsize=(fig_w, 2.8))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, 2.8)
    ax.axis('off')

    # Whole circle at top centre
    cx_top = fig_w / 2
    cy_top = 2.2
    r = 0.38

    circle_top = plt.Circle((cx_top, cy_top), r,
                             facecolor=SHAPE_A, edgecolor='#0A2040',
                             linewidth=1.8, zorder=3)
    ax.add_patch(circle_top)
    ax.text(cx_top, cy_top, str(whole),
            ha='center', va='center', color='white',
            fontsize=15, fontweight='bold', zorder=4)

    # Part circles at bottom, evenly spaced
    spacing = fig_w / (n + 1)
    cy_bot  = 0.6

    for i, p in enumerate(parts):
        cx = spacing * (i + 1)
        # Line from whole to part
        ax.plot([cx_top, cx], [cy_top - r, cy_bot + r],
                color='#444444', lw=1.5, zorder=1)
        circle = plt.Circle((cx, cy_bot), r,
                             facecolor=SHAPE_B, edgecolor='#601800',
                             linewidth=1.8, zorder=3)
        ax.add_patch(circle)
        ax.text(cx, cy_bot, str(p),
                ha='center', va='center', color='white',
                fontsize=15, fontweight='bold', zorder=4)

    if title:
        ax.text(fig_w/2, 2.7, title,
                ha='center', va='top', fontsize=10, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. BAR MODEL
# ═══════════════════════════════════════════════════════════════════════════════

def _bar_model(spec, path, dpi):
    """
    Spec:
        model_type:  'part_whole' | 'comparison' | 'fraction_of' | 'ratio'
        
        For 'part_whole':
            whole:  {value, label, color}
            parts:  [{value, label, color}, ...]
        
        For 'comparison':
            bars:   [{value, label, color}, ...]
            show_difference: bool
        
        For 'fraction_of':
            total_parts: int
            shaded_parts: int
            total_value: number or '?'
            shade_color: hex
        
        For 'ratio':
            groups: [{count, label, color}, ...]
    """
    mt = spec.get('model_type', 'part_whole')

    if mt == 'part_whole':
        return _bar_model_part_whole(spec, path, dpi)
    elif mt == 'comparison':
        return _bar_model_comparison(spec, path, dpi)
    elif mt == 'fraction_of':
        return _bar_model_fraction_of(spec, path, dpi)
    elif mt == 'ratio':
        return _bar_model_ratio(spec, path, dpi)
    else:
        raise ValueError(f"Unknown bar_model model_type: {mt}")


def _bar_model_part_whole(spec, path, dpi):
    whole = spec.get('whole', {'value': '?', 'label': '', 'color': SHAPE_A})
    parts = spec.get('parts', [
        {'value': '?', 'label': '', 'color': SHAPE_B},
        {'value': '?', 'label': '', 'color': SHAPE_C},
    ])

    bar_h   = 0.6
    bar_w   = 7.0
    fig_h   = 3.5
    fig, ax = plt.subplots(figsize=(8, fig_h))
    ax.set_xlim(-0.2, bar_w + 0.5)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Whole bar (top)
    y_whole = 2.5
    rect = mpatches.FancyBboxPatch((0, y_whole), bar_w, bar_h,
        boxstyle='square,pad=0.02', linewidth=1.8,
        edgecolor='#333', facecolor=whole.get('color', SHAPE_A))
    ax.add_patch(rect)
    wv = whole.get('value', '?')
    ax.text(bar_w/2, y_whole + bar_h/2, str(wv),
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    wl = whole.get('label', '')
    if wl:
        ax.text(bar_w + 0.15, y_whole + bar_h/2, wl,
                ha='left', va='center', fontsize=10, color=DARK)

    # Bracket lines
    ax.plot([bar_w/2, bar_w/2], [y_whole - 0.05, y_whole - 0.25], color='#444', lw=1.5)

    # Part bars (bottom)
    y_parts = 1.2
    # Calculate proportional widths using 'proportion' key if present, else 'value'
    # This lets '?' parts still render at the correct width
    def _size_val(p):
        if 'proportion' in p:
            return float(p['proportion'])
        try:
            return float(str(p.get('value', 0)).replace('?', '0'))
        except:
            return 0.0

    nums = [_size_val(p) for p in parts]
    total = sum(nums) or len(parts)
    widths = [bar_w * n / total for n in nums]

    x = 0
    for i, (p, w) in enumerate(zip(parts, widths)):
        col = p.get('color', ARRAY_COLS[i % len(ARRAY_COLS)])
        rect = mpatches.FancyBboxPatch((x, y_parts), w, bar_h,
            boxstyle='square,pad=0.02', linewidth=1.5,
            edgecolor='#333', facecolor=col)
        ax.add_patch(rect)
        # 'display' overrides 'value' for what is shown inside the bar
        pv = p.get('display', p.get('value', '?'))
        ax.text(x + w/2, y_parts + bar_h/2, str(pv),
                ha='center', va='center', fontsize=13, fontweight='bold', color='white')
        pl = p.get('label', '')
        if pl:
            ax.text(x + w/2, y_parts - 0.25, pl,
                    ha='center', va='top', fontsize=9, color=DARK)
        x += w

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _bar_model_comparison(spec, path, dpi):
    bars = spec.get('bars', [
        {'value': 24, 'label': 'Amy', 'color': SHAPE_A},
        {'value': 18, 'label': 'Ben', 'color': SHAPE_B},
    ])
    show_diff = spec.get('show_difference', True)

    vals = []
    for b in bars:
        try: vals.append(float(str(b.get('value','0')).replace('?','0')))
        except: vals.append(0)
    max_v = max(vals) or 1
    max_w = 7.0
    bar_h = 0.55
    gap   = 0.35

    n = len(bars)
    fig_h = n * (bar_h + gap) + 1.2
    fig, ax = plt.subplots(figsize=(9, fig_h))
    ax.set_xlim(-1.5, max_w + 1.0)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    for i, (b, v) in enumerate(zip(bars, vals)):
        y = fig_h - 0.6 - (i + 1) * (bar_h + gap)
        w = max_w * v / max_v
        col = b.get('color', ARRAY_COLS[i % len(ARRAY_COLS)])
        rect = mpatches.FancyBboxPatch((0, y), w, bar_h,
            boxstyle='square,pad=0.02', linewidth=1.5,
            edgecolor='#333', facecolor=col)
        ax.add_patch(rect)
        bv = b.get('value', '?')
        ax.text(w + 0.12, y + bar_h/2, str(bv),
                ha='left', va='center', fontsize=12, fontweight='bold', color=col)
        bl = b.get('label', '')
        if bl:
            ax.text(-0.12, y + bar_h/2, bl,
                    ha='right', va='center', fontsize=11, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _bar_model_fraction_of(spec, path, dpi):
    total  = spec.get('total_parts', 5)
    shaded = spec.get('shaded_parts', 2)
    total_v = spec.get('total_value', '?')
    shade_c = spec.get('shade_color', SHAPE_A)

    bar_w = 7.0
    bar_h = 0.8
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.set_xlim(-0.2, bar_w + 1.5)
    ax.set_ylim(0, 2.5)
    ax.axis('off')

    part_w = bar_w / total
    y = 1.0

    for i in range(total):
        col = shade_c if i < shaded else LIGHT_GREY
        ec  = '#333'
        rect = mpatches.FancyBboxPatch((i * part_w, y), part_w, bar_h,
            boxstyle='square,pad=0.02', linewidth=1.5,
            edgecolor=ec, facecolor=col)
        ax.add_patch(rect)
        # Value label in each section
        part_val = spec.get('part_value', '?')
        ax.text(i * part_w + part_w/2, y + bar_h/2, str(part_val),
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='white' if i < shaded else MID_GREY)

    # Total label
    ax.text(bar_w + 0.15, y + bar_h/2, f'= {total_v}',
            ha='left', va='center', fontsize=13, fontweight='bold', color=DARK)

    # Fraction annotation
    frac_txt = f'{shaded}/{total}'
    ax.text(shaded * part_w / 2, y - 0.25, f'← {frac_txt} →',
            ha='center', va='top', fontsize=10, color=shade_c, fontstyle='italic')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _bar_model_ratio(spec, path, dpi):
    groups = spec.get('groups', [
        {'count': 2, 'label': 'A', 'color': SHAPE_A},
        {'count': 3, 'label': 'B', 'color': SHAPE_B},
    ])
    unit_w  = 0.7
    bar_h   = 0.65
    gap     = 0.08
    total_u = sum(g.get('count', 1) for g in groups)

    fig_w = total_u * (unit_w + gap) + 1
    fig, ax = plt.subplots(figsize=(max(fig_w, 4), 2.2))
    ax.set_xlim(-0.2, fig_w)
    ax.set_ylim(0, 2.2)
    ax.axis('off')

    x = 0
    y = 0.8
    for g in groups:
        cnt = g.get('count', 1)
        col = g.get('color', SHAPE_A)
        gl  = g.get('label', '')
        grp_start = x
        for _ in range(cnt):
            rect = mpatches.FancyBboxPatch((x, y), unit_w, bar_h,
                boxstyle='square,pad=0.02', linewidth=1.5,
                edgecolor='#333', facecolor=col)
            ax.add_patch(rect)
            x += unit_w + gap
        # Group label below
        grp_mid = grp_start + cnt * (unit_w + gap) / 2
        if gl:
            ax.text(grp_mid, y - 0.25, gl,
                    ha='center', va='top', fontsize=11, color=col, fontweight='bold')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ARRAY
# ═══════════════════════════════════════════════════════════════════════════════

def _array(spec, path, dpi):
    """
    Spec:
        rows:          int — number of rows
        groups:        list of {cols, color} — column groups per row
                       e.g. [{'cols':3,'color':'#4A90D9'}, {'cols':3,'color':'#E8A030'}]
                       If single colour: [{'cols':6, 'color':'#4A90D9'}]
        show_row_borders: bool — border around each row (default True)
        circle_radius:    float — override auto circle size
        labels:        {rows_label, cols_label} — optional axis labels
    """
    n_rows     = spec.get('rows', 3)
    groups     = spec.get('groups', [{'cols': 4, 'color': ARRAY_COLS[0]}])
    show_rb    = spec.get('show_row_borders', True)
    labels_d   = spec.get('labels', {})

    total_cols = sum(g.get('cols', 1) for g in groups)
    r_max      = 0.32
    r = min(r_max, 4.0 / max(total_cols, 1), 3.0 / max(n_rows, 1))
    gap_c = r * 0.5
    gap_r = r * 0.45
    pad   = r * 1.2

    row_w = total_cols * (2*r + gap_c) - gap_c + 2 * pad
    row_h_single = 2*r + gap_r + (r * 1.0 if show_rb else 0)
    fig_w = row_w + 0.3
    fig_h = n_rows * row_h_single + 0.4

    fig, ax = plt.subplots(figsize=(min(fig_w, 10), min(fig_h, 8)))
    ax.set_aspect('equal')
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    y = fig_h - 0.2
    for ri in range(n_rows):
        row_top    = y
        rb_pad     = r * 0.45
        row_bottom = y - 2*r - gap_r - (rb_pad if show_rb else 0)
        row_h_vis  = row_top - row_bottom

        if show_rb:
            rect = mpatches.FancyBboxPatch(
                (0.12, row_bottom),
                row_w - 0.12,
                row_h_vis,
                boxstyle='round,pad=0.04',
                linewidth=1.8, edgecolor='#C83030',
                facecolor='#FFF0F0')
            ax.add_patch(rect)

        # Circle centre: vertically centred in the row
        cy = row_bottom + row_h_vis / 2

        x = pad
        for g in groups:
            n_cols = g.get('cols', 1)
            col    = g.get('color', ARRAY_COLS[0])
            for ci in range(n_cols):
                cx = x + ci * (2*r + gap_c) + r
                circle = plt.Circle((cx, cy), r,
                    facecolor=col, edgecolor='#333333',
                    linewidth=0.8, zorder=3)
                ax.add_patch(circle)
            x += n_cols * (2*r + gap_c)

        y = row_bottom - gap_r * 0.4

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. WHICH ANSWER (multi-calculation comparison)
# ═══════════════════════════════════════════════════════════════════════════════

def _which_answer(spec, path, dpi):
    """
    Spec:
        operation:  '+' | '-' | '÷' | '×'
        top:        str — top number
        bottom:     str — bottom number
        answers:    list of {value, regroup_marks: [col_positions], label: 'A'/'B'/'C'}
        title:      str (default 'Which Answer?')
        prompt:     str (default 'Explain the mistakes.')
    """
    op      = spec.get('operation', '+')
    top     = str(spec.get('top', '1417'))
    bottom  = str(spec.get('bottom', '738'))
    answers = spec.get('answers', [])
    title   = spec.get('title', 'Which Answer?')
    prompt  = spec.get('prompt', 'Explain the mistakes.')

    n = len(answers)
    col_w  = 2.8
    fig_w  = n * col_w + 1.0
    fig_h  = 4.5

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Title
    ax.text(fig_w/2, fig_h - 0.25, title,
            ha='center', va='top', fontsize=18, fontweight='bold', color=SHAPE_A)

    # Each answer column
    for i, ans in enumerate(answers):
        x_mid = 0.5 + i * col_w + col_w / 2
        lbl   = ans.get('label', chr(65 + i))  # A, B, C...
        val   = str(ans.get('value', '?'))
        marks = ans.get('regroup_marks', [])

        ax.text(x_mid, fig_h - 0.75, f'Answer {lbl}:',
                ha='center', va='top', fontsize=11, fontweight='bold', color=DARK)

        # Draw column calculation
        _draw_column_calc(ax, x_mid, top, bottom, val, op, marks,
                         y_top=fig_h - 1.25, font_size=16)

    # Prompt
    ax.text(0.3, 0.35, prompt,
            ha='left', va='bottom', fontsize=10, color=DARK, fontstyle='italic')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _draw_column_calc(ax, x_mid, top, bottom, answer, op, regroup_marks, y_top, font_size=16):
    """Draw a single column calculation centred on x_mid."""
    ch  = font_size / 72 * 1.35  # char height in inches
    cw  = font_size / 72 * 0.85  # char width
    lh  = ch * 1.5               # line height

    # Find max width
    max_len = max(len(top), len(bottom), len(answer))
    total_w = max_len * cw

    # operator
    ax.text(x_mid - total_w/2 - cw*0.6, y_top - lh, op,
            ha='right', va='top', fontsize=font_size, color=DARK)

    # Top number (right-aligned)
    for j, ch_top in enumerate(top):
        ax.text(x_mid - total_w/2 + (j + max_len - len(top)) * cw + cw*0.5,
                y_top, ch_top,
                ha='center', va='top', fontsize=font_size, color=DARK)

    # Bottom number
    for j, ch_bot in enumerate(bottom):
        ax.text(x_mid - total_w/2 + (j + max_len - len(bottom)) * cw + cw*0.5,
                y_top - lh, ch_bot,
                ha='center', va='top', fontsize=font_size, color=DARK)

    # Underline
    line_y = y_top - lh * 2 + ch * 0.1
    ax.plot([x_mid - total_w/2 - cw*0.8, x_mid + total_w/2 + cw*0.2],
            [line_y, line_y], color=DARK, lw=1.5)

    # Answer
    for j, ch_ans in enumerate(answer):
        ax.text(x_mid - total_w/2 + (j + max_len - len(answer)) * cw + cw*0.5,
                line_y - lh * 0.3, ch_ans,
                ha='center', va='top', fontsize=font_size, color=DARK)

    # Second underline
    line_y2 = line_y - lh * 1.5
    ax.plot([x_mid - total_w/2 - cw*0.8, x_mid + total_w/2 + cw*0.2],
            [line_y2, line_y2], color=DARK, lw=1.5)

    # Regroup marks (small subscripts below answer line)
    if regroup_marks:
        for pos in regroup_marks:
            rx = x_mid - total_w/2 + (pos + max_len - len(answer)) * cw + cw*0.5
            ax.text(rx, line_y2 - 0.05, '1',
                    ha='center', va='top', fontsize=font_size * 0.55,
                    color=DARK, fontstyle='normal')


# ═══════════════════════════════════════════════════════════════════════════════
# 9. FRACTION BAR
# ═══════════════════════════════════════════════════════════════════════════════

def _fraction_bar(spec, path, dpi):
    """
    Spec:
        denominator:  int — total parts
        numerator:    int — shaded parts
        color:        hex — shade colour (default SHAPE_A)
        show_label:   bool — fraction label below (default True)
        orientation:  'horizontal' | 'vertical' (default 'horizontal')
    """
    denom = spec.get('denominator', 4)
    numer = spec.get('numerator', 1)
    color = spec.get('color', FRACTION_BLUE)
    show_l = spec.get('show_label', True)
    orient = spec.get('orientation', 'horizontal')

    if orient == 'horizontal':
        bar_w, bar_h = 7.0, 1.0
        fig, ax = plt.subplots(figsize=(8, 2.2 if show_l else 1.8))
        ax.set_xlim(-0.2, bar_w + 0.5)
        ax.set_ylim(0, 2.2 if show_l else 1.8)
        ax.axis('off')
        part_w = bar_w / denom
        y = 0.7
        for i in range(denom):
            col = color if i < numer else LIGHT_GREY
            rect = mpatches.FancyBboxPatch((i * part_w, y), part_w, bar_h,
                boxstyle='square,pad=0', linewidth=1.5,
                edgecolor='#444', facecolor=col)
            ax.add_patch(rect)
        if show_l:
            ax.text(bar_w/2, y - 0.25, f'{numer}/{denom}',
                    ha='center', va='top', fontsize=13, color=color, fontweight='bold')
    else:
        bar_w, bar_h = 1.0, 6.0
        fig, ax = plt.subplots(figsize=(2.5, 7.0))
        ax.set_xlim(0, 2.5)
        ax.set_ylim(-0.3, bar_h + 0.5)
        ax.axis('off')
        part_h = bar_h / denom
        x = 0.75
        for i in range(denom):
            col = color if i < numer else LIGHT_GREY
            rect = mpatches.FancyBboxPatch((x, i * part_h), bar_w, part_h,
                boxstyle='square,pad=0', linewidth=1.5,
                edgecolor='#444', facecolor=col)
            ax.add_patch(rect)
        if show_l:
            ax.text(x + bar_w/2, -0.2, f'{numer}/{denom}',
                    ha='center', va='top', fontsize=13, color=color, fontweight='bold')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. EQUIVALENCE BARS
# ═══════════════════════════════════════════════════════════════════════════════

def _equivalence_bars(spec, path, dpi):
    """
    Spec:
        fractions:  list of [n, d] or 'n/d' strings
        color:      hex — shade colour (default FRACTION_BLUE)
        equivalent: bool — fractions are equivalent (default True)
                    if False, bars may differ in shaded proportion
    """
    fracs = spec.get('fractions', [[1,2],[2,4],[3,6]])
    color = spec.get('color', FRACTION_BLUE)

    parsed = []
    for f in fracs:
        if isinstance(f, str):
            n, d = map(int, f.split('/'))
        else:
            n, d = f[0], f[1]
        parsed.append((n, d))

    n_bars = len(parsed)
    bar_w  = 7.0
    bar_h  = 0.65
    gap    = 0.35
    label_w = 1.2

    fig_h = n_bars * (bar_h + gap) + 0.6
    fig, ax = plt.subplots(figsize=(bar_w + label_w + 0.8, fig_h))
    ax.set_xlim(-label_w - 0.2, bar_w + 0.4)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    for i, (n, d) in enumerate(parsed):
        y = fig_h - 0.35 - (i + 1) * (bar_h + gap)
        part_w = bar_w / d
        for j in range(d):
            col = color if j < n else LIGHT_GREY
            rect = mpatches.FancyBboxPatch((j * part_w, y), part_w, bar_h,
                boxstyle='square,pad=0', linewidth=1.2,
                edgecolor='#555', facecolor=col)
            ax.add_patch(rect)
        # Fraction label on left
        ax.text(-0.15, y + bar_h/2, f'{n}/{d}',
                ha='right', va='center', fontsize=13,
                fontweight='bold', color=color)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 11. EQUIVALENCE ARROWS
# ═══════════════════════════════════════════════════════════════════════════════

def _equivalence_arrows(spec, path, dpi):
    """
    Spec:
        fraction1:  [n, d]
        fraction2:  [n, d]
        operation:  '÷' | '×'
        factor:     int
    """
    f1  = spec.get('fraction1', [8, 12])
    f2  = spec.get('fraction2', [2, 3])
    op  = spec.get('operation', '÷')
    fac = spec.get('factor', 4)

    n1, d1 = f1
    n2, d2 = f2
    op_label = f'{op}{fac}'

    fig, ax = plt.subplots(figsize=(5.5, 4.0))
    ax.set_xlim(0, 5.5)
    ax.set_ylim(0.3, 4.0)
    ax.axis('off')

    # Fraction 1
    cx1 = 1.2
    n1_y, d1_y = 2.7, 1.9
    ax.text(cx1, n1_y, str(n1), ha='center', va='bottom',
            fontsize=26, fontweight='bold', color=DARK)
    ax.plot([cx1-0.38, cx1+0.38], [n1_y-0.05, n1_y-0.05], color=DARK, lw=2.5)
    ax.text(cx1, d1_y, str(d1), ha='center', va='top',
            fontsize=26, fontweight='bold', color=DARK)

    # = sign
    ax.text(2.75, 2.3, '=', ha='center', va='center', fontsize=22, color=DARK)

    # Fraction 2
    cx2 = 4.3
    n2_y, d2_y = 2.7, 1.9
    ax.text(cx2, n2_y, str(n2), ha='center', va='bottom',
            fontsize=26, fontweight='bold', color=DARK)
    ax.plot([cx2-0.38, cx2+0.38], [n2_y-0.05, n2_y-0.05], color=DARK, lw=2.5)
    ax.text(cx2, d2_y, str(d2), ha='center', va='top',
            fontsize=26, fontweight='bold', color=DARK)

    arrow_col = SHAPE_B
    mid_x = (cx1 + cx2) / 2   # 2.75
    bow   = 0.55               # arc bow height

    def _bezier_arc_with_label(ax, x0, y0, x1, y1, bow_y, label,
                                label_above, col):
        """Quadratic bezier arc. Control point: (mid_x, (y0+y1)/2 + bow_y)."""
        t    = np.linspace(0, 1, 100)
        mid_y = (y0 + y1) / 2 + bow_y
        px   = (1-t)**2 * x0 + 2*t*(1-t) * ((x0+x1)/2) + t**2 * x1
        py   = (1-t)**2 * y0 + 2*t*(1-t) * mid_y + t**2 * y1
        cut  = 10
        ax.plot(px[:-cut], py[:-cut], color=col, lw=2.2, solid_capstyle='round')
        ax.annotate('',
                    xy=(px[-1], py[-1]),
                    xytext=(px[-cut-2], py[-cut-2]),
                    arrowprops=dict(arrowstyle='->', color=col, lw=2.2,
                                   mutation_scale=14))
        # Label sits at the peak of the arc
        apex_y = mid_y   # for equal start/end y, peak = control point y
        gap = 0.18
        label_y = apex_y + gap if label_above else apex_y - gap
        ax.text(mid_x, label_y, label,
                ha='center', va='bottom' if label_above else 'top',
                fontsize=13, fontweight='bold', color=col)

    # Top arc: just above the numerator, bows UPWARD
    top_y = n1_y + 0.08
    _bezier_arc_with_label(ax,
        cx1 + 0.35, top_y,
        cx2 - 0.35, top_y,
        bow, op_label, label_above=True, col=arrow_col)

    # Bottom arc: just below the denominator, bows DOWNWARD
    bot_y = d1_y - 0.22
    _bezier_arc_with_label(ax,
        cx1 + 0.35, bot_y,
        cx2 - 0.35, bot_y,
        -bow, op_label, label_above=False, col=arrow_col)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 12. HUNDRED SQUARE & TEN STRIP
# ═══════════════════════════════════════════════════════════════════════════════

def _hundred_square(spec, path, dpi):
    """
    Spec:
        shaded:   int (0–100) — number of cells shaded
        color:    hex — shade colour (default FRACTION_ORANGE)
        shade_by: 'columns' (fill column by column) | 'cells' (fill left-to-right row by row)
        label:    str — optional label below (e.g. '0.47' or '47%')
    """
    shaded  = spec.get('shaded', 40)
    color   = spec.get('color', FRACTION_ORANGE)
    by      = spec.get('shade_by', 'columns')
    label   = spec.get('label', None)

    cell = 0.52   # slightly larger cells for clarity
    n    = 10
    pad  = 0.12
    lbl_h = 0.5 if label else 0
    fig_w = n * cell + 2 * pad
    fig_h = n * cell + 2 * pad + lbl_h

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    grid_y0 = lbl_h + pad   # grid starts above label area

    def is_shaded(row, col):
        if by == 'columns':
            full_cols = shaded // 10
            rem = shaded % 10
            if col < full_cols:
                return True
            if col == full_cols and row < rem:
                return True
            return False
        else:
            idx = row * 10 + col
            return idx < shaded

    for row in range(n):
        for col in range(n):
            x = pad + col * cell
            y = grid_y0 + (n - 1 - row) * cell
            fc = color if is_shaded(row, col) else WHITE
            rect = plt.Rectangle((x, y), cell, cell,
                                  facecolor=fc, edgecolor='#999', linewidth=0.7)
            ax.add_patch(rect)

    if label:
        ax.text(fig_w/2, lbl_h / 2, label,
                ha='center', va='center', fontsize=14,
                fontweight='bold', color=color)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _ten_strip(spec, path, dpi):
    """
    Spec:
        shaded:  int (0–10)
        color:   hex
        label:   str
    """
    shaded = spec.get('shaded', 4)
    color  = spec.get('color', FRACTION_ORANGE)
    label  = spec.get('label', None)

    cell_w, cell_h = 0.65, 0.65
    pad = 0.1
    fig, ax = plt.subplots(figsize=(10 * cell_w + 2*pad, cell_h + 2*pad + (0.4 if label else 0)))
    ax.set_xlim(0, 10 * cell_w + 2*pad)
    ax.set_ylim(0, cell_h + 2*pad + (0.4 if label else 0))
    ax.axis('off')

    y = (0.4 if label else 0) + pad
    for i in range(10):
        x = pad + i * cell_w
        fc = color if i < shaded else WHITE
        rect = plt.Rectangle((x, y), cell_w, cell_h,
                              facecolor=fc, edgecolor='#888', linewidth=1.0)
        ax.add_patch(rect)

    if label:
        ax.text(10*cell_w/2 + pad, 0.05, label,
                ha='center', va='bottom', fontsize=11,
                fontweight='bold', color=color)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 13. FRACTION NUMBER LINE
# ═══════════════════════════════════════════════════════════════════════════════

def _fraction_number_line(spec, path, dpi):
    """
    Spec:
        start:       int (default 0)
        end:         int (default 1)
        denominator: int — divisions per unit (default 4)
        x_marker:    float — position of X marker
        labelled:    list of fractions to label explicitly e.g. ['1/2', '1/4']
        show_all_labels: bool (default False) — label every tick
    """
    start  = spec.get('start', 0)
    end    = spec.get('end', 1)
    denom  = spec.get('denominator', 4)
    x_mk   = spec.get('x_marker', None)
    labelled = spec.get('labelled', [])
    show_all = spec.get('show_all_labels', False)

    fig, ax = plt.subplots(figsize=(8, 1.8))
    ax.set_xlim(start - 0.08, end + 0.08)
    ax.set_ylim(-0.6, 0.8)
    ax.axis('off')

    # Main line with arrows
    ax.annotate('', xy=(end + 0.06, 0), xytext=(start - 0.06, 0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2.0))

    total_ticks = (end - start) * denom
    for i in range(int(total_ticks) + 1):
        v = start + i / denom
        is_whole = (i % denom == 0)
        tick_h = 0.14 if is_whole else 0.09
        ax.plot([v, v], [-tick_h, tick_h], color=DARK, lw=1.5 if is_whole else 1.0)

        # Label
        if is_whole:
            ax.text(v, -0.22, str(int(v)), ha='center', va='top', fontsize=11, color=DARK)
        elif show_all or (i % denom in [denom//2, denom//4, 3*denom//4] and i != 0):
            # Show half and quarter marks by default
            n_part = i % denom
            d_part = denom
            from math import gcd
            g = gcd(n_part, d_part)
            n_s, d_s = n_part//g, d_part//g
            unit = i // denom
            if unit > 0:
                frac_str = f'{unit} {n_s}/{d_s}'
            else:
                frac_str = f'{n_s}/{d_s}'
            if frac_str in labelled or show_all:
                ax.text(v, -0.22, frac_str, ha='center', va='top', fontsize=9, color=DARK)

    # X marker
    if x_mk is not None:
        ax.plot([x_mk, x_mk], [-0.16, 0.16], color=DARK, lw=1.5)
        s = 0.025
        ax.plot([x_mk-s, x_mk+s], [0.2, 0.35], color='#C08000', lw=2.5)
        ax.plot([x_mk+s, x_mk-s], [0.2, 0.35], color='#C08000', lw=2.5)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 14. FRACTION OF A SHAPE
# ═══════════════════════════════════════════════════════════════════════════════

def _fraction_shape(spec, path, dpi):
    """
    Spec:
        shape_type:  'bar' | 'circle' | 'grid' | 'L_shape' | 'triangle'
        denominator: int
        numerator:   int
        color:       hex
        show_label:  bool
    """
    st    = spec.get('shape_type', 'bar')
    denom = spec.get('denominator', 4)
    numer = spec.get('numerator', 1)
    color = spec.get('color', FRACTION_BLUE)
    show_l = spec.get('show_label', True)

    if st == 'bar':
        return _fraction_bar({'denominator': denom, 'numerator': numer,
                              'color': color, 'show_label': show_l}, path, dpi)
    elif st == 'circle':
        return _fraction_circle(denom, numer, color, show_l, path, dpi)
    elif st == 'grid':
        return _fraction_grid(denom, numer, color, show_l, path, dpi)
    elif st == 'triangle':
        return _fraction_triangle(denom, numer, color, show_l, path, dpi)
    else:
        return _fraction_bar({'denominator': denom, 'numerator': numer,
                              'color': color, 'show_label': show_l}, path, dpi)


def _fraction_circle(denom, numer, color, show_l, path, dpi):
    fig, ax = plt.subplots(figsize=(3.0, 3.2 if show_l else 3.0))
    ax.set_aspect('equal')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.4 if show_l else -1.2, 1.2)
    ax.axis('off')
    theta_start = 90  # start from top
    angle_each  = 360 / denom
    for i in range(denom):
        t1 = theta_start - i * angle_each
        t2 = t1 - angle_each
        wedge = Wedge((0, 0), 1.0, t2, t1,
                      facecolor=color if i < numer else LIGHT_GREY,
                      edgecolor='#444', linewidth=1.5)
        ax.add_patch(wedge)
    if show_l:
        ax.text(0, -1.25, f'{numer}/{denom}',
                ha='center', va='top', fontsize=12, fontweight='bold', color=color)
    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _fraction_grid(denom, numer, color, show_l, path, dpi):
    # Find best grid layout
    cols = math.ceil(math.sqrt(denom))
    rows = math.ceil(denom / cols)
    cell = 0.7
    fig, ax = plt.subplots(figsize=(cols * cell + 0.4, rows * cell + (0.5 if show_l else 0.2)))
    ax.set_xlim(0, cols * cell + 0.2)
    ax.set_ylim(0, rows * cell + 0.2 + (0.5 if show_l else 0))
    ax.axis('off')
    for i in range(denom):
        r = i // cols
        c = i % cols
        x = 0.1 + c * cell
        y = (0.5 if show_l else 0.1) + (rows - 1 - r) * cell
        fc = color if i < numer else LIGHT_GREY
        rect = plt.Rectangle((x, y), cell - 0.05, cell - 0.05,
                              facecolor=fc, edgecolor='#444', linewidth=1.2)
        ax.add_patch(rect)
    if show_l:
        ax.text(cols * cell / 2 + 0.1, 0.1,
                f'{numer}/{denom}', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=color)
    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _fraction_triangle(denom, numer, color, show_l, path, dpi):
    """Equilateral triangle divided into denom rows."""
    fig, ax = plt.subplots(figsize=(3.5, 3.2))
    ax.set_aspect('equal')
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.0)
    ax.axis('off')
    # Divide into horizontal strips
    h_total = math.sqrt(3) / 2
    for i in range(denom):
        y1 = h_total * i / denom
        y2 = h_total * (i + 1) / denom
        x1_bot = 0.5 - (y1 / h_total) * 0.5
        x2_bot = 0.5 + (y1 / h_total) * 0.5
        x1_top = 0.5 - (y2 / h_total) * 0.5
        x2_top = 0.5 + (y2 / h_total) * 0.5
        pts = np.array([[x1_bot, y1], [x2_bot, y1], [x2_top, y2], [x1_top, y2]])
        poly = plt.Polygon(pts, facecolor=color if i < numer else LIGHT_GREY,
                           edgecolor='#444', linewidth=1.2)
        ax.add_patch(poly)
    if show_l:
        ax.text(0.5, -0.05, f'{numer}/{denom}',
                ha='center', va='top', fontsize=12, fontweight='bold', color=color)
    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 15. FRACTION OF A SET
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_fraction_circle(ax, cx, cy, r, d, shaded, color):
    """Circle divided into d equal sectors, 'shaded' sectors filled."""
    from matplotlib.patches import Wedge as _Wedge
    sector = 360.0 / d
    for i in range(d):
        t2 = 90.0 - i * sector
        t1 = t2 - sector
        fc = color if i < shaded else '#F0F0F0'
        ax.add_patch(_Wedge((cx, cy), r, t1, t2,
                             facecolor=fc, edgecolor='#2A2A2A', lw=1.4, zorder=2))
    # Bold outer ring
    ax.add_patch(plt.Circle((cx, cy), r, fill=False,
                             edgecolor='#2A2A2A', lw=2.0, zorder=3))


def _fraction_circles(spec, path, dpi):
    """
    Show a quantity n/d as a row of circles — each circle divided into d
    equal sectors. The first whole_count circles are fully shaded; the last
    circle (if there is a remainder) is partially shaded. Ideal for teaching
    mixed numbers ↔ improper fractions.

    Spec:
        denominator   int        parts per circle (d)
        total         int        total parts (numerator of improper fraction)
        color         str        hex fill colour for shaded sectors
        show_labels   bool       label each circle below (e.g. '4/4', '3/4') — default True
        total_label   str        text after the circles (e.g. '= 11 quarters') — optional
        max_per_row   int        wrap into rows if more circles than this — default 6

    Example — 2¾ = 11 quarters:
        {'type': 'fraction_circles', 'denominator': 4, 'total': 11, 'color': '#2565AE',
         'total_label': '= 11 quarters'}
    """
    d           = spec.get('denominator', 4)
    total       = spec.get('total', d)
    color       = spec.get('color', SHAPE_A)
    show_labels = spec.get('show_labels', True)
    total_label = spec.get('total_label', '')
    max_per_row = spec.get('max_per_row', 6)

    wholes    = total // d
    remainder = total % d
    n_circles = wholes + (1 if remainder > 0 else 0)

    # Layout
    r      = 0.55
    gap    = 0.32
    row_h  = 2 * r + (0.38 if show_labels else 0.1) + gap
    n_rows = max(1, -(-n_circles // max_per_row))  # ceil division
    per_row = min(n_circles, max_per_row)

    extra_w = 1.4 if total_label else 0.3
    fig_w   = per_row * (2*r + gap) + extra_w
    fig_h   = n_rows * row_h + 0.2

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    for ci in range(n_circles):
        row = ci // max_per_row
        col = ci % max_per_row
        cx  = (gap/2 + r) + col * (2*r + gap)
        cy  = fig_h - (gap/2 + r) - row * row_h

        shaded = d if ci < wholes else remainder
        _draw_fraction_circle(ax, cx, cy, r, d, shaded, color)

        if show_labels:
            lbl = f'{shaded}/{d}'
            ax.text(cx, cy - r - 0.10, lbl,
                    ha='center', va='top', fontsize=10, color=DARK)

    # Total label after last circle in last row
    if total_label:
        last_col   = (n_circles - 1) % max_per_row
        last_cx    = (gap/2 + r) + last_col * (2*r + gap)
        last_row   = (n_circles - 1) // max_per_row
        label_cy   = fig_h - (gap/2 + r) - last_row * row_h
        ax.text(last_cx + r + 0.20, label_cy, total_label,
                ha='left', va='center', fontsize=12,
                fontweight='bold', color=DARK)

    return _save(fig, path, dpi)


def _fraction_set(spec, path, dpi):
    """
    Spec:
        items:      list of {shape, color} — 'square','rectangle','triangle','circle'
        questions:  list of str — questions to display below
    """
    items     = spec.get('items', [
        {'shape': 'square', 'color': '#4A90D9'},
        {'shape': 'rectangle', 'color': '#E8A030'},
        {'shape': 'square', 'color': '#C83060'},
        {'shape': 'triangle', 'color': '#2EA050'},
    ])
    questions = spec.get('questions', [])

    n = len(items)
    item_w = 0.55
    q_h    = 0.45
    fig_w  = max(n * (item_w + 0.12) + 0.5, 6)
    fig_h  = 1.4 + len(questions) * q_h + 0.3

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Draw items
    x = 0.3
    y_items = fig_h - 1.0
    for item in items:
        _draw_set_item(ax, x, y_items, item_w, item)
        x += item_w + 0.15

    # Questions
    for qi, q in enumerate(questions):
        y_q = fig_h - 1.6 - qi * q_h
        ax.text(0.3, y_q, q, ha='left', va='top', fontsize=10, color=DARK)
        # Answer box
        ax.add_patch(plt.Rectangle((fig_w - 0.9, y_q - 0.35), 0.7, 0.38,
                                    facecolor=WHITE, edgecolor='#888', lw=1.2))

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _draw_set_item(ax, x, y, size, item):
    shape = item.get('shape', 'square')
    color = item.get('color', SHAPE_A)
    if shape in ('square',):
        rect = plt.Rectangle((x, y), size, size,
                              facecolor=color, edgecolor='#333', lw=1.2)
        ax.add_patch(rect)
    elif shape == 'rectangle':
        rect = plt.Rectangle((x, y + size*0.15), size, size * 0.65,
                              facecolor=color, edgecolor='#333', lw=1.2)
        ax.add_patch(rect)
    elif shape == 'triangle':
        pts = np.array([[x, y], [x + size, y], [x + size/2, y + size]])
        poly = plt.Polygon(pts, facecolor=color, edgecolor='#333', lw=1.2)
        ax.add_patch(poly)
    elif shape == 'circle':
        c = plt.Circle((x + size/2, y + size/2), size/2,
                       facecolor=color, edgecolor='#333', lw=1.2)
        ax.add_patch(c)


# ═══════════════════════════════════════════════════════════════════════════════
# 16. COORDINATE GRID (single and four-quadrant)
# ═══════════════════════════════════════════════════════════════════════════════

def _coordinate_grid(spec, path, dpi):
    """
    Spec:
        x_range:  [min, max]  e.g. [0, 5] or [-4, 4]
        y_range:  [min, max]
        shapes:   list of {vertices:[(x,y),...], color, label, fill, fill_color}
        points:   list of {coord:(x,y), label, color}
        show_axes_labels: bool (default True)
        grid_style: 'lined' | 'dotted' (default 'lined')
        title:    str
    """
    xr      = spec.get('x_range', [0, 5])
    yr      = spec.get('y_range', [0, 5])
    shapes  = spec.get('shapes', [])
    points  = spec.get('points', [])
    show_ax = spec.get('show_axes_labels', True)
    title   = spec.get('title', '')

    x_min, x_max = xr
    y_min, y_max = yr
    x_range = x_max - x_min
    y_range = y_max - y_min

    # Figure size: aim for square cells, max 8 inches
    cell_size = min(8.0 / max(x_range, 1), 7.0 / max(y_range, 1), 0.7)
    fig_w = x_range * cell_size + 1.4
    fig_h = y_range * cell_size + 1.2

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(x_min - 0.5, x_max + 0.5)
    ax.set_ylim(y_min - 0.5, y_max + 0.5)
    ax.set_aspect('equal')

    # Grid
    for x in range(int(x_min), int(x_max) + 1):
        ax.axvline(x, color=LIGHT_GREY, lw=0.7, zorder=1)
    for y in range(int(y_min), int(y_max) + 1):
        ax.axhline(y, color=LIGHT_GREY, lw=0.7, zorder=1)

    # Axes
    ax.axhline(0, color='#333333', lw=1.5, zorder=2)
    ax.axvline(0, color='#333333', lw=1.5, zorder=2)

    # Axis arrows
    ax.annotate('', xy=(x_max + 0.35, 0), xytext=(x_max + 0.05, 0),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))
    ax.annotate('', xy=(0, y_max + 0.35), xytext=(0, y_max + 0.05),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))

    # Tick labels — always adjacent to the axes (y=0, x=0), not at grid edges
    tick_offset = (x_max - x_min) * 0.028

    for x in range(int(x_min), int(x_max) + 1):
        if x != 0:
            ax.text(x, -tick_offset, str(x),
                    ha='center', va='top', fontsize=9, color=DARK)
    for y in range(int(y_min), int(y_max) + 1):
        if y != 0:
            ax.text(-tick_offset, y, str(y),
                    ha='right', va='center', fontsize=9, color=DARK)
    # Origin
    ax.text(-tick_offset * 0.8, -tick_offset * 0.8, '0',
            ha='right', va='top', fontsize=9, color=DARK)

    # Axis labels
    if show_ax:
        ax.text(x_max + 0.45, -0.05, 'x', ha='left', va='top',
                fontsize=12, fontstyle='italic', color=DARK)
        ax.text(0.08, y_max + 0.42, 'y', ha='left', va='bottom',
                fontsize=12, fontstyle='italic', color=DARK)

    # Shapes
    for sh in shapes:
        verts = sh.get('vertices', [])
        if not verts:
            continue
        fill_c = sh.get('fill_color', SHAPE_A)
        fill   = sh.get('fill', True)
        alpha  = sh.get('alpha', 0.35)
        ec     = sh.get('color', SHAPE_A)
        lbl    = sh.get('label', '')

        pts = np.array(verts)
        poly = plt.Polygon(pts, facecolor=fill_c if fill else 'none',
                           edgecolor=ec, linewidth=2.0, alpha=alpha if fill else 1.0,
                           zorder=3)
        ax.add_patch(poly)
        if fill:
            # Solid outline on top
            poly2 = plt.Polygon(pts, facecolor='none',
                               edgecolor=ec, linewidth=2.0, zorder=4)
            ax.add_patch(poly2)

        if lbl:
            cx = np.mean([v[0] for v in verts])
            cy = np.mean([v[1] for v in verts])
            ax.text(cx, cy, lbl, ha='center', va='center',
                    fontsize=10, fontweight='bold', color=ec, zorder=5)

    # Points
    for pt in points:
        coord = pt.get('coord', (0, 0))
        lbl   = pt.get('label', '')
        col   = pt.get('color', SHAPE_A)
        ax.plot(coord[0], coord[1], 'o', color=col, markersize=8, zorder=6)
        if lbl:
            ax.text(coord[0] + 0.15, coord[1] + 0.15, lbl,
                    ha='left', va='bottom', fontsize=10,
                    fontweight='bold', color=col, zorder=7)

    if title:
        ax.set_title(title, fontsize=11, pad=6)

    ax.axis('off')
    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 17. ANGLE FIGURES
# ═══════════════════════════════════════════════════════════════════════════════

def _angle_figure(spec, path, dpi):
    """
    Spec:
        angle_degrees:  float
        orientation:    float — rotation of the whole figure (degrees, default 0)
        show_arc:       bool (default True)
        label:          str — number/letter label beside figure
        arm_length:     float (default 1.2)
    """
    deg     = spec.get('angle_degrees', 60)
    orient  = spec.get('orientation', 0)
    show_arc = spec.get('show_arc', True)
    lbl     = spec.get('label', '')
    arm_l   = spec.get('arm_length', 1.2)

    fig, ax = plt.subplots(figsize=(2.8, 2.4))
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')

    # Rotate orientation: base arm goes in direction 'orient'
    base_angle = math.radians(orient)
    second_angle = math.radians(orient + deg)

    # Vertex at origin
    vx, vy = 0.0, 0.0
    # First arm
    ax.plot([vx, vx + arm_l * math.cos(base_angle)],
            [vy, vy + arm_l * math.sin(base_angle)],
            color=SHAPE_A, lw=2.8, solid_capstyle='round')
    # Second arm
    ax.plot([vx, vx + arm_l * math.cos(second_angle)],
            [vy, vy + arm_l * math.sin(second_angle)],
            color=SHAPE_A, lw=2.8, solid_capstyle='round')

    # Arc
    if show_arc:
        arc_r = 0.35
        if abs(deg - 90) < 1:
            # Right angle square
            sq = arc_r * 0.6
            ca, sa = math.cos(base_angle), math.sin(base_angle)
            ca2, sa2 = math.cos(second_angle), math.sin(second_angle)
            p1 = (vx + sq*ca, vy + sq*sa)
            p2 = (vx + sq*ca + sq*ca2, vy + sq*sa + sq*sa2)
            p3 = (vx + sq*ca2, vy + sq*sa2)
            sq_pts = [p1, p2, p3, (vx, vy)]
            square = plt.Polygon(sq_pts, facecolor='none',
                                 edgecolor=SHAPE_A, lw=1.5)
            ax.add_patch(square)
        else:
            a1 = math.degrees(base_angle)
            a2 = math.degrees(second_angle)
            arc = Arc((vx, vy), 2*arc_r, 2*arc_r,
                      angle=0, theta1=min(a1,a2), theta2=max(a1,a2),
                      color=SHAPE_A, lw=1.5)
            ax.add_patch(arc)

    if lbl:
        # Place label near vertex
        mid_angle = math.radians(orient + deg / 2 + 180)
        ax.text(vx + 0.4 * math.cos(mid_angle), vy + 0.4 * math.sin(mid_angle),
                lbl, ha='center', va='center', fontsize=14, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _angle_figure_set(spec, path, dpi):
    """
    A set of angle figures side by side on one image.
    Spec:
        angles: list of {angle_degrees, orientation, show_arc, label}
        title:  str (optional)
    """
    angles = spec.get('angles', [
        {'angle_degrees': 90,  'orientation': 0,   'show_arc': True, 'label': '1'},
        {'angle_degrees': 150, 'orientation': -10, 'show_arc': False,'label': '2'},
        {'angle_degrees': 45,  'orientation': 15,  'show_arc': True, 'label': '3'},
    ])
    title = spec.get('title', '')
    n = len(angles)
    cell = 2.2
    fig, axes = plt.subplots(1, n, figsize=(n * cell, 2.5 + (0.4 if title else 0)))

    if n == 1:
        axes = [axes]

    for ax, ang_spec in zip(axes, angles):
        deg    = ang_spec.get('angle_degrees', 60)
        orient = ang_spec.get('orientation', 0)
        show_a = ang_spec.get('show_arc', True)
        lbl    = ang_spec.get('label', '')
        arm_l  = ang_spec.get('arm_length', 1.0)

        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')

        base_angle   = math.radians(orient)
        second_angle = math.radians(orient + deg)
        vx, vy = 0.0, 0.0

        ax.plot([vx, vx + arm_l * math.cos(base_angle)],
                [vy, vy + arm_l * math.sin(base_angle)],
                color=SHAPE_A, lw=2.5)
        ax.plot([vx, vx + arm_l * math.cos(second_angle)],
                [vy, vy + arm_l * math.sin(second_angle)],
                color=SHAPE_A, lw=2.5)

        if show_a:
            arc_r = 0.32
            if abs(deg - 90) < 1:
                sq = arc_r * 0.6
                ca, sa = math.cos(base_angle), math.sin(base_angle)
                ca2, sa2 = math.cos(second_angle), math.sin(second_angle)
                p1 = (vx+sq*ca, vy+sq*sa)
                p2 = (vx+sq*ca+sq*ca2, vy+sq*sa+sq*sa2)
                p3 = (vx+sq*ca2, vy+sq*sa2)
                ax.add_patch(plt.Polygon([p1,p2,p3,(vx,vy)],
                                         facecolor='none', edgecolor=SHAPE_A, lw=1.3))
            else:
                a1 = math.degrees(base_angle)
                a2 = math.degrees(second_angle)
                ax.add_patch(Arc((vx,vy), 2*arc_r, 2*arc_r,
                                  angle=0, theta1=min(a1,a2), theta2=max(a1,a2),
                                  color=SHAPE_A, lw=1.3))

        if lbl:
            mid_a = math.radians(orient + deg/2 + 180)
            ax.text(vx + 0.42*math.cos(mid_a), vy + 0.42*math.sin(mid_a),
                    lbl, ha='center', va='center', fontsize=13, color=DARK)

    if title:
        fig.suptitle(title, fontsize=11, y=0.98)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 18. TRIANGLE WITH ANGLES
# ═══════════════════════════════════════════════════════════════════════════════

def _triangle_angles(spec, path, dpi):
    """
    Spec:
        vertices:     [(x,y), (x,y), (x,y)] — triangle corners
        known_angles: {0: 42, 1: 108} — angle at vertex index → degrees
        unknown_idx:  int — which vertex has the unknown angle (0, 1, or 2)
        show_arc:     bool (default True at unknown vertex)
        label:        str — e.g. 'a)'
    """
    verts   = spec.get('vertices', [(0, 0), (3, 0), (1, 2)])
    known   = spec.get('known_angles', {0: 42, 1: 108})
    unk_idx = spec.get('unknown_idx', 2)
    lbl     = spec.get('label', '')

    pts  = np.array(verts, dtype=float)
    xmin, xmax = pts[:,0].min(), pts[:,0].max()
    ymin, ymax = pts[:,1].min(), pts[:,1].max()
    pad = 0.8
    fig_w = max((xmax - xmin) + 2*pad, 3.5)
    fig_h = max((ymax - ymin) + 2*pad, 2.5)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw triangle
    poly = plt.Polygon(pts, facecolor=LIGHT_GREY, edgecolor=DARK,
                       linewidth=2.0, alpha=0.4)
    ax.add_patch(poly)
    poly2 = plt.Polygon(pts, facecolor='none', edgecolor=DARK, linewidth=2.0)
    ax.add_patch(poly2)

    # Angle labels and arcs
    for i in range(3):
        vx, vy = pts[i]
        # Compute interior bisector direction for placing text
        prev_v = pts[(i - 1) % 3]
        next_v = pts[(i + 1) % 3]
        d1 = prev_v - pts[i]; d1 /= np.linalg.norm(d1)
        d2 = next_v - pts[i]; d2 /= np.linalg.norm(d2)
        bisect = d1 + d2
        if np.linalg.norm(bisect) > 1e-9:
            bisect /= np.linalg.norm(bisect)
        text_offset = 0.38

        if i == unk_idx:
            # Arc indicating unknown
            arc_r = 0.25
            a1 = math.degrees(math.atan2(d1[1], d1[0]))
            a2 = math.degrees(math.atan2(d2[1], d2[0]))
            arc = Arc((vx, vy), 2*arc_r, 2*arc_r, angle=0,
                      theta1=min(a1,a2), theta2=max(a1,a2),
                      color=DARK, lw=1.3)
            ax.add_patch(arc)
        else:
            # Known angle label
            ang_val = known.get(i, '?')
            ax.text(vx + bisect[0] * text_offset,
                    vy + bisect[1] * text_offset,
                    f'{ang_val}°',
                    ha='center', va='center', fontsize=10.5, color=DARK)

    if lbl:
        ax.text(xmin - pad + 0.1, ymax + pad - 0.15, lbl,
                ha='left', va='top', fontsize=11, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)




# ═══════════════════════════════════════════════════════════════════════════════
# 19. POLYGONS (regular and irregular)
# ═══════════════════════════════════════════════════════════════════════════════

POLYGON_SIDES = {
    'triangle': 3, 'equilateral triangle': 3, 'isosceles triangle': 3,
    'scalene triangle': 3, 'right-angled triangle': 3,
    'quadrilateral': 4, 'square': 4, 'rectangle': 4,
    'rhombus': 4, 'parallelogram': 4, 'trapezium': 4, 'kite': 4,
    'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8,
    'nonagon': 9, 'decagon': 10,
}

def _polygon(spec, path, dpi):
    """
    Spec:
        name:         str — shape name e.g. 'hexagon', 'parallelogram'
        vertices:     [(x,y),...] — explicit vertices (overrides name-based generation)
        color:        hex — fill colour (default light blue)
        show_name:    bool — label shape name below (default True)
        side_labels:  list of str — label for each side (in order)
        angle_marks:  list of int — vertex indices to show right-angle or arc marks
        tick_marks:   list of lists — groups of sides with same tick marks
                      e.g. [[0,2], [1,3]] = sides 0&2 equal, sides 1&3 equal
        show_vertices: bool — label vertices A, B, C... (default False)
    """
    name       = spec.get('name', 'hexagon').lower().strip()
    vertices   = spec.get('vertices', None)
    color      = spec.get('color', '#BDD7F0')
    show_name  = spec.get('show_name', True)
    side_labels = spec.get('side_labels', [])
    angle_marks = spec.get('angle_marks', [])
    tick_marks  = spec.get('tick_marks', [])
    show_verts  = spec.get('show_vertices', False)

    if vertices is None:
        vertices = _generate_polygon_vertices(name)

    pts = np.array(vertices, dtype=float)
    xmin, xmax = pts[:,0].min(), pts[:,0].max()
    ymin, ymax = pts[:,1].min(), pts[:,1].max()
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    pad = 1.1   # extra room for exterior labels and tick marks
    fig_w = max((xmax - xmin) + 2*pad, 3.0)
    fig_h = max((ymax - ymin) + 2*pad + (0.5 if show_name else 0), 2.5)

    fig, ax = plt.subplots(figsize=(min(fig_w, 6), min(fig_h, 6)))
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad * 0.8, ymax + pad + (0.5 if show_name else 0))
    ax.set_aspect('equal')
    ax.axis('off')

    # Fill
    poly = plt.Polygon(pts, facecolor=color, edgecolor=DARK, linewidth=2.0, alpha=0.7)
    ax.add_patch(poly)
    poly2 = plt.Polygon(pts, facecolor='none', edgecolor=DARK, linewidth=2.0)
    ax.add_patch(poly2)

    n = len(pts)

    # Side labels — placed OUTSIDE the shape, with white background to clear tick marks
    for i, slbl in enumerate(side_labels):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        mid = (p1 + p2) / 2
        perp = np.array([-(p2[1]-p1[1]), p2[0]-p1[0]])
        perp = perp / max(np.linalg.norm(perp), 1e-9)
        toward_c = np.array([cx, cy]) - mid
        # Point AWAY from centre (exterior)
        if np.dot(perp, toward_c) > 0:
            perp = -perp
        offset = 0.42
        ax.text(mid[0] + perp[0]*offset, mid[1] + perp[1]*offset,
                slbl, ha='center', va='center', fontsize=9.5, color=DARK,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5,
                          boxstyle='round,pad=0.15'))

    # Tick marks (equal sides)
    tick_styles = ['|', '||', '|||']
    for ti, group in enumerate(tick_marks):
        for si in group:
            p1 = pts[si % n]
            p2 = pts[(si + 1) % n]
            mid = (p1 + p2) / 2
            direction = p2 - p1
            direction /= max(np.linalg.norm(direction), 1e-9)
            perp = np.array([-direction[1], direction[0]])
            tick_len = 0.12
            n_ticks = ti + 1
            for j in range(n_ticks):
                offset_along = (j - (n_ticks-1)/2) * 0.08
                t_start = mid + direction*offset_along - perp*tick_len
                t_end   = mid + direction*offset_along + perp*tick_len
                ax.plot([t_start[0], t_end[0]], [t_start[1], t_end[1]],
                        color=DARK, lw=1.5)

    # Angle marks
    for idx in angle_marks:
        vx, vy = pts[idx]
        prev_v = pts[(idx-1) % n]
        next_v = pts[(idx+1) % n]
        d1 = prev_v - np.array([vx,vy])
        d2 = next_v - np.array([vx,vy])
        d1n = d1 / np.linalg.norm(d1)
        d2n = d2 / np.linalg.norm(d2)
        angle = math.degrees(math.acos(min(1, max(-1, np.dot(d1n, d2n)))))
        if abs(angle - 90) < 5:
            sq = 0.15
            p1 = np.array([vx,vy]) + d1n * sq
            p2 = np.array([vx,vy]) + d1n * sq + d2n * sq
            p3 = np.array([vx,vy]) + d2n * sq
            ax.add_patch(plt.Polygon([p1,p2,p3,[vx,vy]],
                                     facecolor='none', edgecolor=DARK, lw=1.2))
        else:
            a1 = math.degrees(math.atan2(d1n[1], d1n[0]))
            a2 = math.degrees(math.atan2(d2n[1], d2n[0]))
            ax.add_patch(Arc((vx,vy), 0.32, 0.32, angle=0,
                             theta1=min(a1,a2), theta2=max(a1,a2),
                             color=DARK, lw=1.2))

    # Vertex labels
    if show_verts:
        for i, (vx, vy) in enumerate(pts):
            away = np.array([vx - cx, vy - cy])
            if np.linalg.norm(away) > 1e-9:
                away /= np.linalg.norm(away)
            ax.text(vx + away[0]*0.25, vy + away[1]*0.25,
                    chr(65 + i), ha='center', va='center',
                    fontsize=10, fontweight='bold', color=DARK)

    if show_name:
        display_name = name.title()
        ax.text(cx, ymin - 0.5, display_name,
                ha='center', va='top', fontsize=10, color=DARK, style='italic')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _generate_polygon_vertices(name):
    """Generate sensible vertices for named polygons."""
    # Regular polygons
    n_sides = POLYGON_SIDES.get(name)
    if n_sides and name not in ('square','rectangle','rhombus','parallelogram',
                                 'trapezium','kite','isosceles triangle',
                                 'scalene triangle','right-angled triangle'):
        r = 1.5
        pts = []
        for i in range(n_sides):
            a = math.radians(90 + i * 360 / n_sides)
            pts.append((r * math.cos(a), r * math.sin(a)))
        return pts

    # Specific irregular shapes
    shapes = {
        'square':              [(-1.2,-1.2),(1.2,-1.2),(1.2,1.2),(-1.2,1.2)],
        'rectangle':           [(-1.8,-1.0),(1.8,-1.0),(1.8,1.0),(-1.8,1.0)],
        'rhombus':             [(0,-1.5),(1.2,0),(0,1.5),(-1.2,0)],
        'parallelogram':       [(-1.5,-1.0),(1.0,-1.0),(1.5,1.0),(-1.0,1.0)],
        'trapezium':           [(-1.8,-1.0),(1.8,-1.0),(1.2,1.0),(-1.2,1.0)],
        'kite':                [(0,-1.8),(1.2,0),(0,1.0),(-1.2,0)],
        'isosceles triangle':  [(-1.4,-1.0),(1.4,-1.0),(0,1.5)],
        'scalene triangle':    [(-1.5,-1.0),(1.8,-1.0),(0.4,1.5)],
        'right-angled triangle':[(-1.5,-1.0),(1.5,-1.0),(-1.5,1.5)],
    }
    # Fix the minus sign issue
    shapes['right-angled triangle'] = [(-1.5, -1.0), (1.5, -1.0), (-1.5, 1.5)]
    return shapes.get(name, shapes['square'])


# ═══════════════════════════════════════════════════════════════════════════════
# 20. 3D SHAPES — ISOMETRIC
# ═══════════════════════════════════════════════════════════════════════════════

def _shape_3d_iso(spec, path, dpi):
    shape = spec.get('shape', 'cube').lower().replace(' ', '_')
    color = spec.get('color', '#4A90D9')
    lbl   = spec.get('label', '')
    dims  = spec.get('dimensions', {})

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    ax.set_aspect('equal')
    ax.axis('off')

    draw_fn = {
        'cube':             _iso_cube,
        'cuboid':           _iso_cuboid,
        'cylinder':         _iso_cylinder,
        'cone':             _iso_cone,
        'sphere':           _iso_sphere,
        'triangular_prism': _iso_triangular_prism,
        'square_pyramid':   _iso_square_pyramid,
    }.get(shape, _iso_cube)

    draw_fn(ax, color, dims)

    # Auto-fit after drawing — with small label margin
    ax.autoscale_view()
    xl = ax.get_xlim(); yl = ax.get_ylim()
    xpad = (xl[1]-xl[0]) * 0.12
    ypad = (yl[1]-yl[0]) * 0.12
    ax.set_xlim(xl[0]-xpad, xl[1]+xpad)
    ax.set_ylim(yl[0]-ypad, yl[1] + ypad + (0.18 if lbl else 0))

    if lbl:
        ax.text((xl[0]+xl[1])/2, yl[0] - ypad * 0.5, lbl,
                ha='center', va='top',
                fontsize=11, color=DARK, style='italic')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def _darken(hex_color, factor=0.6):
    r, g, b = _hex_to_rgb(hex_color)
    return (r*factor, g*factor, b*factor)

def _lighten(hex_color, factor=1.4):
    r, g, b = _hex_to_rgb(hex_color)
    return (min(1, r*factor), min(1, g*factor), min(1, b*factor))

def _iso_cube(ax, color, dims):
    """Proper isometric cube using 30° projection."""
    s = dims.get('w', 1.0)
    c30 = math.cos(math.radians(30))   # √3/2 ≈ 0.866
    s30 = math.sin(math.radians(30))   # 0.5

    # 7 vertices of the visible isometric cube
    # BF = bottom-front (lowest visible point, viewer-facing)
    BF = np.array([ 0.0,          0.0         ])
    BL = np.array([-s * c30,      s * s30     ])
    BR = np.array([ s * c30,      s * s30     ])
    TF = np.array([ 0.0,          s           ])   # inner top vertex
    TL = np.array([-s * c30,      s + s * s30 ])
    TR = np.array([ s * c30,      s + s * s30 ])
    TB = np.array([ 0.0,          s + 2*s*s30 ])   # top-back (highest point)

    # Three visible faces
    # Front-left face
    ax.add_patch(plt.Polygon([BF, BL, TL, TF],
        facecolor=color,
        edgecolor='#1A1A1A', linewidth=2.0, zorder=2))
    # Front-right face (darker)
    ax.add_patch(plt.Polygon([BF, BR, TR, TF],
        facecolor=_darken(color, 0.73),
        edgecolor='#1A1A1A', linewidth=2.0, zorder=2))
    # Top face (lightest)
    ax.add_patch(plt.Polygon([TF, TL, TB, TR],
        facecolor=_lighten(color, 1.35),
        edgecolor='#1A1A1A', linewidth=2.0, zorder=3))

    # Axes bounds
    pad = s * 0.15
    ax.set_xlim(-s*c30 - pad, s*c30 + pad)
    ax.set_ylim(-pad, s + 2*s*s30 + pad)


def _iso_cuboid(ax, color, dims):
    """Isometric cuboid using same 30° projection as cube."""
    w = dims.get('w', 1.4)
    h = dims.get('h', 1.0)
    d = dims.get('d', 0.8)
    c30 = math.cos(math.radians(30))
    s30 = math.sin(math.radians(30))

    def proj(x, y, z):
        return np.array([(x - z) * c30, (x + z) * s30 * 0.5 + y])

    BFL = proj(0, 0, 0); BFR = proj(w, 0, 0)
    BBR = proj(w, 0, d)
    TFL = proj(0, h, 0); TFR = proj(w, h, 0)
    TBL = proj(0, h, d); TBR = proj(w, h, d)

    # Shift so figure is centred on x=0
    cx = (BFR[0] + BFL[0]) / 2
    for v in [BFL, BFR, BBR, TFL, TFR, TBL, TBR]:
        v[0] -= cx

    ax.add_patch(plt.Polygon([BFL, BFR, TFR, TFL],
        facecolor=color, edgecolor='#1A1A1A', lw=1.8, zorder=2))
    ax.add_patch(plt.Polygon([BFR, BBR, TBR, TFR],
        facecolor=_darken(color, 0.73), edgecolor='#1A1A1A', lw=1.8, zorder=2))
    ax.add_patch(plt.Polygon([TFL, TFR, TBR, TBL],
        facecolor=_lighten(color, 1.35), edgecolor='#1A1A1A', lw=1.8, zorder=3))


def _iso_cylinder(ax, color, dims):
    r  = dims.get('r', 0.9)
    h  = dims.get('h', 1.5)
    ry = r * 0.35  # ellipse y-radius for top/bottom

    # Body (rectangle)
    body = plt.Rectangle((-r, -h/2), 2*r, h,
                         facecolor=color, edgecolor='#222', lw=1.5)
    ax.add_patch(body)
    # Top ellipse
    from matplotlib.patches import Ellipse
    top = Ellipse((0, h/2), 2*r, 2*ry, facecolor=_lighten(color, 1.3),
                  edgecolor='#222', lw=1.5, zorder=3)
    ax.add_patch(top)
    # Bottom ellipse (partial — visible edge)
    bot = Ellipse((0, -h/2), 2*r, 2*ry, facecolor=_darken(color, 0.8),
                  edgecolor='#222', lw=1.5, zorder=2)
    ax.add_patch(bot)


def _iso_cone(ax, color, dims):
    r = dims.get('r', 0.9)
    h = dims.get('h', 1.8)
    ry = r * 0.35
    from matplotlib.patches import Ellipse
    # Body (triangle)
    body = plt.Polygon([(-r, -h*0.4), (r, -h*0.4), (0, h*0.6)],
                       facecolor=color, edgecolor='#222', lw=1.5)
    ax.add_patch(body)
    # Base ellipse
    base = Ellipse((0, -h*0.4), 2*r, 2*ry, facecolor=_darken(color, 0.8),
                   edgecolor='#222', lw=1.5, zorder=2)
    ax.add_patch(base)


def _iso_sphere(ax, color, dims):
    r = dims.get('r', 1.1)
    from matplotlib.patches import Ellipse
    sphere = plt.Circle((0, 0), r, facecolor=color, edgecolor='#222', lw=1.5)
    ax.add_patch(sphere)
    # Equator ellipse
    eq = Ellipse((0, 0), 2*r, r*0.5, facecolor='none',
                 edgecolor=_darken(color, 0.7), lw=1.2, linestyle='--')
    ax.add_patch(eq)


def _iso_triangular_prism(ax, color, dims):
    """Triangular prism using same 30° isometric projection as cube.
    The triangular face points toward the viewer; prism extends into depth."""
    w = dims.get('w', 1.0)    # half-width of triangle base
    h = dims.get('h', 1.5)    # height of triangle
    d = dims.get('d', 0.9)    # length of prism (depth)

    c30 = math.cos(math.radians(30))
    s30 = math.sin(math.radians(30))

    # Depth vector: same direction as cube's depth (right-back)
    dv = np.array([c30 * d, s30 * d])

    # Front triangle vertices (in 2D, facing viewer)
    FBL = np.array([-w,  0.0])    # front bottom-left
    FBR = np.array([ w,  0.0])    # front bottom-right
    FA  = np.array([ 0.0, h  ])   # front apex

    # Back triangle (front + depth vector)
    BBL = FBL + dv
    BBR = FBR + dv
    BA  = FA  + dv

    # Draw order: back elements first, front last
    # Bottom face (FBL→FBR→BBR→BBL) — darkest, viewed from below
    ax.add_patch(plt.Polygon([FBL, FBR, BBR, BBL],
        facecolor=_darken(color, 0.55),
        edgecolor='#1A1A1A', lw=1.8, zorder=1))

    # Back triangle — visible through the right face gap
    ax.add_patch(plt.Polygon([BBL, BBR, BA],
        facecolor=_darken(color, 0.68),
        edgecolor='#1A1A1A', lw=1.8, zorder=1))

    # Right rectangular face (FBR→BBR→BA→FA)
    ax.add_patch(plt.Polygon([FBR, BBR, BA, FA],
        facecolor=_darken(color, 0.78),
        edgecolor='#1A1A1A', lw=1.8, zorder=2))

    # Front triangle — main colour, drawn on top
    ax.add_patch(plt.Polygon([FBL, FBR, FA],
        facecolor=color,
        edgecolor='#1A1A1A', lw=1.8, zorder=3))


def _iso_square_pyramid(ax, color, dims):
    b = dims.get('b', 1.0)
    h = dims.get('h', 1.6)

    # Key 2D positions in isometric-style projection
    apex  = np.array([0.0,   h * 0.62])
    # Base: diamond shape — front bottom, right, back top, left
    b_front = np.array([ 0.0,  -h * 0.28])
    b_right = np.array([ b * 1.15, -h * 0.08])
    b_back  = np.array([ 0.0,   h * 0.12])
    b_left  = np.array([-b * 1.15, -h * 0.08])

    # Draw base diamond (darkest, at back/bottom so drawn first)
    ax.add_patch(plt.Polygon(
        [b_front, b_right, b_back, b_left],
        facecolor=_darken(color, 0.52),
        edgecolor='#1A1A1A', lw=1.5, zorder=1))

    # Left-front triangular face (medium — faces viewer)
    ax.add_patch(plt.Polygon(
        [apex, b_left, b_front],
        facecolor=color,
        edgecolor='#1A1A1A', lw=1.5, zorder=2))

    # Right-front triangular face (darker — side-on)
    ax.add_patch(plt.Polygon(
        [apex, b_front, b_right],
        facecolor=_darken(color, 0.76),
        edgecolor='#1A1A1A', lw=1.5, zorder=2))

    # Back-left face hint (very dark, just visible)
    ax.add_patch(plt.Polygon(
        [apex, b_left, b_back],
        facecolor=_darken(color, 0.60),
        edgecolor='#1A1A1A', lw=1.0, zorder=1))


# ═══════════════════════════════════════════════════════════════════════════════
# 21. 3D SHAPES — NET
# ═══════════════════════════════════════════════════════════════════════════════

def _shape_3d_net(spec, path, dpi):
    shape = spec.get('shape', 'cube').lower().replace(' ', '_')
    color = spec.get('color', '#BDD7F0')
    lbl   = spec.get('label', '')

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.set_aspect('equal')
    ax.axis('off')

    nets = {
        'cube':             _net_cube,
        'cuboid':           _net_cuboid,
        'triangular_prism': _net_triangular_prism,
        'square_pyramid':   _net_square_pyramid,
        'cylinder':         _net_cylinder,
    }
    fn = nets.get(shape, _net_cube)
    fn(ax, color)

    if lbl:
        ymin = ax.get_ylim()[0]
        # Place label centred in the space below the net (net bottom at y=0)
        label_y = ymin / 2   # halfway between bottom of axes and y=0
        ax.text(np.mean(ax.get_xlim()), label_y, lbl,
                ha='center', va='center', fontsize=11, style='italic')

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _net_cube(ax, color):
    s = 1.0
    # Cross net: 4 in a column + 1 left + 1 right of second from top
    # Column positions: (col_offset, row_from_bottom)
    faces = [
        (0, 3), (0, 2), (0, 1), (0, 0),   # vertical strip (bottom→top)
        (-1, 2), (1, 2),                    # left and right of third row
    ]
    for (col, row) in faces:
        x, y = col * s, row * s
        rect = plt.Rectangle((x, y), s, s, facecolor=color,
                              edgecolor=DARK, lw=1.8)
        ax.add_patch(rect)
    ax.set_xlim(-1.3, 2.3)
    ax.set_ylim(-0.3, 4.5)   # extra headroom so top face isn't clipped


def _net_cuboid(ax, color):
    w, h, d = 1.5, 1.0, 0.6
    faces = [
        (0, d+h, w, d),    # top
        (0, d, w, h),      # front
        (0, 0, w, d),      # bottom
        (-d, d, d, h),     # left
        (w, d, d, h),      # right
        (0, d+h+d, w, h),  # back
    ]
    for (x, y, fw, fh) in faces:
        rect = plt.Rectangle((x, y), fw, fh, facecolor=color,
                              edgecolor=DARK, lw=1.5)
        ax.add_patch(rect)
    ax.set_xlim(-0.8, w+d+0.3)
    ax.set_ylim(-0.2, d+h+d+h+0.3)


def _net_triangular_prism(ax, color):
    w, h, d = 1.2, 1.0, 0.8
    # Three rectangles + two triangles
    rects = [(0, 0, w, d), (0, d, w, h), (0, d+h, w, d)]
    for (x, y, rw, rh) in rects:
        ax.add_patch(plt.Rectangle((x, y), rw, rh, facecolor=color,
                                   edgecolor=DARK, lw=1.8))
    # Triangles on left and right of middle rectangle
    for tx in [-d, w]:
        pts = np.array([[tx, d], [tx + d, d], [tx + d/2, d + h]])
        ax.add_patch(plt.Polygon(pts, facecolor=color,
                                 edgecolor=DARK, lw=1.8))
    ax.set_xlim(-d - 0.3, w + d + 0.3)
    ax.set_ylim(-0.85, d + h + d + 0.35)   # extra space below for label


def _net_square_pyramid(ax, color):
    b = 1.2
    slant = 1.1
    # Square base
    ax.add_patch(plt.Rectangle((0,0), b, b, facecolor=color,
                               edgecolor=DARK, lw=1.5))
    # Four triangular faces
    midpts = [(b/2, 0), (b, b/2), (b/2, b), (0, b/2)]
    corners = [(0,0),(b,0),(b,b),(0,b)]
    for i, (mx, my) in enumerate(midpts):
        # Direction away from base
        nx = mx - b/2; ny = my - b/2
        norm = math.sqrt(nx**2 + ny**2)
        if norm > 0:
            nx, ny = nx/norm, ny/norm
        apex = (mx + nx * slant, my + ny * slant)
        c1 = corners[i]
        c2 = corners[(i+1)%4]
        ax.add_patch(plt.Polygon([c1, c2, apex],
                                 facecolor=_lighten(color, 1.2),
                                 edgecolor=DARK, lw=1.5))
    ax.set_xlim(-slant-0.3, b+slant+0.3)
    ax.set_ylim(-slant-0.2, b+slant+0.3)


def _net_cylinder(ax, color):
    from matplotlib.patches import Ellipse
    r = 0.7; h = 2.0
    # Rectangle (body)
    circ = 2 * math.pi * r
    ax.add_patch(plt.Rectangle((0, 0), circ, h, facecolor=color,
                               edgecolor=DARK, lw=1.5))
    # Top and bottom circles
    for cy in [-r*0.8, h+r*0.8]:
        ax.add_patch(plt.Circle((circ/2, cy), r, facecolor=_lighten(color,1.2),
                               edgecolor=DARK, lw=1.5))
    ax.set_xlim(-0.3, circ+0.3)
    ax.set_ylim(-r*1.2, h+r*1.2)


# ═══════════════════════════════════════════════════════════════════════════════
# 22. VENN DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def _venn_diagram(spec, path, dpi):
    """
    Spec:
        circles:   2 or 3
        labels:    list of str — label for each circle
        colors:    list of hex
        items_above: list of str — items to sort (shown above diagram)
        placed:    dict — {'left':[...], 'intersection':[...], 'right':[...],
                           'left_only':[...], 'right_only':[...], 'outside':[...]}
                   (optional — leave empty for task state)
        title:     str
    """
    n_circles  = spec.get('circles', 2)
    labels     = spec.get('labels', ['Set A', 'Set B'])
    colors     = spec.get('colors', [SHAPE_A, '#C83030'])
    items_above = spec.get('items_above', [])
    placed     = spec.get('placed', {})
    title      = spec.get('title', '')

    # Layout
    ew, eh   = 3.8, 2.6
    offset   = 1.5
    item_gap = 0.42   # gap between items row bottom and circle top

    items_y  = eh / 2 + item_gap if items_above else 0
    # Extra headroom: labels are now ABOVE the circles
    ylim_top = max(eh / 2 + 0.75, items_y + 0.38)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_xlim(-4.8, 4.8)
    ax.set_ylim(-eh / 2 - 0.5, ylim_top)
    ax.set_aspect('equal')
    ax.axis('off')

    if n_circles == 2:
        from matplotlib.patches import Ellipse
        for i in range(2):
            cx = (-offset if i == 0 else offset)
            col = colors[i] if i < len(colors) else SHAPE_A
            ellipse = Ellipse((cx, 0), ew, eh, facecolor='none',
                              edgecolor=col, lw=2.4)
            ax.add_patch(ellipse)
            # Label OUTSIDE — centred on circle, just above the top arc
            ax.text(cx, eh / 2 + 0.14,
                    labels[i] if i < len(labels) else '',
                    ha='center', va='bottom', fontsize=11,
                    fontweight='bold', color=col)

        # Placed items — vertically centred in each region
        regions = {
            'left':         (-2.0, 0.0),
            'intersection': ( 0.0, 0.0),
            'right':        ( 2.0, 0.0),
        }
        for region, (rx, ry) in regions.items():
            region_items = placed.get(region, [])
            n = len(region_items)
            for j, item in enumerate(region_items):
                iy = ry + (j - (n - 1) / 2) * 0.52
                ax.text(rx, iy, str(item), ha='center', va='center',
                        fontsize=13, color=DARK, fontweight='bold')

    elif n_circles == 3:
        from matplotlib.patches import Ellipse
        r = 2.0
        centres = [(0, 1.0), (-1.4, -1.0), (1.4, -1.0)]
        for i, (cx, cy) in enumerate(centres):
            col = colors[i] if i < len(colors) else SHAPE_A
            ellipse = Ellipse((cx, cy), r*1.6, r*1.6, facecolor='none',
                              edgecolor=col, lw=2.0)
            ax.add_patch(ellipse)
            ax.text(cx + (0 if i==0 else (-0.8 if i==1 else 0.8)),
                    cy + (0.9 if i==0 else -0.8),
                    labels[i] if i < len(labels) else '',
                    ha='center', va='center', fontsize=10,
                    fontweight='bold', color=col)

    # Items to sort — just above the circles, evenly spaced across circle width
    if items_above:
        n_items = len(items_above)
        x_left  = -(offset + ew / 2 - 0.4)
        x_right =   offset + ew / 2 - 0.4
        x_step  = (x_right - x_left) / max(n_items - 1, 1)
        for j, item in enumerate(items_above):
            x_pos = x_left + x_step * j if n_items > 1 else 0.0
            ax.text(x_pos, items_y, str(item),
                    ha='center', va='bottom', fontsize=13,
                    fontweight='bold', color=DARK)

    if title:
        ax.text(0, ylim_top - 0.05, title,
                ha='center', va='top', fontsize=11, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 23. CARROLL DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def _carroll_diagram(spec, path, dpi):
    """
    Spec:
        row_criteria:   [positive_label, negative_label]
        col_criteria:   [positive_label, negative_label]
        items:          dict {(row_idx, col_idx): [values]} — placed items
        items_to_sort:  list — shown above diagram
        title:          str
    """
    row_c  = spec.get('row_criteria', ['Even', 'Not even'])
    col_c  = spec.get('col_criteria', ['Multiple of 3', 'Not multiple of 3'])
    items  = spec.get('items', {})
    above  = spec.get('items_to_sort', [])
    title  = spec.get('title', '')

    n_rows, n_cols = len(row_c), len(col_c)
    cell_w, cell_h = 2.8, 1.6
    head_w, head_h = 2.0, 0.8
    total_w = head_w + n_cols * cell_w
    total_h = head_h + n_rows * cell_h + (0.8 if above else 0) + (0.5 if title else 0)

    fig, ax = plt.subplots(figsize=(total_w + 0.4, total_h + 0.4))
    ax.set_xlim(0, total_w + 0.4)
    ax.set_ylim(0, total_h + 0.4)
    ax.axis('off')

    y_offset = 0.2 + (0.8 if above else 0)

    # Top-left corner cell (blank)
    ax.add_patch(plt.Rectangle((0.2, y_offset + n_rows*cell_h), head_w, head_h,
                                facecolor='#404040', edgecolor='#222', lw=1.2))

    # Column headers
    for ci, cl in enumerate(col_c):
        x = 0.2 + head_w + ci * cell_w
        y = y_offset + n_rows * cell_h
        rect = plt.Rectangle((x, y), cell_w, head_h,
                              facecolor=SHAPE_A, edgecolor='#222', lw=1.5)
        ax.add_patch(rect)
        ax.text(x + cell_w/2, y + head_h/2, cl,
                ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')

    # Row headers
    for ri, rl in enumerate(row_c):
        y = y_offset + (n_rows - 1 - ri) * cell_h
        rect = plt.Rectangle((0.2, y), head_w, cell_h,
                              facecolor=SHAPE_B, edgecolor='#222', lw=1.5)
        ax.add_patch(rect)
        ax.text(0.2 + head_w/2, y + cell_h/2, rl,
                ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')

    # Data cells
    for ri in range(n_rows):
        for ci in range(n_cols):
            x = 0.2 + head_w + ci * cell_w
            y = y_offset + (n_rows - 1 - ri) * cell_h
            rect = plt.Rectangle((x, y), cell_w, cell_h,
                                  facecolor=WHITE, edgecolor='#444', lw=1.2)
            ax.add_patch(rect)
            cell_items = items.get((ri, ci), [])
            for j, item in enumerate(cell_items):
                ix = x + cell_w * (0.25 + (j % 3) * 0.25)
                iy = y + cell_h * (0.65 - (j // 3) * 0.35)
                ax.text(ix, iy, str(item), ha='center', va='center',
                        fontsize=11, color=DARK)

    # Items to sort
    if above:
        n_above = len(above)
        y_top = y_offset + n_rows * cell_h + head_h + 0.1
        step  = total_w / max(n_above + 1, 2)
        for j, item in enumerate(above):
            ax.text(0.2 + step * (j + 1), y_top, str(item),
                    ha='center', va='bottom', fontsize=12,
                    fontweight='bold', color=DARK)

    if title:
        ax.text(total_w/2, total_h + 0.1, title,
                ha='center', va='top', fontsize=11, color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 24. STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

def _tally_chart(spec, path, dpi):
    """
    Spec:
        categories:   list of str
        counts:       list of int
        title:        str
        show_totals:  bool (default True)
    """
    cats    = spec.get('categories', ['A','B','C'])
    counts  = spec.get('counts', [4, 7, 3])
    title   = spec.get('title', '')
    show_t  = spec.get('show_totals', True)

    n = len(cats)
    row_h = 0.65
    col_widths = [2.2, 4.0, 1.0]  # category, tallies, total
    total_w = sum(col_widths)
    header_h = 0.55
    title_h  = 0.55 if title else 0
    total_h  = title_h + header_h + n * row_h

    fig, ax = plt.subplots(figsize=(total_w + 0.3, total_h + 0.4))
    ax.set_xlim(0, total_w + 0.3)
    ax.set_ylim(0, total_h + 0.4)
    ax.axis('off')

    y_off = 0.2  # bottom padding

    # Header
    headers = ['Category', 'Tally', 'Total']
    x = 0.15
    for hi, (h_lbl, cw) in enumerate(zip(headers, col_widths)):
        rect = plt.Rectangle((x, y_off + n*row_h), cw, header_h,
                              facecolor=SHAPE_A, edgecolor='#222', lw=1.2)
        ax.add_patch(rect)
        ax.text(x + cw/2, y_off + n*row_h + header_h/2, h_lbl,
                ha='center', va='center', fontsize=10,
                fontweight='bold', color='white')
        x += cw

    # Rows
    for ri, (cat, count) in enumerate(zip(cats, counts)):
        y = y_off + (n - 1 - ri) * row_h
        x = 0.15
        fc = LIGHT_GREY if ri % 2 == 0 else WHITE
        for cw in col_widths:
            rect = plt.Rectangle((x, y), cw, row_h,
                                  facecolor=fc, edgecolor='#888', lw=0.8)
            ax.add_patch(rect)
            x += cw

        # Category label
        ax.text(0.15 + col_widths[0]/2, y + row_h/2, cat,
                ha='center', va='center', fontsize=10, color=DARK)

        # Tally marks
        _draw_tally(ax, 0.15 + col_widths[0] + 0.1, y + row_h*0.15,
                    col_widths[1] - 0.2, row_h * 0.7, count)

        # Total
        if show_t:
            ax.text(0.15 + col_widths[0] + col_widths[1] + col_widths[2]/2,
                    y + row_h/2, str(count),
                    ha='center', va='center', fontsize=11,
                    fontweight='bold', color=DARK)

    if title:
        # Title sits above the header row, clear of table content
        title_y = y_off + n * row_h + header_h + title_h / 2
        ax.text(total_w / 2, title_y, title,
                ha='center', va='center', fontsize=11,
                fontweight='bold', color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


def _draw_tally(ax, x, y, w, h, count):
    """Draw tally marks (groups of 5) in a box."""
    if count == 0:
        return
    groups = count // 5
    rem    = count % 5
    mark_h = h * 0.75
    mark_w = h * 0.18
    gap    = mark_w * 0.5
    group_w = mark_w * 4 + gap * 3 + mark_h * 0.25 + gap  # 4 uprights + diagonal + gap

    x_pos = x
    for g in range(groups):
        if x_pos + group_w > x + w:
            break
        for m in range(4):
            mx = x_pos + m * (mark_w + gap)
            ax.plot([mx, mx], [y, y + mark_h], color=DARK, lw=1.4)
        # Diagonal cross
        diag_x0 = x_pos - gap * 0.5
        diag_x1 = x_pos + 4 * (mark_w + gap) - gap * 0.5
        ax.plot([diag_x0, diag_x1], [y + mark_h * 0.9, y + mark_h * 0.1],
                color=DARK, lw=1.4)
        x_pos += group_w

    for m in range(rem):
        mx = x_pos + m * (mark_w + gap)
        if mx + mark_w <= x + w:
            ax.plot([mx, mx], [y, y + mark_h], color=DARK, lw=1.4)


def _bar_chart(spec, path, dpi):
    """
    Spec:
        categories:   list of str
        values:       list of number
        x_label:      str
        y_label:      str
        title:        str
        color:        hex
        orientation:  'vertical' | 'horizontal' (default vertical)
        y_max:        number (auto if not given)
        grid:         bool (default True)
    """
    cats   = spec.get('categories', ['A','B','C','D'])
    vals   = spec.get('values', [4, 7, 3, 6])
    xl     = spec.get('x_label', '')
    yl     = spec.get('y_label', '')
    title  = spec.get('title', '')
    color  = spec.get('color', SHAPE_A)
    orient = spec.get('orientation', 'vertical')
    y_max  = spec.get('y_max', None)
    grid   = spec.get('grid', True)

    fig, ax = plt.subplots(figsize=(max(len(cats) * 1.1, 5), 4.5))

    if orient == 'vertical':
        bars = ax.bar(cats, vals, color=color, edgecolor='#333',
                      linewidth=1.0, width=0.6)
        if y_max:
            ax.set_ylim(0, y_max)
        ax.set_xlabel(xl, fontsize=11)
        ax.set_ylabel(yl, fontsize=11)
        if grid:
            ax.yaxis.grid(True, alpha=0.4, linewidth=0.7)
        ax.set_axisbelow(True)
    else:
        bars = ax.barh(cats, vals, color=color, edgecolor='#333',
                       linewidth=1.0, height=0.6)
        ax.set_xlabel(yl, fontsize=11)
        ax.set_ylabel(xl, fontsize=11)
        if grid:
            ax.xaxis.grid(True, alpha=0.4, linewidth=0.7)
        ax.set_axisbelow(True)

    if title:
        ax.set_title(title, fontsize=12, pad=8)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=10)
    fig.patch.set_facecolor(WHITE)
    fig.tight_layout()
    return _save(fig, path, dpi)


def _line_graph(spec, path, dpi):
    """
    Spec:
        x_values:   list
        y_values:   list  (or list of lists for multiple lines)
        x_label:    str
        y_label:    str
        title:      str
        labels:     list of str — series labels (for multiple lines)
        colors:     list of hex
        show_points: bool (default True)
        y_min:      number
        y_max:      number
    """
    x_vals  = spec.get('x_values', [0,1,2,3,4,5])
    y_vals  = spec.get('y_values', [2,4,3,6,5,8])
    xl      = spec.get('x_label', '')
    yl      = spec.get('y_label', '')
    title   = spec.get('title', '')
    lbls    = spec.get('labels', [])
    colors  = spec.get('colors', [SHAPE_A, SHAPE_B, SHAPE_C])
    show_pts = spec.get('show_points', True)

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Handle single or multiple series
    if y_vals and not isinstance(y_vals[0], (list, tuple)):
        y_vals = [y_vals]

    for i, yv in enumerate(y_vals):
        col = colors[i % len(colors)]
        lbl = lbls[i] if i < len(lbls) else None
        ax.plot(x_vals, yv, color=col, lw=2.0, marker='o' if show_pts else None,
                markersize=7, label=lbl)
        if show_pts:
            ax.plot(x_vals, yv, 'o', color=col, markersize=7)

    ax.set_xlabel(xl, fontsize=11)
    ax.set_ylabel(yl, fontsize=11)
    if title:
        ax.set_title(title, fontsize=12, pad=8)
    if lbls:
        ax.legend(fontsize=9)
    ax.yaxis.grid(True, alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=10)
    if spec.get('y_min') is not None:
        ax.set_ylim(bottom=spec['y_min'])
    if spec.get('y_max') is not None:
        ax.set_ylim(top=spec['y_max'])
    fig.patch.set_facecolor(WHITE)
    fig.tight_layout()
    return _save(fig, path, dpi)


def _pie_chart(spec, path, dpi):
    """
    Spec:
        categories: list of str
        values:     list of number
        colors:     list of hex
        title:      str
        show_percentages: bool (default True)
        show_values: bool (default False)
    """
    cats    = spec.get('categories', ['A','B','C'])
    vals    = spec.get('values', [40, 35, 25])
    colors  = spec.get('colors', [SHAPE_A, SHAPE_B, FRACTION_GREEN,
                                   FRACTION_ORANGE, SHAPE_C])
    title   = spec.get('title', '')
    show_pct = spec.get('show_percentages', True)
    show_v   = spec.get('show_values', False)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    clrs = [colors[i % len(colors)] for i in range(len(cats))]

    def autopct_fn(pct):
        if show_pct:
            return f'{pct:.1f}%'
        return ''

    wedges, texts, autotexts = ax.pie(
        vals, labels=cats, colors=clrs,
        autopct=autopct_fn if show_pct else None,
        startangle=90, wedgeprops={'edgecolor': '#333', 'linewidth': 1.2})

    for t in texts:
        t.set_fontsize(10)
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color('white')

    if title:
        ax.set_title(title, fontsize=12, pad=8)

    fig.patch.set_facecolor(WHITE)
    fig.tight_layout()
    return _save(fig, path, dpi)


# ═══════════════════════════════════════════════════════════════════════════════
# 25. TIMETABLE
# ═══════════════════════════════════════════════════════════════════════════════

def _timetable(spec, path, dpi):
    """
    Spec:
        stations:   list of str — row headers (stops)
        services:   list of dicts — each service is {label: str, times: [str or None]}
                    Use None for stops the service doesn't call at
        title:      str
        highlight:  list of (row, col) tuples to highlight in yellow
    """
    stations  = spec.get('stations', ['Town A', 'Town B', 'Town C'])
    services  = spec.get('services', [
        {'label': 'Train 1', 'times': ['09:00', '09:25', '09:45']},
        {'label': 'Train 2', 'times': ['10:30', None, '11:10']},
    ])
    title     = spec.get('title', '')
    highlight = spec.get('highlight', [])

    n_rows = len(stations)
    n_cols = len(services)

    row_h   = 0.55
    col_w   = 1.5
    head_h  = 0.65
    label_w = 2.2
    total_w = label_w + n_cols * col_w
    total_h = head_h + n_rows * row_h + (0.5 if title else 0)

    fig, ax = plt.subplots(figsize=(total_w + 0.3, total_h + 0.3))
    ax.set_xlim(0, total_w + 0.3)
    ax.set_ylim(0, total_h + 0.3)
    ax.axis('off')

    y_off = 0.15 + (0.5 if title else 0)

    # Header row — service labels
    ax.add_patch(plt.Rectangle((0.15, y_off + n_rows*row_h), label_w, head_h,
                                facecolor=SHAPE_A, edgecolor='#222', lw=1.2))
    for ci, svc in enumerate(services):
        x = 0.15 + label_w + ci * col_w
        ax.add_patch(plt.Rectangle((x, y_off + n_rows*row_h), col_w, head_h,
                                    facecolor=SHAPE_A, edgecolor='#222', lw=1.2))
        ax.text(x + col_w/2, y_off + n_rows*row_h + head_h/2,
                svc.get('label', f'Service {ci+1}'),
                ha='center', va='center', fontsize=9.5,
                fontweight='bold', color='white')

    # Data rows
    for ri, station in enumerate(stations):
        y = y_off + (n_rows - 1 - ri) * row_h
        fc_row = LIGHT_GREY if ri % 2 == 0 else WHITE

        # Station label
        ax.add_patch(plt.Rectangle((0.15, y), label_w, row_h,
                                    facecolor=fc_row, edgecolor='#888', lw=0.8))
        ax.text(0.15 + 0.12, y + row_h/2, station,
                ha='left', va='center', fontsize=9.5, color=DARK)

        # Times
        for ci, svc in enumerate(services):
            x = 0.15 + label_w + ci * col_w
            is_highlighted = (ri, ci) in highlight
            fc = '#FFFACD' if is_highlighted else fc_row
            ax.add_patch(plt.Rectangle((x, y), col_w, row_h,
                                        facecolor=fc, edgecolor='#888', lw=0.8))
            times = svc.get('times', [])
            time_val = times[ri] if ri < len(times) else None
            if time_val is not None:
                ax.text(x + col_w/2, y + row_h/2, str(time_val),
                        ha='center', va='center', fontsize=9.5,
                        color=DARK, fontweight='bold' if is_highlighted else 'normal')
            else:
                ax.text(x + col_w/2, y + row_h/2, '—',
                        ha='center', va='center', fontsize=11,
                        color=MID_GREY)

    if title:
        ax.text(total_w/2, total_h + 0.1, title,
                ha='center', va='top', fontsize=11, fontweight='bold', color=DARK)

    fig.patch.set_facecolor(WHITE)
    return _save(fig, path, dpi)


# ─── CONVENIENCE ALIASES ──────────────────────────────────────────────────────
MID_GREY = '#A0A0A0'



# ─── STATISTICS CHARTS ───────────────────────────────────────────────────────
# Used by draw_stats_chart_slide in build_lesson_v3.py.
# All functions accept a chart_data dict and write a PNG to output_path.

_WFA_BLUE   = '#1798d3'
_WFA_ORANGE = '#e57d24'
_GRID_LINE  = '#CCCCCC'
_AXIS_COL   = '#444444'
_TEXT_COL   = '#1A1A1A'
_LABEL_SIZE = 11
_TICK_SIZE  = 10


def render_stats_pictogram(data, output_path, dpi=150):
    """Horizontal pictogram. Each symbol = key_value items."""
    cats      = data['categories']
    vals      = data['values']
    key_val   = data.get('key_value', 2)
    sym_label = data.get('symbol_label', 'pupils')
    title     = data.get('title', '')
    colour    = data.get('colour', _WFA_BLUE)

    n     = len(cats)
    max_syms = max(v // key_val for v in vals)

    fig_w = max(6.5, max_syms * 0.55 + 2.5)
    fig_h = n * 0.65 + 1.2
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    RADIUS = 0.20
    SYM_W  = 0.52   # horizontal spacing per symbol

    # Longest category label — determine left margin
    max_len = max(len(c) for c in cats)
    label_x_end = 0.05 + max_len * 0.062   # rough em-width

    for i, (cat, val) in enumerate(zip(cats, vals)):
        y_row = (n - 1 - i) * 0.65 + 0.5
        # Category label
        ax.text(label_x_end - 0.04, y_row, cat,
                ha='right', va='center',
                fontsize=_LABEL_SIZE, color=_TEXT_COL, fontweight='bold')
        # Symbols
        n_syms = val // key_val
        for j in range(n_syms):
            cx = label_x_end + 0.08 + j * SYM_W + RADIUS
            circle = plt.Circle((cx, y_row), RADIUS, color=colour, zorder=3)
            ax.add_patch(circle)

    # Key
    key_y = -0.25
    ax.add_patch(plt.Circle((label_x_end + 0.08 + RADIUS, key_y), RADIUS,
                             color=colour, zorder=3))
    ax.text(label_x_end + 0.08 + RADIUS * 2 + 0.12, key_y,
            f'= {key_val} {sym_label}',
            ha='left', va='center', fontsize=_LABEL_SIZE - 1, color=_TEXT_COL)

    total_w  = label_x_end + 0.08 + max_syms * SYM_W + 0.3
    total_h  = n * 0.65 + 0.6
    ax.set_xlim(0, total_w)
    ax.set_ylim(-0.55, total_h)
    ax.axis('off')

    if title:
        ax.text(total_w / 2, total_h + 0.05, title,
                ha='center', va='bottom',
                fontsize=_LABEL_SIZE, fontweight='bold', color=_TEXT_COL)

    return _save(fig, output_path, dpi)


def render_stats_bar_chart(data, output_path, dpi=150):
    """Vertical bar chart with explicit y scale."""
    cats    = data['categories']
    vals    = data['values']
    y_max   = data.get('y_max', max(vals) + 5)
    y_step  = data.get('y_step', 5)
    y_label = data.get('y_label', '')
    x_label = data.get('x_label', '')
    title   = data.get('title', '')
    colour  = data.get('colour', _WFA_BLUE)

    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    x_pos = range(len(cats))
    bars = ax.bar(x_pos, vals, color=colour, width=0.55,
                  edgecolor='white', linewidth=0.8, zorder=3)

    # Grid lines at each y_step
    yticks = list(range(0, y_max + 1, y_step))
    ax.set_yticks(yticks)
    ax.yaxis.grid(True, color=_GRID_LINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    ax.set_ylim(0, y_max)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(cats, fontsize=_LABEL_SIZE - 1,
                       color=_TEXT_COL, fontweight='bold')
    ax.tick_params(axis='y', labelsize=_TICK_SIZE, colors=_AXIS_COL)
    ax.tick_params(axis='x', length=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(_GRID_LINE)

    if y_label:
        ax.set_ylabel(y_label, fontsize=_LABEL_SIZE - 1,
                      color=_TEXT_COL, labelpad=6)
    if x_label:
        ax.set_xlabel(x_label, fontsize=_LABEL_SIZE - 1,
                      color=_TEXT_COL, labelpad=6)
    if title:
        ax.set_title(title, fontsize=_LABEL_SIZE, fontweight='bold',
                     color=_TEXT_COL, pad=8)

    plt.tight_layout(pad=0.5)
    return _save(fig, output_path, dpi)


def render_stats_line_graph(data, output_path, dpi=150):
    """Line graph with dots at data points."""
    x_vals  = data['x_values']
    y_vals  = data['y_values']
    y_min   = data.get('y_min', 0)
    y_max   = data.get('y_max', max(y_vals) + 2)
    y_step  = data.get('y_step', 2)
    x_label = data.get('x_label', '')
    y_label = data.get('y_label', '')
    title   = data.get('title', '')
    colour  = data.get('colour', _WFA_BLUE)
    # Optional: mark certain points differently (e.g. for interpolation slides)
    interp_xs = data.get('interpolation_marks', [])

    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    x_idx = list(range(len(x_vals)))
    ax.plot(x_idx, y_vals, color=colour, linewidth=2.2,
            marker='o', markersize=8, markerfacecolor=colour,
            markeredgecolor='white', markeredgewidth=1.5, zorder=4)

    # Interpolation markers (vertical dashed lines at unlabelled x positions)
    for ix in interp_xs:
        ax.axvline(x=ix, color=_WFA_ORANGE, linewidth=1.2,
                   linestyle='--', zorder=2)

    # Grid
    yticks = list(range(y_min, y_max + 1, y_step))
    ax.set_yticks(yticks)
    ax.yaxis.grid(True, color=_GRID_LINE, linewidth=0.8, zorder=0)
    ax.xaxis.grid(True, color=_GRID_LINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    ax.set_ylim(y_min, y_max)
    ax.set_xlim(-0.3, len(x_vals) - 0.7)
    ax.set_xticks(x_idx)
    ax.set_xticklabels(x_vals, fontsize=_TICK_SIZE,
                       color=_TEXT_COL, fontweight='bold', rotation=0)
    ax.tick_params(axis='y', labelsize=_TICK_SIZE, colors=_AXIS_COL)
    ax.tick_params(axis='x', length=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(_GRID_LINE)

    if y_label:
        ax.set_ylabel(y_label, fontsize=_LABEL_SIZE - 1,
                      color=_TEXT_COL, labelpad=6)
    if x_label:
        ax.set_xlabel(x_label, fontsize=_LABEL_SIZE - 1,
                      color=_TEXT_COL, labelpad=6)
    if title:
        ax.set_title(title, fontsize=_LABEL_SIZE, fontweight='bold',
                     color=_TEXT_COL, pad=8)

    plt.tight_layout(pad=0.5)
    return _save(fig, output_path, dpi)


def render_stats_table(data, output_path, dpi=150):
    """Two-way table with coloured header row and optional totals highlight."""
    col_headers  = data['col_headers']
    rows         = data['rows']
    title        = data.get('title', '')
    hi_row       = data.get('highlight_row', -1)   # 0-based data row; -1 = none
    hi_col       = data.get('highlight_col', -1)   # 0-based col; -1 = none

    n_cols = len(col_headers)
    n_rows = len(rows)
    col_w  = 1.35
    row_h  = 0.50
    head_h = 0.55
    pad_t  = 0.40 if title else 0.10
    fig_w  = max(5.5, col_w * n_cols + 0.2)
    fig_h  = pad_t + head_h + row_h * n_rows + 0.15

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, n_cols * col_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    HEADER_BG   = _WFA_BLUE
    TOTAL_BG    = '#cce6f5'
    ALT_BG      = '#f5f5f5'
    BORDER      = '#999999'

    # Title
    if title:
        ax.text(n_cols * col_w / 2, fig_h - 0.08, title,
                ha='center', va='top',
                fontsize=_LABEL_SIZE, fontweight='bold', color=_TEXT_COL)

    # Header row (top of table)
    hdr_y = fig_h - pad_t - head_h
    for ci, hdr in enumerate(col_headers):
        rect = plt.Rectangle((ci * col_w, hdr_y), col_w, head_h,
                              facecolor=HEADER_BG, edgecolor='white', linewidth=0.8)
        ax.add_patch(rect)
        ax.text(ci * col_w + col_w / 2, hdr_y + head_h / 2, str(hdr),
                ha='center', va='center',
                fontsize=_LABEL_SIZE, color='white', fontweight='bold')

    # Data rows
    for ri, row in enumerate(rows):
        row_y = hdr_y - (ri + 1) * row_h
        is_hi_row = (ri == hi_row)
        for ci, val in enumerate(row):
            is_hi_col = (ci == hi_col)
            if is_hi_row or is_hi_col:
                bg   = TOTAL_BG
                bold = True
                tc   = _WFA_BLUE
            elif ri % 2 == 1:
                bg   = ALT_BG
                bold = (ci == 0)
                tc   = _TEXT_COL
            else:
                bg   = 'white'
                bold = (ci == 0)
                tc   = _TEXT_COL
            rect = plt.Rectangle((ci * col_w, row_y), col_w, row_h,
                                  facecolor=bg, edgecolor=BORDER, linewidth=0.5)
            ax.add_patch(rect)
            ax.text(ci * col_w + col_w / 2, row_y + row_h / 2, str(val),
                    ha='center', va='center',
                    fontsize=_LABEL_SIZE - 0.5, color=tc,
                    fontweight='bold' if bold else 'normal')

    plt.tight_layout(pad=0.1)
    return _save(fig, output_path, dpi)


def render_stats_double_bar(data, output_path, dpi=150):
    """Side-by-side grouped bar chart for two data series."""
    cats    = data['categories']
    series  = data['series']    # [{'label': ..., 'values': [...], 'colour': ...}]
    y_max   = data.get('y_max', 35)
    y_step  = data.get('y_step', 4)
    y_label = data.get('y_label', '')
    title   = data.get('title', '')

    n_groups = len(cats)
    n_series = len(series)
    bar_w    = 0.35
    x_idx    = list(range(n_groups))

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    offsets = [-bar_w / 2 * (n_series - 1) + i * bar_w for i in range(n_series)]
    for s, offset in zip(series, offsets):
        colour = s.get('colour', _WFA_BLUE)
        ax.bar([x + offset for x in x_idx], s['values'],
               width=bar_w, color=colour, label=s['label'],
               edgecolor='white', linewidth=0.6, zorder=3)

    yticks = list(range(0, y_max + 1, y_step))
    ax.set_yticks(yticks)
    ax.yaxis.grid(True, color=_GRID_LINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, y_max)
    ax.set_xticks(x_idx)
    ax.set_xticklabels(cats, fontsize=_LABEL_SIZE - 1,
                       color=_TEXT_COL, fontweight='bold')
    ax.tick_params(axis='y', labelsize=_TICK_SIZE, colors=_AXIS_COL)
    ax.tick_params(axis='x', length=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(_GRID_LINE)

    if y_label:
        ax.set_ylabel(y_label, fontsize=_LABEL_SIZE - 1,
                      color=_TEXT_COL, labelpad=6)
    if title:
        ax.set_title(title, fontsize=_LABEL_SIZE, fontweight='bold',
                     color=_TEXT_COL, pad=8)

    leg = ax.legend(fontsize=_LABEL_SIZE - 1, loc='upper right',
                    framealpha=0.9, edgecolor=_GRID_LINE)
    leg.get_frame().set_linewidth(0.5)

    plt.tight_layout(pad=0.5)
    return _save(fig, output_path, dpi)


def render_stats_chart(chart_type, chart_data, output_path, dpi=150):
    """Dispatch to the correct stats chart renderer."""
    dispatch = {
        'pictogram':  render_stats_pictogram,
        'bar_chart':  render_stats_bar_chart,
        'line_graph': render_stats_line_graph,
        'table':      render_stats_table,
        'double_bar': render_stats_double_bar,
    }
    if chart_type not in dispatch:
        raise ValueError(f'Unknown chart_type: {chart_type!r}')
    dispatch[chart_type](chart_data, output_path, dpi)
    return output_path
