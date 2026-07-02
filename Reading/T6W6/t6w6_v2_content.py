# T6W6 Being a Reader — full content for all levels
# Key question: Are England and Brazil different?
# Lessons: Mon 06/07 (Vocabulary) | Wed 08/07 (Retrieval) | Fri 10/07 (Inference)

KEY_Q  = "Are England and Brazil different?"
DATES  = {
    "Vocabulary": ("Monday",    "06/07/2026"),
    "Retrieval":  ("Wednesday", "08/07/2026"),
    "Inference":  ("Friday",    "10/07/2026"),
}
LF = {
    "Vocabulary": "LF: To understand key vocabulary",
    "Retrieval":  "LF: To be able to retrieve information from a text",
    "Inference":  "LF: To make inferences and apply my knowledge",
}
ICAN = {
    "Vocabulary": ("I can: use context and clues to make meaning",
                   "I can: answer questions related to vocabulary"),
    "Retrieval":  ("I can: scan to find key words",
                   "I can: answer questions with reference to the text"),
    "Inference":  ("I can: infer based on clues in the text",
                   "I can: answer questions with evidence from the text"),
}

# ═══════════════════════════════════════════════════════════
# STANDARD — Y4
# ═══════════════════════════════════════════════════════════

STD_VOC = ("Brazil is one of the most culturally diverse countries in the world. Its people speak Portuguese, which arrived with European settlers in the 1500s, but hundreds of indigenous languages are still spoken by communities across the Amazon basin. Over centuries, Brazil welcomed waves of immigrants from Africa, Japan, Italy, Germany and Lebanon, each bringing their own customs, food and traditions. This extraordinary blend of heritage has shaped modern Brazilian culture into something vivid and unlike anywhere else on Earth. England, too, has been shaped by the movement of people. Latin, French, Norse and Saxon languages all left their mark on English, which today borrows from more languages than almost any other tongue on the planet. Festivals like Diwali, Eid and Chinese New Year are celebrated in English cities alongside traditions that have existed for centuries. Though England is a far smaller country than Brazil, it holds a rich patchwork of local dialects, accents and customs — a Geordie from Newcastle speaks very differently to someone from Bristol. Culture is not fixed. In both countries, it changes and grows as communities share food, music, language and ideas. In Brazil, Carnival — the enormous annual festival of music, dance and costume — draws people from every region and background together in a great, joyful spectacle. In England, summer fetes, bonfire night and football bind communities in their own quieter ways. Despite the differences in scale, language and geography, both nations show that culture is always alive and always moving.")

VOC_VOCAB = [
    ("heritage",   "the traditions, values and customs passed down through generations"),
    ("indigenous", "originally from a place, before settlers or colonisers arrived"),
    ("dialect",    "a form of a language spoken in a particular area or by a particular group"),
    ("diverse",    "made up of many different types of people, ideas or things"),
    ("Carnival",   "a large annual festival involving music, dancing and colourful costumes"),
]
VOC_FOCUS = "heritage"

# Vocabulary owns: tick_v, fill, match  |  Shared: short2, evidence2, true_false, written
STD_VOC_QS = [
    ("Q1", "tick_v", "Which word below means 'originally from a place, before settlers arrived'?",
     ["indigenous", "heritage", "dialect"], "indigenous"),
    ("Q2", "fill", "Complete the sentence.\nBrazil welcomed ______________ of immigrants from Africa, Japan, Italy, Germany and Lebanon.",
     None, "waves"),
    ("Q3", "match", "Match each word to its correct definition.",
     [("heritage", "traditions and customs passed down through generations"),
      ("dialect", "a form of language spoken in a particular area"),
      ("Carnival", "a large festival of music, dancing and costumes")], None),
    ("Q4", "short", "What does the text say the blend of heritage has done to Brazilian culture?",
     None, "It has shaped modern Brazilian culture into something vivid and unlike anywhere else on Earth."),
    ("Q5", "true_false", "The text says English borrows from more languages than almost any other tongue on the planet.",
     None, "True"),
    ("Q6", "evidence2", "Give two examples the text uses to show that England is shaped by different cultures.",
     None, ["Festivals like Diwali, Eid and Chinese New Year are celebrated in English cities",
            "England holds a rich patchwork of local dialects, accents and customs"]),
    ("Q7", "written", "The text says 'Culture is not fixed.' Using evidence from the text, explain what this means and give one example to support your answer.",
     None, "Culture changes and grows as communities share food, music, language and ideas. In Brazil, Carnival — shaped by music and costume from many communities — and in England, festivals like Diwali and Eid now celebrated in cities show that culture keeps evolving rather than staying the same."),
]

