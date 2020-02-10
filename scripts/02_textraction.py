"""
TEXTRACTION
===========

This script parses docx files downloaded from LexisNexis per batch.
Each docx file should contain one article.
The batches are defined in 'config.ini' under [LEXISNEXIS].
The files to be processed should be stored in 'PATHS.data_raw / batch name'.

## PHASE I
The script will first create a DataFrame with the 'raw' articles.
Check the `lexisnexis_parser` module for details on how extraction is performed.
The parser should be able to parse most data, but adjustments may be needed as
it was initially built to parse Dutch newspaper articles.

Before pickling the raw data duplicates will be removed. Two records are
considered duplicates if 'title' and 'length' are equal. Only the first record
will be kept. The dataset is stored in PATHS.data_raw

## PHASE II
In the second phase the script will take the DataFrame with the raw data and do
some additional processing:
1. Where possible columns will be processed into the appropriate types.
2. Any duplicate paragraph is removed from the text body.
3. The df is standardized (only specified metadata is kept).
4. The queries defined in 'config.ini' under [LEXISNEXIS] are performed.

Finally, the processed dataset is stored in PATHS.data_int. The raw data, the duplicate paragraphs and the records that were removed through the queries are also stored in separate files starting with an underscore.
"""

print('extract lexisnexis articles from word documents')

# standard libray
import sys
import locale
import time
from collections import Counter

start = time.time()
sys.path.insert(0, '../')
locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')

# third party
import pandas as pd

# local
from src.config import LEXISNEXIS, PATHS, FILENAMES
from src.lexisnexis_parser import (
    docxs_to_df,
    split_page_from_section,
    parse_datestring,
    standardize_df,
)

line = 80 * '-'
overview = list()
for batch, name in zip(LEXISNEXIS.batches, LEXISNEXIS.batch_names):
    print(line, flush=True)
    results = dict()

    # save original parsed data
    path_raw = PATHS.data_raw / batch
    df = docxs_to_df(path_raw)
    df.to_pickle(PATHS.data_int / f'_{batch}_raw.pkl')
    results['initial'] = len(df)

    # set source to configured batch name
    df['source'] = name

    # separate section and page
    df = split_page_from_section(df)

    # extract length as integer
    df['length'] = df.length.str.split(' ').str[0].astype('int')

    # convert date strings to dates
    df['load_date'] = pd.to_datetime(df['load_date'])
    df['publication_date'] = parse_datestring(
        df['publication_date'],
        split_on=',',
        format='%d %B %Y %A',
    )

    # drop duplicate rows
    subset = ['title', 'publication_date', 'section']
    df = df.drop_duplicates(subset=subset, keep='first')
    results['deduped'] = len(df)

    # count occurrence of paragraphs
    paragraphs = Counter()
    for article in df.body.values:
        for p in article:
            paragraphs[p] += 1

    dupes = {p:paragraphs[p] for p in paragraphs if paragraphs[p] > 1}
    df_dupes = pd.DataFrame.from_dict(dupes, orient='index', columns=['count'])
    df_dupes.to_pickle(PATHS.data_int / f"_{batch}_paragraph_dupes.pkl")

    # remove duplicate (>2) paragraphs
    dupes = {p:paragraphs[p] for p in paragraphs if paragraphs[p] > 2}
    df['body_'] = df['body'].apply(lambda ps: [p for p in ps if p not in dupes])

    # add body as string
    df['body_str'] = df.body_.str.join('\n')

    # standardize
    df = standardize_df(df, batch)

    # remove items
    df_out = df.query(' and '.join(LEXISNEXIS.queries))
    df_removed = df.loc[~df.index.isin(df_out.index)]

    # save files
    df_out.to_pickle(PATHS.data_int / f'{batch}.pkl')
    df_removed.to_pickle(PATHS.data_int / f'_{batch}_removed.pkl')

    results['filtered'] = len(df_out)
    results['duped_paragraphs'] = len(df_dupes)
    s = pd.Series(results, name=name)
    print(s, flush=True)
    overview.append(s)

print(line, flush=True)
pd.concat(overview, axis=1).to_pickle(PATHS.results / FILENAMES.textraction)

end = time.time()
print(f"finished in: {round(end - start)}s")
