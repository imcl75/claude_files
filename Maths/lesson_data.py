# lesson_data.py — T6W4 L13  Monday — Mixed numbers and improper fractions
# Production lesson data

LESSON_DATA = {
    13: {
        'vocab': [
            {'word': 'mixed number',      'def': 'A number with a whole part and a fraction part, e.g. 2 and 3/4'},
            {'word': 'improper fraction', 'def': 'A fraction where the numerator is greater than the denominator, e.g. 11/4'},
            {'word': 'numerator',         'def': 'The top number in a fraction'},
            {'word': 'denominator',       'def': 'The bottom number — how many equal parts in one whole'},
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

            # ── C1 I Do 1 ─────────────────────────────────────────────────────
            # I Do: fraction_circles showing 2¾ = 11 quarters
            # We Do: equivalence_bars showing 1⅔ as bars (different representation)
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
                    '8 + 3 more quarters = 11 quarters altogether',
                ],
                'we_do': {
                    # Different representation: equivalence bars instead of circles
                    # Shows 1⅔ as two horizontal bars (3/3 full, 2/3 partial)
                    'visual': {
                        'type': 'equivalence_bars',
                        'fractions': [[3, 3], [2, 3]],
                        'color': '#C83030',
                    },
                    'text': 'How many thirds altogether? Write as an improper fraction.',
                },
                'notes': (
                    'I Do: 2¾ → 2×4+3 = 11, so 11/4. Circles show quarters clearly.\n'
                    'We Do: 1⅔ shown as BARS (different representation). 3+2=5 thirds, so 5/3.\n'
                    'Using bars and circles on the same slide shows the idea is general,\n'
                    'not specific to one shape.'
                ),
            },

            # ── C1 I Do 2 ─────────────────────────────────────────────────────
            # STM: 3½ → wrong answer 4/2 (added instead of multiplied)
            # Fraction circles show 7 halves — pupils count 7, not 4
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
                    'Count the circles. Is that right?'
                ),
                'error_correction': {
                    'text': (
                        '4/2 is wrong — the pupil added whole + numerator.\n\n'
                        'Correct: 3 × 2 + 1 = 7, so 3½ = 7/2.\n\n'
                        'The circles prove it — count 7 halves, not 4.'
                    ),
                },
                'notes': 'Pupils count the circles BEFORE the correction appears — they can see 7, not 4.',
            },

            # ── C2 I Do 1 ─────────────────────────────────────────────────────
            # I Do: fraction_circles showing 17/5 grouped as wholes
            # We Do: number line from 0–4 showing 11/3 — different representation
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
                'caption': '17 fifths — count complete circles, then what is left over.',
                'talk': [
                    'How many complete circles of 5 can you see?',
                    '17 ÷ 5 = 3 remainder 2',
                    '3 complete circles + 2 fifths left = 3 and 2/5',
                ],
                'we_do': {
                    # Different representation: number line shows 11/3 as jumps on a scale
                    # Pupils count 3 complete groups (0→3) then 2 extra thirds
                    'visual': {
                        'type': 'fraction_number_line',
                        'start': 0,
                        'end': 4,
                        'denominator': 3,
                        'markers': [
                            {'value': 11/3, 'label': '11/3', 'color': '#C83030'},
                        ],
                    },
                    'text': 'How many whole numbers fit in 11/3? How many thirds left over?',
                },
                'notes': (
                    'I Do: circles make the groups visual. Count 3 full circles (3 wholes) + 2 fifths.\n'
                    'We Do: number line shows 11/3 on a scale 0–4. Pupils count groups of 3 (0,3,6,9...)\n'
                    'and see 11 lands between 3 and 4: so 3 full wholes and 2/3 leftover.\n'
                    'The different representation reinforces that the METHOD (find wholes + remainder)\n'
                    'works regardless of how you picture the fractions.'
                ),
            },

            # ── C2 I Do 2 ─────────────────────────────────────────────────────
            # STM: 13/4 → forgot the remainder (writes just 3)
            # Circles clearly show the leftover quarter
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
                    'What has been forgotten?'
                ),
                'error_correction': {
                    'text': (
                        'The remainder was forgotten!\n\n'
                        '13 ÷ 4 = 3 remainder 1,  so 13/4 = 3 and 1/4.\n\n'
                        'The circles show 3 full circles AND 1 quarter left — not just 3.'
                    ),
                },
                'notes': 'The leftover quarter is visible in the 4th circle before correction appears.',
            },

        },
    },
}
