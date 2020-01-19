# standard library
import json
import pickle
from collections import Counter

# third party
import pandas as pd

# local
from src.config_ import PATHS, FILENAMES, LEXISNEXIS


def basic_stats(doc):
    """
    Extract some basic statistics from a spaCy `Doc` instance as `dict`:
    - n_tokens:          number of tokens
    - n_stopwords:       number of stopwords
    - n_words:           number of tokens - number of stopwords
    - n_sentences:       number of sentences
    - n_entities:        number of entities
    - n_unique_entities: number of unique entities

    - counts per part of speech attribute
    - counts per entity type

    Parameters
    ==========
    :param doc: instance of spaCy `Doc` class

    Returns
    =======
    :basic_stats: `dict`
    """

    stats = dict()
    stats['id'] = doc._.id
    stopwords = 0
    sen_counts = Counter() # sentences
    pos_counts = Counter() # parts of speech
    ent_counts = Counter() # entities
    ent_unique = dict()
    ent_unique['_total'] = set()

    for token in doc:
        if token.is_stop:
            stopwords += 1
        pos_counts[f"pos_{token.pos_}"] += 1
    for ent in doc.ents:
        ent_counts['n_entities'] += 1
        ent_counts[f"ent_{ent.label_}"] += 1
        if ent.label_ not in ent_unique.keys():
            ent_unique[ent.label_] = set()
        ent_unique['_total'].add(ent.text)
        ent_unique[ent.label_].add(ent.text)

    for sent in doc.sents:
        sen_counts['n_sentences'] += 1

    stats['n_tokens'] = len(doc)
    stats['n_stopwords'] = stopwords
    stats['n_words'] = stats['n_tokens'] - stats['n_stopwords']
    stats.update(sen_counts)
    stats.update(pos_counts)
    stats.update(ent_counts)
    stats['n_unique_entities'] = len(ent_unique['_total'])
    for key in ent_unique:
        if key == '_total':
            continue
        stats[f"unique_ent_{key}"] = len(ent_unique[key])

    return stats


def attribute_counter(doc, unique=False):
    """
    Count occurrances of all lemmas and entities in a spaCy `Doc` instance.
    Return results as a `dict` of `dicts`:
    - Key for the `dict` containing the lemmas is 'lemma'.
    - Key for the `dict` containing a particular entity is the entity label.
    - The containing `dicts` are `Counter` instances, where:
        * The key is the token.text/ent.text.
        * The value is the count of the key within the doc.
    If 'unique' is True, similar items are only counted once.

    Parameters
    ==========
    :param doc: instance of spaCy `Doc` class

    Optional key-word arguments
    ===========================
    :param unique: `boolean`, default=False
        Set to True to count only unique occurrances.

    Returns
    =======
    :basic_stats: `dict` of `dicts`
    """

    fails = list()
    counters = dict()
    counters['lemma'] = Counter()

    for token in doc:
        relevant_token = (
            not token.is_stop and
            not token.is_punct and
            not token.is_space and
            not token.is_quote and
            not token.text == '\n'
            )
        try:
            if unique and token.lemma_ in counters['lemma']:
                continue
            if relevant_token:
                counters['lemma'][token.lemma_] += 1
        except KeyError:
            fails.append((doc._.id, token))
    for ent in doc.ents:
        if ent.label_ not in counters:
            counters[ent.label_] = Counter()
        if unique and ent.text in counters[ent.label_]:
            continue
        counters[ent.label_][ent.text] += 1

    return counters, fails


