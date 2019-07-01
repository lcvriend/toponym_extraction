# standard library
import json
import re
import requests
import zipfile
from collections import namedtuple
from pathlib import Path

# third party
import pandas as pd
from bs4 import BeautifulSoup

# local
from .config import PATH_RESOURCES, PARAM
from .utils import download_from_url


# GeoNames
def create_geonames_datasets(language=None):
    """
    Store data from the GeoNames geographical database as `DataFrames`.
    Instructions are stored in `parameters.ini` under section 'geonames':
    - urls of the files to be downloaded
    - how to parse the csv files
        * column names
        * skip rows if any
        * skip cols if any

    Key-word arguments
    ==================
    :param language: `str` or `list`, default=None

    Returns
    =======
    None
    """

    path_geonames = PATH_RESOURCES / 'geonames'

    # Check if resources are present
    print_title('searching for resources')
    not_downloaded = list()
    paths = dict()
    for param in PARAM.geonames._fields:
        if param.startswith('url_'):
            url = getattr(PARAM.geonames, param)
            paths[param] = path_file = path_geonames / Path(url).name
            print(f"{path_file.name:.<24}: ", end='', flush=True)
            if not path_file.is_file():
                # download_from_url(url, path_out=path_geonames)
                print('not found', flush=True)
                not_downloaded.append(url)
            else:
                # print(f"{path_name.name:.<24}: OK")
                print('OK', flush=True)
    print(flush=True)

    # Download missing resources
    if not_downloaded:
        print_title('download missing resources')
        for url in not_downloaded:
            download_from_url(url, path_out=path_geonames)
        print(flush=True)

    # Load the data into DataFrames
    print_title('loading data')
    settings = {'sep': '\t', 'encoding': 'utf8'}
    dfs = dict()
    for path in paths:
        if 'readme' in path:
            continue
        print(f"{path:.<24}: ", end='', flush=True)
        table = path[4:]
        skiprows = getattr(PARAM.geonames, f"{table}_skiprows", None)
        skipcols = getattr(PARAM.geonames, f"{table}_skipcols", [])
        names = getattr(PARAM.geonames, f"{table}_columns", None)
        if names:
            usecols = [name for name in names if name not in skipcols]
        if paths[path].suffix == '.zip':
            zip_name = Path(paths[path]).name
            zip_path = path_geonames / zip_name
            csv_name = Path(zip_name).with_suffix('.txt').name
            df = load_csv_from_zip(
                zip_path,
                csv_name,
                names=names,
                usecols=usecols,
                **settings,
                )
        else:
            df = pd.read_csv(
                paths[path],
                names=names,
                usecols=usecols,
                skiprows=skiprows,
                **settings,
                )
        dfs[table] = df
        print('OK', flush=True)
    print(flush=True)

    # process the alts dataset
    ids = set(dfs['cities'].geoname_id)
    dfs['alts'] = dfs['alts'].query("geoname_id in @ids")
    language = PARAM.project.language
    if language:
        if not isinstance(language, list):
            language=[language]
        dfs['alts']  = dfs['alts'].query("isolanguage in @language")

    # save the datasets to disk
    print_title('storing data')
    for table in dfs:
        file = f"df_{table}.pkl"
        print(f"{file:.<24}: ", end='', flush=True)
        dfs[table].to_pickle(path_geonames / file)
        print('OK', flush=True)
    return None


def load_csv_from_zip(
    zip_path,
    csv_name,
    **kwargs,
    ):
    with zipfile.ZipFile(zip_path, 'r') as zip:
        with zip.open(csv_name) as f:
            return pd.read_csv(f, **kwargs)


def print_title(x):
    print(f"{x.upper()}\n{'=' * len(x)}", flush=True)
    return None


# REST_countries
def load_rest_countries(language='en', alts_json=None):
    """
    Load countries from 'https://restcountries.eu' and store data as dict.

    Translations
    ============
    If language is not 'en' or 'us', name will be taken from 'translations'.
    Check 'https://restcountries.eu' to see which translations are available.

    Adding alternative names
    ========================
    Pass path to `alts_json` to load alternative names into the dict.
    The json file should consist of:
    - a key referring to the country record you want to add alternatives to.
    - a list as the value containing alternative spellings to the key.

    Optional key-word arguments
    ===========================
    :param language: `str`, default='en'
        Language for returning the country names.
        Options (but check 'https://restcountries.eu'):
            de - German         pt - Portuguese
            es - Spanish        nl - Dutch
            fr - French         hr - Croatian
            ja - Japanese       fa - Persian
            it - Italian

        Country names not available in the chosen translation will be ignored.
    :param alts_json: `str` or `Path` instance
        Location of the json file containing the alternative names.

    Returns
    =======
    :load_rest_countries: `dict`
    """

    r = requests.get('https://restcountries.eu/rest/v2/all')
    r.raise_for_status()  # make sure requests raises an error if it fails
    data = r.json()

    if language == 'en' or language == 'us':
        countries = {
            i['name']: i for i in data
            }
    else:
        countries = {
            i['translations'][language]: i
            for i in data if i['translations'][language] is not None
            }

    if alts_json:
        with open(alts_json, 'r', encoding='utf8') as f:
            alts = json.load(f)

        for key in alts:
            for alt in alts[key]:
                countries[alt] = countries[key]

    return countries


