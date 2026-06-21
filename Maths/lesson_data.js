// lesson_data.js — T6W2 Multiplication and Division (L5–L8)

const LESSON_DATA_JS = {

  5: {
    iCan: [
      "I can multiply a 4-digit number by a 1-digit number using short multiplication.",
      "I can regroup correctly and estimate to check my answer is reasonable."
    ],
    lp1: {
      title: "Short Multiplication",
      type: "arithmetic",
      instruction: "Use short multiplication to work out each calculation. Estimate first, then check your answer.",
      questions: [
        { q: "Work out 1,342 × 4", answer: "5,368" },
        { q: "Work out 2,135 × 6", answer: "12,810" },
        { q: "Work out 3,241 × 5", answer: "16,205" },
        { q: "Work out 1,824 × 7", answer: "12,768" },
      ],
      goingFurther: "What is the largest product you can make using the digits 2, 3, 4 and 5 as the multiplicand and a single digit of your choice as the multiplier? Explain how you know."
    },
    lp2: {
      title: "Multiplication — Reasoning",
      type: "arithmetic",
      instruction: "Solve each problem. Show your working clearly.",
      questions: [
        { q: "A school orders 1,356 exercise books for each of its 6 year groups. How many exercise books does it order in total?", answer: "8,136" },
        { q: "A factory produces 2,147 items each day. How many items does it produce in 8 days? Estimate first, then check how close your estimate was.", answer: "17,176" },
        { q: "True or false? 3,024 × 4 is greater than 12,000. Prove it.", answer: "False — 3,024 × 4 = 12,096, which is greater than 12,000. So it is true." },
      ],
      goingFurther: ""
    },
    adaptedSupport: {
      lp1Questions: [
        { q: "Work out 134 × 4", answer: "536" },
        { q: "Work out 213 × 3", answer: "639" },
      ],
      lp2Questions: [
        { q: "A shop has 1,250 pencils. It orders 3 times as many more. How many pencils does it order?", answer: "3,750" },
      ],
      hint1: "Short multiplication — steps:\n1. Start at the ONES column.\n2. Multiply by the single digit.\n3. Write the ones digit. regroup the tens digit.\n4. Move to TENS: multiply, then add any regroup.\n5. Keep going left until finished.",
      hint2: "Example: 236 × 4\nOnes: 6×4=24 → write 4, regroup 2\nTens: 3×4=12, +2=14 → write 4, regroup 1\nHundreds: 2×4=8, +1=9\nAnswer: 944"
    }
  },

  6: {
    iCan: [
      "I can divide a 4-digit number by a 1-digit number using short division.",
      "I can regroup remainders correctly and interpret any remainder in context."
    ],
    lp1: {
      title: "Short Division",
      type: "arithmetic",
      instruction: "Use short division (bus stop) to work out each calculation. Write any remainder as 'r N'.",
      questions: [
        { q: "Work out 6,484 ÷ 4", answer: "1,621" },
        { q: "Work out 9,369 ÷ 3", answer: "3,123" },
        { q: "Work out 7,256 ÷ 8", answer: "907" },
        { q: "Work out 5,473 ÷ 6", answer: "912 r1" },
      ],
      goingFurther: "Without calculating, explain how you know that 4,357 ÷ 5 will have a remainder. What will the remainder be?"
    },
    lp2: {
      title: "Division — Reasoning",
      type: "arithmetic",
      instruction: "Solve each problem. Show your working and interpret any remainder.",
      questions: [
        { q: "3,672 stickers are shared equally between 8 children. How many stickers does each child receive? Are any left over?", answer: "459 each, with 0 remainder — divided exactly." },
        { q: "A baker makes 5,485 biscuits and packs them into bags of 6. How many complete bags can she fill? How many biscuits are left over?", answer: "914 complete bags, with 1 biscuit left over." },
        { q: "A coach company has 4,239 passengers to transport. Each coach holds 9 passengers. How many coaches are needed? Explain why your answer is not simply 4,239 ÷ 9.", answer: "471 coaches — 4,239 ÷ 9 = 471 exactly, so exactly 471 coaches." },
      ],
      goingFurther: ""
    },
    adaptedSupport: {
      lp1Questions: [
        { q: "Work out 848 ÷ 4", answer: "212" },
        { q: "Work out 756 ÷ 3", answer: "252" },
      ],
      lp2Questions: [
        { q: "672 biscuits are packed into boxes of 4. How many boxes are there? Are any left over?", answer: "168 boxes, no remainder." },
      ],
      hint1: "Short division — steps (bus stop):\n1. Write the divisor outside, dividend inside.\n2. Start at the LEFT (largest digit).\n3. Divide: write quotient digit ABOVE.\n4. If there is a remainder, write it small before the next digit.\n5. regroup on until you reach the last digit.",
      hint2: "Example: 8,484 ÷ 4\n8÷4=2 (above 8)\n4÷4=1 (above 4)\n8÷4=2 (above 8)\n4÷4=1 (above 4)\nAnswer: 2,121"
    }
  },

  7: {
    iCan: [
      "I can solve one-step and two-step problems involving multiplication.",
      "I can choose an efficient method and show each step clearly."
    ],
    lp1: {
      title: "Multiplication Problems",
      type: "arithmetic",
      instruction: "Solve each problem. Estimate first, then calculate. Show all your working.",
      questions: [
        { q: "A publisher prints 2,354 copies of a book. How many copies are printed in 6 runs?", answer: "14,124" },
        { q: "A theatre has 1,478 seats. All seats are sold for 8 performances. How many tickets are sold altogether?", answer: "11,824" },
        { q: "A warehouse has 1,025 boxes on each of its 9 shelves. How many boxes in total?", answer: "9,225" },
      ],
      goingFurther: "A school hall has 48 rows of 27 seats. A teacher estimates this is about 1,500 seats. Is this a good estimate? Work out the exact answer."
    },
    lp2: {
      title: "Two-Step Multiplication",
      type: "arithmetic",
      instruction: "Each problem needs two steps. Show both clearly.",
      questions: [
        { q: "A shop sells 1,256 red pens per week. It sells 3 times as many blue pens. How many pens altogether does it sell in one week?", answer: "Step 1: 1,256 × 3 = 3,768 blue pens. Step 2: 1,256 + 3,768 = 5,024 total pens." },
        { q: "A farmer picks 2,135 apples from one orchard and 4 times as many from a second orchard. He sells 3,000 apples. How many does he have left?", answer: "Step 1: 2,135 × 4 = 8,540. Step 2: 8,540 + 2,135 = 10,675 − 3,000 = 7,675." },
      ],
      goingFurther: ""
    },
    adaptedSupport: {
      lp1Questions: [
        { q: "A shop orders 342 items each month. How many items in 4 months?", answer: "1,368" },
        { q: "A farmer has 1,125 chickens on each of his 3 farms. How many chickens altogether?", answer: "3,375" },
      ],
      lp2Questions: [
        { q: "A factory makes 1,250 parts in the morning. It makes 3 times as many in the afternoon. How many parts in total?", answer: "Morning: 1,250. Afternoon: 1,250 × 3 = 3,750. Total: 1,250 + 3,750 = 5,000." },
      ],
      hint1: "Two-step problems — plan first:\n1. Read the question carefully.\n2. Underline the key information.\n3. Ask: what do I need to find FIRST?\n4. Write step 1, calculate, then do step 2.",
      hint2: "Key words for multiplication:\n'times as many' → ×\n'each, every, per' → ×\n'product' → ×\n\nEstimate before you calculate!"
    }
  },

  8: {
    iCan: [
      "I can solve two-step problems using both multiplication and division.",
      "I can plan and justify the steps needed to solve a two-step problem."
    ],
    lp1: {
      title: "Mixed × and ÷ Problems",
      type: "arithmetic",
      instruction: "Plan your steps before calculating. Show all your working.",
      questions: [
        { q: "5,640 apples are packed into boxes of 8. Then 3 boxes are set aside for display. How many boxes are left for sale?", answer: "5,640 ÷ 8 = 705 boxes. 705 − 3 = 702 boxes for sale." },
        { q: "A factory makes 1,425 parts per hour and runs for 6 hours. The parts are shared equally between 9 warehouses. How many parts go to each warehouse?", answer: "1,425 × 6 = 8,550. 8,550 ÷ 9 = 950 parts per warehouse." },
        { q: "There are 3,600 raffle tickets. They are sold in books of 8 tickets. Each seller is given 9 books. How many sellers are there?", answer: "3,600 ÷ 8 = 450 books. 450 ÷ 9 = 50 sellers." },
      ],
      goingFurther: "Write your own two-step × and ÷ word problem with an answer of 360. Swap with a partner."
    },
    lp2: {
      title: "Reasoning — Justify Your Answer",
      type: "arithmetic",
      instruction: "Solve each problem. Explain your reasoning clearly — not just the answer, but why.",
      questions: [
        { q: "Afia says: '4,500 ÷ 6 is less than 1,250 × 3.' Is she correct? Show working to prove your answer.", answer: "4,500 ÷ 6 = 750. 1,250 × 3 = 3,750. 750 < 3,750 so Afia is correct." },
        { q: "A coach company charges £1,350 per coach. A school needs 8 coaches. The school has a budget of £12,000. Does it have enough money? Explain with a calculation.", answer: "8 × £1,350 = £10,800. £10,800 < £12,000, so yes, the school has enough money." },
      ],
      goingFurther: ""
    },
    adaptedSupport: {
      lp1Questions: [
        { q: "480 chairs are arranged in rows of 8. Then 5 rows are removed for a stage. How many rows are left?", answer: "480 ÷ 8 = 60 rows. 60 − 5 = 55 rows left." },
        { q: "A baker makes 1,200 biscuits each day for 5 days. He packs them into boxes of 6. How many boxes does he fill?", answer: "1,200 × 5 = 6,000. 6,000 ÷ 6 = 1,000 boxes." },
      ],
      lp2Questions: [
        { q: "There are 360 books to share equally between 9 shelves. Then 8 more books arrive. How many books are on the first shelf now?", answer: "360 ÷ 9 = 40. 40 + 8 = 48 books (if all extra books go to one shelf)." },
      ],
      hint1: "Planning two steps:\n1. What do you know? Write it down.\n2. What do you need to find first?\n3. Write step 1 and calculate it.\n4. Use that answer in step 2.",
      hint2: "For × and ÷ together:\n'How many in each group?' → ÷\n'How many altogether?' → ×\n\nAlways check: does my answer make sense?"
    }
  }

};

