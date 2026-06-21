#!/usr/bin/env python3
"""Build T6W4 geography lesson slides: L1 Tue 23/6, L2 Wed 24/6, L3 Fri 26/6."""
import json, os, subprocess, sys

SCRIPT   = '/home/claude/build_geo_lesson.py'
BASE     = '/home/claude/writing_lesson_base.pptx'
KC       = '/home/claude/geo_kc.png'
COVER    = '/home/claude/geo_cover.png'
OUT      = '/home/claude'

GEO_PATCHES = {
    'How do writers use dialogue?':
        'Are England and Brazil different?',
    'Write an entertaining story using correct and effective dialogue':
        'Phase 1: Locate and Observe',
    'To Entertain':
        'Being a Geographer',
    'Other Y4 learners':
        'Year 4 Maple',
}

LESSONS = [
    # ── LESSON 1 ─ Tuesday 23 June ───────────────────────────────────
    {
        'lesson': 1,
        'topic':  'Locating_Brazil',
        'slides': [
            {
                'type': 'cover',
                'day':  'Tuesday AM',
                'text_patches': GEO_PATCHES,
            },
            {'type': 'kc'},
            {
                'type': 'lo',
                'wal':  'locate Brazil and four neighbouring countries on a world map and globe',
                'tib':  'geographers must know exactly where a country is before they can understand it',
                'isb':  'annotating a map with Brazil, Ecuador, Chile, Bolivia and Colombia in the correct positions',
            },
            {
                'type':     'you_do',
                'title':    'What do you already know?',
                'lines': [
                    'Cold task — just have a go, no wrong answers.',
                    '',
                    'Jot down anything you already know about Brazil.',
                    '',
                    'Where is it? What is it near?',
                    'What do you know about the climate or landscape?',
                    'Have you heard of any cities, rivers or landmarks?',
                    '',
                    'We will come back to this at the end of the lesson.',
                ],
            },
            {
                'type':  'we_do',
                'title': 'Let\'s find Brazil together.',
                'lines': [
                    'Open your atlases to the world map.',
                    '',
                    'Can you find South America?',
                    'Can you find Brazil within it?',
                    '',
                    'Think about:',
                    '  \u2022  Which hemisphere is Brazil in?',
                    '  \u2022  Does the Equator pass through it?',
                    '  \u2022  Is it north or south of the Tropic of Capricorn?',
                    '',
                    'Share what you find with your partner.',
                ],
            },
            {
                'type':        'i_do',
                'title':       'Latitude, longitude and location',
                'left_label':  'Key vocabulary',
                'left_lines': [
                    'hemisphere',
                    'a half of the Earth',
                    '',
                    'latitude',
                    'distance north or south of the Equator',
                    '',
                    'longitude',
                    'distance east or west of Greenwich',
                    '',
                    'time zone',
                    'a region with the same clock time',
                    '',
                    'GMT',
                    'Greenwich Mean Time \u2014 our starting point',
                ],
                'right_label': 'Brazil\'s location',
                'right_lines': [
                    'Hemisphere: mainly southern',
                    '(small northern tip crosses the Equator)',
                    '',
                    'Approximate latitude:',
                    '5\u00b0 N to 33\u00b0 S',
                    '',
                    'Approximate longitude:',
                    '35\u00b0 W to 74\u00b0 W',
                    '',
                    'Time zone: GMT \u22123',
                    '(Brazil is 3 hours behind England)',
                ],
            },
            {
                'type':  'we_do',
                'title': 'Label South America together.',
                'lines': [
                    'Use your atlas to find and label these countries',
                    'on the South America outline map:',
                    '',
                    '  \u2022  Brazil',
                    '  \u2022  Ecuador',
                    '  \u2022  Chile',
                    '  \u2022  Bolivia',
                    '  \u2022  Colombia',
                    '',
                    'Add the Equator and Tropic of Capricorn.',
                    '',
                    'Which country is to the south of Brazil?',
                    'Which country is to the north-west?',
                ],
            },
            {
                'type':  'you_do',
                'title': 'Write your location description.',
                'lines': [
                    'Use the sentence starters on your learning paper.',
                    '',
                    'Brazil is located in \u2026',
                    'It lies between \u2026',
                    'Its neighbouring countries include \u2026',
                    'The time difference between England and Brazil is \u2026',
                    '',
                    'Include at least THREE words from the vocabulary bank.',
                    '',
                    'Challenge: Can you calculate what time it is in Brazil',
                    'right now?',
                ],
                'challenge': 'use all five key vocabulary words in your description',
            },
            {
                'type': 'learning_review',
                'q1':   'Which geographical vocabulary word felt trickiest to use?',
                'q2':   'Why do geographers need to know a country\'s hemisphere and time zone?',
                'q3':   'How has your knowledge of Brazil changed since the start of the lesson?',
            },
        ],
    },

    # ── LESSON 2 ─ Wednesday 24 June ─────────────────────────────────
    {
        'lesson': 2,
        'topic':  'Brazil_Physical_Geography',
        'slides': [
            {
                'type': 'cover',
                'day':  'Wednesday AM',
                'text_patches': GEO_PATCHES,
            },
            {'type': 'kc'},
            {
                'type': 'lo',
                'wal':  'describe the biomes and climate zone of Brazil',
                'tib':  'physical geography shapes what a country looks and feels like — it is essential for any comparison',
                'isb':  'writing a paragraph about Brazil\'s physical geography using at least three vocabulary words',
            },
            {
                'type':     'warmup',
                'title':    'Geographer\'s Starter',
                'subtitle': 'Recall from Tuesday — how much do you remember?',
                'cards': [
                    {
                        'label': 'Question 1',
                        'lines': [
                            'Which hemisphere is most of Brazil in?',
                            '',
                            'a)  Northern hemisphere',
                            'b)  Southern hemisphere',
                            'c)  Eastern hemisphere',
                        ],
                    },
                    {
                        'label': 'Question 2',
                        'lines': [
                            'Name TWO countries that border Brazil.',
                            '',
                            '1. ___________________________',
                            '',
                            '2. ___________________________',
                        ],
                    },
                    {
                        'label': 'Question 3',
                        'lines': [
                            'Brazil is GMT\u22123.',
                            '',
                            'If it is 9am in Bristol,',
                            'what time is it in Brazil?',
                            '',
                            'Answer: _______________',
                        ],
                    },
                ],
            },
            {
                'type':  'i_do',
                'title': 'What is a biome?',
                'left_label':  'Three biomes of Brazil',
                'left_lines': [
                    'Tropical Rainforest',
                    'Dense forest, very high rainfall,',
                    'home to extraordinary biodiversity.',
                    '',
                    'Desert',
                    'Dry, low rainfall \u2014 found in',
                    'parts of north-east Brazil.',
                    '',
                    'Tundra',
                    'Cold, sparse vegetation \u2014 found',
                    'at high altitudes in the Andes',
                    'region bordering Brazil.',
                ],
                'right_label': 'Climate zone',
                'right_lines': [
                    'Brazil is mainly in the',
                    'TROPICAL climate zone.',
                    '',
                    'The tropical zone lies between',
                    'the Tropic of Cancer and',
                    'Tropic of Capricorn.',
                    '',
                    'It experiences:',
                    '  \u2022  High temperatures year round',
                    '  \u2022  High levels of cloud cover',
                    '  \u2022  Heavy rainfall',
                    '',
                    'Seasons are WET and DRY,',
                    'not spring/summer/autumn/winter.',
                ],
            },
            {
                'type':  'we_do',
                'title': 'Which biome is which?',
                'lines': [
                    'Look at the photograph cards on your table.',
                    '',
                    'Sort them into three groups:',
                    '  \u2022  Tropical Rainforest',
                    '  \u2022  Desert',
                    '  \u2022  Tundra',
                    '',
                    'For each group, agree one thing you can SEE',
                    'that tells you which biome it is.',
                    '',
                    'Which biome takes up the most of Brazil?',
                ],
            },
            {
                'type':  'i_do',
                'title': 'A common misconception about rainforests',
                'left_label':  'What most people think',
                'left_lines': [
                    '"The rainforest is so lush and',
                    'green \u2014 the soil must be',
                    'incredibly fertile."',
                    '',
                    'It looks like it should be',
                    'the best farmland in the world.',
                    '',
                    'So when rainforest is cleared',
                    'for farming, it should produce',
                    'huge harvests\u2026',
                    '',
                    '\u2026 right?',
                ],
                'right_label': 'What geographers know',
                'right_lines': [
                    'WRONG.',
                    '',
                    'The nutrients in the rainforest',
                    'are held in the VEGETATION,',
                    'not in the soil.',
                    '',
                    'When the trees are removed,',
                    'the soil quickly loses its',
                    'nutrients and becomes poor.',
                    '',
                    'This is why cleared rainforest',
                    'land is often not productive',
                    'for more than a few years.',
                ],
            },
            {
                'type':  'we_do',
                'title': 'Vegetation in Brazil is complex.',
                'lines': [
                    'Brazil\'s vegetation belt is not simple.',
                    '',
                    'Because the physical geography varies so much,',
                    'it includes some unusual plant communities:',
                    '',
                    'Lomas:',
                    'Flowering plants and grasses that grow',
                    'in desert areas using coastal fog for moisture.',
                    '',
                    'High altitude vegetation:',
                    'Found in the Andes \u2014 low-growing plants adapted',
                    'to cold, thin air and strong winds.',
                    '',
                    'Why do you think the vegetation is so varied?',
                ],
            },
            {
                'type':  'you_do',
                'title': 'Write your Brazil physical geography paragraph.',
                'lines': [
                    'Use the paragraph frame on your learning paper.',
                    '',
                    'Include:',
                    '  \u2022  The climate zone Brazil is in',
                    '  \u2022  The three main biomes',
                    '  \u2022  One sentence about the misconception',
                    '  \u2022  At least three vocabulary words',
                    '',
                    'Use your word and phrase bank to help.',
                ],
                'challenge': 'explain why the vegetation belt in Brazil is complex, using two specific examples',
            },
            {
                'type': 'learning_review',
                'q1':   'Which biome did you find most surprising or interesting?',
                'q2':   'Why is it a misconception to think rainforest soil is very fertile?',
                'q3':   'How does knowing about biomes help us compare England and Brazil?',
            },
        ],
    },

    # ── LESSON 3 ─ Friday 26 June ────────────────────────────────────
    {
        'lesson': 3,
        'topic':  'England_Physical_Geography',
        'slides': [
            {
                'type': 'cover',
                'day':  'Friday AM',
                'text_patches': GEO_PATCHES,
            },
            {'type': 'kc'},
            {
                'type': 'lo',
                'wal':  'describe England\'s physical geography and begin comparing it with Brazil',
                'tib':  'a fair comparison needs us to know both sides equally well',
                'isb':  'completing the physical geography comparison frame with at least three features for each country',
            },
            {
                'type':     'warmup',
                'title':    'Geographer\'s Starter',
                'subtitle': 'Brazil recap \u2014 what do you remember?',
                'cards': [
                    {
                        'label': 'Recall 1',
                        'lines': [
                            'Name the THREE biomes',
                            'found in Brazil.',
                            '',
                            '1. ____________________',
                            '2. ____________________',
                            '3. ____________________',
                        ],
                    },
                    {
                        'label': 'Recall 2',
                        'lines': [
                            'Which climate zone is',
                            'Brazil mainly in?',
                            '',
                            'Answer: _______________',
                            '',
                            'What does this mean for',
                            'Brazil\'s seasons?',
                        ],
                    },
                    {
                        'label': 'Challenge',
                        'lines': [
                            'Correct the misconception:',
                            '',
                            '"The soil in the',
                            'rainforest is very fertile."',
                            '',
                            'Why is this wrong?',
                        ],
                    },
                ],
            },
            {
                'type':  'we_do',
                'title': 'What do we know about England\'s physical geography?',
                'lines': [
                    'Think about where you live.',
                    '',
                    '  \u2022  What is the weather like here?',
                    '  \u2022  What types of landscape can you think of in England?',
                    '  \u2022  Have you visited any different parts of England?',
                    '',
                    'Discuss with your partner for 2 minutes.',
                    '',
                    'Which words would you use to describe England\'s physical geography?',
                ],
            },
            {
                'type':        'i_do',
                'title':       'England\'s physical geography',
                'left_label':  'Biome and climate',
                'left_lines': [
                    'Biome: Temperate',
                    '',
                    'England\'s temperate biome means:',
                    '  \u2022  Mild temperatures',
                    '  \u2022  Four distinct seasons',
                    '  \u2022  Reliable rainfall throughout',
                    '     the year',
                    '  \u2022  Mixed woodland and grassland',
                    '',
                    'Climate zone: Temperate Maritime',
                    'Influenced by the Atlantic Ocean',
                    '\u2014 keeps temperatures moderate.',
                ],
                'right_label': 'Topography',
                'right_lines': [
                    'England has varied topography:',
                    '',
                    'Coastal:',
                    'White Cliffs of Dover,',
                    'Jurassic Coast, beaches.',
                    '',
                    'Highland:',
                    'Lake District, Peak District,',
                    'Yorkshire Dales.',
                    '',
                    'River valleys:',
                    'Thames, Severn, Trent.',
                    '',
                    'Flatlands:',
                    'East Anglia, Somerset Levels.',
                ],
            },
            {
                'type':  'we_do',
                'title': 'Let\'s build the comparison frame together.',
                'lines': [
                    'We\'ll complete the ENGLAND column together.',
                    '',
                    'Comparison frame: Physical Geography',
                    '',
                    'Feature     |  England  |  Brazil',
                    '\u2500' * 38,
                    'Biome       |           |  Tropical RF / Desert / Tundra',
                    'Climate     |           |  Tropical',
                    'Topography  |           |  Coastal / Highland / Rainforest',
                    '',
                    'What goes in the England column?',
                ],
            },
            {
                'type':  'you_do',
                'title': 'Complete your comparison frame.',
                'lines': [
                    'Finish the comparison frame on your learning paper.',
                    '',
                    'Then write your summary sentence:',
                    '',
                    '"England and Brazil are similar in that\u2026',
                    'but they are different because\u2026"',
                    '',
                    'Which country do you think has more interesting',
                    'physical geography for a visitor? Why?',
                ],
                'challenge': 'write TWO comparison sentences and explain which physical difference would matter most to a tourist',
            },
            {
                'type': 'learning_review',
                'q1':   'Which physical feature of England surprised you most?',
                'q2':   'How does England\'s temperate climate compare to Brazil\'s tropical climate?',
                'q3':   'Which country\'s physical geography would you find more interesting to visit?',
            },
        ],
    },
]

for lesson_data in LESSONS:
    n     = lesson_data['lesson']
    topic = lesson_data['topic']
    slides_path = f'/home/claude/geo_slides_L{n}.json'

    with open(slides_path, 'w') as f:
        json.dump(lesson_data['slides'], f, indent=2, ensure_ascii=False)

    cmd = [
        'python3', SCRIPT,
        '--base',        BASE,
        '--kc',          KC,
        '--cover',       COVER,
        '--term',        '6',
        '--week',        '4',
        '--lesson',      str(n),
        '--topic',       topic,
        '--out',         OUT,
        '--slides-json', slides_path,
    ]
    print(f'\n=== Building Lesson {n} ({topic}) ===')
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print('STDERR:', result.stderr[:500])
    if result.returncode != 0:
        print(f'ERROR: exit code {result.returncode}')
        sys.exit(1)

print('\nAll lessons built successfully.')