VOC_WE_DO = [
    ("What does 'heritage' mean?",
     "The traditions, values and customs passed down through generations."),
    ("Name two groups of immigrants who came to Brazil and shaped its culture.",
     "Any two from: Africans, Japanese, Italians, Germans, Lebanese."),
]

STD_RET = ("For decades, vast stretches of the Amazon rainforest have been cleared to make way for farmland, cattle ranching and logging. At its peak in the early 2000s, Brazil was losing an area of forest the size of Belgium every year. Deforestation on this scale removes habitats for millions of species, releases stored carbon into the atmosphere and disrupts the water cycle that the entire South American continent depends upon. In recent years, Brazil has taken steps towards sustainability. The Amazon Fund, supported by Norway and Germany, has paid Brazil to reduce deforestation rates, and satellite technology is now used to monitor illegal logging. Between 2004 and 2012, Brazil cut its deforestation rate by nearly eighty percent — one of the largest conservation successes in history. However, rates rose again sharply in the late 2010s, and campaigners argue that the rainforest still faces serious threats. England faces its own sustainability challenges. Intensive farming has removed hedgerows, drained wetlands and reduced biodiversity across much of the countryside. In response, the government has introduced conservation schemes that pay farmers to restore habitats, plant trees and reduce chemical use. The Knepp Estate in West Sussex has become famous for its rewilding project, where land that was once intensively farmed has been returned to nature. Beavers, rare butterflies and turtle doves have returned to areas where they had not been seen for generations. Both Brazil and England show that protecting the natural world requires long-term commitment, political will and significant money.")

RET_VOCAB = [
    ("deforestation",  "the large-scale cutting down of trees in a forested area"),
    ("sustainability", "using natural resources carefully so they can continue to be available in the future"),
    ("biodiversity",   "the variety of plants and animals living in a particular area"),
    ("conservation",   "the protection and careful management of the natural environment"),
    ("rewilding",      "returning land to its natural state, allowing wildlife and habitats to recover"),
]
RET_FOCUS = "sustainability"

# Retrieval owns: quote, order, attrib_table  |  Shared: short, evidence2, true_false, short2
STD_RET_QS = [
    ("Q1", "short", "How large an area of forest was Brazil losing every year at its peak?",
     None, "An area the size of Belgium"),
    ("Q2", "true_false", "The Amazon Fund was supported by Norway and France.",
     None, "False"),
    ("Q3", "evidence2", "Give two problems that deforestation causes, according to the text.",
     None, ["It removes habitats for millions of species",
            "It releases stored carbon into the atmosphere / disrupts the water cycle"]),
    ("Q4", "quote", "Find and copy the phrase that shows how significant Brazil's reduction in deforestation was.",
     None, "one of the largest conservation successes in history"),
    ("Q5", "order", "Number these events in the order they happen in the text. (1 = first)",
     ["Deforestation peaked in the early 2000s",
      "The Amazon Fund is set up with Norway and Germany",
      "Brazil cut its deforestation rate by nearly 80%",
      "Deforestation rates rose again sharply"], "1,2,3,4"),
    ("Q6", "short2", "What has the Knepp Estate in West Sussex become known for, and what animals have returned there?",
     None, "The Knepp Estate is famous for its rewilding project, where land has been returned to nature. Beavers, rare butterflies and turtle doves have returned."),
    ("Q7", "attrib_table", "Which country does each of these statements describe? Tick the correct column.",
     [["Brazil", "England"],
      "Deforestation peaked at the size of Belgium per year",
      "The government pays farmers to restore habitats and plant trees",
      "The Amazon Fund reduced deforestation by nearly 80%",
      "Beavers and turtle doves have returned to rewilded land"],
     ["Brazil", "England", "Brazil", "England"]),
]

RET_WE_DO = [
    ("What does deforestation mean and why is it a problem?",
     "Deforestation is the large-scale cutting down of trees. It destroys habitats, releases carbon and disrupts the water cycle."),
    ("Name the two countries that supported the Amazon Fund.",
     "Norway and Germany."),
]

