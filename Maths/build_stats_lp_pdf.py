"""
build_stats_lp_pdf.py
Generates T6W5 Statistics LPs as A4 PDF using ReportLab.
Heights are calculated from actual text wrap, not guessed.
Produces 3 pages: Standard, Adapted, Marking Station.
Also creates a 3-slide wrapper PPTX for inject_lp_previews.py.
"""
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

# ── Register fonts ────────────────────────────────────────────────────────────
FONT_DIR = '/usr/share/fonts/truetype/liberation'
pdfmetrics.registerFont(TTFont('LibSans',     f'{FONT_DIR}/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LibSansBold', f'{FONT_DIR}/LiberationSans-Bold.ttf'))

# ── Page constants (points) ───────────────────────────────────────────────────
W, H    = A4                   # 595 × 841.9
M       = 18                   # page margin
CUT_Y   = H / 2               # 420.9  — cut line between LP1 and LP2
GAP     = 8                    # gap between elements

# Chart column (right side) — generous width for readability
CHART_W = 265
CHART_X = W - M - CHART_W     # 312

# Question column (left side)
Q_X     = M
Q_W     = CHART_X - Q_X - 12  # 282  (12pt gutter before chart)

# Learning Label dimensions (match build_lp_v3.js constants)
CM           = 28.35           # 1cm in points
LABEL_SCALE  = 0.72 * 0.85
LL_W         = 9.7  * CM * LABEL_SCALE   # 168pt
LL_H         = 4.24 * CM * LABEL_SCALE   # 73.5pt
LL_X         = M
ICON_W       = 18.7            # 0.26" in pt
ICON_H       = ICON_W * (103/120)
ICON_PATH    = '/tmp/claude_work/lp_assets/mathematician_icon.png'
CHART_DIR    = '/tmp/wfa_stats_charts'

# Colours (RGB 0-1)
WFA_BLUE    = (0.09, 0.60, 0.83)
Q_BG        = (0.87, 0.92, 0.95)
Q_TXT       = (0.12, 0.31, 0.47)
Q_BORDER    = (0.08, 0.38, 0.51)
GRN         = (0.10, 0.36, 0.16)
GRN_BG      = (0.91, 0.96, 0.91)
GREY        = (0.75, 0.75, 0.75)
GREY_TXT    = (0.20, 0.20, 0.20)
DARK        = (0.10, 0.10, 0.10)

# ── Paragraph styles ──────────────────────────────────────────────────────────
Q_STYLE = ParagraphStyle('Q',
    fontName='LibSansBold', fontSize=8.5, leading=12,
    textColor=(0.12, 0.31, 0.47),
    leftIndent=6, rightIndent=6, spaceBefore=0, spaceAfter=0)

INTRO_STYLE = ParagraphStyle('I',
    fontName='LibSansBold', fontSize=9, leading=13,
    textColor=DARK, leftIndent=0, rightIndent=0)

ANS_STYLE = ParagraphStyle('A',
    fontName='LibSansBold', fontSize=8.5, leading=12,
    textColor=GRN, leftIndent=6, rightIndent=6)

# ── Helpers ───────────────────────────────────────────────────────────────────
def set_fill(c, rgb):   c.setFillColorRGB(*rgb)
def set_stroke(c, rgb): c.setStrokeColorRGB(*rgb)

def filled_rect(c, x, y_bottom, w, h, fill_rgb, stroke_rgb=None, lw=0.5):
    """Draw a rectangle. y_bottom is the BOTTOM edge (ReportLab bottom-up)."""
    set_fill(c, fill_rgb)
    if stroke_rgb:
        set_stroke(c, stroke_rgb)
        c.setLineWidth(lw)
        c.rect(x, y_bottom, w, h, fill=1, stroke=1)
    else:
        c.rect(x, y_bottom, w, h, fill=1, stroke=0)

def outline_rect(c, x, y_bottom, w, h, stroke_rgb=GREY, lw=0.5):
    """Draw an empty box."""
    set_fill(c, (1,1,1))
    set_stroke(c, stroke_rgb)
    c.setLineWidth(lw)
    c.rect(x, y_bottom, w, h, fill=1, stroke=1)

def draw_chart(c, chart_file, x, y_bottom, w, h):
    """Draw chart image, maintaining aspect ratio, centred in available space."""
    path = os.path.join(CHART_DIR, chart_file)
    if not os.path.exists(path):
        return
    img = PILImage.open(path)
    iw, ih = img.size
    aspect = iw / ih
    # Fit within (w × h) maintaining aspect
    if w / h > aspect:
        draw_h = h
        draw_w = h * aspect
    else:
        draw_w = w
        draw_h = w / aspect
    # Centre
    dx = (w - draw_w) / 2
    dy = (h - draw_h) / 2
    c.drawImage(path, x + dx, y_bottom + dy, draw_w, draw_h,
                preserveAspectRatio=True, mask='auto')

# ── Learning Label ────────────────────────────────────────────────────────────
def draw_ll(c, x, y_top, date, topic, lf, ican):
    """Draw the school LL sticker at (x, y_top). Returns actual height used."""
    PAD    = 3
    NARROW = LL_W - ICON_W - PAD*3
    FULL   = LL_W - PAD*2
    ty = y_top - PAD        # current y baseline, stepping downward

    # Icon — top right
    if os.path.exists(ICON_PATH):
        c.drawImage(ICON_PATH,
                    x + LL_W - ICON_W - PAD,
                    y_top - PAD - ICON_H,
                    ICON_W, ICON_H, mask='auto')

    # Date — 7pt
    c.setFont('LibSans', 7)
    set_fill(c, GREY_TXT)
    ty -= 7 * 0.72
    c.drawString(x + PAD, ty, date)
    ty -= 7 * 0.28 + 2

    # Topic — 9pt bold (underlined)
    c.setFont('LibSansBold', 9)
    set_fill(c, DARK)
    ty -= 9 * 0.72
    c.drawString(x + PAD, ty, topic)
    # Underline
    tw = c.stringWidth(topic, 'LibSansBold', 9)
    c.setLineWidth(0.5); set_stroke(c, DARK)
    c.line(x + PAD, ty - 1, x + PAD + tw, ty - 1)
    ty -= 9 * 0.28 + 3

    # LF — 7pt (may wrap)
    c.setFont('LibSans', 7)
    set_fill(c, GREY_TXT)
    lf_para = Paragraph(lf, ParagraphStyle('LF',
        fontName='LibSans', fontSize=7, leading=9,
        textColor=(0.2,0.2,0.2)))
    lf_w, lf_h = lf_para.wrap(FULL, 200)
    ty -= lf_h
    lf_para.drawOn(c, x + PAD, ty)
    ty -= 3

    # I can statements — 6.5pt
    for ic in ican:
        c.setFont('LibSans', 6.5)
        set_fill(c, GREY_TXT)
        ic_para = Paragraph(ic, ParagraphStyle('IC',
            fontName='LibSans', fontSize=6.5, leading=8.5,
            textColor=(0.2,0.2,0.2)))
        ic_w, ic_h = ic_para.wrap(FULL, 200)
        ty -= ic_h
        ic_para.drawOn(c, x + PAD, ty)
        ty -= 2

    return y_top - ty   # total height used

