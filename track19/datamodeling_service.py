from collections import defaultdict
from datetime import timedelta

import numpy

from track19 import common

QUERYABLE_ATTR_POSITIVE_RATE = "positive_rate"
QUERYABLE_ATTR_POSITIVE = "positive"
QUERYABLE_ATTR_TOTAL_TESTS = "total_tests"
QUERYABLE_ATTR_COVID_DEATHS = "covid_deaths"
QUERYABLE_ATTR_ON_VENTILATOR = "on_ventilator"
QUERYABLE_ATTR_IN_HOSPITAL = "in_hospital"
QUERYABLE_ATTR_IN_ICU = "in_icu"
QUERYABLE_ATTR_OTHER_DEATHS = "other_deaths"
QUERYABLE_ATTR_PERCENT_OF_POPULATION_POSITIVE = "percent_of_population_who_have_had_covid"

QUERYABLE_ATTR_OTHER_DEATH_prefix = "other_death_"
QUERYABLE_ATTR_OTHER_DEATH_ANY = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_any"
QUERYABLE_ATTR_OTHER_DEATH_HEART_DISEASE = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_heart_disease_deaths"
QUERYABLE_ATTR_OTHER_DEATH_CANCER = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_cancer_deaths"
QUERYABLE_ATTR_OTHER_DEATH_SMOKING = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_smoking_deaths"
QUERYABLE_ATTR_OTHER_DEATH_OBESITY = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_obesity_deaths"
QUERYABLE_ATTR_OTHER_DEATH_ALCOHOL = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_alcohol_deaths"
QUERYABLE_ATTR_OTHER_DEATH_TYPICAL_FLU = QUERYABLE_ATTR_OTHER_DEATH_prefix + "_typical_flu_deaths"

QUERYABLE_ATTRS = [
	QUERYABLE_ATTR_POSITIVE_RATE,
	QUERYABLE_ATTR_POSITIVE,
	QUERYABLE_ATTR_TOTAL_TESTS,
	QUERYABLE_ATTR_COVID_DEATHS,
	# QUERYABLE_ATTR_ON_VENTILATOR,
	QUERYABLE_ATTR_IN_HOSPITAL,
	QUERYABLE_ATTR_IN_ICU,
	QUERYABLE_ATTR_OTHER_DEATHS,
	QUERYABLE_ATTR_PERCENT_OF_POPULATION_POSITIVE,
]

QUERYABLE_ATTR_LABELS = {
	QUERYABLE_ATTR_POSITIVE_RATE: "Positive Test Rate",
	QUERYABLE_ATTR_POSITIVE: "Tested Positive per 100k residents",
	QUERYABLE_ATTR_PERCENT_OF_POPULATION_POSITIVE: "Percent of population who've had Covid-19",
	QUERYABLE_ATTR_TOTAL_TESTS: "Tests Performed per 100k residents",
	QUERYABLE_ATTR_COVID_DEATHS: "Covid Deaths per million residents",
	QUERYABLE_ATTR_OTHER_DEATHS: "Other Causes of Death per million residents",
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

CAUSEOFDEATH_USYEARLYDEATHS = {
	QUERYABLE_ATTR_OTHER_DEATH_ANY: 2813503,
	QUERYABLE_ATTR_OTHER_DEATH_HEART_DISEASE: 647000,
	QUERYABLE_ATTR_OTHER_DEATH_TYPICAL_FLU: 55672,
	QUERYABLE_ATTR_OTHER_DEATH_OBESITY: 300000,
	QUERYABLE_ATTR_OTHER_DEATH_CANCER: 606520,
	QUERYABLE_ATTR_OTHER_DEATH_SMOKING: 480000,
	QUERYABLE_ATTR_OTHER_DEATH_ALCOHOL: 88000,
	"Accident": 169936,
	"Lung Disease": 160201,
	"Stroke": 146383,
	"Diabetes": 83564,
	"Kidney Failure": 50633,
	"Suicide": 47143,
	"Car Accident": 38000,
}

OTHER_CAUSES_OF_DEATH_DISPLAY = [
	QUERYABLE_ATTR_OTHER_DEATH_HEART_DISEASE,
	QUERYABLE_ATTR_OTHER_DEATH_TYPICAL_FLU,
	QUERYABLE_ATTR_OTHER_DEATH_OBESITY,
	QUERYABLE_ATTR_OTHER_DEATH_CANCER,
	QUERYABLE_ATTR_OTHER_DEATH_SMOKING,
	QUERYABLE_ATTR_OTHER_DEATH_ALCOHOL
]

ATTR_SCALAR = {
	QUERYABLE_ATTR_OTHER_DEATH_HEART_DISEASE: 1000000,
	QUERYABLE_ATTR_OTHER_DEATH_TYPICAL_FLU: 1000000,
	QUERYABLE_ATTR_OTHER_DEATH_OBESITY: 1000000,
	QUERYABLE_ATTR_OTHER_DEATH_CANCER: 1000000,
	QUERYABLE_ATTR_OTHER_DEATH_SMOKING: 1000000,
	QUERYABLE_ATTR_OTHER_DEATH_ALCOHOL: 1000000,
	QUERYABLE_ATTR_POSITIVE: 100000,
	QUERYABLE_ATTR_TOTAL_TESTS: 100000,
	QUERYABLE_ATTR_COVID_DEATHS: 1000000,
	QUERYABLE_ATTR_OTHER_DEATHS: 1000000,
	QUERYABLE_ATTR_ON_VENTILATOR: 100000,
	QUERYABLE_ATTR_IN_HOSPITAL: 100000,
	QUERYABLE_ATTR_IN_ICU: 100000
}


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


def build_report_caches():
	pass


class Accumulator():
	total = 0
	def accumulate(self, v):
		self.total += v
		return self.total