def most_common(data, attribute, n=10, label_col='label', frq_col='count'):
    """
    Return the n most common attributes per source as DataFrame.

    Parameters
    ==========
    :param data: `dict` or `DataFrame`
        - `dict` mapping sources to their attribute counts.
        - `DataFrame` extracted by the LexisNexis parser.
    :param attribute: `string`
        Name of the attribute to return.

    Optional key-word arguments
    ===========================
    :param n: `int`, default=10
        Number of attributes to return.
    :param label_col: `str`, default='label'
        Name for the label column.
    :param frq_col: `str`, default='count'
        Name for the frequency column.

    Returns
    =======
    :most_common: `DataFrame`
    """

    if isinstance(data, pd.DataFrame):
        def transform(data, source, attribute, n=n):
            cols = pd.MultiIndex.from_product([[source], [label_col, frq_col]])
            qry = f"source == @source"
            df = (
                data.query(qry)[attribute]
                    .value_counts()
                    .to_frame()
                    .reset_index()
                    .head(n)
                )
            return pd.DataFrame(df, columns=cols)
        sources = data.source.unique()

    else:
        def transform(data, source, attribute, n=n):
            cols = pd.MultiIndex.from_product([[source], [label_col, frq_col]])
            try:
                n_most_common = data[source][attribute].most_common(n)
                return pd.DataFrame(n_most_common, columns=cols)
            except KeyError:
                return pd.DataFrame()
        sources = data.keys()

    dfs = [transform(data, source, attribute) for source in sources]
    df = pd.concat(dfs, axis=1)
    df.index.name = 'ranking'
    return df


def overlapping_items(data, attribute, n=12):
    counts = Counter()
    keys = data.keys()
    labels = most_common(
        data,
        attribute,
        n=n
    ).xs('label', level=1, axis=1)
    for key in keys:
        for item in labels[key]:
            counts[item] += 1
    return counts.most_common()


def get_positives(df, threshold=100):
    """
    Return a list of phrases that have at least one positive annotation.
    Input is a df_annotations `DataFrame` created by the annotator.

    Parameters
    ==========
    :param df: `DataFrame`
        df_annotations `DataFrame` created by the annotator.

    Optional key-word arguments
    ===========================
    :param threshold: `int`, default=100
        Threshold determining if a phrase is considered postive.
        If the percentage of positive annotations of a phrase is higher than
        or equal to the threshold, then the phrase is marked positive.

    Returns
    =======
    :get_positives: `list`
    """

    df = df.pivot_table(
        index='phrase',
        columns='annotation',
        values='id',
        aggfunc='count',
        fill_value=0
    )
    df['%'] = (df['+'] / (df.sum(axis=1)) * 100).round(1)
    df['positive'] = df['%'] >= threshold
    return list(df[df['positive']].index)


def load_counts(merge_entries=True, stopwords=None):
    """
    Return a dictionary of dictionaries with total and unique places counts.
    If merge_entries is True synonymous entries are merged in to the main entry.
    If a list of stopwords is given, these will be removed from 'lemma'.
    """

    d = dict()

    files = {
        'total':  FILENAMES.dct_counts_total,
        'unique': FILENAMES.dct_counts_unique,
    }
    for key, file in files.items():
        with open(PATHS.results / file, 'rb') as f:
            d[key] = pickle.load(f)

    # merge synonymoous entries into their main entry
    if merge_entries:
        alts_file = PATHS.parameters / 'alts_countries.json'
        with open(alts_file, 'r', encoding='utf8') as f:
            alts_countries = json.load(f)

        for count_type in d:
            for batch in LEXISNEXIS.batches:
                for country in alts_countries:
                    for alt in alts_countries[country]:
                        n = d[count_type][batch]['countries'][alt]
                        del d[count_type][batch]['countries'][alt]
                        d[count_type][batch]['countries'][country] += n

    # remove any given stopwords
    if stopwords is not None:
        for count_type in d:
            for batch in LEXISNEXIS.batches:
                for stopword in stopwords:
                    del d[count_type][batch]['lemma'][stopword]

    return d


def load_lexisnexis_data(add_stats=True):
    """
    Load all lexisnexis data into a single `DataFrame`.
    Skips any files starting with '_'.

    Returns
    =======
    :load_lexisnexis_data: `DataFrame`
    """

    files = PATHS.data_int.glob('[!_]*.pkl')
    dfs = [pd.read_pickle(f) for f in files]
    df = pd.concat(dfs)
    df = df.set_index('id')
    if add_stats:
        stats_file = PATHS.results / FILENAMES.nlp_statistics
        df = df.join(pd.read_pickle(stats_file).set_index('id'))
    return df
