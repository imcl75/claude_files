#!/usr/bin/env node
/**
 * generate_egypt_docx.js
 * Enquiry-planner extension: reads a History MTP JSON and produces a DOCX
 * planning document (human-readable, for teacher review) in the same format
 * as the existing enquiry-planner DOCX output.
 *
 * Usage:
 *   npm install docx
 *   node generate_egypt_docx.js egypt_mtp.json Egypt_Enquiry_Plan.docx
 *
 * The JSON itself is the MTP; this script turns it into a readable plan.
 * No flags or interactive prompts — all data comes from the JSON.
 */

'use strict';

const fs   = require('fs');
const path = require('path');

const {
  Document, Packer, Paragraph, Table, TableRow, TableCell,
  TextRun, HeadingLevel, AlignmentType, BorderStyle,
  WidthType, ShadingType, PageOrientation, Header,
  VerticalAlign, TableLayoutType,
} = require('docx');

// ── Colour palette (matches enquiry-planner SKILL.md) ────────────────────────
const C = {
  navyFill:    '1F3864',
  navyText:    'FFFFFF',
  phase1Fill:  'FFE6CC', phase1Text: '7D4000',
  phase2Fill:  'DAE8FC', phase2Text: '0D3D91',
  phase3Fill:  'D5E8D4', phase3Text: '1A5C1A',
  histAccent:  '8E3B2E',
  loHeader:    '1F3864',
  loRowA:      'F2F2F2',
  borderGrey:  'AAAAAA',
  conceptYellow: 'FFF2CC',
};

// ── DXA constants (1 inch = 1440 DXA; page = 11906 wide, landscape = 16838 high) ─
// Landscape A4 content width ≈ 15398 DXA (16838 - 2×720 margins)
const CONTENT_W = 15398;
const LABEL_W   = 4000;
const VALUE_W   = CONTENT_W - LABEL_W;

// ── Helpers ──────────────────────────────────────────────────────────────────

function cell(text, { fill, textColor = '000000', bold = false, sz = 20,
                       width, vAlign = VerticalAlign.TOP, colSpan } = {}) {
  const shading = fill
    ? { fill, type: ShadingType.SOLID, color: fill }
    : undefined;
  return new TableCell({
    shading,
    verticalAlign: vAlign,
    columnSpan: colSpan,
    width: width ? { size: width, type: WidthType.DXA } : undefined,
    children: [new Paragraph({
      alignment: AlignmentType.LEFT,
      children: [new TextRun({ text, bold, color: textColor, size: sz })],
    })],
  });
}

function labelCell(text) {
  return cell(text, {
    fill: C.navyFill, textColor: C.navyText,
    bold: true, sz: 20, width: LABEL_W,
  });
}

function valueCell(text, opts = {}) {
  return cell(text, { width: VALUE_W, sz: 20, ...opts });
}

function overviewRow(label, value, opts = {}) {
  return new TableRow({
    children: [labelCell(label), valueCell(value, opts)],
  });
}

function phaseColour(phase) {
  if (phase === 1) return { fill: C.phase1Fill, textColor: C.phase1Text };
  if (phase === 2) return { fill: C.phase2Fill, textColor: C.phase2Text };
  return                  { fill: C.phase3Fill, textColor: C.phase3Text };
}

function phaseName(phase) {
  return { 1: 'Discover', 2: 'Investigate', 3: 'Communicate' }[phase] || `Phase ${phase}`;
}

function skillDisplay(key) {
  return {
    questioning:     'Questioning & Understanding',
    chronology:      'Chronology',
    sources:         'Sources & Evidence',
    interpretations: 'Interpretations',
  }[key] || key;
}

// ── Unit Overview Table ──────────────────────────────────────────────────────

