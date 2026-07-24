# Transfer: Y4 Spanish T1 PPTX build

**Generated:** 2026-07-24
**Originating focus:** Building 6 × pptxgenjs lesson PPTXs for Y4 Spanish T1 (L01–L06), following on from fixing and delivering Y3 T1 L02–L06.
**Skill in use:** none (manual pptxgenjs build)

---

## Status

Y3 T1 L02–L06 PPTXs are fixed (4 layout bugs) and delivered. Naming convention corrected from Aut1→T1 throughout.

Y4 work: data file complete at `/home/claude/y4_t1_data.js`. Generator `gen_y4_t1.js` has NOT been written — that is the immediate next task. One Higgsfield cultural image job was kicked off (L01) but not yet confirmed or downloaded. Three more images still need generating (L02, L04, L05).

---

## What's been produced

- `/home/claude/gen_y3_aut1.js` — Y3 generator, 4 layout bugs fixed, Aut1→T1 naming done. Final.
- `/home/claude/y3_lesson_data.js` — Y3 T1 lesson data, filenames corrected to `Y3_Sp_T1_`. Final.
- `Y3_Sp_T1_L02_MeLlamo.pptx` through `Y3_Sp_T1_L06_Repaso.pptx` — delivered to Innes. Final.
- `/home/claude/y4_t1_data.js` — Y4 T1 lesson data for all 6 lessons. Complete and ready to use.
- `gen_y4_t1.js` — **NOT YET WRITTEN**. This is the next task.

---

## Decisions locked in

- **Naming convention:** T1–T6 for all terms (not Aut1/2, Spr1/2, Sum1/2)
- **Y4 brand colours:** `BLUE='1798D3'`, `AMBER='FFC000'`, `BG='DEECF8'`, `WHITE='FFFFFF'`, `DARK='1A1A2E'`, `CONS_FILL='C8DFF2'`, `CONS_TEXT='0B4F7A'`
- **Y4 alphabet tiles:** All letters shown as "known" (no grey/future tiles — Y4 are not seeing the alphabet for the first time). Vowels=amber, current phonics letter=BLUE, all other consonants=light blue-grey (`CONS_FILL/CONS_TEXT`)
- **Counting layout:** `countingMax=10` → 2 rows of 5 (cardW=2.3, cardH=2.2); `countingMax=20` → 4 rows of 5 (cardW=2.35, cardH=1.15). Sign-off banner at y=6.85, h=0.42.
- **Slide badge text:** `'Y4 · T1 · L'`
- **Fonts:** `FONT_HEADING='Twinkl Cursive Looped'`, `FONT_BODY='Calibri'`
- **16-slide structure:** same order as Y3 — Title, LO, Cultural, Vowels, Alphabet, Counting, Warm-Up, Vocab, Content×3, Phonics, Activity×3, Round-Off
- **pptxgenjs:** v4.0.1 at `/home/claude/.npm-global/lib/node_modules/pptxgenjs`. ShapeType refs extracted from a throw-away instance: `RECT`, `ROUND_RECT`, `ELLIPSE`.
- **Higgsfield images:** model `nano_banana_pro`, aspect `16:9`. Download as JPG to `/home/claude/`. Embed via base64 `data:image/jpeg;base64,...`.

---

## Y4 data file structure differences from Y3 (critical for generator)

The Y4 data uses slightly different field names to Y3. The generator must handle these:

**Cultural slide:** `{ title, subtitle, fact1, fact2, fact3, imgFile }` — NOT a `facts[]` array with `icon/text`. Redesign cultural slide to show 3 fact cards from fact1/fact2/fact3 strings.

**LO criteria:** plain string array — NOT objects with `.text` / `.pro`. Just `lesson.criteria[i]` directly.

**Phonics examples:** `{ word, meaning, highlight }` — NOT `{ word, pro, note }`. Y3 generator uses `ex.pro` and `ex.note`; Y4 must use `ex.meaning` instead (no pronunciation shown per example).

**Activity slides:** `{ title, instruction, steps[] }` — no `icon`, `time`, or `setup` fields. Drop the icon circle, time badge and setup badge from Y3. Just: instruction box + numbered steps.

**Phonics tip:** `ph.tip` (string) replaces Y3's `ph.rule` / `ph.badge` combination.

---

## Y4 content slides by lesson number

The `buildContentSlides` dispatcher switches on `lesson.num`:

| lesson.num | Content focus | Slide titles |
|---|---|---|
| 1 | Y3 greetings + colours recap | Greetings recap; Colours recap; Full conversation |
| 2 | ¿Tienes mascotas? — pets dialogue | Vocab cards: 5 pets; Dialogue: ¿Tienes mascotas?; Pet survey |
| 3 | New numbers 11–20 + new animals | Numbers 11–20 showcase; New animals; ¿Cuántos animales? |
| 4 | Weather patterns (hace/llueve/hay) | Weather phrases; hace vs llueve vs hay; Forecast activity |
| 5 | Four seasons | Season cards (4-up); En [estación] sentence builder; Mi estación favorita |
| 6 | T1 revision | Pets+numbers recap; Weather recap; Seasons+phonics recap |

