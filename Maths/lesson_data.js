// lesson_data.js — T6W4 L13 Monday — Mixed numbers and improper fractions
// Type B: book-based (pupils write in maths books)
// LP type 'arithmetic' = full-page separate slides for LP1 and LP2

module.exports = {
  13: {
    iCan: [
      'I can convert a mixed number to an improper fraction',
      'I can convert an improper fraction to a mixed number',
    ],
    labelTopic: 'Fractions',

    // ── LP1: Mixed numbers → improper fractions ────────────────────────────
    lp1: {
      type: 'arithmetic',   // full-page separate slide
      topic: 'Fractions',
      title: 'Mixed numbers → improper fractions',
      answerPrompt: '×  +  =  ,  so the answer is',
      goingFurther: 'Find a mixed number that converts to an improper fraction with numerator 25. Explain how you found it.',
      questions: [
        { q: 'Write 2 and 3/4 as an improper fraction.\nShow your working.',  answer: '11/4'  },
        { q: 'Write 1 and 4/5 as an improper fraction.\nShow your working.',  answer: '9/5'   },
        { q: 'Write 3 and 2/3 as an improper fraction.\nShow your working.',  answer: '11/3'  },
        { q: 'Write 4 and 5/8 as an improper fraction.\nShow your working.',  answer: '37/8'  },
      ],
    },

    // ── LP2: Improper fractions → mixed numbers ────────────────────────────
    lp2: {
      type: 'arithmetic',
      topic: 'Fractions',
      title: 'Improper fractions → mixed numbers',
      answerPrompt: '÷  =  remainder  ,  so the answer is',
      goingFurther: 'Convert each of your LP2 answers back to an improper fraction. Do you get the same numbers you started with?',
      questions: [
        { q: 'Write 7/2 as a mixed number.\nShow your division.',   answer: '3 and 1/2' },
        { q: 'Write 14/3 as a mixed number.\nShow your division.',  answer: '4 and 2/3' },
        { q: 'Write 23/5 as a mixed number.\nShow your division.',  answer: '4 and 3/5' },
        { q: 'Write 31/8 as a mixed number.\nShow your division.',  answer: '3 and 7/8' },
      ],
    },

    // ── Adapted questions — include fraction circle visuals ────────────────
    adaptedSupport: {
      hint1: 'Mixed → improper: whole × denominator + numerator.\nImproper → mixed: numerator ÷ denominator, write remainder as fraction.',
      lp1Questions: [
        {
          q: 'Write 2 and 3/4 as an improper fraction.\n2 × 4 + 3 = ___',
          visual: { type: 'fraction_circles', denominator: 4, total: 11,
                    color: '#2565AE', show_labels: true, total_label: '' },
          visual_height: 0.90,
          answer: '11/4',
        },
        {
          q: 'Write 1 and 4/5 as an improper fraction.\n1 × 5 + 4 = ___',
          visual: { type: 'fraction_circles', denominator: 5, total: 9,
                    color: '#C83030', show_labels: true, total_label: '' },
          visual_height: 0.90,
          answer: '9/5',
        },
        {
          q: 'Write 3 and 2/3 as an improper fraction.\n3 × ___ + ___ = ___',
          answer: '11/3',
        },
        {
          q: 'Write 4 and 5/8 as an improper fraction.\n4 × ___ + ___ = ___',
          answer: '37/8',
        },
      ],
      lp2Questions: [
        {
          q: 'Write 7/2 as a mixed number.\n7 ÷ 2 = ___ remainder ___',
          visual: { type: 'fraction_circles', denominator: 2, total: 7,
                    color: '#2E8B3A', show_labels: true, total_label: '' },
          visual_height: 0.75,
          answer: '3 and 1/2',
        },
        {
          q: 'Write 14/3 as a mixed number.\n14 ÷ 3 = ___ remainder ___',
          visual: { type: 'fraction_circles', denominator: 3, total: 14,
                    color: '#D4A800', show_labels: true, total_label: '' },
          visual_height: 0.75,
          answer: '4 and 2/3',
        },
        {
          q: 'Write 23/5 as a mixed number.\n23 ÷ 5 = ___ remainder ___',
          answer: '4 and 3/5',
        },
        {
          q: 'Write 31/8 as a mixed number.\n31 ÷ 8 = ___ remainder ___',
          answer: '3 and 7/8',
        },
      ],
    },
  },
};