STD_INF = ("Climate change is already reshaping life in both Brazil and England, though in very different ways. In Brazil, rising temperatures have worsened droughts in the northeast, where communities that depend on river water for farming and drinking are finding rivers running lower than at any point in living memory. In the Amazon, scientists have found that some parts of the forest are now releasing more carbon than they absorb, a warning sign that one of the world's most important carbon stores may be approaching a tipping point. England's challenges look different but are no less serious. Winters are becoming wetter and summers hotter. Flooding has hit communities in Somerset, Yorkshire and Gloucestershire repeatedly in recent years, damaging homes and farmland. The Thames Barrier, built in 1982 to protect London from tidal surges, now closes far more frequently than its designers expected. Sea levels are rising, and low-lying coastal areas like East Anglia face an uncertain future. Both governments have made pledges. Brazil committed to ending illegal deforestation by 2030 under the Glasgow Climate Pact. The UK has set a legally binding target to reach net zero carbon emissions by 2050. But critics of both countries argue that promises on paper are not the same as action on the ground, and that for communities already feeling the effects — whether in the drought-stricken northeast of Brazil or a flooded village in Yorkshire — the pace of change is far too slow.")

INF_VOCAB = [
    ("tipping point", "the moment when a small change triggers a larger, often irreversible change"),
    ("emissions",     "gases such as carbon dioxide released into the atmosphere, usually from burning fuels"),
    ("net zero",      "the point at which the amount of greenhouse gases added equals the amount removed"),
    ("drought",       "a long period of very low rainfall leading to water shortages"),
    ("tidal surge",   "a sudden, large rise in sea level caused by storms or weather systems"),
]
INF_FOCUS = "emissions"

# Inference owns: mc, select, tf_table  |  Shared: short, short2, evidence2_ext, true_false, written
STD_INF_QS = [
    ("Q1", "mc", "What is making droughts worse in northeast Brazil?",
     ["Flooding", "Rising temperatures", "Deforestation", "Tidal surges"], "Rising temperatures"),
    ("Q2", "short", "In what year was the Thames Barrier built?",
     None, "1982"),
    ("Q3", "tf_table", "Are these statements True or False?",
     ["Brazil has committed to ending illegal deforestation by 2030",
      "The Thames Barrier now closes less often than its designers expected"],
     ["True", "False"]),
    ("Q4", "short2", "What have scientists found about the Amazon that concerns them? Use the text.",
     None, "Scientists found that some parts of the Amazon are now releasing more carbon than they absorb. This is worrying because the Amazon is one of the world's most important carbon stores and may be approaching a tipping point."),
    ("Q5", "select", "Tick ALL the effects of climate change mentioned in the text.",
     ["Worsening droughts in northeast Brazil",
      "Wildfires spreading across England",
      "Flooding in Somerset, Yorkshire and Gloucestershire",
      "Rivers running lower in northeast Brazil"],
     ["Worsening droughts in northeast Brazil",
      "Flooding in Somerset, Yorkshire and Gloucestershire",
      "Rivers running lower in northeast Brazil"]),
    ("Q6", "evidence2", "Give two pieces of evidence that show governments are being criticised for not doing enough about climate change.",
     None, ["Critics argue that promises on paper are not the same as action on the ground",
            "For communities in northeast Brazil or Yorkshire, the pace of change is far too slow"]),
    ("Q7", "written", "Why might someone reading this text feel frustrated by both governments' responses to climate change? Use evidence from the text in your answer.",
     None, "Both governments have made long-term pledges — Brazil by 2030 and the UK by 2050 — but for communities already suffering, like those in drought-stricken northeast Brazil or flooded villages in Yorkshire, this is too slow. Critics argue that 'promises on paper are not the same as action on the ground', showing a gap between political commitments and real impact."),
]

INF_WE_DO = [
    ("What are scientists worried about regarding the Amazon?",
     "Parts of the Amazon are now releasing more carbon than they absorb, so it may be approaching a tipping point and losing its ability to act as a carbon store."),
    ("Name one way climate change is affecting England differently to Brazil.",
     "England is experiencing wetter winters and flooding, while Brazil is experiencing worsening droughts."),
]

# ═══════════════════════════════════════════════════════════
# Y4-ADAPTED — shared by Asimenia, Jimi, Reggie (LMES), Asel, Bailey, Daisy (IM)
# Same 3-lesson structure; simpler text ~200 words; 5 Qs; 2 lines per written answer
# ═══════════════════════════════════════════════════════════

ADP_VOC = ("Brazil is one of the most diverse countries in the world. Portuguese is the main language spoken there, but many other languages are also spoken by communities in the Amazon. Over hundreds of years, people from many different countries came to Brazil. They brought their own food, music, traditions and languages. This made Brazilian culture rich and interesting. England has also been shaped by people arriving from different places. English has borrowed words from many other languages including French, Latin and Norse. Festivals such as Diwali and Eid are celebrated in English cities. Though England is much smaller than Brazil, it has many different dialects and local traditions. Culture does not stay the same. It changes as people share their ideas, food and music with each other. In Brazil, Carnival is a yearly festival of music, dance and bright costumes that brings people from all over the country together. In England, events such as bonfire night and local fetes bring communities together in a similar way. Both countries show that sharing culture helps communities grow and change over time.")