module.exports = LESSON_DATA_JS;

// ── T6W3 ──────────────────────────────────────────────────────────────────────

module.exports[9] = {
  iCan: [
    'I can identify which operation a problem needs.',
    'I can find clues in a word problem to choose the right calculation.',
  ],
  lp1: {
    title: 'Identify the Operation',
    type: 'arithmetic',
    typeA: true,
    answerPrompt: 'Operation: ________________________________',
    instruction: 'For each problem, write the operation and explain why.',
    questions: [
      {
        q: 'There are 6 boxes. Each box holds 8 pencils. How many pencils are there altogether?',
        answer: '× (multiply) — "each" and "altogether" show equal groups. 6 × 8 = 48 pencils.',
      },
      {
        q: '24 grapes are shared equally between 4 children. How many does each child get?',
        answer: '÷ (divide) — "shared equally" means splitting into equal groups. 24 ÷ 4 = 6 grapes.',
      },
      {
        q: 'A bag had 45 sweets. Some were eaten. There are 27 left. How many were eaten?',
        answer: '− (subtract) — we know the total and one part, so we find the difference. 45 − 27 = 18.',
      },
    ],
    goingFurther: 'Write one problem each for + and ×. Make the signal word easy to spot.',
  },
  lp2: {
    title: 'Find the Operation',
    type: 'arithmetic',
    typeA: true,
    answerPrompt: 'Operation: ________________________________',
    instruction: 'Identify the operation. Explain what tells you — no obvious signal word here.',
    questions: [
      {
        q: 'I have 48 biscuits. I put 8 in each tin. How many tins do I need?',
        answer: '÷ — the structure shows grouping: how many groups of 8 in 48? 48 ÷ 8 = 6 tins.',
      },
      {
        q: 'Ella reads 9 pages a day. How many pages does she read in 7 days?',
        answer: '× — equal amounts repeated daily means multiply. 9 × 7 = 63 pages.',
      },
      {
        q: 'A bag has red and blue counters. There are 35 red and 16 blue. How many in total?',
        answer: '+ — two separate amounts being combined. 35 + 16 = 51 counters.',
      },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      {
        q: 'There are 4 bags. Each bag has 5 apples. How many apples are there?',
        answer: '× — "each" shows equal groups. 4 × 5 = 20 apples.',
      },
      {
        q: '18 children are split into 3 equal teams. How many children in each team?',
        answer: '÷ — "split into equal teams" shows division. 18 ÷ 3 = 6 children.',
      },
    ],
    lp2Questions: [
      {
        q: 'There are 5 children. Each child has 4 crayons. How many crayons are there?',
        answer: '× — "each" shows equal groups. 5 × 4 = 20 crayons.',
      },
    ],
    hint1: 'Signal words:\n× "each", "groups of", "times as many"\n÷ "shared equally", "split into", "each"\n+ "altogether", "total", "in all"\n− "left", "difference", "how many more"',
    hint2: 'Ask: am I combining, splitting, grouping, or comparing?\nCombine → +\nFind what\'s left → −\nEqual groups (find total) → ×\nEqual groups (find how many) → ÷',
  },
};

