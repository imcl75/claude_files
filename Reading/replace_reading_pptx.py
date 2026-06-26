"""
T5W2 PPTX builder — replaces T5W1 content in freshly unpacked XML.
Works directly with raw XML strings matching the file encoding exactly.
"""
import sys, re, html
sys.path.insert(0, '/home/claude')
from t5w2_content import *

UNPACKED = '/home/claude/t5w2_unpacked/ppt/slides'


def read_slide(n):
    with open(f'{UNPACKED}/slide{n}.xml', encoding='utf-8') as f:
        return f.read()


def write_slide(n, xml):
    with open(f'{UNPACKED}/slide{n}.xml', 'w', encoding='utf-8') as f:
        f.write(xml)


def to_xml(text):
    """Encode plain unicode to XML matching PPTX file style.
    Em dashes stay as literal unicode; curly quotes/apostrophes become entities."""
    return (text
            .replace('&', '&amp;')
            .replace('\u201c', '&#x201C;')
            .replace('\u201d', '&#x201D;')
            .replace('\u2018', '&#x2018;')
            .replace('\u2019', '&#x2019;'))

def replace_vocab_word(xml, old_word, new_word):
    """Replace vocab word by matching the exact <a:t> tag content — avoids substring collisions."""
    old_tag = f'<a:t>{to_xml(old_word)}</a:t>'
    new_tag = f'<a:t>{to_xml(new_word)}</a:t>'
    if old_tag in xml:
        return xml.replace(old_tag, new_tag, 1)
    print(f'  WARNING vocab word not found: {old_word!r}')
    return xml

def replace_vocab_defn(xml, old_defn, new_defn):
    """Replace vocab definition by exact <a:t> tag content."""
    old_tag = f'<a:t>{to_xml(old_defn)}</a:t>'
    new_tag = f'<a:t>{to_xml(new_defn)}</a:t>'
    if old_tag in xml:
        return xml.replace(old_tag, new_tag, 1)
    print(f'  WARNING vocab defn not found: {old_defn[:40]!r}')
    return xml




def get_run_text(xml, search_start=''):
    """Extract the text inside the <a:t> tag that contains search_start."""
    idx = xml.find(search_start)
    if idx == -1:
        return None
    # Find the opening <a:t> before this position
    t_start = xml.rfind('<a:t>', 0, idx)
    t_end = xml.find('</a:t>', idx)
    if t_start == -1 or t_end == -1:
        return None
    return xml[t_start + 5: t_end]


def replace_run(xml, old_raw, new_raw, count=1):
    """Replace old_raw with new_raw inside <a:t> tags. old_raw is the exact
    string as it appears in the XML file (already XML-encoded)."""
    if old_raw not in xml:
        print(f'  WARNING: not found: {old_raw[:60]!r}')
        return xml
    return xml.replace(old_raw, new_raw, count)


def replace_tag_text(xml, old_plain, new_plain, count=1):
    """Replace text by encoding both old and new to XML first."""
    old_xml = to_xml(old_plain)
    new_xml = to_xml(new_plain)
    return replace_run(xml, old_xml, new_xml, count)


# ── Extract T5W1 raw texts directly from the XML files ────────────────────────
# This avoids any encoding guesswork — we read what's actually in the file.

def extract_at_text(xml, hint):
    """Find the <a:t> content containing hint. Returns raw XML-encoded string."""
    t = get_run_text(xml, hint)
    if t is None:
        # hint might be XML-encoded
        t = get_run_text(xml, to_xml(hint))
    return t


# ── Lesson definitions ────────────────────────────────────────────────────────

SLIDES = {
    'Vocabulary': {'title': 2,  'vocab': 4,  'write5': 5,  'read': 6,  'lo': 7,  'pq': 8},
    'Retrieval':  {'title': 9,  'vocab': 11, 'write5': 12, 'read': 13, 'lo': 14, 'pq': 15},
    'Inference':  {'title': 16, 'vocab': 18, 'write5': 19, 'read': 20, 'lo': 21, 'pq': 22},
}

T5W1_DAYS = {'Vocabulary': 'Monday', 'Retrieval': 'Wednesday', 'Inference': 'Thursday'}
T5W2_DAYS = {'Vocabulary': 'Monday', 'Retrieval': 'Wednesday', 'Inference': 'Thursday'}

