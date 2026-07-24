'use strict';
const path = require('path');
const fs   = require('fs');
const PptxGenJs = require('/home/claude/.npm-global/lib/node_modules/pptxgenjs');

const DATA = require('./y5_t1_data.js');

// ── Colours ───────────────────────────────────────────────────────────────────
const ORANGE  = 'E57D24';   // Y5 Hazel brand
const AMBER   = 'FFC000';   // WFA accent
const BG      = 'DEECF8';   // WFA pale blue
const WHITE   = 'FFFFFF';
const DARK    = '2D3142';
const TILE_BG = 'D6EAF8';   // alphabet tile fill (non-phonics, non-vowel)
const TILE_FG = '1A5276';   // alphabet tile text
const TILE_BD = 'A9CCE3';   // alphabet tile border
const ORANGE_PALE = 'FDE8CF'; // soft orange for secondary text

// ── Fonts ─────────────────────────────────────────────────────────────────────
const FH = 'Twinkl Cursive Looped';
const FB = 'Calibri';

// ── Spanish alphabet (29) ─────────────────────────────────────────────────────
const ALPHA = [
  {l:'A',  s:'ah',       v:true},
  {l:'B',  s:'beh'},
  {l:'C',  s:'seh',      tricky:true},
  {l:'D',  s:'deh'},
  {l:'E',  s:'eh',       v:true},
  {l:'F',  s:'ef'},
  {l:'G',  s:'heh',      tricky:true},
  {l:'H',  s:'ah-cheh',  tricky:true},
  {l:'I',  s:'ee',       v:true},
  {l:'J',  s:'hoh-tah',  tricky:true},
  {l:'K',  s:'kah'},
  {l:'L',  s:'el-eh'},
  {l:'LL', s:'el-yeh',   tricky:true},
  {l:'M',  s:'em-eh'},
  {l:'N',  s:'en-eh'},
  {l:'Ñ',  s:'en-yeh',   tricky:true},
  {l:'O',  s:'oh',       v:true},
  {l:'P',  s:'peh'},
  {l:'Q',  s:'koo'},
  {l:'R',  s:'er-eh'},
  {l:'RR', s:'er-reh',   tricky:true},
  {l:'S',  s:'es-eh'},
  {l:'T',  s:'teh'},
  {l:'U',  s:'oo',       v:true},
  {l:'V',  s:'oo-veh',   tricky:true},
  {l:'W',  s:'dob-leh'},
  {l:'X',  s:'eh-kis'},
  {l:'Y',  s:'ee-gree'},
  {l:'Z',  s:'seh-tah',  tricky:true},
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function addBg(slide) {
  slide.addShape('rect', {x:0,y:0,w:13.3,h:7.5, fill:{color:BG}, line:{width:0}});
}

function addHeader(slide, label) {
  slide.addShape('rect', {x:0,y:0,w:13.3,h:0.82, fill:{color:ORANGE}, line:{width:0}});
  slide.addText(label, {
    x:0.25,y:0,w:12.8,h:0.82,
    fontSize:20, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'left',
  });
}

function rr(pres) { return pres.ShapeType.roundRect; }

// ── Slide 1: Title ────────────────────────────────────────────────────────────
function addTitle(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);

  slide.addShape('rect', {x:0,y:0,w:8.0,h:7.5, fill:{color:ORANGE}, line:{width:0}});
  slide.addShape('rect', {x:8.0,y:0,w:0.18,h:7.5, fill:{color:AMBER}, line:{width:0}});

  slide.addText(`Lección ${lesson.num}`, {
    x:0.35,y:0.4,w:7.3,h:0.7,
    fontSize:24, bold:false, fontFace:FB, color:WHITE,
    valign:'middle', align:'left',
  });
  slide.addText(lesson.titleSp, {
    x:0.35,y:1.1,w:7.3,h:2.5,
    fontSize:52, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'left',
  });
  slide.addShape('rect', {x:0.35,y:3.65,w:7.0,h:0.09, fill:{color:AMBER}, line:{width:0}});
  slide.addText(lesson.titleEng, {
    x:0.35,y:3.8,w:7.3,h:0.85,
    fontSize:26, bold:false, fontFace:FB, color:WHITE,
    valign:'middle', align:'left',
  });
  slide.addText('Y5 Spanish · Aut 1 · Body Parts and Health', {
    x:0.35,y:6.85,w:7.3,h:0.45,
    fontSize:13, fontFace:FB, color:ORANGE_PALE,
    valign:'middle', align:'left',
  });

  slide.addText('Wallscourt Farm Academy', {
    x:8.3,y:0.3,w:4.7,h:0.5,
    fontSize:14, bold:true, fontFace:FB, color:ORANGE,
    valign:'middle', align:'right',
  });
  slide.addText('¡Español!', {
    x:8.3,y:2.2,w:4.7,h:2.8,
    fontSize:64, bold:true, fontFace:FH, color:'E8C5A0',
    valign:'middle', align:'center', transparency:40,
  });
  slide.addText('Hazel Learning Zone', {
    x:8.3,y:6.6,w:4.7,h:0.55,
    fontSize:13, fontFace:FB, color:ORANGE,
    valign:'middle', align:'right',
  });
}

