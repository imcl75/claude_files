// generate_geo_lps_v2.js — T6W4 Geography LPs, fixed label + ruled lines
const PptxGenJS   = require('pptxgenjs');
const fs          = require('fs');
const path        = require('path');
const { execSync } = require('child_process');

// ── Layout validator (python) ─────────────────────────────────────────
function validateLayout(pptxPath) {
  const validator = '/home/claude/validate_pptx_layout.py';
  if (!fs.existsSync(validator)) {
    console.log('  [validate] validator not found — skipping');
    return;
  }
  try {
    execSync(`python3 "${validator}" "${pptxPath}" --warnings`, { stdio: 'inherit' });
  } catch(e) {
    // exit code 0 = clean; non-zero only if --strict. Warnings/errors are printed to stdout.
  }
}

const ASSETS = '/home/claude';
const OUT    = '/home/claude';

const CM   = 1 / 2.54;
const SW   = 7.5;
const SH   = 10.833;

const LLW  = 9.7  * CM * 0.72;   // ~2.748"
const LLH  = 4.24 * CM * 0.72;   // ~1.200"
const LS   = 0.8 * CM;           // 8mm line spacing = 0.315"

const FL    = 'Twinkl Cursive Looped';
const FA    = 'Aptos';
const GREEN = '4FAD5B';
const BLACK = '000000';
const BLUE  = '1798d3';
const GREY  = 'AAAAAA';
const PBLUE = 'BDD7EE';   // pale blue for ruled lines — matches exercise books
const PLBW  = 0.6;        // line weight for ruled lines (pt)

const M  = 0.35;
const CX = M;
const CW = SW - 2*M;

// ── 1. Label — single combined text box, shrinkText ──────────────────
function addLabel(slide, opts) {
  const { date, keyQ, lf, ic1, ic2 } = opts;
  const x = SW - M - LLW;
  const y = M;

  // Icon
  let iconW = 0.32, iconH = 0.32;
  try {
    const buf = fs.readFileSync(path.join(ASSETS, 'geographer.png'));
    const iw  = buf.readUInt32BE(16);
    const ih  = buf.readUInt32BE(20);
    const r   = iw / ih;
    const mx  = 0.32;
    if (r >= 1) { iconW = mx; iconH = mx / r; }
    else        { iconH = mx; iconW = mx * r; }
  } catch(e) {}

  const iconX = x + LLW - iconW - 0.02;
  const iconY = y + 0.02;
  slide.addImage({ path: path.join(ASSETS, 'geographer.png'), x: iconX, y: iconY, w: iconW, h: iconH });

  // "geographer" text under icon
  slide.addText('geographer', {
    x: iconX - 0.12, y: iconY + iconH, w: iconW + 0.24, h: 0.13,
    fontSize: 5.5, fontFace: FA, align: 'center', color: BLACK, margin: 0
  });

  // Date (right-aligned, to left of icon)
  slide.addText(date, {
    x: iconX - 0.72, y: iconY + 0.01, w: 0.68, h: 0.13,
    fontSize: 6, fontFace: FA, align: 'right', color: BLACK, margin: 0
  });

  // ── Combined label content — ONE text box, shrinkText ──────────────
  // Using breakLine between runs to force paragraph breaks
  const tx  = x + 0.04;
  const tw  = LLW - iconW - 0.22;   // text width left of icon
  const ty  = y + 0.08;
  const th  = LLH - 0.08;           // fill the remaining label height

  slide.addText([
    { text: 'Key Question',     options: { bold: true, underline: { style: 'sng' }, breakLine: true } },
    { text: keyQ,               options: { bold: true, underline: { style: 'sng' }, breakLine: true } },
    { text: 'LF: ' + lf,       options: { breakLine: true } },
    { text: 'I can ' + ic1,    options: { breakLine: true } },
    { text: 'I can ' + ic2,    options: {} },
  ], {
    x: tx, y: ty, w: tw, h: th,
    fontSize: 6.5,
    fontFace: FA,
    color: BLACK,
    valign: 'top',
    margin: 0,
    shrinkText: true,
    autoFit: false,
  });
}