T5W1_VOCAB = {
    'Vocabulary': [
        ('hemisphere', 'One of the two halves of the Earth, divided by the equator into north and south.'),
        ('latitude',   'Imaginary lines that run east to west around the Earth, measuring distance from the equator.'),
        ('longitude',  'Imaginary lines that run north to south on the Earth, measuring distance from Greenwich.'),
        ('equator',    'The imaginary line that runs around the middle of the Earth, dividing it into north and south.'),
        ('time zone',  'A region of the Earth that shares the same standard time.'),
    ],
    'Retrieval': [
        ('biome',       'A large natural area with its own climate, plants and animals.'),
        ('topography',  'The physical features of an area of land, such as mountains, rivers and plains.'),
        ('vegetation',  'The plants that grow in a particular area or environment.'),
        ('tropical',    'Relating to the region near the equator, known for its warm, wet climate.'),
        ('tundra',      'A vast, flat, treeless region where the ground beneath the surface is permanently frozen.'),
    ],
    'Inference': [
        ('economy',      'The system by which a country produces, distributes and uses money, goods and services.'),
        ('trade',        'The activity of buying and selling goods between people or countries.'),
        ('residential',  'Used for people to live in, such as houses and flats.'),
        ('agricultural', 'Relating to farming and the growing of crops or rearing of animals.'),
        ('commercial',   'Relating to the buying and selling of goods and making money.'),
    ],
}

T5W2_VOCAB = {
    'Vocabulary': VOCAB_VOC,
    'Retrieval':  VOCAB_RET,
    'Inference':  VOCAB_INF,
}

T5W1_FOCUS = {'Vocabulary': 'hemisphere', 'Retrieval': 'biome', 'Inference': 'economy'}
T5W2_FOCUS = {'Vocabulary': FOCUS_WORD_VOC, 'Retrieval': FOCUS_WORD_RET, 'Inference': FOCUS_WORD_INF}

T5W2_TEXTS = {'Vocabulary': STD_VOC, 'Retrieval': STD_RET, 'Inference': STD_INF}

T5W1_READ_INSTR = {
    'Retrieval': 'Fluency focus',   # partial match — enough to find it
    'Inference': 'Fluency focus \u2013 Echo read',
}
T5W2_READ_INSTR = {
    'Retrieval': 'Fluency focus \u2013 Volume.  Take turns reading aloud to the whole class.  Remember to position yourself and push your voice so everyone can hear.',
    'Inference': 'Fluency focus \u2013 Echo read',
}

# T5W1 practice Q text fragments (as they appear plain — will be XML-encoded for search)
T5W1_PQ = {
    'Vocabulary': {
        'q1': 'What is the equator, and why does its position matter for a country’s climate?',
        'a1': 'The equator is an imaginary line dividing the Earth into north and south. Countries near it receive more direct sunlight, so they have warmer, tropical climates.',
        'q2': 'Brazil is mainly in the southern hemisphere. What does this mean?',
        'a2': 'It means that most of Brazil is below the equator, in the southern half of the Earth.',
    },
    'Retrieval': {
        'q1': 'What is a biome? Name one found in Brazil.',
        'a1': 'A biome is a large natural area with its own climate, plants and animals. The Amazon rainforest is one biome found in Brazil.',
        'q2': "How is England's topography different from Brazil's?",
        'a2': "England's topography is mostly gentle and rolling, with the highest ground in the north. Brazil's ranges from low-lying flood plains to highland plateaus, making it much more varied.",
    },
    'Inference': {
        'q1': 'What products does Brazil export?',
        'a1': 'Brazil exports soya beans, cattle, iron ore, oil, coffee and meat to countries around the world, including to the United Kingdom.',
        'q2': 'Why has the Amazon rainforest been affected by farming?',
        'a2': "As Brazil's agricultural industry has grown, forested land has been cleared to make way for farms, reducing the size of the rainforest.",
    },
}

T5W2_PQ = {
    'Vocabulary': {'q1': WE_DO_VOC[0][0], 'a1': WE_DO_VOC[0][1],
                   'q2': WE_DO_VOC[1][0], 'a2': WE_DO_VOC[1][1]},
    'Retrieval':  {'q1': WE_DO_RET[0][0], 'a1': WE_DO_RET[0][1],
                   'q2': WE_DO_RET[1][0], 'a2': WE_DO_RET[1][1]},
    'Inference':  {'q1': WE_DO_INF[0][0], 'a1': WE_DO_INF[0][1],
                   'q2': WE_DO_INF[1][0], 'a2': WE_DO_INF[1][1]},
}


# ── Main replacement loop ─────────────────────────────────────────────────────