// ── Slide 2: Learning Objective ───────────────────────────────────────────────
function addLO(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, 'Objetivo de aprendizaje — Learning Objective');

  slide.addShape(rr(pres), {
    x:0.5,y:1.1,w:12.3,h:2.1,
    fill:{color:ORANGE}, line:{color:AMBER,width:3}, rectRadius:0.1,
  });
  slide.addText(lesson.lo, {
    x:0.7,y:1.15,w:11.9,h:2.0,
    fontSize:28, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'center', wrap:true,
  });

  slide.addShape(rr(pres), {
    x:0.5,y:3.4,w:12.3,h:1.3,
    fill:{color:WHITE}, line:{color:AMBER,width:2}, rectRadius:0.1,
  });
  slide.addText(lesson.loEng, {
    x:0.7,y:3.45,w:11.9,h:1.2,
    fontSize:22, fontFace:FB, color:DARK,
    valign:'middle', align:'center', wrap:true,
  });

  slide.addText('Can you do this by the end of today?', {
    x:0.5,y:4.9,w:12.3,h:0.55,
    fontSize:16, italic:true, fontFace:FB, color:ORANGE,
    valign:'middle', align:'center',
  });
}

// ── Slide 3: Vowels ───────────────────────────────────────────────────────────
function addVowels(pres) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, 'El abecedario — Las vocales · The vowels');

  const vows = [{l:'A',s:'ah'},{l:'E',s:'eh'},{l:'I',s:'ee'},{l:'O',s:'oh'},{l:'U',s:'oo'}];
  const tW=2.1, tH=3.8, gap=0.3;
  const startX = (13.3 - (5*tW + 4*gap)) / 2;
  const startY = 1.4;

  vows.forEach((v,i) => {
    const x = startX + i*(tW+gap);
    slide.addShape(rr(pres), {
      x,y:startY,w:tW,h:tH,
      fill:{color:ORANGE}, line:{color:AMBER,width:4}, rectRadius:0.12,
    });
    slide.addText(v.l, {
      x,y:startY+0.2,w:tW,h:2.5,
      fontSize:96, bold:true, fontFace:FH, color:WHITE,
      valign:'middle', align:'center',
    });
    slide.addShape('rect', {
      x:x+0.08,y:startY+tH-1.05,w:tW-0.16,h:0.9,
      fill:{color:AMBER}, line:{width:0},
    });
    slide.addText(v.s, {
      x,y:startY+tH-1.0,w:tW,h:0.8,
      fontSize:22, bold:true, fontFace:FB, color:DARK,
      valign:'middle', align:'center',
    });
  });

  slide.addText('The five vowels always sound the same — every single time!', {
    x:0.5,y:6.55,w:12.3,h:0.6,
    fontSize:16, italic:true, fontFace:FB, color:ORANGE,
    valign:'middle', align:'center',
  });
}

