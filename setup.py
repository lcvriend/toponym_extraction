# standard library
import zipfile
from pathlib import Path

# local
from src.config import PARAM, PATH_RESOURCES
from src.utils import get_dataset, download_from_url

get_dataset(PARAM.geonames, PATH_RESOURCES / 'geonames')

for field, url in zip(PARAM.mapping._fields, PARAM.mapping):
    suffix = Path(url).suffix
    path_out = PATH_RESOURCES / 'shapefiles' / field
    filename = f"{field}.{suffix}"

    download_from_url(
        url,
        filename=filename,
        path_out=path_out
        )

    if suffix == 'zip':
        with zipfile.ZipFile(path_out / filename, 'r') as zip_ref:
            zip_ref.extractall(path_out)
