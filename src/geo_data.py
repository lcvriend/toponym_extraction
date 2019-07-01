# standard library
import json
import re
import requests
from collections import namedtuple
from pathlib import Path

# third party
import pandas as pd
from bs4 import BeautifulSoup

# local
from .config import PATH_RESOURCES, PARAM
from .utils import download_from_url


# GeoNames
def load_geonames(language=PARAM.project.language):
    """
    Load data from the geonames dataset and return as `DataFrame`.

    Optional key-word arguments
    ===========================
    :param language: `str`, default=project parameter in 'parameters.ini'
    :param language: `str` or `list`,
        default=project parameter in 'parameters.ini'
        Language for returning the city names.

    Returns
    =======
    :load_geonames: `DataFrame`
    """

    path_geonames = PATH_RESOURCES / 'geonames'
    dfs = {i.stem[3:]:pd.read_pickle(i) for i in path_geonames.glob('*.pkl')}

    # process the alts dataset
    ids = set(dfs['cities'].geoname_id)
    dfs['alts'] = dfs['alts'].query("geoname_id in @ids")
    if language:
        if not isinstance(language, list):
            language=[language]
        dfs['alts']  = dfs['alts'].query("isolanguage in @language")

    dfs['featcodes']['feature_code'] = (
        dfs['featcodes'].class_code.str.split('.').str[1]
        )

    dfs['admincodes1'] = (
        dfs['admincodes1']
        .join(dfs['admincodes1'].code.str.split('.', expand=True))
        .rename(columns={
            0:'country_code',
            1:'admin_code1',
            'admin_name': 'admin_name1'}
            )
        )

    dfs['admincodes2'] = (
        dfs['admincodes2']
        .join(dfs['admincodes2'].code.str.split('.', expand=True))
        .rename(columns={
            0:'country_code',
            1:'admin_code1',
            2:'admin_code2',
            'admin_name': 'admin_name2'}
            )
        )

    df = (
        dfs['cities']
        .merge(dfs['alts'][
            ['geoname_id', 'alternate_name']
            ], on='geoname_id', how='left')
        .merge(dfs['countryinfo'][
            ['country_code', 'country']
            ], on='country_code', how='left')
        .merge(dfs['featcodes'][
            ['feature_code', 'feature_name']
            ], on='feature_code', how='left')
        .merge(dfs['admincodes1'][
            ['country_code', 'admin_code1', 'admin_name1']
            ], on=['country_code', 'admin_code1'], how='left')
        .merge(dfs['admincodes2'][
            ['country_code', 'admin_code1', 'admin_code2', 'admin_name2']
            ], on=['country_code', 'admin_code1', 'admin_code2'], how='left')
        )

    cols = [
        'geoname_id', 'name', 'ascii_name', 'alternate_name',
        'latitude', 'longitude',
        'feature_code', 'feature_name',
        'country_code', 'country',
        'admin_code1', 'admin_name1', 'admin_code2', 'admin_name2',
        'population',
        ]
    df = df[cols]
    df['alt'] = df.alternate_name.notna()
    df['alternate_name'] = df.alternate_name.fillna(df.name)

    return df


# REST_countries
def load_rest_countries(language=PARAM.project.language, alts_json=None):
    """
    Load countries from 'https://restcountries.eu' and return data as dict.

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
    :param language: `str`, default=project parameter in 'parameters.ini'
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
def load_cbs_municipalities(table_id='83859NED', alts_json=None):
    """
    Return a `DataFrame` of Dutch municipalities in the CBS dataset:
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
