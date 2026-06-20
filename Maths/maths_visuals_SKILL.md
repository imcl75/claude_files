# maths_visuals.py — WFA Maths Visual Rendering Library

**Location:** `Maths/maths_visuals.py` in repo · `/mnt/skills/user/maths-complete-planning-and-resources/maths_visuals.py`  
**Version:** 1.0 — 49 visual types, 2918 lines  
**Stack:** Python 3, matplotlib, numpy

---

## Overview

Every mathematical representation renders to a PNG via one call:

```python
from maths_visuals import render_visual
path = render_visual(spec_dict, output_path, dpi=150)
```

Both builders consume PNGs identically:
- `build_lesson_v3.py` — embeds PNG on slide via `add_picture`
- `build_lp_v3.js` — embeds PNG in LP question via `imageRun`

**DPI guidance:** 150 for teaching slides; 200 for print LPs.

---

## Colour palette

Place value colours are consistent across ALL representation types (counters, chart headers, dienes):

| Column | Colour | Hex |
|--------|--------|-----|
| M | dark red-brown | `#8B1A00` |
| HTH | burnt orange | `#C84400` |
| TTH | orange | `#E06010` |
| **TH** | **blue** | `#2565AE` |
| **H** | **green** | `#2E8B3A` |
| **T** | **amber** | `#D4A800` |
| **O** | **red** | `#C83030` |
| t | light blue | `#4BAEE0` |
| h | lighter blue | `#82CBF0` |
| th | lightest blue | `#B8E2F8` |
| . (decimal point) | grey | `#B0B0B0` |

---

## All 49 visual types

### Place Value

#### `pv_counter_chart`
PV chart with coloured counters in each cell. Up to 9 counters per cell, arranged in 3×3 grid. Optional digit summary row.

```python
{
  'type': 'pv_counter_chart',
  'columns': ['TH', 'H', 'T', 'O'],         # any subset of PV_ORDER
  'rows': [
    {'TH': 2, 'H': 0, 'T': 5, 'O': 4},      # one dict per row
    {'TH': 1, 'H': 7, 'T': 2, 'O': 1},
  ],
  'show_digit_row': True,                     # digit total row at bottom
}
```

#### `pv_chart_header`
Empty PV chart for pupils to fill in. Coloured headers with long and short names.

```python
{
  'type': 'pv_chart_header',
  'columns': ['TTH', 'TH', 'H', 'T', 'O'],  # include '.' for decimal point
  'n_rows': 2,
  'show_long_names': True,
}
```

#### `dienes`
2D flat base-10 blocks. TH = blue large square, H = green 10×10, T = amber rod, O = red small square.

```python
{
  'type': 'dienes',
  'TH': 1, 'H': 3, 'T': 2, 'O': 4,
}
```

---

### Number & Operations

#### `number_line`
Horizontal number line with arrows, optional jump arcs and X marker.

```python
{
  'type': 'number_line',
  'start': 0, 'end': 100, 'step': 10,
  'jumps': [
    {'start': 0, 'end': 73, 'label': '+73', 'color': '#2E6DB4'},
  ],
  'x_marker': 37,          # X symbol at this position (for rounding tasks)
  'labelled_points': [      # named points with coloured dots
    {'value': 50, 'label': 'halfway', 'color': '#C83030'},
  ],
  'minor_ticks': 4,         # subdivisions between major ticks
}
```

#### `part_whole`
Circle node model: one whole circle at top, 2–4 part circles below.

```python
{
  'type': 'part_whole',
  'whole': 48,
  'parts': ['?', 24],
}
```

#### `bar_model`
Four subtypes controlled by `model_type`.

```python
# Part-whole
{'type': 'bar_model', 'model_type': 'part_whole',
 'whole': {'value': 84, 'label': 'total', 'color': '#2E6DB4'},
 'parts': [{'value': 36, 'label': 'red'}, {'value': '?', 'label': 'blue'}]}

# Comparison
{'type': 'bar_model', 'model_type': 'comparison',
 'bars': [{'value': 64, 'label': 'Amy'}, {'value': 48, 'label': 'Ben'}]}

# Fraction of
{'type': 'bar_model', 'model_type': 'fraction_of',
 'total_parts': 5, 'shaded_parts': 3,
 'total_value': 40, 'part_value': 8, 'shade_color': '#2E6DB4'}

# Ratio
{'type': 'bar_model', 'model_type': 'ratio',
 'groups': [{'count': 2, 'label': 'Boys', 'color': '#2E6DB4'},
            {'count': 3, 'label': 'Girls', 'color': '#C83060'}]}
```

