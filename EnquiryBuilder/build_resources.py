#!/usr/bin/env python3
"""
build_resources.py — WFA Enquiry Supporting Resources Builder
Generates PDFs for sort cards, word cards, statement sorts, and writing toolkits.
Usage: python3 build_resources.py config.json

===== WRITING TOOLKIT config schema =====

{
  "year_group": "Y4",
  "resources": [
    {
      "type": "writing_mat",
      "output": "T6W2_Writing_Toolkit.pdf",
      "title": "Writing Toolkit — Varjak's First Night Outside",
      "subtitle": "Use these examples to help build your narrative. Adapt them — make them your own.",
      "year_info": "Year 4 | T6W2 | Being a Writer",
      "footer": "T6W2 | Being a Writer | Varjak Paw by S. F. Said",
      "rows": [
        {
          "sections": [
            {
              "heading": "Fronted Adverbials",
              "type": "multi_column_list",
              "columns": [
                {"heading": "Place",  "items": ["At the far end of the alley,", ...]},
                {"heading": "Time",   "items": ["As the night grew darker,", ...]},
                {"heading": "Manner", "items": ["Trembling with every step,", ...]}
              ]
            }
          ]
        },
        {
          "sections": [
            {
              "heading": "Similes",
              "type": "bullet_list",
              "items": ["The car's headlights blazed like...", ...]
            },
            {
              "heading": "Alliteration",
              "type": "bullet_list",
              "items": ["damp, dark doorways", ...]
            }
          ]
        },
        {
          "sections": [
            {
              "heading": "Direct Speech",
              "type": "two_panel",
              "left": {
                "heading": "Different ways to place the reporting clause",
                "entries": [
                  {"label": "Reporting clause AFTER the speech:", "example": "\\"You lost?\\" she said."},
                  ...
                ]
              },
              "right": {
                "heading": "Speech verbs",
                "categories": [
                  {"label": "Quiet / calm", "words": ["whispered", "murmured", ...]},
                  ...
                ]
              }
            }
          ]
        },
        {
          "sections": [
            {
              "heading": "Powerful Verbs",
              "type": "word_grid",
              "columns": [
                {"heading": "Moving through the city", "words": ["crept", "prowled", ...]},
                {"heading": "Sounds and voices",       "words": ["growled", "screeched", ...]},
                {"heading": "Showing fear or shock",   "words": ["swallowed", "shuddered", ...]},
                {"heading": "Fighting and defending",  "words": ["swiped", "lunged", ...]}
              ]
            }
          ]
        }
      ]
    }
  ]
}

Section types:
  bullet_list        — bulleted list of items
  multi_column_list  — N sub-columns each with heading + items (e.g. Fronted Adverbials)
  word_grid          — N sub-columns each with heading + word list (dense, no bullets)
  two_panel          — left structured text, right categorised word lists

For simple enquiry resources (sort_cards, word_cards, statement_sort) see bottom of file.
"""

import sys, json, os, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black

# ── Year group colours ────────────────────────────────────────────────────────

YEAR_COLOURS = {
    'Y3': '#c0157b',
    'Y4': '#1798d3',
    'Y5': '#e57d24',
    'Y6': '#2bae62',
}

# Writing toolkit section colours — distinct from WFA year group colours
# so sections don't carry accidental year-group meaning for children.
# The ONLY year-colour element is the page header bar.
TOOLKIT_SECTION_COLOURS = [
    '#4a6fa5',   # slate blue   (≠ Y4 blue #1798d3)
    '#3a7a50',   # forest green (≠ Y6 green #2bae62)
    '#7a4a90',   # warm purple  (≠ Y3 magenta #c0157b)
    '#b05028',   # burnt sienna (≠ Y5 orange #e57d24)
]

def get_colour_cycle(year_group):
    """Section colours for writing toolkit — always the toolkit palette, never year colours."""
    return TOOLKIT_SECTION_COLOURS

# ── Colour helpers ────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lighten(hc, f=0.88):
    r,g,b = hex_to_rgb(hc)
    return '#{:02x}{:02x}{:02x}'.format(
        int(r+(255-r)*f), int(g+(255-g)*f), int(b+(255-b)*f))

