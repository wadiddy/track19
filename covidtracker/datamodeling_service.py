from collections import defaultdict
from datetime import timedelta

import numpy


def get_normalized_data(
		locations,
		function_get_value,
		scalar,
		earliest_date,
		normalize_by_population=True,
		rolling_average_size=14
):
	dict_date_values = defaultdict(list)
	total_population = 0

	for location in locations:
		total_population += location.population
		for ldd in location.locationdaydata_set.filter(date__gte=earliest_date):
			v = function_get_value(ldd)
			if v is not None:
				dict_date_values[ldd.date].append(v)

	map_date_normalized_value = {}
	for d, values in dict_date_values.items():
		total_value = sum(values) if len(values) > 0 else 0
		normalized_value = float(scalar) * float(total_value) / (float(total_population) if normalize_by_population else 1)
		map_date_normalized_value[d] = normalized_value

	dict_date_rolling_values = defaultdict(list)
	for d in map_date_normalized_value:
		for i in range(rolling_average_size):
			# d2 = (d - timedelta(days=i))
			d2 = (d - timedelta(days=i))
			if d2 in map_date_normalized_value:
				dict_date_rolling_values[d].append(map_date_normalized_value[d2])

	map_date_smoothed_value = {}
	for d, value_list in dict_date_rolling_values.items():
		map_date_smoothed_value[d] = numpy.average(value_list) if len(value_list) >= 0 else 0

	return map_date_smoothed_value
