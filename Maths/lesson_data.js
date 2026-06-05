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
      "I can plan my steps using a bar model and justify my answer."
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
      hint1: "Planning two steps:\n1. Draw a bar model — what do you know?\n2. What do you need to find first?\n3. Write step 1 and calculate it.\n4. Use that answer in step 2.",
      hint2: "For × and ÷ together:\n'How many in each group?' → ÷\n'How many altogether?' → ×\n\nAlways check: does my answer make sense?"
    }
  }

};

module.exports = LESSON_DATA_JS;
