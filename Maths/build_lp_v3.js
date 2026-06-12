/**
 * build_lp_v3.js — Generalised LP builder
 * Usage: node build_lp_v3.js <lesson_number>   (1–20)
 *
 * Reads label text from maths_plan_v3.json.
 * Reads LP grid data and adapted support from lesson_data.js.
 */

const PptxGenJS  = require("pptxgenjs");
const { createCanvas, loadImage } = require("canvas");
const fs   = require("fs");
const path = require("path");

// ─── Lesson number ────────────────────────────────────────────────────────────
const LESSON_NUM = parseInt(process.argv[2] || "1", 10);

// ─── Load JSON plan ───────────────────────────────────────────────────────────
const PLAN       = JSON.parse(fs.readFileSync("/home/claude/transfer_files/maths_plan_v3.json", "utf8"));
const LESSON     = PLAN.lessons[LESSON_NUM - 1];
if (!LESSON || LESSON.lesson !== LESSON_NUM)
  throw new Error(`Lesson ${LESSON_NUM} not found in JSON`);

console.log(`Building LP ${LESSON_NUM}: ${LESSON.day} (${LESSON.topic})`);

// ─── Load authored lesson data ────────────────────────────────────────────────
const LESSON_DATA = require("/home/claude/lesson_data.js");
const ld = LESSON_DATA[LESSON_NUM];
if (!ld) throw new Error(`No authored LP data for lesson ${LESSON_NUM} in lesson_data.js`);

// ─── Constants ────────────────────────────────────────────────────────────────
const ASSETS  = "/home/claude/lp_assets";
const CM      = 1 / 2.54;
const SLIDE_W = 7.5;
const SLIDE_H = 10.833;
const MID_Y   = SLIDE_H / 2;
const CUT_GAP = 0.12;
const MARGIN  = 0.25;
const GUTTER  = 0.30;

const GREEN  = "4FAD5B";
const BLACK  = "000000";
const GREY   = "AAAAAA";
const BLUE   = "1F4E79";
const RED    = "C00000";
const PURPLE = "7030A0";
const FONT_C = "Twinkl Cursive Looped";
const FONT_M = "Aptos";

const LABEL_SCALE = 0.72 * 0.85;
const LL_W = 9.7 * CM * LABEL_SCALE;
const LL_H = 4.24 * CM * LABEL_SCALE;

// Date: use today formatted as DD/MM/YYYY
const _d = new Date();
const TODAY = `${String(_d.getDate()).padStart(2,'0')}/${String(_d.getMonth()+1).padStart(2,'0')}/${_d.getFullYear()}`;

// ─── Label content from JSON ─────────────────────────────────────────────────
const lo    = LESSON.loText;
const lp1   = LESSON.lp1;
const lp1Topic = lp1.topic;
// LF line: first sentence of li
const lfLine = LESSON.li.replace(/\.$/, '').toLowerCase();
// I can statements derived from iwstb — split on comma/and
const iwstb = lo.iwstb.replace(/^…/, '');
// Use lp1 topic area for the maths label topic line
const LABEL_TOPIC   = lp1Topic;
const LABEL_LF      = `LF: ${lfLine}`;
const LABEL_ICAN    = ld.iCan || [
  `I can ${iwstb.split(',')[0].trim()}`,
  `I can ${(iwstb.split(',')[1] || iwstb.split(' and ')[1] || 'check my work').trim()}`,
];

// ─── LP data from lesson_data.js ─────────────────────────────────────────────
const LP1_DATA       = ld.lp1;
const LP2_DATA       = ld.lp2;
const ADAPTED_SUPPORT = ld.adaptedSupport;

// Output filename
const outFile = `/home/claude/${LESSON.week}_L${LESSON_NUM}_LP.pptx`;


