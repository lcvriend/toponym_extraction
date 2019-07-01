from src.config import PARAM, PATH_RESOURCES
from src.utils import get_datasets

get_datasets(PARAM.geonames, PATH_RESOURCES / 'geonames')