function buildOverviewTable(mtp) {
  const phases = mtp.phases || {};
  const phaseText = Object.entries(phases)
    .map(([n, p]) => `Phase ${n}: ${p.name} (L${p.lessons[0]}–L${p.lessons[p.lessons.length - 1]})`)
    .join(' / ');

  const skillsUsed = [...new Set(mtp.lessons.map(l => skillDisplay(l.skill_focus)))].join(', ');

  const diffGrid =
    'A — Identifies one historical source with support and locates Egypt on a map with a guide.\n' +
    'Y — Describes one source and explains what it tells us; places two key periods on a timeline.\n' +
    'O — Uses two or more sources; notes where accounts differ; places four or more periods correctly.\n' +
    'D — Selects sources independently; explains why accounts might differ; builds a reasoned argument about Egypt\'s legacy.';

  const rows = [
    overviewRow('Subject', `History — Being an Historian`),
    overviewRow('Topic', mtp.topic),
    overviewRow('Key Question', mtp.key_question),
    overviewRow('Challenge', mtp.challenge || '—'),
    overviewRow('NC Links',
      'History of the world — Ancient civilisations; historical skills of chronology, sources and evidence, questioning, and interpretations; comparing ancient civilisations with British history'),
    overviewRow('Duration', `${mtp.total_lessons} lessons (approximately 2 half-terms)`),
    overviewRow('Phase Structure', phaseText),
    overviewRow('Substantive Concept', 'Civilisation — "A civilisation is a group of people with their own languages and way of life. Civilised people live in organised groups like towns."'),
    overviewRow('Disciplinary Skills Focus', skillsUsed),
    overviewRow('Writing Outcome',
      `Genre: ${mtp.writing_outcome.genre} — ${mtp.writing_outcome.description}`),
    overviewRow('Enquiry Outcome', mtp.enquiry_outcome),
    overviewRow('Differentiation (Sources & Chronology)', diffGrid),
    overviewRow('Teacher Notes',
      '⚠ Prepare model non-chronological report before Lesson 10.\n' +
      '⚠ Gather artefact images/replica artefacts before Lesson 6.\n' +
      '⚠ Exhibition space needed for Lesson 14 — notify parents if opening to families.\n' +
      'Cross-curricular: links to geography (North Africa / River Nile); English (non-chronological report writing).'),
  ];

  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    layout: TableLayoutType.FIXED,
    rows,
  });
}

// ── Lesson Plan Section ──────────────────────────────────────────────────────