module.exports[10] = {
  iCan: [
    'I can follow the two-step routine.',
    'I can solve word problems using all four operations.',
  ],
  lp1: {
    title: 'Multiply and Divide',
    type: 'arithmetic',
    compact: true,
    instruction: 'Name the operation, then calculate.',
    questions: [
      {
        q: 'A class has 6 tables. Each table has 4 chairs. How many chairs altogether?',
        answer: '×: 6 × 4 = 24 chairs.',
      },
      {
        q: '32 pencils are shared equally between 4 pots. How many pencils in each pot?',
        answer: '÷: 32 ÷ 4 = 8 pencils.',
      },
      {
        q: 'There are 9 bags of marbles. Each bag has 7 marbles. How many marbles in total?',
        answer: '×: 9 × 7 = 63 marbles.',
      },
    ],
    goingFurther: 'Solve: "48 children sit at tables of 8. Each table needs a pencil pot. How many pots?" Show both steps.',
  },
  lp2: {
    title: 'Mixed Operations',
    type: 'arithmetic',
    compact: true,
    instruction: 'For each problem: name the operation, then solve.',
    questions: [
      {
        q: 'There are 56 children. 24 go home for lunch. How many stay at school?',
        answer: '−: 56 − 24 = 32 children.',
      },
      {
        q: 'A baker makes 8 loaves a day for 6 days. How many loaves does he make?',
        answer: '×: 8 × 6 = 48 loaves.',
      },
      {
        q: 'Tom has 37 stickers. Jo has 25. How many do they have altogether?',
        answer: '+: 37 + 25 = 62 stickers.',
      },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      {
        q: 'There are 3 bags. Each has 6 apples. How many apples altogether?',
        answer: '×: 3 × 6 = 18 apples.',
      },
      {
        q: '24 books are shared equally between 4 shelves. How many books per shelf?',
        answer: '÷: 24 ÷ 4 = 6 books.',
      },
    ],
    lp2Questions: [
      {
        q: 'There are 5 baskets. Each has 3 oranges. How many oranges altogether?',
        answer: '×: 5 × 3 = 15 oranges.',
      },
    ],
    hint1: 'Two-step routine:\n1. What is the question asking?\n2. Which operation? (× groups together, ÷ splits equally, + combines, − finds what\'s left)\n3. Write the calculation.\n4. Calculate.',
    hint2: 'For ×: number of groups × size of each group\nFor ÷: total ÷ number of groups\nAlways write the operation before you calculate.',
  },
};

