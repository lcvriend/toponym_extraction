"""
SPACIFY THE LEXISNEXIS ARTICLES
===============================

This script will serialize the LexisNexis articles. The resulting spaCy `Docs`
will be stored
"""

# standard library
import json
import pickle

# third party
import pandas as pd
from spacy.util import load_model

# local
from src.config_ import PATHS, LEXISNEXIS
from src.spacy_helpers import serialize_batch, fetch_docs
from src.doc_analysis import basic_stats, attribute_counter, most_common


### Serialize LexisNexis documents
nlp = load_model(PATHS.model)

for batch in LEXISNEXIS.batches:
    serialize_batch(nlp, batch)


### Store some general stats
df_stats = pd.DataFrame()
for batch in LEXISNEXIS.batches:
    pre_df = list()

    for doc in fetch_docs(PATHS.data_prc / batch, nlp.vocab):
        stats = basic_stats(doc)
        pre_df.append(stats)

    df_doc = pd.DataFrame(pre_df)
    df_doc.columns = [col.lower() for col in df_doc.columns]

    df_stats = df_stats.append(df_doc, sort=False)
df_stats.to_pickle(PATHS.results / 'df_nlp_stats.pkl')


### Store entity and token counts
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
    'dct_total_tokens_and_entities': batches_totals,
    'dct_unique_tokens_and_entities': batches_unique,
}
for key in d:
    with open(PATHS.results / f"{key}.pkl", 'wb') as f:
        pickle.dump(d[key], f)

flatten_fails = [fail for fails in all_fails for fail in fails]
print(f"Encountered {len(flatten_fails)} failed items.")

with open(PATHS.results / 'unrecognized_tokens.json', 'w') as f:
    json.dump(all_fails, f, indent=4)


### Store as dataframes
df_totals = pd.DataFrame()
for batch in LEXISNEXIS.batches:
    df = pd.DataFrame.from_dict(batches_totals[batch], orient='index')
    df = df.stack().to_frame().rename(columns={0: batch})
    if df_totals.empty:
        df_totals = df
    else:
        df_totals = df.merge(df_totals, how='outer', left_index=True, right_index=True)
df_totals.to_pickle(PATHS.results / 'df_counts_totals.pkl')

df_unique = pd.DataFrame()
for batch in LEXISNEXIS.batches:
    df = pd.DataFrame.from_dict(batches_unique[batch], orient='index')
    df = df.stack().to_frame().rename(columns={0: batch})
    if df_unique.empty:
        df_unique = df
    else:
        df_unique = df.merge(df_unique, how='outer', left_index=True, right_index=True)
df_unique.to_pickle(PATHS.results / 'df_counts_unique.pkl')
