# standard library
import zipfile
from pathlib import Path
from unicodedata import normalize

# third party
import pandas as pd
import xml.etree.ElementTree as ET


URI = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
BASE_URL = 'https://advance.lexis.com/api/document'


def docxs_to_df(path):
    """
    Parse all docx files within a path location with `docx_to_dict`.
    Store the results in a DataFrame.

    The parser assumes that each article is stored as a separate `docx` file.

    Parameters
    ==========
    :param path: `str` or `Path` instance
        Path location to the files to be converted.

    Returns
    =======
    :docx_to_df: `DataFrame`
    """

    if isinstance(path, str):
        path = Path(path)

    articles = path.glob('*.docx')
    pre_df = list()
    for a in articles:
        row = docx_to_dict(a)
        pre_df.append(row)

    df = pd.DataFrame(pre_df)
    df.columns = [format_colname(column) for column in df.columns]

    return df


def docx_to_dict(filename):
    """
    Convert LexisNexis docx to dictionary:

    1. From the filename:
        - Store directory of filename as 'folder'.
        - Store filename as 'filename'.
    1. Unzip the docx.
    2. Read `document.xml` and `document.xml.rels`.
    3. From the xml:
        - Store first paragraph as 'title'.
        - Store second paragraph as 'source'.
        - Store third paragraph as 'publication_date'.
        - Store fourth paragraph as 'copyright'.
        - Convert any paragraphs that contain ':' to key, value pair.
        - Add paragraphs between 'Body' and 'Classification' to 'body' as list.
        - Find LexisNexis url in rels and store it as 'url'.

    The date formats in LexisNexis may vary from source to source.
    Therefore the parsing of dates should be done separately by you.

    Parameters
    ==========
    :param filename: `Path` or `str`
        Location of the `docx` file to convert.

    Returns
    =======
    :docx_to_dict: `dict`.
    """

    with zipfile.ZipFile(filename, 'r') as docx:
        with docx.open('word/document.xml') as xml:
            xml_doc = xml.read()
        with docx.open('word/_rels/document.xml.rels') as xml:
            xml_rel = xml.read()

    doc = dict()
    doc['folder'] = str(filename.parent)
    doc['filename'] = filename.name
    doc['url'] = get_url(xml_rel)
    doc['body'] = list()

    in_body = False
    document = xml_to_text(xml_doc)
    for idx, paragraph in enumerate(document):

        if idx < 4:
            if idx == 0:
                doc['title'] = paragraph
                continue
            if idx == 1:
                doc['source'] = paragraph
                continue
            if idx == 2:
                doc['publication_date'] = paragraph
                continue
            if idx == 3:
                doc['copyright'] = paragraph
                continue

        if paragraph == 'Classification':
            in_body = False
            continue
        elif in_body and paragraph:
            doc['body'].append(paragraph)
            continue
        else:
            if ':' in paragraph:
                key_val = paragraph.split(':', maxsplit=1)
                doc[key_val[0]] = key_val[1].strip()
                continue
        if paragraph == 'Body':
            in_body = True
    return doc


def get_url(xml, base=BASE_URL):
    """
    Search for base url in xml and if found return it, else return `None`.

    Paramters
    =========
    :param xml: `str`

    Optional key-word arguments
    ===========================
    :param base: `str`
        Common part of the url to search for.
        I.e. LexisNexis links to its articles using:
            'https://advance.lexis.com/api/document'

    Return
    ======
    :get_url: `str`
    """

    root = ET.fromstring(xml)
    for child in root.iter():
        if 'Target' in child.attrib:
            if base in child.attrib['Target']:
                return child.attrib['Target']
    return None


def xml_to_text(xml, uri=URI):
    """
    Extract text within the xml of a docx file into a list of strings.
    The list represents the separate paragraphs within the document.

    Paramters
    =========
    :param xml: `str`

    Optional key-word arguments
    ===========================
    :param uri: `str`
        Common part of the docx xml tags.

    Return
    ======
    :get_url: `str`
    """

    root = ET.fromstring(xml)
    document = list()
    text = u''
    for paragraph in root.iter(f'{{{uri}}}p'):
        for run in paragraph.iter(f'{{{uri}}}t'):
            if run.text:
                text += run.text
        text = text.strip()
        text = normalize('NFKD', text)
        if text:
            document.append(text)
            text = u''
    return document