# ── Question block ────────────────────────────────────────────────────────────
def draw_questions(c, x, y_start, w, avail_h, intro, questions, is_ms):
    """
    Draw intro + questions with answer boxes.
    y_start: top of the question area (in bottom-up coords).
    avail_h: total height available.
    Returns nothing — all layout is calculated internally.
    """
    PAD = 6

    # Step 1: measure intro
    intro_para = Paragraph(intro, INTRO_STYLE)
    intro_w, intro_h = intro_para.wrap(w, 200)
    intro_h += 6   # bottom gap

    # Step 2: measure each question text
    q_paras = []
    q_heights = []
    for i, (qt, ans) in enumerate(questions):
        p = Paragraph(f'{i+1}.  {qt}', Q_STYLE)
        pw, ph = p.wrap(w - PAD*2, 200)
        box_h = ph + PAD*2   # question box height = text + padding top+bottom
        q_paras.append((p, box_h))
        q_heights.append(box_h)

    n = len(questions)
    ITEM_GAP = 6

    # Step 3: calculate answer box heights dynamically
    used = intro_h + sum(q_heights) + n * ITEM_GAP
    remaining = avail_h - used - 12   # 12pt bottom margin
    ans_h_each = max(28, remaining / n)  # at least 28pt per answer box

    # Step 4: draw everything top-down
    cy = y_start

    # Intro text
    intro_para.drawOn(c, x, cy - intro_h + 6)
    cy -= intro_h

    for i, ((p, qbox_h), (qt, ans)) in enumerate(zip(q_paras, questions)):
        # Question box
        qbox_bottom = cy - qbox_h
        filled_rect(c, x, qbox_bottom, w, qbox_h,
                    fill_rgb=Q_BG, stroke_rgb=Q_BORDER, lw=0.6)
        set_fill(c, (0,0,0))
        p.drawOn(c, x + PAD, qbox_bottom + PAD)
        cy = qbox_bottom - 3

        # Answer box
        ans_bottom = cy - ans_h_each
        if is_ms:
            # Green filled answer box
            filled_rect(c, x, ans_bottom, w, ans_h_each,
                        fill_rgb=GRN_BG, stroke_rgb=GRN, lw=0.6)
            ap = Paragraph(f'✓  {ans}', ANS_STYLE)
            ap_w, ap_h = ap.wrap(w - PAD*2, ans_h_each - PAD*2)
            ap.drawOn(c, x + PAD, ans_bottom + PAD)
        else:
            # Empty answer box (light border only)
            outline_rect(c, x, ans_bottom, w, ans_h_each, stroke_rgb=GREY, lw=0.5)

        cy = ans_bottom - ITEM_GAP

# ── Half-page builder ─────────────────────────────────────────────────────────
def draw_half(c, lp_data, region_top, region_bot, meta, show_ll, is_ms):
    """
    region_top, region_bot: y coordinates (bottom-up) bounding this LP half.
    show_ll: True for LP1 only.
    """
    PAD = 10

    # Draw chart — right column, full height of region
    chart_h = region_top - region_bot - 2*PAD
    draw_chart(c, lp_data['chart'], CHART_X, region_bot + PAD,
               CHART_W, chart_h)

    # Chart label below (centred)
    c.setFont('LibSans', 7)
    set_fill(c, GREY_TXT)
    label = lp_data.get('chart_label', '')
    tw = c.stringWidth(label, 'LibSans', 7)
    c.drawString(CHART_X + (CHART_W - tw)/2, region_bot + 2, label)

    # Learning Label (LP1 only)
    q_top = region_top - PAD
    if show_ll:
        ll_h = draw_ll(c, LL_X, region_top - PAD,
                       meta['date'], meta['topic'], meta['lf'], meta['ican'])
        q_top = region_top - PAD - ll_h - 8

    # Questions — left column
    q_bot    = region_bot + PAD
    q_avail  = q_top - q_bot
    draw_questions(c, Q_X, q_top, Q_W, q_avail,
                   lp_data['intro'], lp_data['qs'], is_ms)

# ── Cut line ──────────────────────────────────────────────────────────────────
def draw_cut_line(c):
    set_stroke(c, (0.7, 0.7, 0.7))
    c.setLineWidth(0.5)
    c.setDash([4, 4], 0)
    c.line(0, CUT_Y, W, CUT_Y)
    c.setDash()
    # Scissors symbol
    c.setFont('LibSans', 8)
    set_fill(c, (0.6, 0.6, 0.6))
    c.drawString(4, CUT_Y + 2, '✂')

