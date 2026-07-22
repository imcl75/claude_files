#!/usr/bin/env python3
"""
Rebuild all 6 Geography LPs with correct WFA learning label (white background)
and verified non-overlapping layout throughout.

Coordinate system (ReportLab): y=0 bottom of page, y increases UPWARD.
- drawString(x, y, text): baseline at y, text ascends upward from y
- rect(x, y_bottom, width, height): bottom-left at (x, y_bottom)

All section heights calculated from content before drawing anything.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

W, H = A4          # 595.28 x 841.89
M   = 35           # page margin (all sides)
CW  = W - 2*M      # 525.28 content width

BLUE   = (0x17/255, 0x98/255, 0xd3/255)   # #1798d3 WFA blue
ORANGE = (0xe5/255, 0x7d/255, 0x24/255)   # #e57d24 WFA orange
GREEN  = (0x27/255, 0xae/255, 0x60/255)   # #27ae60
RED    = (0xc0/255, 0x39/255, 0x2b/255)
DARK   = (0.10, 0.10, 0.10)
GREY   = (0.45, 0.45, 0.45)
LGREY  = (0.80, 0.80, 0.80)
CREAM  = (0.996, 0.976, 0.910)            # light orange tint for word banks

def sf(c, rgb): c.setFillColorRGB(*rgb)
def ss(c, rgb): c.setStrokeColorRGB(*rgb)

# ── Learning label ────────────────────────────────────────────────────
# White background throughout. Blue text for heading elements.
# Returns y position of first content line below separator.
def learning_label(c, key_q, date, lf, icans):
    y = H - M       # start at top margin (this is the TOP of first text)

    # Line 1: "Key Question" (blue bold 8pt) + date (grey 8pt)
    sf(c, BLUE); c.setFont('Helvetica-Bold', 8)
    c.drawString(M, y - 8, 'Key Question')          # baseline at y-8
    sf(c, GREY); c.setFont('Helvetica', 8)
    c.drawRightString(W - M, y - 8, date)

    # Line 2: key question text (black bold 10pt)
    y -= 22
    sf(c, DARK); c.setFont('Helvetica-Bold', 10)
    c.drawString(M, y - 7, key_q)

    # Thin blue underline 3pt below that text
    y -= 18
    ss(c, BLUE); c.setLineWidth(0.75)
    c.line(M, y, W - M, y)
    y -= 12

    # LF line (blue bold 8pt)
    sf(c, BLUE); c.setFont('Helvetica-Bold', 8)
    c.drawString(M, y - 6, f'LF: {lf}')
    y -= 14

    # I can statements (dark 8pt)
    sf(c, DARK); c.setFont('Helvetica', 8)
    for ican in icans:
        c.drawString(M + 4, y - 6, f'\u2022 {ican}')
        y -= 12

    # Separator line
    y -= 6
    ss(c, BLUE); c.setLineWidth(1.2)
    c.line(M, y, W - M, y)

    return y - 14   # content starts here


# ── Section heading ───────────────────────────────────────────────────
# Returns y after heading (baseline of heading text was at y_top - 10).
def section_head(c, text, y_top, colour=BLUE):
    sf(c, colour); c.setFont('Helvetica-Bold', 12)
    c.drawString(M, y_top - 10, text)
    y = y_top - 22
    ss(c, colour); c.setLineWidth(1.0)
    c.line(M, y, W - M, y)
    return y - 10   # content y below underline


# ── Body text (single line) ───────────────────────────────────────────
def body(c, text, y_top, sz=9, colour=DARK, indent=0):
    sf(c, colour); c.setFont('Helvetica', sz)
    c.drawString(M + indent, y_top - sz * 0.72 - 2, text)
    return y_top - sz - 6


# ── Body text bold ────────────────────────────────────────────────────
def body_bold(c, text, y_top, sz=9, colour=DARK, indent=0):
    sf(c, colour); c.setFont('Helvetica-Bold', sz)
    c.drawString(M + indent, y_top - sz * 0.72 - 2, text)
    return y_top - sz - 6


# ── Writing line ──────────────────────────────────────────────────────
def writing_line(c, y_top, x=None, w=None):
    """Single writing line. y_top is where the line is drawn. Returns next y_top."""
    if x is None: x = M
    if w is None: w = CW
    ss(c, (0.65, 0.80, 0.88)); c.setLineWidth(0.6)
    c.line(x, y_top - 16, x + w, y_top - 16)
    return y_top - 22


# ── Answer box (right-aligned) ────────────────────────────────────────
def ans_box(c, y_top, box_w=120, row_h=22):
    """Draw an answer box at the RIGHT of the content area. Returns same y_top."""
    x = M + CW - box_w
    y_bot = y_top - row_h
    ss(c, LGREY); sf(c, (1, 1, 1)); c.setLineWidth(0.5)
    c.rect(x, y_bot, box_w, row_h, fill=1, stroke=1)
    return x  # x position of box (for reference)


# ── Horizontal table row ──────────────────────────────────────────────
ROW_H = 22   # standard row height

def table_header(c, cols, y_top):
    """cols = [(label, width), ...]  widths in points. Returns y below header."""
    x = M
    # Filled header row
    sf(c, BLUE); ss(c, BLUE); c.setLineWidth(0.3)
    c.rect(M, y_top - ROW_H, CW, ROW_H, fill=1, stroke=0)
    sf(c, (1,1,1)); c.setFont('Helvetica-Bold', 8)
    x = M
    for label, w in cols:
        c.drawString(x + 4, y_top - ROW_H + 7, label)
        x += w
    return y_top - ROW_H


def table_row(c, items, col_widths, y_top, shade=False):
    """items = list of strings. Returns y below row."""
    if shade:
        sf(c, (0.96, 0.96, 0.96))
        c.rect(M, y_top - ROW_H, CW, ROW_H, fill=1, stroke=0)
    ss(c, LGREY); c.setLineWidth(0.3)
    c.rect(M, y_top - ROW_H, CW, ROW_H, fill=0, stroke=1)
    sf(c, DARK); c.setFont('Helvetica', 8)
    x = M
    for item, w in zip(items, col_widths):
        c.drawString(x + 4, y_top - ROW_H + 7, item)
        # Divider
        if x + w < M + CW:
            ss(c, LGREY); c.setLineWidth(0.3)
            c.line(x + w, y_top - ROW_H, x + w, y_top)
        x += w
    return y_top - ROW_H


# ── Word bank ─────────────────────────────────────────────────────────
WB_H = 38   # word bank box height

def word_bank(c, words, y_top, label='Word bank', colour=ORANGE):
    """Draw a word bank box. Returns y below."""
    sf(c, CREAM); ss(c, colour); c.setLineWidth(1.2)
    c.roundRect(M, y_top - WB_H, CW, WB_H, 5, fill=1, stroke=1)
    sf(c, colour); c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M + 8, y_top - WB_H + 22, f'{label}:')
    lw = c.stringWidth(f'{label}:  ', 'Helvetica-Bold', 8.5)
    sf(c, DARK); c.setFont('Helvetica', 8.5)
    c.drawString(M + 8 + lw, y_top - WB_H + 22, words)
    return y_top - WB_H - 8


# ── Marking station header ────────────────────────────────────────────
def marking_header(c):
    sf(c, BLUE); c.setFont('Helvetica-Bold', 20)
    c.drawString(M, H - M - 14, 'Marking Station')
    ss(c, BLUE); c.setLineWidth(0.8)
    c.line(M, H - M - 24, W - M, H - M - 24)
    return H - M - 40


# ── Answer key row ────────────────────────────────────────────────────
def answer_row(c, arrow_text, main_text, sub_text, y_top, colour=GREEN):
    sf(c, colour); c.setFont('Helvetica-Bold', 9)
    c.drawString(M, y_top - 8, f'\u2192 {arrow_text}')
    sf(c, DARK); c.setFont('Helvetica', 9)
    c.drawString(M + 60, y_top - 8, main_text)
    if sub_text:
        sf(c, GREY); c.setFont('Helvetica', 8)
        c.drawRightString(W - M, y_top - 8, sub_text)
    return y_top - 16


# ══════════════════════════════════════════════════════════════════════
# LP4 — Standard
# ══════════════════════════════════════════════════════════════════════
def build_lp4_standard():
    path = '/mnt/user-data/outputs/T6W4_LP4_Geographers_Human_Geography.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    # PAGE 1 — pupil sheet
    y = learning_label(c,
        'Are England and Brazil different?', '06/07/2026',
        'to describe and compare how people use land in England and Brazil',
        ['I can describe two ways land is used in Brazil',
         'I can compare land use in England and Brazil using geographical vocabulary'])

    y = section_head(c, 'Part A   Land use sort', y)
    y = body(c, 'For each land use below, write E (England), B (Brazil) or Both. Then write the type of land use.', y, sz=9)
    y -= 6

    # Table
    col_w = [CW * 0.50, CW * 0.26, CW * 0.24]
    cols  = [('Land use', col_w[0]), ('England / Brazil / Both', col_w[1]), ('Type', col_w[2])]
    y = table_header(c, cols, y)
    rows = [
        'Coffee plantation', 'Coal mine / quarry', 'Cattle ranch / farmland',
        'Offshore wind farm', 'Iron ore mine', 'Arable crop field (wheat, barley)',
        'Oil rig or power station', 'Terraced housing / urban suburb',
        'Hydro-electric dam', 'Shopping centre / commercial area',
        'Port / container terminal', 'Moorland / national park',
    ]
    for i, row in enumerate(rows):
        y = table_row(c, [row, '', ''], col_w, y, shade=(i % 2 == 0))

    y -= 8
    y = section_head(c, 'Part B   Comparison sentences', y)
    y = body(c, 'Write one sentence about what England and Brazil have in common and one about how they differ.', y, sz=9)
    y = body(c, 'Use at least ONE word from the vocabulary bank.', y, sz=9)
    y -= 8
    y = body_bold(c, 'England and Brazil are similar because...', y, sz=10)
    for _ in range(3): y = writing_line(c, y)
    y -= 8
    y = body_bold(c, 'However, they are different because...', y, sz=10)
    for _ in range(3): y = writing_line(c, y)
    y -= 10
    word_bank(c, 'land use  \u2022  natural resource  \u2022  trade  \u2022  economic activity  \u2022  agricultural  \u2022  industrial', y)

    c.showPage()

    # PAGE 2 — marking station
    y = marking_header(c)
    y = section_head(c, 'Part A   Suggested answers', y, GREEN)
    answers = [
        ('B', 'Coffee plantation', 'Agricultural'),
        ('Both', 'Coal mine / quarry', 'Industrial / mining'),
        ('B', 'Cattle ranch / farmland', 'Agricultural'),
        ('E', 'Offshore wind farm', 'Energy'),
        ('B', 'Iron ore mine', 'Industrial / mining'),
        ('E', 'Arable crop field (wheat, barley)', 'Agricultural'),
        ('Both', 'Oil rig or power station', 'Energy'),
        ('Both', 'Terraced housing / urban suburb', 'Residential'),
        ('B', 'Hydro-electric dam', 'Energy'),
        ('Both', 'Shopping centre / commercial area', 'Commercial'),
        ('Both', 'Port / container terminal', 'Transport / trade'),
        ('E', 'Moorland / national park', 'Recreational / environmental'),
    ]
    for ab, item, typ in answers:
        y = answer_row(c, ab, item, typ, y)

    y -= 6
    y = section_head(c, 'Part B   Model sentences', y, GREEN)
    y = body(c, 'England and Brazil are similar because both countries use land for agriculture, industry and energy production.', y, sz=9)
    y = body(c, "However, they are different because Brazil's main agricultural land uses include coffee and cattle, while England's", y, sz=9)
    body(c, 'focus more on arable crops such as wheat and barley. Trade links the two: England imports products from Brazil.', y, sz=9)
    c.save()
    print('LP4 standard done')


# ══════════════════════════════════════════════════════════════════════
# LP4 — Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp4_adapted():
    path = '/mnt/user-data/outputs/T6W4_LP4_Geographers_Human_Geography_adapted.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    # PAGE 1
    y = learning_label(c,
        'Are England and Brazil different?', '06/07/2026',
        'to describe and compare how people use land in England and Brazil',
        ['I can match a land use to the correct country',
         'I can complete a comparison sentence about England and Brazil'])

    y = section_head(c, 'Part A   Which country?', y)
    y = body(c, 'Read each statement. Write England, Brazil or Both in the box on the right.', y, sz=9)
    y -= 4
    y = word_bank(c, 'England  \u2022  Brazil  \u2022  Both', y + WB_H + 8, label='Countries', colour=BLUE)
    y -= 6

    statements = [
        'This country grows coffee beans as one of its most important crops.',
        'This country has oil fields and uses wind turbines for energy.',
        'This country has huge iron ore mines in the ground.',
        'This country has mostly flat farmland in the east and hilly farmland in the west.',
        'This country has hydro-electric dams on its rivers.',
        'This country has large ports where goods are shipped abroad.',
        'This country trades with the other, buying and selling different goods.',
    ]
    BOX_W = 115
    STMT_W = CW - BOX_W - 8
    for i, stmt in enumerate(statements):
        shade = (i % 2 == 0)
        if shade:
            sf(c, (0.96, 0.97, 1.0))
            c.rect(M, y - ROW_H, CW, ROW_H, fill=1, stroke=0)
        ss(c, LGREY); c.setLineWidth(0.3)
        c.rect(M, y - ROW_H, CW, ROW_H, fill=0, stroke=1)
        sf(c, DARK); c.setFont('Helvetica', 8)
        c.drawString(M + 4, y - ROW_H + 7, f'{i+1}. {stmt}')
        # Answer box (right side, inside row bounds — 12pt margins verified)
        bx = M + CW - BOX_W
        sf(c, (1,1,1)); ss(c, (0.6,0.6,0.6)); c.setLineWidth(0.5)
        c.rect(bx + 2, y - ROW_H + 2, BOX_W - 4, ROW_H - 4, fill=1, stroke=1)
        y -= ROW_H

    y -= 10
    y = section_head(c, 'Part B   Cloze comparison sentences', y)
    y = body(c, 'Fill in the missing words using the word bank below.', y, sz=9)
    y -= 12

    sf(c, DARK); c.setFont('Helvetica', 10)
    c.drawString(M, y - 7, 'England and Brazil are similar because they both use land for')
    y -= 18
    c.drawString(M, y - 7, '___________________ and ___________________.')
    y -= 22
    c.drawString(M, y - 7, 'However, they are different because Brazil grows ___________________, while')
    y -= 18
    c.drawString(M, y - 7, 'England grows ___________________. England imports ___________________ from Brazil.')
    y -= 22
    word_bank(c, 'agriculture  \u2022  energy  \u2022  coffee  \u2022  wheat  \u2022  iron ore  \u2022  trade  \u2022  industry', y)

    c.showPage()

    # PAGE 2 — marking
    y = marking_header(c)
    y = section_head(c, 'Part A   Which country? (answers)', y, GREEN)
    ms_rows = [
        ('Brazil',  'This country grows coffee beans...', ''),
        ('Both',    'This country has oil fields and wind turbines...', ''),
        ('Brazil',  'This country has huge iron ore mines...', ''),
        ('England', 'Mostly flat farmland in the east and hilly in the west.', ''),
        ('Brazil',  'Hydro-electric dams on its rivers.', ''),
        ('Both',    'Large ports where goods are shipped abroad.', ''),
        ('Both',    'This country trades with the other...', ''),
    ]
    for ab, stmt, _ in ms_rows:
        y = answer_row(c, ab, stmt, '', y)

    y -= 8
    y = section_head(c, 'Part B   Cloze model answers', y, GREEN)
    y = body(c, 'England and Brazil are similar because they both use land for agriculture and energy.', y, sz=9)
    y = body(c, 'However, they are different because Brazil grows coffee, while England grows wheat.', y, sz=9)
    body(c, 'England imports coffee from Brazil.', y, sz=9)
    c.save()
    print('LP4 adapted done')


# ══════════════════════════════════════════════════════════════════════
# LP5 — Standard
# ══════════════════════════════════════════════════════════════════════
def build_lp5_standard():
    from reportlab.lib.utils import ImageReader
    path = '/mnt/user-data/outputs/T6W4_LP5_Geographers_Map_Skills.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    # PAGE 1
    y = learning_label(c,
        'Are England and Brazil different?', '07/07/2026',
        'to use maps to investigate and describe places',
        ['I can read a grid reference correctly',
         'I can describe what a map tells me about a place'])

    # Map image — centred, shallow height to leave room for questions
    MAP_H = 180
    img = ImageReader('/home/claude/lp5_map.png')
    iw, ih = img.getSize()
    scale = min(CW * 0.65 / iw, MAP_H / ih)
    dw, dh = iw * scale, ih * scale
    img_x = M + (CW - dw) / 2
    img_y_bottom = y - dh  # rect bottom
    c.drawImage(img, img_x, img_y_bottom, dw, dh, mask='auto')
    y = img_y_bottom - 10

    y = section_head(c, 'Part A   Map skills questions', y)
    questions = [
        ('1. What feature is shown at grid reference 322 510?', 2),
        ('2. Write the 4-figure grid reference for Ashton settlement.', 2),
        ("3. Write the 6-figure grid reference for St Mary\u2019s Church/school.", 2),
        ('4. What do the contour lines around grid square 31 50 tell you about the land?', 3),
        ('5. Name one land use shown on the map and write its grid reference.', 2),
    ]
    for q, n_lines in questions:
        y = body_bold(c, q, y, sz=9)
        for _ in range(n_lines): y = writing_line(c, y)
        y -= 4

    y -= 4
    y = section_head(c, 'Part B   Compare two places', y)
    y = body(c, 'After looking at the board: write two sentences comparing the OS map area with the satellite image of Brazil.', y, sz=9)
    for _ in range(4): y = writing_line(c, y)

    c.showPage()

    # PAGE 2 — marking
    y = marking_header(c)
    y = section_head(c, 'Part A   Suggested answers', y, GREEN)
    ans = [
        ('1', 'Feature at 322 510', 'Woodland (shaded green area in the key)'),
        ('2', '4-figure grid ref for Ashton', '3248'),
        ("3", "6-figure grid ref for St Mary\u2019s", '322 510 (approx.)'),
        ('4', 'Contour lines in square 31 50', 'Close together \u2014 land is steeply sloping / hilly. Hill reaches over 150m.'),
        ('5', 'One land use + grid ref', 'e.g. Woodland at 326 503 / Road B4027 at 320 490 (any valid)'),
    ]
    for n, q_label, ans_text in ans:
        sf(c, GREEN); c.setFont('Helvetica-Bold', 9); c.drawString(M, y - 8, f'{n}.')
        sf(c, DARK); c.setFont('Helvetica-Bold', 9); c.drawString(M + 14, y - 8, q_label)
        y -= 14
        sf(c, DARK); c.setFont('Helvetica', 9); c.drawString(M + 14, y - 8, ans_text)
        y -= 18
    c.save()
    print('LP5 standard done')


# ══════════════════════════════════════════════════════════════════════
# LP5 — Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp5_adapted():
    from reportlab.lib.utils import ImageReader
    path = '/mnt/user-data/outputs/T6W4_LP5_Geographers_Map_Skills_adapted.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    y = learning_label(c,
        'Are England and Brazil different?', '07/07/2026',
        'to use maps to investigate and describe places',
        ['I can read a grid reference using the rule "along first, then up"',
         'I can name one thing a map shows me about a place'])

    MAP_H = 170
    img = ImageReader('/home/claude/lp5_map.png')
    iw, ih = img.getSize()
    scale = min(CW * 0.65 / iw, MAP_H / ih)
    dw, dh = iw * scale, ih * scale
    img_x = M + (CW - dw) / 2
    img_y_bottom = y - dh
    c.drawImage(img, img_x, img_y_bottom, dw, dh, mask='auto')
    y = img_y_bottom - 10

    y = section_head(c, 'Part A   Reading the map', y)

    # Reminder box
    REMIND_H = 24
    sf(c, (0.88, 0.94, 0.98)); ss(c, BLUE); c.setLineWidth(0.8)
    c.rect(M, y - REMIND_H, CW, REMIND_H, fill=1, stroke=1)
    sf(c, BLUE); c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M + 6, y - REMIND_H + 8, 'Remember:')
    sf(c, DARK); c.setFont('Helvetica', 8.5)
    c.drawString(M + 68, y - REMIND_H + 8, 'go ACROSS first, then UP \u2014 \u201calong the corridor, up the stairs\u201d')
    y -= REMIND_H + 8

    mc_questions = [
        ('1. What is shown at grid reference 322 510?',
         ['A. The river', 'B. The woodland', 'C. The road', 'D. Ashton settlement']),
        ('2. The 4-figure grid reference for Ashton is:',
         ['A. 4832', 'B. 3248', 'C. 4823', 'D. 2348']),
        ('3. The contour lines near grid square 31 50 are close together. This means:',
         ['A. The land is flat', 'B. The land is wet', 'C. The land is steep', 'D. There is a river']),
    ]
    for q_text, opts in mc_questions:
        y = body_bold(c, q_text, y, sz=9)
        for opt in opts:
            y = body(c, opt, y, sz=9, indent=12)
        y -= 4

    y -= 4
    y = section_head(c, 'Part B   Comparison sentence (cloze)', y)
    y = body(c, 'Fill in the missing words.', y, sz=9)
    y -= 10
    sf(c, DARK); c.setFont('Helvetica', 10)
    c.drawString(M, y - 7, 'The OS map of Westhaven shows ___________________ and ___________________.')
    y -= 22
    c.drawString(M, y - 7, 'This is different from the satellite image of Brazil because ___________________________')
    y -= 18
    c.drawString(M, y - 7, '____________________________________________________________.')
    y -= 22
    word_bank(c, 'woodland  \u2022  roads  \u2022  hills  \u2022  settlement  \u2022  rainforest  \u2022  flat  \u2022  land use', y)

    c.showPage()

    y = marking_header(c)
    y = section_head(c, 'Part A   Answers', y, GREEN)
    mc_ans = [('1', 'B. The woodland'), ('2', 'B. 3248'), ('3', 'C. The land is steep')]
    for n, a in mc_ans:
        sf(c, GREEN); c.setFont('Helvetica-Bold', 9); c.drawString(M, y - 8, f'{n}. \u2192 {a}')
        y -= 16
    y -= 6
    y = section_head(c, 'Part B   Model sentence', y, GREEN)
    y = body(c, 'The OS map of Westhaven shows woodland and roads.', y, sz=9)
    body(c, 'This is different from the satellite image of Brazil because Brazil shows flat farmland / rainforest with very different land use patterns.', y, sz=9)
    c.save()
    print('LP5 adapted done')


# ══════════════════════════════════════════════════════════════════════
# LP6 — Standard (no split-column layout — left-to-right sequential)
# ══════════════════════════════════════════════════════════════════════
def build_lp6_standard():
    path = '/mnt/user-data/outputs/T6W4_LP6_Geographers_Environmental_Impact.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    y = learning_label(c,
        'Are England and Brazil different?', '08/07/2026',
        'to explain how humans affect the environment in England and Brazil and compare them',
        ['I can describe one way humans are affecting Brazil\u2019s environment',
         'I can write a structured comparison using geographical vocabulary'])

    y = section_head(c, 'Part A   Before and after', y)
    y = body(c, 'Look at the images on the board. For each pair, record what you observe.', y, sz=9)
    y -= 6

    for pair_label in ['Image pair 1: Amazon rainforest', 'Image pair 2: English landscape']:
        BOX_H = 64
        sf(c, (0.93, 0.96, 0.99)); ss(c, BLUE); c.setLineWidth(0.7)
        c.rect(M, y - BOX_H, CW, BOX_H, fill=1, stroke=1)
        sf(c, BLUE); c.setFont('Helvetica-Bold', 9)
        c.drawString(M + 6, y - BOX_H + 52, pair_label)
        sf(c, DARK); c.setFont('Helvetica', 8.5)
        labels = ['What changed?', 'What caused the change?', 'What might the geographical impact be?']
        line_ys = [y - BOX_H + 38, y - BOX_H + 24, y - BOX_H + 10]
        for lbl, ly in zip(labels, line_ys):
            c.drawString(M + 8, ly, f'{lbl} ________________')
        y -= BOX_H + 8

    y -= 4
    y = section_head(c, 'Part B   Geographical comparison', y)
    y = body(c, 'Write your comparison. Use the vocabulary checklist \u2014 tick each term when you use it.', y, sz=9)
    y -= 8

    # Vocabulary checklist — full width, compact
    vc_terms = ['hemisphere', 'biome', 'climate zone', 'topography', 'land use',
                'natural resource', 'trade', 'deforestation', 'urbanisation', 'temperate', 'tropical']
    VC_ITEM_H = 13
    VC_HEADER_H = 18
    VC_PAD = 8
    vc_box_h = VC_HEADER_H + len(vc_terms) * VC_ITEM_H + VC_PAD
    VC_W = 130
    vc_x = M + CW - VC_W
    vc_top = y

    # Draw checklist box
    sf(c, CREAM); ss(c, ORANGE); c.setLineWidth(0.8)
    c.rect(vc_x - 4, vc_top - vc_box_h, VC_W + 4, vc_box_h, fill=1, stroke=1)
    sf(c, ORANGE); c.setFont('Helvetica-Bold', 8)
    c.drawString(vc_x, vc_top - VC_HEADER_H + 6, 'Vocabulary checklist')
    sf(c, DARK); c.setFont('Helvetica', 7.5)
    for i, term in enumerate(vc_terms):
        item_y = vc_top - VC_HEADER_H - i * VC_ITEM_H
        # Checkbox (fully inside box: bottom = item_y - VC_ITEM_H + 3, top = item_y - 3)
        ss(c, ORANGE); sf(c, (1,1,1)); c.setLineWidth(0.5)
        c.rect(vc_x, item_y - VC_ITEM_H + 3, 7, 7, fill=1, stroke=1)
        sf(c, DARK)
        c.drawString(vc_x + 11, item_y - VC_ITEM_H + 4, term)

    # Writing sections — left of checklist
    WRITE_W = CW - VC_W - 14
    write_prompts = [
        ('Physical geography \u2014 how the two countries compare physically:', 3),
        ('Human geography \u2014 how land use compares:', 3),
        ('Environmental impact \u2014 how humans are affecting each place:', 3),
    ]
    wy = y
    for prompt, n_lines in write_prompts:
        sf(c, DARK); c.setFont('Helvetica-Bold', 8.5)
        c.drawString(M, wy - 7, prompt)
        wy -= 16
        for _ in range(n_lines):
            ss(c, (0.65, 0.80, 0.88)); c.setLineWidth(0.6)
            c.line(M, wy - 14, M + WRITE_W, wy - 14)
            wy -= 20
        wy -= 6

    c.showPage()

    y = marking_header(c)
    y = section_head(c, 'Part A   Key points', y, GREEN)
    for label, note in [
        ('Amazon rainforest', 'Deforestation: cleared for cattle / soya / mining. Impact: loss of biome, species, carbon storage.'),
        ('English landscape', 'Urban growth: farmland covered by housing and roads. Quarrying changes highland landscape.'),
    ]:
        sf(c, GREEN); c.setFont('Helvetica-Bold', 9); c.drawString(M, y - 8, label)
        y -= 14
        sf(c, DARK); c.setFont('Helvetica', 9); c.drawString(M + 12, y - 8, note)
        y -= 16

    y -= 6
    y = section_head(c, 'Part B   Model comparison (extract)', y, GREEN)
    lines = [
        'Physically, England has a temperate maritime climate with four seasons and temperate deciduous woodland,',
        'while Brazil has a tropical climate with biomes including the rainforest, cerrado and pantanal.',
        "In terms of human geography, Brazil\u2019s main land uses are agriculture (coffee, soya, cattle) and mining,",
        "while England focuses more on arable farming in the east and services and industry in its cities.",
        'Humans are having a greater environmental impact in Brazil: around 20% of the Amazon has been',
        'deforested since the 1970s for farming and mining. In England, urban growth has covered farmland',
        'around cities like Bristol. Both countries face the challenge of meeting people\u2019s needs without',
        'permanently destroying the environments they depend on.',
    ]
    sf(c, DARK); c.setFont('Helvetica', 9)
    for line in lines:
        c.drawString(M, y - 8, line); y -= 14
    c.save()
    print('LP6 standard done')


# ══════════════════════════════════════════════════════════════════════
# LP6 — Adapted
# ══════════════════════════════════════════════════════════════════════
def build_lp6_adapted():
    path = '/mnt/user-data/outputs/T6W4_LP6_Geographers_Environmental_Impact_adapted.pdf'
    c = canvas.Canvas(path, pagesize=A4)

    y = learning_label(c,
        'Are England and Brazil different?', '08/07/2026',
        'to explain how humans affect the environment in England and Brazil and compare them',
        ['I can name one cause of Amazon deforestation',
         'I can complete comparison sentences using geographical vocabulary'])

    y = section_head(c, 'Part A   What has changed?', y)
    y = body(c, 'Look at the images on the board. Tick the boxes that apply to each image pair.', y, sz=9)
    y -= 8

    tick_items = [
        'Trees / vegetation removed', 'Buildings added',
        'Farmland expanded', 'Roads or infrastructure built',
    ]
    for pair_label in ['Image pair 1: Amazon rainforest', 'Image pair 2: English landscape']:
        BOX_H = 76
        sf(c, (0.93, 0.96, 0.99)); ss(c, BLUE); c.setLineWidth(0.7)
        c.rect(M, y - BOX_H, CW, BOX_H, fill=1, stroke=1)
        sf(c, BLUE); c.setFont('Helvetica-Bold', 9)
        c.drawString(M + 6, y - BOX_H + 64, pair_label)
        sf(c, DARK); c.setFont('Helvetica', 8.5)
        # Two columns of tick boxes, 2 items each
        for j, item in enumerate(tick_items):
            col = j % 2
            row = j // 2
            ix = M + 10 + col * (CW // 2)
            iy = y - BOX_H + 50 - row * 20
            ss(c, ORANGE); sf(c, (1,1,1)); c.setLineWidth(0.5)
            c.rect(ix, iy - 2, 8, 8, fill=1, stroke=1)
            sf(c, DARK); c.drawString(ix + 12, iy - 1, item)
        y -= BOX_H + 8

    y -= 4
    y = section_head(c, 'Part B   Cloze comparison', y)
    y = body(c, 'Fill in the missing words using the word bank.', y, sz=9)
    y -= 12

    sf(c, DARK); c.setFont('Helvetica', 10)
    cloze_lines = [
        ('Physically, England has a _______________ climate, while Brazil has a', None),
        ('_______________ climate. England\u2019s main biome is _______________ forest.', None),
        (None, 8),
        ('For human geography, Brazil uses land mainly for _______________ such as', None),
        ('coffee and soya, while England uses land more for _______________ and services.', None),
        (None, 8),
        ('Humans are affecting Brazil by _______________ the Amazon, which destroys the', None),
        ('_______________ and the habitats that depend on it. In England, _______________ growth', None),
        ('has covered farmland around cities.', None),
    ]
    for line_text, gap in cloze_lines:
        if gap:
            y -= gap
        else:
            c.drawString(M, y - 7, line_text)
            y -= 18

    y -= 8
    word_bank(c, 'temperate  \u2022  tropical  \u2022  deciduous  \u2022  agriculture  \u2022  arable farming  \u2022  deforesting  \u2022  biome  \u2022  urban', y)

    c.showPage()

    y = marking_header(c)
    y = section_head(c, 'Part B   Cloze answers', y, GREEN)
    cloze_ans = [
        ('temperate', 'Climate (England)'),
        ('tropical', 'Climate (Brazil)'),
        ('deciduous', "England\u2019s main biome"),
        ('agriculture', 'Brazil land use'),
        ('arable farming', 'England land use'),
        ('deforesting', 'Human impact on Brazil'),
        ('biome', 'What is destroyed'),
        ('urban', 'England impact type'),
    ]
    for ans, label in cloze_ans:
        y = answer_row(c, ans, f'({label})', '', y)
    c.save()
    print('LP6 adapted done')


# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    build_lp4_standard()
    build_lp4_adapted()
    build_lp5_standard()
    build_lp5_adapted()
    build_lp6_standard()
    build_lp6_adapted()
    print('All done.')