ADP_VOC_QS = [
    ("Q1", "tick_v", "What is the main language in Brazil?",
     ["English", "Portuguese", "French", "Spanish"], "Portuguese"),
    ("Q2", "fill", "Complete the sentence.\nFestivals such as Diwali and ______________ are celebrated in English cities.",
     None, "Eid"),
    ("Q3", "match", "Match each word to its meaning.",
     [("heritage", "traditions passed down through generations"),
      ("dialect",  "a form of language spoken in one area"),
      ("Carnival", "a festival with music and dancing")], None),
    ("Q4", "true_false", "The text says that culture stays the same over time.",
     None, "False"),
    ("Q5", "written", "Give one way England and Brazil are similar, using the text.",
     None, "Both England and Brazil have been shaped by people arriving from different places and bringing their own culture. Both also have festivals that bring communities together."),
]

ADP_RET = ("For many years, large areas of the Amazon rainforest in Brazil have been cut down to make space for farms and cattle. This is called deforestation. When trees are cut down, animals lose their homes and carbon is released into the air. This harms the water cycle that much of South America depends on. Brazil has tried to slow this down. A special fund, supported by Norway and Germany, paid Brazil to protect its forests and reduce the rate of deforestation. Satellite technology was also used to spot illegal logging. By 2012, Brazil had cut its deforestation rate by nearly 80 percent — a huge achievement. However, rates began to rise again in the late 2010s. England has its own challenges with looking after nature. Intensive farming has damaged wildlife and habitats across the countryside. In response, the government has set up conservation schemes that pay farmers to restore habitats, plant trees and reduce chemical use. The Knepp Estate in West Sussex is a well-known rewilding project. Land that was once intensively farmed has been given back to nature, and animals like beavers and turtle doves have returned.")

ADP_RET_QS = [
    ("Q1", "short", "What does the word 'deforestation' mean?",
     None, "Cutting down large areas of trees / forest"),
    ("Q2", "true_false", "The Amazon Fund was supported by Norway and Germany.",
     None, "True"),
    ("Q3", "evidence2", "Give two problems that deforestation causes.",
     None, ["Animals lose their homes / habitats are destroyed",
            "Carbon is released into the air / the water cycle is harmed"]),
    ("Q4", "quote", "Find and copy the number that shows how much Brazil cut its deforestation by.",
     None, "nearly 80 percent"),
    ("Q5", "written", "What has been done at the Knepp Estate in West Sussex?",
     None, "Land that was once intensively farmed has been turned into a rewilding project, and animals like beavers and turtle doves have returned."),
]

ADP_INF = ("Climate change is making life harder in both Brazil and England. In Brazil, it has caused worse droughts in the northeast. Communities there need river water for farming and drinking, but rivers are running lower than ever. In England, winters have become wetter and summers hotter. Many communities have been hit by flooding, including areas in Somerset and Yorkshire. The Thames Barrier was built in 1982 to protect London from floods. It now has to close much more often than it used to. Both countries have made promises about climate change. Brazil plans to stop illegal deforestation by 2030. The UK wants to reach net zero carbon by 2050. However, many people believe both countries need to act faster. The effects of climate change are already being felt by communities in both countries, and long-term targets do not always help people who are suffering right now. There is a growing gap between what governments promise and what they actually do.")

ADP_INF_QS = [
    ("Q1", "mc", "What is making droughts worse in northeast Brazil?",
     ["Heavy rainfall", "Rising temperatures", "Flooding", "Earthquakes"], "Rising temperatures"),
    ("Q2", "short", "When was the Thames Barrier built?",
     None, "1982"),
    ("Q3", "tf_table", "Are these statements True or False?",
     ["The UK has set a target to reach net zero carbon by 2050",
      "Brazil plans to stop all farming by 2030"],
     ["True", "False"]),
    ("Q4", "short2", "Why do many people think both countries need to act faster on climate change?",
     None, "The effects of climate change are already being felt by communities now, and long-term targets do not help people who are suffering right now."),
    ("Q5", "written", "Why might people in flooded villages in Yorkshire feel frustrated by the UK government's response to climate change?",
     None, "They are already experiencing flooding now, but the government's target is not until 2050. Long-term targets do not help people suffering right now."),
]

