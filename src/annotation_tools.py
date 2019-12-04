# standard library
import re
from collections import namedtuple
from datetime import datetime

# third party
import pandas as pd
from IPython.display import HTML, display, clear_output

# local
from src.config import PATH_RESULTS


class Annotator():
    def __init__(self):
        self.annotations = list()

    @property
    def annotated_phrases(self):
        return [annotation.phrase for annotation in self.annotations]

    def to_dataframe(self):
        return pd.DataFrame(self.annotations)

    def from_dataframe(self, df):
        self.annotations = [
            annotation for annotation in df.itertuples(
                index=False, name='Annotation')
                ]
        return None


class DocEvaluator(Annotator):
    """
    Evaluate accuracy of the ner in a spacy Doc.
    """

    Annotation = namedtuple('Annotation', ['id', 'idx', 'type', 'timestamp'])

    def __init__(self):
        super().__init__()

    def __call__(self, doc):
        lines = HTML_from_doc(doc).html_lines
        out = self._interface(doc._.id, lines)
        return out

    def _interface(self, id, lines):
        for html in lines:
            display(HTML(html))

            while True:
                idx = input('idx and [+] false positve, [-] false negative: ')
                if idx and idx != '.':
                    try:
                        annotation = idx[-1:]
                        int(idx[:-1])
                        # annotation = None
                        # while annotation not in ['+', '-']:
                        #     annotation = input(
                        #         '[+] false positve, [-] false negative: '
                        #         )
                        self.annotations.append(
                            self.Annotation(id, idx, annotation, datetime.now())
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


class HTML_from_doc():
    """
    Separate tokens, idx and ner of a spaCy `Doc` into lines and render as html.
    """

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


class PhraseAnnotator(Annotator):
    """
    Annotator
    =========
    Stores annotations as Annotation objects (`namedtuple`).
    Annotations are stored under the 'annotations' attribute.

    Attributes
    ==========
    name: Name of the class (used for display)
    data: Tuple of LexisNexis data and column name with text
    info: Tuple of info data and column name with phrase key
    n: Number of samples
    annotations: List of stored annotations
    annotated_phrases: List of annotated phrases

    Methods
    =======
    __call__: Run annotator
    to_dateframe: Return annotations as `DataFrame`
    """

    name = 'Phrase Annotator'
    Annotation = namedtuple(
        'Annotation', ['phrase', 'id', 'annotation', 'timestamp']
        )

    def __init__(self, data, info=None, n=5):
        """
        Initialize annotator.

        Parameters
        ==========
        :param data: `tuple` of `DataFrame`, `str`
            Tuple containing:
            - DataFrame with the source data
            - Name of the column containing the text
            The annotator will search the key-column for phrase matches.
            The matched records will be displayed.

        Optional key-word arguments
        ===========================
        :param info: `tuple` of `DataFrame`, `str`
            Tuple containing:
            - DataFrame with the phrase info
            - Name of the column containing the phrase key
            The annotator will search the key-column for phrase matches.
            The matched records will be displayed.
        :param n: `int`, default=5
            Number of samples to annotate per phrase.
            If n=0 no sampling will take place.
        """

        super().__init__()
        self.data = data
        self.info = info
        self.n = n

    def __call__(self, phrases):
        """
        Annotate search results.
        The annotator skips phrases that were annotated in a previous session.

        Parameters
        ==========
        :param phrases: iterable
            Iterable of phrases to annotate.

        Returns
        =======
        :__call__: None
        """

        for phrase in phrases:
            if phrase in self.annotated_phrases:
                continue
            user = self._interface(phrase)
            if user == '.':
                break
        return None

    def _interface(self, phrase):
        search = PhraseSearch(
            self.name, phrase, self.data, info=self.info, n=self.n
            )

        test = search()
        if not test:
            self.annotations.append(
                self.Annotation(phrase, None, 'n/f', datetime.now())
                )
            clear_output()
            return None

        for row, html in search():
            user = ''
            while user not in ['+', '-', '?', '.']:
                display(HTML(html))
                user = input(
                    "Please annotate the sample above:\n"
                    "[+] if the sample matches.\n"
                    "[-] if the sample does not.\n"
                    "[?] when unsure.\n"
                    "[.] to exit (current phrase will NOT be saved).\n"
                    )
                clear_output()

            if user == '.':
                return user

            self.annotations.append(
                self.Annotation(phrase, row.id, user, datetime.now())
                )
        return None


class PhraseExplorer():
    """
    Annotator
    =========
    Stores annotations as Annotation objects (`namedtuple`).
    Annotations are stored under the 'annotations' attribute.

    Attributes
    ==========
    name: Name of the class (used for display)
    data: Tuple of LexisNexis data and column name with text
    info: Tuple of info data and column name with phrase key
    n: Number of samples
    annotations: List of stored annotations
    annotated_phrases: List of annotated phrases

    Methods
    =======
    __call__: Run annotator
    to_dateframe: Return annotations as `DataFrame`
    """

    name = 'Phrase Explorer'

    def __init__(self, data, info=None):
        """
        Initialize phrase explorer.

        Parameters
        ==========
        :param data: `tuple` of `DataFrame`, `str`
            Tuple containing:
            - DataFrame with the source data
            - Name of the column containing the text
            The annotator will search the key-column for phrase matches.
            The matched records will be displayed.

        Optional key-word arguments
        ===========================
        :param info: `tuple` of `DataFrame`, `str`
            Tuple containing:
            - DataFrame with the phrase info
            - Name of the column containing the phrase key
            The annotator will search the key-column for phrase matches.
            The matched records will be displayed.
        """

        self.data = data
        self.info = info
        self.annotations = list()

    def __call__(self, phrase=None):
        """
        Annotate search results.
        The annotator skips phrases that were annotated in a previous session.

        Parameters
        ==========
        :param phrases: iterable
            Iterable of phrases to annotate.

        Returns
        =======
        :__call__: None
        """

        if not phrase:
            phrase = input("Input new search phrase\n")
            clear_output()
        while True:
            user = self._interface(phrase)
            if user is '.':
                break
        return None

    def _interface(self, phrase):
        while True:
            search = PhraseSearch(
                self.name, phrase, self.data, info=self.info, n=0
                )

            test = search()
            if not test:
                phrase = input("Input new search phrase\n")
                clear_output()
                continue

            for _, html in search():
                display(HTML(html))
                user = input(
                    "Press <enter> to go to next record\n"
                    "Input new search phrase\n"
                    "Input '.' to exit\n"
                    )
                clear_output()

                if user == '.':
                    return user
                if user:
                    phrase = user
                    break
        return None


class PhraseSearch():
    style = """
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
            text-transform: uppercase;
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

    def __init__(self, name, phrase, data, info=None, n=0):
        self.name = name
        self.phrase = phrase
        self.regex = rf"\b{phrase}\b"
        self.data = data[0]
        self.column = data[1]
        self.info = info
        self.n = n

    @property
    def results(self):
        results = self.data.loc[
            self.data[self.column].str.contains(self.regex, regex=True)
            ].reset_index()
        if results.empty:
            results = self.data.loc[
                self.data[self.column].str.contains(self.phrase)
                ].reset_index()
        return results

    @property
    def n_results(self):
        return len(self.results)

    @property
    def n_samples(self):
        if self.n_results < self.n:
            return self.n_results
        return self.n

    @property
    def phrase_info(self):
        if self.info:
            qry = f"{self.info[1]} == @self.phrase"
            phrase_info = self.info[0].query(qry)
            if not phrase_info.empty:
                return phrase_info
        return None

    def __call__(self):
        if self.n_results:
            return self._yield_results()
        else:
            print(f"Phrase '{self.phrase}' not found")
            return None

    def _yield_results(self):
        if self.n:
            for sample, (idx, row) in enumerate(
                self.results.sample(self.n_samples).iterrows()
                ):
                html = self.get_html(sample + 1, idx, row)
                yield row, html
        else:
            for idx, row in self.results.iterrows():
                html = self.get_html(None, idx, row)
                yield row, html

    def get_html(self, sample, idx, row):
        info_html = ''
        if self.phrase_info is not None:
            info_html = self.phrase_info.to_html(
                index=False,
                notebook=True
                )
            info_html = f"<div class='container'>{info_html}</div>"

        sample_html = ''
        if sample:
            sample_html += f"SAMPLE: {sample} of {self.n_samples} | "

        content = (
            f"<h1>{self.name}</h1>"
            f"<h2>PHRASE: {self.phrase}</h2>"
            f"{info_html}"
            f"<h3>"
            f"{sample_html}"
            f"SOURCE: {row.source} | "
            f"RESULT: {idx + 1} of {self.n_results} | "
            f"{row.id}"
            f"</h3><hr>"
            f"<h4>{row.title}</h4><hr>"
            )

        for p in row.body_:
            if re.search(self.regex, p):
                p = f"<p>{p}</p>"
                content += re.sub(
                    self.regex,
                    f"<mark><b>{self.phrase}</b></mark>",
                    p,
                    )
        return f"<style>{self.style}</style><div class='box'>{content}</div>"


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

            html = (
                f"<style>{PhraseSearch.style}</style>"
                f"<div class='box'>{html}</div>"
            )
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
