"""
L12 Model Text — A4 landscape handout.
Starts from paragraph 2 (city descent). Five plot points. Y4 punctuation only.
No sentences starting with conjunctions. Dog scary-then-friendly arc.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W2_FriAM_Model_Text.pdf'

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 1.6 * cm

BLUE  = HexColor('#1798d3')
LBLUE = HexColor('#EBF5FB')
DGREY = HexColor('#333333')
GREY  = HexColor('#888888')
LGREY = HexColor('#F5F5F5')
MGREY = HexColor('#DDDDDD')

c = canvas.Canvas(OUT, pagesize=landscape(A4))
c.setTitle("Varjak's First Night Outside — Model Text")

# ── Header bar ─────────────────────────────────────────────────────
bar_h = 0.9 * cm
c.setFillColor(BLUE)
c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 12)
c.drawString(MARGIN, PAGE_H - bar_h + 0.26 * cm,
             "Varjak\u2019s First Night Outside  \u2014  Model Text")
c.setFont('Helvetica', 9.5)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.26 * cm,
                  "T6W2 Friday AM  |  Being a Writer  |  Year 4")

# ── Column split ────────────────────────────────────────────────────
col_split = PAGE_W * 0.56
key_x     = col_split + 0.25 * cm
key_w     = PAGE_W - key_x - MARGIN * 0.6

# ── Annotation key ──────────────────────────────────────────────────
key_y = PAGE_H - bar_h - 0.28 * cm
key_h = 3.5 * cm

c.setFillColor(LBLUE)
c.rect(key_x, key_y - key_h, key_w, key_h, fill=1, stroke=0)
c.setFillColor(BLUE)
c.setFont('Helvetica-Bold', 8.5)
c.drawString(key_x + 0.22 * cm, key_y - 0.42 * cm,
             "Annotation key  \u2014  use four colours")

items = [
    ("Colour 1", "Setting and character description",
     "expanded noun phrases, sensory detail, thoughts and reactions"),
    ("Colour 2", "Figurative language",
     "simile, alliteration, hyperbole, power of three"),
    ("Colour 3", "Sentence structure",
     "fronted adverbials, subordinating conjunctions, short sentences"),
    ("Colour 4", "Speech punctuation",
     "inverted commas, reporting clauses, action woven in"),
]
ky = key_y - 0.98 * cm
for label, title, sub in items:
    c.setFillColor(DGREY)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(key_x + 0.3 * cm, ky, f"{label}: {title}")
    c.setFillColor(GREY)
    c.setFont('Helvetica', 7)
    c.drawString(key_x + 0.52 * cm, ky - 0.28 * cm, sub)
    ky -= 0.66 * cm

# ── Annotation notes ────────────────────────────────────────────────
ann_y      = key_y - key_h - 0.2 * cm
ann_bottom = 0.68 * cm

c.setFillColor(LGREY)
c.setStrokeColor(MGREY)
c.setLineWidth(0.4)
c.rect(key_x, ann_bottom, key_w, ann_y - ann_bottom, fill=1, stroke=1)

c.setFillColor(GREY)
c.setFont('Helvetica', 7.5)
c.drawString(key_x + 0.28 * cm, ann_y - 0.38 * cm, "Annotation notes")

ry = ann_y - 0.64 * cm
c.setStrokeColor(MGREY)
c.setLineWidth(0.25)
while ry > ann_bottom + 0.28 * cm:
    c.line(key_x + 0.18 * cm, ry, key_x + key_w - 0.18 * cm, ry)
    ry -= 0.52 * cm

# ── Text layout helpers ──────────────────────────────────────────────
tx       = MARGIN
text_w   = col_split - MARGIN - 0.45 * cm
body_sz  = 9.0
lead     = 11.6
para_gap = 1.5
ty       = PAGE_H - bar_h - 0.35 * cm
bot      = 0.68 * cm

def wrap(text):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if stringWidth(test, 'Helvetica', body_sz) <= text_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def emit(lines, italic=False):
    global ty
    font = 'Helvetica-Oblique' if italic else 'Helvetica'
    for ln in lines:
        if ty - lead < bot: return
        c.setFillColor(DGREY)
        c.setFont(font, body_sz)
        c.drawString(tx, ty, ln)
        ty -= lead
    ty -= para_gap

def gap(extra=3):
    global ty
    ty -= extra

# ── Title ────────────────────────────────────────────────────────────
ty_start = PAGE_H - bar_h - 0.36 * cm
c.setFillColor(BLUE)
c.setFont('Helvetica-Bold', 13)
c.drawString(tx, ty_start - 0.38 * cm, "Varjak\u2019s First Night Outside")
c.setStrokeColor(BLUE)
c.setLineWidth(0.5)
c.line(tx, ty_start - 0.56 * cm, tx + text_w, ty_start - 0.56 * cm)
ty = ty_start - 0.80 * cm

# ════════════════════════════════════════════════════════════════════
# MODEL TEXT — five plot points, Y4 punctuation only, no conjunction openers
# ════════════════════════════════════════════════════════════════════

# ── SECTION 2: Varjak enters the city — sensory experience ──────────
emit(wrap("Trembling with cold, he crept down from the wall into the alleyway below. "
          "The smell hit him like a fist. Oil, hot metal and something sharp that he "
          "had no name for filled his nose and made his eyes water. Shadows slipped "
          "and slid along the damp, dark brickwork. A sea of lights blinked and pulsed "
          "at the end of the street. He had imagined the Outside a thousand times. "
          "He had never imagined anything like this."))

# ── SECTION 3: Two cats, car-not-dog confusion ──────────────────────
emit(wrap("He had not gone far when a shape dropped silently from the wall above. "
          "Then another."))

# Dialogue block — new speaker new line, action woven in
for line in [
    "\u201cYou lost?\u201d said one of them. She was lean and fast-looking, with eyes like pale flames.",
    "\u201cNo,\u201d said Varjak. \u201cI am looking for a dog.\u201d",
    "The two cats stared at each other. The first one started to laugh. \u201cA dog?\u201d she said. \u201cYou? Looking for a dog?\u201d",
]:
    emit(wrap(line))

emit(wrap("Varjak didn\u2019t answer. At the end of the alleyway, something vast was "
          "thundering along the road. Its eyes blazed white and its whole body shook "
          "with a sound like a hundred growls rolled into one. "
          "He pressed himself flat against the wall. "
          "\u201cIs that one?\u201d he said. \u201cIs that what they call a dog?\u201d"))

emit(wrap("The two cats looked. The first one tilted her head. "
          "\u201cThat,\u201d she said, \u201cis a car.\u201d "
          "She glanced at her friend, then back at Varjak, "
          "and when she spoke again her voice was a little gentler. "
          "\u201cDogs are different. Come on.\u201d"))

# ── SECTION 4: Journey and dog — scary first, then friendly ─────────
emit(wrap("He followed them deeper into the city, though his paws ached and his heart "
          "would not slow down. They turned left, then right, then down a long steep "
          "alley that smelled of rain and old stone. At the far end, in a patch of "
          "yellow lamplight, something enormous lay very still."))

emit(wrap("Varjak stopped. The creature was bigger than anything he had ever seen in "
          "his life. It was huge and dark, with fur the texture of wire and teeth "
          "like white knives. A low sound came from deep inside its chest. Not quite "
          "a growl. Something worse."))

for line in [
    "\u201cThat,\u201d said the first cat quietly, \u201cis a dog.\u201d",
]:
    emit(wrap(line))

emit(wrap("Varjak crept forward a step. His legs had gone hollow and his claws "
          "scraped against the cobbles without him telling them to. "
          "The dog\u2019s eyes opened. They were pale and cold, like two chips of ice. "
          "They fixed on Varjak and did not move."))

emit(wrap("\u201cAre you looking for something, little cat?\u201d the dog said."))

emit(wrap("Varjak swallowed. \u201cI need your help,\u201d he said. "
          "\u201cMy family are in danger.\u201d"))

emit(wrap("For a long moment the dog said nothing. Then the rough coat settled. "
          "The great head dropped slowly. Something in those pale eyes changed, "
          "like a fire going down to embers, and the voice that came out next "
          "was low and steady."))

emit(wrap("\u201cTell me what you need,\u201d it said."))

# ── SECTION 5: Razor's gang ─────────────────────────────────────────
emit(wrap("They had no time to make a plan. Something screeched from the shadows "
          "just as Varjak was about to speak. Five cats slid out of the darkness, "
          "their eyes glittering and their claws already unsheathed. "
          "Varjak had heard about Razor\u2019s gang. "
          "They were the ones who ruled these streets."))

emit(wrap("\u201cRun,\u201d said the first cat."))

emit(wrap("Varjak stood his ground. He was afraid. He was outnumbered. "
          "He had been training for this moment his whole life. "
          "He felt the Way move through him, calm and steady, "
          "like water running over smooth stone. "
          "The gang moved fast, but Varjak moved faster. "
          "His friends fought beside him, and the gang scattered howling into the dark."))

emit(wrap("The alleyway was silent. Varjak stood in the lamplight and looked at his paws. "
          "He was still shaking. He had done it."))

# ── Footer ────────────────────────────────────────────────────────────
c.setFillColor(GREY)
c.setFont('Helvetica', 7)
c.drawString(MARGIN, 0.32 * cm,
             "T6W2  |  L12 Friday AM  |  Varjak Paw by S. F. Said  |  Teacher model text")
c.drawRightString(PAGE_W - MARGIN, 0.32 * cm,
                  "Colour 1: setting/character  \u2022  Colour 2: figurative language  "
                  "\u2022  Colour 3: sentence structure  \u2022  Colour 4: speech punctuation")

c.save()
print("Saved:", OUT)