# ═══════════════════════════════════════════════════════════
# TEDDIE — Y3 (1 year behind → Y3 level for Y4)
# 3 lessons each blend Vocabulary + Retrieval + Inference
# 130–170 words per text; 5 Qs
# ═══════════════════════════════════════════════════════════

Y3_VOC_TEXT = ("Brazil and England are very different countries. Brazil is a very big country in South America. England is a smaller country in Europe. In Brazil, the weather is hot and tropical. In England, the weather is usually cool and rainy. The main language in Brazil is Portuguese. In England, people speak English. English has borrowed words from many other languages, including French and Latin. Both countries have lots of traditions. In Brazil, Carnival is a famous festival with music, dancing and colourful costumes. People from all over the country come together to celebrate. In England, people celebrate events like bonfire night and summer fetes. People in both countries love sport, especially football. Over many years, people from different places have come to live in both Brazil and England. They brought their own food, music and traditions. This has made both countries rich and interesting places to live.")

Y3_VOC_QS = [
    ("Q1", "tick_v", "What is the main language in Brazil?",
     ["English", "Portuguese", "Spanish", "French"], "Portuguese"),
    ("Q2", "true_false", "Carnival is a festival celebrated in England.",
     None, "False"),
    ("Q3", "short", "Name one festival celebrated in England.",
     None, "Bonfire night / summer fetes (accept either)"),
    ("Q4", "short", "What sport is popular in both countries?",
     None, "Football"),
    ("Q5", "written", "Give one way Brazil and England are different. Use the text.",
     None, "Brazil is a very big country in South America, while England is smaller and in Europe. / Brazil is hot and tropical, while England is cool and rainy."),
]

Y3_RET_TEXT = ("The Amazon rainforest is in Brazil. It is one of the largest forests in the world. Many animals and plants live there. For many years, people have been cutting down trees in the Amazon. This is called deforestation. Trees are cut down to make space for farms and cattle. When trees are cut down, animals lose their homes. In recent years, Brazil has tried to protect the rainforest. Satellite cameras are used to spot illegal logging. A special fund, paid for by other countries, helped Brazil to cut the amount of deforestation. England also has problems looking after nature. Many hedgerows and wetlands have been damaged by farming. The government now pays some farmers to plant trees and help wildlife. Some areas of land have been turned into rewilding projects, where animals can live safely. Both countries are working to protect nature, but there is still a lot more to do.")

Y3_RET_QS = [
    ("Q1", "short", "Where is the Amazon rainforest?",
     None, "Brazil"),
    ("Q2", "true_false", "Trees in the Amazon are cut down to build schools.",
     None, "False"),
    ("Q3", "short", "What are satellite cameras used for in Brazil?",
     None, "To spot / find illegal logging / where trees are being cut down"),
    ("Q4", "evidence2", "Give two ways the text shows that cutting down trees is a problem.",
     None, ["Animals lose their homes",
            "Habitats are destroyed / the forest shrinks / it harms the environment"]),
    ("Q5", "written", "What has England done to try to protect nature? Use the text.",
     None, "The government pays farmers to plant trees and help wildlife, and some land has been turned into rewilding projects where animals can live safely."),
]

Y3_INF_TEXT = ("Climate change is affecting both Brazil and England. In Brazil, some parts of the country have not had much rain. Rivers are getting lower. This makes it hard for people to find water for farming and drinking. In England, it has been raining more in winter. Some towns and villages have been flooded. Homes and farms have been damaged. Scientists are worried about the Amazon rainforest. Some parts of it are not absorbing as much carbon as they used to. This could make climate change worse. Both governments have made promises to try to help. Brazil wants to protect its forests. England has set targets to reduce carbon in the air. However, many people think both countries need to do more and act faster. People who are already flooded or facing drought cannot wait many years for change. They need help now, not just promises for the future.")

Y3_INF_QS = [
    ("Q1", "tick_v", "What is causing rivers to get lower in Brazil?",
     ["More rainfall", "Less rainfall / drought", "Flooding", "Deforestation"], "Less rainfall / drought"),
    ("Q2", "true_false", "Flooding has damaged homes and farms in England.",
     None, "True"),
    ("Q3", "short", "What are scientists worried about in the Amazon?",
     None, "Some parts aren't absorbing as much carbon as before, which could make climate change worse"),
    ("Q4", "short2", "Why do you think some people are frustrated with what governments are doing about climate change?",
     None, "People who are already being flooded or struggling to find water cannot wait years for long-term targets. They need help now."),
    ("Q5", "written", "How does the text show that climate change affects both countries? Give one example for each.",
     None, "In Brazil, less rainfall means rivers are getting lower. In England, more winter rain has caused flooding and damage to homes and farms."),
]

