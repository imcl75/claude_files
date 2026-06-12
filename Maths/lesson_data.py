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


    9: {
        'visuals': {
            'c1_ido1': {
                'title': 'What does × mean?',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '6',
                'bottom': '4',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': 'There are 6 bags.\nEach bag holds 4 oranges.\nHow many oranges altogether?\n\nSignal word: "each" → equal groups → ×',
                'notes': 'I DO C1 — Model each operation in turn: ×, ÷, +, −. Use tiny numbers so the operation is the focus, not the arithmetic.',
            },
            'c1_ido2': {
                'title': 'Finding the signal word',
                'slide_type': 'column_calc',
                'calc_type': 'division',
                'top': '30',
                'bottom': '5',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '30 stickers shared equally\nbetween 5 friends.\nHow many does each get?\n\nSignal: "shared equally" → ÷\nCircle the signal word before calculating.',
                'notes': 'I DO C1 I2 — Model circling the signal word on the board. Show that identifying the operation happens BEFORE writing the calculation.',
            },
            'c2_ido1': {
                'title': 'What if there is no signal word?',
                'slide_type': 'column_calc',
                'calc_type': 'division',
                'top': '48',
                'bottom': '6',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': 'I packed 48 eggs into boxes.\nEach box holds 6 eggs.\nHow many boxes did I fill?\n\nNo "share" word — but structure shows\nhow many groups of 6 in 48? → ÷',
                'notes': 'I DO C2 — Show that structure, not just vocabulary, signals the operation. Ask: what do I know? What am I finding? That reveals the operation.',
            },
        },
        'wm': {
            'items': [8, 24, 56, 12, 48, 36, 64],
            'qa': [
                {'q': 'What was the 3rd number?',        'a': '56'},
                {'q': 'What was the first number?',      'a': '8'},
                {'q': 'Which number came after 56?',     'a': '12'},
                {'q': 'What was the 5th number?',        'a': '48'},
                {'q': 'How many numbers were there?',    'a': '7'},
            ],
        },
        'rm': {
            'day': 1,
            'questions': [
                {'num': 1, 'topic': 'Place Value',    'q': 'What is the value of 4 in 84,362?',          'a': '4,000'},
                {'num': 2, 'topic': 'Fractions',      'q': 'What is 1/4 of 48?',                         'a': '12'},
                {'num': 3, 'topic': 'Multiplication', 'q': '7 × 9 = ?',                                  'a': '63'},
                {'num': 4, 'topic': 'Geometry',       'q': 'How many sides does a hexagon have?',        'a': '6'},
                {'num': 5, 'topic': 'Measurement',    'q': 'How many cm in 1.5 m?',                      'a': '150 cm'},
            ],
        },
        'vocab': [
            ['operation',    'A mathematical process: add, subtract, multiply or divide.'],
            ['signal word',  'A word in a problem that tells you which operation to use.'],
            ['groups of',    'Equal groups — a signal that multiplication is needed.'],
            ['share equally','Splitting into equal parts — a signal that division is needed.'],
            ['altogether',   'All amounts combined — a signal that addition is needed.'],
        ],
    },

    10: {
        'visuals': {
            'c1_ido1': {
                'title': 'The two-step routine: identify then calculate',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '32',
                'bottom': '4',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': 'There are 32 marbles in a bag.\nI have 4 bags.\nHow many marbles altogether?\n\nStep 1: "equal groups" → ×\nStep 2: 32 × 4 =',
                'notes': 'I DO C1 — Use a problem from Monday\'s sorted set. Model the two-step routine explicitly: identify and justify BEFORE writing the calculation.',
            },
            'c1_ido2': {
                'title': 'Division: identify then calculate',
                'slide_type': 'column_calc',
                'calc_type': 'division',
                'top': '96',
                'bottom': '3',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '96 apples packed equally\ninto 3 crates.\nHow many per crate?\n\nStep 1: "equally" → ÷\nStep 2: 96 ÷ 3 =',
                'notes': 'I DO C1 I2 — Same routine, different operation. Stress that Step 1 (identify) always comes before Step 2 (calculate).',
            },
            'c2_ido1': {
                'title': 'Same routine: addition and subtraction',
                'slide_type': 'column_calc',
                'calc_type': 'addition',
                'top': '47',
                'bottom': '35',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': 'There are 47 red beads\nand 35 blue beads.\nHow many beads altogether?\n\nStep 1: "altogether" → +\nStep 2: 47 + 35 =',
                'notes': 'I DO C2 — Show that the same two-step routine works for all four operations. Model + then introduce a − example verbally.',
            },
        },
        'wm': {
            'items': ['share', 'multiply', 'total', 'groups', 'equal', 'divide', 'steps'],
            'qa': [
                {'q': 'What was the 3rd word?',              'a': 'total'},
                {'q': 'What was the first word?',            'a': 'share'},
                {'q': 'Which word came after "total"?',      'a': 'groups'},
                {'q': 'What was the 6th word?',              'a': 'divide'},
                {'q': 'How many words were there?',          'a': '7'},
            ],
        },
        'rm': {
            'day': 2,
            'questions': [
                {'num': 1, 'topic': 'Place Value',  'q': 'Round 7,841 to the nearest 1,000',         'a': '8,000'},
                {'num': 2, 'topic': 'Fractions',    'q': 'Which is greater: 2/3 or 3/4?',             'a': '3/4'},
                {'num': 3, 'topic': 'Division',     'q': '56 ÷ 7 = ?',                               'a': '8'},
                {'num': 4, 'topic': 'Geometry',     'q': 'Perimeter of a square with sides 8 cm?',   'a': '32 cm'},
                {'num': 5, 'topic': 'Measurement',  'q': 'How many ml in 3.5 litres?',               'a': '3,500 ml'},
            ],
        },
        'vocab': [
            ['identify',          'To name or recognise which operation a problem needs.'],
            ['estimate',          'A sensible approximation before calculating.'],
            ['regroup',           'To exchange 10 ones for 1 ten (or 10 tens for 1 hundred) during a calculation.'],
            ['two-step routine',  'Step 1: identify the operation. Step 2: calculate.'],
            ['short multiplication', 'A compact written method for multiplying by a 1-digit number.'],
        ],
    },

    11: {
        'visuals': {
            'c1_ido1': {
                'title': 'Bar model: making steps visible',
                'slide_type': 'column_calc',
                'calc_type': 'division',
                'top': '36',
                'bottom': '6',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '36 children split into groups of 6.\nEach group plants 4 seeds.\nStep 1: 36 ÷ 6 = groups\nStep 2: groups × 4 = seeds total\n\nDraw the bar model BEFORE calculating.',
                'notes': 'I DO C1 — Draw bar model on board first: top bar = 36, split into 6 equal sections. Label Step 1. Then show where Step 2 connects. Only calculate once both steps are labelled.',
            },
            'c1_ido2': {
                'title': 'Label before you calculate',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '5',
                'bottom': '8',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '5 bags each have 8 counters.\nThen 4 counters are removed\nfrom each bag.\nStep 1: 5 × 8 = total counters\nStep 2: total − 4 = ?',
                'notes': 'I DO C1 I2 — Model labelling both steps on the bar model before touching the calculation. Ask: "Which step must happen first? Why?"',
            },
            'c2_ido1': {
                'title': 'Two routes — which is more efficient?',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '5',
                'bottom': '8',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '5 children each have 8 counters.\nThey share all counters among 4 tables.\nRoute A: (5 × 8) ÷ 4\nRoute B: 5 × (8 ÷ 4)\n\nBoth give 10. Which is simpler?',
                'notes': 'I DO C2 — Work through both routes. Show that for this problem, Route B (8÷4=2 first, then ×5=10) is simpler. Establish: some problems have fixed order, some are flexible.',
            },
        },
        'wm': {
            'items': ['🌟', '🎯', '🦋', '🍕', '🎪', '🦁', '🌈'],
            'qa': [
                {'q': 'What was the 3rd emoji?',               'a': '🦋'},
                {'q': 'What was the first emoji?',             'a': '🌟'},
                {'q': 'Which emoji came after the butterfly?', 'a': '🍕'},
                {'q': 'What was the 5th emoji?',               'a': '🎪'},
                {'q': 'How many emojis were there?',           'a': '7'},
            ],
        },
        'rm': {
            'day': 3,
            'questions': [
                {'num': 1, 'topic': 'Place Value',    'q': 'Write 30,500 in words',                   'a': 'thirty thousand five hundred'},
                {'num': 2, 'topic': 'Fractions',      'q': 'What is 3/5 of 40?',                      'a': '24'},
                {'num': 3, 'topic': 'Multiplication', 'q': '11 × 12 = ?',                             'a': '132'},
                {'num': 4, 'topic': 'Geometry',       'q': 'What type of angle is 120°?',             'a': 'obtuse'},
                {'num': 5, 'topic': 'Measurement',    'q': 'How many grams in 2.25 kg?',              'a': '2,250 g'},
            ],
        },
        'vocab': [
            ['two-step',  'A problem that needs two separate calculations to find the answer.'],
            ['bar model', 'A diagram using rectangles to show what a problem is asking.'],
            ['plan',      'To decide the steps needed before you start calculating.'],
            ['justify',   'To explain why your answer is correct using evidence.'],
            ['efficient', 'Finding the answer using the fewest and simplest steps.'],
        ],
    },

    12: {
        'visuals': {
            'c1_ido1': {
                'title': 'Money: identify then calculate',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '35',
                'bottom': '4',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': 'Each pen costs 35p.\nI buy 4 pens.\nHow much do I spend?\n\nStep 1: "each" → ×\nStep 2: 35 × 4 = ___ p',
                'notes': 'I DO C1 — Model money problem with tiny amounts. Emphasise: same two-step routine, same process. Remind: units go in the answer.',
            },
            'c1_ido2': {
                'title': 'Two-step money problem',
                'slide_type': 'column_calc',
                'calc_type': 'multiplication',
                'top': '25',
                'bottom': '6',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '6 stickers cost 25p each.\nI pay with £2 (= 200p).\nStep 1: 25 × 6 = total cost\nStep 2: 200 − total = change\n\nBar model before calculating.',
                'notes': 'I DO C1 I2 — Two-step money. Draw bar model. Show unit conversion (£2 → 200p) as a key step before calculating.',
            },
            'c2_ido1': {
                'title': 'Measurement: same routine',
                'slide_type': 'column_calc',
                'calc_type': 'division',
                'top': '240',
                'bottom': '6',
                'regroups': '',
                'show_answer': False,
                'answer': '',
                'caption': '240 g of rice shared equally\ninto 6 portions.\nHow many grams each?\n\nStep 1: "shared equally" → ÷\nStep 2: 240 ÷ 6 = ___ g',
                'notes': 'I DO C2 — Same identify-then-calculate routine, measurement context. Emphasise: the operation does not change because the context is different. Unit must be included in the answer.',
            },
        },
        'wm': {
            'items': [
                'The 🌟 shone in the dark sky.',
                'She found a 🎯 in the garden.',
                'He counted 🦋 on the bush.',
                'They shared the 🍕 at the party.',
                'The 🎪 opened on a hot day.',
                'A 🦁 walked across the path.',
                'The 🌈 appeared after the rain.',
            ],
            'qa': [
                {'q': 'What shone in the dark sky?',               'a': 'A star 🌟'},
                {'q': 'What did she find in the garden?',          'a': 'A target 🎯'},
                {'q': 'What did they share at the party?',         'a': 'A pizza 🍕'},
                {'q': 'What appeared after the rain?',             'a': 'A rainbow 🌈'},
                {'q': 'What sentence mentioned the big top?',      'a': 'The 🎪 opened on a hot day.'},
            ],
        },
        'rm': {
            'day': 4,
            'questions': [
                {'num': 1, 'topic': 'Place Value',  'q': 'What is 100 × 349?',                              'a': '34,900'},
                {'num': 2, 'topic': 'Fractions',    'q': 'Order from largest: 1/2, 3/8, 5/6',              'a': '5/6, 1/2, 3/8'},
                {'num': 3, 'topic': 'Division',     'q': '108 ÷ 9 = ?',                                    'a': '12'},
                {'num': 4, 'topic': 'Geometry',     'q': 'Area of a rectangle 7 cm × 8 cm?',               'a': '56 cm²'},
                {'num': 5, 'topic': 'Measurement',  'q': 'How many minutes in 3/4 of an hour?',            'a': '45 minutes'},
            ],
        },
        'vocab': [
            ['pence',   'The smaller unit of British money. 100 pence = £1.'],
            ['change',  'The money you get back when you pay more than something costs.'],
            ['total',   'The complete amount after adding everything together.'],
            ['mass',    'How heavy something is, measured in grams or kilograms.'],
            ['unit',    'The standard measurement for an answer: cm, g, p, etc.'],
        ],
    },
}  # end LESSON_DATA
