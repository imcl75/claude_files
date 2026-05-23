/**
 * lesson_data.js — Hand-authored per-lesson LP data
 * Used by build_lp_v3.js
 *
 * Each lesson entry contains:
 *   lp1:           { title, instruction, questions[], goingFurther }
 *   lp2:           { title, instruction, questions[], goingFurther }
 *   adaptedSupport: { lp1Questions[], lp2Questions[], hint1, hint2 }
 *   iCan:          [ "I can ...", "I can ..." ]  — overrides JSON-derived lines if needed
 */

const BLUE   = "1F4E79";
const RED    = "C00000";
const PURPLE = "7030A0";

module.exports = {

// ---------------------------------------------------------------------------
// LESSON 1 — T5W1 Monday — Directions on a grid
// ---------------------------------------------------------------------------
1: {
  iCan: [
    "I can write directions using left / right / up / down",
    "I can check directions by tracing the route",
  ],
  lp1: {
    title: "Directions on a Grid",
    questions: [
      { start:[1,1], end:[4,3], answer:"3 right, 2 up"   },
      { start:[2,4], end:[5,2], answer:"3 right, 2 down" },
      { start:[3,1], end:[1,4], answer:"2 left, 3 up"    },
      { start:[1,3], end:[4,5], answer:"3 right, 2 up"   },
    ],
    goingFurther: "Can you find two different direction routes that both get from A to B?\n\nDraw both routes on Q1 and write each set of directions.",
  },
  lp2: {
    title: "Three-Stop Journeys",
    instruction: "Each journey visits A → B → C.  Write the directions for each leg.",
    questions: [
      { pts:[[1,1,"A",BLUE],[3,2,"B",PURPLE],[5,4,"C",RED]], a1:"2 right, 1 up",   a2:"2 right, 2 up"   },
      { pts:[[2,5,"A",BLUE],[4,3,"B",PURPLE],[6,5,"C",RED]], a1:"2 right, 2 down", a2:"2 right, 2 up"   },
      { pts:[[1,3,"A",BLUE],[3,1,"B",PURPLE],[5,3,"C",RED]], a1:"2 right, 2 down", a2:"2 right, 2 up"   },
    ],
    goingFurther: "For one journey, describe the return route from C back to A.",
  },
  adaptedSupport: {
    lp1Questions: [
      { start:[1,1], end:[4,3], answer:"3 right, 2 up"  },
      { start:[3,1], end:[1,4], answer:"2 left, 3 up"   },
    ],
    lp2Questions: [
      { pts:[[1,1,"A",BLUE],[3,2,"B",PURPLE],[5,4,"C",RED]], a1:"2 right, 1 up",   a2:"2 right, 2 up"   },
      { pts:[[2,5,"A",BLUE],[4,3,"B",PURPLE],[6,5,"C",RED]], a1:"2 right, 2 down", a2:"2 right, 2 up"   },
    ],
    hint1: "Check your answer by tracing your finger along the route on the grid.  Does it start at A and end at B?",
    hint2: "Trace Leg 1 first — does your finger land on B?  Then trace Leg 2 — does it end at C?",
  },
},

// ---------------------------------------------------------------------------
// LESSON 2 — T5W1 Tuesday — Translating shapes on a grid
// ---------------------------------------------------------------------------
2: {
  iCan: [
    "I can move a shape on a grid using direction instructions",
    "I can explain what stays the same when a shape is translated",
  ],
  lp1: {
    title: "Moving Shapes on a Grid",
    // LP1: polygon questions — show original shape, pupil draws translated version
    // gridSize: grid dimensions; shape: vertices; translation: [dc,dr]; answer: text description
    gridSize: 7,
    type: "polygon_translation",
    questions: [
      {
        shape: [[1,1],[4,1],[4,4],[1,4]],   // square
        labels: ['A','B','C','D'],
        translation: [2, 2],
        answer: "2 right, 2 up",
      },
      {
        shape: [[1,1],[4,1],[2,4]],          // triangle
        labels: ['A','B','C'],
        translation: [2, 1],
        answer: "2 right, 1 up",
      },
      {
        shape: [[1,1],[3,1],[4,3],[2,4],[0,3]],  // pentagon
        labels: ['A','B','C','D','E'],
        translation: [2, 2],
        answer: "2 right, 2 up",
      },
    ],
    instruction: "Translate each shape using the direction given.  Draw the new position.",
    goingFurther: "Choose one shape and write the direction instruction that would move it back to its original position.",
  },
  lp2: {
    title: "Translating More Polygons",
    gridSize: 7,
    type: "polygon_translation",
    instruction: "Translate each shape using the direction given.  Draw the new position.",
    questions: [
      {
        shape: [[1,1],[3,1],[4,3],[3,5],[1,5],[0,3]],  // hexagon
        labels: ['A','B','C','D','E','F'],
        translation: [2, 1],
        answer: "2 right, 1 up",
      },
      {
        shape: [[2,1],[4,1],[5,3],[3,5],[1,3]],  // irregular pentagon
        labels: ['A','B','C','D','E'],
        translation: [1, 2],
        answer: "1 right, 2 up",
      },
    ],
    goingFurther: "Write a direction instruction that would move Shape A back to where it started.",
  },
  adaptedSupport: {
    lp1Questions: [
      {
        shape: [[1,1],[4,1],[4,4],[1,4]],
        labels: ['A','B','C','D'],
        translation: [2, 2],
        answer: "2 right, 2 up",
      },
      {
        shape: [[1,1],[4,1],[2,4]],
        labels: ['A','B','C'],
        translation: [2, 1],
        answer: "2 right, 1 up",
      },
    ],
    lp2Questions: [
      {
        shape: [[1,1],[3,1],[4,3],[3,5],[1,5],[0,3]],
        labels: ['A','B','C','D','E','F'],
        translation: [2, 1],
        answer: "2 right, 1 up",
      },
    ],
    workedExample1: {
      shape: [[1,1],[3,1],[3,3],[1,3]],   // small square — different from Q1/Q2
      labels: ['A','B','C','D'],
      translation: [2, 2],
      answer: "2 right, 2 up",
    },
    workedExample2: {
      shape: [[1,1],[3,1],[2,3]],          // small triangle — different from Q1
      labels: ['A','B','C'],
      translation: [2, 1],
      answer: "2 right, 1 up",
    },
    hint1: "Move every dot the same number of steps.  Start with vertex A, then B, then C.  Connect them when you're done.",
    hint2: "Each vertex moves the same direction and distance.  Check by counting squares from each original dot to its new position.",
  },
},


// ---------------------------------------------------------------------------
// LESSON 3 — T5W1 Wednesday — Describing translations
// ---------------------------------------------------------------------------
3: {
  iCan: [
    "I can describe a translation using the words 'right', 'left', 'up' and 'down'",
    "I can track a vertex to work out how far a shape has moved",
  ],
  lp1: {
    title: "Describing Translations",
    instruction: "Look at each pair of grids.  Describe the translation from the original to the image.",
    gridSize: 7,
    type: "polygon_translation",
    questions: [
      {
        shape: [[1,1],[4,1],[4,4],[1,4]],
        labels: ['A','B','C','D'],
        translation: [0, 3],
        answer: "Translated 3 up",
      },
      {
        shape: [[1,1],[3,1],[2,4]],
        labels: ['A','B','C'],
        translation: [4, 0],
        answer: "Translated 4 right",
      },
      {
        shape: [[1,1],[3,1],[4,3],[2,4],[0,3]],
        labels: ['A','B','C','D','E'],
        translation: [0, 2],
        answer: "Translated 2 up",
      },
      {
        shape: [[2,1],[4,1],[4,3],[2,3]],
        labels: ['A','B','C','D'],
        translation: [2, 0],
        answer: "Translated 2 right",
      },
    ],
    goingFurther: "Write the inverse of the translation for question 1.  What instruction would move the image back to the original position?",
  },
  lp2: {
    title: "Two-Direction Translations",
    instruction: "Describe each translation — say how far right or left and how far up or down.",
    gridSize: 7,
    type: "polygon_translation",
    questions: [
      {
        shape: [[1,1],[3,1],[2,3]],
        labels: ['A','B','C'],
        translation: [3, 2],
        answer: "Translated 3 right and 2 up",
      },
      {
        shape: [[1,1],[3,1],[4,3],[2,4],[0,3]],
        labels: ['A','B','C','D','E'],
        translation: [2, 3],
        answer: "Translated 2 right and 3 up",
      },
      {
        shape: [[1,4],[4,4],[4,6],[1,6]],
        labels: ['A','B','C','D'],
        translation: [2, -2],
        answer: "Translated 2 right and 2 down",
      },
      {
        shape: [[3,1],[5,1],[6,3],[4,4],[2,3]],
        labels: ['A','B','C','D','E'],
        translation: [-2, 2],
        answer: "Translated 2 left and 2 up",
      },
    ],
    goingFurther: "Write a pair of translations from questions 1 and 2 that together make a single translation.  What single instruction replaces both?",
  },
  adaptedSupport: {
    lp1Questions: [
      {
        shape: [[1,1],[4,1],[4,4],[1,4]],
        labels: ['A','B','C','D'],
        translation: [0, 3],
        answer: "Translated 3 up",
      },
      {
        shape: [[1,1],[3,1],[2,4]],
        labels: ['A','B','C'],
        translation: [4, 0],
        answer: "Translated 4 right",
      },
    ],
    lp2Questions: [
      {
        shape: [[1,1],[3,1],[2,3]],
        labels: ['A','B','C'],
        translation: [3, 2],
        answer: "Translated 3 right and 2 up",
      },
      {
        shape: [[1,1],[3,1],[4,3],[2,4],[0,3]],
        labels: ['A','B','C','D','E'],
        translation: [2, 3],
        answer: "Translated 2 right and 3 up",
      },
    ],
    workedExample1: {
      shape: [[2,1],[4,1],[4,3],[2,3]],    // different square, different position
      labels: ['A','B','C','D'],
      translation: [0, 2],
      answer: "Translated 2 up",
    },
    workedExample2: {
      shape: [[2,1],[4,1],[3,3]],           // different triangle
      labels: ['A','B','C'],
      translation: [2, 2],
      answer: "Translated 2 right and 2 up",
    },
    hint1: "Pick one vertex (e.g. A).  Count how many squares it has moved to the right or left.  Then count how many it has moved up or down.",
    hint2: "Describe horizontal movement first (right or left), then vertical movement (up or down).  Check with a second vertex to make sure you get the same answer.",
  },
},

// ---------------------------------------------------------------------------
// LESSON 4 — T5W1 Thursday — Drawing translations
// ---------------------------------------------------------------------------
4: {
  iCan: [
    "I can draw a shape in its new position after a translation",
    "I can label the original shape and the image using letters and primes",
  ],
  lp1: {
    title: "Drawing Translations",
    instruction: "Translate each shape using the instruction given.  Draw the image and label each new vertex with a prime (e.g. A').",
    gridSize: 7,
    type: "polygon_translation",
    questions: [
      {
        shape: [[1,1],[3,1],[3,3],[1,3]],
        labels: ['A','B','C','D'],
        translation: [3, 2],
        answer: "3 right, 2 up — A'(4,3)  B'(6,3)  C'(6,5)  D'(4,5)",
      },
      {
        shape: [[1,1],[3,1],[2,4]],
        labels: ['A','B','C'],
        translation: [2, 2],
        answer: "2 right, 2 up — A'(3,3)  B'(5,3)  C'(4,6)",
      },
      {
        shape: [[1,1],[3,1],[4,3],[2,4],[0,3]],
        labels: ['A','B','C','D','E'],
        translation: [2, 1],
        answer: "2 right, 1 up — A'(3,2)  B'(5,2)  C'(6,4)  D'(4,5)  E'(2,4)",
      },
    ],
    goingFurther: "For one of your shapes, write the single instruction that would translate the image back to the original position.",
  },
  lp2: {
    title: "Two-Directional Translations and Reversal",
    instruction: "For each task below, follow the instruction carefully.",
    gridSize: 7,
    type: "polygon_translation",
    questions: [
      {
        shape: [[1,1],[4,1],[5,3],[3,4],[1,3]],
        labels: ['A','B','C','D','E'],
        translation: [1, 3],
        answer: "Translate 1 right and 3 up — A'(2,4)  B'(5,4)  C'(6,6)  D'(4,7 — note top of grid)  E'(2,6)",
      },
      {
        // reverse task: image given, find original
        shape: [[3,3],[5,3],[5,5],[3,5]],   // this IS the image
        labels: ["A'","B'","C'","D'"],
        translation: [-2, -2],              // reverse: the original is 2 left and 2 down
        answer: "Original: 2 left, 2 down from image — A(1,1)  B(3,1)  C(3,3)  D(1,3)",
      },
      {
        shape: [[1,1],[3,1],[2,3]],
        labels: ['A','B','C'],
        translation: [3, 1],
        answer: "Is this a valid translation? Yes — A'(4,2)  B'(6,2)  C'(5,4)",
      },
    ],
    goingFurther: "In question 2, the image is shown.  Write the single instruction that would translate the image back to the original.",
  },
  adaptedSupport: {
    lp1Questions: [
      {
        shape: [[1,1],[3,1],[3,3],[1,3]],
        labels: ['A','B','C','D'],
        translation: [3, 2],
        answer: "3 right, 2 up — A'(4,3)  B'(6,3)  C'(6,5)  D'(4,5)",
      },
      {
        shape: [[1,1],[3,1],[2,4]],
        labels: ['A','B','C'],
        translation: [2, 2],
        answer: "2 right, 2 up — A'(3,3)  B'(5,3)  C'(4,6)",
      },
    ],
    lp2Questions: [
      {
        shape: [[1,1],[4,1],[5,3],[3,4],[1,3]],
        labels: ['A','B','C','D','E'],
        translation: [1, 3],
        answer: "1 right, 3 up",
      },
    ],
    workedExample1: {
      shape: [[2,1],[4,1],[4,3],[2,3]],    // different square — different from Q1
      labels: ['A','B','C','D'],
      translation: [2, 2],
      answer: "2 right, 2 up — A'(4,3)  B'(6,3)  C'(6,5)  D'(4,5)",
    },
    workedExample2: {
      shape: [[2,1],[4,1],[3,4]],           // different triangle — different from Q2
      labels: ['A','B','C'],
      translation: [1, 2],
      answer: "1 right, 2 up — A'(3,3)  B'(5,3)  C'(4,6)",
    },
    hint1: "Move each vertex one at a time — right first, then up.  Count squares carefully from each original dot to find its new position.",
    hint2: "When all vertices are marked, join them up.  Label each new vertex with its letter and an apostrophe: A', B', C'.",
  },
},

}; // end module.exports
