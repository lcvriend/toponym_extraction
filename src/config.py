# standard library
import configparser
from pathlib import Path
from collections import namedtuple


PATH_HOME      = Path(__file__).resolve().parent.parent
PATH_MODEL     = PATH_HOME / 'model'
PATH_DATA      = PATH_HOME / 'data'
PATH_DATA_R    = PATH_DATA / '00_raw'
PATH_DATA_I    = PATH_DATA / '01_interim'
PATH_DATA_P    = PATH_DATA / '02_processed'
PATH_RESULTS   = PATH_HOME / 'results'
PATH_RESOURCES = PATH_HOME / 'resources'


def load_ini(filename):
    # load parameters
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(filename, encoding='utf-8')
    return ini


def get_list(param):
    return param.strip('\n').split('\n')


def drop_types(name):
    strings_to_drop = ['list_', 'int_']
    for string in strings_to_drop:
        name = name.replace(string, '')
    return name


# create easy access to the parameters
ini = load_ini(PATH_HOME / 'parameters.ini')
Parameters = namedtuple('Parameters', [s for s in ini])

sections = list()
for section in ini:

    Section = namedtuple(
        section, [drop_types(p) for p in ini[section]]
        )
    values = list()
    for p in ini[section]:
        value = ini[section][p]
        if 'list_' in p:
            values.append(get_list(value))
        elif 'int_' in p:
            values.append(int(value))
        else:
            values.append(value)

    sections.append(Section._make(values))
PARAM = Parameters._make(sections)