#### `array`
Rows of coloured circles. `groups` defines colour bands across columns. `show_row_borders` adds red border around each row.

```python
{
  'type': 'array',
  'rows': 5,
  'groups': [
    {'cols': 3, 'color': '#4A90D9'},
    {'cols': 3, 'color': '#E8A030'},
    {'cols': 3, 'color': '#8040B0'},
  ],
  'show_row_borders': True,
}
```

#### `which_answer`
Three-column comparison of worked calculations. Each answer can carry regroup marks.

```python
{
  'type': 'which_answer',
  'operation': '+', 'top': '1417', 'bottom': '738',
  'answers': [
    {'label': 'A', 'value': '8797', 'regroup_marks': []},
    {'label': 'B', 'value': '2145', 'regroup_marks': [1, 2]},
    {'label': 'C', 'value': '2155', 'regroup_marks': [1, 2]},
  ],
  'title': 'Which Answer?',
  'prompt': 'Explain the mistakes.',
}
```

---

### Fractions

#### `fraction_bar`
Single horizontal (or vertical) bar divided into parts.

```python
{'type': 'fraction_bar', 'denominator': 4, 'numerator': 3,
 'color': '#4A90D9', 'show_label': True,
 'orientation': 'horizontal'}   # or 'vertical'
```

#### `equivalence_bars`
Multiple bars of identical total width, each divided differently. Shows equivalence visually.

```python
{'type': 'equivalence_bars',
 'fractions': [[1,2],[2,4],[4,8],[3,6]],
 'color': '#4A90D9'}
```

#### `equivalence_arrows`
Two fractions with curved arrows showing ÷N or ×N between numerator and denominator.

```python
{'type': 'equivalence_arrows',
 'fraction1': [8, 12], 'fraction2': [2, 3],
 'operation': '÷', 'factor': 4}
```

#### `hundred_square`
10×10 grid, shaded by columns (`shade_by: 'columns'`) or cell-by-cell (`shade_by: 'cells'`).

```python
{'type': 'hundred_square', 'shaded': 47,
 'color': '#E8A030', 'label': '0.47'}
```

#### `ten_strip`
Single 10-cell strip for tenths representation.

```python
{'type': 'ten_strip', 'shaded': 7, 'color': '#E8A030', 'label': '7/10'}
```

#### `fraction_number_line`
Number line with fraction subdivisions and optional X marker.

```python
{'type': 'fraction_number_line',
 'start': 0, 'end': 2, 'denominator': 4,
 'x_marker': 0.75, 'show_all_labels': True}
```

#### `fraction_shape`
A shape divided into equal parts with some shaded. `shape_type`: `'bar'`, `'circle'`, `'grid'`, `'triangle'`.

```python
{'type': 'fraction_shape', 'shape_type': 'circle',
 'denominator': 5, 'numerator': 3, 'color': '#C83030'}
```

#### `fraction_set`
A collection of shapes with questions about what fraction match a criterion.

```python
{'type': 'fraction_set',
 'items': [
   {'shape': 'square', 'color': '#4A90D9'},
   {'shape': 'triangle', 'color': '#2EA050'},
   {'shape': 'circle', 'color': '#C83060'},
 ],
 'questions': ['a) What fraction are triangles?', 'b) What fraction are blue?']}
```
Valid shapes: `'square'`, `'rectangle'`, `'triangle'`, `'circle'`

---

### Geometry

#### `coordinate_grid`
Matplotlib-rendered grid — handles single and four-quadrant correctly. Axis arrows, x/y labels, negative numbers, filled polygons.

```python
# Single quadrant
{'type': 'coordinate_grid',
 'x_range': [0, 6], 'y_range': [0, 6],
 'points': [{'coord': (2, 3), 'label': 'A', 'color': '#2E6DB4'}]}

# Four-quadrant with shapes
{'type': 'coordinate_grid',
 'x_range': [-5, 5], 'y_range': [-5, 5],
 'shapes': [
   {'vertices': [(-3,-3),(-1,-3),(-1,-1),(-3,-1)],
    'color': '#2E6DB4', 'fill_color': '#2E6DB4', 'fill': True, 'label': 'A'},
 ]}
```

