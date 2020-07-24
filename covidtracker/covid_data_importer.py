import pprint

from covidtracker import constants


def exec():
    california_pop = float(constants.LOCATION_POPULATION['CA'])
    map_cacount_percentofca = {}
    for loc, pop in constants.LOCATION_POPULATION.items():
        if loc.startswith("CA:"):
            map_cacount_percentofca[loc] = float(pop) / california_pop
            pass
    pprint.pprint(map_cacount_percentofca)