for lesson in ['Vocabulary', 'Retrieval', 'Inference']:
    s = SLIDES[lesson]
    print(f'\n── {lesson} ──')

    # Title slide: day name
    xml = read_slide(s['title'])
    xml = replace_run(xml, T5W1_DAYS[lesson], T5W2_DAYS[lesson])
    write_slide(s['title'], xml)
    print(f'  Title: {T5W1_DAYS[lesson]} → {T5W2_DAYS[lesson]}')

    # Vocab hidden slide: 5 word/definition pairs
    xml = read_slide(s['vocab'])
    for (ow, od), (nw, nd) in zip(T5W1_VOCAB[lesson], T5W2_VOCAB[lesson]):
        xml = replace_vocab_word(xml, ow, nw)
        xml = replace_vocab_defn(xml, od, nd)
        print(f'  {ow!r} → {nw!r}')
    write_slide(s['vocab'], xml)

    # Write-it-5-times slide: focus word (appears twice — in table and spider)
    xml = read_slide(s['write5'])
    old_f = T5W1_FOCUS[lesson]
    new_f = T5W2_FOCUS[lesson]
    # Replace ALL occurrences
    count = xml.count(f'<a:t>{old_f}</a:t>')
    xml = xml.replace(f'<a:t>{old_f}</a:t>', f'<a:t>{new_f}</a:t>')
    write_slide(s['write5'], xml)
    print(f'  Focus word: {old_f!r} → {new_f!r} ({count} occurrences)')

    # Independent Read slide: extract text + reading instruction
    xml = read_slide(s['read'])
    # Extract the T5W1 text as it appears raw in the XML
    # Find it by searching for the start
    t1_hints = {
        'Vocabulary': 'Brazil is the largest country in South America',
        'Retrieval':  'Brazil’s physical geography is extraordinarily varied',
        'Inference':  'Brazil and England share some similarities in the way they use their land',
    }
    hint = t1_hints[lesson]
    t1_raw = extract_at_text(xml, hint)
    if t1_raw:
        t2_raw = to_xml(T5W2_TEXTS[lesson])
        xml = xml.replace(t1_raw, t2_raw, 1)
        print(f'  Text: replaced ({len(t1_raw)} → {len(t2_raw)} chars)')
    else:
        print(f'  WARNING: could not find extract text for {lesson}')

    # Reading instruction (Retrieval and Inference only)
    if lesson == 'Retrieval':
        # Find the fluency focus instruction
        fi_hint = 'Decoding &amp; phonics'
        fi_raw = extract_at_text(xml, fi_hint)
        if fi_raw:
            xml = xml.replace(fi_raw, to_xml(T5W2_READ_INSTR['Retrieval']), 1)
            print(f'  Fluency instruction updated')

    write_slide(s['read'], xml)

    # Practice Q slide: Q1, A1, Q2, A2, extract
    xml = read_slide(s['pq'])
    old_pq = T5W1_PQ[lesson]
    new_pq = T5W2_PQ[lesson]

    # Q1 (may be truncated in XML — search for start fragment)
    q1_raw = extract_at_text(xml, to_xml(old_pq['q1'][:40]))
    if q1_raw:
        xml = xml.replace(q1_raw, to_xml(new_pq['q1']), 1)
        print(f'  PQ Q1 replaced')
    else:
        print(f'  WARNING: PQ Q1 not found')

    a1_raw = extract_at_text(xml, to_xml(old_pq['a1'][:40]))
    if a1_raw:
        xml = xml.replace(a1_raw, to_xml(new_pq['a1']), 1)
        print(f'  PQ A1 replaced')
    else:
        print(f'  WARNING: PQ A1 not found')

    q2_raw = extract_at_text(xml, to_xml(old_pq['q2'][:40]))
    if q2_raw:
        xml = xml.replace(q2_raw, to_xml(new_pq['q2']), 1)
        print(f'  PQ Q2 replaced')
    else:
        print(f'  WARNING: PQ Q2 not found')

    a2_raw = extract_at_text(xml, to_xml(old_pq['a2'][:40]))
    if a2_raw:
        xml = xml.replace(a2_raw, to_xml(new_pq['a2']), 1)
        print(f'  PQ A2 replaced')
    else:
        print(f'  WARNING: PQ A2 not found')

    # Extract text in PQ slide
    t1_raw = extract_at_text(xml, hint)
    if t1_raw:
        xml = xml.replace(t1_raw, to_xml(T5W2_TEXTS[lesson]), 1)
        print(f'  PQ extract replaced')

    write_slide(s['pq'], xml)

print('\nAll done.')
