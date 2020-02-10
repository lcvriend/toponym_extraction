"""
GATHER RESOURCES
================

This script will download the following resources:
- The geonames datasets from 'http://www.geonames.org/'
- The shapefiles from the urls defined in 'config.ini'

Some tuning is possible by editing 'config.ini'.
It may be necessary to gather the resources manually depending on your needs.
"""


# standard library
import os
import zipfile
from pathlib import Path

# local
from src.config import PATHS, GEONAMES, MAPPING
from src.utils import get_dataset, download_from_url


# change the working directory
os.chdir('../')

# download the place name data files
get_dataset(GEONAMES, PATHS.resources / 'geonames')

# download shapefiles
for field, url in zip(MAPPING._fields, MAPPING):
    suffix = Path(url).suffix
    path_out = PATHS.resources / 'shapefiles' / field
    filename = f"{field}{suffix}"

    if not (path_out / filename).exists():
        download_from_url(url, filename=filename, path_out=path_out)

    if suffix == '.zip':
        with zipfile.ZipFile(path_out / filename, 'r') as zip_ref:
            zip_ref.extractall(path_out)