# ── LP data ───────────────────────────────────────────────────────────────────
LP = {
17: {
    'date': '29/06/2026', 'topic': 'Statistics',
    'lf':   'LF: To read and interpret data from pictograms, bar charts and tables.',
    'ican': ['I can read values from a pictogram using the key.',
             'I can read values from a bar chart and a two-way table.'],
    'lp1': {
        'chart': 'c1_ido1_pictogram.png',
        'chart_label': 'Favourite sports in Year 4',
        'intro': 'Use the pictogram to answer the questions.',
        'qs': [
            ('How many pupils chose basketball?',
             '6 pupils  (3 symbols × 2)'),
            ('How many pupils chose football and volleyball altogether?',
             '12 + 8 = 20 pupils'),
            ('How many MORE pupils chose swimming than capoeira?',
             '10 − 4 = 6 more pupils'),
        ],
    },
    'lp2': {
        'chart': 'c2_ido1_table.png',
        'chart_label': 'Average daily sunshine hours',
        'intro': 'Use the table to answer the questions.',
        'qs': [
            ('How many hours of sunshine does England get in winter?',
             '2 hours'),
            ('What is the total sunshine across both countries in spring?',
             '5 + 7 = 12 hours'),
            ('Which country has more sunshine overall? By how many hours?',
             'Brazil — 31 vs 19 = 12 more hours'),
            ('In which season are England and Brazil most similar?',
             'Summer — just 1 hour apart (8 vs 9)'),
        ],
    },
},
18: {
    'date': '30/06/2026', 'topic': 'Statistics',
    'lf':   'LF: To calculate sums and differences from charts and compare two data sets.',
    'ican': ['I can add and subtract values read from a bar chart.',
             'I can compare two data sets and describe differences.'],
    'lp1': {
        'chart': 'c1_ido1_bar_chart.png',
        'chart_label': 'Animals counted at an Amazon river each day',
        'intro': 'Use the bar chart to answer the questions.',
        'qs': [
            ('How many animals were counted on Tuesday and Wednesday altogether?',
             '24 + 15 = 39 animals'),
            ('How many MORE were counted on Thursday than Monday?',
             '30 − 18 = 12 more animals'),
            ('What is the total for all five days?',
             '18 + 24 + 15 + 30 + 21 = 108 animals'),
        ],
    },
    'lp2': {
        'chart': 'c2_ido1_double_bar.png',
        'chart_label': 'Average temperature — London and Rio de Janeiro',
        'intro': 'Use the double bar chart to answer the questions.',
        'qs': [
            ('What is the temperature difference between London and Rio in winter?',
             '22 − 6 = 16°C'),
            ('In which season are the two cities closest in temperature?',
             'Summer — gap of 10°C'),
            ("What is London's temperature range across the year?",
             '18 − 6 = 12°C range'),
            ('Write a statement comparing the two cities using data from the chart.',
             'Any valid statement using values from the chart.'),
        ],
    },
},
19: {
    'date': '01/07/2026', 'topic': 'Statistics',
    'lf':   'LF: To read and interpret line graphs, including estimating between points.',
    'ican': ['I can read values from a line graph at labelled points.',
             'I can estimate values between two labelled points on a line graph.'],
    'lp1': {
        'chart': 'c1_ido1_line_graph.png',
        'chart_label': 'Temperature in Bristol on a June day',
        'intro': 'Use the line graph to answer the questions.',
        'qs': [
            ('What was the temperature at 10:00?',
             '17°C'),
            ('At what time was Bristol warmest? What was the temperature?',
             '14:00 — 24°C'),
            ('Between which two readings did the temperature rise the most?',
             '10:00 to 12:00 — rose by 4°C'),
        ],
    },
    'lp2': {
        'chart': 'c2_ido1_line_graph.png',
        'chart_label': 'Temperature in São Paulo on a June day',
        'intro': 'Use the São Paulo line graph to answer the questions.',
        'qs': [
            ('What was the temperature at 12:00?',
             '30°C'),
            ('Estimate the temperature at 09:00.',
             'About 24°C — halfway between 22°C and 26°C'),
            ('Estimate the temperature at 11:00.',
             'About 28°C — halfway between 26°C and 30°C'),
            ('At approximately what time was it 30°C on the way back down?',
             'Around 15:00 — the line falls from 32°C to 29°C'),
        ],
    },
},
}