# ═══════════════════════════════════════════════════════════
# ROLAND — Y2
# 90–130 words per text; tick_v, true_false, short; 1 line each; 5 Qs
# ═══════════════════════════════════════════════════════════

Y2_VOC_TEXT = ("Brazil and England are in different parts of the world. Brazil is in South America. England is in Europe. Brazil is a very big country. England is much smaller. In Brazil, the weather is hot. In England, the weather is usually cool and rainy. The main language in Brazil is Portuguese. In England, people speak English. Both countries have lots of different people and traditions. In Brazil, Carnival is a big festival with music and dancing. In England, people celebrate bonfire night and sports events. Both countries love football. Different people have come to live in both countries over many years.")

Y2_VOC_QS = [
    ("Q1", "tick_v", "Where is Brazil?",
     ["Europe", "South America", "Africa", "Asia"], "South America"),
    ("Q2", "true_false", "The weather in Brazil is usually cool and rainy.",
     None, "False"),
    ("Q3", "short", "What is the main language in Brazil?",
     None, "Portuguese"),
    ("Q4", "true_false", "Carnival is a festival with music and dancing.",
     None, "True"),
    ("Q5", "short", "Name one event people celebrate in England.",
     None, "Bonfire night / sports events"),
]

Y2_RET_TEXT = ("The Amazon is a huge rainforest in Brazil. Many animals live there. Some people cut down trees in the Amazon. This is called deforestation. Trees are cut down to make space for farms. This hurts animals and the environment. Brazil is trying to protect the rainforest. Special cameras in space help to spot where trees are being cut down. England also has problems with nature. Lots of hedgerows and wetlands have been destroyed. Some farmers now plant trees to help wildlife. Some areas have been made into special places for animals. Both countries are working to look after the natural world.")

Y2_RET_QS = [
    ("Q1", "tick_v", "What is deforestation?",
     ["Planting more trees", "Cutting down trees", "Flooding rivers", "Building farms"], "Cutting down trees"),
    ("Q2", "true_false", "Trees in the Amazon are cut down to make space for farms.",
     None, "True"),
    ("Q3", "short", "What do special cameras in space help to spot?",
     None, "Where trees are being cut down"),
    ("Q4", "true_false", "England has never had any problems with nature.",
     None, "False"),
    ("Q5", "short", "What do some farmers in England do to help nature?",
     None, "Plant trees / help wildlife"),
]

Y2_INF_TEXT = ("The weather is changing all over the world. This is called climate change. In Brazil, some areas are getting too dry. Rivers have less water in them. This makes it hard for people and animals. In England, some winters have had a lot of rain. Some towns have flooded. Houses and farms have been damaged. Both countries are trying to do something about it. Brazil has made a promise to protect its forests. England has made a promise to make less pollution. Some people think both countries need to do more to help people now, not just make promises for the future.")

Y2_INF_QS = [
    ("Q1", "tick_v", "What does climate change cause in some parts of Brazil?",
     ["Snow", "Dry weather and less water", "Earthquakes", "More trees"], "Dry weather and less water"),
    ("Q2", "true_false", "Some towns in England have flooded.",
     None, "True"),
    ("Q3", "short", "What has Brazil promised to do?",
     None, "Protect its forests"),
    ("Q4", "short", "What has England promised to do?",
     None, "Make less pollution / reduce carbon"),
    ("Q5", "true_false", "Some people think both countries are already doing enough about climate change.",
     None, "False"),
]

# ═══════════════════════════════════════════════════════════
# HOPE — Y1
# 60–90 words per text; tick_v, true_false, short (copy a word); 6 Qs
# ═══════════════════════════════════════════════════════════

Y1_VOC_TEXT = ("Brazil is in South America. England is in Europe. Brazil is big and hot. England is small and cool. People in Brazil speak Portuguese. People in England speak English. Both countries have lots of people and traditions. In Brazil, Carnival is a festival with music, dancing and bright colours. In England, people celebrate bonfire night. Both countries love football. People have come from many places to live in both countries.")

