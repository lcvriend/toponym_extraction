from src.config import PARAM, PATH_RESOURCES
from src.utils import get_dataset

get_dataset(PARAM.geonames, PATH_RESOURCES / 'geonames')