# ── T6W6 LP data ──────────────────────────────────────────────────────────────
# L20: draw line graph (Bristol July temps)
# L21: draw bar chart (after-school activities)
# L22: evaluate claims (standard chart + questions — no change)
# L23: tally + draw bar chart (Year 5 transition survey)
LP.update({
20: {
    'date': '06/07/2026', 'topic': 'Statistics',
    'lf':   'LF: To draw an accurate line graph from a given data set.',
    'ican': ['I can choose a suitable scale and write the values on the y-axis.',
             'I can plot data points accurately and join them with straight lines.'],
    'lp1': {
        'lp_type':      'draw_graph',
        'intro':        'Use the data in the table to draw a line graph in the space below.',
        'table_headers':['Time', 'Temperature (\u00b0C)'],
        'table_rows':   [['6 am', 15], ['9 am', 18], ['12 pm', 23], ['3 pm', 22], ['6 pm', 19]],
        'ax': {
            'n_x': 5, 'n_y': 5,
            'ms_x_labels': ['6 am', '9 am', '12 pm', '3 pm', '6 pm'],
            'ms_y_vals':   [15, 18, 23, 22, 19],
            'ms_y_min': 0, 'ms_y_max': 25, 'ms_y_step': 5,
            'ms_x_label': 'Time', 'ms_y_label': 'Temperature (\u00b0C)',
            'ms_title': 'Temperature in Bristol on a July day',
        },
        'qs': [
            ('What was the temperature at 12 pm?', '23\u00b0C'),
            ('How much warmer was it at 12 pm than at 6 am?', '23 \u2212 15 = 8\u00b0C warmer'),
            ('Describe the trend across the day.',
             'Temperature rises to a peak at noon then falls in the afternoon.'),
        ],
    },
    'lp2': {
        'intro': 'Look at your completed graph and answer these questions in your book.',
        'qs': [
            ('At what time was it warmest?  What was the temperature?',
             '12 pm \u2014 23\u00b0C'),
            ('Compare your Bristol July graph with the London January graph from the lesson.\n'
             'Write one similarity and one difference.',
             'Similarity: both peak at midday. Difference: Bristol July is much warmer.'),
        ],
    },
},
21: {
    'date': '08/07/2026', 'topic': 'Statistics',
    'lf':   'LF: To draw an accurate bar chart from a given data set.',
    'ican': ['I can choose a suitable scale for a bar chart and write values on the y-axis.',
             'I can draw bars to the correct height and label my chart fully.'],
    'lp1': {
        'lp_type':      'draw_bar',
        'intro':        'Use the data in the table to draw a bar chart in the space below.',
        'table_headers':['Activity', 'Number of pupils'],
        'table_rows':   [['Football', 8], ['Reading', 5], ['Gaming', 7],
                         ['Cooking', 4], ['Art', 2]],
        'ax': {
            'n_x': 5, 'n_y': 5,
            'ms_x_labels': ['Football', 'Reading', 'Gaming', 'Cooking', 'Art'],
            'ms_y_vals':   [8, 5, 7, 4, 2],
            'ms_y_min': 0, 'ms_y_max': 10, 'ms_y_step': 2,
            'ms_x_label': 'Activity', 'ms_y_label': 'Number of pupils',
            'ms_title': 'Favourite after-school activities \u2014 Maple class',
        },
        'qs': [
            ('Which activity was most popular?',  'Football \u2014 8 pupils'),
            ('How many more pupils chose football than art?', '8 \u2212 2 = 6 more'),
            ('How many pupils are in the class altogether?', '8+5+7+4+2 = 26'),
        ],
    },
    'lp2': {
        'intro': 'Look at your completed chart and answer in your book.',
        'qs': [
            ('Write one statement about your bar chart using a number from the data as evidence.',
             'Any valid statement with a data value cited.'),
            ('Could you use a pictogram for this data?  '
             'What key value would work best and why?',
             'Yes.  Key = 2 works (all values are even or small). '
             'Key = 5 would leave 7 and 4 hard to show exactly.'),
        ],
    },
},
22: {
    'date': '09/07/2026', 'topic': 'Statistics',
    'lf':   'LF: To evaluate claims about data using evidence from charts and tables.',
    'ican': ['I can decide whether a claim is true or false using values from a chart.',
             'I can write a verdict with evidence: "I agree/disagree because\u2026"'],
    'lp1': {
        'chart':       'c1_ido1_double_bar.png',
        'chart_label': 'Average monthly rainfall (mm) \u2014 Bristol vs Manaus',
        'intro':       'For each claim write Agree, Disagree or Not enough information. Show your evidence.',
        'qs': [
            ('Claim: \u201cManaus gets more rain than Bristol in every month shown.\u201d',
             'Agree \u2014 every Manaus bar is taller.  e.g. Jan: 260 > 89.'),
            ('Claim: \u201cBristol and Manaus get a similar amount of rain in June.\u201d',
             'Disagree \u2014 Bristol 45mm, Manaus 100mm.  100 \u2212 45 = 55mm difference.'),
            ('Claim: \u201cManaus gets more than 200mm of rain in every month from Jan to Jun.\u201d',
             'Disagree \u2014 June is 100mm, which is less than 200mm.'),
        ],
    },
    'lp2': {
        'chart':       'c2_ido1_table.png',
        'chart_label': 'Hours of daylight \u2014 Bristol and S\u00e3o Paulo, by season',
        'intro':       'For each claim write Agree, Disagree or Not enough information. Show your evidence.',
        'qs': [
            ('Claim: \u201cBristol always has fewer hours of daylight than S\u00e3o Paulo.\u201d',
             'Disagree \u2014 in summer Bristol has 17h, S\u00e3o Paulo 11h.  Bristol has MORE in summer.'),
            ('Claim: \u201cThe total daylight hours are the same for both cities.\u201d',
             'Disagree \u2014 Bristol 8+12+17+12=49h.  S\u00e3o Paulo 11+12+11+12=46h.'),
            ('Claim: \u201cS\u00e3o Paulo has the same hours of daylight in spring and autumn.\u201d',
             'Agree \u2014 both show 12h.'),
        ],
    },
},
23: {
    'date': '11/07/2026', 'topic': 'Statistics',
    'lf':   'LF: To complete the full data cycle \u2014 collect, tally, represent and analyse.',
    'ican': ['I can tally class data accurately and choose a suitable representation.',
             'I can draw a bar chart from my own data and answer questions from it.'],
    'lp1': {
        'lp_type':     'tally_draw',
        'survey_q':    'How are you feeling about moving to Year 5?',
        'intro':       'Tally each response as your teacher counts the hands.',
        'tally_categories': ['Very excited', 'Excited', 'A bit nervous', 'Not sure'],
        'ms_tallies':  [12, 8, 4, 2],
        'ax': {
            'n_x': 4, 'n_y': 6,
            'ms_x_labels': ['Very\nexcited', 'Excited', 'A bit\nnervous', 'Not\nsure'],
            'ms_y_vals':   [12, 8, 4, 2],
            'ms_y_min': 0, 'ms_y_max': 14, 'ms_y_step': 2,
            'ms_x_label': 'How I feel', 'ms_y_label': 'Number of pupils',
            'ms_title': 'How Maple class feels about moving to Year 5',
        },
        'qs': [
            ('Which feeling was chosen by most pupils?',
             'Depends on class data \u2014 pupils read from their own chart.'),
            ('How many pupils chose \u201cVery excited\u201d or \u201cExcited\u201d altogether?',
             'Pupils add their two values.'),
            ('What does your chart tell you about how Maple class feels about Year 5?',
             'Pupils write their own conclusion using data from their chart.'),
        ],
    },
    'lp2': {
        'intro': 'Write your answers in your book.',
        'qs': [
            ('How many pupils are in your class altogether?  '
             'Check your tally totals add up to this.',
             '26 (all tallies should sum to 26)'),
            ('Write two or three sentences about what your chart shows.',
             'Pupils write their own summary.'),
        ],
    },
},
})

DAYS = {17: 'Monday',  18: 'Tuesday',  19: 'Wednesday',
        20: 'Monday',  21: 'Wednesday', 22: 'Thursday',  23: 'Friday'}

