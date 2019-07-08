# standard library
import re
from collections import Counter
from datetime import datetime

# third party
import pandas as pd
from IPython.display import HTML, display, clear_output

# local
from src.config import PATH_DATA_I, PATH_RESULTS


STYLE = """
    * {
        box-sizing: border-box;
    }
    h1, h2, h3, h4, p, .container {
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
    """


def annotator(df, phrases, name='df_annotations', n=5, info=None):
    """
    Annotate search results.
    Annotations are stored in PATH_RESULTS as a pickled ` DataFrame`:
    > 'df_annotations.pkl'.

    The annotator skips phrases that were annotated in a previous session.

    Parameters
    ==========
    :param df: `DataFrame`
        df containing the LexisNexis articles.
    :param phrases: iterable
        Iterable of phrases to annotate.

    Optional key-word arguments
    ===========================
    :param name: `str`
        Name of the `DataFrame` where the annotations will be stored.
    :param n: `int`, default=5
        Number of samples to annotate per phrase.
    :param info: `tuple` of `str`, `DataFrame`
        Tuple containing:
        - Name of the column containing the phrase key
        - DataFrame with the phrase info
        The annotator will search the key-column for phrase matches.
        The matched records will be displayed.

    Returns
    =======
    :annotator: None
    """

    path = PATH_RESULTS / f"{name}.pkl"
    if path.exists():
        df_annotations = pd.read_pickle(path)
    else:
        df_annotations = _create_df_annotations()

    for phrase in phrases:
        if phrase in df_annotations.phrase.values:
            continue
        df_phrase = annotate(df, phrase, n, info=info)
        if df_phrase.empty:
            break
        df_annotations = df_annotations.append(df_phrase, ignore_index=True)
    df_annotations.to_pickle(path)
    None


def annotate(df, phrase, n, info=None):
    df_annotations = _create_df_annotations()

    while phrase != '.':
        user = ''

        if info:
            qry = f"{info[0]} == @phrase"
            phrase_info = info[1].query(qry).to_html(index=False, notebook=True)

        regex = rf"\b{phrase}\b"
        df_q = df.loc[df.body_.str.contains(regex, regex=True)]
        if df_q.empty:
            print("phrase not found as a word unit")
            regex = phrase
            df_q = df.loc[df.body_.str.contains(regex)]
        if df_q.empty:
            return _create_df_annotations(
                [[phrase, None, None, pd.Timestamp(datetime.now())]]
                )

        results = len(df_q)
        if results < n:
            n = results

        for smp, (idx, row) in enumerate(
            df_q.reset_index().sample(n).iterrows()
            ):
            user = ''

            content  = f"<h1>ANNOTATOR</h1>"
            content += f"<h2>PHRASE: {phrase}</h2>"
            if info:
                content += f"<div class='container'>{phrase_info}</div>"
            content += (
                f"<h3>"
                f"SAMPLE: {smp + 1} of {n} | "
                f"SOURCE: {row.source} | "
                f"RESULT: {idx + 1} of {results} | "
                f"{row.id}"
                f"</h3><hr>"
                )
            content += f"<h4>{row.title}</h4><hr>"

            for p in row.body:
                if re.search(regex, p):
                    p = f"<p>{p}</p>"
                    content += re.sub(
                        regex,
                        f"<mark><b>{phrase}</b></mark>",
                        p,
                        )

            while user not in ['+', '-', '?', '.'] and not len(user) > 1:
                html = f"<style>{STYLE}</style><div class='box'>{content}</div>"
                display(HTML(html))
                user = input(
                    "Please annotate the sample above.\n"
                    "[+] if the sample matches.\n"
                    "[-] if the sample does not.\n"
                    "[?] when unsure.\n"
                    "(you can also input a new search phrase or '.' to exit)\n"
                    "(NOTE: current phrase annotations will NOT be saved)\n"
                    )
                clear_output()

            if user == '.' or len(user) > 1:
                df_annotations = pd.DataFrame()
                break

            record = [
                [phrase.strip(), row.id, user, pd.Timestamp(datetime.now())]
                ]
            df_annotations = df_annotations.append(
                _create_df_annotations(data=record), ignore_index=True
                )

        if len(user) > 1:
            phrase = user
            continue

        phrase = '.'

    return df_annotations