// ── Slide 4: Alphabet grid ────────────────────────────────────────────────────
function addAlphabet(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, 'El abecedario — El alfabeto español');

  const COLS=6, tW=1.95, tH=1.05, gX=0.11, gY=0.1;
  const totalW = COLS*tW + (COLS-1)*gX;
  const startX = (13.3-totalW)/2;
  const startY = 0.92;
  const phLetter = lesson.phonicsLetter.toUpperCase();

  ALPHA.forEach((lt, idx) => {
    const col = idx % COLS;
    const row = Math.floor(idx / COLS);
    const x = startX + col*(tW+gX);
    const y = startY + row*(tH+gY);

    const isPh   = lt.l.toUpperCase() === phLetter;
    const isVow  = !!lt.v;

    const fillC  = isPh ? ORANGE : (isVow ? AMBER : TILE_BG);
    const textC  = isPh ? WHITE  : (isVow ? DARK  : TILE_FG);
    const bordC  = isPh ? AMBER  : (isVow ? ORANGE : TILE_BD);
    const bordW  = isPh ? 3 : (isVow ? 2 : 1);
    const subC   = isPh ? ORANGE_PALE : (isVow ? '5D4E00' : '6090B0');

    slide.addShape(rr(pres), {
      x,y,w:tW,h:tH,
      fill:{color:fillC}, line:{color:bordC,width:bordW}, rectRadius:0.07,
    });
    slide.addText(lt.l, {
      x,y:y+0.02,w:tW,h:tH*0.58,
      fontSize:isPh?25:20, bold:true, fontFace:FH, color:textC,
      valign:'middle', align:'center',
    });
    slide.addText(lt.s, {
      x,y:y+tH*0.57,w:tW,h:tH*0.38,
      fontSize:9, fontFace:FB, color:subC,
      valign:'middle', align:'center',
    });

    // Tricky badge
    if (lt.tricky) {
      const bdgC = isPh ? AMBER : ORANGE;
      const bdgT = isPh ? DARK  : WHITE;
      slide.addShape(rr(pres), {
        x:x+tW-0.27,y:y+0.03,w:0.22,h:0.22,
        fill:{color:bdgC}, line:{width:0}, rectRadius:0.11,
      });
      slide.addText('!', {
        x:x+tW-0.27,y:y+0.03,w:0.22,h:0.22,
        fontSize:10, bold:true, fontFace:FB, color:bdgT,
        valign:'middle', align:'center',
      });
    }
  });

  // Legend
  const legY = 6.6;
  slide.addShape('rect', {x:0.3,y:legY,w:0.22,h:0.22, fill:{color:ORANGE}, line:{width:0}});
  slide.addText("Today's sound", {x:0.56,y:legY-0.02,w:2.0,h:0.26, fontSize:11, fontFace:FB, color:ORANGE});
  slide.addShape('rect', {x:3.1,y:legY,w:0.22,h:0.22, fill:{color:AMBER}, line:{width:0}});
  slide.addText('Vowels', {x:3.36,y:legY-0.02,w:1.3,h:0.26, fontSize:11, fontFace:FB, color:DARK});
  slide.addShape(rr(pres), {x:5.1,y:legY,w:0.22,h:0.22, fill:{color:ORANGE}, line:{width:0}, rectRadius:0.11});
  slide.addText('! = Tricky sound', {x:5.36,y:legY-0.02,w:2.2,h:0.26, fontSize:11, fontFace:FB, color:DARK});
}