def standardize_df(
    df,
    batch,
    cols=None,
    extend=None,
    sort_on=['publication_date', 'page']
    ):
    """
    Standardize the format of the `DataFrame` containing the LexisNexis data:
    - Keep only the specified columns in the specified order.
    - Sort the df according on the specified columns.
    - Add an identifier to each record.

    ## Purpose
    LexisNexis metadata is not uniform for all sources.
    A standardized data format may be convenient for further analysis.
    This function will set the df to a specified format.

    ## Format
    This function creates a df containing the following columns:

        01. id                      09. section
        02. source                  10. page
        03. title                   11. length
        04. body (as list)          12. byline
        05. body (filtered)         13. copyright
        06. body (as string)        14. folder
        07. publication date        15. filename
        08. load date               16. url

    Any columns missing in the input, will be added to the ouptut (`nan`).
    This format may be replaced completely (by passing `cols`).
    Or alternatively extended (by passing `extend`).

    Arguments
    =========
    :param df: `DataFrame`
        Df created by the LexisNexis parser.
    :param batch: `str`
        Batch name used for creating the record id.

    Optional key-word arguments
    ===========================
    :param cols: `list`, default None
        Alternative list of columns to standardize to.
    :param extend: `list`, default None
        Additional columns to add to the standardized output.
    :param sort_on: `str` or `list`, default ['publication_date', 'page']


    Returns
    =======
    :standardize_df: `DataFrame`
    """

    if not cols:
        cols = [
            'id', 'source', 'title',
            'body', 'body_', 'body_str',
            'publication_date', 'load_date',
            'section', 'page', 'length',
            'byline', 'copyright',
            'folder', 'filename', 'url',
            ]
    if extend:
        cols.extend(extend)
    if not 'id' in cols:
        cols.insert(0, 'id')

    df = df.sort_values(sort_on).reset_index(drop=True)

    # prepare output df with expected columns
    # even if columns are missing in the input df
    # they will be in the output df
    df_out = pd.DataFrame(columns=cols, index=df.index)
    date_cols = [col for col in df_out.columns if 'date' in col]
    if date_cols:
        df_out[date_cols] = df_out[date_cols].astype('datetime64[ns]')

    # add id
    df['id'] = df.apply(
        lambda row: f"{codify_batch(batch)}_{row.name:04d}", axis=1
        )

    df_out.update(df)

    # set columns to their original dtypes
    dtypes = df.dtypes.to_dict()
    df_out = df_out.astype(
        {col:dtypes[col] for col in dtypes if col in df_out.columns}
        )
    return df_out


def parse_datestring(
    s,
    format=None,
    split_on=None,
    nsplits=1,
    ):
    """
    Convert a `Series` of dates as strings into a `Series` of dates.

    The publication date in LexisNexis documents sometimes has a redundant tail.
    Use 'split_on' to split the string from the right to remove it.
    If necessary set 'nsplits' to the number of splits necessary.

    Arguments
    =========
    :param s: `Series`

    Optional key-word arguments
    ===========================
    :param format: `str`, default None
        strftime to parse time, eg '%d/%m/%Y'.
    :param split_on: `str`, default None
        String to split on. If None do not split.
    :param nsplits: `int`, default 1
        Number of splits to make from right to left.

    Returns
    =======
    :parse_datestring: `Series`
    """

    if split_on:
        s = s.str.rsplit(split_on, n=nsplits).str[0]
    s = pd.to_datetime(s, format=format)
    return s


def split_page_from_section(df, split_on=';'):
    """
    Separate section and page number in the LexisNexis 'section' field.
    Assumes something like the following format:

        'SECTION; [SUB-SECTION;] PAGE NO'

    Splits string once from the right.
    String to split on can be modified via 'spit_on'.

    Parameters
    ==========
    :param df: `DataFrame`

    Optional key-word arguments
    ===========================
    :param split_on: `str`, default None
        String to split on. If None do not split.

    Returns
    =======
    :split_section_page: `DataFrame`
    """

    colnames = {0: 'section', 1: 'page'}
    section_page = df.section.str.rsplit(
        split_on, n=1, expand=True
        ).rename(columns=colnames)
    df = df.drop('section', axis=1).join(section_page)
    df['section'] = df['section'].str.lower().str.replace('| ', '', regex=False)
    df['page'] = df['page'].str.split('. ').str[1].astype('int')
    return df


def format_colname(colname):
    colname = colname.lower()
    colname = colname.replace('-', '_')
    colname = colname.replace(' ', '_')
    return colname


def codify_batch(batch):
    batch = batch.lower().replace(' ', '')
    return f'{batch[:5]}'.ljust(5, '_')
