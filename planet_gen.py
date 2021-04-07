import os
os.chdir(os.path.dirname(__file__))
import json
import random
from functools import reduce

import spacy
import tracery
from tracery.modifiers import base_english
from collections import Counter
nlp = spacy.load('en_core_web_sm')

def file_count():
    # This is our counter
    count = 0

    # Notice r'' raw string to preserve literal backslash
    for file in os.listdir():
        if('grammar' in file):
            print(file)
            count += 1
    print('Total:', count)
    return count




#starter code stolen with gratitude from allison parrish - https://github.com/aparrish/corpus-driven-narrative-generation
corpus = open('internet_archive_scifi_v3.txt')
sentences = corpus.read().split('. ')
words = []
noun_chunks = []
entities = []

for i, sent in enumerate(random.sample(sentences, 1000)):
    doc = nlp(sent)
    words.extend([w for w in list(doc) if w.is_alpha])
    noun_chunks.extend(list(doc.noun_chunks))
    entities.extend(list(doc.ents))

# strip to uniques
def return_unique(a,b):
    if a.text != b.text:
        return a
#words = reduce(return_unique, list(words_raw))
#noun_chunks = reduce(return_unique, noun_chunks_raw)

#get POS tags
subjects = [chunk.text for chunk in noun_chunks if chunk.root.dep_ == 'nsubj']
objects = [chunk.text for chunk in noun_chunks if chunk.root.dep_ == 'dobj']

nouns = [w.text for w in words if w.pos_ == "NOUN"]
verbs = [w.text for w in words if w.pos_ == "VERB"]
past_tense_verbs = [w.text for w in words if w.tag_ == 'VBD']
adjs = [w.text for w in words if w.tag_ == "JJ"]
advs = [w.text for w in words if w.pos_ == "ADV"]

people = [e.text for e in entities if e.label_ == "PERSON"]
locations = [e.text for e in entities if e.label_ == "LOC"]
times = [e.text for e in entities if e.label_ == "TIME"]
events = [e.text for e in entities if e.label_ == "EVENT"]

test_grammar = {'subs': list(set(subjects)), 'objs': list(set(objects)), 'nouns': list(set(nouns)), 'verbs' : list(set(verbs)), 'past_tense_verbs': list(set(past_tense_verbs)), 'adjs': list(set(adjs)), 'advs': list(set(advs)), 'people': list(set(people)), 'locs': list(set(locations)), 'times': list(set(times)), 'events': list(set(events))}
location_count = Counter([w for w in locations])
print('least common locations: ', location_count.most_common()[:-5-1:-1])

event_count = Counter([w for w in events])
print('least common events: ', event_count.most_common()[:-5-1:-1])
#Raw pull from text grammar
#This could be good for filler text, AI text - 'poorly translated' documents of the planet
rules = {
    #TODO adverbs
    "subject": [w for w in subjects],
    "object": [w for w in objects],
    "verb": [w for w in past_tense_verbs if w not in ('was', 'were', 'went')], # exclude common irregular verbs
    "adj": [w for w in adjs],
    "people": [w for w in people],
    "loc": [w for w in locations],
    "time": [w for w in times],
    "event": [w for w in events],
    "origin": "#scene#\n\n[charA:#loc#][charB:#object#][prop:#adjective#]#sentences#",
    "scene": "#loc#, #time.lowercase#",
    "sentences": [
        "#sentence#\n#sentence#",
        "#sentence#\n#sentence#\n#sentence#",
        "#sentence#\n#sentence#\n#sentence#\n#sentence#"
    ],
    "sentence": [
        "#charB.capitalize# is known to #verb# on #charA#.",
        "The #charB.capitalize# is #adj# and #adj#, and #verb#s.",
    ]
}
grammar = tracery.Grammar(rules)
grammar.add_modifiers(base_english)

object_descs = []
for i in range(3):
    object_descs.append(grammar.flatten("#origin#"))

#curated grammar
with open('planet_type_grammars.json', 'r') as planet_json:
    planet_data = json.load(planet_json)
    planet_key = list(planet_data.keys())[random.randint(0, 1)]
    planet = planet_data[planet_key]
    planet_rules = {
    #TODO adverbs
        "ptverb": [w for w in planet['grammar']['ptverbs'] if w not in ('was', 'were', 'went')], # exclude common irregular verbs
        "verb": [w for w in planet['grammar']['verbs']],
        "culture_adj": [w for w in planet['grammar']['culture_adjs']],
        "nature_adj": [w for w in planet['grammar']['nature_adjs']],
        "event_noun": [w for w in planet['grammar']['event_nouns']],
        "people_noun": [w for w in planet['grammar']['people_nouns']],
        "person": [w for w in planet['grammar']['people']],
        "loc": [w for w in planet['grammar']['locs']],
        "time": [w for w in planet['grammar']['times']],
        "origin": "#scene#\n\n[charA:#loc#][charB:#person#][prop:#event_noun#]#sentences#",
        "scene": "#loc#, #time.lowercase#",
        "sentences": [
            "#sentence# #sentence#",
            "#sentence# #sentence# #sentence#",
            "#sentence# #sentence# #sentence# #sentence#"
        ],
        "sentence": [
            "#charA.capitalize# #ptverb# #people_noun#.",
            "#charB.capitalize# led #charA#, before the #prop# .",
            "#prop.capitalize# became #culture_adj#, at the #event_noun#.",
            "#person.capitalize# and #charA# were known to be #culture_adj#, before the #event_noun#.",
            "#charA.capitalize# was famous for #event_noun# #verb# #people_noun#.",
            "#charA.capitalize# fell during the #event_noun# of #charB#, a #culture_adj# #event_noun#."
        ]
    }
    planet_grammar = tracery.Grammar(planet_rules)
    planet_grammar.add_modifiers(base_english)

    desc = planet_grammar.flatten("#origin#")
    type = planet_key
    name = desc.split(',')[0]
    objects = []
    for i in planet['obj_categories']:
        rand = random.random()
        obj_type = ''
        if rand > 0.9:
            for i in range(3):
                obj_type += planet['obj_categories'][random.randint(0, 2)]
        elif rand > 0.7:
            for i in range(2):
                obj_type += planet['obj_categories'][random.randint(0, 2)]
        elif rand > 0.5:
                obj_type += planet['obj_categories'][random.randint(0, 2)]
        else:
                obj_type += planet['obj_categories'][random.randint(0, 1)]
        objects.append({'type': obj_type, 'desc': object_descs[planet['obj_categories'].index(i)]})
    event_chance  = random.random()
    planet_gen = {'name': name, 'desc': desc, 'type': type, 'objects': objects}
    if event_chance > 0.9:
        event = random.choice(planet['events'])
        planet_gen['event'] = event
    print(planet_gen)

#write random grammars to file
#page = file_count()
#with open('grammar_test_' + str(page) + '.json', 'w') as outfile:
#    out_json = json.dumps(test_grammar)
#    outfile.write(out_json)
corpus.close()