// ── Slide 5: Counting ─────────────────────────────────────────────────────────
function addCounting(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, `¡Vamos a contar! — ${lesson.counting.label}`);

  const nums = lesson.counting.nums;
  const PER_ROW = 5;
  const rows = Math.ceil(nums.length / PER_ROW);
  const cW = nums.length <= 10 ? 2.2 : 2.1;
  const cH = nums.length <= 10 ? 2.6 : 1.42;
  const gX = nums.length <= 10 ? 0.22 : 0.18;
  const gY = nums.length <= 10 ? 0.2 : 0.12;
  const totalW = PER_ROW*cW + (PER_ROW-1)*gX;
  const startX = (13.3-totalW)/2;
  const startY = nums.length <= 10 ? 1.5 : 0.9;

  nums.forEach((item, i) => {
    const col = i % PER_ROW;
    const row = Math.floor(i / PER_ROW);
    const x = startX + col*(cW+gX);
    const y = startY + row*(cH+gY);
    const even = i%2===0;

    slide.addShape(rr(pres), {
      x,y,w:cW,h:cH,
      fill:{color: even ? ORANGE : WHITE},
      line:{color:AMBER,width:2}, rectRadius:0.1,
    });
    slide.addText(item.n, {
      x,y:y+0.08,w:cW,h:cH*0.54,
      fontSize: nums.length<=10 ? 48 : 36, bold:true, fontFace:FH,
      color: even ? WHITE : ORANGE,
      valign:'middle', align:'center',
    });
    slide.addText(item.sp, {
      x,y:y+cH*0.57,w:cW,h:cH*0.38,
      fontSize: nums.length<=10 ? 20 : 15, fontFace:FH,
      color: even ? ORANGE_PALE : DARK,
      valign:'middle', align:'center',
    });
  });
}

// ── Slide 6: Warm-up ──────────────────────────────────────────────────────────
function addWarmUp(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, '¡Calentamiento! — Warm-up');

  slide.addShape(rr(pres), {
    x:0.5,y:1.0,w:12.3,h:1.05,
    fill:{color:ORANGE}, line:{width:0}, rectRadius:0.1,
  });
  slide.addText(lesson.warmUp.title, {
    x:0.7,y:1.02,w:11.9,h:1.0,
    fontSize:32, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'left',
  });
  slide.addText(lesson.warmUp.instruction, {
    x:0.5,y:2.2,w:12.3,h:1.0,
    fontSize:20, fontFace:FB, color:DARK,
    valign:'middle', align:'left', wrap:true,
  });
  slide.addShape(rr(pres), {
    x:0.5,y:3.35,w:12.3,h:1.1,
    fill:{color:WHITE}, line:{color:ORANGE,width:2}, rectRadius:0.1,
  });
  slide.addText(lesson.warmUp.sentence1, {
    x:0.7,y:3.4,w:11.9,h:1.0,
    fontSize:22, bold:true, fontFace:FH, color:ORANGE,
    valign:'middle', align:'center', wrap:true,
  });
  slide.addShape(rr(pres), {
    x:0.5,y:4.6,w:12.3,h:0.95,
    fill:{color:AMBER}, line:{width:0}, rectRadius:0.1,
  });
  slide.addText(lesson.warmUp.response, {
    x:0.7,y:4.65,w:11.9,h:0.85,
    fontSize:18, fontFace:FB, color:DARK,
    valign:'middle', align:'center', wrap:true,
  });
}

// ── Slide 7: Vocabulary ───────────────────────────────────────────────────────
function addVocab(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, 'El vocabulario nuevo — New vocabulary');

  const vocab = lesson.vocab;
  const COLS = 3;
  const rows = Math.ceil(vocab.length / COLS);
  const cW = 3.9, gX = 0.22;
  const cH = rows >= 2 ? 2.3 : 3.0;
  const gY = 0.18;
  const totalW = COLS*cW + (COLS-1)*gX;
  const startX = (13.3-totalW)/2;
  const startY = 0.95;

  vocab.forEach((v, i) => {
    const col = i % COLS;
    const row = Math.floor(i / COLS);
    const x = startX + col*(cW+gX);
    const y = startY + row*(cH+gY);

    slide.addShape(rr(pres), {
      x,y,w:cW,h:cH,
      fill:{color:WHITE}, line:{color:ORANGE,width:2}, rectRadius:0.1,
    });
    slide.addShape('rect', {
      x,y,w:cW,h:0.09, fill:{color:ORANGE}, line:{width:0},
    });
    slide.addText(v.sp, {
      x:x+0.1,y:y+0.1,w:cW-0.2,h:cH*0.44,
      fontSize:21, bold:true, fontFace:FH, color:DARK,
      valign:'middle', align:'center', wrap:true,
    });
    slide.addShape('rect', {
      x:x+0.1,y:y+cH*0.5,w:cW-0.2,h:0.04,
      fill:{color:AMBER}, line:{width:0},
    });
    slide.addText(v.pron, {
      x:x+0.1,y:y+cH*0.52,w:cW-0.2,h:cH*0.24,
      fontSize:12, italic:true, fontFace:FB, color:'7F8C8D',
      valign:'middle', align:'center',
    });
    slide.addText(v.eng, {
      x:x+0.1,y:y+cH*0.74,w:cW-0.2,h:cH*0.23,
      fontSize:16, fontFace:FB, color:ORANGE,
      valign:'middle', align:'center', wrap:true,
    });
  });

  slide.addShape(rr(pres), {
    x:0.5,y:6.5,w:12.3,h:0.72,
    fill:{color:ORANGE}, line:{width:0}, rectRadius:0.08,
  });
  slide.addText(`Key structure:   ${lesson.keyStructure}`, {
    x:0.7,y:6.52,w:11.9,h:0.68,
    fontSize:17, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'left',
  });
}

