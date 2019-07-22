# standard library
import zipfile
from pathlib import Path

# third party
import geopandas

# local
from src.config import PARAM, PATH_RESOURCES, PATH_SHAPES, PATH_RESULTS
from src.utils import get_dataset, download_from_url
from src.geo_data import load_cbs_municipalities

get_dataset(PARAM.geonames, PATH_RESOURCES / 'geonames')
print()

for field, url in zip(PARAM.mapping._fields, PARAM.mapping):
    suffix = Path(url).suffix
    path_out = PATH_RESOURCES / 'shapefiles' / field
    filename = f"{field}{suffix}"

    if not (path_out / filename).exists():
        download_from_url(
            url,
            filename=filename,
            path_out=path_out
            )

    if suffix == '.zip':
        with zipfile.ZipFile(path_out / filename, 'r') as zip_ref:
            zip_ref.extractall(path_out)

# create nl map on province level
map_ = geopandas.read_file(PATH_SHAPES / 'nl' / 'Uitvoer_shape')
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
map_prov.to_file(PATH_SHAPES / 'nl' / 'nl_cbs_provincies_2018.shp')

# unpack world map
with zipfile.ZipFile(
    PATH_SHAPES / 'world/CNTR_RG_01M_2016_4326.shp.zip', 'r'
    ) as zip_ref:
    zip_ref.extractall(path_out)


print('~ F I N I S H E D ~')
