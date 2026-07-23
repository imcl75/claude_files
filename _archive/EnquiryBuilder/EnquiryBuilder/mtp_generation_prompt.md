# MTP Generation — Standing Instructions

Use these rules every time you generate an MTP JSON file for a Geography or Science enquiry.

---

## Three vocabulary lists — they are NOT the same list

Every MTP has three vocabulary structures. Each serves a different reader and a different purpose. Write them separately. Some overlap between lists is natural — do not worry about it — but do not copy one list to fill the others.

### 1. `mtp.vocabulary[]` — Top-10 poster (10 words)

**Who:** Less confident learners who need the most foundational 10 words to access the enquiry at all.
**Output:** A3 poster, printed for books or displayed in the room. Words with images.
**Write:** The 10 most important access words. Prefer concrete, high-frequency terms over technical depth.
**Format:**
```json
{ "word": "orbit", "definition": "The path one object takes around another because of gravity.", "image": "vocab_sci_orbit.png" }
```
Image filename: `vocab_geo_{slug}.png` for Geography, `vocab_sci_{slug}.png` for Science.

### 2. `mtp.ko.vocabulary[]` — Knowledge Organiser (~12–16 pairs)

**Who:** All children — this is the class reference document they use throughout the enquiry.
**Output:** KO PDF, kept in books.
**Write:** Comprehensive. Include the top-10 words plus the extra technical vocabulary needed to follow the full enquiry. Definitions can be slightly more precise than the poster.
**Format:** list-of-lists — `["word", "definition"]`. NOT dicts. This is intentional.
```json
["orbit", "the path one object takes around another due to gravity"]
```

### 3. `mtp.lessons[n].vocabulary[]` — Lesson vocab (~4–5 per lesson)

**Who:** Children in that specific lesson, for the animated vocabulary slide.
**Output:** One animated slide in the lesson PPTX.
**Write:** Only the 4–5 words being introduced or heavily used in that specific lesson. These may overlap with the other lists — that is fine.
**Format:**
```json
{ "word": "orbit", "definition": "The path one object takes around another because of gravity." }
```

---

## ko block

```json
"ko": {
  "key_facts": ["8 concise facts about the enquiry topic"],
  "key_skills": ["5 skills the children will develop across the enquiry"],
  "vocabulary": [["word", "definition"], ...]
}
```

- `key_facts`: 8 facts, each one sentence. Cover the full enquiry breadth, not just lesson 1.
- `key_skills`: 5 skills. Mix subject-specific (e.g. reading a data table) and transferable (e.g. explaining using evidence).
- `vocabulary`: 12–16 pairs as list-of-lists. Covers everything on the top-10 poster plus additional technical terms.

---

## resources block

```json
"resources": [
  {
    "type": "sort_cards",
    "title": "...",
    "output": "Sort_Cards.pdf",
    "items": [{"text": "..."}, ...]
  },
  {
    "type": "word_cards",
    "title": "...",
    "output": "Word_Cards.pdf",
    "items": [{"word": "...", "definition": "..."}, ...]
  },
  {
    "type": "statement_sort",
    "title": "True or False? — [topic]",
    "output": "Statement_Sort.pdf",
    "items": [{"text": "...", "answer": "..."}, ...]
  }
]
```

- `sort_cards`: 10–14 items. Used in lesson 1 to hook enquiry thinking. Each card = one object, place, or concept from the enquiry — children sort into categories.
- `word_cards`: 10–14 items matching `ko.vocabulary`. Used as a matching or definition activity.
- `statement_sort`: 8–10 items. Half true, half false. Answers given so children can self-check.
- `writing_mat` is optional — only include if there is significant writing in the enquiry.

---

## Subject field

- Geography: `"subject": "geographer"` at lesson level
- Science: `"subject": "scientist"` at lesson level
- Top-level MTP field: `"subject": "science"` or `"subject": "geography"`

---

## What NOT to do

- Do not copy `ko.vocabulary` into `mtp.vocabulary` with different formatting.
- Do not list 14 words in `mtp.vocabulary` — it must be exactly 10 (the poster grid is 5×2).
- Do not use `knowledge_organiser` or `supporting_resources` as key names — use `ko` and `resources`.
- Do not encode `ko.vocabulary` as a list of dicts — it must be a list-of-lists.