// ── Slide 8: Cultural ─────────────────────────────────────────────────────────
function addCultural(pres, lesson, imgData) {
  const slide = pres.addSlide();
  addBg(slide);

  if (imgData) {
    slide.addImage({
      data: imgData, x:0,y:0,w:8.5,h:7.5,
      sizing:{type:'cover',w:8.5,h:7.5},
    });
    slide.addShape('rect', {x:8.5,y:0,w:4.8,h:7.5, fill:{color:ORANGE}, line:{width:0}});
    slide.addShape('rect', {x:8.5,y:0,w:0.12,h:7.5, fill:{color:AMBER}, line:{width:0}});

    const c = lesson.cultural;
    slide.addText(c.heading, {
      x:8.68,y:0.55,w:4.4,h:0.75,
      fontSize:17, bold:true, fontFace:FH, color:AMBER,
      valign:'middle', align:'left', wrap:true,
    });
    slide.addText(c.fact, {
      x:8.68,y:1.5,w:4.4,h:2.6,
      fontSize:21, bold:true, fontFace:FB, color:WHITE,
      valign:'top', align:'left', wrap:true,
    });
    slide.addShape('rect', {x:8.7,y:4.2,w:4.0,h:0.07, fill:{color:AMBER}, line:{width:0}});
    slide.addText(c.detail, {
      x:8.68,y:4.4,w:4.4,h:2.5,
      fontSize:17, fontFace:FB, color:ORANGE_PALE,
      valign:'top', align:'left', wrap:true,
    });
  } else {
    // Card fallback
    addHeader(slide, '¿Recuerdas? — Can you remember?');
    const vocab = lesson.vocab;
    const cW=3.8, gX=0.22, cH=2.0, gY=0.18;
    const startX=(13.3-(3*cW+2*gX))/2;
    const startY=1.05;
    vocab.slice(0,6).forEach((v,i) => {
      const col=i%3, row=Math.floor(i/3);
      const x=startX+col*(cW+gX), y=startY+row*(cH+gY);
      const even=i%2===0;
      slide.addShape(rr(pres), {
        x,y,w:cW,h:cH,
        fill:{color:even?ORANGE:WHITE}, line:{color:AMBER,width:2}, rectRadius:0.1,
      });
      slide.addText(v.sp, {
        x:x+0.1,y:y+0.1,w:cW-0.2,h:cH*0.5,
        fontSize:20, bold:true, fontFace:FH, color:even?WHITE:DARK,
        valign:'middle', align:'center', wrap:true,
      });
      slide.addText(v.eng, {
        x:x+0.1,y:y+cH*0.52,w:cW-0.2,h:cH*0.44,
        fontSize:17, fontFace:FB, color:even?ORANGE_PALE:ORANGE,
        valign:'middle', align:'center', wrap:true,
      });
    });
    slide.addText('Cover the English — can you remember all the Spanish words?', {
      x:0.5,y:6.6,w:12.3,h:0.55,
      fontSize:15, italic:true, fontFace:FB, color:ORANGE,
      valign:'middle', align:'center',
    });
  }
}

