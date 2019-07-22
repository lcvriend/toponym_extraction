#standard library
import requests
import zipfile
from pathlib import Path

# third party
import pandas as pd
from tqdm import tqdm

# local
from src.config import PARAM


def get_dataset(parameters, path_out):
    """
    Get data as (zipped) csv's online and store as `DataFrames`.
    Instructions are passed through the 'parameters' argument.
    It is a namedtuple containing information on:
    - the urls of the files to be downloaded
    - how to parse the csv files
        * column names
        * skip rows if any
        * skip cols if any

    Arguments
    ==================
    :param parameters: `namedtuple`
        `namedtuple` containing the following attributes:

        tuple                 | value
        ===================== | =====
        url_[table name]      | url
        [table name]_columns  | list of column names
        [table name]_skipcols | list of column names to skip
        [table name]_skiprows | number of rows to skip (integer)

    :parm path: `Path` or `str`
        Location where the output should be stored.

    Returns
    =======
    None
    """

    if isinstance(path_out, str):
        path_out = Path(path_out)

    # Check if resources are present
    print_title('searching for resources')
    not_downloaded = list()
    paths = dict()
    for param in parameters._fields:
        if param.startswith('url_'):
            url = getattr(parameters, param)
            paths[param] = path_file = path_out / Path(url).name
            print(f"{path_file.name:.<24}: ", end='', flush=True)
            if not path_file.is_file():
                print('not found', flush=True)
                not_downloaded.append(url)
            else:
                print('OK', flush=True)
    print(flush=True)

    # Download missing resources
    if not_downloaded:
        print_title('download missing resources')
        for url in not_downloaded:
            download_from_url(url, path_out=path_out)
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
        skiprows = getattr(parameters, f"{table}_skiprows", None)
        skipcols = getattr(parameters, f"{table}_skipcols", [])
        names = getattr(parameters, f"{table}_columns", None)
        if names:
            usecols = [name for name in names if name not in skipcols]
        if paths[path].suffix == '.zip':
            zip_name = Path(paths[path]).name
            zip_path = path_out / zip_name
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

    # save the datasets to disk
    print_title('storing data')
    for table in dfs:
        file = f"df_{table}.pkl"
        print(f"{file:.<24}: ", end='', flush=True)
        dfs[table].to_pickle(path_out / file)
        print('OK', flush=True)
    return None


def download_from_url(url, filename=None, path_out=None):
    headers = {'User-Agent': PARAM.project.user_agent}
    if not filename:
        filename = Path(url).name
    r = requests.get(url, headers=headers, stream=True)
    size = r.headers['Content-length']

    if not r.status_code == requests.codes.ok:
        raise requests.exceptions.HTTPError(
            f"The following url: '{url}' returned status code {r.status_code}. "
            f"Check if the provided url is still valid."
            )
    if path_out:
        path_out.mkdir(parents=True, exist_ok=True)
        filename = path_out / filename
    with open(filename, 'wb') as handle:
        iter_bytes = tqdm(
            r.iter_content(),
            desc=f"{filename.name:.<24}",
            total=int(size),
            ncols=200,
            )
        for data in iter_bytes:
            handle.write(data)
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