def midtone(hc, f=0.45):
    r,g,b = hex_to_rgb(hc)
    return '#{:02x}{:02x}{:02x}'.format(
        int(r+(255-r)*f), int(g+(255-g)*f), int(b+(255-b)*f))

# ── Text wrap ─────────────────────────────────────────────────────────────────

def wrap(c, text, font, sz, max_w):
    words = str(text).split()
    lines, cur = [], ''
    for w in words:
        test = (cur+' '+w).strip()
        if c.stringWidth(test, font, sz) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines or ['']

def count_lines(c, text, font, sz, max_w):
    return len(wrap(c, text, font, sz, max_w))

# ── Cut lines (for cut-and-sort resources) ────────────────────────────────────

def cut_h(c, x, y, w):
    c.setStrokeColor(HexColor('#aaaaaa'))
    c.setLineWidth(0.4); c.setDash([3,5],0)
    c.line(x, y, x+w, y); c.setDash([])

def cut_v(c, x, y_bot, h):
    c.setStrokeColor(HexColor('#aaaaaa'))
    c.setLineWidth(0.4); c.setDash([3,5],0)
    c.line(x, y_bot, x, y_bot+h); c.setDash([])

# ─────────────────────────────────────────────────────────────────────────────
# WRITING TOOLKIT
# ─────────────────────────────────────────────────────────────────────────────

# Layout constants (portrait A4: 595×842)
W_A4, H_A4 = A4
M = 22          # page margin
GAP = 6         # gap between rows / between paired sections
SEC_HDR = 20    # section heading bar height
COL_HDR = 16    # sub-column heading height
PAD_T = 7       # padding below section header before first item
PAD_B = 7       # padding at bottom of section
ITEM_FS = 9     # font size for items
ITEM_LH = 12.5  # line height for items
WORD_LH = 12    # line height for word-grid items
BULL = '•  '    # bullet character + space


def _measure_section(c, section, w):
    """Return the height this section needs at content width w."""
    stype = section.get('type', 'bullet_list')
    tw = w - 16   # text width inside a section (left+right padding)

    if stype == 'bullet_list':
        items = section.get('items', [])
        lines = sum(count_lines(c, BULL+item, 'Helvetica', ITEM_FS, tw)
                    for item in items)
        return SEC_HDR + PAD_T + lines * ITEM_LH + PAD_B

    elif stype == 'multi_column_list':
        cols  = section.get('columns', [])
        n     = max(len(cols), 1)
        col_w = (w - 8*(n-1)) / n
        ctw   = col_w - 10
        max_l = max(
            (sum(count_lines(c, item, 'Helvetica', ITEM_FS, ctw)
                 for item in col.get('items', []))
             for col in cols), default=0)
        return SEC_HDR + COL_HDR + PAD_T + max_l * ITEM_LH + PAD_B

    elif stype == 'word_grid':
        cols   = section.get('columns', [])
        max_wc = max((len(col.get('words', [])) for col in cols), default=0)
        return SEC_HDR + COL_HDR + PAD_T + max_wc * WORD_LH + PAD_B

    elif stype == 'two_panel':
        left  = section.get('left',  {})
        right = section.get('right', {})
        pw    = (w - GAP) / 2 - 8
        # Left: label+example entries
        entries  = left.get('entries', [])
        l_lines  = sum(1 + count_lines(c, e.get('example',''), 'Helvetica-Oblique', ITEM_FS, pw)
                       for e in entries)
        # Right: categorised word lists
        cats     = right.get('categories', [])
        r_lines  = sum(1 + count_lines(c, '  '.join(cat.get('words',[])),
                                       'Helvetica', ITEM_FS, pw)
                       for cat in cats)
        return SEC_HDR + COL_HDR + PAD_T + max(l_lines, r_lines) * ITEM_LH + PAD_B

    return 60  # fallback


