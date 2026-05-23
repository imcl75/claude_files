"""
lesson_data.py — Hand-authored per-lesson visual and assessment data.

This file contains content that cannot be machine-derived from the JSON plan:
  - VISUALS: exact grid point coordinates for each teaching slide
  - WM: working memory sequences and Q&A
  - RM: rapid maths questions
  - vocab: word/definition pairs

WM CYCLING RULE — must follow every week without exception:
  Monday    (day 1) → numbers   (e.g. [7, 13, 4, 28, 11, 5, 19])
  Tuesday   (day 2) → words     (e.g. ['robin', 'castle', 'proud', ...])
  Wednesday (day 3) → emojis    (e.g. ['🐝', '🌵', '🎺', '🦊', '⚡', '🍕', '🏔️'])
  Thursday  (day 4) → text+image (handled by separate text+image slide builder — TBD)
  Check day position: Monday=1, Tuesday=2, Wednesday=3, Thursday=4
"""

# ---------------------------------------------------------------------------
# COLOUR CONSTANTS (shared)
# ---------------------------------------------------------------------------
BLUE   = '1F4E79'
RED    = 'C00000'
PURPLE = '7030A0'
GREEN  = '375623'
TEAL   = '156082'

# ---------------------------------------------------------------------------
# LESSON 1 — T5W1 Monday — Directions on a Grid
# ---------------------------------------------------------------------------
LESSON_DATA = {

1: {
    'visuals': {
        'c1_ido1': {
            'title': 'Giving directions on a grid',
            'cols': 6, 'rows': 6,
            'points': [(1,1,'A',BLUE), (4,3,'B',RED)],
            'caption': 'How do we get from A to B?',
            'notes': "I DO C1 — Narrate: 'From A, I move 3 right, then 2 up, and I arrive at B.'"
        },
        'c1_ido2': {
            'title': 'Does the order of moves matter?',
            'cols': 6, 'rows': 6,
            'points': [(1,4,'A',BLUE), (4,2,'B',RED)],
            'caption': 'Try: 3 right then 2 down. Now try: 2 down then 3 right. Where do you end up?',
            'notes': "I DO C1 — Key question: does the order of moves change the destination?"
        },
        'c1_wedo': {
            'title': 'Your turn — write the directions',
            'cols': 6, 'rows': 6,
            'points': [(1,2,'A',BLUE), (5,5,'B',RED)],
            'sentence_stem': 'From A, move ___ right/left and ___ up/down to reach B.',
            'notes': "WE DO C1 — Pupils tell the teacher what moves to make. Compare correct answers."
        },
        'c2_ido1': {
            'title': 'Multi-step journeys — three positions',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A',BLUE), (3,2,'B',PURPLE), (5,5,'C',RED)],
            'caption': 'Journey: A → B → C. Write directions for each leg separately.',
            'notes': "I DO C2 — Model leg 1 (A→B): 2 right, 1 up. Leg 2 (B→C): 2 right, 3 up."
        },
    },
    'wm': {
        'items': [7, 13, 4, 28, 11, 5, 19],
        'qa': [
            {'q': 'What was the 1st number?',        'a': '7'},
            {'q': 'What was the 3rd number?',         'a': '4'},
            {'q': 'Sum of the first two numbers?',    'a': '20  (7 + 13)'},
            {'q': 'How many odd numbers were there?', 'a': '4  (7, 13, 11, 19)'},
            {'q': 'What was the largest number?',     'a': '28'},
        ]
    },
    'rm': {
        'day': 1,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is the value of the digit 4 in 34,512?','a':'4,000'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 1/2 as a decimal?',                  'a':'0.5'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 7 × 8?',                             'a':'56'},
            {'num':4,'topic':'Geometry',                 'q':'How many sides does a hexagon have?',         'a':'6'},
            {'num':5,'topic':'Measurement',              'q':'How many centimetres are in 2 metres?',       'a':'200 cm'},
        ]
    },
    'vocab': [
        ('grid',      'A pattern of lines making rows and columns of squares.'),
        ('direction', 'The way you move on a grid — left, right, up or down.'),
        ('steps',     'The number of squares you move in one direction.'),
        ('route',     'The path you take from one place to another.'),
        ('position',  'The exact place where something sits on a grid.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 2 — T5W1 Tuesday — Translating shapes on a grid
# ---------------------------------------------------------------------------
2: {
    'visuals': {
        'c1_ido1': {
            'title': 'Moving a point, then a shape',
            'cols': 7, 'rows': 7,
            'points': [(2,2,'A','1F4E79')],
            'caption': 'Move A: 4 right, 2 up. Where does it land?',
            # Single point shown first — no polygon, no translation yet
            # Pedagogy: establish the principle with a dot before scaling to a shape
            'notes': "I DO C1 — Model moving a single point, then extend to a square (track each corner)."
        },
        'c1_ido2': {
            'title': 'What stays the same?',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(3,3,'C','1F4E79'),(1,3,'D','1F4E79')],
            'polygon': ['A','B','C','D'],
            'translation': [3, 2],           # 3 right, 2 up
            'shape_a_label': 'Shape A',
            'shape_b_label': 'Shape B',
            'caption': 'Move the square 3 right, 2 up. Has its size or shape changed?',
            'notes': "I DO C1 — Shape A static on load. Click: Shape B appears with translation arrow. Ask: has anything changed about the shape? Size? Orientation?"
        },
        'c1_wedo': {
            'title': 'Your turn — track the vertices',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(4,1,'B','1F4E79'),(2,3,'C','1F4E79')],
            'polygon': ['A','B','C'],
            # No translation — pupils predict the destination, We Do
            'sentence_stem': 'Move each vertex ___ right and ___ up. Draw the new triangle.',
            'notes': "WE DO C1 — Show triangle, pupils track all three vertices using the same direction on mini-whiteboards."
        },
        'c2_ido1': {
            'title': 'Moving polygons with more vertices',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(4,3,'C','1F4E79'),(2,4,'D','1F4E79'),(0,3,'E','1F4E79')],
            'polygon': ['A','B','C','D','E'],
            'translation': [2, 3],           # 2 right, 3 up
            'shape_a_label': 'Shape A',
            'shape_b_label': 'Shape B',
            'caption': 'Move the pentagon 2 right, 3 up. Track every vertex.',
            'notes': "I DO C2 — Pentagon. Click reveals Shape B. Stress: every vertex moves the same distance. What stays the same? Size, shape, orientation — all identical."
        },
    },
    'wm': {
        'items': ['robin', 'castle', 'proud', 'February', 'enormous', 'gravity', 'swift'],
        'qa': [
            {'q': 'What was the 1st word?',                        'a': 'robin'},
            {'q': 'What was the 4th word?',                        'a': 'February'},
            {'q': 'Which word means very large?',                  'a': 'enormous'},
            {'q': 'How many words had more than 6 letters?',       'a': '3  (February, enormous, gravity)'},
            {'q': 'What was the last word?',                       'a': 'swift'},
        ]
    },
    'rm': {
        'day': 2,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is 10 more than 4,756?',                 'a':'4,766'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 3/4 as a decimal?',                   'a':'0.75'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 63 ÷ 9?',                             'a':'7'},
            {'num':4,'topic':'Geometry',                 'q':'What is the sum of angles in a triangle?',    'a':'180°'},
            {'num':5,'topic':'Measurement',              'q':'How many grams are in 1.5 kg?',               'a':'1,500 g'},
        ]
    },
    'vocab': [
        ('translation', 'Moving a shape without rotating or flipping it.'),
        ('vertex',      'A corner point of a shape (plural: vertices).'),
        ('congruent',   'Shapes that are identical in size and shape.'),
        ('polygon',     'A flat shape with straight sides.'),
        ('orientation', 'The direction a shape is facing.'),
    ],
},