// ── Slide 9/10/12: Activity ───────────────────────────────────────────────────
function addActivity(pres, lesson, idx) {
  const act = lesson.activities[idx];
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, `Actividad ${idx+1} — ${act.title}`);

  // Icon circle
  if (act.icon) {
    slide.addShape('ellipse', {
      x:0.4,y:1.0,w:1.35,h:1.35,
      fill:{color:ORANGE}, line:{color:AMBER,width:3},
    });
    slide.addText(act.icon, {
      x:0.4,y:1.0,w:1.35,h:1.35, fontSize:34,
      valign:'middle', align:'center',
    });
  }

  slide.addText(act.instruction, {
    x:2.05,y:1.0,w:11.0,h:1.5,
    fontSize:21, fontFace:FB, color:DARK,
    valign:'top', align:'left', wrap:true,
  });

  let nextY = 2.7;
  if (act.examples && act.examples.length) {
    act.examples.forEach((ex, i) => {
      const even=i%2===0;
      slide.addShape(rr(pres), {
        x:0.5,y:nextY,w:12.3,h:0.85,
        fill:{color:even?ORANGE:WHITE}, line:{color:ORANGE,width:2}, rectRadius:0.08,
      });
      slide.addText(ex, {
        x:0.7,y:nextY+0.02,w:11.9,h:0.8,
        fontSize:22, bold:true, fontFace:FH,
        color:even?WHITE:DARK,
        valign:'middle', align:'center', wrap:true,
      });
      nextY += 0.95;
    });
  }

  if (act.tip) {
    slide.addShape(rr(pres), {
      x:0.5,y:nextY+0.1,w:12.3,h:0.85,
      fill:{color:AMBER}, line:{width:0}, rectRadius:0.08,
    });
    slide.addText(`💡  ${act.tip}`, {
      x:0.7,y:nextY+0.15,w:11.9,h:0.75,
      fontSize:18, fontFace:FB, color:DARK,
      valign:'middle', align:'left', wrap:true,
    });
  }
}

// ── Slide 11: Phonics ─────────────────────────────────────────────────────────
function addPhonics(pres, lesson) {
  const slide = pres.addSlide();
  addBg(slide);
  addHeader(slide, `El sonido del día — Today's sound: ${lesson.phonicsLetter}`);

  // Big letter tile
  slide.addShape(rr(pres), {
    x:0.45,y:0.95,w:3.6,h:4.6,
    fill:{color:ORANGE}, line:{color:AMBER,width:5}, rectRadius:0.15,
  });
  slide.addText(lesson.phonicsLetter, {
    x:0.45,y:0.95,w:3.6,h:3.1,
    fontSize:lesson.phonicsLetter.length>1?80:110, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'center',
  });
  slide.addShape('rect', {
    x:0.45,y:4.05,w:3.6,h:1.5, fill:{color:AMBER}, line:{width:0},
  });
  slide.addText(lesson.phonicsSound, {
    x:0.45,y:4.1,w:3.6,h:1.4,
    fontSize:17, bold:true, fontFace:FB, color:DARK,
    valign:'middle', align:'center', wrap:true,
  });

  // Fact box
  slide.addShape(rr(pres), {
    x:4.3,y:0.95,w:8.6,h:1.9,
    fill:{color:WHITE}, line:{color:ORANGE,width:2}, rectRadius:0.1,
  });
  slide.addText(lesson.phonicsFact, {
    x:4.5,y:1.0,w:8.2,h:1.8,
    fontSize:19, fontFace:FB, color:DARK,
    valign:'middle', align:'left', wrap:true,
  });

  // Examples
  lesson.phonicsExamples.forEach((ex, i) => {
    const even=i%2===0;
    slide.addShape(rr(pres), {
      x:4.3,y:3.1+i*1.05,w:8.6,h:0.9,
      fill:{color:even?ORANGE:'F5CBA7'}, line:{color:AMBER,width:1}, rectRadius:0.08,
    });
    slide.addText(`${ex.word}   ·   ${ex.pron}   ·   ${ex.eng}`, {
      x:4.5,y:3.12+i*1.05,w:8.2,h:0.86,
      fontSize:19, bold:i===0, fontFace:FH,
      color:even?WHITE:DARK,
      valign:'middle', align:'left',
    });
  });

  slide.addText('Listen, repeat, get it right!', {
    x:0.5,y:6.6,w:12.3,h:0.6,
    fontSize:16, italic:true, fontFace:FB, color:ORANGE,
    valign:'middle', align:'center',
  });
}