def _create_df_annotations(data=None):
    cols = ['phrase', 'id', 'annotation', 'timestamp']
    return pd.DataFrame(data, columns=cols)


def section_explorer(df, phrase=None):
    if not phrase:
        phrase = input("Input section to search for:\n")

    def explore(phrase):
        df_q = df.query("section.str.contains(@phrase)", engine='python')
        results = len(df_q)

        for idx, row in df_q.reset_index().iterrows():
            html  = f"<h1>SECTION EXPLORER</h1>"
            html += (
                f"<h2>"
                f"SECTION: {row.section}"
                f"</h2>"
                )
            html += (
                f"<h3>"
                f"RESULT: {idx + 1} of {results} | "
                f"SOURCE: {row.source} | "
                f"ID: {row.id}"
                "</h3><hr>"
                )
            html += f"<h4>{row.title}</h4><hr>"

            for p in row.body:
                html += f"<p>{p}</p>"

            html = f"<style>{STYLE}</style><div class='box'>{html}</div>"
            display(HTML(html))
            user = input(
                "Press <enter> to go to next record "
                "(you can also input a new section or '.' to exit)"
                )
            clear_output()
            if user == '.':
                break
            if len(user) > 0:
                return user

        if df_q.empty:
            clear_output()
            print(f"Section '{phrase}' not found.")
        return '.'

    while phrase != '.':
        phrase = explore(phrase)
    return None


def phrase_explorer(df, phrase=None, unedited=False):
    """
    Explore phrases in the data.

    Parameters
    ==========
    :param df: `DataFrame`
        df containing the LexisNexis articles.

    Optional key-word arguments
    ===========================
    :param phrase: `str`, default=None
        Search phrase. If none is passed, user will be prompted.
    :param unedited: `bool`, default=False
        If True the explorer will search 'body' instead of the deduped 'body_'.

    Returns
    =======
    :phrase explorer: None
    """

    df = df.copy()
    if unedited:
        df['body_'] = df.body
        df['body_str'] = df.body.str.join('\n')
    if not phrase:
        phrase = input("Input phrase to search for:\n")

    def explore(phrase):
        df_q = df.query("body_.str.contains(@phrase)", engine='python')
        results = len(df_q)

        for idx, row in df_q.reset_index().iterrows():
            html  = f"<h1>PHRASE EXPLORER</h1>"
            html += (
                f"<h2>"
                f"PHRASE: {phrase} | "
                f"SOURCE: {row.source} | "
                f"SECTION: {row.section}"
                f"</h2>"
                )
            html += f"<h3>RESULT: {idx + 1} of {results} | {row.id}</h3><hr>"
            html += f"<h4>{row.title}</h4><hr>"

            for p in row.body:
                if phrase in p:
                    p = f"<p>{p}</p>"
                    html += p.replace(phrase, f"<mark><b>{phrase}</b></mark>")

            html = f"<style>{STYLE}</style><div class='box'>{html}</div>"
            display(HTML(html))
            user = input(
                "Press <enter> to go to next record "
                "(you can also input a new phrase or '.' to exit)"
                )
            clear_output()
            if user == '.':
                break
            if len(user) > 0:
                return user

        if df_q.empty:
            clear_output()
            print(f"Phrase '{phrase}' not found.")
        return '.'

    while phrase != '.':
        phrase = explore(phrase)
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


def load_lexisnexis_data():
    """
    Load all lexisnexis data into a single `DataFrame`.

    Returns
    =======
    :load_lexisnexis_data: `DataFrame`
    """

    df = pd.DataFrame()
    for pkl in PATH_DATA_I.glob('*_.pkl'):
        df = df.append(pd.read_pickle(pkl))
    return df