// ── 2. Pale blue ruled lines (exercise book style) ────────────────────
// Always white background first, then pale blue lines on top.
function ruledLines(slide, x, y, w, nLines) {
  // Explicit white background so no inherited tint shows through
  slide.addShape('rect', {
    x, y: y - 0.04, w, h: nLines * LS + 0.08,
    fill: { color: 'FFFFFF' },
    line: { type: 'none' }
  });
  for (let i = 0; i < nLines; i++) {
    slide.addShape('line', {
      x, y: y + i * LS, w, h: 0,
      line: { color: PBLUE, width: PLBW }
    });
  }
  return y + nLines * LS;
}

// ── 3. Separator ──────────────────────────────────────────────────────
function sep(slide, y, style) {
  const st = style || 'dash';
  slide.addShape('line', { x: CX, y, w: CW, h: 0,
    line: { color: GREY, width: 0.6, dashType: st } });
  return y + 0.1;
}

// ── 4. Section heading ────────────────────────────────────────────────
function secHead(slide, text, x, y, w) {
  slide.addText(text, { x, y, w, h: 0.24,
    fontSize: 11, fontFace: FL, bold: true, color: BLUE, margin: 0 });
  return y + 0.26;
}

// ── 5. Question text ──────────────────────────────────────────────────
function qText(slide, text, x, y, w, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h: o.h || 0.27,
    fontSize: o.fs || 11,
    fontFace: o.ff || FL,
    bold:  o.bold  || false,
    color: o.color || BLACK,
    margin: 0, valign: 'top',
  });
  return y + (o.h || 0.27);
}

// ── 6. Answer box (small labelled input box, white fill) ──────────────
function ansBox(slide, x, y, w, h, opts) {
  const o = opts || {};
  slide.addShape('rect', { x, y, w, h,
    fill: { color: o.fill || 'FFFFFF' },
    line: { color: o.border || '888888', width: 0.75 } });
}

// ── 7. Word bank strip ────────────────────────────────────────────────
function wordBank(slide, words, x, y, w) {
  slide.addShape('rect', { x, y, w, h: 0.30,
    fill: { color: 'EEF6FF' }, line: { color: BLUE, width: 0.6 } });
  slide.addText('Word bank:', { x: x+0.08, y: y+0.03, w: 0.70, h: 0.16,
    fontSize: 8, fontFace: FA, bold: true, color: BLUE, margin: 0 });
  slide.addText(words.join('  |  '), { x: x+0.80, y: y+0.05, w: w-0.88, h: 0.22,
    fontSize: 9, fontFace: FL, color: '333333', margin: 0 });
}

// ── 8. Marking station header ─────────────────────────────────────────
function markHead(slide) {
  slide.addText('Marking Station', {
    x: M, y: M, w: 3, h: 0.34,
    fontSize: 18, fontFace: FA, bold: true, color: GREEN, margin: 0 });
  return M + 0.38;
}