// ── Slide 13: Round Off ───────────────────────────────────────────────────────
function addRoundOff(pres, lesson) {
  const slide = pres.addSlide();

  slide.addShape('rect', {x:0,y:0,w:13.3,h:7.5, fill:{color:ORANGE}, line:{width:0}});
  slide.addShape('rect', {x:0,y:6.85,w:13.3,h:0.65, fill:{color:AMBER}, line:{width:0}});

  slide.addText('¡Hasta luego!', {
    x:0.5,y:0.4,w:12.3,h:1.5,
    fontSize:56, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'center',
  });
  slide.addShape('rect', {x:0.8,y:2.05,w:11.7,h:0.09, fill:{color:AMBER}, line:{width:0}});

  slide.addShape(rr(pres), {
    x:0.8,y:2.3,w:11.7,h:2.2,
    fill:{color:WHITE}, line:{color:AMBER,width:3}, rectRadius:0.12,
  });
  slide.addText(lesson.roundOff, {
    x:1.0,y:2.35,w:11.3,h:2.1,
    fontSize:21, fontFace:FB, color:DARK,
    valign:'middle', align:'center', wrap:true,
  });

  slide.addShape(rr(pres), {
    x:0.8,y:4.8,w:11.7,h:1.35,
    fill:{color:'D4651C'}, line:{color:AMBER,width:2}, rectRadius:0.1,
  });
  slide.addText(`¿Puedes...?   ${lesson.lo}`, {
    x:1.0,y:4.85,w:11.3,h:1.25,
    fontSize:17, bold:true, fontFace:FH, color:WHITE,
    valign:'middle', align:'center', wrap:true,
  });

  slide.addText('Wallscourt Farm Academy · Spanish · Y5 · Aut 1', {
    x:0.5,y:6.88,w:12.3,h:0.42,
    fontSize:13, fontFace:FB, color:DARK,
    valign:'middle', align:'center',
  });
}

// ── Build one lesson ──────────────────────────────────────────────────────────
async function buildLesson(lesson) {
  const pres = new PptxGenJs();
  pres.layout = 'LAYOUT_WIDE';

  let imgData = null;
  const imgPath = `/home/claude/y5_l0${lesson.num}_img.jpg`;
  if (fs.existsSync(imgPath)) {
    const buf = fs.readFileSync(imgPath);
    imgData = 'image/jpeg;base64,' + buf.toString('base64');
    console.log(`  Image loaded: y5_l0${lesson.num}_img.jpg`);
  } else {
    console.log(`  No image — card fallback`);
  }

  addTitle(pres, lesson);       // 1: Title
  addLO(pres, lesson);          // 2: LO
  addVowels(pres);              // 3: Vowels
  addAlphabet(pres, lesson);    // 4: Alphabet
  addCounting(pres, lesson);    // 5: Counting
  addWarmUp(pres, lesson);      // 6: Warm-up
  addVocab(pres, lesson);       // 7: Vocab
  addCultural(pres, lesson, imgData); // 8: Cultural
  addActivity(pres, lesson, 0); // 9: Activity 1
  addActivity(pres, lesson, 1); // 10: Activity 2
  addPhonics(pres, lesson);     // 11: Phonics
  addActivity(pres, lesson, 2); // 12: Activity 3
  addRoundOff(pres, lesson);    // 13: Round off

  const outPath = `/home/claude/${lesson.fileOut}`;
  await pres.writeFile({ fileName: outPath });
  console.log(`  ✓ ${lesson.fileOut}`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  for (const lesson of DATA) {
    console.log(`\nL0${lesson.num}: ${lesson.titleSp}`);
    await buildLesson(lesson);
  }
  console.log('\n✅ All 6 lessons complete.');
})().catch(e => { console.error(e); process.exit(1); });