---

## Warm-up recap for Y4

Replace Y3's `buildWarmUpRecap` with Y4-appropriate known vocab:

```js
function buildWarmUpRecap(lessonNum) {
  const base = [
    { es:'¡Hola! / ¡Adiós!',    en:'Hello! / Goodbye!' },
    { es:'Buenos días',           en:'Good morning' },
    { es:'¿Cómo estás?',         en:'How are you?' },
    { es:'Me llamo...',           en:'My name is...' },
    { es:'Tengo... años',         en:'I am ... years old' },
    { es:'uno... diez',           en:'Numbers 1–10' },
    { es:'rojo, azul, verde...',  en:'Red, blue, green...' },
    { es:'El X es [colour]',      en:'The X is [colour]' },
  ];
  if (lessonNum >= 2) base.push(
    { es:'un gato / un perro',    en:'a cat / a dog' },
    { es:'Tengo un...',           en:'I have a...' }
  );
  if (lessonNum >= 3) base.push(
    { es:'once... veinte',        en:'Numbers 11–20' },
    { es:'un caballo / un pájaro',en:'a horse / a bird' }
  );
  if (lessonNum >= 4) base.push(
    { es:'Hace sol / llueve',     en:'It\'s sunny / raining' },
    { es:'Hace frío / calor',     en:'It\'s cold / hot' }
  );
  if (lessonNum >= 5) base.push(
    { es:'el verano / el invierno',en:'summer / winter' },
    { es:'En verano, hace calor', en:'In summer, it\'s hot' }
  );
  return base.slice(0, 8);
}
```

---

## Higgsfield image jobs

| Lesson | File | Job ID | Status |
|---|---|---|---|
| L01 | l01_spain_geo.jpg | `740ed92d-094e-4f09-9e3e-b5c1dece9bdd` | Kicked off — check `job_display` |
| L02 | l02_spain_home.jpg | — | Not started |
| L04 | l04_spain_weather.jpg | — | Not started |
| L05 | l05_spain_seasons.jpg | — | Not started |
| L03 | — | — | imgFile:null, no image needed |
| L06 | — | — | imgFile:null, no image needed |

**Prompts to use (model: nano_banana_pro, aspect: 16:9):**
- L01: `Aerial landscape photo of Spain showing the Pyrenees mountains, river valleys and Mediterranean coastline, golden light, dramatic geography, editorial style`
- L02: `Sunny Spanish street market in a white-walled Andalusian village, colourful fresh produce stalls, families shopping, cheerful and warm`
- L04: `Split weather map of Spain showing sun in the south, rain clouds in the north and snow on mountains, illustrated editorial style, bright colours`
- L05: `Four-panel collage of the seasons in Spain: spring blossom festival, hot summer beach, autumn grape harvest, winter snowy sierra, vibrant colours`

---

## Files in play

| Path | State | Notes |
|---|---|---|
| `/home/claude/y4_t1_data.js` | Complete | Source of truth for all 6 lessons |
| `/home/claude/gen_y3_aut1.js` | Final | Use as template for gen_y4_t1.js |
| `/home/claude/gen_y4_t1.js` | Not written | Immediate task |
| `/home/claude/l01_spain_geo.jpg` | Pending download | Check Higgsfield job first |
| `/home/claude/l02_spain_home.jpg` | Not generated | Generate via Higgsfield |
| `/home/claude/l04_spain_weather.jpg` | Not generated | Generate via Higgsfield |
| `/home/claude/l05_spain_seasons.jpg` | Not generated | Generate via Higgsfield |

---

## Y3 layout bug fixes already applied — replicate these in Y4

1. **Alphabet key:** `keyGap=2.4` (not 2.8). `!` annotation on separate line below key row at `excY = keyRowY + keyBoxH + 0.06`.
2. **NEW! badge on counting cards:** Badge at `y:cy-0.28` (above card top), NOT inside the card.
3. **Round-off vocab tiles:** 3 tiles only (not 6), `startY=5.55`, label `y=5.3`. Keeps clear of exit ticket box.
4. **Round-off sign-off:** at `y=6.85`, h=0.5. Exit ticket box `h=1.85`.

---

## Open questions / blockers

- None from Innes — he said "go ahead with Y4 T1"

---

## Immediate next step

1. Check Higgsfield job `740ed92d-094e-4f09-9e3e-b5c1dece9bdd` with `job_display` and download L01 image if ready.
2. Generate L02, L04, L05 images via Higgsfield (prompts above).
3. Write `/home/claude/gen_y4_t1.js` using gen_y3_aut1.js as template — adapt for Y4 brand, data field differences, counting layout and content slides listed above.
4. Run `node gen_y4_t1.js`, QA thumbnails with LibreOffice → pdftoppm, deliver all 6 PPTXs to Innes.
