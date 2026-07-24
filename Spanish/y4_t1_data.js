'use strict';
// Y4 T1 Spanish lesson data — L01 to L06
// Y4 brand: #1798D3 (blue) — Maple Learning Zone
// CLF Y4 focus: pets, numbers 1–20, weather, seasons, physical geography of Spain

const ALL_NUMBERS = [
  { num:1,  es:'uno',        pro:'OO-noh' },
  { num:2,  es:'dos',        pro:'doss' },
  { num:3,  es:'tres',       pro:'tress' },
  { num:4,  es:'cuatro',     pro:'KWAH-troh' },
  { num:5,  es:'cinco',      pro:'THIN-koh' },
  { num:6,  es:'seis',       pro:'SAY-ss' },
  { num:7,  es:'siete',      pro:'SYEH-teh' },
  { num:8,  es:'ocho',       pro:'OH-choh' },
  { num:9,  es:'nueve',      pro:'NWEH-beh' },
  { num:10, es:'diez',       pro:'dyeth' },
  { num:11, es:'once',       pro:'ON-theh' },
  { num:12, es:'doce',       pro:'DOH-theh' },
  { num:13, es:'trece',      pro:'TREH-theh' },
  { num:14, es:'catorce',    pro:'kah-TOR-theh' },
  { num:15, es:'quince',     pro:'KEEN-theh' },
  { num:16, es:'dieciséis',  pro:'dyeh-thee-SAY-ss' },
  { num:17, es:'diecisiete', pro:'dyeh-thee-SYEH-teh' },
  { num:18, es:'dieciocho',  pro:'dyeh-thee-OH-choh' },
  { num:19, es:'diecinueve', pro:'dyeh-thee-NWEH-beh' },
  { num:20, es:'veinte',     pro:'BAYN-teh' },
];

