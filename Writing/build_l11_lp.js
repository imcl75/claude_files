const PptxGenJS = require('pptxgenjs');
const path = require('path');
const fs   = require('fs');

const ASSETS = '/mnt/skills/user/learning-paper/assets';
const OUT    = '/mnt/user-data/outputs/T6W2_ThuAM2_Writer_LP.pptx';

const CM   = 1 / 2.54;
const SLIDE_W = 7.5;
const SLIDE_H = 10.833;
const LL_SET2_W = 7.3;
const LL_SET2_H = 1.85;
const FONT_C = 'Twinkl Cursive Looped';
const FONT_L = 'Aptos';
const BLACK  = '000000';
const BLUE   = '1798d3';
const LINE_H = 0.315;   // 0.8cm

const pptx = new PptxGenJS();
pptx.defineLayout({ name: 'A4P', width: SLIDE_W, height: SLIDE_H });
pptx.layout = 'A4P';

const slide = pptx.addSlide();

// ── Set 2 Writer label ──────────────────────────────────────────────
const lx = 0.1, ly = 0.1;
const w = LL_SET2_W, h = LL_SET2_H;

// ETIW banner
const bannerW = w - 0.08;
const bannerH = bannerW / 7.04;
const bannerY = ly + h - bannerH - 0.02;
slide.addImage({ path: path.join(ASSETS, 'ETIW_LKS2.png'), x: lx + 0.04, y: bannerY, w: bannerW, h: bannerH });

// LKS2 logo
const topH = h - bannerH - 0.06;
const logoSize = topH * 0.75;
slide.addImage({ path: path.join(ASSETS, 'school_logo_LKS2.png'), x: lx + 0.06, y: ly + 0.02, w: logoSize, h: logoSize });

// Date
slide.addText('11/06/2026', {
  x: lx + 0.02, y: ly + logoSize + 0.02, w: logoSize + 0.1, h: 0.16,
  fontSize: 7, fontFace: FONT_L, align: 'center', color: BLACK, margin: 0
});

// Writer icon
const writerIconSize = 0.35;
const writerX = lx + w - writerIconSize - 0.08;
slide.addImage({ path: path.join(ASSETS, 'writer.png'), x: writerX, y: ly + 0.22, w: writerIconSize, h: writerIconSize });
slide.addText('Writer', {
  x: writerX - 0.12, y: ly + 0.22 + writerIconSize, w: writerIconSize + 0.24, h: 0.15,
  fontSize: 7, fontFace: FONT_L, bold: true, align: 'center', color: BLACK, margin: 0
});

// Key Question + Learning Focus
const textX = lx + logoSize + 0.2;
const textW  = writerX - textX - 0.15;
slide.addText([
  { text: 'Key Question:  ', options: { bold: true, fontSize: 11 } },
  { text: 'How does a writer make a reader feel characters\u2019 emotions?', options: { bold: true, fontSize: 11 } }
], { x: textX, y: ly + 0.06, w: textW, h: 0.35, fontFace: FONT_L, color: BLACK, margin: 0, valign: 'top' });

slide.addText([
  { text: 'Learning Focus:  ', options: { bold: true, fontSize: 11 } },
  { text: 'To punctuate direct speech accurately', options: { fontSize: 11, underline: { style: 'sng' } } }
], { x: textX, y: ly + 0.40, w: textW, h: 0.35, fontFace: FONT_L, color: BLACK, margin: 0, valign: 'top' });

// ── Five rules reference box ────────────────────────────────────────
let cy = ly + h + 0.18;

