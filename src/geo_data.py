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
from tqdm import tqdm

# local
from .config import PATH_RESOURCES, PARAM


# GeoNames
def create_geonames_datasets(language=None):
    """
    Create datasets from the GeoNames geographical database.
    - Download resources from 'https://www.geonames.org/' if not yet present.
    - Use the alternative names from the selected languages.
    - Convert the files to DataFrames and pickle them.

    Key-word arguments
    ==================
    :param language: `str` or `list`, default=None

    Returns
    =======
    None
    """

    def load_data(url, cols):
        zip_name = Path(url).name
        zip_path = PATH_RESOURCES / zip_name
        csv_name = Path(zip_name).with_suffix('.txt').name

        return load_csv_from_zip(
            zip_path,
            csv_name,
            names=cols,
            usecols=cols,
            )

    # Download the resources if they are not yet present
    paths = dict()
    for param in PARAM._fields:
        if param.startswith('url_'):
            url = getattr(PARAM, param)
            paths[param] = path_name = PATH_RESOURCES / Path(url).name
            if not path_name.is_file():
                download_from_url(url, path_out=PATH_RESOURCES)

    # read the files
    df_countries = pd.read_csv(
        paths['url_countryinfo'],
        sep='\t',
        encoding='utf8',
        skiprows=50,
        )

    admin = ['code', 'name', 'ascii_name', 'geoname_id']
    df_admin = pd.read_csv(
        paths['url_admincodes'],
        sep='\t',
        encoding='utf8',
        names=admin,
        )

    geonames = [
        'geoname_id', 'name', 'ascii_name', 'alternate_names',
        'latitude', 'longitude',
        'feature_class', 'feature_code',
        'country_code', 'cc2',
        'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
        'population', 'elevation', 'dem', 'timezone',
        'modification_date',
        ]
    altnames = [
        'alternate_name_id',
        'geoname_id',
        'isolanguage',
        'alternate_name',
        ]
    df_geo = load_data(PARAM.url_cities, geonames)
    df_alt = load_data(PARAM.url_alts, altnames)

    # process the datasets
    df_geo = df_geo.drop('alternate_names', axis=1)
    ids = set(df_geo.geoname_id)
    df_alt = df_alt.query("geoname_id in @ids")

    language = PARAM.language
    if language:
        if not isinstance(language, list):
            language=[language]
        df_alt = df_alt.query("isolanguage in @language")

    # save the datasets to disk
    df_countries.to_pickle(PATH_RESOURCES / 'df_countries.pkl')
    df_admin.to_pickle(PATH_RESOURCES / 'df_admin.pkl')
    df_geo.to_pickle(PATH_RESOURCES / 'df_geo.pkl')
    df_alt.to_pickle(PATH_RESOURCES / 'df_alt.pkl')
    return None


def load_csv_from_zip(
    zip_path,
    csv_name,
    sep='\t',
    encoding='utf8',
    **kwargs,
    ):
    with zipfile.ZipFile(zip_path, 'r') as zip:
        with zip.open(csv_name) as f:
            return pd.read_csv(f, sep=sep, encoding=encoding, **kwargs)


def download_from_url(url, path_out=None):
    file_path = Path(url).name
    r = requests.get(url, stream=True)
    size = r.headers['Content-length']

    if not r.status_code == requests.codes.ok:
        raise requests.exceptions.HTTPError(
            f"The following url: '{url}' returned status code {r.status_code}. "
            f"Check if the provided url is still valid."
            )
    if path_out:
        file_path = path_out / file_path
    with open(file_path, 'wb') as handle:
        for data in tqdm(
            r.iter_content(),
            desc=f"{file_path.name:.<24}",
            total=int(size)):
            handle.write(data)
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
