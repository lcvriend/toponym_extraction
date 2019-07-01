# standard library
from collections import Counter

# third party
import pandas as pd
from IPython.display import HTML, display, clear_output


def phrase_explorer(df, search):

    style = """
        <style>
            * {
                box-sizing: border-box;
            }
            h1, h3, h4, p {
                margin: 0 !important;
                padding: 12px;
            }
            h1 {
                background-color: black;
                color: white;
            }
            hr {
                margin: 0 !important;
                border: none;
                border-top: 1px solid black;
            }
            .box {
                border: 1px solid black;
            }
        </style>
        """

    def explore(search, results):
        for idx, row in df_q.reset_index().iterrows():
            html = f"<h1>SOURCE: {row.source}</h1>"
            html += f"<h3>RESULT: {idx + 1} of {results} | {row.id}</h3><hr>"
            html += f"<h4>{row.title}</h4><hr>"

            for p in row.body:
                if search in p:
                    p = f"<p>{p}</p>"
                    html += p.replace(search, f"<mark>{search}</mark>")

            html = f"{style}<div class='box'>{html}</div>"
            display(HTML(html))
            user = input(
                "Press <enter> to continue "
                "(you can also input a new search phrase or '.' to exit)"
                )
            clear_output()
            if user == '.':
                return user
            if len(user) > 0:
                return user
        return '.'

    while search != '.':
        df_q = df.query("body_.str.contains(@search)", engine='python')
        results = len(df_q)
        search = explore(search, results)
    return None


def basic_stats(doc):
    """
    Extract some basic statistics from a spaCy `Doc` instance as `dict`:
    - n_sentences: number of sentences
    - n_entities:  number of entities
    - n_tokens:    number of tokens
    - n_stopwords: number of stopwords

    - count per part of speech attributes
    - count per entity type

    Parameters
    ==========
    :param doc: instance of spaCy `Doc` class

    Returns
    =======
    :basic_stats: `dict`
    """

    stats = dict()
    stopwords = 0
    sen_counts = Counter() # sentences
    pos_counts = Counter() # parts of speech
    ent_counts = Counter() # entities
    ent_unique = dict()

    for token in doc:
        if token.is_stop:
            stopwords += 1
        pos_counts[f"pos_{token.pos_}"] += 1
    for ent in doc.ents:
        ent_counts['n_entities'] += 1
        ent_counts[f"ent_{ent.label_}"] += 1
        if ent.label_ in ent_unique.keys():
            ent_unique[ent.label_].add(ent.text)
        else:
            ent_unique[ent.label_] = set(ent.text)
    for sent in doc.sents:
        sen_counts['n_sentences'] += 1

    stats['n_tokens'] = len(doc)
    stats['n_stopwords'] = stopwords
    stats.update(sen_counts)
    stats.update(pos_counts)
    stats.update(ent_counts)
    for key in ent_unique:
        stats[f"uniq_ent_{key}"] = len(ent_unique[key])

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
            if unique and token.lemma_ in counters['lemma'].keys():
                continue
            if relevant_token:
                counters['lemma'][token.lemma_] += 1
        except KeyError:
            fails.append((doc._.id, token))
    for ent in doc.ents:
        if ent.label_ not in counters:
            counters[ent.label_] = Counter()
        if unique and ent.text in counters[ent.label_].keys():
            continue
        counters[ent.label_][ent.text] += 1

    return counters, fails


def most_common(data, attribute, n=10):
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

    Returns
    =======
    :most_common: `DataFrame`
    """

    df = pd.DataFrame()

    if isinstance(data, pd.DataFrame):
        sources = data.source.unique()
        for source in sources:
            qry = f'source == @source'
            cols = pd.MultiIndex.from_product([[source], [attribute, 'count']])
            n_most_common = (
                data.query(qry)[attribute]
                    .value_counts()
                    .to_frame()
                    .reset_index()
                    .head(n)
                )
            if df.empty:
                df = n_most_common
                df.columns = cols
            else:
                n_most_common.columns = cols
                df = df.join(n_most_common)

    else:
        for source in data:
            cols = pd.MultiIndex.from_product([[source], ['label', 'count']])
            n_most_common = data[source][attribute].most_common(n)
            df_ = pd.DataFrame(n_most_common, columns=cols)
            if df.empty:
                df = df_
            else:
                df = df.join(df_)

    return df