# CBS
def load_cbs_dutch_cities(table_id='83859NED', alts_json=None):
    """
    Return a `DataFrame` of Dutch cities in the CBS dataset:
    > 'Gebieden in Nederland 2018'

    The df contains the following info:
    - Province
    - Municipality
    - Level of urbanization
    - Number of residents
    - Address density

    Strings are stripped of leading/trailing spaces.

    Optional key-word arguments
    ===========================
    :param table_id: `str`, default='83859NED'
        CBS table id, can be updated to a newer year.

    Returns
    =======
    :load_cbs_dutch_cities: `DataFrame`
    """

    cols = {
        'Naam_33':                       'provincie',
        'Naam_2':                        'gemeentenaam',
        'Omschrijving_49':               'stedelijkheid',
        'Inwonertal_50':                 'inwonertal',
        'Omgevingsadressendichtheid_51': 'adressendichtheid',
        }

    dataset = load_cbs_dataset(table_id)
    df = pd.DataFrame.from_dict(dataset.typeddataset)
    df.update(df.select_dtypes(exclude='number').applymap(lambda x: x.strip()))
    df = df[cols].rename(columns=cols)

    if alts_json:
        with open(alts_json, 'r', encoding='utf8') as f:
            alts = json.load(f)

        for key in alts:
            for alt in alts[key]:
                df_ = df.loc[df.gemeentenaam == key].copy()
                df_.gemeentenaam = alt
                df = df.append(df_)
    return df.sort_values(['provincie', 'gemeentenaam'])


def load_cbs_dataset(table_id):
    """
    Load data sets from an opendata.cbs.nl table.
    The underlying data is stored as dictionaries in a namedtuple.

    For more information check:
    https://www.cbs.nl/nl-nl/onze-diensten/open-data/databank-cbs-statline-als-open-data
    https://www.cbs.nl/-/media/_pdf/2017/13/handleiding-cbs-open-data-services.pdf?la=nl-nl

    Available tables can be viewed here:
    https://opendata.cbs.nl/ODataCatalog/Tables
    table_id is stored in the 'd:Identifier' tag.

    Parameters
    ==========
    :param table_id: `str`
        Id for the CBS table.

    Returns
    =======
    :load_cbs: `namedtuple`
    """

    url = f"https://opendata.cbs.nl/ODataApi/OData/{table_id}"
    data_links = requests.get(url).json()['value']
    CBS_Data = namedtuple(
        'CBS_Data', [link['name'].lower() for link in data_links]
        )

    return CBS_Data(
        *[requests.get(link['url']).json()['value'] for link in data_links]
        )


# WIKI
def load_capitals_from_wiki():
    """
    Extract country-capital pairs in Dutch from the following page:

    https://nl.wikipedia.org/wiki/Lijst_van_hoofdsteden

    Returns
    =======
    :load_capitals_from_wiki: `list`
    """

    url = 'https://nl.wikipedia.org/wiki/Lijst_van_hoofdsteden'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, features='lxml')

    capitals = list()
    for span in soup.body.find_all(id=re.compile('Landen.*')):
        for el in span.parent.next_siblings:
            if el.name == 'h3':
                break
            elif el.name == 'div':
                for li in el.find_all('li'):
                    capitals.append(li.text.split(' - '))
    return capitals


def parse_wiki_place_lists(url):
    """
    Extract place names from wikipedia lists.
    Examples of pages the parser can handle:

    https://nl.wikipedia.org/wiki/Lijst_van_plaatsen_in_Engeland
    https://nl.wikipedia.org/wiki/Lijst_van_Nederlandse_plaatsen
    https://nl.wikipedia.org/wiki/Lijst_van_steden_en_dorpen_in_Friesland

    Parameters
    ==========
    :param url: `str`
        url for the wikipedia page to parse.

    Returns
    =======
    :parse_wiki_places: `list`
    """

    html = requests.get(url)
    soup = BeautifulSoup(html.text, features='lxml')
    results = list()

    headings = soup.find_all('h3')
    for h in headings:
        if h.span and len(h.span.text) < 3:
            for a in h.next_sibling.next_sibling.find_all('a'):
                if a.text.isalpha():
                    results.append(a.text)
    if not results:
        headings = soup.find_all('h2')
        for h in headings:
            if h.span and len(h.span.text) < 3:
                for a in h.next_sibling.next_sibling.find_all('a'):
                    if a.text.isalpha():
                        results.append(a.text)
    if not results:
        raise ValueError(
            f"Sorry, the url '{url}' yielded no results. "
            f"Try creating your own parser to extract "
            f"the place names from this page."
            )
    return results
