"""
lesson_data.py — T6W2 Multiplication and Division (L5–L8)

WM CYCLING RULE (must follow exactly):
  Monday    (day 1) → numbers    e.g. [7, 13, 4, 28, 11, 5, 19]
  Tuesday   (day 2) → words      e.g. ['robin', 'castle', 'proud', ...]
  Wednesday (day 3) → emojis     e.g. ['🐝','🌵','🎺','🦊','⚡','🍕','🏔️']
  Thursday  (day 4) → text+image (sentences with embedded emojis)

WM Q&A: questions must be MEMORY RECALL about the sequence shown,
not standalone maths questions.
"""

BLUE   = '1F4E79'
RED    = 'C00000'
PURPLE = '7030A0'
GREEN  = '375623'
TEAL   = '156082'
ORANGE = 'E07000'

LESSON_DATA = {

# ---------------------------------------------------------------------------
# LESSON 5 — T6W2 Monday — Short multiplication (4-digit × 1-digit)
# ---------------------------------------------------------------------------
5: {
    'visuals': {
        'c1_ido1': {
            'title': 'Short multiplication — build up',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '236',
            'bottom': '4',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '236 × 4\n\nOnes first.\nThen tens.\nThen hundreds.\n\nThe regrouped digit goes ABOVE the next column.',
            'notes': 'I DO C1 — Build from 3-digit. Narrate every step. Demonstrate on the squared paper.',
        },
        'c1_ido2': {
            'title': '4-digit × 1-digit — step by step',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '2,364',
            'bottom': '3',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '2,364 × 3\n\nSame method, one more column.\n\nOnes → tens → hundreds → thousands.',
            'notes': 'I DO C1 — Extend to 4-digit. Pause on hundreds column: 3×3+1=10, write 0, regroup 1.',
        },
        'c2_ido1': {
            'title': 'Multiple regroups — 3,476 × 8',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '3,476',
            'bottom': '8',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '3,476 × 8\n\nEstimate first:\n3,500 × 8 = 28,000\n\nEvery column will have a regroup.\nWork slowly.',
            'notes': 'I DO C2 — Multiple regroups every column. Always look for the regroup BEFORE multiplying.',
        },
    },
    'wm': {
        'items': [17, 8, 34, 6, 25, 12, 41],
        'qa': [
            {'q': 'What was the 3rd number?',                      'a': '34'},
            {'q': 'What was the last number?',                     'a': '41'},
            {'q': 'Which number was the largest?',                 'a': '41'},
            {'q': 'What were the first two numbers?',              'a': '17 and 8'},
            {'q': 'What was the 5th number?',                      'a': '25'},
        ]
    },
    'rm': {
        'day': 1,
        'questions': [
            {'num':1,'topic':'Place Value','q':'Write 40,507 in words.','a':'Forty thousand, five hundred and seven'},
            {'num':2,'topic':'Fractions','q':'What is 3/4 as a decimal?','a':'0.75'},
            {'num':3,'topic':'Multiplication','q':'What is 7 × 8?','a':'56'},
            {'num':4,'topic':'Geometry','q':'How many degrees in a right angle?','a':'90°'},
            {'num':5,'topic':'Measurement','q':'How many cm in 1.5 m?','a':'150 cm'},
        ]
    },
    'vocab': [
        ('short multiplication', 'A formal written method for multiplying a number by a 1-digit number, working column by column from ones to the highest place value.'),
        ('product',   'The answer when two numbers are multiplied together.'),
        ('regroup',     'A digit written small above the next column when a column total reaches 10 or more.'),
        ('factor',    'A number that divides exactly into another. 3 and 4 are both factors of 12.'),
        ('estimate',  'A rounded approximation used to check a calculated answer is reasonable.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 6 — T6W2 Tuesday — Short division (4-digit ÷ 1-digit)
# ---------------------------------------------------------------------------
6: {
    'visuals': {
        'c1_ido1': {
            'title': 'Short division — the bus stop layout',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '8,484',
            'bottom': '4',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '8,484 ÷ 4\n\nWork LEFT to RIGHT.\nQuotient goes ABOVE.\n\nCheck: 4 × answer = 8,484.',
            'notes': 'I DO C1 — Stress direction (left to right). Quotient above the bracket. Model checking with multiplication.',
        },
        'c1_ido2': {
            'title': 'Short division — with a remainder',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '7,543',
            'bottom': '3',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '7,543 ÷ 3\n\nRegroup the remainder into the next digit.\n\nFinal remainder written as r N.',
            'notes': 'I DO C1 — Show how remainders are regrouped. Final remainder written as "r N".',
        },
        'c2_ido1': {
            'title': 'What does the remainder mean?',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '9,157',
            'bottom': '6',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '9,157 ÷ 6\n\nIn context:\n9,157 sweets shared between 6 bags.\n\nThe remainder = sweets left over — cannot be shared equally.',
            'notes': 'I DO C2 — Interpret the remainder in context. Ask: does the remainder mean we round up or down?',
        },
    },
    'wm': {
        'items': ['castle', 'multiply', 'penguin', 'divide', 'trophy', 'whisper', 'balance'],
        'qa': [
            {'q': 'What was the 2nd word?',                        'a': 'multiply'},
            {'q': 'What was the last word?',                       'a': 'balance'},
            {'q': 'Which two words are maths operations?',         'a': 'multiply and divide'},
            {'q': 'What was the 4th word?',                        'a': 'divide'},
            {'q': 'How many words were there altogether?',         'a': '7'},
        ]
    },
    'rm': {
        'day': 2,
        'questions': [
            {'num':1,'topic':'Place Value','q':'Round 37,846 to the nearest thousand.','a':'38,000'},
            {'num':2,'topic':'Fractions','q':'What is 0.6 as a fraction?','a':'3/5'},
            {'num':3,'topic':'Division','q':'What is 63 ÷ 9?','a':'7'},
            {'num':4,'topic':'Geometry','q':'How many lines of symmetry does a square have?','a':'4'},
            {'num':5,'topic':'Measurement','q':'How many ml in 2.5 litres?','a':'2,500 ml'},
        ]
    },
    'vocab': [
        ('short division', 'A formal written method for dividing a number by a 1-digit number using the bus stop layout, working left to right.'),
        ('dividend',  'The number being divided. In 24 ÷ 6, the dividend is 24.'),
        ('divisor',   'The number you are dividing by. In 24 ÷ 6, the divisor is 6.'),
        ('quotient',  'The result of a division. In 24 ÷ 6 = 4, the quotient is 4.'),
        ('remainder', 'The amount left over when a number does not divide exactly. 25 ÷ 4 = 6 remainder 1.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 7 — T6W2 Wednesday — Multistep multiplication problems
# ---------------------------------------------------------------------------
7: {
    'visuals': {
        'c1_ido1': {
            'title': 'Choose your method — multiplication',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1,234',
            'bottom': '6',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '1,234 × 6\n\nEstimate: 1,200 × 6 = 7,200\n\nA box holds 1,234 crayons.\nHow many in 6 boxes?',
            'notes': 'I DO C1 — Model full process: underline key words, estimate, calculate, check vs estimate.',
        },
        'c1_ido2': {
            'title': 'Two-step multiplication — find the hidden step',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1,256',
            'bottom': '3',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': 'Step 1: 1,256 × 3 = blue pens\nStep 2: 1,256 + answer = total\n\n1,256 red pens.\nBlue pens: 3 times as many.\nHow many altogether?',
            'notes': 'I DO C1 I2 — Two-step. Slide shows Step 1. Narrate Step 2 verbally and on the squared paper.',
        },
        'c2_ido1': {
            'title': 'Two-step — plan before you calculate',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '2,135',
            'bottom': '4',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': 'Stadium: 2,135 seats per tier.\n4 tiers.\nStep 1: 2,135 × 4 = total seats\nStep 2: total − 975 = occupied\n\nWhat is the second operation?',
            'notes': 'I DO C2 — Model planning both steps (× then −). Ask pupils to predict the second operation.',
        },
    },
    'wm': {
        'items': ['🚀', '🌊', '🎯', '🦁', '🍎', '🔑', '⭐'],
        'qa': [
            {'q': 'What was the 3rd emoji?',                        'a': '🎯'},
            {'q': 'What was the first emoji?',                      'a': '🚀'},
            {'q': 'Which emoji came after the lion?',               'a': '🍎'},
            {'q': 'What was the 6th emoji?',                        'a': '🔑'},
            {'q': 'How many emojis were there altogether?',         'a': '7'},
        ]
    },
    'rm': {
        'day': 3,
        'questions': [
            {'num':1,'topic':'Place Value','q':'What is the value of 7 in 47,362?','a':'7,000'},
            {'num':2,'topic':'Fractions','q':'Order from smallest: 0.5, 3/4, 0.25','a':'0.25, 0.5, 3/4'},
            {'num':3,'topic':'Multiplication','q':'What is 8 × 12?','a':'96'},
            {'num':4,'topic':'Geometry','q':'Area of a rectangle 6 cm × 9 cm?','a':'54 cm²'},
            {'num':5,'topic':'Measurement','q':'How many minutes in 2.5 hours?','a':'150 minutes'},
        ]
    },
    'vocab': [
        ('multiply',         'To find the total of equal groups. 4 × 6 = 24.'),
        ('multiple',         'A number in a times table. 24 is a multiple of both 6 and 4.'),
        ('efficient',        'Using the quickest or most straightforward method to get the right answer.'),
        ('approximate',      'A value close to the exact answer, often found by rounding first.'),
        ('two-step problem', 'A problem that needs two separate calculations to reach the final answer.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 8 — T6W2 Thursday — Multistep × and ÷ problems
# ---------------------------------------------------------------------------
8: {
    'visuals': {
        'c1_ido1': {
            'title': 'Mixed × and ÷ — divide first',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '5,640',
            'bottom': '8',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '5,640 apples → boxes of 8.\nStep 1: 5,640 ÷ 8 = boxes\nStep 2: boxes − 3 = boxes for sale\n\nWhat do I need to find first?',
            'notes': 'I DO C1 — Model a ÷ then − two-step. Stress: identify what you find first before calculating.',
        },
        'c1_ido2': {
            'title': 'Multiply then subtract',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1,425',
            'bottom': '6',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '1,425 parts/hour × 6 hours\nStep 1: 1,425 × 6 = parts made\nStep 2: answer − 2,340 = remaining\n\nDraw a bar model to plan.',
            'notes': 'I DO C1 I2 — Draw a bar model on the board first. Pupils sketch bar model in LP.',
        },
        'c2_ido1': {
            'title': 'Work backwards — how large is each team?',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '4,250',
            'bottom': '5',
            'regroups': '',
            'show_answer': False,
            'answer': '',
            'caption': '85 coaches total.\nEach team gets 5 coaches.\nStep 1: 85 ÷ 5 = number of teams\nStep 2: 4,250 ÷ teams = team size\n\nCheck: teams × size = 4,250?',
            'notes': 'I DO C2 — Work backwards problem. Find teams first, then size. Model on squared paper.',
        },
    },
    'wm': {
        'items': [
            'The 🚀 travels at great speed.',
            'She found a 🔑 under the mat.',
            'He ate an 🍎 after school.',
            'The 🦁 roared loudly.',
            'They sailed on the 🌊.',
            'She aimed at the 🎯.',
            'One ⭐ shone above the rest.',
        ],
        'qa': [
            {'q': 'What did she find under the mat?',               'a': 'A key 🔑'},
            {'q': 'What did he eat after school?',                   'a': 'An apple 🍎'},
            {'q': 'What animal roared loudly?',                     'a': 'The lion 🦁'},
            {'q': 'What was the last sentence about?',              'a': 'A star ⭐'},
            {'q': 'Which sentence mentioned the sea?',              'a': 'They sailed on the 🌊'},
        ]
    },
    'rm': {
        'day': 4,
        'questions': [
            {'num':1,'topic':'Place Value','q':'What is 10 × 3,456?','a':'34,560'},
            {'num':2,'topic':'Fractions','q':'What is half of 3/4?','a':'3/8'},
            {'num':3,'topic':'Division','q':'What is 144 ÷ 12?','a':'12'},
            {'num':4,'topic':'Geometry','q':'How many right angles in a rectangle?','a':'4'},
            {'num':5,'topic':'Measurement','q':'A jug holds 2 litres. How many 250 ml cups can it fill?','a':'8 cups'},
        ]
    },
    'vocab': [
        ('divide',     'To split a number into equal groups. 24 ÷ 6 = 4.'),
        ('quotient',   'The result of a division.'),
        ('bar model',  'A diagram using rectangles to represent quantities and relationships in a problem.'),
        ('reasoning',  'Explaining why an answer is correct using evidence from the calculation or context.'),
        ('justify',    'To provide mathematical argument that proves an answer is correct.'),
    ],
},

}  # end LESSON_DATA