module.exports[11] = {
  iCan: [
    'I can plan the steps needed to solve a two-step problem.',
    'I can work through steps in the correct order.',
  ],
  lp1: {
    title: 'Two-Step Problems',
    type: 'arithmetic',
    compact: true,
    instruction: 'Show your working. Label the operation for each step.',
    questions: [
      {
        q: 'There are 5 bags of crayons. Each bag has 8 crayons. 4 crayons break. How many good crayons are there?',
        answer: 'Step 1: 5 × 8 = 40. Step 2: 40 − 4 = 36 good crayons.',
      },
      {
        q: '36 apples are shared equally between 6 boxes. Then 3 more apples are added to each box. How many are in each box now?',
        answer: 'Step 1: 36 ÷ 6 = 6. Step 2: 6 + 3 = 9 apples per box.',
      },
    ],
    goingFurther: 'Write your own two-step problem where the answer to Step 1 is used in Step 2.',
  },
  lp2: {
    title: 'Plan Your Steps',
    type: 'arithmetic',
    compact: true,
    instruction: 'Show your working. Label the operation for each step.',
    questions: [
      {
        q: 'A footballer scores 6 goals in each of 4 matches. He scores 3 more in a fifth match. How many goals in total?',
        answer: 'Step 1: 6 × 4 = 24. Step 2: 24 + 3 = 27 goals.',
      },
      {
        q: '48 books are split equally onto 6 shelves. Then 4 books are removed from each shelf. How many are on each shelf now?',
        answer: 'Step 1: 48 ÷ 6 = 8. Step 2: 8 − 4 = 4 books.',
      },
      {
        q: 'Each child in a group of 5 brings 8 sweets. They split all the sweets equally into 4 bags. How many sweets in each bag?',
        answer: 'Step 1: 5 × 8 = 40. Step 2: 40 ÷ 4 = 10 sweets.',
      },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      {
        q: 'There are 4 bags of apples. Each bag has 5 apples. 2 apples are eaten. How many are left?',
        answer: 'Step 1: 4 × 5 = 20. Step 2: 20 − 2 = 18 apples.',
      },
      {
        q: '18 children are split into 3 equal groups. Each group gets 2 extra children. How many are in each group now?',
        answer: 'Step 1: 18 ÷ 3 = 6. Step 2: 6 + 2 = 8 children.',
      },
    ],
    lp2Questions: [
      {
        q: 'There are 3 bags of 7 grapes. Then 5 grapes are eaten. How many grapes are left?',
        answer: 'Step 1: 3 × 7 = 21. Step 2: 21 − 5 = 16 grapes.',
      },
    ],
    hint1: 'Planning two steps:\n1. What do you know? Write it down.\n2. Solve Step 1 first.\n3. Use that answer for Step 2.',
    hint2: 'Can you do Step 2 without knowing the answer to Step 1?\nIf not — that tells you the correct order.\nAlways check: does my final answer make sense?',
  },
};