def _draw_section(c, section, x, y_top, w, h, colour):
    """
    Draw a single section box.
    x, y_top are the top-left corner. h is the total height.
    ReportLab: y increases upward, so bottom = y_top - h.
    """
    stype   = section.get('type', 'bullet_list')
    heading = section.get('heading', '')
    y_bot   = y_top - h
    col_h   = HexColor(colour)
    bg      = HexColor(lighten(colour, 0.92))
    sub_hd  = HexColor(midtone(colour, 0.28))
    DRK     = HexColor('#111111')
    GRY     = HexColor('#444444')

    # Background
    c.setFillColor(bg)
    c.rect(x, y_bot, w, h, fill=1, stroke=0)

    # Section heading bar
    c.setFillColor(col_h)
    c.rect(x, y_top - SEC_HDR, w, SEC_HDR, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(x+8, y_top - SEC_HDR + (SEC_HDR - 10*0.72)/2, heading)

    content_y = y_top - SEC_HDR - PAD_T  # top of content area
    tw = w - 16   # default text width

    # ── bullet_list ───────────────────────────────────────────────────────────
    if stype == 'bullet_list':
        items = section.get('items', [])
        iy = content_y - ITEM_FS*0.72
        c.setFillColor(DRK)
        for j, item in enumerate(items):
            # Alternate very-light row tint
            lns = wrap(c, BULL+item, 'Helvetica', ITEM_FS, tw)
            row_h = len(lns)*ITEM_LH
            if j % 2 == 0:
                c.setFillColor(HexColor(lighten(colour, 0.97)))
                c.rect(x, iy - ITEM_FS*0.28 - (len(lns)-1)*ITEM_LH,
                       w, row_h+1, fill=1, stroke=0)
            c.setFillColor(DRK)
            row_y = iy
            for ln in lns:
                c.setFont('Helvetica', ITEM_FS)
                c.drawString(x+8, row_y, ln)
                row_y -= ITEM_LH
            iy = row_y
            if iy < y_bot + PAD_B: break

    # ── multi_column_list ─────────────────────────────────────────────────────
    elif stype == 'multi_column_list':
        cols  = section.get('columns', [])
        n     = max(len(cols), 1)
        col_w = (w - 8*(n-1)) / n

        for ci, col in enumerate(cols):
            col_hd  = col.get('heading', '')
            col_items = col.get('items', [])
            cx = x + ci*(col_w+8)
            # Sub-column header
            c.setFillColor(sub_hd)
            c.rect(cx, content_y - COL_HDR, col_w, COL_HDR, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(cx+6, content_y - COL_HDR + (COL_HDR - 8.5*0.72)/2, col_hd)
            # Items
            ctw = col_w - 12
            iy  = content_y - COL_HDR - 3 - ITEM_FS*0.72
            c.setFillColor(DRK)
            for item in col_items:
                lns = wrap(c, item, 'Helvetica', ITEM_FS, ctw)
                for ln in lns:
                    c.setFont('Helvetica', ITEM_FS)
                    c.drawString(cx+6, iy, ln)
                    iy -= ITEM_LH
                if iy < y_bot + PAD_B: break

    # ── word_grid ─────────────────────────────────────────────────────────────
    elif stype == 'word_grid':
        cols  = section.get('columns', [])
        n     = max(len(cols), 1)
        col_w = (w - 6*(n-1)) / n

        for ci, col in enumerate(cols):
            col_hd = col.get('heading', '')
            words  = col.get('words', [])
            cx = x + ci*(col_w+6)
            # Sub-column header
            c.setFillColor(sub_hd)
            c.rect(cx, content_y - COL_HDR, col_w, COL_HDR, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(cx+5, content_y - COL_HDR + (COL_HDR - 8*0.72)/2, col_hd)
            # Words — 2 per row
            iy = content_y - COL_HDR - 3 - ITEM_FS*0.72
            WPR = 2  # words per sub-row
            col_w_half = (col_w - 10) / WPR
            c.setFillColor(DRK)
            for wi in range(0, len(words), WPR):
                row_words = words[wi:wi+WPR]
                if iy < y_bot + PAD_B: break
                # Alternate row tint
                if (wi//WPR) % 2 == 0:
                    c.setFillColor(HexColor(lighten(colour, 0.97)))
                    c.rect(cx, iy - ITEM_FS*0.28, col_w, WORD_LH, fill=1, stroke=0)
                c.setFillColor(DRK)
                for wj, word in enumerate(row_words):
                    c.setFont('Helvetica', ITEM_FS)
                    c.drawString(cx + 5 + wj*col_w_half, iy, word)
                iy -= WORD_LH

    # ── two_panel ─────────────────────────────────────────────────────────────
    elif stype == 'two_panel':
        left  = section.get('left',  {})
        right = section.get('right', {})
        pw    = (w - GAP) / 2

        for pi, panel in enumerate([left, right]):
            px    = x + pi*(pw+GAP)
            p_hd  = panel.get('heading', '')
            # Sub-panel header
            c.setFillColor(sub_hd)
            c.rect(px, content_y - COL_HDR, pw, COL_HDR, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont('Helvetica-Bold', 8)
            hdr_lns = wrap(c, p_hd, 'Helvetica-Bold', 8, pw-10)
            c.drawString(px+6, content_y - COL_HDR + (COL_HDR - 8*0.72)/2, hdr_lns[0])

            ptw = pw - 12
            iy  = content_y - COL_HDR - 4 - ITEM_FS*0.72
            c.setFillColor(DRK)

            if pi == 0:
                # Left: label (bold) + example (italic, indented)
                entries = panel.get('entries', [])
                for entry in entries:
                    lbl = entry.get('label', '')
                    ex  = entry.get('example', '')
                    if iy < y_bot + PAD_B: break
                    c.setFillColor(col_h)
                    c.setFont('Helvetica-Bold', 8)
                    c.drawString(px+6, iy, lbl)
                    iy -= ITEM_LH
                    if ex:
                        ex_lns = wrap(c, ex, 'Helvetica-Oblique', ITEM_FS, ptw-8)
                        c.setFillColor(DRK)
                        for ln in ex_lns:
                            c.setFont('Helvetica-Oblique', ITEM_FS)
                            c.drawString(px+14, iy, ln)
                            iy -= ITEM_LH
                    iy -= 2  # small gap between entries
            else:
                # Right: category label (bold small) + words on same line(s)
                cats = panel.get('categories', [])
                for cat in cats:
                    lbl   = cat.get('label', '')
                    words = cat.get('words', [])
                    if iy < y_bot + PAD_B: break
                    c.setFillColor(col_h)
                    c.setFont('Helvetica-Bold', 8)
                    c.drawString(px+6, iy, lbl)
                    iy -= ITEM_LH
                    word_line = '  '.join(words)
                    wlns = wrap(c, word_line, 'Helvetica', ITEM_FS, ptw)
                    c.setFillColor(DRK)
                    for ln in wlns:
                        c.setFont('Helvetica', ITEM_FS)
                        c.drawString(px+6, iy, ln)
                        iy -= ITEM_LH
                    iy -= 3

    # Border
    c.setStrokeColor(HexColor(colour))
    c.setLineWidth(0.5)
    c.rect(x, y_bot, w, h, fill=0, stroke=1)


def build_writing_mat(c, resource, colour, colour_cycle=None):
    """
    A4 portrait. Row-based layout.
    Each row has 1 or 2 sections; heights are content-driven.
    Each section cycles through the four WFA colours in order.
    """
    if colour_cycle is None:
        colour_cycle = [colour]
    cw = W_A4 - 2*M   # content width = 551pt

    title     = resource.get('title',    'Writing Toolkit')
    subtitle  = resource.get('subtitle', '')
    year_info = resource.get('year_info', '')
    footer    = resource.get('footer',   '')
    rows      = resource.get('rows',     [])

    # ── Header ────────────────────────────────────────────────────────────────
    HDR_BG_H = 28
    hdr_bot  = H_A4 - M - HDR_BG_H
    c.setFillColor(HexColor(colour))
    c.rect(M, hdr_bot, cw, HDR_BG_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(M+10, hdr_bot + (HDR_BG_H - 12*0.72)/2, title)
    if year_info:
        c.setFont('Helvetica', 9)
        yi_w = c.stringWidth(year_info, 'Helvetica', 9)
        c.drawString(M + cw - yi_w - 8, hdr_bot + (HDR_BG_H - 9*0.72)/2, year_info)

    # Subtitle (italic, below header)
    SUB_H = 16
    sub_bot = hdr_bot - SUB_H
    if subtitle:
        c.setFillColor(HexColor('#333333'))
        c.setFont('Helvetica-Oblique', 8.5)
        c.drawString(M, sub_bot + (SUB_H - 8.5*0.72)/2, subtitle)

    # ── Footer ────────────────────────────────────────────────────────────────
    FTR_H = 14
    ftr_top = M + FTR_H
    if footer:
        c.setFillColor(HexColor('#666666'))
        c.setFont('Helvetica', 7.5)
        c.drawString(M, M + (FTR_H - 7.5*0.72)/2, footer)
        fw = c.stringWidth('Adapt these examples — change the details to fit your own narrative.',
                           'Helvetica-Oblique', 7.5)
        c.setFont('Helvetica-Oblique', 7.5)
        c.drawRightString(M+cw, M + (FTR_H - 7.5*0.72)/2,
                          'Adapt these examples — change the details to fit your own narrative.')

    # ── Rows ──────────────────────────────────────────────────────────────────
    available_top = sub_bot - GAP
    available_bot = ftr_top + GAP
    cursor = available_top   # current y position (moving down)

    sec_idx = 0  # global section counter for colour cycling

    for row in rows:
        sections = row.get('sections', [])
        if not sections:
            continue
        n = len(sections)

        if n == 1:
            sec = sections[0]
            sec_w = cw
            sec_col = colour_cycle[sec_idx % len(colour_cycle)]
            sec_idx += 1
            row_h = _measure_section(c, sec, sec_w)
            row_h = min(row_h, cursor - available_bot)
            _draw_section(c, sec, M, cursor, sec_w, row_h, sec_col)
        else:
            # 2 sections side by side — each gets its own colour
            sec_w = (cw - GAP) / 2
            h0 = _measure_section(c, sections[0], sec_w)
            h1 = _measure_section(c, sections[1], sec_w)
            row_h = min(max(h0, h1), cursor - available_bot)
            col0 = colour_cycle[sec_idx % len(colour_cycle)]; sec_idx += 1
            col1 = colour_cycle[sec_idx % len(colour_cycle)]; sec_idx += 1
            _draw_section(c, sections[0], M,            cursor, sec_w, row_h, col0)
            _draw_section(c, sections[1], M+sec_w+GAP, cursor, sec_w, row_h, col1)

        cursor -= row_h + GAP
        if cursor <= available_bot:
            break


# ─────────────────────────────────────────────────────────────────────────────
# CUT-AND-SORT RESOURCES  (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

MARGIN = 24
HDR_H  = 34

def draw_header(c, title, colour, pw, ph):
    hdr_bot = ph - MARGIN - HDR_H
    c.setFillColor(HexColor(colour))
    c.rect(MARGIN, hdr_bot, pw-2*MARGIN, HDR_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(MARGIN+10, hdr_bot+(HDR_H-11*0.72)/2, title)
    return hdr_bot

def build_sort_cards(c, resource, colour):
    W, H = A4
    COLS, ROWS, GAP = 2, 3, 8
    items = resource.get('items', [])
    title = resource.get('title', 'Sort Cards')
    bg = HexColor(lighten(colour, 0.90))
    strip = HexColor(midtone(colour, 0.40))
    col_h = HexColor(colour)
    area_top = H - MARGIN - HDR_H - GAP
    area_bot, area_w = MARGIN, W - 2*MARGIN
    card_w = (area_w - GAP*(COLS-1)) / COLS
    card_h = (area_top - area_bot - GAP*(ROWS-1)) / ROWS
    STRIP_H = 18
    per_page = COLS*ROWS
    for pg in range(max(1, math.ceil(len(items)/per_page))):
        if pg: c.showPage()
        draw_header(c, title, colour, W, H)
        for i, item in enumerate(items[pg*per_page:(pg+1)*per_page]):
            text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
            ci, ri = i%COLS, i//COLS
            cx  = MARGIN + ci*(card_w+GAP)
            top = area_top - ri*(card_h+GAP)
            bot = top - card_h
            c.setFillColor(bg); c.rect(cx, bot, card_w, card_h, fill=1, stroke=0)
            c.setFillColor(strip); c.rect(cx, top-STRIP_H, card_w, STRIP_H, fill=1, stroke=0)
            c.setStrokeColor(col_h); c.setLineWidth(0.8)
            c.rect(cx, bot, card_w, card_h, fill=0, stroke=1)
            inner_top, inner_h = top-STRIP_H-6, top-STRIP_H-6-bot-8
            lns = wrap(c, text, 'Helvetica-Bold', 11, card_w-20)
            total_h = len(lns)*15
            ty = inner_top - (inner_h-total_h)/2 - 11*0.72
            c.setFillColor(HexColor('#111111'))
            for ln in lns:
                c.setFont('Helvetica-Bold', 11)
                c.drawCentredString(cx+card_w/2, ty, ln); ty -= 15
        for row in range(1, ROWS):
            cut_h(c, MARGIN, area_top-row*(card_h+GAP)+GAP/2, area_w)
        for col in range(1, COLS):
            cut_v(c, MARGIN+col*(card_w+GAP)-GAP/2, area_bot, area_top-area_bot)

def build_word_cards(c, resource, colour):
    W, H = A4
    COLS, ROWS, GAP = 2, 4, 6
    words = resource.get('words', [])
    title = resource.get('title', 'Vocabulary Cards')
    col_h, strip = HexColor(colour), HexColor(midtone(colour, 0.35))
    area_top = H - MARGIN - HDR_H - GAP
    area_bot, area_w = MARGIN, W - 2*MARGIN
    card_w = (area_w - GAP*(COLS-1)) / COLS
    card_h = (area_top - area_bot - GAP*(ROWS-1)) / ROWS
    BAND_H = card_h * 0.40
    per_page = COLS*ROWS
    for pg in range(max(1, math.ceil(len(words)/per_page))):
        if pg: c.showPage()
        draw_header(c, title, colour, W, H)
        for i, entry in enumerate(words[pg*per_page:(pg+1)*per_page]):
            word = entry.get('word','') if isinstance(entry,dict) else str(entry[0])
            defn = entry.get('definition','') if isinstance(entry,dict) else str(entry[1])
            ci, ri = i%COLS, i//COLS
            cx  = MARGIN + ci*(card_w+GAP)
            top = area_top - ri*(card_h+GAP)
            bot = top - card_h
            c.setFillColor(white); c.rect(cx, bot, card_w, card_h, fill=1, stroke=0)
            c.setFillColor(strip); c.rect(cx, top-BAND_H, card_w, BAND_H, fill=1, stroke=0)
            wf = min(16, max(10, int(card_w*0.065)))
            c.setFillColor(white); c.setFont('Helvetica-Bold', wf)
            c.drawCentredString(cx+card_w/2, top-BAND_H/2-wf*0.72/2, word)
            dt, db = top-BAND_H-7, bot+7
            dlns = wrap(c, defn, 'Helvetica', 8.5, card_w-14)
            dy = dt - (dt-db-len(dlns)*11.5)/2 - 8.5*0.72
            c.setFillColor(HexColor('#222222'))
            for ln in dlns:
                c.setFont('Helvetica', 8.5); c.drawCentredString(cx+card_w/2, dy, ln); dy -= 11.5
            c.setStrokeColor(col_h); c.setLineWidth(0.8)
            c.rect(cx, bot, card_w, card_h, fill=0, stroke=1)
        for row in range(1, ROWS):
            cut_h(c, MARGIN, area_top-row*(card_h+GAP)+GAP/2, area_w)
        for col in range(1, COLS):
            cut_v(c, MARGIN+col*(card_w+GAP)-GAP/2, area_bot, area_top-area_bot)

def build_statement_sort(c, resource, colour):
    W, H = A4
    CARD_H, GAP, TF_W, TF_H, TF_GAP = 74, 8, 58, 38, 6
    statements = resource.get('statements', [])
    title      = resource.get('title', 'True or False?')
    col_h, bg  = HexColor(colour), HexColor(lighten(colour, 0.91))
    area_top, area_w = H - MARGIN - HDR_H - GAP, W - 2*MARGIN
    per_page = max(1, int((area_top-MARGIN)/(CARD_H+GAP)))
    for pg in range(max(1, math.ceil(len(statements)/per_page))):
        if pg: c.showPage()
        draw_header(c, title, colour, W, H)
        cy = area_top
        for i, stmt in enumerate(statements[pg*per_page:(pg+1)*per_page]):
            text = stmt.get('text', str(stmt)) if isinstance(stmt, dict) else str(stmt)
            bot  = cy - CARD_H
            c.setFillColor(bg); c.rect(MARGIN, bot, area_w, CARD_H, fill=1, stroke=0)
            tf_x = MARGIN + area_w - 2*(TF_W+TF_GAP)
            tf_y_b = bot + (CARD_H-TF_H)/2
            for j, lbl in enumerate(['True','False']):
                bx = tf_x + j*(TF_W+TF_GAP)
                c.setFillColor(white); c.rect(bx, tf_y_b, TF_W, TF_H, fill=1, stroke=0)
                c.setStrokeColor(col_h); c.setLineWidth(1.0)
                c.rect(bx, tf_y_b, TF_W, TF_H, fill=0, stroke=1)
                c.setFillColor(col_h); c.setFont('Helvetica-Bold', 9)
                c.drawCentredString(bx+TF_W/2, tf_y_b+(TF_H-9*0.72)/2, lbl)
            text_w = tf_x - MARGIN - 22
            lns = wrap(c, text, 'Helvetica', 10, text_w)
            ty = cy - (CARD_H-len(lns)*14)/2 - 10*0.72
            c.setFillColor(HexColor('#111111'))
            for ln in lns:
                c.setFont('Helvetica', 10); c.drawString(MARGIN+10, ty, ln); ty -= 14
            c.setStrokeColor(col_h); c.setLineWidth(0.8)
            c.rect(MARGIN, bot, area_w, CARD_H, fill=0, stroke=1)
            if i < len(statements[pg*per_page:(pg+1)*per_page])-1:
                cut_h(c, MARGIN, bot-GAP/2, area_w)
            cy = bot - GAP

# ─────────────────────────────────────────────────────────────────────────────
# DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

BUILDERS = {
    'sort_cards':     build_sort_cards,
    'word_cards':     build_word_cards,
    'statement_sort': build_statement_sort,
    'writing_mat':    build_writing_mat,
}

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 build_resources.py config.json')
        sys.exit(1)
    with open(sys.argv[1]) as f:
        cfg = json.load(f)

    year_group = cfg.get('year_group', 'Y5')
    colour     = cfg.get('colour', YEAR_COLOURS.get(year_group, '#1798d3'))
    resources  = cfg.get('resources', [])
    out_dir    = cfg.get('output_dir',
                         os.path.dirname(os.path.abspath(sys.argv[1])))
    os.makedirs(out_dir, exist_ok=True)

    colour_cycle = get_colour_cycle(year_group)

    generated = []
    for resource in resources:
        rtype  = resource.get('type')
        rtitle = resource.get('title', rtype or 'resource')
        safe   = rtitle.lower().replace(' ','_').replace('/','_')[:40]
        fname  = resource.get('output', f'resource_{safe}.pdf')
        out    = os.path.join(out_dir, fname)
        builder = BUILDERS.get(rtype)
        if not builder:
            print(f'  Unknown type: {rtype} — skipping'); continue
        cv = canvas.Canvas(out, pagesize=A4)
        cv.setTitle(rtitle)
        if rtype == 'writing_mat':
            builder(cv, resource, colour, colour_cycle=colour_cycle)
        else:
            builder(cv, resource, colour)
        cv.save()
        generated.append(out)
        print(f'  ✓ {os.path.basename(out)}')

    print(f'\nDone — {len(generated)} resource(s) generated.')

if __name__ == '__main__':
    main()