Y1_VOC_QS = [
    ("Q1", "tick_v", "Where is Brazil?",
     ["Europe", "South America"], "South America"),
    ("Q2", "true_false", "People in Brazil speak English.",
     None, "False"),
    ("Q3", "tick_v", "What is Carnival?",
     ["A sport", "A festival"], "A festival"),
    ("Q4", "true_false", "England is big and hot.",
     None, "False"),
    ("Q5", "short", "Copy one word from the text that describes what Carnival has.",
     None, "music / dancing / colours (any one)"),
    ("Q6", "tick_v", "What sport do both countries love?",
     ["Tennis", "Football"], "Football"),
]

Y1_RET_TEXT = ("The Amazon is a big forest in Brazil. It is home to many animals and plants. Some people cut down trees in the Amazon. This is called deforestation. Animals lose their homes when trees are cut down. People in Brazil are trying to stop this. They use cameras to find where trees have been cut. In England, some farmers plant trees to help wildlife. Special places have been made for animals to live safely. Both countries are trying to look after nature.")

Y1_RET_QS = [
    ("Q1", "tick_v", "Where is the Amazon forest?",
     ["England", "Brazil"], "Brazil"),
    ("Q2", "true_false", "Trees in the Amazon are being cut down.",
     None, "True"),
    ("Q3", "tick_v", "What happens to animals when trees are cut down?",
     ["They get new homes", "They lose their homes"], "They lose their homes"),
    ("Q4", "short", "Copy the word from the text that means cutting down trees.",
     None, "deforestation"),
    ("Q5", "true_false", "Some farmers in England plant trees to help wildlife.",
     None, "True"),
    ("Q6", "tick_v", "What do cameras help people find?",
     ["New animals", "Where trees have been cut"], "Where trees have been cut"),
]

Y1_INF_TEXT = ("In Brazil, it has not been raining very much. Rivers have less water. This is hard for people who need water. In England, it has been raining a lot. Some places have flooded. This has damaged homes and farms. Both countries are worried about the weather changing. They have made promises to try to help. But some people think we all need to act now.")

Y1_INF_QS = [
    ("Q1", "tick_v", "What is happening to rivers in Brazil?",
     ["They have more water", "They have less water"], "They have less water"),
    ("Q2", "true_false", "Some places in England have flooded.",
     None, "True"),
    ("Q3", "tick_v", "What has flooding damaged in England?",
     ["Homes and farms", "Shops and trains"], "Homes and farms"),
    ("Q4", "true_false", "Both countries are worried about the weather changing.",
     None, "True"),
    ("Q5", "short", "Copy one word from the text that means flooding or rain problems.",
     None, "flooded / raining / flooded (any reasonable answer)"),
    ("Q6", "tick_v", "What do both countries want to do?",
     ["Stop farming", "Try to help"], "Try to help"),
]

# ═══════════════════════════════════════════════════════════
# ADNAN + CALLUM — Ph2 phonics-based text
# 30–50 words; tick or true_false only; max 3 Qs; glossary included
# ═══════════════════════════════════════════════════════════

PH2_GLOSSARY = {
    "Vocabulary": {
        "Brazil":   "a big country far away",
        "Carnival": "a big party with music and dancing",
        "English":  "the main language in England",
    },
    "Retrieval": {
        "Amazon":        "a huge forest in Brazil",
        "deforestation": "cutting down trees",
        "wildlife":      "animals that live in the wild",
    },
    "Inference": {
        "climate change": "when the weather all over the world starts to change",
        "flood":          "when too much water covers land",
        "drought":        "when there is not enough rain",
    },
}

PH2_VOC_TEXT = "Brazil is hot. England is not hot. Brazil has Carnival. Carnival has big music and lots of colour. England has bonfire night. Both places have lots of people. People in Brazil speak a lot. People in England speak a lot too."

PH2_VOC_QS = [
    ("Q1", "tick_v", "Is Brazil hot or not hot?",
     ["Hot", "Not hot"], "Hot"),
    ("Q2", "tick_v", "What is Carnival?",
     ["A sport", "A big party with music"], "A big party with music"),
    ("Q3", "true_false", "England is very hot.",
     None, "False"),
]

PH2_RET_TEXT = "The Amazon is a big forest in Brazil. People cut down lots of trees. This is bad for animals. Animals lose their homes. People are trying to help. Some men and women plant trees. This helps the animals."

PH2_RET_QS = [
    ("Q1", "tick_v", "Where is the Amazon?",
     ["England", "Brazil"], "Brazil"),
    ("Q2", "true_false", "Cutting down trees is good for animals.",
     None, "False"),
    ("Q3", "tick_v", "What do some people do to help?",
     ["Cut more trees", "Plant trees"], "Plant trees"),
]

PH2_INF_TEXT = "In Brazil, it has not had much rain. Rivers have less water. This is hard. In England, it has had too much rain. Some places got wet. People want things to get better."

