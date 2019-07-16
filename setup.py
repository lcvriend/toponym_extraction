from src.config import PARAM, PATH_RESOURCES
from src.utils import get_dataset, download_from_url

get_dataset(PARAM.geonames, PATH_RESOURCES / 'geonames')

for field, url in zip(PARAM.mapping._fields, PARAM.mapping):
    download_from_url(url, path_out=PATH_RESOURCES / 'shapefiles' / field)
