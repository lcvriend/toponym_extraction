# standard library
import re
from collections import namedtuple
from datetime import datetime

# third party
import pandas as pd
from IPython.display import HTML, display, clear_output

# local
from src.config import PATH_RESULTS


class Evaluator():
    Annotation = namedtuple('Annotation', ['id', 'idx', 'type'])

    def __init__(self):
        self.annotations = list()

    def __call__(self, doc):
        lines = HTML_from_doc(doc).html_lines
        out = self.interface(doc._.id, lines)
        return out

    def interface(self, id, lines):
        for html in lines:
            display(HTML(html))

            while True:
                idx = input('idx: ')
                if idx and idx != '.':
                    try:
                        int(idx)
                        annotation = None
                        while annotation not in ['+', '-']:
                            annotation = input(
                                '[+] false positve, [-] false negative: '
                                )
                        self.annotations.append(
                            self.Annotation(id, idx, annotation)
                            )
                    except ValueError:
                        pass
                    clear_output()
                    display(HTML(html))
                else:
                    break

            clear_output()
            if idx == '.':
                return '.'
        return None

    def to_dataframe(self):
        return pd.DataFrame(self.annotations)


class HTML_from_doc():
    Token = namedtuple('Token', ['text', 'idx', 'ent'])
    class_name = 'a'
    style = (
        "<style>"
            "* {"
                "box-sizing: border-box;"
            "}"
            f"table.{class_name},"
            f"th.{class_name},"
            f"td.{class_name} {{"
                "border-right: 1px solid black;"
            "}"
            f"table.{class_name} {{"
                "margin-bottom: 24px !important;"
            "}"
        "</style>"
        )

    def __init__(self, doc, char_limit=80):
        self.doc = doc
        self.char_limit = char_limit
        self.lines = self.doc_to_lines(doc, char_limit)
        self.max_lines = max(self.lines)
        self.html_lines = self.lines_to_html_lines(self.lines)

    def lines_to_html_lines(self, lines):
        def cell(x):
            return f"<td class='{self.class_name}'>{x}</td>"

        def concat(lst):
            return ''.join(lst)

        html_lines = list()
        for line in lines:
            indeces = [cell(token.idx) for token in lines[line]]
            ents = [cell(token.ent) for token in lines[line]]
            texts = [
                cell(token.text) if token.ent == ''
                else cell('<mark>' + token.text + '</mark>')
                for token in lines[line]
                ]

            html = (
                f"{self.style}"
                f"<h3>{self.doc._.id}</h3>"
                f"<table class='{self.class_name}'>"
                    "<tr>"
                        f"<th rowspan='3' class='{self.class_name}'>"
                        f"{line:02} / {self.max_lines}</th>"
                        f"{concat(ents)}"
                    "</tr>"
                    "<tr>"
                        f"{concat(texts)}"
                    "</tr>"
                    "<tr>"
                        f"{concat(indeces)}"
                    "</tr>"
                "</table>"
            )
            html_lines.append(html)
        return html_lines

    @classmethod
    def doc_to_lines(cls, doc, char_limit):
        lines = dict()
        line = list()
        line_length = 0
        line_idx = 0

        for token in doc:
            text = token.text if token.text != '\n' else '^'
            line_length += len(text)
            line.append(cls.Token(text, token.i, token.ent_type_))

            if line_length > char_limit:
                line_length = 0
                lines[line_idx] = line
                line_idx += 1
                line = list()
        return lines


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
    .container {
        overflow: scroll;
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
        df_q = df.loc[df.body_str.str.contains(regex, regex=True)]
        if df_q.empty:
            print("phrase not found as a word unit")
            regex = phrase
            df_q = df.loc[df.body_str.str.contains(regex)]
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

            for p in row.body_:
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
        df_q = df.query("body_str.str.contains(@phrase)", engine='python')
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

            for p in row.body_:
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