PH2_INF_QS = [
    ("Q1", "tick_v", "What problem does Brazil have?",
     ["Too much rain", "Not enough rain"], "Not enough rain"),
    ("Q2", "tick_v", "What problem does England have?",
     ["Too much rain", "Not enough rain"], "Too much rain"),
    ("Q3", "true_false", "People want things to get better.",
     None, "True"),
]

# ═══════════════════════════════════════════════════════════
# Pupil profiles
# ═══════════════════════════════════════════════════════════

# Sort order within a day: Ph2 → Y1 → Y2 → Y3 → Y4-adapted → standard copies
# LMES adapted pupils (in sort order):
LMES_ADAPTED = [
    {"name": "Adnan",    "level": "Ph2"},
    {"name": "Callum",   "level": "Ph2"},
    {"name": "Hope",     "level": "Y1"},
    {"name": "Roland",   "level": "Y2"},
    {"name": "Asimenia", "level": "Y4-adapted"},
    {"name": "Jimi",     "level": "Y4-adapted"},
    {"name": "Reggie",   "level": "Y4-adapted"},
]
# IM adapted pupils (in sort order):
IM_ADAPTED = [
    {"name": "Teddie", "level": "Y3"},
    {"name": "Asel",   "level": "Y4-adapted"},
    {"name": "Bailey", "level": "Y4-adapted"},
    {"name": "Daisy",  "level": "Y4-adapted"},
]

LMES_STANDARD = ["Aaliyah","Cameron","Cruz","Delton","Dovind","Elliot","Eloho","Fola",
                  "Heidi","Isabelle","Isla","Jacob","Josh","Lilly","Lily H","Maisie",
                  "Mary","Meshach","Mia","Ralf","Ruby","Sebastian","Taylor"]  # 23
IM_STANDARD   = ["Amir","Arthur","Bonnie","Carena","Ceecee","Cody","Connie","Diyan",
                  "Emilia","Freya","Haris","Iris","Izzy","Jesse","Lois","Louie",
                  "Maddie","Maximilian","Penny","Phoebe","Ramani","Rory","Sam","Sohan",
                  "Zeek","Ziyad"]  # 26

# ═══════════════════════════════════════════════════════════
# GLOSSARY IMAGE PATHS — Ph2 and Y1 levels
# Used by draw_image_glossary() in the build script
# ═══════════════════════════════════════════════════════════

IMG_DIR = "/home/claude/gloss_imgs"

GLOSSARY_IMAGES = {
    "Vocabulary": {
        "Brazil":   f"{IMG_DIR}/brazil_flag.png",
        "Carnival": f"{IMG_DIR}/carnival_small.jpg",
        "English":  f"{IMG_DIR}/english_flag.png",
    },
    "Retrieval": {
        "Amazon":        f"{IMG_DIR}/amazon.jpg",
        "deforestation": f"{IMG_DIR}/deforest3.jpg",
        "wildlife":      f"{IMG_DIR}/wildlife.jpg",
    },
    "Inference": {
        "climate change": f"{IMG_DIR}/earth.png",
        "flood":          f"{IMG_DIR}/flood.jpg",
        "drought":        f"{IMG_DIR}/drought.jpg",
    },
}

# ═══════════════════════════════════════════════════════════
# LEVEL-SPECIFIC LEARNING LABELS
# Agreed T6W6 session. Y4-adapted and standard use lesson default.
# ═══════════════════════════════════════════════════════════

LL_PHONICS = {
    "lf":  "LF: To read accurately and understand what I have read",
    "sc1": "I can: recognise some words and decode others",
    "sc2": "I can: show my understanding of what I have read",
}

LL_2_PLUS_BEHIND = {
    "lf":  "LF: To read accurately and understand what I have read",
    "sc1": "I can: use different strategies to read and understand",
    "sc2": "I can: answer questions about what I have read",
}

LL_1_BEHIND = {
    "lf":  "LF: To read and comprehend different texts",
    "sc1": "I can: use different strategies to read and comprehend",
    "sc2": "I can: answer a variety of questions about what I have read",
}

# Map level tag → LL dict (None = use standard lesson LF)
LEVEL_LL = {
    "Ph2":        LL_PHONICS,
    "Y1":         LL_2_PLUS_BEHIND,
    "Y2":         LL_2_PLUS_BEHIND,
    "Y3":         LL_1_BEHIND,
    "Y4-adapted": None,   # uses standard lesson LF
    "Y4-standard":None,
}
