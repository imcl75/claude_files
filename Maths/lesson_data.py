"""
lesson_data.py — Hand-authored per-lesson visual and assessment data.
Term 6 — Multiplication and Division (and later topics).

WM CYCLING RULE:
  Monday    (day 1) → numbers    e.g. [7, 13, 4, 28, 11, 5, 19]
  Tuesday   (day 2) → words      e.g. ['robin', 'castle', ...]
  Wednesday (day 3) → emojis     e.g. ['🐝','🌵','🎺','🦊','⚡','🍕','🏔️']
  Thursday  (day 4) → text+image (sentences with embedded emojis)
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
        # ── Cycle 1 I Do 1 — build up from 2-digit ──────────────────────
        'c1_ido1': {
            'title': 'Short multiplication — build up',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '236',
            'bottom': '4',
            'carries': '  1 ',
            'show_answer': True,
            'answer': '944',
            'caption': 'Start with ones. 6×4=24. Write 4, carry 2.\nTens: 3×4=12, +2=14. Write 4, carry 1.\nHundreds: 2×4=8, +1=9.',
            'notes': 'I DO C1 — Lesson 5. Model narrating every step. Stress: start at ones, carry goes ABOVE next column.',
        },
        # ── Cycle 1 I Do 2 — 4-digit × 1-digit step by step ─────────────
        'c1_ido2': {
            'title': '4-digit × 1-digit — step by step',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '2364',
            'bottom': '3',
            'carries': '   1 ',
            'show_answer': True,
            'answer': '7092',
            'caption': 'Ones: 4×3=12 → write 2, carry 1.\nTens: 6×3=18, +1=19 → write 9, carry 1.\nH: 3×3=9, +1=10 → write 0, carry 1.\nTh: 2×3=6, +1=7.',
            'notes': 'I DO C1 — Narrate each step. Pause on the hundreds column: 9+1=10 → write 0, carry 1 into thousands.',
        },
        # ── Cycle 2 I Do 1 — multiple carries ────────────────────────────
        'c2_ido1': {
            'title': 'Multiple carries — 3,476 × 8',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '3476',
            'bottom': '8',
            'carries': ' 365 ',
            'show_answer': True,
            'answer': '27808',
            'caption': 'Estimate first: 3,500×8=28,000.\nOnes: 6×8=48 → write 8, carry 4.\nTens: 7×8=56, +4=60 → write 0, carry 6.\nH: 4×8=32, +6=38 → write 8, carry 3.\nTh: 3×8=24, +3=27.',
            'notes': 'I DO C2 — Lesson 5. Multiple carries every column. Emphasise: always check carry BEFORE multiplying next column. Estimate = 28,000 → answer 27,808 ✓ close.',
        },
        # c2_ido2 is auto-built from STM JSON
    },
    'wm': {
        # Monday → numbers
        'items': [17, 8, 34, 6, 25, 12, 41],
        'qa': [
            {'q': 'What is 6 × 7?',                          'a': '42'},
            {'q': 'What is 8 × 9?',                          'a': '72'},
            {'q': 'What is 12 × 4?',                         'a': '48'},
            {'q': 'What are the first 4 multiples of 8?',    'a': '8, 16, 24, 32'},
            {'q': 'What is 7 × 7?',                          'a': '49'},
        ]
    },
    'rm': {
        'day': 1,
        'questions': [
            {'num':1,'topic':'Place Value','q':'Write 40,507 in words.','a':'Forty thousand, five hundred and seven'},
            {'num':2,'topic':'Fractions and Decimals','q':'What is 3/4 as a decimal?','a':'0.75'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 7 × 8?','a':'56'},
            {'num':4,'topic':'Geometry','q':'How many degrees in a right angle?','a':'90°'},
            {'num':5,'topic':'Measurement','q':'How many cm in 1.5 m?','a':'150 cm'},
        ]
    },
    'vocab': [
        ('short multiplication', 'A formal written method for multiplying a number by a 1-digit number, working column by column from ones to the highest place value.'),
        ('product',              'The answer when two numbers are multiplied together. 6 × 4 = 24, so 24 is the product.'),
        ('carry',                'A digit carried into the next column when a column total is 10 or more. The carried digit is written small above the next column.'),
        ('factor',               'A number that divides exactly into another. 3 and 4 are both factors of 12.'),
        ('estimate',             'A sensible approximation, often made by rounding, used to check that a calculated answer is reasonable.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 6 — T6W2 Tuesday — Short division (4-digit ÷ 1-digit)
# ---------------------------------------------------------------------------
6: {
    'visuals': {
        # ── Cycle 1 I Do 1 — bus stop layout, no remainder ───────────────
        'c1_ido1': {
            'title': 'Short division — the bus stop layout',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '8484',
            'bottom': '4',
            'carries': '',
            'show_answer': True,
            'answer': '2121',
            'caption': 'Work LEFT to RIGHT.\n8÷4=2. 4÷4=1. 8÷4=2. 4÷4=1.\nQuotient written ABOVE the bracket.\nCheck: 4 × 2,121 = 8,484 ✓',
            'notes': 'I DO C1 — Lesson 6. Stress the direction (left to right). Stress where the quotient goes (above). Model checking with multiplication.',
        },
        # ── Cycle 1 I Do 2 — 4-digit with remainder ──────────────────────
        'c1_ido2': {
            'title': 'Short division — with a remainder',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '7543',
            'bottom': '3',
            'carries': '',
            'show_answer': True,
            'answer': '2514r1',
            'caption': '7÷3=2 rem 1 → carry 1.\n15÷3=5. 4÷3=1 rem 1 → carry 1.\n13÷3=4 rem 1.\nAnswer: 2,514 remainder 1.',
            'notes': 'I DO C1 — Lesson 6. Show how remainders are carried as a small digit before the next dividend digit. Final remainder written as "r N".',
        },
        # ── Cycle 2 I Do 1 — context: what does the remainder mean? ──────
        'c2_ido1': {
            'title': 'What does the remainder mean?',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '9157',
            'bottom': '6',
            'carries': '',
            'show_answer': True,
            'answer': '1526r1',
            'caption': '9,157 sweets shared equally between 6 bags.\nEach bag gets 1,526 sweets.\n1 sweet is left over — it cannot be shared.\nIn context: "1 remainder" = 1 extra sweet.',
            'notes': 'I DO C2 — Lesson 6. Model interpreting the remainder in context. Ask: does the remainder mean we round up or down? Depends on the problem.',
        },
        # c2_ido2 is auto-built from STM JSON
    },
    'wm': {
        # Tuesday → words
        'items': ['castle', 'multiply', 'penguin', 'divide', 'trophy', 'whisper', 'balance'],
        'qa': [
            {'q': 'What is 56 ÷ 7?',                                  'a': '8'},
            {'q': 'What is 72 ÷ 9?',                                   'a': '8'},
            {'q': 'What is 48 ÷ 6?',                                   'a': '8'},
            {'q': 'What is the remainder when 25 is divided by 4?',    'a': '1'},
            {'q': 'What is 100 ÷ 4?',                                  'a': '25'},
        ]
    },
    'rm': {
        'day': 2,
        'questions': [
            {'num':1,'topic':'Place Value','q':'Round 37,846 to the nearest thousand.','a':'38,000'},
            {'num':2,'topic':'Fractions and Decimals','q':'What is 0.6 as a fraction?','a':'3/5'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 63 ÷ 9?','a':'7'},
            {'num':4,'topic':'Geometry','q':'How many lines of symmetry does a square have?','a':'4'},
            {'num':5,'topic':'Measurement','q':'How many ml in 2.5 litres?','a':'2,500 ml'},
        ]
    },
    'vocab': [
        ('short division',  'A formal written method for dividing a number by a 1-digit number, using the bus stop layout and working from the largest digit to the smallest.'),
        ('dividend',        'The number being divided. In 24 ÷ 6 = 4, the dividend is 24.'),
        ('divisor',         'The number you are dividing by. In 24 ÷ 6 = 4, the divisor is 6.'),
        ('quotient',        'The answer to a division. In 24 ÷ 6 = 4, the quotient is 4.'),
        ('remainder',       'The amount left over when a number cannot be divided exactly. 25 ÷ 4 = 6 remainder 1.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 7 — T6W2 Wednesday — Multistep multiplication problems
# ---------------------------------------------------------------------------
7: {
    'visuals': {
        # ── Cycle 1 I Do 1 — one-step × problem, choosing method ─────────
        'c1_ido1': {
            'title': 'Choose your method — multiplication',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1234',
            'bottom': '6',
            'carries': '  12 ',
            'show_answer': True,
            'answer': '7404',
            'caption': 'A box holds 1,234 crayons.\nHow many crayons in 6 boxes?\nEstimate: 1,200×6=7,200.\nCalculate: 1,234×6=7,404 ✓',
            'notes': 'I DO C1 — Lesson 7. Model the full process: underline key words, write estimate, choose short multiplication, calculate, check vs estimate.',
        },
        # ── Cycle 1 I Do 2 — two-step × problem ──────────────────────────
        'c1_ido2': {
            'title': 'Two-step multiplication — find the hidden step',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1256',
            'bottom': '3',
            'carries': ' 11  ',
            'show_answer': True,
            'answer': '3768',
            'caption': 'A shop sells 1,256 red pens.\nBlue pens: 3 times as many.\nStep 1: 1,256×3=3,768 blue pens.\nStep 2: 1,256+3,768=5,024 pens in total.',
            'notes': 'I DO C1 — Lesson 7 C1I2. Two-step. Slide shows Step 1 (×3). Narrate Step 2 (addition) verbally — the LP will require both steps in writing.',
        },
        # ── Cycle 2 I Do 1 — more complex two-step ───────────────────────
        'c2_ido1': {
            'title': 'Two-step — plan before you calculate',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '2135',
            'bottom': '4',
            'carries': '  21 ',
            'show_answer': True,
            'answer': '8540',
            'caption': 'A stadium has 2,135 seats in each tier.\nThere are 4 tiers.\nTotal seats: 2,135×4=8,540.\nIf 975 seats are empty, how many are occupied?\n8,540−975=7,565.',
            'notes': 'I DO C2 — Lesson 7. Model planning both steps (× then −). Ask pupils to predict the second operation before revealing.',
        },
        # c2_ido2 is auto-built from STM JSON
    },
    'wm': {
        # Wednesday → emojis, sz=60, bottom-aligned
        'items': ['🚀', '🌊', '🎯', '🦁', '🍎', '🔑', '⭐'],
        'qa': [
            {'q': 'What is 5 × 12?',                                         'a': '60'},
            {'q': 'What is 9 × 11?',                                         'a': '99'},
            {'q': 'How many cm in 3 m?',                                      'a': '300 cm'},
            {'q': 'Round 4,678 to the nearest hundred.',                      'a': '4,700'},
            {'q': 'What is double 365?',                                      'a': '730'},
        ]
    },
    'rm': {
        'day': 3,
        'questions': [
            {'num':1,'topic':'Place Value','q':'What is the value of 7 in 47,362?','a':'7,000'},
            {'num':2,'topic':'Fractions and Decimals','q':'Order from smallest: 0.5, 3/4, 0.25','a':'0.25, 0.5, 3/4'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 8 × 12?','a':'96'},
            {'num':4,'topic':'Geometry','q':'What is the area of a rectangle 6 cm × 9 cm?','a':'54 cm²'},
            {'num':5,'topic':'Measurement','q':'How many minutes in 2.5 hours?','a':'150 minutes'},
        ]
    },
    'vocab': [
        ('multiply',        'To find the total of equal groups. 4 × 6 means 4 groups of 6, which equals 24.'),
        ('multiple',        'A number in a times table. 24 is a multiple of both 6 and 4.'),
        ('efficient',       'Using the quickest or most straightforward method to get the right answer.'),
        ('approximate',     'A value that is close to the exact answer, often found by rounding before calculating.'),
        ('two-step problem','A problem that needs two separate calculations to find the final answer.'),
    ],
},

# ---------------------------------------------------------------------------
# LESSON 8 — T6W2 Thursday — Multistep × and ÷ problems
# ---------------------------------------------------------------------------
8: {
    'visuals': {
        # ── Cycle 1 I Do 1 — ÷ then − two-step problem ───────────────────
        'c1_ido1': {
            'title': 'Mixed × and ÷ — plan first',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '5640',
            'bottom': '8',
            'carries': '',
            'show_answer': True,
            'answer': '705',
            'caption': '5,640 apples packed into boxes of 8.\nStep 1: 5,640÷8=705 boxes.\nStep 2: 705−3=702 boxes left\n(3 boxes kept for display).\nAnswer: 702 boxes.',
            'notes': 'I DO C1 — Lesson 8. Model a ÷ then − two-step. Stress: identify what you need to find first before calculating anything.',
        },
        # ── Cycle 1 I Do 2 — bar model to plan ───────────────────────────
        'c1_ido2': {
            'title': 'Bar model — plan your steps',
            'slide_type': 'column_calc',
            'calc_type': 'multiplication',
            'top': '1425',
            'bottom': '6',
            'carries': ' 21  ',
            'show_answer': True,
            'answer': '8550',
            'caption': 'A factory makes 1,425 parts each hour for 6 hours. Then 2,340 parts are shipped.\nStep 1: 1,425×6=8,550 parts made.\nStep 2: 8,550−2,340=6,210 parts remaining.',
            'notes': 'I DO C1 I2 — Lesson 8. Draw a bar model on the board before calculating: total bar split into two sections. Pupils sketch bar model first in LP.',
        },
        # ── Cycle 2 I Do 1 — working backwards ───────────────────────────
        'c2_ido1': {
            'title': 'Work backwards — how many in a team?',
            'slide_type': 'column_calc',
            'calc_type': 'division',
            'top': '4250',
            'bottom': '5',
            'carries': '',
            'show_answer': True,
            'answer': '850',
            'caption': '4,250 pupils split into equal teams.\nEach team gets 5 coaches.\n85 coaches altogether.\n85÷5=17 teams.\n4,250÷17=250 pupils per team.\nCheck: 17×250=4,250 ✓',
            'notes': 'I DO C2 — Lesson 8. Work backwards problem. Model two-step: find number of teams first, then size of each team. Slide shows 4,250÷5 as a demonstration — actual problem is more complex, covered in speaker notes.',
        },
        # c2_ido2 is auto-built from STM JSON
    },
    'wm': {
        # Thursday → text+image (sentences with emojis)
        'items': [
            'The 🚀 travels at great speed.',
            'She found a 🔑 under the mat.',
            'He ate 🍎 after school.',
            'The 🦁 roared loudly.',
            'They sailed on the 🌊.',
            'She aimed at the 🎯.',
            'One 🌟 shone above the rest.',
        ],
        'qa': [
            {'q': 'What is 84 ÷ 7?',                                         'a': '12'},
            {'q': 'What is 6 × 9?',                                           'a': '54'},
            {'q': 'A factory makes 1,250 items per day. How many in 5 days?', 'a': '6,250'},
            {'q': 'What is 3,600 ÷ 9?',                                       'a': '400'},
            {'q': 'Double 1,234.',                                             'a': '2,468'},
        ]
    },
    'rm': {
        'day': 4,
        'questions': [
            {'num':1,'topic':'Place Value','q':'What is 10 × 3,456?','a':'34,560'},
            {'num':2,'topic':'Fractions and Decimals','q':'What is half of 3/4?','a':'3/8'},
            {'num':3,'topic':'Multiplication / Division','q':'What is 144 ÷ 12?','a':'12'},
            {'num':4,'topic':'Geometry','q':'How many right angles in a rectangle?','a':'4'},
            {'num':5,'topic':'Measurement','q':'A jug holds 2 litres. How many 250 ml cups can it fill?','a':'8 cups'},
        ]
    },
    'vocab': [
        ('divide',      'To split a number into equal groups. 24 ÷ 6 = 4 means 24 shared equally into 6 groups of 4.'),
        ('quotient',    'The result of a division. In 24 ÷ 6 = 4, the quotient is 4.'),
        ('bar model',   'A diagram using rectangles to represent quantities and show the relationships between them in a problem.'),
        ('reasoning',   'Explaining why an answer is correct using evidence from the calculation or the context of the problem.'),
        ('justify',     'To provide evidence or mathematical argument that proves an answer is correct.'),
    ],
},

}  # end LESSON_DATA