module.exports[12] = {
  iCan: [
    'I can solve money and measurement problems.',
    'I can include the correct unit in every answer.',
  ],
  lp1: {
    title: 'Money Problems',
    type: 'arithmetic',
    compact: true,
    instruction: 'Identify the operation, show your working, include the unit (p or £).',
    questions: [
      {
        q: 'Pencils cost 15p each. I buy 6. How much do I spend?',
        answer: '×: 15 × 6 = 90p',
      },
      {
        q: 'I have £2 (= 200p). I spend 75p. How much change do I get? Give your answer in pence.',
        answer: '−: 200 − 75 = 125p',
      },
      {
        q: '4 children share 120p equally. How many pence does each child get?',
        answer: '÷: 120 ÷ 4 = 30p',
      },
    ],
    goingFurther: 'A book costs 85p. I buy 3 books and pay with a £5 note. How much change? Show both steps.',
  },
  lp2: {
    title: 'Measurement Problems',
    type: 'arithmetic',
    compact: true,
    instruction: 'Identify the operation, show working, include the unit.',
    questions: [
      {
        q: 'A bag of flour weighs 250 g. How much do 6 bags weigh?',
        answer: '×: 250 × 6 = 1,500 g',
      },
      {
        q: 'A piece of ribbon is 72 cm long. It is cut into 8 equal pieces. How long is each piece?',
        answer: '÷: 72 ÷ 8 = 9 cm',
      },
      {
        q: 'A shelf is 90 cm long. A book is 9 cm wide. How many books fit on the shelf?',
        answer: '÷: 90 ÷ 9 = 10 books',
      },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      {
        q: 'Stickers cost 10p each. I buy 5. How much do I spend?',
        answer: '×: 10 × 5 = 50p',
      },
      {
        q: 'I have 80p. I spend 35p. How much is left?',
        answer: '−: 80 − 35 = 45p',
      },
    ],
    lp2Questions: [
      {
        q: 'A bag of apples weighs 300 g. There are 6 apples in the bag. How heavy is each apple?',
        answer: '÷: 300 ÷ 6 = 50 g',
      },
    ],
    hint1: 'Money operations:\n× when buying several of the same item\n÷ when sharing money equally\n+ when combining amounts\n− when finding change or what is left\n\nAlways check: is your answer in p or £?',
    hint2: 'For measurement:\nAlways include the unit in your answer (g, kg, cm, m).\nCheck: does the size of your answer make sense?\n(50 g for one apple sounds right — 5,000 g would not!)',
  },
};