WEEK = {17: 'T6W5', 18: 'T6W5', 19: 'T6W5',
        20: 'T6W6', 21: 'T6W6', 22: 'T6W6', 23: 'T6W6'}


# ── Blank axes for drawing lessons ────────────────────────────────────────────
# Pupils write in all values, labels and title themselves.

def _blank_axes_png(n_x, n_y, chart_type, is_ms, ms_data, tmp_path):
    """
    Render a blank (or marked-up) axes PNG for pupil drawing.
    chart_type: 'line' or 'bar'
    is_ms: if True, plot the completed graph in the ms colour
    ms_data: dict with ms_y_vals, ms_y_min, ms_y_max, ms_y_step, ms_x_labels etc.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np, io, tempfile

    fig, ax = plt.subplots(figsize=(6.5, 2.8), dpi=180)
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    if is_ms:
        y_min  = ms_data.get('ms_y_min', 0)
        y_max  = ms_data.get('ms_y_max', 10)
        y_step = ms_data.get('ms_y_step', 2)
        x_labs = ms_data.get('ms_x_labels', [str(i) for i in range(n_x)])
        y_vals = ms_data.get('ms_y_vals', [])
        x_lab  = ms_data.get('ms_x_label', '')
        y_lab  = ms_data.get('ms_y_label', '')
        title  = ms_data.get('ms_title', '')

        ax.set_xlim(-0.5, n_x - 0.5)
        ax.set_ylim(y_min, y_max)
        ax.set_xticks(range(n_x))
        ax.set_xticklabels(x_labs, fontsize=7)
        ax.set_yticks(range(y_min, y_max + 1, y_step))
        ax.tick_params(labelsize=7)
        ax.set_xlabel(x_lab, fontsize=7, labelpad=2)
        ax.set_ylabel(y_lab, fontsize=7, labelpad=2)
        if title:
            ax.set_title(title, fontsize=7, pad=4)
        ax.grid(True, linewidth=0.4, color='#AAAAAA', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if chart_type == 'line' and y_vals:
            ax.plot(range(n_x), y_vals, color='#C83030', linewidth=1.5,
                    marker='x', markersize=6, markeredgewidth=2, zorder=3)
        elif chart_type == 'bar' and y_vals:
            ax.bar(range(n_x), y_vals, color='#1798d3', alpha=0.85,
                   edgecolor='#0f6fa0', linewidth=0.6, width=0.6)

    else:
        # Fully blank — pupils write everything
        # Use fixed number of gridlines as visual reference
        n_y_grid = n_y + 1  # one extra so bottom = 0
        ax.set_xlim(-0.5, n_x - 0.5)
        ax.set_ylim(0, n_y_grid)

        # Axis lines thick
        ax.spines['left'].set_linewidth(1.8)
        ax.spines['bottom'].set_linewidth(1.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Set explicit tick positions so vertical gridlines align with data points
        ax.set_xticks(range(n_x))

        # Horizontal gridlines across full width
        for gy in range(1, n_y_grid + 1):
            ax.axhline(gy, color='#CCCCCC', linewidth=0.5, alpha=0.7)

        # Vertical gridlines up from every x tick — for ALL chart types
        # Helps pupils plot points accurately above each category/time mark
        for gx in range(n_x):
            ax.axvline(gx, color='#CCCCCC', linewidth=0.5, alpha=0.6)

        # No tick labels — pupils write their own
        # Set a large labelpad so matplotlib reserves space below x-axis
        # even with empty tick labels. bbox_inches='tight' then includes it.
        ax.set_xticklabels([''] * n_x)
        ax.set_yticks(range(n_y_grid + 1))
        ax.set_yticklabels([''] * (n_y_grid + 1))
        ax.tick_params(axis='x', pad=4, length=5, width=1.2)
        ax.tick_params(axis='y', pad=4, length=5, width=1.2)

    plt.tight_layout(pad=0.4)
    fig.savefig(tmp_path, format='png', dpi=180, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)


def _place_image(c, img_path, x, y_bottom, max_w, max_h):
    from PIL import Image as PILImage2
    img = PILImage2.open(img_path)
    iw, ih = img.size
    aspect = iw / ih
    w = max_w
    h = max_w / aspect
    if h > max_h:
        h = max_h
        w = max_h * aspect
    dx = (max_w - w) / 2
    c.drawImage(img_path, x + dx, y_bottom, w, h,
                preserveAspectRatio=True, mask='auto')


def draw_half_draw(c, lp_data, region_top, region_bot, meta, show_ll, is_ms):
    """Vertical layout for line graph drawing LPs."""
    import tempfile, os

    PAD    = 8
    FULL_W = CHART_X + CHART_W - Q_X   # full usable width
    LL_COL = 165                        # LL column width
    TBL_X  = Q_X + LL_COL + 6          # data table starts here
    TBL_W  = FULL_W - LL_COL - 6
    TOP_H  = 80                         # height for LL + table row

    cy = region_top - PAD

    # ── LL (top-left) ─────────────────────────────────────────────────────────
    if show_ll:
        ll_h = draw_ll(c, Q_X, cy, meta['date'], meta['topic'],
                       meta['lf'], meta['ican'])
    else:
        ll_h = TOP_H

    # ── Data table (top-right, beside LL) ─────────────────────────────────────
    hdrs = lp_data.get('table_headers', [])
    rows = lp_data.get('table_rows', [])
    if hdrs and rows:
        ROW_H  = min(13, (TOP_H) // (len(rows) + 1))
        COL_W  = [TBL_W * 0.55, TBL_W * 0.42]
        tbl_y  = cy
        filled_rect(c, TBL_X, tbl_y - ROW_H, sum(COL_W), ROW_H,
                    fill_rgb=(0.09, 0.60, 0.83), stroke_rgb=None)
        for ci, hdr in enumerate(hdrs[:2]):
            c.setFont('LibSansBold', 7.5); set_fill(c, (1, 1, 1))
            c.drawString(TBL_X + sum(COL_W[:ci]) + 3, tbl_y - ROW_H + 3, hdr)
        tbl_y -= ROW_H
        for ri, row in enumerate(rows):
            fill = (0.93, 0.97, 1.0) if ri % 2 == 0 else (1, 1, 1)
            filled_rect(c, TBL_X, tbl_y - ROW_H, sum(COL_W), ROW_H,
                        fill_rgb=fill, stroke_rgb=(0.78, 0.78, 0.78), lw=0.4)
            for ci, val in enumerate(row[:2]):
                c.setFont('LibSans', 7.5); set_fill(c, (0.1, 0.1, 0.1))
                c.drawString(TBL_X + sum(COL_W[:ci]) + 3, tbl_y - ROW_H + 3, str(val))
            tbl_y -= ROW_H

    # ── Intro text ─────────────────────────────────────────────────────────────
    intro_y = cy - max(ll_h, TOP_H) - 3
    intro_p = Paragraph(lp_data.get('intro', ''), INTRO_STYLE)
    _, intro_h = intro_p.wrap(FULL_W, 60)
    intro_p.drawOn(c, Q_X, intro_y - intro_h)
    axes_top = intro_y - intro_h - 4

    # ── Blank (or completed) axes — full width ─────────────────────────────────
    # q_top = where Q1 will start.  axes_bot = bottom of axes image.
    # LABEL_GAP is the explicit >1cm space for pupils to write x-axis labels.
    LABEL_GAP   = 35
    q_section_h = len(lp_data.get('qs', [])) * 30 + 6
    q_top    = region_bot + PAD + q_section_h
    axes_bot = q_top + LABEL_GAP
    axes_h   = axes_top - axes_bot

    tmp_png = '/tmp/_lp_axes_tmp.png'
    ax_cfg  = lp_data.get('ax', {})
    _blank_axes_png(ax_cfg.get('n_x', 5), ax_cfg.get('n_y', 5),
                    'line', is_ms, ax_cfg, tmp_png)
    _place_image(c, tmp_png, Q_X, axes_bot, FULL_W, max(axes_h, 40))

    # ── Questions at bottom ────────────────────────────────────────────────────
    cy2 = q_top
    for qi, (qt, ans) in enumerate(lp_data.get('qs', [])):
        qp = Paragraph(f'{qi+1}.  {qt}', Q_STYLE)
        _, qph = qp.wrap(FULL_W - 6, 200)
        qbox_h = qph + 7
        filled_rect(c, Q_X, cy2 - qbox_h, FULL_W, qbox_h,
                    fill_rgb=Q_BG, stroke_rgb=Q_BORDER, lw=0.6)
        set_fill(c, (0, 0, 0)); qp.drawOn(c, Q_X + 3, cy2 - qbox_h + 3)
        cy2 -= qbox_h + 2
        ans_h = 16
        if is_ms:
            filled_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h,
                        fill_rgb=GRN_BG, stroke_rgb=GRN, lw=0.6)
            ap = Paragraph(f'\u2713  {ans}', ANS_STYLE)
            ap.wrap(FULL_W - 6, ans_h); ap.drawOn(c, Q_X + 3, cy2 - ans_h + 3)
        else:
            outline_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h, stroke_rgb=GREY, lw=0.5)
        cy2 -= ans_h + 2


def draw_half_bar(c, lp_data, region_top, region_bot, meta, show_ll, is_ms):
    """Vertical layout for bar chart drawing LPs."""
    import tempfile, os

    PAD    = 8
    FULL_W = CHART_X + CHART_W - Q_X
    LL_COL = 165
    TBL_X  = Q_X + LL_COL + 6
    TBL_W  = FULL_W - LL_COL - 6
    TOP_H  = 80

    cy = region_top - PAD

    if show_ll:
        ll_h = draw_ll(c, Q_X, cy, meta['date'], meta['topic'],
                       meta['lf'], meta['ican'])
    else:
        ll_h = TOP_H

    hdrs = lp_data.get('table_headers', [])
    rows = lp_data.get('table_rows', [])
    if hdrs and rows:
        ROW_H = min(13, TOP_H // (len(rows) + 1))
        COL_W = [TBL_W * 0.58, TBL_W * 0.38]
        tbl_y = cy
        filled_rect(c, TBL_X, tbl_y - ROW_H, sum(COL_W), ROW_H,
                    fill_rgb=(0.09, 0.60, 0.83), stroke_rgb=None)
        for ci, hdr in enumerate(hdrs[:2]):
            c.setFont('LibSansBold', 7.5); set_fill(c, (1, 1, 1))
            c.drawString(TBL_X + sum(COL_W[:ci]) + 3, tbl_y - ROW_H + 3, hdr)
        tbl_y -= ROW_H
        for ri, row in enumerate(rows):
            fill = (0.93, 0.97, 1.0) if ri % 2 == 0 else (1, 1, 1)
            filled_rect(c, TBL_X, tbl_y - ROW_H, sum(COL_W), ROW_H,
                        fill_rgb=fill, stroke_rgb=(0.78, 0.78, 0.78), lw=0.4)
            for ci, val in enumerate(row[:2]):
                c.setFont('LibSans', 7.5); set_fill(c, (0.1, 0.1, 0.1))
                c.drawString(TBL_X + sum(COL_W[:ci]) + 3, tbl_y - ROW_H + 3, str(val))
            tbl_y -= ROW_H

    intro_y = cy - max(ll_h, TOP_H) - 3
    intro_p = Paragraph(lp_data.get('intro', ''), INTRO_STYLE)
    _, intro_h = intro_p.wrap(FULL_W, 60)
    intro_p.drawOn(c, Q_X, intro_y - intro_h)
    axes_top = intro_y - intro_h - 4

    LABEL_GAP   = 35
    q_section_h = len(lp_data.get('qs', [])) * 30 + 6
    q_top    = region_bot + PAD + q_section_h
    axes_bot = q_top + LABEL_GAP
    axes_h   = axes_top - axes_bot

    tmp_png = '/tmp/_lp_axes_tmp.png'
    ax_cfg  = lp_data.get('ax', {})
    _blank_axes_png(ax_cfg.get('n_x', 5), ax_cfg.get('n_y', 5),
                    'bar', is_ms, ax_cfg, tmp_png)
    _place_image(c, tmp_png, Q_X, axes_bot, FULL_W, max(axes_h, 40))

    cy2 = q_top
    for qi, (qt, ans) in enumerate(lp_data.get('qs', [])):
        qp = Paragraph(f'{qi+1}.  {qt}', Q_STYLE)
        _, qph = qp.wrap(FULL_W - 6, 200)
        qbox_h = qph + 7
        filled_rect(c, Q_X, cy2 - qbox_h, FULL_W, qbox_h,
                    fill_rgb=Q_BG, stroke_rgb=Q_BORDER, lw=0.6)
        set_fill(c, (0, 0, 0)); qp.drawOn(c, Q_X + 3, cy2 - qbox_h + 3)
        cy2 -= qbox_h + 2
        ans_h = 16
        if is_ms:
            filled_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h,
                        fill_rgb=GRN_BG, stroke_rgb=GRN, lw=0.6)
            ap = Paragraph(f'\u2713  {ans}', ANS_STYLE)
            ap.wrap(FULL_W - 6, ans_h); ap.drawOn(c, Q_X + 3, cy2 - ans_h + 3)
        else:
            outline_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h, stroke_rgb=GREY, lw=0.5)
        cy2 -= ans_h + 2


def draw_half_tally(c, lp_data, region_top, region_bot, meta, show_ll, is_ms):
    """Vertical layout for tally + bar chart LPs (L23)."""
    import tempfile, os

    PAD    = 8
    FULL_W = CHART_X + CHART_W - Q_X

    cy = region_top - PAD

    # ── LL ────────────────────────────────────────────────────────────────────
    if show_ll:
        ll_h = draw_ll(c, Q_X, cy, meta['date'], meta['topic'],
                       meta['lf'], meta['ican'])
        cy -= ll_h + 4

    # ── Survey question ────────────────────────────────────────────────────────
    survey_q = lp_data.get('survey_q', '')
    if survey_q:
        sq_p = Paragraph(f'<b>{survey_q}</b>', ParagraphStyle('SQ',
            fontName='LibSansBold', fontSize=8, leading=11, textColor=(0.05,0.05,0.05)))
        _, sq_h = sq_p.wrap(FULL_W, 40)
        sq_p.drawOn(c, Q_X, cy - sq_h)
        cy -= sq_h + 4

    # ── Intro ─────────────────────────────────────────────────────────────────
    intro_p = Paragraph(lp_data.get('intro', ''), INTRO_STYLE)
    _, ih = intro_p.wrap(FULL_W, 40)
    intro_p.drawOn(c, Q_X, cy - ih)
    cy -= ih + 4

    # ── Tally table ───────────────────────────────────────────────────────────
    cats   = lp_data.get('tally_categories', [])
    ms_t   = lp_data.get('ms_tallies', [0] * len(cats))
    ROW_H  = 14
    C1, C2, C3 = FULL_W * 0.38, FULL_W * 0.38, FULL_W * 0.22
    filled_rect(c, Q_X, cy - ROW_H, FULL_W, ROW_H,
                fill_rgb=(0.09, 0.60, 0.83), stroke_rgb=None)
    for txt, x_off in [('How I feel', Q_X + 3),
                        ('Tally', Q_X + C1 + 3),
                        ('Total', Q_X + C1 + C2 + 3)]:
        c.setFont('LibSansBold', 7.5); set_fill(c, (1, 1, 1))
        c.drawString(x_off, cy - ROW_H + 3, txt)
    cy -= ROW_H
    for ri, (cat, mt) in enumerate(zip(cats, ms_t)):
        fill = (0.93, 0.97, 1.0) if ri % 2 == 0 else (1, 1, 1)
        filled_rect(c, Q_X, cy - ROW_H, FULL_W, ROW_H,
                    fill_rgb=fill, stroke_rgb=(0.75, 0.75, 0.75), lw=0.4)
        c.setFont('LibSans', 7.5); set_fill(c, (0.1, 0.1, 0.1))
        c.drawString(Q_X + 3, cy - ROW_H + 3, cat)
        if is_ms:
            tally_str = ('\u2225 ' * (mt // 5) + '| ' * (mt % 5)).strip()
            c.drawString(Q_X + C1 + 3, cy - ROW_H + 3, tally_str)
            c.drawString(Q_X + C1 + C2 + 3, cy - ROW_H + 3, str(mt))
        cy -= ROW_H
    cy -= 4

    # ── Blank/completed bar chart ─────────────────────────────────────────────
    LABEL_GAP   = 35
    q_section_h = len(lp_data.get('qs', [])) * 30 + 4
    q_top    = region_bot + PAD + q_section_h
    axes_bot = q_top + LABEL_GAP
    axes_h   = cy - axes_bot

    tmp_png = '/tmp/_lp_axes_tmp.png'
    ax_cfg  = lp_data.get('ax', {})
    _blank_axes_png(ax_cfg.get('n_x', 4), ax_cfg.get('n_y', 6),
                    'bar', is_ms, ax_cfg, tmp_png)
    _place_image(c, tmp_png, Q_X, axes_bot, FULL_W, max(axes_h, 40))

    # ── Questions ─────────────────────────────────────────────────────────────
    cy2 = q_top
    for qi, (qt, ans) in enumerate(lp_data.get('qs', [])):
        qp = Paragraph(f'{qi+1}.  {qt}', Q_STYLE)
        _, qph = qp.wrap(FULL_W - 6, 200)
        qbox_h = qph + 7
        filled_rect(c, Q_X, cy2 - qbox_h, FULL_W, qbox_h,
                    fill_rgb=Q_BG, stroke_rgb=Q_BORDER, lw=0.6)
        set_fill(c, (0, 0, 0)); qp.drawOn(c, Q_X + 3, cy2 - qbox_h + 3)
        cy2 -= qbox_h + 2
        ans_h = 16
        if is_ms:
            filled_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h,
                        fill_rgb=GRN_BG, stroke_rgb=GRN, lw=0.6)
            ap = Paragraph(f'\u2713  {ans}', ANS_STYLE)
            ap.wrap(FULL_W - 6, ans_h); ap.drawOn(c, Q_X + 3, cy2 - ans_h + 3)
        else:
            outline_rect(c, Q_X, cy2 - ans_h, FULL_W, ans_h, stroke_rgb=GREY, lw=0.5)
        cy2 -= ans_h + 2


def draw_half_lp2_ext(c, lp_data, region_top, region_bot, meta, show_ll, is_ms):
    """Simple extension LP2 for drawing lessons — questions only, no drawing."""
    PAD    = 8
    FULL_W = CHART_X + CHART_W - Q_X
    cy     = region_top - PAD

    intro_p = Paragraph(lp_data.get('intro', 'Going further'), INTRO_STYLE)
    _, ih   = intro_p.wrap(FULL_W, 60)
    intro_p.drawOn(c, Q_X, cy - ih)
    cy -= ih + 6

    for qi, (qt, ans) in enumerate(lp_data.get('qs', [])):
        qp = Paragraph(f'{qi+1}.  {qt}', Q_STYLE)
        _, qph = qp.wrap(FULL_W - 6, 200)
        qbox_h = qph + 8
        filled_rect(c, Q_X, cy - qbox_h, FULL_W, qbox_h,
                    fill_rgb=Q_BG, stroke_rgb=Q_BORDER, lw=0.6)
        set_fill(c, (0, 0, 0)); qp.drawOn(c, Q_X + 3, cy - qbox_h + 4)
        cy -= qbox_h + 3
        ans_h = 36
        if is_ms:
            filled_rect(c, Q_X, cy - ans_h, FULL_W, ans_h,
                        fill_rgb=GRN_BG, stroke_rgb=GRN, lw=0.6)
            ap = Paragraph(f'\u2713  {ans}', ANS_STYLE)
            ap.wrap(FULL_W - 6, ans_h - 4); ap.drawOn(c, Q_X + 3, cy - ans_h + 4)
        else:
            outline_rect(c, Q_X, cy - ans_h, FULL_W, ans_h, stroke_rgb=GREY, lw=0.5)
        cy -= ans_h + 4

def build(lesson_num):
    d   = LP[lesson_num]
    day = DAYS[lesson_num]
    wk  = WEEK.get(lesson_num, 'T6W5')
    _dn = {'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5}
    out = f'/tmp/claude_work/{wk} - {_dn.get(day,1)} - {day} - MathsLP.pdf'

    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle(f'{wk} {day} L{lesson_num} — Statistics LP')

    is_draw  = d['lp1'].get('lp_type') == 'draw_graph'
    is_bar   = d['lp1'].get('lp_type') == 'draw_bar'
    is_tally = d['lp1'].get('lp_type') == 'tally_draw'

    for page_type in ['standard', 'adapted', 'marking']:
        is_ms = (page_type == 'marking')
        c.setPageSize(A4)
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        if is_draw:
            draw_half_draw(c, d['lp1'], H - M, CUT_Y + M, d,
                           show_ll=True, is_ms=is_ms)
            draw_half_lp2_ext(c, d['lp2'], CUT_Y - M, M, d,
                              show_ll=False, is_ms=is_ms)
        elif is_bar:
            draw_half_bar(c, d['lp1'], H - M, CUT_Y + M, d,
                          show_ll=True, is_ms=is_ms)
            draw_half_lp2_ext(c, d['lp2'], CUT_Y - M, M, d,
                              show_ll=False, is_ms=is_ms)
        elif is_tally:
            draw_half_tally(c, d['lp1'], H - M, CUT_Y + M, d,
                            show_ll=True, is_ms=is_ms)
            draw_half_lp2_ext(c, d['lp2'], CUT_Y - M, M, d,
                              show_ll=False, is_ms=is_ms)
        else:
            draw_half(c, d['lp1'], H - M, CUT_Y + M, d,
                      show_ll=True, is_ms=is_ms)
            draw_half(c, d['lp2'], CUT_Y - M, M, d,
                      show_ll=False, is_ms=is_ms)

        draw_cut_line(c)
        c.showPage()

    c.save()
    print(f'Saved: {out}')
    return out

# ── PPTX wrapper for inject_lp_previews.py ────────────────────────────────────
def make_pptx_wrapper(pdf_path, pptx_path):
    """
    Converts each PDF page to an image and creates a 3-slide A4 PPTX.
    inject_lp_previews.py will then crop top/bottom halves for the preview.
    """
    import subprocess, tempfile, glob
    from pptx import Presentation
    from pptx.util import Inches, Emu

    SLIDE_W, SLIDE_H = 7.5, 10.833

    # Rasterise PDF pages to images
    tmp = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-jpeg', '-r', '150', pdf_path,
                    os.path.join(tmp, 'page')], capture_output=True)
    pages = sorted(glob.glob(os.path.join(tmp, 'page-*.jpg')))
    if not pages:
        pages = sorted(glob.glob(os.path.join(tmp, 'page*.jpg')))

    prs = Presentation()
    prs.slide_width  = Emu(int(SLIDE_W * 914400))
    prs.slide_height = Emu(int(SLIDE_H * 914400))
    blank = prs.slide_layouts[6]

    for page_img in pages[:3]:
        sld = prs.slides.add_slide(blank)
        sld.background.fill.solid()
        sld.background.fill.fore_color.rgb = __import__(
            'pptx.dml.color', fromlist=['RGBColor']).RGBColor(0xFF,0xFF,0xFF)
        sld.shapes.add_picture(page_img,
                               Emu(0), Emu(0),
                               Emu(int(SLIDE_W*914400)),
                               Emu(int(SLIDE_H*914400)))

    prs.save(pptx_path)
    print(f'PPTX wrapper: {pptx_path}  ({len(pages)} slides)')


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    pdf  = build(n)
    day  = DAYS[n]
    wk   = WEEK.get(n, 'T6W5')
    _dn  = {'Monday':1,'Tuesday':2,'Wednesday':3,'Thursday':4,'Friday':5}
    pptx = f'/tmp/claude_work/{wk} - {_dn.get(day,1)} - {day} - MathsLP.pptx'
    make_pptx_wrapper(pdf, pptx)
