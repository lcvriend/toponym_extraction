# standard library
import zipfile

# third party
import geopandas

# local
from src.config import PATHS
from src.geo_data import load_cbs_municipalities


# create nl map on province level
map_ = geopandas.read_file(PATHS.shapes / 'nl' / 'Uitvoer_shape')
map_ = map_.query("WATER == 'NEE'")[['GM_NAAM', 'geometry']]
df = load_cbs_municipalities()

map_prov = map_.merge(
    df[['provincie', 'gemeentenaam']],
    left_on='GM_NAAM',
    right_on='gemeentenaam',
    how='left',
    )
map_prov = (
    map_prov
        .dissolve(by='provincie')
        .drop(['GM_NAAM', 'gemeentenaam'], axis=1)
    )
map_prov.to_file(PATHS.shapes / 'nl' / 'nl_cbs_provincies_2018.shp')

# unpack world map
path = PATHS.shapes / 'world/CNTR_RG_01M_2016_4326.shp.zip'
with zipfile.ZipFile(path, 'r') as zip_ref:
    zip_ref.extractall(path_out)