// ── 9. Table cell helper ──────────────────────────────────────────────
function tableCell(slide, text, x, y, w, h, opts) {
  const o = opts || {};
  slide.addShape('rect', { x, y, w, h,
    fill: { color: o.fill || 'FFFFFF' },
    line: { color: o.border || 'AAAAAA', width: 0.5 } });
  if (text) {
    slide.addText(text, {
      x: x+0.06, y: y+0.04, w: w-0.10, h: h-0.06,
      fontSize: o.fs || 10, fontFace: o.ff || FL,
      bold: o.bold || false, color: o.color || BLACK,
      margin: 0, valign: 'middle',
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════
// LP 1 — Where in the world is Brazil?  (Tue 23 June)
// ═══════════════════════════════════════════════════════════════════════
async function buildLP1() {
  const pres = new PptxGenJS();
  pres.defineLayout({ name: 'A4P', width: SW, height: SH });
  pres.layout = 'A4P';

  const LABEL = {
    date: '23/06/2026',
    keyQ: 'Are England and Brazil different?',
    lf:   'to locate countries in South America using a map',
    ic1:  'locate Brazil and name four countries that border it',
    ic2:  'write a location description using geographical vocabulary',
  };

  // ── Question slide ──────────────────────────────────────────────────
  const s1 = pres.addSlide();
  addLabel(s1, LABEL);

  let y = M + LLH + 0.08;
  y = sep(s1, y); y += 0.04;

  // PART A
  y = secHead(s1, 'Part A   South American neighbours', CX, y, CW);
  y = qText(s1, 'Name four countries that share a border with Brazil.', CX, y, CW);
  y += 0.06;

  // Four white answer boxes in a row
  const boxW = 1.45, boxH = 0.28, gapX = 0.11;
  for (let i = 0; i < 4; i++) {
    const bx = CX + i*(boxW + gapX);
    ansBox(s1, bx, y, boxW, boxH);
    s1.addText(`${i+1}.`, { x: bx+0.06, y: y+0.05, w: 0.20, h: 0.17,
      fontSize: 9, fontFace: FA, color: BLACK, margin: 0 });
  }
  y += boxH + 0.16;

  y = qText(s1, 'Use compass directions to complete these sentences.', CX, y, CW);
  y += 0.04;
  for (const ln of [
    'Brazil is to the ____________ of Ecuador.',
    'Chile is to the ____________ of Brazil.',
    'Colombia is to the ____________ of Brazil.',
  ]) {
    y = qText(s1, ln, CX+0.1, y, CW-0.1);
    y += 0.04;
  }
  y += 0.10;

  y = sep(s1, y); y += 0.04;

  // PART B
  y = secHead(s1, 'Part B   Location description', CX, y, CW);
  y = qText(s1,
    'Use the sentence starters below. Include at least THREE words from the vocabulary bank. Use the map on the board and your notes to help you.',
    CX, y, CW, { fs: 11, h: 0.48 });
  y += 0.08;

  const starters = [
    'Brazil is located in the _______ hemisphere.',
    'It lies between _______.',
    'Its neighbouring countries include _______.',
    'The time difference between England and Brazil is _______.',
  ];
  for (const stem of starters) {
    y = qText(s1, stem, CX, y, CW);
    y += 0.04;
    y = ruledLines(s1, CX, y, CW - 0.1, 2);
    y += 0.14;
  }

  // ── Marking station ─────────────────────────────────────────────────
  const s2 = pres.addSlide();
  addLabel(s2, LABEL);
  let my = markHead(s2);
  my = sep(s2, my); my += 0.08;

  my = secHead(s2, 'Part A   South American neighbours', CX, my, CW);
  my = qText(s2, 'Name four countries that share a border with Brazil.', CX, my, CW);
  my += 0.06;

  const ans1 = ['Ecuador', 'Chile', 'Bolivia', 'Colombia'];
  for (let i = 0; i < 4; i++) {
    const bx = CX + i*(boxW + gapX);
    ansBox(s2, bx, my, boxW, boxH, { fill: 'E8FFE8', border: GREEN });
    s2.addText(`${i+1}.  ${ans1[i]}`, {
      x: bx+0.06, y: my+0.05, w: boxW-0.1, h: 0.17,
      fontSize: 9, fontFace: FA, bold: true, color: GREEN, margin: 0 });
  }
  my += boxH + 0.14;

  for (const a of [
    'Brazil is to the EAST / SOUTH-EAST of Ecuador.',
    'Chile is to the SOUTH-WEST of Brazil.',
    'Colombia is to the NORTH-WEST of Brazil.',
  ]) {
    my = qText(s2, a, CX+0.1, my, CW-0.1, { color: GREEN, bold: true });
    my += 0.04;
  }
  my += 0.08; my = sep(s2, my); my += 0.04;

  my = secHead(s2, 'Part B   Model answers', CX, my, CW);
  for (const ln of [
    'Brazil is located in the southern hemisphere.',
    'It lies between the Equator and the Tropic of Capricorn.',
    'Its neighbouring countries include Ecuador, Chile, Bolivia and Colombia.',
    'The time difference between England and Brazil is 3 hours — Brazil is GMT-3.',
  ]) {
    my = qText(s2, ln, CX, my, CW, { color: GREEN });
    my += 0.12;
  }

  await pres.writeFile({ fileName: path.join(OUT, 'T6W4_-_LP1_-_Geographers_-_Locating_Brazil.pptx') });
  validateLayout(path.join(OUT, 'T6W4_-_LP1_-_Geographers_-_Locating_Brazil.pptx'));
  console.log('LP1 done');
}

// ═══════════════════════════════════════════════════════════════════════
// LP 2 — Physical geography of Brazil  (Wed 24 June)
// ═══════════════════════════════════════════════════════════════════════
async function buildLP2() {
  const pres = new PptxGenJS();
  pres.defineLayout({ name: 'A4P', width: SW, height: SH });
  pres.layout = 'A4P';

  const LABEL = {
    date: '24/06/2026',
    keyQ: 'Are England and Brazil different?',
    lf:   'to describe the physical geography of Brazil',
    ic1:  'name and describe at least two biomes found in Brazil',
    ic2:  'explain what the tropical climate zone means for Brazil',
  };

  // ── Question slide ──────────────────────────────────────────────────
  const s1 = pres.addSlide();
  addLabel(s1, LABEL);

  let y = M + LLH + 0.08;
  y = sep(s1, y); y += 0.04;

  // PART A — matching
  y = secHead(s1, 'Part A   Key vocabulary', CX, y, CW);
  y = qText(s1, 'Draw a line to match each word to its correct definition.', CX, y, CW);
  y += 0.10;

  const matchWords = ['biome', 'tropical climate zone', 'latitude', 'vegetation belt'];
  const matchDefs  = [
    'The distance north or south of the Equator',
    'A large region with a particular climate, plants and animals',
    'The range of plants found across a geographical area',
    'A warm climate zone between the tropics that experiences high temperatures',
  ];
  const col1W = (CW - 0.18) / 2;
  const col2X = CX + col1W + 0.18;
  const rh    = 0.36;

  for (let i = 0; i < matchWords.length; i++) {
    const rowY = y + i * rh;
    // Left: word box (white)
    ansBox(s1, CX, rowY, col1W-0.05, rh-0.06);
    s1.addText(matchWords[i], {
      x: CX+0.08, y: rowY+0.07, w: col1W-0.16, h: rh-0.14,
      fontSize: 11, fontFace: FL, color: BLACK, margin: 0 });
    // Right: definition box (white)
    ansBox(s1, col2X, rowY, col1W-0.05, rh-0.06);
    s1.addText(matchDefs[i], {
      x: col2X+0.08, y: rowY+0.04, w: col1W-0.16, h: rh-0.08,
      fontSize: 9.5, fontFace: FL, color: BLACK, margin: 0 });
  }
  y += matchWords.length * rh + 0.12;

  y = sep(s1, y); y += 0.04;

  // PART B — paragraph frame
  y = secHead(s1, 'Part B   Physical geography paragraph', CX, y, CW);
  y = qText(s1, 'Complete the paragraph using the word bank below.', CX, y, CW);
  y += 0.04;

  wordBank(s1, ['tropical','warm','heavy','tundra','desert','tropical rainforest','lush','poor','vegetation'], CX, y, CW);
  y += 0.38;

  // Paragraph frame — white background, light border
  const paraLines = [
    'Brazil is mainly in the _____________ climate zone. This means the',
    'country experiences _____________ temperatures and _____________ rainfall.',
    '',
    'The three main biomes found in Brazil are _____________,',
    '_____________ and _____________.',
    '',
    'One important thing to know is that although the rainforest looks very',
    '_____________, the soil is actually _____________. This is because',
    'the nutrients are held in the _____________, not the soil.',
  ];
  const pfH = SH - y - M - 0.04;
  s1.addShape('rect', { x: CX, y, w: CW, h: pfH,
    fill: { color: 'FFFFFF' }, line: { color: 'DDDDDD', width: 0.6 } });

  let py = y + 0.1;
  for (const ln of paraLines) {
    if (ln) {
      py = qText(s1, ln, CX+0.1, py, CW-0.2);
      py += 0.04;
    } else {
      py += 0.10;
    }
  }

  // ── Marking station ─────────────────────────────────────────────────
  const s2 = pres.addSlide();
  addLabel(s2, LABEL);
  let my = markHead(s2);
  my = sep(s2, my); my += 0.08;

  my = secHead(s2, 'Part A   Key vocabulary answers', CX, my, CW);
  for (const [w, d] of [
    ['biome', 'A large region with a particular climate, plants and animals'],
    ['tropical climate zone', 'A warm climate zone between the tropics that experiences high temperatures'],
    ['latitude', 'The distance north or south of the Equator'],
    ['vegetation belt', 'The range of plants found across a geographical area'],
  ]) {
    s2.addText(`${w}  →  ${d}`, {
      x: CX+0.10, y: my, w: CW-0.10, h: 0.26,
      fontSize: 10, fontFace: FL, color: GREEN, bold: true, margin: 0 });
    my += 0.28;
  }
  my += 0.06; my = sep(s2, my); my += 0.04;

  my = secHead(s2, 'Part B   Completed paragraph', CX, my, CW);
  const cText = 'Brazil is mainly in the TROPICAL climate zone. This means the country experiences WARM temperatures and HEAVY rainfall.\n\nThe three main biomes found in Brazil are TROPICAL RAINFOREST, DESERT and TUNDRA.\n\nOne important thing to know is that although the rainforest looks very LUSH, the soil is actually POOR. This is because the nutrients are held in the VEGETATION, not the soil.';
  s2.addText(cText, {
    x: CX+0.1, y: my, w: CW-0.2, h: SH-my-M-0.05,
    fontSize: 11, fontFace: FL, color: GREEN, bold: true,
    margin: 0, valign: 'top', paraSpaceAfter: 6 });

  await pres.writeFile({ fileName: path.join(OUT, 'T6W4_-_LP2_-_Geographers_-_Brazil_Physical_Geography.pptx') });
  validateLayout(path.join(OUT, 'T6W4_-_LP2_-_Geographers_-_Brazil_Physical_Geography.pptx'));
  console.log('LP2 done');
}

// ═══════════════════════════════════════════════════════════════════════
// LP 3 — Physical geography comparison frame  (Fri 26 June)
// ═══════════════════════════════════════════════════════════════════════
async function buildLP3() {
  const pres = new PptxGenJS();
  pres.defineLayout({ name: 'A4P', width: SW, height: SH });
  pres.layout = 'A4P';

  const LABEL = {
    date: '26/06/2026',
    keyQ: 'Are England and Brazil different?',
    lf:   'to compare the physical geography of England and Brazil',
    ic1:  "describe England's biome, climate zone and topography",
    ic2:  'identify at least one similarity and one difference between the two countries',
  };

  const tableRows = [
    ['Feature', 'England', 'Brazil'],
    ['Biome', '', 'Tropical rainforest, desert and tundra'],
    ['Climate zone', '', 'Tropical'],
    ['Topography', '', 'Coastal, highlands and rainforest'],
    ['Seasons', '', 'Wet season and dry season'],
    ['Vegetation', '', 'Lomas, tropical rainforest, high-altitude plants'],
  ];
  const tableH = 3.10;
  const col1W  = 1.30;
  const col2W  = (CW - col1W) / 2;
  const col3W  = CW - col1W - col2W;
  const rowH   = tableH / tableRows.length;

  function drawTable(slide, topY, answers, green) {
    for (let r = 0; r < tableRows.length; r++) {
      const ry  = topY + r * rowH;
      const isH = r === 0;
      const c1bg = isH ? BLUE : 'E8F0FA';
      const c2bg = isH ? BLUE : 'FFFFFF';
      const c3bg = isH ? BLUE : 'FFFBEE';
      const htx  = 'FFFFFF';
      const ans  = answers ? answers[r] : tableRows[r];

      tableCell(slide, ans[0], CX, ry, col1W, rowH,
        { fill: c1bg, color: isH ? htx : '333333', bold: isH, border: 'AAAAAA' });
      tableCell(slide, ans[1], CX+col1W, ry, col2W, rowH,
        { fill: c2bg, color: isH ? htx : (green ? GREEN : BLACK),
          bold: green || isH, border: 'AAAAAA' });
      tableCell(slide, ans[2], CX+col1W+col2W, ry, col3W, rowH,
        { fill: c3bg, color: isH ? htx : '555522', bold: isH, border: 'AAAAAA' });
    }
  }

  // ── Question slide ──────────────────────────────────────────────────
  const s1 = pres.addSlide();
  addLabel(s1, LABEL);

  let y = M + LLH + 0.08;
  y = sep(s1, y); y += 0.04;

  y = qText(s1,
    'Complete the comparison frame. Use the map on the board and your notes to help you.',
    CX, y, CW, { fs: 11 });
  y += 0.08;

  drawTable(s1, y, null, false);
  y += tableH + 0.14;

  y = sep(s1, y); y += 0.04;
  y = secHead(s1, 'Comparison sentences', CX, y, CW);

  y = qText(s1, 'England and Brazil are similar in that...', CX, y, CW);
  y += 0.06;
  y = ruledLines(s1, CX, y, CW - 0.08, 3);
  y += 0.16;

  y = qText(s1, 'However, they are different because...', CX, y, CW);
  y += 0.06;
  y = ruledLines(s1, CX, y, CW - 0.08, 3);
  y += 0.16;

  // Challenge box — amber border, white interior, pale blue lines
  const chalH = SH - y - M - 0.04;
  s1.addShape('rect', { x: CX, y, w: CW, h: chalH,
    fill: { color: 'FFFFFF' }, line: { color: 'DDAA00', width: 0.9 } });
  s1.addText('Challenge:', {
    x: CX+0.10, y: y+0.06, w: 1.0, h: 0.20,
    fontSize: 10, fontFace: FA, bold: true, color: 'AA7700', margin: 0 });
  s1.addText(
    "Which country's physical geography would be more interesting to visit? Give a geographical reason.",
    { x: CX+1.12, y: y+0.06, w: CW-1.20, h: 0.26,
      fontSize: 10, fontFace: FL, color: '553300', margin: 0 });
  ruledLines(s1, CX+0.1, y+0.38, CW-0.2, Math.max(2, Math.floor((chalH - 0.46) / LS)));

  // ── Marking station ─────────────────────────────────────────────────
  const s2 = pres.addSlide();
  addLabel(s2, LABEL);
  let my = markHead(s2);
  my = sep(s2, my); my += 0.08;

  const answers = [
    ['Feature', 'England', 'Brazil'],
    ['Biome', 'Temperate', 'Tropical rainforest, desert and tundra'],
    ['Climate zone', 'Temperate maritime', 'Tropical'],
    ['Topography', 'Coastal, highland, river valleys and flatlands', 'Coastal, highlands and rainforest'],
    ['Seasons', 'Spring, summer, autumn and winter', 'Wet season and dry season'],
    ['Vegetation', 'Mixed deciduous and evergreen woodland', 'Lomas, tropical rainforest, high-altitude plants'],
  ];
  drawTable(s2, my, answers, true);
  my += tableH + 0.14;

  my = sep(s2, my); my += 0.04;
  my = secHead(s2, 'Model comparison sentences', CX, my, CW);

  s2.addText(
    'England and Brazil are similar in that both countries have a varied topography with coastal regions, highlands and river systems.',
    { x: CX, y: my, w: CW, h: 0.36,
      fontSize: 10, fontFace: FL, color: GREEN, bold: true, margin: 0 });
  my += 0.40;
  s2.addText(
    'However, they are different because England has a temperate climate with four seasons, whereas Brazil is in the tropical climate zone and only has a wet season and a dry season.',
    { x: CX, y: my, w: CW, h: 0.44,
      fontSize: 10, fontFace: FL, color: GREEN, bold: true, margin: 0 });

  await pres.writeFile({ fileName: path.join(OUT, 'T6W4_-_LP3_-_Geographers_-_England_Comparison_Frame.pptx') });
  validateLayout(path.join(OUT, 'T6W4_-_LP3_-_Geographers_-_England_Comparison_Frame.pptx'));
  console.log('LP3 done');
}

// ── Run ───────────────────────────────────────────────────────────────
(async () => {
  try {
    await buildLP1();
    await buildLP2();
    await buildLP3();
    console.log('\nAll LPs built.');
  } catch(e) {
    console.error(e);
    process.exit(1);
  }
})();