// ── T6W4 — Fractions (L13–L16) ────────────────────────────────────────────────

module.exports[13] = {
  iCan: [
    'I can convert a mixed number to an improper fraction.',
    'I can convert an improper fraction back to a mixed number.',
  ],
  lp1: {
    title: 'Mixed Numbers to Improper Fractions',
    type: 'arithmetic',
    compact: true,
    instruction: 'Convert each mixed number to an improper fraction. Show your working.',
    questions: [
      { q: 'Convert 1 3/4 to an improper fraction.',  answer: '1 × 4 + 3 = 7. Answer: 7/4' },
      { q: 'Convert 2 2/3 to an improper fraction.',  answer: '2 × 3 + 2 = 8. Answer: 8/3' },
      { q: 'Convert 3 1/5 to an improper fraction.',  answer: '3 × 5 + 1 = 16. Answer: 16/5' },
      { q: 'Convert 4 3/8 to an improper fraction.',  answer: '4 × 8 + 3 = 35. Answer: 35/8' },
    ],
    goingFurther: 'Write three different mixed numbers that all have a denominator of 6. Convert each to an improper fraction. What do you notice about the numerators?',
  },
  lp2: {
    title: 'Improper Fractions to Mixed Numbers',
    type: 'arithmetic',
    compact: true,
    instruction: 'Convert each improper fraction to a mixed number. Use division.',
    questions: [
      { q: 'Convert 9/4 to a mixed number.',   answer: '9 ÷ 4 = 2 remainder 1. Answer: 2 1/4' },
      { q: 'Convert 13/3 to a mixed number.',  answer: '13 ÷ 3 = 4 remainder 1. Answer: 4 1/3' },
      { q: 'Convert 22/5 to a mixed number.',  answer: '22 ÷ 5 = 4 remainder 2. Answer: 4 2/5' },
      { q: 'Convert 41/8 to a mixed number.',  answer: '41 ÷ 8 = 5 remainder 1. Answer: 5 1/8' },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      { q: 'Convert 1 1/2 to an improper fraction.',  answer: '1 × 2 + 1 = 3. Answer: 3/2' },
      { q: 'Convert 2 3/4 to an improper fraction.',  answer: '2 × 4 + 3 = 11. Answer: 11/4' },
    ],
    lp2Questions: [
      { q: 'Convert 5/2 to a mixed number.',  answer: '5 ÷ 2 = 2 remainder 1. Answer: 2 1/2' },
      { q: 'Convert 7/4 to a mixed number.',  answer: '7 ÷ 4 = 1 remainder 3. Answer: 1 3/4' },
    ],
    hint1: 'Mixed number → improper fraction:\n1. Multiply the whole number by the denominator.\n2. Add the numerator.\n3. Write the total over the same denominator.\nExample: 2 3/4 → 2 × 4 = 8, + 3 = 11 → 11/4',
    hint2: 'Improper fraction → mixed number:\n1. Divide the numerator by the denominator.\n2. The answer is the whole number.\n3. The remainder is the new numerator.\nExample: 9/4 → 9 ÷ 4 = 2 remainder 1 → 2 1/4',
  },
};

