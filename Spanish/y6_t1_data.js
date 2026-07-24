'use strict';

const N1_20 = [
  {n:1,sp:'uno'},{n:2,sp:'dos'},{n:3,sp:'tres'},{n:4,sp:'cuatro'},{n:5,sp:'cinco'},
  {n:6,sp:'seis'},{n:7,sp:'siete'},{n:8,sp:'ocho'},{n:9,sp:'nueve'},{n:10,sp:'diez'},
  {n:11,sp:'once'},{n:12,sp:'doce'},{n:13,sp:'trece'},{n:14,sp:'catorce'},{n:15,sp:'quince'},
  {n:16,sp:'dieciséis'},{n:17,sp:'diecisiete'},{n:18,sp:'dieciocho'},{n:19,sp:'diecinueve'},{n:20,sp:'veinte'},
];

const N21_30 = [
  {n:21,sp:'veintiuno'},{n:22,sp:'veintidós'},{n:23,sp:'veintitrés'},{n:24,sp:'veinticuatro'},{n:25,sp:'veinticinco'},
  {n:26,sp:'veintiséis'},{n:27,sp:'veintisiete'},{n:28,sp:'veintiocho'},{n:29,sp:'veintinueve'},{n:30,sp:'treinta'},
];

module.exports = [

  // ── L01 ──────────────────────────────────────────────────────────────────────
  {
    num: 1,
    fileOut: 'Y6_Sp_T1_L01_LaFamilia.pptx',
    titleSp:  'La familia',
    titleEng: 'My family',
    lo:    'Puedo nombrar los miembros de mi familia y usar "hay" para describir una foto',
    loEng: 'I can name family members and use "hay" to describe a photo',

    phonicsLetter: 'C',
    phonicsSound:  'K or TH',
    phonicsFact:   'C has two sounds in Spanish. Before A, O or U it sounds like K (as in "cat"). Before E or I it sounds like TH (like "think" in Castilian Spanish). Context is everything!',
    phonicsExamples: [
      {word:'casa',   pron:'KAH-sah',        eng:'house'},
      {word:'ciudad', pron:'thyoo-DAHD',      eng:'city'},
      {word:'cinco',  pron:'THIN-koh',        eng:'five'},
    ],

    counting: {label: 'Let\'s count to 20! — ¡Contamos hasta veinte!', nums: N1_20},

    warmUp: {
      title:       '¡Hola, familia!',
      instruction: 'Start with greetings — then we\'ll introduce our families. Listen and repeat each phrase.',
      sentence1:   'Buenos días, ¿cómo estás?',
      response:    '¡Muy bien, gracias! ¿Y tú? — Very well, thanks! And you?',
    },

    vocab: [
      {sp:'mi madre',   pron:'mee MAH-dreh',    eng:'my mum'},
      {sp:'mi padre',   pron:'mee PAH-dreh',    eng:'my dad'},
      {sp:'mi hermano/a', pron:'mee ehr-MAH-noh', eng:'my brother/sister'},
      {sp:'mi abuelo/a',  pron:'mee ah-BWEH-loh', eng:'my grandad/grandma'},
      {sp:'mi tío/a',   pron:'mee TEE-oh',      eng:'my uncle/aunt'},
    ],

    keyStructure: 'En la foto hay... · En mi familia hay...',

    cultural: {
      heading: 'La familia española',
      fact:    'In Spain, family life is central. It is common for grandparents to live nearby or even with the family, and the whole family often eats together every day.',
      detail:  'Sunday lunch — el almuerzo del domingo — is a big deal. Families gather for a long, leisurely meal. Meals can last two or three hours!',
    },

    activities: [
      {
        title:       'Escucha y señala',
        icon:        '👂',
        instruction: 'Your teacher says a family member in Spanish. Point to the right picture on your card.',
        examples:    [],
        tip:         'Repeat the word out loud — hearing it and saying it together helps it stick.',
      },
      {
        title:       'En la foto hay...',
        icon:        '🖼️',
        instruction: 'Look at the family photo on your sheet. Write 3 sentences describing who you can see using "En la foto hay..."',
        examples:    [
          'En la foto hay una madre y un padre.',
          'En la foto hay dos hermanos y una abuela.',
        ],
        tip:         'Join two ideas with "y" (and) — it makes your sentences sound more fluent!',
      },
      {
        title:       'Mi familia',
        icon:        '✏️',
        instruction: 'Write 3 sentences about your own family using "En mi familia hay..."',
        examples:    [
          'En mi familia hay cuatro personas.',
          'En mi familia hay una hermana mayor.',
        ],
        tip:         'Feeling confident? Try: "Mi madre tiene el pelo negro."',
      },
    ],

    roundOff: 'Today we learned our family vocabulary and how to describe a photo using "hay". Practise at home — describe a family photo to someone and see if they can understand!',
    imgFile: null,
  },

  // ── L02 ──────────────────────────────────────────────────────────────────────
  {
    num: 2,
    fileOut: 'Y6_Sp_T1_L02_ComoEs.pptx',
    titleSp:  '¿Cómo es?',
    titleEng: 'What are they like?',
    lo:    'Puedo describir a las personas usando adjetivos de apariencia y personalidad',
    loEng: 'I can describe people using adjectives for appearance and personality',

    phonicsLetter: 'G',
    phonicsSound:  'hard G or soft J',
    phonicsFact:   'G before A, O or U sounds like a hard G (as in "go"). But G before E or I sounds like J — a strong H from the back of the throat. The letters GUE and GUI use a silent U to keep the G hard.',
    phonicsExamples: [
      {word:'gordo',   pron:'GOR-doh',       eng:'fat/chubby'},
      {word:'general', pron:'heh-neh-RAL',   eng:'general'},
      {word:'grande',  pron:'GRAHN-deh',     eng:'big/tall'},
    ],

    counting: {label: 'Let\'s count to 20! — ¡Repasamos hasta veinte!', nums: N1_20},

    warmUp: {
      title:       '¿Cómo es tu familia?',
      instruction: 'Point to the family member pictures and say what you remember from last lesson. Can you describe them?',
      sentence1:   '¿Tienes hermanos? — Do you have any brothers or sisters?',
      response:    'Sí, tengo una hermana. / No, soy hijo único. — Yes, I have a sister. / No, I\'m an only child.',
    },

    vocab: [
      {sp:'simpático/a',   pron:'seem-PAH-tee-koh', eng:'kind/nice'},
      {sp:'divertido/a',   pron:'dee-vehr-TEE-doh',  eng:'funny/fun'},
      {sp:'tiene el pelo...', pron:'tee-EH-neh el PEH-loh', eng:'has ... hair'},
      {sp:'tiene los ojos...', pron:'tee-EH-neh lohs OH-hohs', eng:'has ... eyes'},
      {sp:'inteligente',   pron:'een-teh-lee-HEN-teh', eng:'clever'},
    ],

    keyStructure: 'Es... (personality) · Tiene el pelo... / Tiene los ojos... (appearance)',

    cultural: {
      heading: 'Arte español: Picasso',
      fact:    'Pablo Picasso was born in Málaga, Spain in 1881. He is one of the most famous artists who ever lived, known for his Cubist style which shows people from multiple angles at once.',
      detail:  'Look at his portrait "Guernica" — can you see faces? How are they described? Try describing the people you see in Spanish!',
    },

    activities: [
      {
        title:       '¿Cómo es?',
        icon:        '🎨',
        instruction: 'Your teacher describes someone using adjectives. Draw what they describe!',
        examples:    [
          'Tiene el pelo negro y los ojos azules.',
          'Es simpático y divertido.',
        ],
        tip:         'Listen for "tiene" — that\'s your clue for a physical description!',
      },
      {
        title:       'Describe a tu amigo',
        icon:        '🗣️',
        instruction: 'Take turns describing a classmate — your partner must guess who you are talking about.',
        examples:    [
          'Es alto. Tiene el pelo rubio y los ojos marrones.',
          'Es inteligente y un poco tímido.',
        ],
        tip:         'Use "es" for personality, "tiene" for appearance — they are different verbs!',
      },
      {
        title:       'Mi retrato en español',
        icon:        '🖼️',
        instruction: 'Describe yourself or a famous person using at least four adjectives. Write 3-4 sentences.',
        examples:    [
          'Picasso es muy famoso. Es inteligente y creativo.',
          'Tiene el pelo oscuro y los ojos marrones.',
        ],
        tip:         'Remember: adjectives must match — inteligente stays the same, but divertido/divertida changes!',
      },
    ],

    roundOff: 'Today we used adjectives to describe people\'s appearance and personality. Challenge: describe someone in your family to a partner using only Spanish tonight!',
    imgFile: null,
  },

  // ── L03 ──────────────────────────────────────────────────────────────────────
  {
    num: 3,
    fileOut: 'Y6_Sp_T1_L03_EnMiEstuche.pptx',
    titleSp:  'En mi estuche',
    titleEng: 'In my pencil case',
    lo:    'Puedo decir qué hay y qué no hay en mi estuche',
    loEng: 'I can say what is and is not in my pencil case',

    phonicsLetter: 'J',
    phonicsSound:  'strong H',
    phonicsFact:   'J in Spanish never sounds like English J. It is always a strong H sound made at the back of the throat — like gently clearing your throat. You will hear it a lot in Spanish words!',
    phonicsExamples: [
      {word:'tijeras', pron:'tee-HEH-rahs', eng:'scissors'},
      {word:'caja',    pron:'KAH-hah',      eng:'box'},
      {word:'rojo',    pron:'ROH-hoh',      eng:'red'},
    ],

    counting: {label: 'Let\'s count to 20! — ¡Seguimos contando!', nums: N1_20},

    warmUp: {
      title:       '¿Qué hay en tu estuche?',
      instruction: 'Look around the classroom. What objects can you already name in Spanish? Shout them out!',
      sentence1:   '¿Qué hay en tu estuche? — What is in your pencil case?',
      response:    'En mi estuche hay un lápiz y una goma. — In my pencil case there is a pencil and a rubber.',
    },

    vocab: [
      {sp:'un lápiz',      pron:'oon LAH-peeth',         eng:'a pencil'},
      {sp:'una goma',      pron:'oo-nah GOH-mah',         eng:'a rubber'},
      {sp:'unas tijeras',  pron:'oo-nahs tee-HEH-rahs',   eng:'scissors'},
      {sp:'una regla',     pron:'oo-nah REH-glah',         eng:'a ruler'},
      {sp:'un sacapuntas', pron:'oon sah-kah-POON-tahs',   eng:'a pencil sharpener'},
    ],

    keyStructure: 'En mi estuche tengo... · En mi estuche no tengo...',

    cultural: {
      heading: 'El colegio en España',
      fact:    'Spanish children often have school from 9am to 2pm, go home for a long lunch, then return for afternoon lessons from 3pm to 5pm — the school day reflects Spain\'s eating habits!',
      detail:  'Subjects include Lengua (Spanish), Matemáticas, Ciencias (Science) and Inglés. Many Spanish children learn English from age 3.',
    },

    activities: [
      {
        title:       '¿Tienes...?',
        icon:        '🎒',
        instruction: 'Your teacher holds up an item. Thumbs up if you have it in your pencil case, thumbs down if not. Then say your sentence!',
        examples:    [
          'En mi estuche tengo unas tijeras.',
          'En mi estuche no tengo un sacapuntas.',
        ],
        tip:         'Remember: "no tengo" for things you do not have — the "no" goes before the verb.',
      },
      {
        title:       'El reto del estuche',
        icon:        '🏆',
        instruction: 'Partner A looks away. Partner B describes what is in their pencil case — A must draw what they hear.',
        examples:    [
          'Tengo dos lápices y una goma.',
          'No tengo una regla.',
        ],
        tip:         'Count the items — "tengo tres lápices." Numbers make your sentences much more precise!',
      },
      {
        title:       'Escríbelo',
        icon:        '✏️',
        instruction: 'Write 4 sentences about your own pencil case — 2 "tengo" and 2 "no tengo".',
        examples:    [
          'En mi estuche tengo un boli y una regla.',
          'En mi estuche no tengo unas tijeras.',
        ],
        tip:         'Double-check the gender: is it "un" or "una"? The vocab card will tell you.',
      },
    ],

    roundOff: 'Today we learned pencil case vocabulary and how to say what we have and don\'t have. Can you label your pencil case at home with Spanish sticky notes?',
    imgFile: null,
  },

  // ── L04 ──────────────────────────────────────────────────────────────────────
  {
    num: 4,
    fileOut: 'Y6_Sp_T1_L04_LosAnimales.pptx',
    titleSp:  'Los animales',
    titleEng: 'Animals',
    lo:    'Puedo nombrar animales salvajes, de granja y del zoo usando "hay"',
    loEng: 'I can name wild, farm and zoo animals using "hay"',

    phonicsLetter: 'X',
    phonicsSound:  'KS or H',
    phonicsFact:   'X usually sounds like KS (as in "six"). But in words borrowed from indigenous languages — like México or Oaxaca — the X sounds like a strong H. So "México" is pronounced MEH-hee-koh!',
    phonicsExamples: [
      {word:'taxi',    pron:'TAK-see',       eng:'taxi'},
      {word:'México',  pron:'MEH-hee-koh',   eng:'Mexico'},
      {word:'extraño', pron:'eks-TRAH-nyoh', eng:'strange/odd'},
    ],

    counting: {label: 'New numbers: 21-30! — ¡Números nuevos!', nums: N21_30},

    warmUp: {
      title:       '¡Animales!',
      instruction: 'Your teacher shows an animal picture — make its sound, then try to say the animal\'s name in Spanish!',
      sentence1:   '¿Qué animal es? — What animal is it?',
      response:    '¡Es un elefante! / ¡Es una vaca! — It\'s an elephant! / It\'s a cow!',
    },

    vocab: [
      {sp:'el elefante', pron:'el eh-leh-FAHN-teh', eng:'elephant'},
      {sp:'la vaca',     pron:'lah BAH-kah',         eng:'cow'},
      {sp:'el lobo',     pron:'el LOH-boh',           eng:'wolf'},
      {sp:'el oso',      pron:'el OH-soh',            eng:'bear'},
      {sp:'el pájaro',   pron:'el PAH-hah-roh',       eng:'bird'},
    ],

    keyStructure: 'Hay un/una... · Es un animal salvaje / de granja / del zoo',

    cultural: {
      heading: 'Animales en peligro en España',
      fact:    'Spain is home to the Iberian lynx (el lince ibérico) — one of the world\'s rarest wild cats. Decades of conservation work have pulled it back from the edge of extinction.',
      detail:  'Spain\'s national parks protect wolves, brown bears, golden eagles and thousands of plant species. El Parque Nacional de Doñana is a UNESCO World Heritage Site and vital wetland for migratory birds.',
    },

    activities: [
      {
        title:       '¿Qué animal es?',
        icon:        '🦁',
        instruction: 'Look at the animal picture. Say the Spanish name, then sort it: "Es un animal salvaje / de granja / del zoo."',
        examples:    [
          'Es un elefante. Es un animal del zoo.',
          'Es una vaca. Es un animal de granja.',
        ],
        tip:         'Is it "el" or "la"? That tells you whether to say "un" or "una"!',
      },
      {
        title:       'Hábitats',
        icon:        '🌍',
        instruction: 'Sort a set of animal cards into three groups: animales salvajes, animales de granja, animales del zoo.',
        examples:    [
          'El lobo es un animal salvaje.',
          'La vaca es un animal de granja.',
        ],
        tip:         'Some animals could go in more than one group — be ready to explain your reasoning!',
      },
      {
        title:       'En el zoo hay...',
        icon:        '✏️',
        instruction: 'Design your perfect zoo and describe it. Write 4 sentences using "En el zoo hay..."',
        examples:    [
          'En el zoo hay tres elefantes.',
          'En el zoo no hay lobos — ¡son muy peligrosos!',
        ],
        tip:         'Use numbers to say how many: "hay dos osos." Link it to our new numbers 21-30!',
      },
    ],

    roundOff: 'Today we explored Spanish animal vocabulary and habitats. Can you sort 5 more animals into wild, farm and zoo categories in Spanish tonight?',
    imgFile: null,
  },

  // ── L05 ──────────────────────────────────────────────────────────────────────
  {
    num: 5,
    fileOut: 'Y6_Sp_T1_L05_TienesMascotas.pptx',
    titleSp:  '¿Tienes mascotas?',
    titleEng: 'Do you have any pets?',
    lo:    'Puedo preguntar y responder sobre mascotas usando números y "tengo / no tengo"',
    loEng: 'I can ask and answer about pets using numbers and "tengo / no tengo"',

    phonicsLetter: 'Q',
    phonicsSound:  'K (the U is always silent)',
    phonicsFact:   'QU in Spanish always sounds like K — the U is completely silent! So "que" sounds like "keh", not "kweh". QU is just the way Spanish writes K before the vowels E and I.',
    phonicsExamples: [
      {word:'¿qué?',   pron:'keh',         eng:'what?'},
      {word:'quiero',  pron:'KYEH-roh',    eng:'I want'},
      {word:'pequeño', pron:'peh-KEH-nyoh',eng:'small'},
    ],

    counting: {label: 'Numbers 21-30 — ¡Seguimos!', nums: N21_30},

    warmUp: {
      title:       '¿Tienes mascotas?',
      instruction: 'Ask your partner about their pets. Use the phrase and the response. Try to add a number!',
      sentence1:   '¿Tienes mascotas? — Do you have any pets?',
      response:    'Sí, tengo un gato. Tengo dos perros. / No, no tengo mascotas. — Yes I have a cat. I have two dogs. / No, I don\'t have any pets.',
    },

    vocab: [
      {sp:'un perro',   pron:'oon PEH-rroh',    eng:'a dog'},
      {sp:'un gato',    pron:'oon GAH-toh',      eng:'a cat'},
      {sp:'un conejo',  pron:'oon koh-NEH-hoh',  eng:'a rabbit'},
      {sp:'un pez',     pron:'oon peth',          eng:'a fish'},
      {sp:'un hámster', pron:'oon AHM-stehr',    eng:'a hamster'},
    ],

    keyStructure: '¿Tienes mascotas? · Tengo... · No tengo... · Tengo dos gatos',

    cultural: {
      heading: 'El Zoo de Madrid',
      fact:    'Madrid Zoo has over 3,000 animals from around 150 species. It opened in 1770, making it one of the oldest zoos in the world.',
      detail:  'Spain also has many animal rescue centres (centros de rescate) where people can adopt abandoned or rescued animals. Adopting a pet is called "adoptar una mascota".',
    },

    activities: [
      {
        title:       '¡Pregunta a tus compañeros!',
        icon:        '🐾',
        instruction: 'Move around the room asking classmates about their pets. Record the answers in your book.',
        examples:    [
          '¿Tienes mascotas? — Sí, tengo un gato.',
          '¿Cuántos tienes? — Tengo dos perros.',
        ],
        tip:         'Challenge: ask a follow-up question — "¿Cómo se llama?" (What is its name?)',
      },
      {
        title:       'Más mascotas que...',
        icon:        '🏆',
        instruction: 'Who has the most pets in the class? Write a sentence comparing using "Tengo más... que..."',
        examples:    [
          'Tengo más mascotas que Sofía.',
          'Sofía tiene tres gatos. Yo tengo un perro.',
        ],
        tip:         'No pets? Try: "¡No tengo mascotas pero quiero un perro!"',
      },
      {
        title:       '¡Se busca!',
        icon:        '📢',
        instruction: 'Write a short lost-pet poster in Spanish. Describe your (real or imaginary) pet using adjectives from L02.',
        examples:    [
          '¡Se busca! Tengo un gato. Se llama Pipo.',
          'Tiene el pelo negro y los ojos verdes. Es muy simpático.',
        ],
        tip:         'Link to L02 — use adjectives you already know to make the description detailed!',
      },
    ],

    roundOff: 'Today we asked and answered about pets and used numbers to say how many. Try asking your family "¿tienes mascotas?" in Spanish — report back next lesson!',
    imgFile: null,
  },

  // ── L06 ──────────────────────────────────────────────────────────────────────
  {
    num: 6,
    fileOut: 'Y6_Sp_T1_L06_Repaso.pptx',
    titleSp:  '¡Repaso!',
    titleEng: 'Term Review',
    lo:    'Puedo usar el vocabulario y las estructuras de este trimestre con confianza',
    loEng: 'I can use this term\'s vocabulary and structures with confidence',

    phonicsLetter: 'CH',
    phonicsSound:  'like English CH',
    phonicsFact:   'CH in Spanish sounds just like English CH (as in "cheese"). CH used to be listed as a separate letter in the Spanish alphabet but was officially removed in 1994. You still see and hear it everywhere!',
    phonicsExamples: [
      {word:'chocolate', pron:'choh-koh-LAH-teh', eng:'chocolate'},
      {word:'muchacho',  pron:'moo-CHAH-choh',    eng:'boy'},
      {word:'noche',     pron:'NOH-cheh',          eng:'night'},
    ],

    counting: {label: 'Numbers 21-30 — ¡Repasamos!', nums: N21_30},

    warmUp: {
      title:       '¡Todo junto! — All together!',
      instruction: 'Your teacher calls a category — shout a Spanish word from that category as fast as you can!',
      sentence1:   '¡Familia! ¡Anímate! — Family! Get going!',
      response:    '¡madre! ¡padre! ¡hermano! ¡abuelo! — Keep going — how many can you remember?',
    },

    vocab: [
      {sp:'la familia',   pron:'lah fah-MEE-lyah',   eng:'the family'},
      {sp:'los animales', pron:'lohs ah-nee-MAH-lehs', eng:'the animals'},
      {sp:'el estuche',   pron:'el es-TOO-cheh',       eng:'the pencil case'},
      {sp:'hay',          pron:'eye',                  eng:'there is/are'},
      {sp:'tengo',        pron:'TEN-goh',              eng:'I have'},
    ],

    keyStructure: 'En la foto hay... · Tengo... / No tengo... · Es un animal...',

    cultural: null,

    activities: [
      {
        title:       'Bingo en español',
        icon:        '🎱',
        instruction: 'Fill your bingo card with Spanish words from this term — family, classroom, animals, adjectives. Listen and cross them off!',
        examples:    [],
        tip:         'Win a "línea" (line) or a full house — shout "¡Bingo!" when you win!',
      },
      {
        title:       'Tres en raya',
        icon:        '⭕',
        instruction: 'Play noughts and crosses. Claim a square by translating the word in it correctly — your partner checks!',
        examples:    [
          'mi madre — my mum ✓',
          'un lápiz — a pencil ✓',
        ],
        tip:         'Wrong answer? Your partner gets a chance to steal that square!',
      },
      {
        title:       'Escribe una historia',
        icon:        '✏️',
        instruction: 'Write 5-6 sentences about a made-up Spanish family and their pets. Use everything from this term!',
        examples:    [
          'La familia Pérez tiene dos hijos y un gato.',
          'La madre tiene el pelo rojo. El padre es muy divertido.',
        ],
        tip:         'Can you include a family member, a pet, an adjective, a classroom word and a number? ¡Fantastico!',
      },
    ],

    roundOff: '¡Fantástico! You have completed Y6 Autumn 1 Spanish. Look how much you can say now — family, descriptions, classroom, animals and pets. ¡Muy bien!',
    imgFile: null,
  },

];