# ---------------------------------------------------------------------------
# LESSON 3 — T5W1 Wednesday — Describing translations
# ---------------------------------------------------------------------------
3: {
    'visuals': {
        'c1_ido1': {
            'title': 'What is a translation?',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(2,3,'C','1F4E79')],
            'polygon': ['A','B','C'],
            'translation': [4, 2],   # 4 right, 2 up
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'caption': 'The shape slides without rotating or flipping.\nThis is called a translation.',
            'notes': "I DO C1 — Triangle in lower-left. Click: translated image appears 4 right 2 up. Introduce the word 'translation'. Stress: no rotation, no reflection — pure slide."
        },
        'c1_ido2': {
            'title': 'Describing single-direction translations',
            'cols': 7, 'rows': 7,
            'points': [(1,2,'A','1F4E79'),(4,2,'B','1F4E79'),(1,4,'C','1F4E79')],
            'polygon': ['A','B','C'],
            'translation': [0, 3],   # 3 up only — single direction
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'caption': 'Count how far one vertex has moved.\nThe same move applies to all vertices.',
            'notes': "I DO C1 — Single direction (vertical only). Track vertex A: was at row 2, now at row 5 — moved 3 up. Sentence stem: 'Translated 3 up.'"
        },
        'c1_wedo': {
            'title': 'Your turn — describe the move',
            'cols': 7, 'rows': 7,
            'points': [(2,1,'A','1F4E79'),(5,1,'B','1F4E79'),(6,3,'C','1F4E79'),(2,3,'D','1F4E79'),
                       (2,4,'E','C00000'),(5,4,'F','C00000'),(6,6,'G','C00000'),(2,6,'H','C00000')],
            'polygon': ['A','B','C','D'],
            # Image polygon drawn separately using red points — no animation needed
            # Red points show the image in its translated position (3 up)
            'sentence_stem': 'The shape has been translated ___ right/left and ___ up/down.',
            'notes': "WE DO C1 — Show original (blue) and image (red) rectangle. Pupils write description on whiteboards: 3 up. Share."
        },
        'c2_ido1': {
            'title': 'Translations in two directions',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(2,3,'C','1F4E79')],
            'polygon': ['A','B','C'],
            'translation': [3, 2],   # 3 right, 2 up — two directions
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'caption': 'Track any one vertex from original to image.\nCount right/left first, then up/down.',
            'notes': "I DO C2 — Two-directional translation. Track vertex A: col 1→4 (3 right), row 1→3 (2 up). Sentence: 'Translated 3 right and 2 up.' Key Q: does it matter which vertex you track? Try C."
        },
    },
    'wm': {
        # Wednesday = emojis
        'items': ['🐠', '🎸', '🌋', '🐧', '🎃', '🦋', '🚂'],
        'qa': [
            {'q': 'What was the 1st emoji?',                 'a': '🐠 (fish)'},
            {'q': 'What was the 3rd emoji?',                 'a': '🌋 (volcano)'},
            {'q': 'Which emoji was an insect?',              'a': '🦋 (butterfly)'},
            {'q': 'How many emojis were living things?',     'a': '3  (🐠 🐧 🦋)'},
            {'q': 'What was the last emoji?',                'a': '🚂 (train)'},
        ]
    },
    'rm': {
        'day': 3,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is 1,000 more than 23,450?',              'a':'24,450'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 1/4 as a decimal?',                    'a':'0.25'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 9 × 4?',                               'a':'36'},
            {'num':4,'topic':'Geometry',                 'q':'What is the name for a shape with 8 sides?',   'a':'Octagon'},
            {'num':5,'topic':'Measurement',              'q':'How many millimetres are in 3 cm?',             'a':'30 mm'},
        ]
    },
    'vocab': [
        ('translation', 'A sliding movement where a shape moves without rotating or flipping.'),
        ('image',       'The new position of a shape after it has been translated.'),
        ('original',    'The starting position of a shape before it is translated.'),
        ('horizontal',  'Going left or right — along the x-direction.'),
        ('vertical',    'Going up or down — along the y-direction.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 4 — T5W1 Thursday — Drawing translations
# ---------------------------------------------------------------------------
4: {
    'visuals': {
        'c1_ido1': {
            'title': 'Drawing a translation — vertex by vertex',
            'cols': 7, 'rows': 7,
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(3,3,'C','1F4E79'),(1,3,'D','1F4E79')],
            'polygon': ['A','B','C','D'],
            'translation': [3, 2],   # 3 right, 2 up
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'caption': "Translate square ABCD: 3 right, 2 up.\nMove each vertex individually — never move the whole shape by eye.",
            'notes': "I DO C1 — Square. Move vertex A first: col 1+3=4, row 1+2=3. Repeat for B, C, D. Click reveals image. Join vertices and label A', B', C', D'."
        },
        'c1_ido2': {
            'title': 'Spot the error',
            'cols': 7, 'rows': 7,
            # Triangle original: A(1,1) B(3,1) C(2,3)
            # Correct image (3 right, 2 up): A'(4,3) B'(6,3) C'(5,5)
            # Error: only A translated, B and C left in place — shown in red
            'points': [
                (1,1,"A",'1F4E79'),(3,1,"B",'1F4E79'),(2,3,"C",'1F4E79'),  # original
                (4,3,"A'",'C00000'),                                          # only A moved — error
                (3,1,"B",'C00000'),(2,3,"C",'C00000'),                       # B and C unchanged — error
            ],
            'polygon': ['A','B','C'],
            'caption': "Instruction: translate 3 right, 2 up.\nOnly A has moved — what went wrong?\nAll vertices must move the same distance.",
            'notes': "I DO C1 STM — Error: only vertex A moved. B and C left in place. Result: misshapen triangle. Rule: every vertex moves by the same translation vector."
        },
        'c1_wedo': {
            'title': "Label original and image vertices",
            'cols': 7, 'rows': 7,
            # Triangle original: (1,1)(4,1)(2,4) — translation 2 right 1 up
            'points': [(1,1,'A','1F4E79'),(4,1,'B','1F4E79'),(2,4,'C','1F4E79')],
            'polygon': ['A','B','C'],
            'translation': [2, 1],
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'sentence_stem': "Label the original vertices A, B, C.\nLabel the image vertices A', B', C'.",
            'notes': "WE DO C1 — Class draw the translated triangle together, labelling both sets of vertices. Peer-check by measuring the distance each vertex moved."
        },
        'c2_ido1': {
            'title': 'Two-directional translations',
            'cols': 7, 'rows': 7,
            # Pentagon original: (1,1)(3,1)(4,3)(2,4)(0,3)
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(4,3,'C','1F4E79'),(2,4,'D','1F4E79'),(0,3,'E','1F4E79')],
            'polygon': ['A','B','C','D','E'],
            'translation': [2, 2],   # 2 right, 2 up
            'shape_a_label': 'Original',
            'shape_b_label': 'Image',
            'caption': 'Translate pentagon: 2 right, 2 up.\nTrack each vertex in turn — right first, then up.',
            'notes': "I DO C2 — Pentagon with two-directional translation. Stress moving each vertex separately. Click reveals image."
        },
        'c2_ido2': {
            'title': 'Working backwards',
            'cols': 7, 'rows': 7,
            # Show image only, original to be found
            # Image (red) at (4,3)(6,3)(5,5) — translation was 3 right 2 up
            # So original is at (1,1)(3,1)(2,3)
            'points': [
                (4,3,"A'",'C00000'),(6,3,"B'",'C00000'),(5,5,"C'",'C00000'),  # image shown
                (1,1,"A",'4FAD5B'),(3,1,"B",'4FAD5B'),(2,3,"C",'4FAD5B'),    # original revealed on click
            ],
            'polygon': ["A'","B'","C'"],
            'caption': "Translation was 3 right, 2 up.\nThe image is shown. Find the original.\nReverse: move 3 left and 2 down.",
            'notes': "I DO C2 — Reverse task: given image (red), find original. Reverse translation: 3 left, 2 down. Click reveals original (green). Key Q: what is the reverse of any translation?"
        },
        'c2_wedo': {
            'title': 'Find the original shape',
            'cols': 7, 'rows': 7,
            # Image rectangle (red): corners at (4,4)(6,4)(6,6)(4,6), translation was 3 right 3 up
            # Original to find: (1,1)(3,1)(3,3)(1,3)
            'points': [(4,4,"A'",'C00000'),(6,4,"B'",'C00000'),(6,6,"C'",'C00000'),(4,6,"D'",'C00000')],
            'polygon': ["A'","B'","C'","D'"],
            'sentence_stem': "The image moved 3 right and 3 up to get here.\nTo find the original, I move ___ left and ___ down.",
            'notes': "WE DO C2 — Pupils reverse the translation to find and draw the original rectangle on whiteboards."
        },
    },
    'wm': {
        # Thursday = text + image (picture_scene type)
        'items': [
            {'text': 'planet',    'image': 'https://em-content.zobj.net/source/google/387/ringed-planet_1fa90.png'},
            {'text': 'forest',    'image': 'https://em-content.zobj.net/source/google/387/deciduous-tree_1f333.png'},
            {'text': 'triangle',  'image': 'https://em-content.zobj.net/source/google/387/red-triangle-pointed-up_1f53a.png'},
            {'text': 'lightning', 'image': 'https://em-content.zobj.net/source/google/387/high-voltage_26a1.png'},
            {'text': 'castle',    'image': 'https://em-content.zobj.net/source/google/387/european-castle_1f3f0.png'},
            {'text': 'compass',   'image': 'https://em-content.zobj.net/source/google/387/compass_1f9ed.png'},
            {'text': 'cactus',    'image': 'https://em-content.zobj.net/source/google/387/cactus_1f335.png'},
        ],
        'qa': [
            {'q': 'What was the 1st word?',                   'a': 'planet'},
            {'q': 'What was the 4th word?',                   'a': 'lightning'},
            {'q': 'Which word is linked to navigation?',      'a': 'compass'},
            {'q': 'How many words were natural features?',    'a': '3  (forest, lightning, cactus)'},
            {'q': 'What was the last word?',                  'a': 'cactus'},
        ]
    },
    'rm': {
        'day': 4,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is the value of the digit 7 in 57,083?',    'a':'7,000'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 3/10 as a decimal?',                     'a':'0.3'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 48 ÷ 6?',                                'a':'8'},
            {'num':4,'topic':'Geometry',                 'q':'A shape has 4 equal sides and 4 right angles. What is it?', 'a':'A square'},
            {'num':5,'topic':'Measurement',              'q':'How many seconds are in 2 minutes?',              'a':'120 seconds'},
        ]
    },
    'vocab': [
        ('congruent',  'Identical in shape and size — a translated shape is always congruent to the original.'),
        ('label',      "To mark the vertices of a shape — use A, B, C for the original and A', B', C' for the image."),
        ('image',      'The new position of a shape after a translation.'),
        ('original',   'The shape before it is moved.'),
        ('describe',   'To say how far and in which direction a shape has moved.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 11 — T5W3 Wednesday — Completing symmetrical patterns
# ---------------------------------------------------------------------------
11: {
    'visuals': {
        'c1_ido1': {
            'slide_type': 'symmetry_grid',
            'title': 'Completing symmetrical patterns',
            'cols': 8, 'rows': 8,
            # Mirror line at column 4 (vertical)
            'mirror_col': 4,
            # Shape A: 5 squares on the left side (col < 4)
            # Squares specified as (col, row) in grid coords, row 0 = bottom
            'squares_a': [(1,6),(2,5),(2,6),(3,4),(1,4)],
            # Shape B: reflected across mirror at col 4 (each col c → 8-c)
            'squares_b': [(7,6),(6,5),(6,6),(5,4),(7,4)],
            # Pedagogy: animate the reflection — pupils predict, then reveal
            'animate_b': True,
            'caption': 'How far is each square from the mirror line?\nCount carefully — then mark the same distance on the other side.',
            'notes': "I DO C1 — Shape A static on load. Click: Shape B (reflection) appears. Stress: count distance from mirror line, not from edge."
        },
        'c1_ido2': {
            # C1 Spot the error: reflected point placed at wrong distance from mirror
            # A at col 2 (distance 2 from mirror at col 4). Correct reflection = col 6.
            # Error: pupil placed reflection at col 7 (distance 3 — one too far).
            'slide_type':  'symmetry_grid',
            'title':       'Spot the error — wrong distance',
            'cols': 8, 'rows': 8,
            'mirror_col':  4,
            'squares_a':   [],
            'squares_b':   [],
            'animate_b':   False,
            'points': [
                (2, 4, 'A',  '1F4E79'),   # original point, 2 squares left of mirror
                (7, 4, '✗',  'C00000'),   # wrong reflection (3 squares right — too far)
                (6, 4, "A'", '4FAD5B'),   # correct reflection (2 squares right) — revealed on click
            ],
            'animate_labels': ["A'"],
            'animate_b':  True,
            'caption':    'A is 2 squares from the mirror.\nWhere should its reflection be?\nIs the red mark correct?',
            'notes':      "C1 STM — A is 2 from mirror (col 4). Error mark at col 7 (3 squares right). Click reveals correct position at col 6 (2 squares right). Rule: equidistant from the mirror line."
        },
        'c1_wedo': {
            'slide_type': 'symmetry_grid',
            'title': 'Complete the half-pattern',
            'cols': 8, 'rows': 8,
            'mirror_col': 4,
            'squares_a': [(2,7),(1,6),(3,6),(2,5),(3,4)],
            'squares_b': [],   # blank — pupils complete
            'animate_b': False,
            'sentence_stem': 'For each square, count its distance from the mirror line. Mark the same distance on the other side.',
            'notes': "WE DO C1 — Pupils complete the reflection on mini-whiteboards. Share and compare."
        },
        'c2_ido1': {
            # Composing symmetrical shapes: two congruent right-angled triangles
            # Draw them as polygons. First triangle static, second animated into position.
            'slide_type': 'grid',
            'title': 'Composing symmetrical shapes from congruent pieces',
            'cols': 8, 'rows': 8,
            # Triangle 1 (bottom-left): A(1,1) B(3,1) C(1,3)
            'points': [(1,1,'A','1F4E79'),(3,1,'B','1F4E79'),(1,3,'C','1F4E79')],
            'polygon': ['A','B','C'],
            # Triangle 2 (reflected to make rectangle): joins along hypotenuse
            # B(3,1) D(3,3) C(1,3) — appears on click
            'translation': None,
            # Use polygon_b to define second triangle separately
            'polygon_b_points': [(3,1,'B','E8642A'),(3,3,'D','E8642A'),(1,3,'C','E8642A')],
            'polygon_b_edges': [['B','D'],['D','C'],['C','B']],
            'shape_a_label': 'Triangle 1',
            'shape_b_label': 'Triangle 2',
            'caption': 'Join the two triangles along the hypotenuse.\nWhat shape do you make?\nIs the join line a line of symmetry?',
            'notes': "I DO C2 — Triangle 1 static. Click: Triangle 2 appears joined along hypotenuse making a rectangle. Mark line of symmetry."
        },
    },
    'wm': {
        # Wednesday = emojis
        'items': ['🐝', '🌵', '🎺', '🦊', '⚡', '🍕', '🏔️'],
        'qa': [
            {'q': 'What was the 1st emoji?',                    'a': '🐝 (bee)'},
            {'q': 'What was the 4th emoji?',                    'a': '🦊 (fox)'},
            {'q': 'Which emoji was a musical instrument?',      'a': '🎺 (trumpet)'},
            {'q': 'How many emojis were living things?',        'a': '3  (🐝 🌵 🦊)'},
            {'q': 'What was the last emoji?',                   'a': '🏔️ (mountain)'},
        ]
    },
    'rm': {
        'day': 3,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is 100 less than 7,340?',              'a':'7,240'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 0.25 as a fraction?',               'a':'1/4'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 8 × 7?',                            'a':'56'},
            {'num':4,'topic':'Geometry',                 'q':'How many lines of symmetry does a square have?', 'a':'4'},
            {'num':5,'topic':'Measurement',              'q':'How many mm are in 4.5 cm?',                'a':'45 mm'},
        ]
    },
    'vocab': [
        ('symmetry',    'When one half of a shape or pattern is a mirror image of the other.'),
        ('mirror line', 'The line across which a shape or pattern is reflected.'),
        ('reflect',     'To flip a shape or point across a mirror line.'),
        ('equidistant', 'The same distance away — a reflected point is equidistant from the mirror line.'),
        ('congruent',   'Identical in shape and size.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 17 — T5W5 Monday — Analogue and digital time
# ---------------------------------------------------------------------------
17: {
    'visuals': {
        'c1_ido1': {
            'slide_type': 'clock',
            'title': 'Reading analogue clocks',
            # Four clocks showing common times — o'clock, half past, quarter past, quarter to
            'clocks': [
                {'hour': 3,  'minute': 0,  'label': '3:00'},
                {'hour': 7,  'minute': 30, 'label': '7:30'},
                {'hour': 11, 'minute': 15, 'label': '11:15'},
                {'hour': 4,  'minute': 45, 'label': '4:45'},
            ],
            'caption': 'Read each clock aloud.\nWrite the 12-hour digital time.',
            'notes': "I DO C1 — Work through each clock. Stress: short hand = hours, long hand = minutes. 4:45 = quarter to 5."
        },
        'c1_ido2': {
            'slide_type': 'clock',
            'title': "am and pm — what's the difference?",
            # Same time shown twice — morning and afternoon
            'clocks': [
                {'hour': 7, 'minute': 45, 'label': '7:45 am'},
                {'hour': 7, 'minute': 45, 'label': '7:45 pm'},
            ],
            'caption': 'Both clocks show the same time.\nWhat is different about them?\nHow do we know which is morning and which is evening?',
            'notes': "I DO C1 — Key question: same clock reading, different meaning. am = before noon, pm = after noon."
        },
        'c1_wedo': {
            'slide_type': 'clock',
            'title': 'Write the 12-hour digital time',
            # Three clocks, digital boxes blank for pupils to write
            'clocks': [
                {'hour': 9,  'minute': 20, 'label': '', 'show_digital': True},
                {'hour': 1,  'minute': 50, 'label': '', 'show_digital': True},
                {'hour': 6,  'minute': 35, 'label': '', 'show_digital': True},
            ],
            'sentence_stem': 'The short hand shows ___. The long hand shows ___ minutes. The time is ___.',
            'notes': "WE DO C1 — Pupils write digital time in the box. Sentence stem supports less confident."
        },
        'c2_ido1': {
            'slide_type': 'number_line',
            'title': 'Converting to 24-hour time',
            'nl_start': 0, 'nl_end': 24,
            'nl_ticks': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
            'nl_markers': [
                {'val': 0,  'label': '00:00\nmidnight', 'color': '7030A0'},
                {'val': 12, 'label': '12:00\nmidday',   'color': 'C00000'},
            ],
            'examples': [
                {'val': 9,  'text': '9:15 am\n= 09:15'},
                {'val': 15, 'text': '3:45 pm\n= 15:45'},
            ],
            'caption': 'am times: same digits in 24-hour.\npm times: add 12 to the hours.\nSpecial cases: midday = 12:00, midnight = 00:00.',
            'notes': "I DO C2 — Number line from 00:00 to 23:59. Midday marked at 12:00. Show am times = same, pm times = +12."
        },
        'c2_ido2': {
            # Special cases: noon and midnight
            'slide_type': 'clock',
            'title': 'Special cases — noon and midnight',
            'clocks': [
                {'hour': 12, 'minute': 0, 'label': '12:00 noon\n= 12:00'},
                {'hour': 0,  'minute': 0, 'label': '12:00 midnight\n= 00:00'},
            ],
            'caption': 'Noon and midnight are the two special cases.\n12:00 midday stays as 12:00.\n12:00 midnight becomes 00:00.',
            'notes': "I DO C2 — Special cases only: noon (12:00 stays 12:00) and midnight (12:00 am becomes 00:00). Common error: writing midnight as 12:00."
        },
        'c2_wedo': {
            'slide_type': 'clock',
            'title': '12 conversion tasks on whiteboards',
            'clocks': [
                {'hour': 2,  'minute': 30, 'label': '', 'show_digital': True},
                {'hour': 8,  'minute': 15, 'label': '', 'show_digital': True},
                {'hour': 11, 'minute': 50, 'label': '', 'show_digital': True},
            ],
            'sentence_stem': 'If the time is pm, I add ___ to the hours. If the time is am, the 24-hour time is ___.',
            'notes': "WE DO C2 — Pupils convert each clock to 24-hour time on whiteboards."
        },
    },
    'wm': {
        'items': [8, 3, 15, 6, 22, 11, 4],
        'qa': [
            {'q': 'What was the 2nd number?',          'a': '3'},
            {'q': 'What was the 5th number?',           'a': '22'},
            {'q': 'Sum of the 1st and last numbers?',   'a': '12  (8 + 4)'},
            {'q': 'Which numbers were multiples of 3?', 'a': '3, 15, 6'},
            {'q': 'What was the largest number?',       'a': '22'},
        ]
    },
    'rm': {
        'day': 1,
        'questions': [
            {'num':1,'topic':'Place Value',              'q':'What is 1,000 more than 45,620?',           'a':'46,620'},
            {'num':2,'topic':'Fractions and Decimals',   'q':'What is 0.75 as a fraction?',               'a':'3/4'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 9 × 6?',                            'a':'54'},
            {'num':4,'topic':'Measurement',              'q':'How many minutes in 3 hours?',              'a':'180 minutes'},
            {'num':5,'topic':'Measurement – Time',       'q':'What is 7:45 pm in 24-hour time?',          'a':'19:45'},
        ]
    },
    'vocab': [
        ('analogue',    'A clock with hands that move around a numbered face.'),
        ('digital',     'A clock that shows the time as numbers.'),
        ('12-hour',     'A clock system using am (midnight to midday) and pm (midday to midnight).'),
        ('24-hour',     'A clock system using hours 00 to 23, with no am or pm.'),
        ('am / pm',     'am = before midday; pm = after midday.'),
    ],
},

}  # end LESSON_DATA

