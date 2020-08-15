from collections import defaultdict
from datetime import timedelta

import numpy

from track19 import common, models, constants

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

QUERYABLE_ATTR_RELATED_ATTRS = {
	QUERYABLE_ATTR_POSITIVE_RATE: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_POSITIVE: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_PERCENT_OF_POPULATION_POSITIVE: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_TOTAL_TESTS: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_COVID_DEATHS: [QUERYABLE_ATTR_OTHER_DEATHS],
	QUERYABLE_ATTR_OTHER_DEATHS: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_ON_VENTILATOR: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_IN_HOSPITAL: [QUERYABLE_ATTR_COVID_DEATHS],
	QUERYABLE_ATTR_IN_ICU: [QUERYABLE_ATTR_COVID_DEATHS],
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


def build_attr_data(
		attr_token,
		attr,
		locations,
		earliest_date,
		latest_date,
		rolling_average_size
):
	attr_label = attr.replace("_", " ").title().replace("Other Death", "").strip()
	scalar = common.get(ATTR_SCALAR, attr, 1)

	if attr.startswith(QUERYABLE_ATTR_OTHER_DEATH_prefix):
		function_get_value = lambda ldd: float(
			CAUSEOFDEATH_USYEARLYDEATHS[attr]) / (365.0 * float(constants.USA_POPULATION))
		normalize_by_population = False
		multiple_location_handling = MULTIPLE_LOCATION_HANDLING_AVG
	elif attr == QUERYABLE_ATTR_PERCENT_OF_POPULATION_POSITIVE:
		scalar = 100
		normalize_by_population = True
		multiple_location_handling = MULTIPLE_LOCATION_HANDLING_AVG
		accumulator = Accumulator()
		function_get_value = lambda ldd: accumulator.accumulate(ldd.positive)
	elif attr == QUERYABLE_ATTR_POSITIVE_RATE:
		scalar = 100
		normalize_by_population = False
		multiple_location_handling = MULTIPLE_LOCATION_HANDLING_AVG
		function_get_value = lambda ldd: min(1, float(ldd.positive) / float(ldd.total_tests))
	else:
		normalize_by_population = True
		multiple_location_handling = MULTIPLE_LOCATION_HANDLING_SUM
		if attr_token == QUERYABLE_ATTR_COVID_DEATHS:
			query_attr = "deaths"
		else:
			query_attr = attr
		function_get_value = lambda ldd: float(getattr(ldd, query_attr, 0))
	attr_data = get_normalized_data(
		locations,
		function_get_value,
		scalar,
		earliest_date,
		latest_date,
		multiple_location_handling=multiple_location_handling,
		rolling_average_size=rolling_average_size,
		normalize_by_population=normalize_by_population
	)
	return attr_data, attr_label, scalar


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
	if not isinstance(locations, list):
		locations = [locations]

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
	i = 0
	for l in models.Location.objects.all():
		for attr in QUERYABLE_ATTRS:
			i = i + 1

			map_date_value = build_attr_data(
				attr,
				attr,
				[l],
				None,
				None,
				14
			)[0]

			if len(map_date_value) == 0:
				continue

			map_value_date = common.flip_map(map_date_value)
			peak_value = max(map_value_date)
			peak_value_date = map_value_date[peak_value]

			latest_date = common.parse_date(max(map_date_value))
			two_weeks_ago = latest_date - timedelta(days=14)
			month_ago = latest_date - timedelta(days=30)

			dk_latest_date = common.get_date_key(latest_date)
			dk_two_weeks_ago = common.get_date_key(two_weeks_ago)
			dk_month_ago = common.get_date_key(month_ago)

			v_latest_date = common.get(map_date_value, dk_latest_date, 0)
			v_two_weeks_ago = common.get(map_date_value, dk_two_weeks_ago, 0)
			v_month_ago = common.get(map_date_value, dk_month_ago, 0)

			two_week_delta = (v_latest_date - v_two_weeks_ago) / v_two_weeks_ago if v_two_weeks_ago > 0 else 0
			month_delta = (v_latest_date - v_month_ago) / v_month_ago if v_month_ago > 0 else 0

			k = "___".join([l.token, attr])

			try:
				rollup_data = models.RollupLocationAttrRecentDelta.objects.get(k=k)
				rollup_data.peak_date = peak_value_date
				rollup_data.peak_value = peak_value
				rollup_data.latest_date = latest_date
				rollup_data.two_weeks_ago_date = two_weeks_ago
				rollup_data.month_ago_date = month_ago
				rollup_data.latest_value = v_latest_date
				rollup_data.two_weeks_ago_value = v_two_weeks_ago
				rollup_data.month_ago_value = v_month_ago
				rollup_data.two_week_delta = two_week_delta
				rollup_data.month_delta = month_delta
				rollup_data.save()
			except models.RollupLocationAttrRecentDelta.DoesNotExist:
				models.RollupLocationAttrRecentDelta(
					k=k,
					token=l.token,
					attr=attr,
					peak_date=peak_value_date,
					peak_value=peak_value,
					latest_date=latest_date,
					two_weeks_ago_date=two_weeks_ago,
					month_ago_date=month_ago,
					latest_value=v_latest_date,
					two_weeks_ago_value=v_two_weeks_ago,
					month_ago_value=v_month_ago,
					two_week_delta=two_week_delta,
					month_delta=month_delta
				).save()


class Accumulator():
	total = 0

	def accumulate(self, v):
		self.total += v
		return self.total