// ─── Maths label PNG ─────────────────────────────────────────────────────────
async function renderMathsLabel() {
  const DPI = 300;
  const wCm = 9.7 * 0.72 * 0.85;
  const hCm = 4.24 * 0.72 * 0.85;
  const cW  = Math.round(wCm * DPI / 2.54);
  const cH  = Math.round(hCm * DPI / 2.54);
  const cv  = createCanvas(cW, cH);
  const ctx = cv.getContext("2d");

  // Word-wrap helper: splits text into lines that fit within maxW pixels
  function wrapText(text, maxW) {
    const words = text.split(' ');
    const lines = [];
    let line = '';
    for (const word of words) {
      const test = line ? line + ' ' + word : word;
      if (ctx.measureText(test).width > maxW && line) {
        lines.push(line);
        line = word;
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    return lines;
  }

  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, cW, cH);

  const icon  = await loadImage(path.join(ASSETS, "mathematician.png"));
  const iconW = cW * 0.11;
  const iconH = iconW * (icon.height / icon.width);
  ctx.drawImage(icon, cW * 0.02, cH * 0.04, iconW, iconH);

  ctx.font = `${Math.round(cH * 0.09)}px sans-serif`;
  ctx.fillStyle = "#000000"; ctx.textAlign = "right";
  ctx.fillText(TODAY, cW * 0.97, cH * 0.14);

  const maxTextW = cW * 0.94;   // leave 3% margin each side
  const textX    = cW * 0.03;

  const topicY  = iconH + cH * 0.18;
  const topicSz = Math.round(cH * 0.088);
  ctx.font = `bold ${topicSz}px sans-serif`;
  ctx.textAlign = "left"; ctx.fillStyle = "#000000";
  // Topic may also be long — wrap it too
  const topicLines = wrapText(LABEL_TOPIC, maxTextW);
  topicLines.forEach((line, i) => ctx.fillText(line, textX, topicY + i * topicSz * 1.2));
  const tw = ctx.measureText(topicLines[0]).width;  // underline first line only
  ctx.beginPath();
  ctx.moveTo(textX, topicY + 2);
  ctx.lineTo(textX + tw, topicY + 2);
  ctx.lineWidth = 1.5; ctx.stroke();

  const topicBlockH = topicLines.length * topicSz * 1.2;

  const sm = Math.round(cH * 0.083);
  ctx.font = `${sm}px sans-serif`;
  const lg = sm * 1.55;   // line height based on font size, not canvas height
  let textY = topicY + topicBlockH + lg * 0.4;

  // LF line — wrap if needed
  const lfLines = wrapText(LABEL_LF, maxTextW);
  lfLines.forEach(line => { ctx.fillText(line, textX, textY); textY += lg; });

  // I can 1 — wrap if needed
  const ic1Lines = wrapText(LABEL_ICAN[0], maxTextW);
  ic1Lines.forEach(line => { ctx.fillText(line, textX, textY); textY += lg; });

  // I can 2 — wrap if needed
  const ic2Lines = wrapText(LABEL_ICAN[1], maxTextW);
  ic2Lines.forEach(line => { ctx.fillText(line, textX, textY); textY += lg; });

  const out = `/home/claude/maths_label_L${LESSON_NUM}.png`;
  fs.writeFileSync(out, cv.toBuffer("image/png"));
  return out;
}

// ─── Grid drawing ─────────────────────────────────────────────────────────────
// Returns { panelH, totalH }
//   panelH = height of the white grid panel itself
//   totalH = panelH + axis label overhang below
function drawGrid(slide, gx, gy, panelW, cols, rows, points) {
  const cell   = panelW / cols;          // cell size driven by width
  const panelH = cell * rows;
  const numSz  = Math.max(5, Math.round(cell * 24));
  const numH   = numSz / 72 + 0.04;     // approx height of axis number row

  // White panel
  slide.addShape("rect", {
    x: gx, y: gy, w: panelW, h: panelH,
    fill: { color: "FFFFFF" }, line: { color: "CCCCCC", width: 0.4 }
  });

  // Grid lines
  for (let c = 0; c <= cols; c++) {
    slide.addShape("line", {
      x: gx + c*cell, y: gy, w: 0, h: panelH,
      line: { color: "CCCCCC", width: 0.3 }
    });
  }
  for (let r = 0; r <= rows; r++) {
    slide.addShape("line", {
      x: gx, y: gy + r*cell, w: panelW, h: 0,
      line: { color: "CCCCCC", width: 0.3 }
    });
  }

  // X-axis numbers (below grid)
  for (let c = 0; c <= cols; c++) {
    slide.addText(String(c), {
      x: gx + c*cell - 0.06, y: gy + panelH + 0.01,
      w: 0.12, h: numH,
      fontSize: numSz, fontFace: FONT_M, align: "center", color: "555555", margin: 0
    });
  }

  // Y-axis numbers (left of grid)
  const yLabelW = 0.14;
  for (let r = 0; r <= rows; r++) {
    slide.addText(String(rows - r), {
      x: gx - yLabelW - 0.02, y: gy + r*cell - numH/2,
      w: yLabelW, h: numH,
      fontSize: numSz, fontFace: FONT_M, align: "right", color: "555555", margin: 0
    });
  }

  // Points
  const dotR = Math.min(0.060, cell * 0.22);
  for (const [col, row, label, col6] of points) {
    const px = gx + col * cell;
    const py = gy + (rows - row) * cell;
    slide.addShape("ellipse", {
      x: px - dotR, y: py - dotR, w: dotR*2, h: dotR*2,
      fill: { color: col6 || BLUE }, line: { color: col6 || BLUE, width: 0 }
    });
    if (label) {
      slide.addText(label, {
        x: px + dotR*0.3, y: py - dotR*2.2 - numH*0.6,
        w: 0.18, h: numH * 1.1,
        fontSize: numSz + 1, fontFace: FONT_M, bold: true,
        color: col6 || BLUE, margin: 0
      });
    }
  }

  return { panelH, totalH: panelH + numH + 0.04 };
}

// ─── Route arrow ─────────────────────────────────────────────────────────────
// Draws a two-segment dashed route on the grid: A → corner → B
// segments: array of [x1,y1,x2,y2] in grid coords (col,row values)
// gx,gy: top-left of the grid panel; cell: cell size in inches; rows: total rows
function drawRoute(slide, gx, gy, cell, rows, segments) {
  const ROUTE_COLOR = "156082";
  const ROUTE_W = 0.9;

  segments.forEach(([c1, r1, c2, r2], idx) => {
    // Actual slide coordinates of start (A-side) and end (tip/arrow-side)
    const sx = gx + c1 * cell;
    const sy = gy + (rows - r1) * cell;
    const tx = gx + c2 * cell;
    const ty = gy + (rows - r2) * cell;

    const isLast = idx === segments.length - 1;

    // For lines in pptxgenjs, x/y/w/h define a bounding box.
    // The line runs from (x,y) to (x+w, y+h) UNLESS flipped.
    // flipH mirrors horizontally (swaps left/right ends).
    // flipV mirrors vertically (swaps top/bottom ends).
    //
    // To put an endArrowType at the tip (tx,ty), we need the line to
    // naturally end there. Simplest: always put tip at bottom-right of
    // bounding box (no flipping needed for endArrow), and flip when tip
    // is at top-left.
    //
    // Natural end = bottom-right = (lx+lw, ly+lh).
    // If tip IS bottom-right: no flip, use endArrowType.
    // If tip is bottom-left: flipH, use endArrowType.
    // If tip is top-right:   flipV, use endArrowType.
    // If tip is top-left:    flipH+flipV, use endArrowType.

    const lx = Math.min(sx, tx);
    const ly = Math.min(sy, ty);
    const lw = Math.abs(tx - sx) || 0.001;
    const lh = Math.abs(ty - sy) || 0.001;

    // Is tip at the right side of the bounding box?
    const tipIsRight  = tx >= sx;
    // Is tip at the bottom of the bounding box?
    const tipIsBottom = ty >= sy;

    slide.addShape("line", {
      x: lx, y: ly, w: lw, h: lh,
      flipH: !tipIsRight,
      flipV: !tipIsBottom,
      line: {
        color: ROUTE_COLOR,
        width: ROUTE_W,
        dashType: "dash",
        ...(isLast ? { endArrowType: "arrow" } : {})
      }
    });
  });
}

// ─── Answer line ─────────────────────────────────────────────────────────────
// Returns height consumed (label + line)
function addAnswerSection(slide, x, y, w, labelText, answer) {
  const labelH = 0.16;
  const lineGap = 0.06;
  if (labelText) {
    slide.addText(labelText, {
      x, y, w, h: labelH,
      fontSize: 8, fontFace: FONT_C, color: "333333", margin: 0
    });
  }
  const lineY = y + (labelText ? labelH + lineGap : 0.10);
  slide.addShape("line", { x, y: lineY, w, h: 0, line: { color: BLACK, width: 0.6 } });
  if (answer) {
    // Text sits ON the line — position so baseline aligns with the line
    const ansH = 0.18;
    slide.addText(answer, {
      x, y: lineY - ansH + 0.02, w, h: ansH,
      fontSize: 8.5, fontFace: FONT_C, bold: true, color: "156082",
      valign: "bottom", margin: 0
    });
  }
  return (labelText ? labelH + lineGap : 0.10) + 0.02;
}

// ─── Glue here ───────────────────────────────────────────────────────────────
function addGlueHere(slide, halfTopY, halfH) {
  slide.addText("✂  Glue here", {
    x: SLIDE_W - 0.26, y: halfTopY + 0.20,
    w: halfH - 0.40, h: 0.20,
    fontSize: 6, fontFace: FONT_M, color: GREY,
    align: "center", margin: 0, rotate: 90
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// TOP HALF — dispatch based on LP type
// ─────────────────────────────────────────────────────────────────────────────
function buildLP1(slide, labelPath, isMarkingStation) {
  if (LP1_DATA.type === 'polygon_translation') {
    return buildLP1Polygon(slide, labelPath, isMarkingStation);
  }
  buildLP1Directions(slide, labelPath, isMarkingStation);
}

function buildLP2(slide, isMarkingStation) {
  if (LP2_DATA.type === 'polygon_translation') {
    return buildLP2Polygon(slide, isMarkingStation);
  }
  buildLP2Journeys(slide, isMarkingStation);
}


function buildLP1Directions(slide, labelPath, isMarkingStation) {
  const HALF_TOP  = MARGIN;
  const HALF_BOT  = MID_Y - CUT_GAP;
  const HALF_H    = HALF_BOT - HALF_TOP;

  // Right column anchor — same width as label
  const lblX = SLIDE_W - LL_W - MARGIN;
  const lblY = HALF_TOP;

  // Fixed grid dimensions: 5×5, gridPanelW=1.55"
  const yLabelGutter = 0.18;
  const gridPanelW   = 1.55;
  const cols = 5, rows = 5;
  const cell = gridPanelW / cols;     // 0.31"
  const numH = Math.max(5, Math.round(cell * 24)) / 72 + 0.04;

  const col2X = MARGIN + gridPanelW + yLabelGutter + GUTTER;

  // ── Left/centre: title + questions ────────────────────────────────────────
  let curY = HALF_TOP;

  if (isMarkingStation) {
    const titleW = lblX - GUTTER;
    slide.addText("Marking Station 1", {
      x: MARGIN, y: curY, w: titleW, h: 0.26,
      fontSize: 13, fontFace: FONT_M, bold: true, color: GREEN, margin: 0
    });
    curY += 0.30;
  } else {
    const titleW = lblX - GUTTER;
    slide.addText(LP1_DATA.title || "Directions on a Grid", {
      x: MARGIN, y: curY, w: titleW, h: 0.26,
      fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    curY += 0.28;
    slide.addText(
      "Write the directions from A to B on the line under each grid.  Use: left / right / up / down + steps.",
      { x: MARGIN, y: curY, w: titleW, h: 0.20,
        fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 }
    );
    curY += 0.22;
  }

  const qLabelH   = 0.18;
  const ansH      = 0.28;
  const rowGap    = 0.14;
  const rowH      = qLabelH + cell*rows + numH + 0.04 + ansH;
  const twoRowsH  = rowH * 2 + rowGap;
  const ROW_Y     = [curY, curY + rowH + rowGap];

  LP1_DATA.questions.forEach(({ start, end, answer }, i) => {
    const col   = i % 2;
    const row   = Math.floor(i / 2);
    const gridX = col === 0 ? MARGIN + yLabelGutter : col2X + yLabelGutter;
    let gy = ROW_Y[row];

    slide.addText(`Q${i + 1}`, {
      x: gridX, y: gy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    gy += qLabelH;

    const { totalH } = drawGrid(slide, gridX, gy, gridPanelW, cols, rows, [
      [...start, "A", BLUE],
      [...end,   "B", RED],
    ]);
    gy += totalH;

    addAnswerSection(
      slide, gridX, gy, gridPanelW, "",
      isMarkingStation ? answer : null
    );
  });

  curY += twoRowsH;

  // ── Right column ──────────────────────────────────────────────────────────
  if (!isMarkingStation) {
    // Learning label
    slide.addImage({ path: labelPath, x: lblX, y: lblY, w: LL_W, h: LL_H });

    let rY = lblY + LL_H + 0.10;

    // "Worked Example:" heading
    slide.addText("Worked Example:", {
      x: lblX, y: rY, w: LL_W, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
    });
    rY += 0.22;

    // Worked grid — same 5×5 size, Q1 data
    const { start, end, answer } = LP1_DATA.questions[0];
    const { totalH: wGridH } = drawGrid(slide, lblX, rY, gridPanelW, cols, rows, [
      [...start, "A", BLUE],
      [...end,   "B", RED],
    ]);

    // Route arrow: right 3 then up 2
    const [sc, sr] = start;
    const [ec, er] = end;
    drawRoute(slide, lblX, rY, cell, rows, [
      [sc, sr, ec, sr],   // right to (4,1)
      [ec, sr, ec, er],   // up to (4,3) — arrowhead here
    ]);
    rY += wGridH;

    // Answer ON the line
    addAnswerSection(slide, lblX, rY, gridPanelW, "", answer);
    rY += 0.20;

    // Going further box
    const challengeMaxH = HALF_BOT - rY - 0.08;
    if (challengeMaxH > 0.55) {
      slide.addText("Going further…", {
        x: lblX, y: rY, w: LL_W, h: 0.20,
        fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
      });
      rY += 0.22;
      const boxH = Math.min(challengeMaxH - 0.22, 0.88);
      slide.addText(LP1_DATA.goingFurther ||
        "Can you find two different direction routes that both get from A to B?\n\nDraw both routes on Q1 and write each set of directions.",
        {
          x: lblX, y: rY, w: LL_W, h: boxH,
          fontSize: 8.5, fontFace: FONT_C, color: BLACK,
          fill: { color: "FFFFFF" },
          line: { color: "156082", width: 0.75 },
          margin: 6, valign: "top"
        }
      );
    }
  }

  addGlueHere(slide, HALF_TOP, HALF_H);
}

// ─────────────────────────────────────────────────────────────────────────────
// BOTTOM HALF — LP2: 3 three-stop journeys
// Grid: 6×6 at gridPanelW=1.0" (cell=0.167") — proven to fit in half-A4
// ─────────────────────────────────────────────────────────────────────────────
function buildLP2Journeys(slide, isMarkingStation) {
  const HALF_TOP = MID_Y + CUT_GAP;
  const HALF_BOT = SLIDE_H - MARGIN;
  const HALF_H   = HALF_BOT - HALF_TOP;

  // Right column — same anchor as LP1
  const lblX  = SLIDE_W - LL_W - MARGIN;
  const rColW = LL_W;

  // Grid: 6×6, gridPanelW=1.0"
  const gridPanelW   = 1.0;
  const yLabelGutter = 0.16;
  const gridX        = MARGIN + yLabelGutter;
  const cols = 6, rows = 6;
  const cell = gridPanelW / cols;
  const numH = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const totalGridH   = cell * rows + numH + 0.03;

  // Answer column for main questions: between grid and right column
  const ansColX = gridX + gridPanelW + 0.18;
  const ansColW = lblX - ansColX - 0.10;

  const legLabelH  = 0.14;
  const legLineGap = 0.04;
  const legAnswerH = 0.14;
  const legH       = legLabelH + legLineGap + legAnswerH;
  const twoLegsH   = legH * 2 + 0.08;
  const qLabelH    = 0.16;
  const qBlockH    = Math.max(qLabelH + totalGridH, qLabelH + twoLegsH) + 0.03;
  const qGap       = 0.08;

  let curY = HALF_TOP;

  if (isMarkingStation) {
    slide.addText("Marking Station 2", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
      fontSize: 13, fontFace: FONT_M, bold: true, color: GREEN, margin: 0
    });
    curY += 0.26;
  } else {
    slide.addText(LP2_DATA.title || "Three-Stop Journeys", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
      fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    curY += 0.26;
    slide.addText(
      LP2_DATA.instruction || "Each journey visits A → B → C.  Write the directions for each leg.",
      { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
        fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 }
    );
    curY += 0.20;
  }

  // Helper: one leg row — label left, answer inline after it, line below the whole row
  // labelW: width reserved for the label text
  // totalW: full width of the row
  // answer: null = blank line, string = show answer in given color
  const LEG_ROW_H    = 0.18;   // text height
  const LEG_LINE_GAP = 0.05;   // gap between text and underline
  const LEG_LABEL_W  = 0.62;   // "Leg 1 (A→B): " width at 8pt

  function addLegRow(x, y, totalW, labelText, answer, answerColor) {
    // Label
    slide.addText(labelText, {
      x, y, w: LEG_LABEL_W, h: LEG_ROW_H,
      fontSize: 8, fontFace: FONT_C, bold: true, color: BLACK,
      valign: "bottom", margin: 0
    });
    // Answer inline (starts after label)
    if (answer) {
      slide.addText(answer, {
        x: x + LEG_LABEL_W, y, w: totalW - LEG_LABEL_W, h: LEG_ROW_H,
        fontSize: 8.5, fontFace: FONT_C, bold: true, color: answerColor || GREEN,
        valign: "bottom", margin: 0
      });
    }
    // Underline below the whole row
    const lineY = y + LEG_ROW_H + LEG_LINE_GAP;
    slide.addShape("line", { x, y: lineY, w: totalW, h: 0,
      line: { color: BLACK, width: 0.6 } });
    return LEG_ROW_H + LEG_LINE_GAP;  // height consumed to line (caller adds gap after)
  }

  LP2_DATA.questions.forEach(({ pts, a1, a2 }, i) => {
    slide.addText(`Q${i + 1}`, {
      x: MARGIN, y: curY, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });

    drawGrid(slide, gridX, curY + qLabelH, gridPanelW, cols, rows, pts);

    let aY = curY + qLabelH;

    aY += addLegRow(ansColX, aY, ansColW, "Leg 1 (A→B):",
      isMarkingStation ? a1 : null, GREEN) + 0.10;

    addLegRow(ansColX, aY, ansColW, "Leg 2 (B→C):",
      isMarkingStation ? a2 : null, GREEN);

    curY += qBlockH + qGap;

    if (i < LP2_DATA.questions.length - 1) {
      slide.addShape("line", {
        x: MARGIN, y: curY - qGap / 2,
        w: lblX - MARGIN - 0.10, h: 0,
        line: { color: "DDDDDD", width: 0.4, dashType: "dash" }
      });
    }
  });

  // ── Right column: LP2 worked example ──────────────────────────────────────
  if (!isMarkingStation) {
    let rY = HALF_TOP;

    slide.addText("Worked Example:", {
      x: lblX, y: rY, w: rColW, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
    });
    rY += 0.22;

    // Q1 worked grid
    const { pts, a1, a2 } = LP2_DATA.questions[0];
    drawGrid(slide, lblX, rY, gridPanelW, cols, rows, pts);

    // Route segments — driven by Q1 points
    const [pA, pB, pC] = LP2_DATA.questions[0].pts;
    const drawSeg = (c1, r1, c2, r2, arrowhead, color) => {
      const sx = lblX + c1 * cell, sy = rY + (rows - r1) * cell;
      const tx = lblX + c2 * cell, ty = rY + (rows - r2) * cell;
      slide.addShape("line", {
        x: Math.min(sx,tx), y: Math.min(sy,ty),
        w: Math.abs(tx-sx)||0.001, h: Math.abs(ty-sy)||0.001,
        flipH: tx < sx, flipV: ty < sy,
        line: { color, width: 0.8, dashType: "dash",
          ...(arrowhead ? { endArrowType: "arrow" } : {}) }
      });
    };
    // Leg 1: A→corner→B (go right then up/down)
    drawSeg(pA[0], pA[1], pB[0], pA[1], false, "156082");
    drawSeg(pB[0], pA[1], pB[0], pB[1], true,  "156082");
    // Leg 2: B→corner→C
    drawSeg(pB[0], pB[1], pC[0], pB[1], false, "7030A0");
    drawSeg(pC[0], pB[1], pC[0], pC[1], true,  "7030A0");

    rY += totalGridH + 0.06;

    // Leg 1 — label inline with answer, line below
    rY += addLegRow(lblX, rY, rColW, "Leg 1 (A→B):", a1, "156082") + 0.12;

    // Leg 2
    addLegRow(lblX, rY, rColW, "Leg 2 (B→C):", a2, "7030A0");
    rY += LEG_ROW_H + LEG_LINE_GAP + 0.12;

    // Going further box — matches LP1 style
    const challengeMaxH = HALF_BOT - rY - 0.08;
    if (challengeMaxH > 0.55) {
      slide.addText("Going further…", {
        x: lblX, y: rY, w: rColW, h: 0.20,
        fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
      });
      rY += 0.22;
      const boxH = Math.min(challengeMaxH - 0.22, 0.88);
      slide.addText(LP2_DATA.goingFurther ||
        "For one journey, describe the return route from C back to A.",
        {
          x: lblX, y: rY, w: rColW, h: boxH,
          fontSize: 8.5, fontFace: FONT_C, color: BLACK,
          fill: { color: "FFFFFF" },
          line: { color: "156082", width: 0.75 },
          margin: 6, valign: "top"
        }
      );
    }
  }

  addGlueHere(slide, HALF_TOP, HALF_H);
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPASS — directional aid for adapted LP
// Draws a four-arm compass cross centred at (cx, cy) within a pale box
// boxX, boxY, boxW, boxH: bounding box for the whole aid
// ─────────────────────────────────────────────────────────────────────────────
function drawCompass(slide, boxX, boxY, boxW, boxH) {
  // Pale background box
  slide.addShape("rect", {
    x: boxX, y: boxY, w: boxW, h: boxH,
    fill: { color: "DEECF8" },
    line: { color: "156082", width: 0.75 }
  });

  const cx = boxX + boxW / 2;
  const cy = boxY + boxH / 2;
  const arm   = Math.min(boxW, boxH) * 0.28;   // arm length from centre
  const lblOff = arm + 0.10;                    // label offset from centre
  const lblW  = 0.36;
  const lblH  = 0.18;
  const lblSz = 9;
  const ARROW_COLOR = "156082";
  const ARROW_W     = 1.2;

  // Draw one arm: arrowhead points away from centre toward (tx,ty)
  // Strategy: draw line from centre to tip; arrowhead is endArrowType
  // For pptxgenjs lines, the "end" is determined by flipH/flipV on the bounding box.
  // Simplest reliable approach: always draw tip→centre so endArrow lands at tip.
  function arm2(tx, ty) {
    // tip is at (tx,ty), base at centre (cx,cy)
    // endArrowType lands at bottom-right of bbox; flip to move it to tip
    slide.addShape("line", {
      x: Math.min(cx,tx), y: Math.min(cy,ty),
      w: Math.abs(tx-cx)||0.001, h: Math.abs(ty-cy)||0.001,
      flipH: tx < cx, flipV: ty < cy,
      line: { color: ARROW_COLOR, width: ARROW_W, endArrowType: "arrow" }
    });
  }

  // Four arms
  arm2(cx - arm, cy);  // left
  arm2(cx + arm, cy);  // right
  arm2(cx, cy - arm);  // up   (tip is at lower y = visually up)
  arm2(cx, cy + arm);  // down (tip is at higher y = visually down)

  // Small centre dot
  const dotR = 0.04;
  slide.addShape("ellipse", {
    x: cx - dotR, y: cy - dotR, w: dotR*2, h: dotR*2,
    fill: { color: ARROW_COLOR }, line: { color: ARROW_COLOR, width: 0 }
  });

  // Labels
  const labels = [
    { text: "left",  x: cx - lblOff - lblW, y: cy - lblH/2 },
    { text: "right", x: cx + lblOff,         y: cy - lblH/2 },
    { text: "up",    x: cx - lblW/2,          y: cy - lblOff - lblH },
    { text: "down",  x: cx - lblW/2,          y: cy + lblOff },
  ];
  labels.forEach(({ text, x, y }) => {
    slide.addText(text, {
      x, y, w: lblW, h: lblH,
      fontSize: lblSz, fontFace: FONT_C, bold: true,
      color: ARROW_COLOR, align: "center", margin: 0
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// ADAPTED LP1 — compass replaces top row; 2 questions; helpful hint box
// support: { hint: "..." } — hint text for the right column box
// ─────────────────────────────────────────────────────────────────────────────
function buildLP1Adapted(slide, labelPath) {
  if (LP1_DATA.type === 'polygon_translation') {
    return buildLP1PolygonAdapted(slide, labelPath);
  }
  buildLP1DirectionsAdapted(slide, labelPath);
}

function buildLP2Adapted(slide) {
  if (LP2_DATA.type === 'polygon_translation') {
    return buildLP2PolygonAdapted(slide);
  }
  buildLP2JourneysAdapted(slide);
}

function buildLP1DirectionsAdapted(slide, labelPath) {
  const HALF_TOP  = MARGIN;
  const HALF_BOT  = MID_Y - CUT_GAP;
  const HALF_H    = HALF_BOT - HALF_TOP;

  const lblX = SLIDE_W - LL_W - MARGIN;
  const lblY = HALF_TOP;

  const yLabelGutter = 0.18;
  const gridPanelW   = 1.55;
  const cols = 5, rows = 5;
  const cell = gridPanelW / cols;
  const numH = Math.max(5, Math.round(cell * 24)) / 72 + 0.04;
  const col2X = MARGIN + gridPanelW + yLabelGutter + GUTTER;

  // Use adapted questions from lesson_data
  const LP1_ADAPTED = ADAPTED_SUPPORT.lp1Questions;

  const qLabelH = 0.18;
  const ansH    = 0.28;
  const rowH    = qLabelH + cell*rows + numH + 0.04 + ansH;

  let curY = HALF_TOP;

  // Title + instruction
  const titleW = lblX - GUTTER;
  slide.addText(LP1_DATA.title || "Directions on a Grid", {
    x: MARGIN, y: curY, w: titleW, h: 0.26,
    fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
  });
  curY += 0.28;
  slide.addText(
    "Write the directions from A to B on the line under each grid.  Use: left / right / up / down + steps.",
    { x: MARGIN, y: curY, w: titleW, h: 0.20,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 }
  );
  curY += 0.22;

  // ── Compass support box — takes one full row height ────────────────────────
  const compassBoxW = lblX - MARGIN - GUTTER;
  drawCompass(slide, MARGIN, curY, compassBoxW, rowH);
  curY += rowH + 0.10;

  // ── Two questions (side by side, same column layout) ──────────────────────
  LP1_ADAPTED.forEach(({ start, end, answer }, i) => {
    const gridX = i === 0 ? MARGIN + yLabelGutter : col2X + yLabelGutter;
    let gy = curY;

    slide.addText(`Q${i + 1}`, {
      x: gridX, y: gy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    gy += qLabelH;

    const { totalH } = drawGrid(slide, gridX, gy, gridPanelW, cols, rows, [
      [...start, "A", BLUE],
      [...end,   "B", RED],
    ]);
    gy += totalH;

    addAnswerSection(slide, gridX, gy, gridPanelW, "", null);
  });

  // ── Right column ───────────────────────────────────────────────────────────
  slide.addImage({ path: labelPath, x: lblX, y: lblY, w: LL_W, h: LL_H });

  let rY = lblY + LL_H + 0.10;

  slide.addText("Worked Example:", {
    x: lblX, y: rY, w: LL_W, h: 0.20,
    fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
  });
  rY += 0.22;

  const { start, end, answer } = LP1_ADAPTED[0];
  const { totalH: wGridH } = drawGrid(slide, lblX, rY, gridPanelW, cols, rows, [
    [...start, "A", BLUE],
    [...end,   "B", RED],
  ]);
  const [sc, sr] = start, [ec, er] = end;
  drawRoute(slide, lblX, rY, cell, rows, [
    [sc, sr, ec, sr],
    [ec, sr, ec, er],
  ]);
  rY += wGridH;
  addAnswerSection(slide, lblX, rY, gridPanelW, "", answer);
  rY += 0.20;

  // Helpful hint box
  const hintMaxH = HALF_BOT - rY - 0.08;
  if (hintMaxH > 0.55) {
    slide.addText("Helpful hint…", {
      x: lblX, y: rY, w: LL_W, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
    });
    rY += 0.22;
    const boxH = Math.min(hintMaxH - 0.22, 0.88);
    slide.addText(ADAPTED_SUPPORT.hint1, {
      x: lblX, y: rY, w: LL_W, h: boxH,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK,
      fill: { color: "FFFFFF" },
      line: { color: "156082", width: 0.75 },
      margin: 6, valign: "top"
    });
  }

  addGlueHere(slide, HALF_TOP, HALF_H);
}

// ─────────────────────────────────────────────────────────────────────────────
// ADAPTED LP2 — compass replaces top slot; 2 questions; helpful hint box
// ─────────────────────────────────────────────────────────────────────────────
function buildLP2JourneysAdapted(slide) {
  const HALF_TOP = MID_Y + CUT_GAP;
  const HALF_BOT = SLIDE_H - MARGIN;
  const HALF_H   = HALF_BOT - HALF_TOP;

  const lblX  = SLIDE_W - LL_W - MARGIN;
  const rColW = LL_W;

  const gridPanelW   = 1.0;
  const yLabelGutter = 0.16;
  const gridX        = MARGIN + yLabelGutter;
  const cols = 6, rows = 6;
  const cell = gridPanelW / cols;
  const numH = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const totalGridH   = cell * rows + numH + 0.03;

  const ansColX = gridX + gridPanelW + 0.18;
  const ansColW = lblX - ansColX - 0.10;

  // 2 questions for adapted — from lesson_data
  const LP2_ADAPTED = ADAPTED_SUPPORT.lp2Questions;

  const LEG_ROW_H    = 0.18;
  const LEG_LINE_GAP = 0.05;
  const LEG_LABEL_W  = 0.62;

  function addLegRow(x, y, totalW, labelText, answer, answerColor) {
    slide.addText(labelText, {
      x, y, w: LEG_LABEL_W, h: LEG_ROW_H,
      fontSize: 8, fontFace: FONT_C, bold: true, color: BLACK,
      valign: "bottom", margin: 0
    });
    if (answer) {
      slide.addText(answer, {
        x: x + LEG_LABEL_W, y, w: totalW - LEG_LABEL_W, h: LEG_ROW_H,
        fontSize: 8.5, fontFace: FONT_C, bold: true, color: answerColor || GREEN,
        valign: "bottom", margin: 0
      });
    }
    const lineY = y + LEG_ROW_H + LEG_LINE_GAP;
    slide.addShape("line", { x, y: lineY, w: totalW, h: 0,
      line: { color: BLACK, width: 0.6 } });
    return LEG_ROW_H + LEG_LINE_GAP;
  }

  const twoLegsH = (LEG_ROW_H + LEG_LINE_GAP) * 2 + 0.10;
  const qLabelH  = 0.16;
  const qBlockH  = Math.max(qLabelH + totalGridH, qLabelH + twoLegsH) + 0.03;
  const qGap     = 0.08;

  let curY = HALF_TOP;

  // Title + instruction
  slide.addText(LP2_DATA.title || "Three-Stop Journeys", {
    x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
    fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
  });
  curY += 0.26;
  slide.addText(
    LP2_DATA.instruction || "Each journey visits A → B → C.  Write the directions for each leg.",
    { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 }
  );
  curY += 0.20;

  // Compass box — takes one qBlockH of space
  const compassBoxW = lblX - MARGIN - GUTTER;
  drawCompass(slide, MARGIN, curY, compassBoxW, qBlockH);
  curY += qBlockH + qGap;

  // Two questions
  LP2_ADAPTED.forEach(({ pts, a1, a2 }, i) => {
    slide.addText(`Q${i + 1}`, {
      x: MARGIN, y: curY, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });

    drawGrid(slide, gridX, curY + qLabelH, gridPanelW, cols, rows, pts);

    let aY = curY + qLabelH;
    aY += addLegRow(ansColX, aY, ansColW, "Leg 1 (A→B):", null, GREEN) + 0.10;
    addLegRow(ansColX, aY, ansColW, "Leg 2 (B→C):", null, GREEN);

    curY += qBlockH + qGap;

    if (i < LP2_ADAPTED.length - 1) {
      slide.addShape("line", {
        x: MARGIN, y: curY - qGap / 2,
        w: lblX - MARGIN - 0.10, h: 0,
        line: { color: "DDDDDD", width: 0.4, dashType: "dash" }
      });
    }
  });

  // ── Right column ───────────────────────────────────────────────────────────
  let rY = HALF_TOP;

  slide.addText("Worked Example:", {
    x: lblX, y: rY, w: rColW, h: 0.20,
    fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
  });
  rY += 0.22;

  const { pts, a1, a2 } = LP2_ADAPTED[0];
  drawGrid(slide, lblX, rY, gridPanelW, cols, rows, pts);

  // Route segments — data-driven from Q1 points
  const [pA, pB, pC] = LP2_ADAPTED[0].pts;
  const drawSeg = (c1, r1, c2, r2, arrowhead, color) => {
    const sx = lblX + c1*cell, sy = rY + (rows-r1)*cell;
    const tx = lblX + c2*cell, ty = rY + (rows-r2)*cell;
    slide.addShape("line", {
      x: Math.min(sx,tx), y: Math.min(sy,ty),
      w: Math.abs(tx-sx)||0.001, h: Math.abs(ty-sy)||0.001,
      flipH: tx<sx, flipV: ty<sy,
      line: { color, width: 0.8, dashType: "dash",
        ...(arrowhead ? { endArrowType: "arrow" } : {}) }
    });
  };
  drawSeg(pA[0], pA[1], pB[0], pA[1], false, "156082");
  drawSeg(pB[0], pA[1], pB[0], pB[1], true,  "156082");
  drawSeg(pB[0], pB[1], pC[0], pB[1], false, "7030A0");
  drawSeg(pC[0], pB[1], pC[0], pC[1], true,  "7030A0");

  rY += totalGridH + 0.06;
  rY += addLegRow(lblX, rY, rColW, "Leg 1 (A→B):", a1, "156082") + 0.12;
  addLegRow(lblX, rY, rColW, "Leg 2 (B→C):", a2, "7030A0");
  rY += LEG_ROW_H + LEG_LINE_GAP + 0.12;

  // Helpful hint box
  const hintMaxH = HALF_BOT - rY - 0.08;
  if (hintMaxH > 0.55) {
    slide.addText("Helpful hint…", {
      x: lblX, y: rY, w: rColW, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
    });
    rY += 0.22;
    const boxH = Math.min(hintMaxH - 0.22, 0.88);
    slide.addText(ADAPTED_SUPPORT.hint2, {
      x: lblX, y: rY, w: rColW, h: boxH,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK,
      fill: { color: "FFFFFF" },
      line: { color: "156082", width: 0.75 },
      margin: 6, valign: "top"
    });
  }

  addGlueHere(slide, HALF_TOP, HALF_H);
}
// ─────────────────────────────────────────────────────────────────────────────
// POLYGON DRAWING on LP grid
// Draws a connected polygon (shape) on a pptxgenjs slide at position gx,gy
// vertices: array of [col,row] in grid coordinates
// labels: vertex label strings e.g. ['A','B','C','D']
// color: hex string for edges and dots
// cell: cell size in inches (grid width / cols)
// rows: number of rows (for y-coordinate flip)
// showLabel: whether to draw vertex labels
// ─────────────────────────────────────────────────────────────────────────────
function drawPolygon(slide, gx, gy, cell, rows, vertices, labels, color, showLabel = true) {
  const dotR    = Math.min(0.055, cell * 0.25);
  const numH    = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const lblSz   = Math.max(6, Math.round(cell * 24));
  const edgeW   = 0.9;   // pt — slightly thinner than dots to read edges vs vertices

  // Edges first (so dots sit on top)
  for (let i = 0; i < vertices.length; i++) {
    const [c1, r1] = vertices[i];
    const [c2, r2] = vertices[(i + 1) % vertices.length];
    const sx = gx + c1 * cell, sy = gy + (rows - r1) * cell;
    const tx = gx + c2 * cell, ty = gy + (rows - r2) * cell;
    slide.addShape("line", {
      x: Math.min(sx, tx), y: Math.min(sy, ty),
      w: Math.abs(tx - sx) || 0.001, h: Math.abs(ty - sy) || 0.001,
      flipH: tx < sx, flipV: ty < sy,
      line: { color, width: edgeW }
    });
  }

  // Dots and labels
  vertices.forEach(([col, row], i) => {
    const px = gx + col * cell, py = gy + (rows - row) * cell;
    slide.addShape("ellipse", {
      x: px - dotR, y: py - dotR, w: dotR * 2, h: dotR * 2,
      fill: { color }, line: { color: "FFFFFF", width: 0.8 }
    });
    if (showLabel && labels[i]) {
      slide.addText(labels[i], {
        x: px + dotR * 0.3, y: py - dotR * 2.5,
        w: 0.16, h: numH * 1.1,
        fontSize: lblSz, fontFace: FONT_M, bold: true,
        color, align: "center", margin: 0
      });
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// LP1 — POLYGON TRANSLATION VERSION
// Layout: two question columns, each column has:
//   - Q label + translation instruction
//   - Original shape on left half-grid, blank right half-grid for translated shape
//   - Answer line below
// Right column: label + worked example showing Shape A + Shape B
// ─────────────────────────────────────────────────────────────────────────────
function buildLP1Polygon(slide, labelPath, isMarkingStation) {
  const HALF_TOP = MARGIN;
  const HALF_BOT = MID_Y - CUT_GAP;

  const lblX = SLIDE_W - LL_W - MARGIN;
  const lblY = HALF_TOP;

  const gridSize = LP1_DATA.gridSize || 7;
  // Each question: two side-by-side half-grids, each half-grid wide enough to fit shape + translated
  // Half-grid width = (lblX - MARGIN - GUTTER) / 2 / 2 ... but simpler: one full-width grid per question row
  // Layout decision: 3 questions in 2 rows (Q1+Q2 top, Q3 bottom-left only)
  // Each question: small grid showing shape only; right side is blank grid of same size
  // Grid pair width = (lblX - MARGIN - GUTTER) / 2 → each grid ≈ 1.4" for 7×7

  const yLG    = 0.16;   // y-axis label gutter
  const qCols  = 2;      // 2 questions per row
  const qW     = (lblX - MARGIN - (qCols - 1) * GUTTER) / qCols;  // ~2.5" per question column
  const gridW  = (qW - yLG - 0.1) / 2 - 0.06;   // each half-grid: shape grid or blank grid
  const cell   = gridW / gridSize;
  const numH   = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const gridH  = cell * gridSize;

  const qLabelH  = 0.16;
  const instrH   = 0.18;
  const ansH     = 0.24;
  const qBlockH  = qLabelH + instrH + gridH + numH + 0.03 + ansH + 0.06;

  let curY = HALF_TOP;

  // Title + instruction
  if (isMarkingStation) {
    slide.addText("Marking Station 1", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.26,
      fontSize: 13, fontFace: FONT_M, bold: true, color: GREEN, margin: 0
    });
  } else {
    slide.addText(LP1_DATA.title || "Moving Shapes on a Grid", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.26,
      fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
  }
  curY += 0.28;
  if (!isMarkingStation) {
    slide.addText(LP1_DATA.instruction || "Translate each shape using the direction given.  Draw the new position.",
      { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
        fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 });
    curY += 0.20;
  }

  const questions = LP1_DATA.questions;
  const SHAPE_COLOR = "1F4E79";
  const TRANS_COLOR = "E8642A";

  // Layout: 2 columns, auto-rows
  questions.forEach((q, qi) => {
    const col  = qi % qCols;
    const row  = Math.floor(qi / qCols);
    const qx   = MARGIN + col * (qW + GUTTER);
    const qy   = curY + row * (qBlockH + 0.08);
    const gx_a = qx + yLG;       // shape A grid origin x
    const gx_b = gx_a + gridW + 0.06;  // blank grid (shape B) origin x
    const gy   = qy + qLabelH + instrH;

    // Q label
    slide.addText(`Q${qi + 1}`, {
      x: qx, y: qy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });

    // Translation instruction below Q label
    const dc = q.translation[0], dr = q.translation[1];
    const instrText = `Translate: ${dc > 0 ? dc + ' right' : Math.abs(dc) + ' left'}, ${dr > 0 ? dr + ' up' : Math.abs(dr) + ' down'}`;
    slide.addText(instrText, {
      x: qx + 0.24, y: qy, w: qW - 0.24, h: qLabelH,
      fontSize: 8, fontFace: FONT_C, bold: false, color: "333333", margin: 0
    });

    // Grid A: original shape
    drawGrid(slide, gx_a, gy, gridW, gridSize, gridSize, []);
    drawPolygon(slide, gx_a, gy, cell, gridSize, q.shape, q.labels, SHAPE_COLOR);
    // x-axis labels for grid A
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_a + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    // Grid B: blank (pupil draws translated shape) or answer (marking station)
    drawGrid(slide, gx_b, gy, gridW, gridSize, gridSize, []);
    if (isMarkingStation) {
      // Draw translated shape in orange as answer
      const translated = q.shape.map(([c, r]) => [c + dc, r + dr]);
      drawPolygon(slide, gx_b, gy, cell, gridSize, translated,
        q.labels.map(l => `${l}'`), TRANS_COLOR);
    }
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_b + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    // Labels above each grid: "Shape A" (left) and "Draw Shape B here" (right, light)
    slide.addText("Shape A", {
      x: gx_a, y: gy - 0.16, w: gridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, bold: true, color: "1F4E79", margin: 0
    });
    if (!isMarkingStation) {
      slide.addText("Draw Shape B here", {
        x: gx_b, y: gy - 0.16, w: gridW, h: 0.15,
        fontSize: 7, fontFace: FONT_C, color: "AAAAAA", margin: 0
      });
    }

    // Answer line below both grids
    const ansY = gy + gridH + numH + 0.04;
    addAnswerSection(slide, gx_a, ansY, gridW * 2 + 0.06, "",
      isMarkingStation ? q.answer : null);
  });

  // ── Right column ──────────────────────────────────────────────────────────
  if (!isMarkingStation) {
    slide.addImage({ path: labelPath, x: lblX, y: lblY, w: LL_W, h: LL_H });
    let rY = lblY + LL_H + 0.10;

    // Worked example: Q1 with both shapes shown
    slide.addText("Worked Example:", {
      x: lblX, y: rY, w: LL_W, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
    });
    rY += 0.22;

    const wq   = questions[0];
    const wdc  = wq.translation[0], wdr = wq.translation[1];
    const wCell = gridW / gridSize;
    const wGridH = wCell * gridSize;
    const wNumH  = Math.max(5, Math.round(wCell * 24)) / 72 + 0.03;

    // Draw grid
    drawGrid(slide, lblX, rY, gridW, gridSize, gridSize, []);

    // Shape A (teal)
    drawPolygon(slide, lblX, rY, wCell, gridSize, wq.shape, wq.labels, SHAPE_COLOR);

    // Shape B (orange) — translated
    const wTranslated = wq.shape.map(([c, r]) => [c + wdc, r + wdr]);
    drawPolygon(slide, lblX, rY, wCell, gridSize, wTranslated,
      wq.labels.map(l => `${l}'`), TRANS_COLOR);

    // Translation arrow: A→A'
    const ax = lblX + wq.shape[0][0] * wCell;
    const ay = rY + (gridSize - wq.shape[0][1]) * wCell;
    const bx = lblX + (wq.shape[0][0] + wdc) * wCell;
    const by = rY + (gridSize - (wq.shape[0][1] + wdr)) * wCell;
    slide.addShape("line", {
      x: Math.min(ax, bx), y: Math.min(ay, by),
      w: Math.abs(bx - ax) || 0.001, h: Math.abs(by - ay) || 0.001,
      flipH: bx < ax, flipV: by < ay,
      line: { color: "888888", width: 0.8, dashType: "dash", endArrowType: "arrow" }
    });

    // x-axis labels
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: lblX + c * wCell - 0.06, y: rY + wGridH + 0.01,
        w: 0.12, h: wNumH, fontSize: Math.max(5, Math.round(wCell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }
    rY += wGridH + wNumH + 0.04;

    // Answer on the line
    addAnswerSection(slide, lblX, rY, LL_W, "", wq.answer);
    rY += 0.22;

    // Going further box
    const gfMaxH = HALF_BOT - rY - 0.08;
    if (gfMaxH > 0.50) {
      slide.addText("Going further…", {
        x: lblX, y: rY, w: LL_W, h: 0.20,
        fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
      });
      rY += 0.22;
      const boxH = Math.min(gfMaxH - 0.22, 0.88);
      slide.addText(LP1_DATA.goingFurther || "Can you write the reverse direction?", {
        x: lblX, y: rY, w: LL_W, h: boxH,
        fontSize: 8.5, fontFace: FONT_C, color: BLACK,
        fill: { color: "FFFFFF" }, line: { color: "156082", width: 0.75 },
        margin: 6, valign: "top"
      });
    }
  }

  addGlueHere(slide, HALF_TOP, HALF_BOT - HALF_TOP);
}

// ─────────────────────────────────────────────────────────────────────────────
// LP2 — POLYGON TRANSLATION VERSION (same pattern as LP1)
// ─────────────────────────────────────────────────────────────────────────────
function buildLP2Polygon(slide, isMarkingStation) {
  const HALF_TOP = MID_Y + CUT_GAP;
  const HALF_BOT = SLIDE_H - MARGIN;

  const lblX  = SLIDE_W - LL_W - MARGIN;
  const rColW = LL_W;

  const gridSize = LP2_DATA.gridSize || 7;
  const yLG    = 0.16;
  const qCols  = 2;
  const qW     = (lblX - MARGIN - (qCols - 1) * GUTTER) / qCols;
  const gridW  = (qW - yLG - 0.1) / 2 - 0.06;
  const cell   = gridW / gridSize;
  const numH   = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const gridH  = cell * gridSize;

  const qLabelH  = 0.16;
  const instrH   = 0.18;
  const ansH     = 0.24;
  const qBlockH  = qLabelH + instrH + gridH + numH + 0.03 + ansH + 0.06;

  const SHAPE_COLOR = "1F4E79";
  const TRANS_COLOR = "E8642A";

  let curY = HALF_TOP;

  if (isMarkingStation) {
    slide.addText("Marking Station 2", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
      fontSize: 13, fontFace: FONT_M, bold: true, color: GREEN, margin: 0
    });
  } else {
    slide.addText(LP2_DATA.title || "Translating More Polygons", {
      x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
      fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
  }
  curY += 0.28;
  if (!isMarkingStation) {
    slide.addText(LP2_DATA.instruction || "Translate each shape using the direction given.  Draw the new position.",
      { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
        fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 });
    curY += 0.20;
  }

  LP2_DATA.questions.forEach((q, qi) => {
    const col = qi % qCols;
    const row = Math.floor(qi / qCols);
    const qx  = MARGIN + col * (qW + GUTTER);
    const qy  = curY + row * (qBlockH + 0.08);
    const gx_a = qx + yLG;
    const gx_b = gx_a + gridW + 0.06;
    const gy   = qy + qLabelH + instrH;

    const dc = q.translation[0], dr = q.translation[1];

    slide.addText(`Q${qi + 1}`, {
      x: qx, y: qy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    const instrText = `Translate: ${dc > 0 ? dc + ' right' : Math.abs(dc) + ' left'}, ${dr > 0 ? dr + ' up' : Math.abs(dr) + ' down'}`;
    slide.addText(instrText, {
      x: qx + 0.24, y: qy, w: qW - 0.24, h: qLabelH,
      fontSize: 8, fontFace: FONT_C, color: "333333", margin: 0
    });

    drawGrid(slide, gx_a, gy, gridW, gridSize, gridSize, []);
    drawPolygon(slide, gx_a, gy, cell, gridSize, q.shape, q.labels, SHAPE_COLOR);
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_a + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    drawGrid(slide, gx_b, gy, gridW, gridSize, gridSize, []);
    if (isMarkingStation) {
      const translated = q.shape.map(([c, r]) => [c + dc, r + dr]);
      drawPolygon(slide, gx_b, gy, cell, gridSize, translated,
        q.labels.map(l => `${l}'`), TRANS_COLOR);
    }
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_b + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    slide.addText("Shape A", {
      x: gx_a, y: gy - 0.16, w: gridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, bold: true, color: "1F4E79", margin: 0
    });
    if (!isMarkingStation) {
      slide.addText("Draw Shape B here", {
        x: gx_b, y: gy - 0.16, w: gridW, h: 0.15,
        fontSize: 7, fontFace: FONT_C, color: "AAAAAA", margin: 0
      });
    }

    const ansY = gy + gridH + numH + 0.04;
    addAnswerSection(slide, gx_a, ansY, gridW * 2 + 0.06, "",
      isMarkingStation ? q.answer : null);
  });

  // Right column — worked example
  if (!isMarkingStation) {
    let rY = HALF_TOP;
    slide.addText("Worked Example:", {
      x: lblX, y: rY, w: rColW, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
    });
    rY += 0.22;

    const wq  = LP2_DATA.questions[0];
    const wdc = wq.translation[0], wdr = wq.translation[1];
    const wCell = gridW / gridSize;
    const wGridH = wCell * gridSize;
    const wNumH  = Math.max(5, Math.round(wCell * 24)) / 72 + 0.03;

    drawGrid(slide, lblX, rY, gridW, gridSize, gridSize, []);
    drawPolygon(slide, lblX, rY, wCell, gridSize, wq.shape, wq.labels, SHAPE_COLOR);
    const wTranslated = wq.shape.map(([c, r]) => [c + wdc, r + wdr]);
    drawPolygon(slide, lblX, rY, wCell, gridSize, wTranslated,
      wq.labels.map(l => `${l}'`), TRANS_COLOR);

    const ax = lblX + wq.shape[0][0] * wCell;
    const ay = rY + (gridSize - wq.shape[0][1]) * wCell;
    const bx = lblX + (wq.shape[0][0] + wdc) * wCell;
    const by = rY + (gridSize - (wq.shape[0][1] + wdr)) * wCell;
    slide.addShape("line", {
      x: Math.min(ax, bx), y: Math.min(ay, by),
      w: Math.abs(bx - ax) || 0.001, h: Math.abs(by - ay) || 0.001,
      flipH: bx < ax, flipV: by < ay,
      line: { color: "888888", width: 0.8, dashType: "dash", endArrowType: "arrow" }
    });

    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: lblX + c * wCell - 0.06, y: rY + wGridH + 0.01,
        w: 0.12, h: wNumH, fontSize: Math.max(5, Math.round(wCell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }
    rY += wGridH + wNumH + 0.04;
    addAnswerSection(slide, lblX, rY, rColW, "", wq.answer);
    rY += 0.22;

    const gfMaxH = HALF_BOT - rY - 0.08;
    if (gfMaxH > 0.50) {
      slide.addText("Going further…", {
        x: lblX, y: rY, w: rColW, h: 0.20,
        fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
      });
      rY += 0.22;
      slide.addText(LP2_DATA.goingFurther || "Write the reverse direction for one shape.", {
        x: lblX, y: rY, w: rColW, h: Math.min(gfMaxH - 0.22, 0.88),
        fontSize: 8.5, fontFace: FONT_C, color: BLACK,
        fill: { color: "FFFFFF" }, line: { color: "156082", width: 0.75 },
        margin: 6, valign: "top"
      });
    }
  }

  addGlueHere(slide, HALF_TOP, HALF_BOT - HALF_TOP);
}


// ─────────────────────────────────────────────────────────────────────────────
// POLYGON ADAPTED VERSIONS — same layout as full polygon LP but fewer questions
// Uses ADAPTED_SUPPORT.lp1Questions / lp2Questions instead of full question list
// ─────────────────────────────────────────────────────────────────────────────
function drawTranslationScaffold(slide, boxX, boxY, boxW, boxH) {
  // Step-by-step scaffold for less confident learners doing polygon translation
  slide.addShape("rect", {
    x: boxX, y: boxY, w: boxW, h: boxH,
    fill: { color: "DEECF8" },
    line: { color: "156082", width: 0.75 }
  });
  const pad = 0.08;
  const stepSz = 8.5;
  const stepH = 0.20;
  let sy = boxY + pad;
  slide.addText("Steps to translate a shape:", {
    x: boxX + pad, y: sy, w: boxW - pad*2, h: stepH,
    fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
  });
  sy += stepH + 0.04;
  const steps = [
    "1.  Look at vertex A on Shape A.",
    "2.  Count the squares in the direction given.",
    "3.  Plot the new position — this is A\u2032.",
    "4.  Repeat for every vertex (B, C, D …).",
    "5.  Connect all the new vertices to draw Shape B."
  ];
  steps.forEach(s => {
    slide.addText(s, {
      x: boxX + pad, y: sy, w: boxW - pad*2, h: stepH,
      fontSize: stepSz, fontFace: FONT_C, color: BLACK, margin: 0
    });
    sy += stepH;
  });
}

function buildLP1PolygonAdapted(slide, labelPath) {
  const HALF_TOP = MARGIN;
  const HALF_BOT = MID_Y - CUT_GAP;

  const lblX = SLIDE_W - LL_W - MARGIN;
  const lblY = HALF_TOP;

  const gridSize = LP1_DATA.gridSize || 7;
  const yLG    = 0.16;
  const qCols  = 2;
  const qW     = (lblX - MARGIN - (qCols - 1) * GUTTER) / qCols;
  const gridW  = (qW - yLG - 0.1) / 2 - 0.06;
  const cell   = gridW / gridSize;
  const numH   = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const gridH  = cell * gridSize;

  const qLabelH  = 0.16;
  const instrH   = 0.18;
  const ansH     = 0.24;
  const qBlockH  = qLabelH + instrH + gridH + numH + 0.03 + ansH + 0.06;

  const SHAPE_COLOR = "1F4E79";

  let curY = HALF_TOP;

  // Title + instruction
  slide.addText(LP1_DATA.title || "Moving Shapes on a Grid", {
    x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.26,
    fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
  });
  curY += 0.28;
  slide.addText(LP1_DATA.instruction || "Translate each shape using the direction given.  Draw the new position.",
    { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 });
  curY += 0.20;

  // ── Scaffold box — takes one full qBlockH of space ──
  const scaffoldW = lblX - MARGIN - GUTTER;
  drawTranslationScaffold(slide, MARGIN, curY, scaffoldW, qBlockH);
  curY += qBlockH + 0.08;

  // ── Two questions (from adaptedSupport) ──
  const LP1_ADAPTED = ADAPTED_SUPPORT.lp1Questions;
  LP1_ADAPTED.forEach((q, qi) => {
    const col  = qi % qCols;
    const qx   = MARGIN + col * (qW + GUTTER);
    const qy   = curY;
    const gx_a = qx + yLG;
    const gx_b = gx_a + gridW + 0.06;
    const gy   = qy + qLabelH + instrH;

    const dc = q.translation[0], dr = q.translation[1];

    slide.addText(`Q${qi + 1}`, {
      x: qx, y: qy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    const instrText = `Translate: ${dc > 0 ? dc + ' right' : Math.abs(dc) + ' left'}, ${dr > 0 ? dr + ' up' : Math.abs(dr) + ' down'}`;
    slide.addText(instrText, {
      x: qx + 0.24, y: qy, w: qW - 0.24, h: qLabelH,
      fontSize: 8, fontFace: FONT_C, color: "333333", margin: 0
    });

    // Grid A: original shape
    drawGrid(slide, gx_a, gy, gridW, gridSize, gridSize, []);
    drawPolygon(slide, gx_a, gy, cell, gridSize, q.shape, q.labels, SHAPE_COLOR);
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_a + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    // Grid B: blank for pupil
    drawGrid(slide, gx_b, gy, gridW, gridSize, gridSize, []);
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_b + c * cell - 0.06, y: gy + gridH + 0.01,
        w: 0.12, h: numH, fontSize: Math.max(5, Math.round(cell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    slide.addText("Shape A", {
      x: gx_a, y: gy - 0.16, w: gridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, bold: true, color: "1F4E79", margin: 0
    });
    slide.addText("Draw Shape B here", {
      x: gx_b, y: gy - 0.16, w: gridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, color: "AAAAAA", margin: 0
    });

    const ansY = gy + gridH + numH + 0.04;
    addAnswerSection(slide, gx_a, ansY, gridW * 2 + 0.06, "", null);
  });

  // ── Right column: label, worked example, helpful hint ──
  slide.addImage({ path: labelPath, x: lblX, y: lblY, w: LL_W, h: LL_H });
  let rY = lblY + LL_H + 0.10;

  slide.addText("Worked Example:", {
    x: lblX, y: rY, w: LL_W, h: 0.20,
    fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
  });
  rY += 0.22;

  const wq  = ADAPTED_SUPPORT.workedExample1 || LP1_ADAPTED[0];
  const wdc = wq.translation[0], wdr = wq.translation[1];
  const wCell = gridW / gridSize;
  const wGridH = wCell * gridSize;
  const wNumH  = Math.max(5, Math.round(wCell * 24)) / 72 + 0.03;

  drawGrid(slide, lblX, rY, gridW, gridSize, gridSize, []);
  drawPolygon(slide, lblX, rY, wCell, gridSize, wq.shape, wq.labels, SHAPE_COLOR);
  const wTranslated = wq.shape.map(([c, r]) => [c + wdc, r + wdr]);
  drawPolygon(slide, lblX, rY, wCell, gridSize, wTranslated,
    wq.labels.map(l => `${l}'`), "E8642A");

  // Dashed arrow from A to A'
  const ax = lblX + wq.shape[0][0] * wCell;
  const ay = rY + (gridSize - wq.shape[0][1]) * wCell;
  const bx = lblX + (wq.shape[0][0] + wdc) * wCell;
  const by = rY + (gridSize - (wq.shape[0][1] + wdr)) * wCell;
  slide.addShape("line", {
    x: Math.min(ax, bx), y: Math.min(ay, by),
    w: Math.abs(bx - ax) || 0.001, h: Math.abs(by - ay) || 0.001,
    flipH: bx < ax, flipV: by < ay,
    line: { color: "888888", width: 0.8, dashType: "dash", endArrowType: "arrow" }
  });

  for (let c = 0; c <= gridSize; c++) {
    slide.addText(String(c), {
      x: lblX + c * wCell - 0.06, y: rY + wGridH + 0.01,
      w: 0.12, h: wNumH, fontSize: Math.max(5, Math.round(wCell*24)),
      fontFace: FONT_M, align: "center", color: "555555", margin: 0
    });
  }
  rY += wGridH + wNumH + 0.04;
  addAnswerSection(slide, lblX, rY, LL_W, "", wq.answer);
  rY += 0.22;

  // Helpful hint box (replaces going further)
  const hintMaxH = HALF_BOT - rY - 0.08;
  if (hintMaxH > 0.55) {
    slide.addText("Helpful hint\u2026", {
      x: lblX, y: rY, w: LL_W, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
    });
    rY += 0.22;
    const boxH = Math.min(hintMaxH - 0.22, 0.88);
    slide.addText(ADAPTED_SUPPORT.hint1, {
      x: lblX, y: rY, w: LL_W, h: boxH,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK,
      fill: { color: "FFFFFF" }, line: { color: "156082", width: 0.75 },
      margin: 6, valign: "top"
    });
  }

  addGlueHere(slide, HALF_TOP, HALF_BOT - HALF_TOP);
}

function buildLP2PolygonAdapted(slide) {
  const HALF_TOP = MID_Y + CUT_GAP;
  const HALF_BOT = SLIDE_H - MARGIN;

  const lblX  = SLIDE_W - LL_W - MARGIN;
  const rColW = LL_W;

  const gridSize = LP2_DATA.gridSize || 7;
  const yLG    = 0.16;
  const qW     = lblX - MARGIN - GUTTER;   // full width for single question
  const gridW  = (qW - yLG - 0.1) / 2 - 0.06;
  const cell   = gridW / gridSize;
  const numH   = Math.max(5, Math.round(cell * 24)) / 72 + 0.03;
  const gridH  = cell * gridSize;

  const qLabelH  = 0.16;
  const instrH   = 0.18;
  const ansH     = 0.24;

  const SHAPE_COLOR = "1F4E79";

  let curY = HALF_TOP;

  // Title + instruction
  slide.addText(LP2_DATA.title || "Translating More Polygons", {
    x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.24,
    fontSize: 13, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
  });
  curY += 0.28;
  slide.addText(LP2_DATA.instruction || "Translate each shape using the direction given.  Draw the new position.",
    { x: MARGIN, y: curY, w: lblX - GUTTER, h: 0.18,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK, margin: 0 });
  curY += 0.20;

  // ── Questions (from adaptedSupport — typically 1) ──
  const LP2_ADAPTED = ADAPTED_SUPPORT.lp2Questions;
  const qCols = Math.min(LP2_ADAPTED.length, 2);
  const qColW = (lblX - MARGIN - (qCols - 1) * GUTTER) / qCols;
  const qGridW = (qColW - yLG - 0.1) / 2 - 0.06;
  const qCell  = qGridW / gridSize;
  const qNumH  = Math.max(5, Math.round(qCell * 24)) / 72 + 0.03;
  const qGridH = qCell * gridSize;

  LP2_ADAPTED.forEach((q, qi) => {
    const col = qi % qCols;
    const qx  = MARGIN + col * (qColW + GUTTER);
    const qy  = curY;
    const gx_a = qx + yLG;
    const gx_b = gx_a + qGridW + 0.06;
    const gy   = qy + qLabelH + instrH;

    const dc = q.translation[0], dr = q.translation[1];

    slide.addText(`Q${qi + 1}`, {
      x: qx, y: qy, w: 0.22, h: qLabelH,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLACK, margin: 0
    });
    const instrText = `Translate: ${dc > 0 ? dc + ' right' : Math.abs(dc) + ' left'}, ${dr > 0 ? dr + ' up' : Math.abs(dr) + ' down'}`;
    slide.addText(instrText, {
      x: qx + 0.24, y: qy, w: qColW - 0.24, h: qLabelH,
      fontSize: 8, fontFace: FONT_C, color: "333333", margin: 0
    });

    drawGrid(slide, gx_a, gy, qGridW, gridSize, gridSize, []);
    drawPolygon(slide, gx_a, gy, qCell, gridSize, q.shape, q.labels, SHAPE_COLOR);
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_a + c * qCell - 0.06, y: gy + qGridH + 0.01,
        w: 0.12, h: qNumH, fontSize: Math.max(5, Math.round(qCell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    drawGrid(slide, gx_b, gy, qGridW, gridSize, gridSize, []);
    for (let c = 0; c <= gridSize; c++) {
      slide.addText(String(c), {
        x: gx_b + c * qCell - 0.06, y: gy + qGridH + 0.01,
        w: 0.12, h: qNumH, fontSize: Math.max(5, Math.round(qCell*24)),
        fontFace: FONT_M, align: "center", color: "555555", margin: 0
      });
    }

    slide.addText("Shape A", {
      x: gx_a, y: gy - 0.16, w: qGridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, bold: true, color: "1F4E79", margin: 0
    });
    slide.addText("Draw Shape B here", {
      x: gx_b, y: gy - 0.16, w: qGridW, h: 0.15,
      fontSize: 7, fontFace: FONT_C, color: "AAAAAA", margin: 0
    });

    const ansY = gy + qGridH + qNumH + 0.04;
    addAnswerSection(slide, gx_a, ansY, qGridW * 2 + 0.06, "", null);
  });

  // ── Right column: worked example + helpful hint ──
  let rY = HALF_TOP;
  slide.addText("Worked Example:", {
    x: lblX, y: rY, w: rColW, h: 0.20,
    fontSize: 9, fontFace: FONT_C, bold: true, color: "156082", margin: 0
  });
  rY += 0.22;

  const wq  = ADAPTED_SUPPORT.workedExample2 || LP2_ADAPTED[0];
  const wdc = wq.translation[0], wdr = wq.translation[1];
  const wCell = gridW / gridSize;
  const wGridH = wCell * gridSize;
  const wNumH  = Math.max(5, Math.round(wCell * 24)) / 72 + 0.03;

  drawGrid(slide, lblX, rY, gridW, gridSize, gridSize, []);
  drawPolygon(slide, lblX, rY, wCell, gridSize, wq.shape, wq.labels, SHAPE_COLOR);
  const wTranslated = wq.shape.map(([c, r]) => [c + wdc, r + wdr]);
  drawPolygon(slide, lblX, rY, wCell, gridSize, wTranslated,
    wq.labels.map(l => `${l}'`), "E8642A");

  const ax = lblX + wq.shape[0][0] * wCell;
  const ay = rY + (gridSize - wq.shape[0][1]) * wCell;
  const bx = lblX + (wq.shape[0][0] + wdc) * wCell;
  const by = rY + (gridSize - (wq.shape[0][1] + wdr)) * wCell;
  slide.addShape("line", {
    x: Math.min(ax, bx), y: Math.min(ay, by),
    w: Math.abs(bx - ax) || 0.001, h: Math.abs(by - ay) || 0.001,
    flipH: bx < ax, flipV: by < ay,
    line: { color: "888888", width: 0.8, dashType: "dash", endArrowType: "arrow" }
  });

  for (let c = 0; c <= gridSize; c++) {
    slide.addText(String(c), {
      x: lblX + c * wCell - 0.06, y: rY + wGridH + 0.01,
      w: 0.12, h: wNumH, fontSize: Math.max(5, Math.round(wCell*24)),
      fontFace: FONT_M, align: "center", color: "555555", margin: 0
    });
  }
  rY += wGridH + wNumH + 0.04;
  addAnswerSection(slide, lblX, rY, rColW, "", wq.answer);
  rY += 0.22;

  // Helpful hint box
  const hintMaxH = HALF_BOT - rY - 0.08;
  if (hintMaxH > 0.55) {
    slide.addText("Helpful hint\u2026", {
      x: lblX, y: rY, w: rColW, h: 0.20,
      fontSize: 9, fontFace: FONT_C, bold: true, color: BLUE, margin: 0
    });
    rY += 0.22;
    const boxH = Math.min(hintMaxH - 0.22, 0.88);
    slide.addText(ADAPTED_SUPPORT.hint2, {
      x: lblX, y: rY, w: rColW, h: boxH,
      fontSize: 8.5, fontFace: FONT_C, color: BLACK,
      fill: { color: "FFFFFF" }, line: { color: "156082", width: 0.75 },
      margin: 6, valign: "top"
    });
  }

  addGlueHere(slide, HALF_TOP, HALF_BOT - HALF_TOP);
}


function addCutLine(slide) {
  slide.addShape("line", {
    x: 0, y: MID_Y, w: SLIDE_W, h: 0,
    line: { color: "BBBBBB", width: 0.75, dashType: "dash" }
  });
  slide.addText("✂", {
    x: 0.04, y: MID_Y - 0.12, w: 0.18, h: 0.16,
    fontSize: 10, fontFace: FONT_M, color: GREY, margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN
(async () => {
  console.log(`Building LP for lesson ${LESSON_NUM}: ${LESSON.week} ${LESSON.day}`);
  console.log("Rendering label...");
  const labelPath = await renderMathsLabel();

  const pres = new PptxGenJS();
  pres.defineLayout({ name: "A4P", width: SLIDE_W, height: SLIDE_H });
  pres.layout = "A4P";

  // ── Pupil sheet ──
  console.log("Building pupil sheet...");
  const qSlide = pres.addSlide();
  buildLP1(qSlide, labelPath, false);
  addCutLine(qSlide);
  buildLP2(qSlide, false);

  // ── Adapted sheet ──
  console.log("Building adapted sheet...");
  const aSlide = pres.addSlide();
  buildLP1Adapted(aSlide, labelPath);
  addCutLine(aSlide);
  buildLP2Adapted(aSlide);

  // ── Marking station sheet ──
  console.log("Building marking station...");
  const mSlide = pres.addSlide();
  buildLP1(mSlide, labelPath, true);
  addCutLine(mSlide);
  buildLP2(mSlide, true);

  await pres.writeFile({ fileName: outFile });
  console.log("Saved:", outFile);
})();
