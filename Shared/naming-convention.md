# WFA File Naming Convention

All lesson outputs follow a single convention so files sort correctly in a folder.

## Standard pattern

```
{TxWy} - {N} - {DayName} - {Subject}{Type}.{ext}
```

| Token | Example |
|-------|---------|
| TxWy | T6W5 |
| N | 1, 2, 3, 4, 5 |
| DayName | Monday, Tuesday, Wednesday, Thursday, Friday |
| Subject | See table below |
| Type | Teaching, LP, Standard, Supported, Answers, Data |
| ext | pptx, pdf, xlsx, docx |

## Subject labels

| CLF "Being a…" | Subject token |
|----------------|---------------|
| Being a Reader | Reader |
| Being a Writer | Writer |
| Being a Mathematician | Maths |
| Being a Geographer | Geographer |
| Being a Historian | Historian |
| Being a Scientist | Scientist |
| Being a Linguist | Linguist |
| Being a Citizen | Citizen |
| Being an Artist | Artist |
| Being a Designer | Designer |
| Being a Musician | Musician |
| Spelling Shed | Spelling |

## File type suffixes

| Suffix | Meaning |
|--------|---------|
| Teaching | Main lesson PPTX for smartboard |
| LP | Learning Paper PPTX or PDF |
| Standard | Standard pupil PDF (Being a Reader) |
| Supported | Supported pupil PDF (Being a Reader) |
| Answers | All-answers PDF (Being a Reader) |
| Data | Data/content XLSX (Being a Reader) |
| Plan | Unit planning DOCX (enquiry planner) |

## Weekly/standalone outputs (no day number)

These outputs cover a whole week or aren't tied to a single lesson:

```
{TxWy} - MathsWorkingMemory.pptx
{TxWy} - ReaderTeaching.pptx
{TxWy} - ReaderStandard.pdf
{TxWy} - ReaderSupported.pdf
{TxWy} - ReaderAnswers.pdf
{TxWy} - ReaderData.xlsx
{TxWy} - ArithmeticReasoning.pdf
{TxWy} - HomeLearningStandard.pdf
{TxWy} - HomeLearningAdapted.pdf
{TxWy} - HomeLearningEditing.pdf
{TxWy} - {Subject}Plan.docx        (e.g. T6W5 - GeographerPlan.docx)
```

## Day-specific outputs (include day number + name)

```
{TxWy} - {N} - {DayName} - SpellingTeaching.pptx
{TxWy} - {N} - {DayName} - SpellingLP.pptx
{TxWy} - {N} - {DayName} - WriterTeaching.pptx
{TxWy} - {N} - {DayName} - MathsTeaching.pptx
{TxWy} - {N} - {DayName} - MathsLP.pdf
{TxWy} - {N} - {DayName} - MathsLP.pptx
{TxWy} - {N} - {DayName} - GeographerTeaching.pptx
{TxWy} - {N} - {DayName} - HistorianTeaching.pptx
{TxWy} - {N} - {DayName} - ScientistTeaching.pptx
```

## Implementation status

| Skill | Status | Where name is set |
|-------|--------|-------------------|
| Maths (teaching) | ✅ Done | `Maths/build_lesson_v3.py` |
| Maths (LP) | ✅ Done | `Maths/build_stats_lp_pdf.py` |
| Maths (working memory) | ✅ Done | `Maths/working_memory_starters.py` |
| Spelling Shed | ✅ Done | SKILL.md rename step |
| Being a Reader | ✅ Done | `Skills/being-a-reader-SKILL.md` Step 7 |
| Writing lesson | ✅ Done | `Writing/build_lesson.py` |
| Enquiry planner | ✅ Done | SKILL.md present step (use `{TxWy} - {Subject}Plan.docx`) |
| Home Learning | Pending | |
| Arithmetic & Reasoning | Pending | |
| ETIW | Pending | |
