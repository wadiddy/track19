from collections import defaultdict
from datetime import timedelta

import numpy

from covidtracker import common

QUERYABLE_ATTR_POSITIVE_RATE = "positive_rate"
QUERYABLE_ATTR_POSITIVE = "positive"
QUERYABLE_ATTR_TOTAL_TESTS = "total_tests"
QUERYABLE_ATTR_DEATHS = "deaths"
QUERYABLE_ATTR_ON_VENTILATOR = "on_ventilator"
QUERYABLE_ATTR_IN_HOSPITAL = "in_hospital"
QUERYABLE_ATTR_IN_ICU = "in_icu"

QUERYABLE_ATTRS = [
	QUERYABLE_ATTR_POSITIVE_RATE,
	QUERYABLE_ATTR_POSITIVE,
	QUERYABLE_ATTR_TOTAL_TESTS,
	QUERYABLE_ATTR_DEATHS,
	# QUERYABLE_ATTR_ON_VENTILATOR,
	QUERYABLE_ATTR_IN_HOSPITAL,
	QUERYABLE_ATTR_IN_ICU
]

QUERYABLE_ATTR_LABELS = {
	QUERYABLE_ATTR_POSITIVE_RATE: "Positive Test Rate",
	QUERYABLE_ATTR_POSITIVE: "Tested Positive per 100k residents",
	QUERYABLE_ATTR_TOTAL_TESTS: "Tests Performed per 100k residents",
	QUERYABLE_ATTR_DEATHS: "Deaths per million residents",
	QUERYABLE_ATTR_ON_VENTILATOR: "People ventilated per 100k residents",
	QUERYABLE_ATTR_IN_HOSPITAL: "People hospitalized per 100k residents",
	QUERYABLE_ATTR_IN_ICU: "People in ICU per 100k residents",
}

MULTIPLE_LOCATION_HANDLING_SUM = "sum"
MULTIPLE_LOCATION_HANDLING_AVG = "avg"

MULTIPLE_LOCATION_HANDLING_OPTIONS = [
	MULTIPLE_LOCATION_HANDLING_SUM,
	MULTIPLE_LOCATION_HANDLING_AVG
]


def get_normalized_data(
		locations,
		function_get_value,
		scalar=1,
		earliest_date=None,
		latest_date=None,
		multiple_location_handling=None,
		normalize_by_population=True,
		rolling_average_size=14
):
	if multiple_location_handling not in MULTIPLE_LOCATION_HANDLING_OPTIONS:
		multiple_location_handling = MULTIPLE_LOCATION_HANDLING_SUM

	try:
		rolling_average_size = int(rolling_average_size)
	except:
		rolling_average_size = 14

	dict_date_values = defaultdict(list)
	dict_date_populations = defaultdict(list)
	total_population = 0

	populations_list = []
	for location in locations:
		total_population += location.population

		if earliest_date is None and latest_date is None:
			ldds = location.locationdaydata_set.all()
		elif earliest_date is not None and latest_date is not None:
			ldds = location.locationdaydata_set.filter(date__gte=earliest_date, date__lte=latest_date)
		elif earliest_date is not None and latest_date is None:
			ldds = location.locationdaydata_set.filter(date__gte=earliest_date)
		elif earliest_date is None and latest_date is not None:
			ldds = location.locationdaydata_set.filter(date__lte=latest_date)
		else:
			raise Exception("should never happen")

		for ldd in ldds:
			try:
				v = function_get_value(ldd)
			except:
				v = None

			if v is not None:
				dict_date_values[ldd.date].append(v)
				dict_date_populations[ldd.date].append(location.population)

	map_date_normalized_value = {}
	for d, values in dict_date_values.items():
		if len(values) == 0:
			total_value = 0
		elif multiple_location_handling == MULTIPLE_LOCATION_HANDLING_SUM:
			total_value = sum(values)
		elif multiple_location_handling == MULTIPLE_LOCATION_HANDLING_AVG:
			total_value = numpy.average(values, weights=dict_date_populations[d])
		else:
			raise Exception("Invalid MULTIPLE_LOCATION_HANDLING " + multiple_location_handling)

		normalized_value = float(scalar) * float(total_value) / (
			float(total_population) if normalize_by_population else 1)
		map_date_normalized_value[d] = normalized_value

	dict_date_rolling_values = defaultdict(list)
	for d in map_date_normalized_value:
		for i in range(rolling_average_size):
			d2 = (d - timedelta(days=i))
			if d2 in map_date_normalized_value:
				dict_date_rolling_values[common.get_date_key(d)].append(map_date_normalized_value[d2])

	map_date_smoothed_value = {}
	for d in sorted(dict_date_rolling_values):
		value_list = dict_date_rolling_values[d]
		map_date_smoothed_value[d] = numpy.average(value_list) if len(value_list) >= 0 else 0

	return map_date_smoothed_value