**Shape keys:** `vertices`, `color` (outline), `fill_color`, `fill` (bool), `alpha` (0–1), `label`  
**Point keys:** `coord`, `label`, `color`

Supports asymmetric ranges: `x_range: [-8, 5]` works correctly (as in the 2026 SATs example).

#### `angle_figure`
Single angle with arc or right-angle square.

```python
{'type': 'angle_figure',
 'angle_degrees': 60, 'orientation': 15,
 'show_arc': True, 'label': 'a', 'arm_length': 1.2}
```

#### `angle_figure_set`
Multiple angle figures side by side on one image.

```python
{'type': 'angle_figure_set',
 'angles': [
   {'angle_degrees': 90,  'orientation': 0,   'show_arc': True,  'label': '1'},
   {'angle_degrees': 150, 'orientation': -20, 'show_arc': False, 'label': '2'},
   {'angle_degrees': 40,  'orientation': 10,  'show_arc': True,  'label': '3'},
 ]}
```

#### `triangle_angles`
Triangle with two known angle labels and an arc at the unknown vertex.

```python
{'type': 'triangle_angles',
 'vertices': [(0.0, 0.0), (4.0, 0.0), (1.0, 3.0)],
 'known_angles': {0: 42, 1: 108},
 'unknown_idx': 2,
 'label': 'a)'}
```

#### `polygon`
Named regular or irregular polygon. Supports side labels, tick marks (equal sides), angle marks (right angles or arcs), vertex labels.

```python
{'type': 'polygon', 'name': 'parallelogram',
 'color': '#FFE0B0',
 'side_labels': ['8 cm', '5 cm', '8 cm', '5 cm'],
 'tick_marks': [[0, 2], [1, 3]],      # group indices → equal tick style
 'angle_marks': [0, 2],               # right-angle squares at these vertices
 'show_vertices': False,
 'show_name': True}
```

Named polygons auto-generate sensible shapes: `triangle`, `equilateral triangle`, `isosceles triangle`, `scalene triangle`, `right-angled triangle`, `square`, `rectangle`, `rhombus`, `parallelogram`, `trapezium`, `kite`, `pentagon`, `hexagon`, `heptagon`, `octagon`, `nonagon`, `decagon`.

Custom shapes: pass `'vertices': [(x,y), ...]` to override.

#### `shape_3d_iso`
Isometric 3D shape with light/dark face shading.

```python
{'type': 'shape_3d_iso',
 'shape': 'cube',          # cube | cuboid | cylinder | cone | sphere |
                            # triangular_prism | square_pyramid
 'color': '#4A90D9',
 'label': 'Cube',
 'dimensions': {'w': 1.2}} # optional proportional dimensions
```

#### `shape_3d_net`
Unfolded net of a 3D shape.

```python
{'type': 'shape_3d_net',
 'shape': 'triangular_prism',   # cube | cuboid | triangular_prism |
                                  # square_pyramid | cylinder
 'color': '#D0F0D0',
 'label': 'Net of a triangular prism'}
```

---

### Statistics

#### `venn_diagram`
2 or 3 circle Venn diagram. Items shown above for sorting tasks; `placed` dict populates regions.

```python
# Task state (empty, items above)
{'type': 'venn_diagram',
 'circles': 2,
 'labels': ['Divisible by 2', 'Divisible by 3'],
 'colors': ['#2E6DB4', '#C83030'],
 'items_above': [2, 4, 6, 9, 12, 15, 18]}

# Answer state (items placed)
{'type': 'venn_diagram',
 'circles': 2,
 'labels': ['Divisible by 2', 'Divisible by 3'],
 'placed': {'left': [2,4,14], 'intersection': [6,12,18], 'right': [9,15]}}
```

3-circle regions: `left`, `right`, `top`, `left_right`, `left_top`, `right_top`, `centre`

#### `carroll_diagram`
2×2 (or larger) sorting grid. Dark corner, blue column headers, orange row headers.

```python
{'type': 'carroll_diagram',
 'row_criteria': ['Even', 'Not even'],
 'col_criteria': ['Multiple of 3', 'Not a multiple of 3'],
 'items_to_sort': [3, 6, 9, 12, 15, 18, 21, 24],
 'items': {(0, 0): [6, 12, 18], (0, 1): [24], (1, 0): [3,9,15], (1, 1): [21]}}
```

#### `tally_chart`
Category | Tally marks (groups of 5 with diagonal) | Total. Alternating row shading.