const lessons = [

  // ── L01 ────────────────────────────────────────────────────────────────────
  {
    num: 1,
    title: '¡Bienvenidos de vuelta!',
    subtitle: 'Welcome Back!',
    filename: 'Y4_Sp_T1_L01_Bienvenidos.pptx',
    phonicsLetter: 'RR',
    countingMax: 10,
    lo: 'Recall greetings, numbers to 10 and colours from Year 3',
    criteria: [
      'Name 3 greetings in Spanish',
      'Count from 1 to 10 in Spanish',
      'Say 5 colours in Spanish',
    ],
    cultural: {
      title: 'España — una mirada geográfica',
      subtitle: 'Spain — a geographical look',
      fact1: 'The Pyrenees mountains form a natural border between Spain and France — some peaks reach over 3,400 metres!',
      fact2: 'Three great rivers flow through Spain: the Ebro, the Tagus (Tajo) and the Guadalquivir.',
      fact3: 'Spain has more than 8,000 km of coastline along the Atlantic Ocean and Mediterranean Sea.',
      imgFile: 'l01_spain_geo.jpg',
    },
    warmUp: {
      prompt: 'Think back to Year 3 Spanish. What can you still remember? Tell your partner everything — greetings, your name, how you feel, numbers, colours. How much can you string together?',
      hint: 'Try a full conversation: greet, give your name, say how you are, say a colour, count — then say goodbye!',
    },
    vocab: [
      { es:'Hola',          en:'Hello',          pro:'OH-lah' },
      { es:'Buenos días',   en:'Good morning',   pro:'BWEH-noss DEE-ahss' },
      { es:'¿Cómo estás?',  en:'How are you?',   pro:'KOH-moh ess-TAHSS' },
      { es:'Muy bien',      en:'Very well',       pro:'mwee BYEN' },
      { es:'Así así',       en:'So-so',           pro:'ah-SEE ah-SEE' },
      { es:'Adiós',         en:'Goodbye',         pro:'ah-DYOSS' },
    ],
    phonics: {
      letter: 'RR',
      sound: 'rolled / trilled R — like a purring cat!',
      examples: [
        { word:'perro',  meaning:'dog',          highlight:'rr' },
        { word:'tierra', meaning:'earth / land', highlight:'rr' },
        { word:'arriba', meaning:'up! / hooray!',highlight:'rr' },
      ],
      tip: 'Flick your tongue against the roof of your mouth very fast — a tiny flutter. Don\'t use your throat! Practice: "rrrr" like a small engine.',
    },
    activities: [
      {
        title: '¡Conversación!',
        instruction: 'Stand up! Walk around and meet people. With each person, have a full Y3 Spanish conversation: greet, ask names, ask how they are, then say goodbye. Try to keep going for 2 minutes.',
        steps: [
          'A: ¡Hola! ¿Cómo te llamas?',
          'B: Me llamo [name]. ¿Y tú?',
          'A: Me llamo [name]. ¿Cómo estás?',
          'B: Muy bien / así así. ¡Adiós!',
        ],
      },
      {
        title: '¡Los colores!',
        instruction: 'Teacher holds up a coloured object or card. Call out the colour in Spanish as fast as you can! The first to shout correctly must then say it in a sentence: "Es [colour]."',
        steps: [
          'Teacher shows a colour — shout it in Spanish!',
          'Winner says the full sentence: ¡Es rojo!',
          'Colours to know: rojo, azul, verde, amarillo,',
          'naranja, morado, negro, blanco — can you get all 8?',
        ],
      },
      {
        title: '¡Números!',
        instruction: 'Count around the class from 1 to 10 — then backwards. Then: teacher calls a number and you hold up that many fingers. Finally, count in twos as a class.',
        steps: [
          'Round the class: uno, dos, tres... diez',
          'Backwards: diez, nueve, ocho... uno',
          'Hold up fingers for the number teacher calls',
          'Count in twos: dos, cuatro, seis, ocho, diez!',
        ],
      },
    ],
    roundOff: {
      prompt: 'Three things to a partner: one greeting, one number (as a word), one colour — all in Spanish. Then swap.',
      exit: 'Write: one greeting, one number (word form) and one colour — in Spanish.',
      nextLesson: 'Next time: ¿Tienes mascotas? — Do you have any pets?',
    },
  },

  // ── L02 ────────────────────────────────────────────────────────────────────
  {
    num: 2,
    title: '¿Tienes mascotas?',
    subtitle: 'Do you have any pets?',
    filename: 'Y4_Sp_T1_L02_Mascotas.pptx',
    phonicsLetter: 'G',
    countingMax: 10,
    lo: 'Ask and answer "Do you have any pets?" in Spanish',
    criteria: [
      'Name 5 pets in Spanish',
      'Ask: ¿Tienes mascotas?',
      'Answer: Tengo un... or No, no tengo mascotas.',
    ],
    cultural: {
      title: 'La vida en casa española',
      subtitle: 'Home life in Spain',
      fact1: 'Over half of Spanish families have a pet — el perro (dog) is the most popular, closely followed by el gato (cat).',
      fact2: 'Spain has a tradition of keeping songbirds — canarios (canaries) are common household pets, especially in Andalucia.',
      fact3: 'In many Spanish towns, weekly mercados (markets) sell everything from pet food to plants, fresh fish and handmade goods.',
      imgFile: 'l02_spain_home.jpg',
    },
    warmUp: {
      prompt: 'Do you have any pets at home? Tell your partner — but try to say the pet name in Spanish if you know it! Can you guess how to say cat, dog, or fish?',
      hint: 'Gato sounds a bit like... cat (not really — but gato is Spanish for cat). Perro for dog. Pez for fish. Can you spot the patterns?',
    },
    vocab: [
      { es:'un gato',      en:'a cat',     pro:'oon GAH-toh' },
      { es:'un perro',     en:'a dog',     pro:'oon PEH-rroh' },
      { es:'un pez',       en:'a fish',    pro:'oon peth' },
      { es:'un conejo',    en:'a rabbit',  pro:'oon koh-NEH-hoh' },
      { es:'un hámster',   en:'a hamster', pro:'oon AHM-ster' },
      { es:'Tengo un...',  en:'I have a...', pro:'TEN-goh oon' },
    ],
    phonics: {
      letter: 'G',
      sound: 'like English "g" in "go" — but softer before e or i',
      examples: [
        { word:'gato',   meaning:'cat',      highlight:'g' },
        { word:'tengo',  meaning:'I have',   highlight:'g' },
        { word:'agosto', meaning:'August',   highlight:'g' },
      ],
      tip: 'Before a, o, u: G sounds like the g in "get". Before e or i: it becomes a breathier sound — like gently clearing your throat.',
    },
    activities: [
      {
        title: 'Escucha y señala',
        instruction: 'Listen and point! Teacher describes their pets in Spanish. Point to the right picture card each time. Then try to say the full sentence yourself without looking at the board.',
        steps: [
          'Listen: "Tengo un gato" — which animal?',
          'Point to the right picture card',
          'Repeat the sentence as a class',
          'Now say 3 pets you have — or wish you had!',
        ],
      },
      {
        title: '¿Tienes mascotas?',
        instruction: 'Pair work: ask your partner about their pets. Try to include a number (tengo DOS gatos). If you don\'t have a pet, make one up — you can have an exotic dream pet!',
        steps: [
          'A: ¿Tienes mascotas?',
          'B: Sí, tengo un perro. / No, no tengo mascotas.',
          'A: ¿Cómo se llama? (What\'s it called?)',
          'B: Se llama [name]! — then swap roles.',
        ],
      },
      {
        title: 'Encuesta de mascotas',
        instruction: 'Class pet survey! Walk around asking ¿Tienes mascotas? Make a tally chart. At the end, report back in Spanish: how many people have a dog, cat, fish...?',
        steps: [
          'Ask at least 4 people: ¿Tienes mascotas?',
          'Note down their answers in a tally',
          'Count the totals — in Spanish!',
          'Report: "Cuatro personas tienen un perro."',
        ],
      },
    ],
    roundOff: {
      prompt: '¿Tienes mascotas? Go around the group — everyone says one sentence about their pets (real or imaginary).',
      exit: 'Write ¿Tienes mascotas? and your answer in full Spanish sentences.',
      nextLesson: 'Next time: more animals and numbers all the way to 20!',
    },
  },

  // ── L03 ────────────────────────────────────────────────────────────────────
  {
    num: 3,
    title: 'Más animales · Números 11–20',
    subtitle: 'More animals · Numbers 11–20',
    filename: 'Y4_Sp_T1_L03_NumerosAnimales.pptx',
    phonicsLetter: 'QU',
    countingMax: 20,
    lo: 'Count to 20 in Spanish and use numbers with pet vocabulary',
    criteria: [
      'Count from 11 to 20 in Spanish',
      'Name 4 new animals in Spanish',
      'Make a sentence using a number and an animal',
    ],
    cultural: {
      title: 'El mercado español',
      subtitle: 'The Spanish market',
      fact1: 'Spain has over 1,000 traditional outdoor markets. La Boqueria in Barcelona is one of the most famous in the world.',
      fact2: 'At a Spanish pet shop — una tienda de animales — you can buy everything from tropical fish to hamsters, canaries and rabbits.',
      fact3: 'Andalucia is famous for its beautiful Andalusian horses (caballos). Horsemanship (equitación) is a big part of the culture there.',
      imgFile: null,
    },
    warmUp: {
      prompt: 'Can you count to 10 in Spanish without looking? Now — do you think you can guess what comes next after diez (10)?',
      hint: 'Once = eleven. Can you hear the word "once" hiding in the English word "eleven"? Well... not quite, but once you know it you\'ll never forget it!',
    },
    vocab: [
      { es:'once',      en:'eleven',   pro:'ON-theh' },
      { es:'doce',      en:'twelve',   pro:'DOH-theh' },
      { es:'quince',    en:'fifteen',  pro:'KEEN-theh' },
      { es:'veinte',    en:'twenty',   pro:'BAYN-teh' },
      { es:'un caballo',en:'a horse',  pro:'oon kah-BAH-yoh' },
      { es:'un pájaro', en:'a bird',   pro:'oon PAH-hah-roh' },
    ],
    phonics: {
      letter: 'QU',
      sound: 'always sounds like "k" — the U is completely silent!',
      examples: [
        { word:'quince', meaning:'fifteen', highlight:'qu' },
        { word:'queso',  meaning:'cheese',  highlight:'qu' },
        { word:'¿qué?',  meaning:'what?',   highlight:'qu' },
      ],
      tip: '"Qu" in Spanish is ALWAYS a k sound. Never say the U — quince = KEEN-theh, NOT KWEE-ntheh. Think of it like qu = k.',
    },
    activities: [
      {
        title: '¡Cadena de números!',
        instruction: 'Number chain! Count around the class from 1 to 20. Anyone who hesitates or gets it wrong sits down. Can the whole class get all the way to veinte?',
        steps: [
          'Everyone stands up!',
          'Count around the class: uno, dos, tres...',
          'Keep going past diez into the new numbers',
          'Last one standing wins — but aim for everyone to reach veinte!',
        ],
      },
      {
        title: '¿Cuántos animales?',
        instruction: 'Teacher holds up a number card. Say the number in Spanish, then make a silly sentence: "Tengo [number] [animals]!" The more ridiculous the better.',
        steps: [
          'Teacher shows a number — call it out in Spanish!',
          'Make a sentence: ¡Tengo catorce peces!',
          'Try with a partner — compete for the silliest sentence',
          'e.g. Tengo veinte caballos en mi dormitorio!',
        ],
      },
      {
        title: 'Animales nuevos',
        instruction: 'Meet four new animals! Practise pronunciation, then play Backs to the Board — one player faces away while the class gives Spanish clues about the animal behind them.',
        steps: [
          'Learn: caballo, pájaro, ratón, cobaya',
          'Say each three times with a matching action',
          'Backs to the board: "Es pequeño... tiene pelo..."',
          '"¡Es una cobaya!" — Can you guess it?',
        ],
      },
    ],
    roundOff: {
      prompt: 'Count from 11 to 20 as a class, then backwards. Then everyone says their dream pet collection in Spanish with numbers!',
      exit: 'Write the numbers 11, 13, 15, 17 and 20 as Spanish words. Then write one sentence: Tengo [number] [animal]s.',
      nextLesson: 'Next time: ¿Qué tiempo hace? — What\'s the weather like in Spain?',
    },
  },

  // ── L04 ────────────────────────────────────────────────────────────────────
  {
    num: 4,
    title: '¿Qué tiempo hace?',
    subtitle: 'What\'s the weather like?',
    filename: 'Y4_Sp_T1_L04_ElTiempo.pptx',
    phonicsLetter: 'J',
    countingMax: 20,
    lo: 'Describe the weather in Spanish using hace, llueve and hay',
    criteria: [
      'Say 6 weather expressions in Spanish',
      'Ask and answer: ¿Qué tiempo hace?',
      'Identify the pattern: hace / llueve / hay',
    ],
    cultural: {
      title: 'El tiempo en España',
      subtitle: 'Weather across Spain',
      fact1: 'Spain has Europe\'s most varied climate: the rainy, green north (País Vasco) gets over 1,500 mm of rain per year, while Almería in the south is almost a desert!',
      fact2: 'The Canary Islands (Las Islas Canarias) belong to Spain and enjoy a subtropical climate — mild and sunny all year round!',
      fact3: 'Near Granada, you can ski on the Sierra Nevada mountains in the morning and swim in the Mediterranean in the afternoon — in the same day!',
      imgFile: 'l04_spain_weather.jpg',
    },
    warmUp: {
      prompt: 'Look outside (or think about today). How is the weather? Describe it in English — then challenge yourself: how would you say any of it in Spanish?',
      hint: 'Sol sounds like solar... viento sounds like ventilator (fan)... llueve sounds a bit like "lluvia" (rain)... calor sounds like calorie (heat)!',
    },
    vocab: [
      { es:'Hace sol',    en:'It\'s sunny',   pro:'AH-theh sol' },
      { es:'Hace viento', en:'It\'s windy',   pro:'AH-theh BYEN-toh' },
      { es:'Llueve',      en:'It\'s raining', pro:'YWEH-beh' },
      { es:'Hace frío',   en:'It\'s cold',    pro:'AH-theh FREE-oh' },
      { es:'Hace calor',  en:'It\'s hot',     pro:'AH-theh kah-LOR' },
      { es:'Hay niebla',  en:'It\'s foggy',   pro:'eye NYEH-blah' },
    ],
    phonics: {
      letter: 'J',
      sound: 'a strong H sound — like blowing warm air on cold hands',
      examples: [
        { word:'julio',  meaning:'July',   highlight:'j' },
        { word:'junio',  meaning:'June',   highlight:'j' },
        { word:'rojo',   meaning:'red',    highlight:'j' },
      ],
      tip: 'Spanish J is much stronger than English H. It\'s like blowing warm air on your hands: "hhhhh". Julio = HOOL-yoh. Rojo = ROH-hoh.',
    },
    activities: [
      {
        title: 'Pronóstico del tiempo',
        instruction: 'Weather forecast! Teacher points to a region on a map of Spain. Call out the weather in Spanish. Then a volunteer becomes the meteorólogo/a (weather presenter) and gives the whole forecast!',
        steps: [
          'Look at the Spain weather map on the board',
          'Teacher points to a city or region',
          'Class: "¡En Madrid, hace sol!"',
          'Volunteer presenter: give the full Spanish forecast!',
        ],
      },
      {
        title: '¡Mímica del tiempo!',
        instruction: 'Weather mime! One person mimes a weather type — no words, just actions. Class shouts the Spanish. Then: teacher calls out Spanish and everyone mimes together.',
        steps: [
          'Volunteer mimes a weather — class guesses in Spanish',
          'Check: ¿Hace sol? ¡Sí! / ¿Llueve? ¡No!',
          'Fast round: teacher says "¡Hace frío!" — everyone shivers!',
          'Try: llueve, viento, calor, niebla, nieve',
        ],
      },
      {
        title: '¿Qué tiempo hace hoy?',
        instruction: 'Pair weather reporters. A gives a 3-phrase Spanish weather report for different parts of Spain. B counts correct phrases. Then swap.',
        steps: [
          'A: "Buenos días. En Madrid, hace sol."',
          '"En el norte, llueve y hace frío."',
          '"En el sur, hace mucho calor. ¡Hasta luego!"',
          'B: score correct phrases. Swap roles!',
        ],
      },
    ],
    roundOff: {
      prompt: 'Quick-fire: teacher says a Spanish city — you call the weather. Then write tonight\'s forecast for Spain in Spanish.',
      exit: 'Write 4 weather expressions in Spanish — using hace, llueve and hay (at least one of each).',
      nextLesson: 'Next time: Las estaciones — the four seasons of the year!',
    },
  },

  // ── L05 ────────────────────────────────────────────────────────────────────
  {
    num: 5,
    title: 'Las estaciones',
    subtitle: 'The Seasons',
    filename: 'Y4_Sp_T1_L05_Estaciones.pptx',
    phonicsLetter: 'Ñ',
    countingMax: 20,
    lo: 'Name the four seasons in Spanish and link them to weather',
    criteria: [
      'Name all four seasons in Spanish',
      'Use En [season], [weather] to describe each season',
      'Say your favourite season with a reason',
    ],
    cultural: {
      title: 'Las estaciones en España',
      subtitle: 'The seasons in Spain',
      fact1: 'Summers in Seville (el verano en Sevilla) regularly reach 45°C — it\'s the hottest city in western Europe!',
      fact2: 'La primavera (spring) brings the famous Feria de Abril in Seville: a week of flamenco dancing, decorated horses and colourful dresses.',
      fact3: 'El otoño (autumn) in La Rioja means the grape harvest — la vendimia — when whole communities celebrate the wine harvest together.',
      imgFile: 'l05_spain_seasons.jpg',
    },
    warmUp: {
      prompt: 'What season is it right now? What\'s the weather usually like in this season in Spain compared to Bristol? What\'s your favourite season — and why?',
      hint: 'Think about what you do in each season — swimming, wearing coats, seeing leaves fall, spotting blossom... How would you explain it in Spanish?',
    },
    vocab: [
      { es:'el invierno',  en:'winter',       pro:'el in-BYER-noh' },
      { es:'el verano',    en:'summer',        pro:'el beh-RAH-noh' },
      { es:'la primavera', en:'spring',        pro:'lah pree-mah-BEH-rah' },
      { es:'el otoño',     en:'autumn',        pro:'el oh-TOH-nyoh' },
      { es:'En verano...',  en:'In summer...', pro:'en beh-RAH-noh' },
      { es:'Mi favorita',  en:'My favourite',  pro:'mee fah-boh-REE-tah' },
    ],
    phonics: {
      letter: 'Ñ',
      sound: 'NY sound — like "canyon" or "onion"',
      examples: [
        { word:'otoño',  meaning:'autumn',  highlight:'ñ' },
        { word:'España', meaning:'Spain',   highlight:'ñ' },
        { word:'señor',  meaning:'Mr/Sir',  highlight:'ñ' },
      ],
      tip: 'You know this from Y3! The tilde (~) on the n makes it say "ny". Otoño = oh-TOH-nyoh. España = ess-PAH-nyah. Listen for it — it\'s everywhere!',
    },
    activities: [
      {
        title: 'Las cuatro esquinas',
        instruction: 'Four corners! Each corner is a season. Teacher calls out a weather phrase — run to the season that fits best! If unsure, discuss with others in your corner.',
        steps: [
          'Corners: invierno / verano / primavera / otoño',
          'Teacher: "Hace mucho calor y hace sol" — run!',
          'Discuss: "¿Por qué?" — justify your choice!',
          'Try: llueve a veces / hace frío y hay nieve...',
        ],
      },
      {
        title: 'En [estación], [tiempo]',
        instruction: 'Sentence builder! Pick a season and two weather phrases that go with it. Say your sentence to your partner. They mime both weather phrases — no words!',
        steps: [
          'Choose: En el verano... / En el otoño...',
          'Add weather: hace sol y hace calor.',
          'Partner mimes both weather phrases',
          'Build longer: En el invierno, hace frío, llueve y hay nieve.',
        ],
      },
      {
        title: 'Mi estación favorita',
        instruction: 'Everyone prepares one sentence: Mi estación favorita es [season] porque [reason]. Then stand up and share. Vote for the most popular season!',
        steps: [
          'Think: what\'s your favourite season?',
          'Draft: Mi estación favorita es el verano...',
          'Add porque: porque hace sol y hace calor.',
          'Share — then class vote: which season wins?',
        ],
      },
    ],
    roundOff: {
      prompt: 'Going round the class: each person says a different "En [season], [weather]" sentence. Keep going until you\'ve covered every combination you know!',
      exit: 'Write all four seasons in Spanish. Then write one weather sentence for each season.',
      nextLesson: 'Next time: big T1 review — pets, numbers, weather and seasons all together!',
    },
  },

  // ── L06 ────────────────────────────────────────────────────────────────────
  {
    num: 6,
    title: '¡Repaso de T1!',
    subtitle: 'T1 Review',
    filename: 'Y4_Sp_T1_L06_Repaso.pptx',
    phonicsLetter: 'LL',
    countingMax: 20,
    lo: 'Recall and use T1 vocabulary: pets, numbers 1–20, weather and seasons',
    criteria: [
      'Use pet vocabulary with numbers',
      'Describe the weather using at least 4 expressions',
      'Link seasons with weather phrases in sentences',
    ],
    cultural: {
      title: 'El tiempo libre en España',
      subtitle: 'Leisure time in Spain',
      fact1: 'In Spain, the paseo — an evening walk through the town — is a tradition in every season. Whole families head out to chat, buy ice cream and enjoy the plaza.',
      fact2: 'Spain has more Blue Flag beaches than any other country in the world — ¡más de 500 playas de bandera azul!',
      fact3: 'Even in winter, Spanish families often eat outside — wrapping up in coats rather than staying indoors. La vida es para vivirla — life is for living!',
      imgFile: null,
    },
    warmUp: {
      prompt: 'Quick-fire T1 quiz with your partner — they ask, you answer in Spanish: ¿Tienes mascotas? ¿Cuántos años tienes? ¿Qué tiempo hace? ¿Qué estación es? Fire away!',
      hint: 'You know ALL of this from the last five lessons. Trust yourself — go for it!',
    },
    vocab: [
      { es:'¿Tienes mascotas?',  en:'Do you have pets?', pro:'tyeh-NESS mas-KOH-tahss' },
      { es:'Tengo un gato',      en:'I have a cat',       pro:'TEN-goh oon GAH-toh' },
      { es:'Hace sol',           en:'It\'s sunny',        pro:'AH-theh sol' },
      { es:'el verano',          en:'summer',             pro:'el beh-RAH-noh' },
      { es:'el invierno',        en:'winter',             pro:'el in-BYER-noh' },
      { es:'¡Repasamos!',        en:'Let\'s review!',     pro:'rreh-pah-SAH-moss' },
    ],
    phonics: {
      letter: 'LL',
      sound: 'Y sound — like "yes" or "yellow"',
      examples: [
        { word:'llamo',   meaning:'(I am) called', highlight:'ll' },
        { word:'llueve',  meaning:'it rains',       highlight:'ll' },
        { word:'caballo', meaning:'horse',          highlight:'ll' },
      ],
      tip: 'You know this from Y3 — LL = Y sound. Me llamo = meh YAH-moh. Llueve = YWEH-beh. Caballo = kah-BAH-yoh. The LL is the secret Y!',
    },
    activities: [
      {
        title: 'El Gran Repaso',
        instruction: 'T1 Quiz Show! Teams compete to answer in Spanish. Points for correct answers — bonus points for full sentences. Teacher is the quiz master!',
        steps: [
          'Round 1: Pets — ¿Qué animal es? (picture clues)',
          'Round 2: Numbers — call out or fill in the gap',
          'Round 3: Weather — mime → Spanish phrase',
          'Round 4: Seasons — match weather to season',
        ],
      },
      {
        title: '¡El reportero del tiempo!',
        instruction: 'Weather reporter challenge! In pairs, prepare a 30-second Spanish weather report covering at least two regions of Spain and two seasons. Then perform it to the class.',
        steps: [
          'Choose two Spanish regions (north/south or coast/mountains)',
          'Describe the weather there in Spanish',
          'Add a season: "En el verano en Sevilla..."',
          'Perform your forecast — audience scores you out of 10!',
        ],
      },
      {
        title: 'Mi mundo en español',
        instruction: 'Quick sketch and label! Draw your pet (or dream pet), today\'s weather and the current season. Label everything in Spanish, then describe your picture to your partner in full sentences.',
        steps: [
          'Draw: your pet (real or imaginary)',
          'Draw: today\'s weather with a symbol',
          'Draw: the current season (a tree, sun, leaves...)',
          'Label in Spanish — then describe to your partner!',
        ],
      },
    ],
    roundOff: {
      prompt: 'Standing circle: each person adds one Spanish sentence to build a shared "profile" — pet, number, weather, season. Keep going until everyone has contributed.',
      exit: 'Write 5 sentences in Spanish using T1 vocabulary — at least one about pets, one about weather and one about a season.',
      nextLesson: 'T2 coming soon — clothes, describing what you wear and when. ¡Hasta el próximo término!',
    },
  },

]; // end lessons

module.exports = { ALL_NUMBERS, lessons };
