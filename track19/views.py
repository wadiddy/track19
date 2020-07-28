import json
import pprint

import dateparser
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from . import models, datamodeling_service, common, constants
from .common import MyJSONEncoder


def index_page(request):
	page_model = build_page_model(request, default_chart={
		"name": None,
		"locations": ["USA"],
		"attributes": [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE]
	})
	chart_data = build_chart_data(page_model)

	ctx = {
		"chart_data": chart_data,
		"chart_data_json": json.dumps(chart_data),
		"page_model": page_model,
		"page_model_json": json.dumps(page_model),
		"last_updated": models.LocationDayData.objects.all().order_by("-date")[0].date,
		"avail_attributes": get_attr_labelvalues(),
		"avail_locations": get_locations()
	}
	return render(request, "index.html", context=ctx)

def about(request):
	page_model = build_page_model(request, default_chart={
		"name": None,
		"locations": ["USA"],
		"attributes": [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE]
	})
	chart_data = build_chart_data(page_model)

	ctx = {
		"chart_data": chart_data,
		"chart_data_json": json.dumps(chart_data),
		"page_model": page_model,
		"page_model_json": json.dumps(page_model),
		"last_updated": models.LocationDayData.objects.all().order_by("-date")[0].date,
		"avail_attributes": get_attr_labelvalues(),
		"avail_locations": get_locations()
	}
	return render(request, "about.html", context=ctx)

def build_page_model(request, default_chart=None):
	page_model = {
		"rolling_average_size": common.get_int(request.GET, 'ravg', '14'),
		"earliest_date": common.get_date_key(common.get_date(request.GET, 'date_from', '2020-05-01')),
		"latest_date": common.get_date_key(common.get_date(request.GET, 'date_to')),
		"charts": []
	}

	all_location_tokens = [l['token'] for l in get_locations()]
	for i in range(10):
		suffix = "" if i == 0 else str(i)
		locations = [l for l in request.GET.getlist("loc" + suffix) if l in all_location_tokens]
		attributes = [a for a in request.GET.getlist("attr" + suffix) if a in datamodeling_service.QUERYABLE_ATTRS]
		if len(locations) > 0 and len(attributes) > 0:
			page_model['charts'].append({
				"name": common.get(request.GET, "name" + suffix),
				"locations": locations,
				"attributes": attributes,
			})

	if len(page_model['charts']) == 0 and default_chart is not None:
		page_model['charts'].append(default_chart)

	return page_model


@cache_page(60 * 5)
def api_vi_attributes(request):
	return send_api_response(get_attr_labelvalues())


@cache_page(60 * 5)
def api_vi_locations(request):
	return send_api_response(get_locations())


@cache_page(60 * 5)
def api_vi_fetch(request):
	return send_api_response(
		build_chart_data(
			build_page_model(request)
		)
	)


def build_chart_data(page_model):
	rolling_average_size = page_model['rolling_average_size']
	earliest_date = common.parse_date(page_model['earliest_date'])
	latest_date = common.parse_date(page_model['latest_date'])

	chart_list = []
	for chart_meta in page_model['charts']:
		all_location_names = []
		chart_data = {
			"series_list": []
		}
		series_list = chart_data["series_list"]
		chart_list.append(chart_data)

		for loc_tokens in chart_meta['locations']:
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

			all_location_names += location_names
			locations = list(models.Location.objects.filter(token__in=location_tokens))
			total_population = sum([l.population for l in locations]) if len(locations) > 0 else 0

			for attr_token in chart_meta['attributes']:
				if attr_token == datamodeling_service.QUERYABLE_ATTR_OTHER_DEATHS:
					attrs = datamodeling_service.OTHER_CAUSES_OF_DEATH_DISPLAY
				else:
					attrs = [attr_token]

				for attr in attrs:
					attr_label = attr.replace("_", " ").title().replace("Other Death", "").strip()
					scalar = common.get(datamodeling_service.ATTR_SCALAR, attr, 1)

					if scalar > 1:
						if scalar == 100000:
							scalar_label = "100k"
						elif scalar == 1000000:
							scalar_label = "million people"
						else:
							scalar_label = str(scalar)

						if len(location_names) == 1 and attr_token == datamodeling_service.QUERYABLE_ATTR_OTHER_DEATHS:
							series_name = "%s per %s" % (attr_label, scalar_label)
						else:
							series_name = "%s per %s in %s" % (attr_label, scalar_label, " & ".join(location_names))
					else:
						if len(location_names) == 1 and attr_token == datamodeling_service.QUERYABLE_ATTR_OTHER_DEATHS:
							series_name = "%s" % (attr_label)
						else:
							series_name = "%s in %s" % (attr_label, " & ".join(location_names))

					if attr.startswith(datamodeling_service.QUERYABLE_ATTR_OTHER_DEATH_prefix):
						function_get_value = lambda ldd: float(datamodeling_service.CAUSEOFDEATH_USYEARLYDEATHS[attr]) / (365.0 * float(constants.USA_POPULATION))
						normalize_by_population = False
						multiple_location_handling = datamodeling_service.MULTIPLE_LOCATION_HANDLING_AVG
					elif attr == datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE:
						scalar = 100
						normalize_by_population = False
						multiple_location_handling = datamodeling_service.MULTIPLE_LOCATION_HANDLING_AVG
						function_get_value = lambda ldd: min(1, float(ldd.positive) / float(ldd.total_tests))
					else:
						attr_label = attr_label + "s"
						normalize_by_population = True
						multiple_location_handling = datamodeling_service.MULTIPLE_LOCATION_HANDLING_SUM
						if attr_token == datamodeling_service.QUERYABLE_ATTR_COVID_DEATHS:
							query_attr = "deaths"
						else:
							query_attr = attr
						function_get_value = lambda ldd: float(getattr(ldd, query_attr, 0))

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
			chart_data["name"] = chart_meta['name']
			if chart_data["name"] is None:
				all_attrs = [attr.replace("_", " ").title() for attr in chart_meta['attributes']]
				chart_data["name"] = "%s in %s" % (" vs ".join(all_attrs), ", ".join(sorted(set(all_location_names))))
	return chart_list


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
