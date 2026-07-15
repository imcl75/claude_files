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

T5W1_DAYS = {'Vocabulary': 'Monday', 'Retrieval': 'Tuesday', 'Inference': 'Wednesday'}
T5W2_DAYS = {'Vocabulary': 'Tuesday', 'Retrieval': 'Thursday', 'Inference': 'Friday'}

T5W1_VOCAB = {
    'Vocabulary': [
        ('dialogue',   'the words spoken between characters in a story'),
        ('persistent', 'keeping on trying and not giving up, even when it is difficult'),
        ('suspicious', 'feeling that something is wrong or that someone is not being truthful'),
        ('repetition', 'when something is said or done again and again'),
        ('reveal',     'to show or make known something that was hidden'),
    ],
    'Retrieval': [
        ('pattern',   'a repeated design or sequence that helps us notice when something changes'),
        ('deny',      'to say that something is not true or that you did not do something'),
        ('politely',  'in a kind and respectful way'),
        ('panicked',  'suddenly feeling very worried or frightened, often causing a rushed reaction'),
        ('hopeless',  'feeling that there is no chance of things getting better'),
    ],
    'Inference': [
        ('technique',  'a particular way of doing something, especially in writing or art'),
        ('infer',      'to work out something that is not said directly, using clues'),
        ('omission',   'when something is deliberately left out or not included'),
        ('echo',       'when something is repeated in a way that reminds you of something earlier'),
        ('impression', 'the feeling or idea you are left with after reading or seeing something'),
    ],
}

T5W2_VOCAB = {
    'Vocabulary': VOCAB_VOC,
    'Retrieval':  VOCAB_RET,
    'Inference':  VOCAB_INF,
}

T5W1_FOCUS = {'Vocabulary': 'dialogue', 'Retrieval': 'pattern', 'Inference': 'infer'}
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
        'q1': 'The text says Bear noticed something \u2018suspicious\u2019 about the rabbit. What does suspicious suggest about how',
        'a1': 'It suggests Bear felt uneasy and began to sense that something was not right about the rabbit\u2019s answer.',
        'q2': 'The text says every word matters in the dialogue. What does this suggest about the writer\u2019s use of language?',
        'a2': 'It suggests the writer has chosen each word carefully so that small details give the reader important clues.',
    },
    'Retrieval': {
        'q1': 'What question does Bear ask every animal he meets in the forest?',
        'a1': 'Bear asks every animal the same question: \u201cHave you seen my hat?\u201d',
        'q2': 'How is the rabbit\u2019s answer different from the other animals\u2019 answers?',
        'a2': 'The other animals give short, calm replies. The rabbit says \u201cNo. Why are you asking me? I would never steal a hat. I do not even like hats.\u201d Nobody else mentioned stealing, liking hats or being asked again.',
    },
    'Inference': {
        'q1': 'Bear\u2019s answer to the squirrel sounds almost exactly like the rabbit\u2019s earlier answer. Why does the writer',
        'a1': 'The writer uses this to show that Bear is now hiding something, just as the rabbit was hiding something. The echo of the rabbit\u2019s words reveals Bear\u2019s guilt.',
        'q2': 'What technique does the writer use to make the ending powerful? Use evidence from the text.',
        'a2': 'The writer uses omission \u2014 leaving out what happened to the rabbit. The text says the writer never tells us directly. This makes the reader infer the ending from the clues, which makes it more powerful.',
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
    # FIX: replacements are scoped to the <p:graphicFrame> table ONLY.
    # Previously, replace() ran on the full slide XML, which hit TextBox 14 before
    # the table for the first definition — corrupting the prompt text and cascading
    # wrong definitions into subsequent rows every week.
    VOCAB_PROMPT = (
        'Are there any words you feel confident to explain the meaning of (definition)? '
        'Are there any where you are less confident?'
    )
    xml = read_slide(s['vocab'])

    # Step 1: Restore TextBox 14 to the correct prompt text if a previous build
    # incorrectly placed a vocabulary definition there.
    prompt_xml = to_xml(VOCAB_PROMPT)
    tb_name_idx = xml.find('name="TextBox 14"')
    if tb_name_idx != -1:
        sp_end_idx = xml.find('</p:sp>', tb_name_idx)
        at_start = xml.find('<a:t>', tb_name_idx)
        at_end = xml.find('</a:t>', at_start) if at_start != -1 else -1
        if at_start != -1 and at_end != -1 and at_start < sp_end_idx:
            current_text = xml[at_start + 5: at_end]
            if current_text != prompt_xml:
                xml = xml[:at_start + 5] + prompt_xml + xml[at_end:]
                print(f'  TextBox 14 restored (was: {current_text[:50]!r})')

    # Step 2: Replace words/defs inside the graphicFrame table ONLY.
    gf_match = re.search(r'<p:graphicFrame>.*?</p:graphicFrame>', xml, re.DOTALL)
    if gf_match:
        gf_xml = gf_match.group(0)
        for (ow, od), (nw, nd) in zip(T5W1_VOCAB[lesson], T5W2_VOCAB[lesson]):
            gf_xml = replace_tag_text(gf_xml, ow, nw)
            gf_xml = replace_tag_text(gf_xml, od, nd)
            print(f'  {ow!r} → {nw!r}')
        xml = xml[:gf_match.start()] + gf_xml + xml[gf_match.end():]
    else:
        print(f'  WARNING: no graphicFrame on vocab slide {s["vocab"]}, falling back to full-slide replace')
        for (ow, od), (nw, nd) in zip(T5W1_VOCAB[lesson], T5W2_VOCAB[lesson]):
            xml = replace_tag_text(xml, ow, nw)
            xml = replace_tag_text(xml, od, nd)
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
        'Vocabulary': 'Bear had lost his hat',
        'Retrieval': 'In the story I Want My Hat Back, Bear asks many',
        'Inference': 'At the end of the story, Bear finds the rabbit. The writer does not describe',
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
        fi_hint = 'Fluency focus'
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
