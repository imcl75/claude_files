# lesson_data.py — T6W4 L13  Monday — Mixed numbers and improper fractions
# Type B: book-based LP (pupils write calculations in maths books)

LESSON_DATA = {
    13: {
        'vocab': [
            {'word': 'mixed number',      'def': 'A number with a whole part and a fraction part, e.g. 2 and 3/4'},
            {'word': 'improper fraction', 'def': 'A fraction where the numerator is greater than the denominator, e.g. 11/4'},
            {'word': 'numerator',         'def': 'The top number in a fraction — how many parts we have'},
            {'word': 'denominator',       'def': 'The bottom number in a fraction — how many equal parts in one whole'},
            {'word': 'convert',           'def': 'Change from one form to another without changing the value'},
        ],
        'wm': {
            'type': 'numbers',
            'items': [3, 7, 11, 24, 5, 13, 2, 9],
            'qa': [
                {'q': 'Double 11',                         'a': '22'},
                {'q': '24 ÷ 4',                            'a': '6'},
                {'q': 'How many halves in 3 wholes?',      'a': '6'},
                {'q': 'How many thirds in 2 wholes?',      'a': '6'},
                {'q': '5 × 3 + 2 = ?',                    'a': '17'},
            ],
        },
        'rm': {
            'day': 1,
            'questions': [
                {'num':1,'topic':'Times tables',  'q':'8 × 7 = ?',                         'a':'56'},
                {'num':2,'topic':'Division',       'q':'13 ÷ 4 = ? remainder ?',            'a':'3 remainder 1'},
                {'num':3,'topic':'Fractions',      'q':'1/4 of 36 = ?',                     'a':'9'},
                {'num':4,'topic':'Fractions',      'q':'How many quarters in 3 wholes?',    'a':'12'},
                {'num':5,'topic':'Mental addition','q':'148 + 37 = ?',                      'a':'185'},
            ],
        },
        'visuals': {

            # ── Cycle 1 I Do 1 ────────────────────────────────────────────────
            # Mixed numbers → improper fractions
            # I Do: 2¾ shown as 3 circles (4/4, 4/4, 3/4) = 11 quarters
            # We Do: 1⅔ shown as 2 circles (3/3, 2/3) = 5 thirds
            'c1_ido1': {
                'slide_type': 'visual_teach',
                'title': 'Mixed numbers → improper fractions',
                'visual': {
                    'type': 'fraction_circles',
                    'denominator': 4,
                    'total': 11,
                    'color': '#2565AE',
                    'total_label': '= 11 quarters',
                },
                'caption': '2 wholes and 3 quarters — how many quarters altogether?',
                'talk': [
                    'How many quarters in each complete circle?',
                    '2 × 4 = 8 quarters in the two full circles',
                    '8 + 3 more quarters = 11 quarters total',
                ],
                'we_do': {
                    'visual': {
                        'type': 'fraction_circles',
                        'denominator': 3,
                        'total': 5,
                        'color': '#C83030',
                        'total_label': '= ? thirds',
                    },
                    'text': 'How many thirds altogether? Write as an improper fraction.',
                },
                'notes': (
                    'I Do: 2¾ → 2×4+3 = 11, so 11/4.\n'
                    'Show each step clearly: count 4+4=8 in the full circles, then add 3 = 11.\n'
                    'We Do: 1⅔ → 1×3+2=5, so 5/3. The circles show 3+2=5 thirds.'
                ),
            },

            # ── Cycle 1 I Do 2 ────────────────────────────────────────────────
            # visual_stm: 3½ → wrong answer 4/2 (added instead of multiplied)
            # Left panel: fraction circles showing 7 halves (the CORRECT amount)
            # Pupils see 7 halves, then discuss why 4/2 is wrong
            'c1_ido2': {
                'slide_type': 'visual_stm',
                'title': 'Spot the mistake',
                'visual': {
                    'type': 'fraction_circles',
                    'denominator': 2,
                    'total': 7,
                    'color': '#2E8B3A',
                    'total_label': '= 7 halves',
                },
                'error_instruction': (
                    'Convert 3½ to an improper fraction.\n'
                    'A pupil writes:  3 + 1 = 4,  so the answer is 4/2.\n'
                    'Can you see what went wrong?'
                ),
                'error_correction': {
                    'text': (
                        '4/2 is wrong — the pupil added the whole number to the numerator.\n\n'
                        'Correct: 3 × 2 + 1 = 7, so 3½ = 7/2.\n\n'
                        'The circles show 7 halves — not 4.'
                    ),
                },
                'notes': (
                    'Common error: pupil treats 3+1=4 (adds whole + numerator) rather than 3×2+1=7.\n'
                    'The circles make the error visible — there are clearly 7 half-circles (3 full + 1 half),\n'
                    'not 4. Let pupils count the halves before revealing the correction.'
                ),
            },

            # ── Cycle 2 I Do 1 ────────────────────────────────────────────────
            # Improper fractions → mixed numbers
            # I Do: 17/5 shown as 4 circles (5/5, 5/5, 5/5, 2/5) = 3 wholes rem 2
            # We Do: 11/3 shown as circles (3/3, 3/3, 3/3, 2/3) = 3 rem 2 → 3⅔
            'c2_ido1': {
                'slide_type': 'visual_teach',
                'title': 'Improper fractions → mixed numbers',
                'visual': {
                    'type': 'fraction_circles',
                    'denominator': 5,
                    'total': 17,
                    'color': '#D4A800',
                    'total_label': '= 3 wholes and 2/5',
                },
                'caption': '17 fifths — count the complete circles, then count what is left.',
                'talk': [
                    'How many complete circles of 5 can you see?',
                    '17 ÷ 5 = 3 remainder 2',
                    '3 complete circles + 2 fifths left = 3 and 2/5',
                ],
                'we_do': {
                    'visual': {
                        'type': 'fraction_circles',
                        'denominator': 3,
                        'total': 11,
                        'color': '#C83030',
                        'total_label': '= ? wholes and ?/3',
                    },
                    'text': 'Count the complete circles. How many thirds are left? Write as a mixed number.',
                },
                'notes': (
                    'I Do: 17/5 → 17÷5 = 3 rem 2 → 3⅖.\n'
                    'Link division to the visual: count full circles (wholes), then count remaining shaded parts.\n'
                    'We Do: 11/3 → 11÷3 = 3 rem 2 → 3⅔. Pupils count 3 full circles + 2 thirds remaining.'
                ),
            },

            # ── Cycle 2 I Do 2 ────────────────────────────────────────────────
            # visual_stm: 13/4 → forgot the remainder, writes just 3 (or 3/0)
            'c2_ido2': {
                'slide_type': 'visual_stm',
                'title': 'Spot the mistake',
                'visual': {
                    'type': 'fraction_circles',
                    'denominator': 4,
                    'total': 13,
                    'color': '#2565AE',
                    'total_label': '= 3 wholes and ?',
                },
                'error_instruction': (
                    'Convert 13/4 to a mixed number.\n'
                    'A pupil writes:  13 ÷ 4 = 3,  so the answer is 3.\n'
                    'What has the pupil forgotten?'
                ),
                'error_correction': {
                    'text': (
                        'The pupil forgot the remainder!\n\n'
                        '13 ÷ 4 = 3 remainder 1,  so 13/4 = 3 and 1/4.\n\n'
                        'The circles show 3 full circles and 1 quarter left over — not just 3 wholes.'
                    ),
                },
                'notes': (
                    'Common error: 13÷4=3 (correct whole number) but pupil forgets the remainder.\n'
                    'The circles make the leftover visible — pupils can count 3 full + 1 quarter.\n'
                    'Reinforce: always check for a remainder and write it as the numerator.'
                ),
            },

        },
    },
}