slide.addShape(pptx.ShapeType.rect, {
  x: 0.1, y: cy, w: 7.3, h: 1.22,
  fill: { color: 'EBF5FB' }, line: { color: '1798d3', width: 0.75 }
});
slide.addText('The five rules of speech punctuation', {
  x: 0.2, y: cy + 0.05, w: 7.1, h: 0.22,
  fontSize: 10, fontFace: FONT_L, bold: true, color: '1798d3', margin: 0
});
const rules = [
  '1. Inverted commas around the spoken words.',
  '2. Capital letter at the start of the speech.',
  '3. Punctuation before the closing inverted comma.',
  '4. If a reporting clause follows, use a comma (not a full stop) inside the inverted comma.',
  '5. New speaker, new line.'
];
rules.forEach((r, i) => {
  slide.addText(r, {
    x: 0.25, y: cy + 0.28 + i * 0.185, w: 7.0, h: 0.20,
    fontSize: 9, fontFace: FONT_L, color: BLACK, margin: 0
  });
});

// ── Dashed separator ────────────────────────────────────────────────
cy += 1.22 + 0.15;
slide.addShape(pptx.ShapeType.line, {
  x: 0.1, y: cy, w: 7.3, h: 0,
  line: { color: 'AAAAAA', width: 0.5, dashType: 'dash' }
});
cy += 0.12;

// ── Activity 1: Punctuate the exchange ──────────────────────────────
slide.addText('Activity 1: Punctuate this exchange between Varjak and Holly.', {
  x: 0.15, y: cy, w: 7.2, h: 0.24,
  fontSize: 11, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
});
cy += 0.26;
slide.addText('Add inverted commas, capital letters, correct punctuation and paragraph breaks.', {
  x: 0.15, y: cy, w: 7.2, h: 0.20,
  fontSize: 9.5, fontFace: FONT_C, italic: true, color: '555555', margin: 0
});
cy += 0.24;

// Unpunctuated exchange — printed in a lightly shaded box
slide.addShape(pptx.ShapeType.rect, {
  x: 0.15, y: cy, w: 7.2, h: 1.72,
  fill: { color: 'F5F5F5' }, line: { color: 'CCCCCC', width: 0.5 }
});
const exchange = [
  'hello said a voice from above. where are you going.',
  'Varjak looked up. nowhere he said. just looking.',
  'you new here asked the cat. i have not seen you before.',
  'yes said Varjak. i only came outside tonight.',
  'the cat dropped down beside him. i am Holly she said. what are you called.',
  'Varjak said Varjak. i am looking for a dog.',
  'Holly stared at him. a dog she said. you have more courage than sense.'
];
exchange.forEach((ln, i) => {
  slide.addText(ln, {
    x: 0.25, y: cy + 0.08 + i * 0.225, w: 7.0, h: 0.22,
    fontSize: 9.5, fontFace: FONT_C, color: '333333', italic: true, margin: 0
  });
});
cy += 1.72 + 0.15;

// ── Dashed separator ────────────────────────────────────────────────
slide.addShape(pptx.ShapeType.line, {
  x: 0.1, y: cy, w: 7.3, h: 0,
  line: { color: 'AAAAAA', width: 0.5, dashType: 'dash' }
});
cy += 0.14;

// ── Activity 2: Write own dialogue ──────────────────────────────────
slide.addText('Activity 2: Write your own dialogue.', {
  x: 0.15, y: cy, w: 7.2, h: 0.24,
  fontSize: 11, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
});
cy += 0.26;
slide.addText('Varjak meets a cat for the first time. Write three or four lines of dialogue.\nAt least one speech line must have a reporting clause after it.', {
  x: 0.15, y: cy, w: 7.2, h: 0.38,
  fontSize: 9.5, fontFace: FONT_C, italic: true, color: '555555', margin: 0
});
cy += 0.42;

// Writing lines
const linesRemaining = Math.floor((SLIDE_H - cy - 0.15) / LINE_H);
for (let i = 0; i < linesRemaining; i++) {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.15, y: cy + i * LINE_H, w: 7.2, h: 0,
    line: { color: '888888', width: 0.5 }
  });
}

pptx.writeFile({ fileName: OUT }).then(() => console.log('LP written:', OUT));