module.exports[14] = {
  iCan: [
    'I can add fractions with the same denominator.',
    'I can add fractions that cross the whole and write the answer as a mixed number.',
  ],
  lp1: {
    title: 'Adding Fractions',
    type: 'arithmetic',
    compact: true,
    instruction: 'Add the fractions. Remember — only the numerators add.',
    questions: [
      { q: '2/9 + 5/9 = ?',    answer: '7/9' },
      { q: '1/8 + 4/8 = ?',    answer: '5/8' },
      { q: '3/7 + 2/7 = ?',    answer: '5/7' },
      { q: '4/10 + 3/10 = ?',  answer: '7/10' },
    ],
    goingFurther: 'Can you find two fractions, both with denominator 8, that add to make exactly 1 whole? How many different pairs can you find?',
  },
  lp2: {
    title: 'Adding Fractions — Crossing the Whole',
    type: 'arithmetic',
    compact: true,
    instruction: 'Add the fractions. Convert your answer to a mixed number.',
    questions: [
      { q: '5/6 + 4/6 = ?',    answer: '9/6 = 1 3/6' },
      { q: '7/8 + 5/8 = ?',    answer: '12/8 = 1 4/8' },
      { q: '3/4 + 3/4 = ?',    answer: '6/4 = 1 2/4' },
      { q: '8/10 + 7/10 = ?',  answer: '15/10 = 1 5/10' },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      { q: '1/4 + 2/4 = ?',  answer: '3/4' },
      { q: '2/5 + 2/5 = ?',  answer: '4/5' },
    ],
    lp2Questions: [
      { q: '3/4 + 3/4 = ?',  answer: '6/4 = 1 2/4' },
    ],
    hint1: 'Adding fractions — same denominator:\n1. Check the denominators match.\n2. Add only the numerators.\n3. The denominator stays the same.\nExample: 2/7 + 3/7 = 5/7',
    hint2: 'Crossing the whole:\nIf your numerator is bigger than the denominator, convert.\nExample: 11/8 → 11 ÷ 8 = 1 remainder 3 → 1 3/8',
  },
};

module.exports[15] = {
  iCan: [
    'I can subtract fractions with the same denominator.',
    'I can subtract fractions from a mixed number by exchanging one whole.',
  ],
  lp1: {
    title: 'Subtracting Fractions',
    type: 'arithmetic',
    compact: true,
    instruction: 'Subtract the fractions. Show your working.',
    questions: [
      { q: '5/7 − 2/7 = ?',       answer: '3/7' },
      { q: '7/9 − 3/9 = ?',       answer: '4/9' },
      { q: '8/10 − 5/10 = ?',     answer: '3/10' },
      { q: '2 5/6 − 3/6 = ?',     answer: '2 2/6' },
      { q: '3 7/8 − 4/8 = ?',     answer: '3 3/8' },
      { q: '5 6/9 − 4/9 = ?',     answer: '5 2/9' },
    ],
    goingFurther: "Zara says 6/7 − 3/7 = 3. Explain what mistake she made and write the correct answer.",
  },
  lp2: {
    title: 'Subtracting — Crossing the Whole',
    type: 'arithmetic',
    compact: true,
    instruction: 'You will need to exchange one whole. Show each step.',
    questions: [
      { q: '2 1/5 − 3/5 = ?',     answer: 'Exchange: 7/5 − 3/5 = 4/5. Answer: 1 4/5' },
      { q: '3 2/8 − 5/8 = ?',     answer: 'Exchange: 10/8 − 5/8 = 5/8. Answer: 2 5/8' },
      { q: '1 3/10 − 7/10 = ?',   answer: 'Exchange: 13/10 − 7/10 = 6/10. Answer: 6/10' },
      { q: '4 1/6 − 4/6 = ?',     answer: 'Exchange: 7/6 − 4/6 = 3/6. Answer: 3 3/6' },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      { q: '5/6 − 2/6 = ?',  answer: '3/6' },
      { q: '7/8 − 3/8 = ?',  answer: '4/8' },
    ],
    lp2Questions: [
      { q: '2 1/4 − 3/4 = ?',  answer: 'Exchange: 5/4 − 3/4 = 2/4. Answer: 1 2/4' },
    ],
    hint1: 'Subtracting fractions:\n1. Check denominators match.\n2. Subtract numerators only.\n3. Denominator stays the same.\nExample: 6/9 − 2/9 = 4/9',
    hint2: 'Exchanging a whole:\nIf the top numerator is too small, exchange.\n1 whole = denominator/denominator (e.g. 1 = 8/8)\nAdd that to your fraction, then subtract.\nExample: 2 3/8 − 7/8: exchange → 11/8 − 7/8 = 4/8. Answer: 1 4/8',
  },
};

