"""
SPACIFY THE LEXISNEXIS ARTICLES
===============================

This script will serialize the LexisNexis articles. The resulting spaCy `Docs`
will be stored in PATHS.data_prc. After processing all the files, an aggregated
count will be performed on all entities and all lemmas. This counting procedure
will be done twice: once counting every occurrence, and once counting entities
and lemmas only once per article. These results will be stored in PATHS.results.
It may happen that certain lemmas/entities fail to be counted. These will be
stored in PATHS.results as well.
"""

print('spacify lexisnexis articles')

# standard library
import json
import pickle
import sys
import time

start = time.time()
sys.path.insert(0, '../')

# third party
import pandas as pd
from spacy.util import load_model

# local
from src.config import PATHS, FILENAMES, LEXISNEXIS
from src.spacy_helpers import serialize_batch, fetch_docs
from src.doc_analysis import basic_stats, attribute_counter, most_common


### Serialize LexisNexis documents
print("[1] serialize batches")
nlp = load_model(PATHS.model)
for batch in LEXISNEXIS.batches:
    serialize_batch(nlp, batch)


### Store some general stats
print("[2] store stats")
def get_stats(batch):
    data = list()
    for doc in fetch_docs(PATHS.data_prc / batch, nlp.vocab):
        stats = basic_stats(doc)
        data.append(stats)
    df = pd.DataFrame(data)
    df.columns = [col.lower() for col in df.columns]
    return df

pd.concat(
    [get_stats(batch) for batch in LEXISNEXIS.batches], sort=False,
).to_pickle(PATHS.results / FILENAMES.nlp_statistics)


### Store entity and token counts
print("[3] store counts")
all_fails = list()
batches_totals = dict()
batches_unique = dict()
for batch in LEXISNEXIS.batches:
    batch_totals = dict()
    batch_unique = dict()
    for doc in fetch_docs(PATHS.data_prc / batch, nlp.vocab):
        totals, fails = attribute_counter(doc)
        unique, _ = attribute_counter(doc, unique=True)
        if fails:
            all_fails.append(fails)
        for key in totals:
            if key not in batch_totals:
                batch_totals[key] = totals[key]
            else:
                batch_totals[key] = batch_totals[key] + totals[key]
        for key in unique:
            if key not in batch_unique:
                batch_unique[key] = unique[key]
            else:
                batch_unique[key] = batch_unique[key] + unique[key]
    batches_totals[batch] = batch_totals
    batches_unique[batch] = batch_unique

d = {
    FILENAMES.dct_counts_total:  batches_totals,
    FILENAMES.dct_counts_unique: batches_unique,
}
for key in d:
    with open(PATHS.results / key, 'wb') as f:
        pickle.dump(d[key], f)

flatten_fails = [fail for fails in all_fails for fail in fails]
print(f"---encountered {len(flatten_fails)} failed items.")

with open(PATHS.results / 'unrecognized_tokens.json', 'w') as f:
    json.dump(all_fails, f, indent=4)


### Store as dataframes
print("[4] store as dataframes")
def dict_to_df(dct, batch):
    return (
        pd.DataFrame
            .from_dict(dct[batch], orient='index')
            .stack()
            .to_frame()
            .rename(columns={0: batch})
    )

d = {
    FILENAMES.df_counts_total:  batches_totals,
    FILENAMES.df_counts_unique: batches_unique,
}
for filename, dct in d.items():
    df = pd.concat([dict_to_df(dct[b], b) for b in LEXISNEXIS.batches], axis=1)
    df.to_pickle(PATHS.results / filename)

print(df.count())

end = time.time()
print(f"finished in: {round(end - start)}s")