function buildLessonSection(lesson, mtp) {
  const phase    = lesson.phase;
  const pName    = phaseName(phase);
  const pColours = phaseColour(phase);

  const elements = [];

  // Lesson heading (navy background)
  elements.push(new Paragraph({
    children: [new TextRun({
      text: `Lesson ${lesson.lesson_number} — ${pName} — ${lesson.building_block_text}`,
      bold: true, size: 28, color: C.navyText,
    })],
    shading: { fill: C.navyFill, type: ShadingType.SOLID, color: C.navyFill },
    spacing: { before: 300, after: 100 },
  }));

  // Phase badge
  elements.push(new Paragraph({
    children: [new TextRun({
      text: `  Phase ${phase}: ${pName}  `,
      bold: true, size: 18, color: pColours.textColor,
    })],
    shading: { fill: pColours.fill, type: ShadingType.SOLID, color: pColours.fill },
    spacing: { before: 60, after: 200 },
  }));

  // LO table (3 rows × 2 cols)
  const loRows = [
    { label: 'We are learning to:',          value: lesson.what   || '' },
    { label: 'We are learning this because:', value: lesson.why    || '' },
    { label: 'I will show this by:',          value: lesson.success|| '' },
  ];
  elements.push(new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({
        children: [
          cell('Learning Objective', { fill: C.loHeader, textColor: C.navyText, bold: true, sz: 20, width: 4500 }),
          cell('',                   { fill: C.loHeader, textColor: C.navyText, bold: true, sz: 20, width: CONTENT_W - 4500 }),
        ],
      }),
      ...loRows.map((r, i) => new TableRow({
        children: [
          cell(r.label, { fill: i % 2 === 0 ? C.loRowA : 'FFFFFF', bold: true, sz: 18, width: 4500 }),
          cell(r.value, { fill: i % 2 === 0 ? 'FFFFFF' : C.loRowA, sz: 18, width: CONTENT_W - 4500 }),
        ],
      })),
    ],
  }));

  // Vocabulary
  elements.push(new Paragraph({
    children: [new TextRun({ text: 'VOCABULARY', bold: true, size: 20 })],
    spacing: { before: 200, after: 80 },
  }));
  (lesson.vocabulary || []).forEach((v, i) => {
    elements.push(new Paragraph({
      children: [
        new TextRun({ text: `${i + 1}. `, bold: true, size: 18 }),
        new TextRun({ text: `${v.word}`, bold: true, size: 18 }),
        new TextRun({ text: ` — ${v.definition}`, size: 18 }),
      ],
      spacing: { before: 60, after: 60 },
    }));
  });

  // Quiz
  elements.push(new Paragraph({
    children: [new TextRun({ text: 'RECAP QUIZ', bold: true, size: 20 })],
    spacing: { before: 200, after: 80 },
  }));
  const quiz = lesson.quiz || [];
  if (quiz.length === 0) {
    elements.push(new Paragraph({
      children: [new TextRun({ text: 'No quiz (first lesson — KWL activity instead)', size: 18, italics: true })],
    }));
  } else {
    quiz.forEach((q, i) => {
      elements.push(new Paragraph({
        children: [
          new TextRun({ text: `Q${i + 1}: `, bold: true, size: 18 }),
          new TextRun({ text: q.question, size: 18 }),
          new TextRun({ text: `  →  A: `, bold: true, size: 18, color: '1A5C2A' }),
          new TextRun({ text: q.answer, size: 18, color: '1A5C2A' }),
        ],
        spacing: { before: 60, after: 60 },
      }));
    });
  }

  // Skill focus
  elements.push(new Paragraph({
    children: [
      new TextRun({ text: 'Skill focus: ', bold: true, size: 18 }),
      new TextRun({ text: skillDisplay(lesson.skill_focus), size: 18 }),
      new TextRun({ text: `   Building block: `, bold: true, size: 18 }),
      new TextRun({ text: lesson.building_block_text, size: 18 }),
    ],
    spacing: { before: 160, after: 80 },
  }));

  // Slide plan table
  elements.push(new Paragraph({
    children: [new TextRun({ text: 'SLIDE PLAN', bold: true, size: 20 })],
    spacing: { before: 160, after: 80 },
  }));

  const slideTypeLabel = { i_do: 'I Do', we_do: 'We Do', you_do: 'You Do', you_do_trio: 'You Do (Trio)' };
  const slideColour   = {
    i_do:        { fill: 'DAE3F3', text: '0D3D91' },
    we_do:       { fill: 'D5E8D4', text: '1A5C1A' },
    you_do:      { fill: 'FFE6CC', text: '7D4000' },
    you_do_trio: { fill: 'EFE0FF', text: '4B0082' },
  };

  const slideRows = (lesson.slides || []).map(s => {
    const sc = slideColour[s.type] || { fill: 'EEEEEE', text: '000000' };
    return new TableRow({
      children: [
        cell(slideTypeLabel[s.type] || s.type, { fill: sc.fill, textColor: sc.text, bold: true, sz: 18, width: 2000 }),
        cell(s.title || '', { bold: true, sz: 18, width: 4000 }),
        cell(s.content || '', { sz: 16, width: CONTENT_W - 6000 }),
      ],
    });
  });

  if (slideRows.length > 0) {
    elements.push(new Table({
      width: { size: CONTENT_W, type: WidthType.DXA },
      layout: TableLayoutType.FIXED,
      rows: [
        new TableRow({
          children: [
            cell('Type',    { fill: C.navyFill, textColor: C.navyText, bold: true, sz: 18, width: 2000 }),
            cell('Title',   { fill: C.navyFill, textColor: C.navyText, bold: true, sz: 18, width: 4000 }),
            cell('Content', { fill: C.navyFill, textColor: C.navyText, bold: true, sz: 18, width: CONTENT_W - 6000 }),
          ],
        }),
        ...slideRows,
      ],
    }));
  }

  elements.push(new Paragraph({ children: [], spacing: { after: 400 } }));
  return elements;
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const [,, mtpPath, outPath] = process.argv;
  if (!mtpPath || !outPath) {
    console.error('Usage: node generate_egypt_docx.js <mtp.json> <output.docx>');
    process.exit(1);
  }

  const mtp = JSON.parse(fs.readFileSync(mtpPath, 'utf8'));

  const titleSection = [
    new Paragraph({
      children: [new TextRun({
        text: `${mtp.topic} — History Enquiry Plan`,
        bold: true, size: 40, color: C.histAccent,
      })],
      spacing: { after: 200 },
    }),
    new Paragraph({
      children: [new TextRun({
        text: `Key Question: ${mtp.key_question}`,
        bold: true, size: 24, italics: true,
      })],
      spacing: { after: 400 },
    }),
    new Paragraph({
      children: [new TextRun({ text: 'UNIT OVERVIEW', bold: true, size: 26 })],
      spacing: { after: 120 },
    }),
    buildOverviewTable(mtp),
    new Paragraph({ children: [], spacing: { after: 600 } }),
    new Paragraph({
      children: [new TextRun({ text: 'LESSON PLANS', bold: true, size: 26 })],
      spacing: { after: 200 },
    }),
  ];

  const lessonSections = mtp.lessons.flatMap(l => buildLessonSection(l, mtp));

  const doc = new Document({
    sections: [{
      properties: {
        page: {
          size: { width: 16838, height: 11906 },
          margin: { top: 720, bottom: 720, left: 720, right: 720 },
        },
      },
      children: [...titleSection, ...lessonSections],
    }],
  });

  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);
  console.log(`Written: ${outPath} (${(buf.length / 1024).toFixed(0)} KB)`);
}

main().catch(e => { console.error(e); process.exit(1); });
