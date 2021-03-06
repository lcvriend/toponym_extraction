"""
CREATE NLP MODEL FOR IDENTIFIYING TOPONYMS
==========================================

This script creates the NLP model in spaCy for identifying toponyms.
The toponyms are divided into countries and cities.
- Countrty toponyms are taken from 'http://restcountries.eu/'.
- City toponyms are taken from 'http://www.geonames.org/'.


## GEO DATA
**restcountries**
All countries from the restcountries dataset are selected in the language
defined in [PROJECT] in 'config.ini'. In this project an 'alts_countries.json'
is passed as well, providing alternative names for some of the countries.

**Geonames**
In the current project the 'cities5000' dataset is used which contains
all cities with a population > 5000 or which are a seat of a first-order
administrative division. The data is loaded with the `load_geonames` function.
This function will select the place name in the language set under [PROJECT] in
'config.ini'.

It is important to note that certain toponyms may refer to multiple places.
Here this ambiguity is dealt with by assigning the place name to the place with
the largest population and ignoring the others. If it is necessary to deal with
this ambiguity differently than you will need to adjust the code to fit your
needs.


## GEOGRAPHICAL ENTITIES
The city toponyms may be subcategorized using the [MODEL] chapter in
'config.ini' by assigning a label to a query that will run on the geonames
dataset. This will allow spaCy to group toponyms together under the assigned
labels. In the current iteration of the project four categories are
distinguished:
- 'places_uk': places in the UK
- 'places_nl': places in the NL but not Friesland
- 'places_fr': places in Friesland
- 'places':    places in the world which are in none of the above


## WORKFLOW
The script first sets up the topographies based on the project settings. Because
this project uses a naive approach, i.e. simply counting toponyms, there
should not be any homonyms between the topographies. Therefore, when building
the model the topographies are compared to eachother. If any homonyms are found,
they are stored under 'duplicate_place_names.json' in the PAHTS.results folder.

The script should be run twice: once before and once after the annotation phase.
Because this method will initially create many false positives, a round of
annotation takes place where all found entities are marked as either positive
(when it correctly matches the geographical entity) or negative (when it does
not). The second time the model is built only the positive identities are added.

The model itself will be stored in the `PATHS.model` folder.
"""

# standard library
import json
import sys
import time
from itertools import combinations

start = time.time()
sys.path.insert(0, '../')

# third party
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

# internal
from src.config import PATHS, MODEL
from src.doc_analysis import get_positives
from src.geo_data import (
    load_geonames,
    load_rest_countries,
)


### Prepare geo entities
# load datasets
print('loading RESTcountries')
countries = load_rest_countries()
print('loading geonames')
geonames = load_geonames()

# remove geonames that are also country names and store the table
geonames = geonames.query("alternate_name not in @countries")
path = PATHS.resources / 'geonames/df_geonames.pkl'
if not path.exists():
    path.mkdir(parents=True, exist_ok=True)
geonames.to_pickle(path)

# create topography
print('creating topography')
topography = {k:getattr(MODEL, k) for k in MODEL._fields}
topography = {k:geonames.query(v).alternate_name for k, v in topography.items()}
topography['countries'] = countries
for k in topography:
    topography[k] = [{'label': k, 'pattern': v} for v in topography[k]]


### Check for duplicates between topographies
problems = dict()
place_names = dict()
for key in topography:
    patterns = set()
    for d in topography[key]:
        patterns.add(d['pattern'])
    place_names[key] = patterns

for key1, key2 in list(combinations(place_names, r=2)):
    if place_names[key1] & place_names[key2]:
        new_key = (key1, key2)
        duplicates = place_names[key1] & place_names[key2]
        print("Duplicate found: ", new_key, ": ", duplicates, "\n")
        problems[new_key] = list(duplicates)

path = PATHS.parameters / 'duplicate_place_names.json'
with open(path, 'w', encoding='utf8') as f:
    json.dump(problems, f, indent=4)


### Select topography based on annotation results
for key in topography:
    patterns = list()
    try:
        annotation = PATHS.annotations / f"df_annotations_{key}.pkl"
        positives = get_positives(pd.read_pickle(annotation), threshold=50)
    except FileNotFoundError:
        continue

    for item in topography[key]:
        if item['pattern'] in positives:
            patterns.append(item)

    topography[key] = patterns


### Create model
print('building model')
nlp = spacy.load('nl', disable=['ner'])
ruler = EntityRuler(nlp)
for label in topography:
    ruler.add_patterns(topography[label])
nlp.add_pipe(ruler)
nlp.to_disk(PATHS.model)

end = time.time()
print(f"Finished in: {round(end - start)}s")
