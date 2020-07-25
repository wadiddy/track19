import json

import dateparser
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from . import models, datamodeling_service, common, constants
from .common import MyJSONEncoder


def index_page(request):
	page_model = {
		"locations": request.GET.getlist("loc"),
		"attributes": request.GET.getlist("attr"),
		"rolling_average_size": common.get(request.GET, 'ravg'),
		"earliest_date": common.get_date(request.GET, 'date_from'),
		"latest_date": common.get_date(request.GET, 'date_to'),
	}

	chart_data = build_chart_data(request)
	return render(request, "index.html", context={
		"chart_data": chart_data,
		"chart_data_json": json.dumps(chart_data),
		"page_model": json.dumps(page_model),
		"last_updated": models.LocationDayData.objects.all().order_by("-date")[0].date,
		"avail_attributes": get_attr_labelvalues(),
		"avail_locations": get_locations()
	})


@cache_page(60 * 5)
def api_vi_attributes(request):
	return send_api_response(get_attr_labelvalues())


@cache_page(60 * 5)
def api_vi_locations(request):
	return send_api_response(get_locations())



@cache_page(60 * 5)
def api_vi_fetch(request):
	return send_api_response(build_chart_data(request))


def build_chart_data(request):
	rolling_average_size = common.get(request.GET, 'ravg', 14)
	earliest_date = common.get_date(request.GET, 'date_from', '2020-05-01')
	latest_date = common.get_date(request.GET, 'date_to')
	series_list = []
	attr_list = request.GET.getlist("attr")
	if len(attr_list) == 0:
		attr_list = [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE]
	loc_tokens_list = request.GET.getlist("loc")
	if len(loc_tokens_list) == 0:
		loc_tokens_list = ["USA"]
	for loc_tokens in loc_tokens_list:
		location_tokens = []
		location_names = []
		for lt in loc_tokens.split("~"):
			try:
				location_group = models.LocationGroup.objects.get(token=lt)
				location_names.append(location_group.name)
				location_tokens += [lgl.location_id for lgl in location_group.locationgrouplocation_set.all()]
			except:
				location_tokens.append(lt)
				location_names.append(lt)

		print("location_tokens", location_tokens)
		locations = list(models.Location.objects.filter(token__in=location_tokens))
		total_population = sum([l.population for l in locations]) if len(locations) > 0 else 0
		for attr in attr_list:
			if attr not in datamodeling_service.QUERYABLE_ATTRS:
				continue

			attr_label = attr.replace("_", " ").title()
			scalar = common.get(constants.ATTR_SCALAR, attr, 1)
			if scalar > 1:
				if scalar == 100000:
					scalar_label = "100k"
				elif scalar == 1000000:
					scalar_label = "million people"
				else:
					scalar_label = str(scalar)

				series_name = "%s per %s in %s" % (attr_label, scalar_label, " & ".join(location_names))
			else:
				series_name = "%s in %s" % (attr_label, " & ".join(location_names))

			if attr == datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE:
				scalar = 100
				normalize_by_population = False
				multiple_location_handling = datamodeling_service.MULTIPLE_LOCATION_HANDLING_AVG
				function_get_value = lambda ldd: float(ldd.positive) / float(ldd.total_tests)
			else:
				attr_label = attr_label + "s"
				normalize_by_population = True
				multiple_location_handling = datamodeling_service.MULTIPLE_LOCATION_HANDLING_SUM
				function_get_value = lambda ldd: float(getattr(ldd, attr, 0))

			series_list.append(
				{
					"type": "series",
					"name": series_name,
					"location": loc_tokens,
					"population": total_population,
					"attr": attr,
					"rolling_average_size": rolling_average_size,
					"data": datamodeling_service.get_normalized_data(
						locations,
						function_get_value,
						scalar,
						earliest_date,
						latest_date,
						multiple_location_handling=multiple_location_handling,
						rolling_average_size=rolling_average_size,
						normalize_by_population=normalize_by_population
					)
				}
			)
	return series_list


def send_api_response(payload):
	return JsonResponse({
		'success': True,
		'api_version': 1,
		'payload': payload,
	}, encoder=MyJSONEncoder)


def get_locations():
	locations = []
	for lg in models.LocationGroup.objects.all():
		group_population = 0
		for l in models.Location.objects.filter(pk__in=[lgl.location_id for lgl in lg.locationgrouplocation_set.all()]):
			group_population += l.population
		locations.append({
			"type": "location_group",
			"token": lg.token,
			"name": lg.name,
			"population": group_population
		})

	for l in models.Location.objects.all():
		locations.append({
			"type": "location",
			"token": l.token,
			"name": l.token,
			"population": l.population
		})

	return locations

def get_attr_labelvalues():
	return [
		{"label": datamodeling_service.QUERYABLE_ATTR_LABELS[a], "value": a}
		for a in datamodeling_service.QUERYABLE_ATTRS
	]