```python
{'type': 'tally_chart',
 'categories': ['Football', 'Tennis', 'Swimming', 'Cycling'],
 'counts': [8, 5, 12, 3],
 'title': 'Favourite Sports',
 'show_totals': True}
```

#### `bar_chart`
Vertical or horizontal. Labelled axes, grid, clean spine.

```python
{'type': 'bar_chart',
 'categories': ['Mon','Tue','Wed','Thu','Fri'],
 'values': [14, 22, 18, 25, 19],
 'x_label': 'Day', 'y_label': 'Visitors',
 'title': 'Museum visitors',
 'color': '#2E6DB4',
 'orientation': 'vertical',   # or 'horizontal'
 'y_max': 30}
```

#### `line_graph`
Single or multiple series. Points marked, gridded background.

```python
# Single series
{'type': 'line_graph',
 'x_values': [0,1,2,3,4,5],
 'y_values': [4,7,5,9,6,11],
 'x_label': 'Month', 'y_label': 'Temperature (°C)',
 'title': 'Monthly Temperature'}

# Multiple series
{'type': 'line_graph',
 'x_values': [2019, 2020, 2021, 2022],
 'y_values': [[12,15,13,18], [8,11,9,14]],
 'labels': ['School A', 'School B'],
 'colors': ['#2E6DB4', '#C83030']}
```

#### `pie_chart`
Circle divided into wedges with percentage labels.

```python
{'type': 'pie_chart',
 'categories': ['Football', 'Tennis', 'Swimming', 'Other'],
 'values': [40, 25, 20, 15],
 'colors': ['#2E6DB4', '#C83030', '#2EA050', '#E8A030'],
 'title': 'Favourite Sports',
 'show_percentages': True}
```

---

### Time

#### `timetable`
Train/bus-style timetable. `None` in times list renders as `—`. Cells can be highlighted.

```python
{'type': 'timetable',
 'stations': ['Bristol Temple Meads', 'Bath Spa', 'Chippenham', 'Swindon',
              'Reading', 'London Paddington'],
 'services': [
   {'label': 'Train A', 'times': ['07:30','07:52','08:10','08:28','08:55','09:30']},
   {'label': 'Train B', 'times': ['08:15', None, '08:55','09:13','09:40','10:15']},
 ],
 'title': 'Great Western Railway — Morning Services',
 'highlight': [(5, 0), (5, 1)]}   # (row_idx, col_idx) tuples
```

---

## Extending the library

The library is parametric — spec dicts are driven by mathematical values, not pre-drawn templates. To add a new visual type:

1. Write a `_my_type(spec, path, dpi)` function
2. Add `'my_type': _my_type` to the `_DISPATCH` dict in `render_visual()`
3. Update this SKILL.md
4. Run `test_visuals.py` with a new test case
5. Push to GitHub

All renderers follow the same pattern: `_save(fig, path, dpi)` at the end.

---

## Integration with lesson builders

### build_lesson_v3.py (Python / pptxgenjs)

Add a `visual_teach` slide type to `lesson_data.py`:

```python
{
  'type': 'visual_teach',
  'title': 'Comparing fractions using equivalence bars',
  'visual': {
    'type': 'equivalence_bars',
    'fractions': [[1,2],[2,4],[4,8]],
    'color': '#4A90D9',
  },
  'questions': ['Which fractions are equivalent to ½?'],
}
```

The builder calls `render_visual(slide['visual'], f'/tmp/vis_{i}.png')` then inserts the PNG.

### build_lp_v3.js (Node.js)

Question objects gain an optional `visual` key:

```json
{
  "q": "Write the fraction shown.",
  "visual": {
    "type": "fraction_shape",
    "shape_type": "circle",
    "denominator": 5,
    "numerator": 3,
    "color": "#C83030"
  },
  "answer": "3/5"
}
```

The builder calls `python3 -c "from maths_visuals import render_visual; render_visual(...)"`
or (better) runs a thin Python wrapper that accepts a JSON spec argument.

---

## Notes

- White background on all outputs (`facecolor='white'`, `pad_inches=0.05`)
- Figure sizes are auto-calculated per type — never hardcoded
- All text uses DejaVu Sans (matplotlib default) — clean, readable, no font dependencies
- Counter labels inside circles scale with circle radius (min 4pt, max 7pt)
- The `_fmt_number()` utility formats integers cleanly and converts simple decimals to fractions where possible