module.exports[16] = {
  iCan: [
    'I can find a fraction of an amount by dividing and multiplying.',
    'I can use fractions of amounts to solve word problems.',
  ],
  lp1: {
    title: 'Fractions of Amounts',
    type: 'arithmetic',
    compact: true,
    instruction: 'Find each fraction of the amount. Show your working.',
    questions: [
      { q: 'Find 1/4 of 240.',   answer: '240 ÷ 4 = 60' },
      { q: 'Find 3/4 of 240.',   answer: '240 ÷ 4 = 60, then × 3 = 180' },
      { q: 'Find 1/5 of 3,500.', answer: '3,500 ÷ 5 = 700' },
      { q: 'Find 2/5 of 3,500.', answer: '3,500 ÷ 5 = 700, then × 2 = 1,400' },
      { q: 'Find 2/3 of 720.',   answer: '720 ÷ 3 = 240, then × 2 = 480' },
      { q: 'Find 3/8 of 1,600.', answer: '1,600 ÷ 8 = 200, then × 3 = 600' },
    ],
    goingFurther: 'Which is greater — 3/4 of 480 or 5/6 of 360? Show your working to prove your answer.',
  },
  lp2: {
    title: 'Fraction Word Problems',
    type: 'arithmetic',
    compact: true,
    instruction: 'Solve each problem. Show all your working.',
    questions: [
      { q: 'A baker has 840 g of flour. He uses 2/3 of it to make bread. How much flour does he use?', answer: '840 ÷ 3 = 280, then × 2 = 560 g' },
      { q: 'After spending 1/4 of her savings, Maya has £180 left. How much did she start with?', answer: '£180 is 3/4. So 1/4 = £60. Total = 4 × £60 = £240.' },
      { q: '3/5 of the children in a school of 650 travel by bus. How many travel by bus? How many do not?', answer: '650 ÷ 5 = 130, × 3 = 390 by bus. 650 − 390 = 260 do not.' },
    ],
  },
  adaptedSupport: {
    lp1Questions: [
      { q: 'Find 1/2 of 360.',  answer: '360 ÷ 2 = 180' },
      { q: 'Find 1/4 of 120.',  answer: '120 ÷ 4 = 30' },
      { q: 'Find 3/4 of 120.',  answer: '120 ÷ 4 = 30, then × 3 = 90' },
    ],
    lp2Questions: [
      { q: 'A box has 60 chocolates. 1/3 are milk chocolate. How many are milk chocolate?', answer: '60 ÷ 3 = 20 milk chocolate.' },
    ],
    hint1: 'Fractions of amounts:\nStep 1 — Divide by the DENOMINATOR to find 1 part.\nStep 2 — Multiply by the NUMERATOR to find your fraction.\nExample: 3/4 of 80: 80 ÷ 4 = 20, then × 3 = 60',
    hint2: 'Working backwards:\nIf you know the fraction that is LEFT, find the whole part first.\nExample: 3/4 left = £180. So 1/4 = £60. Whole = 4 × £60 = £240.',
  },
};
