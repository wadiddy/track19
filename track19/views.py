import json
import pprint

import dateparser
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from . import models, datamodeling_service, common, constants
from .common import MyJSONEncoder


def index_page(request):
	if 'g' not in request.GET:
		gq = models.GuidQuery.get(request)
		if gq is not None:
			return HttpResponseRedirect(reverse('index_page') + "?g=" + gq.guid)

	if 'clear' in request.GET:
		page_model = build_page_model(request)
	else:
		page_model = build_page_model(request, default_chart={
			"name": None,
			"locations": ["USA"],
			"attributes": [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE]
		})

	chart_data = build_chart_data(page_model)

	return _send_response(request, "index.html", {
		"chart_data": chart_data,
		"chart_data_json": json.dumps(chart_data),
		"page_model": page_model,
		"page_model_json": json.dumps(page_model),
		"avail_attributes": get_attr_labelvalues(),
		"avail_locations": models.Location.get_locations()
	})


def _send_response(request, tmpl, ctx=None):
	if ctx is None:
		ctx = {}

	ctx["last_updated"] = models.LocationDayData.objects.all().order_by("-date")[0].date

	ctx["example_charts"] = [
		{
			"params": "ravg=14&date_from=2020-02-01&loc=NY&loc=FL&loc=TX&loc=CA&attr=covid_deaths&loc1=NY&loc1=FL&loc1=TX&loc1=CA&attr1=positive",
			"label": "NY vs FL vs TX vs CA"
		},
		{
			"params": "ravg=14&date_from=2020-05-15&loc=SanFranciscoBayArea&loc=CA:%20San%20Francisco%20County&loc=CA&loc=USA&loc=WI&loc=Delta&attr=positive_rate",
			"label": "Positive Test Rate across multiple locations"
		},
		{
			"params": "ravg=14&date_from=2020-02-01&loc=CA:%20San%20Francisco%20County&attr=covid_deaths&attr=other_deaths&loc1=SanFranciscoBayArea&attr1=covid_deaths&attr1=other_deaths&loc2=Delta&attr2=covid_deaths&attr2=other_deaths&loc3=CA&attr3=covid_deaths&attr3=other_deaths&loc4=WI&attr4=covid_deaths&attr4=other_deaths&loc5=USA&attr5=covid_deaths&attr5=other_deaths",
			"label": "Deaths per million people across multiple locations "
		},
		{
			"params": "ravg=14&date_from=2020-05-15&loc=CA:%20San%20Francisco%20County&attr=positive_rate&attr=covid_deaths&loc1=SanFranciscoBayArea&attr1=positive_rate&attr1=covid_deaths&loc2=Delta&attr2=positive_rate&attr2=covid_deaths&loc3=CA&attr3=positive_rate&attr3=covid_deaths&loc4=USA&attr4=positive_rate&attr4=covid_deaths",
			"label": "Positive Test Rate vs Covid Deaths"
		},
	]

	r = render(request, tmpl, context=ctx)
	return r


def about(request):
	return _send_response(request, "about.html", {
		"metrics": get_attr_labelvalues()
	})


def build_page_model(request, default_chart=None):
	from track19 import datamodeling_service
	request_dict = models.GuidQuery.get_query_dict(request)
	pprint.pprint(request_dict)

	page_model = {
		"guid": common.get(request_dict, 'guid'),
		"rolling_average_size": common.get_int(request_dict, 'ravg', '14'),
		"earliest_date": common.get_date_key(common.get_date(request_dict, 'date_from', '2020-05-01')),
		"latest_date": common.get_date_key(common.get_date(request_dict, 'date_to')),
		"charts": []
	}

	if 'clear' not in request_dict:
		all_location_tokens = [l['token'] for l in models.Location.get_locations()]
		for i in range(10):
			suffix = "" if i == 0 else str(i)
			locations = [l for l in common.get(request_dict, "loc" + suffix, []) if l in all_location_tokens]
			attributes = [a for a in common.get(request_dict, "attr" + suffix, []) if
			              a in datamodeling_service.QUERYABLE_ATTRS]

			if len(locations) > 0 and len(attributes) > 0:
				page_model['charts'].append({
					"name": common.get_first(request_dict, "name" + suffix),
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
	return send_api_response(models.Location.get_locations())


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

			for ln in location_names:
				if ln not in all_location_names:
					# do this instead of a set to preserve order
					all_location_names.append(ln)

			locations = list(models.Location.objects.filter(token__in=location_tokens))
			total_population = sum([l.population for l in locations]) if len(locations) > 0 else 0

			for attr_token in chart_meta['attributes']:
				if attr_token == datamodeling_service.QUERYABLE_ATTR_OTHER_DEATHS:
					attrs = datamodeling_service.OTHER_CAUSES_OF_DEATH_DISPLAY
				else:
					attrs = [attr_token]

				for attr in attrs:
					attr_data, attr_label, scalar = datamodeling_service.build_attr_data(
						attr_token,
						attr,
						locations,
						earliest_date,
						latest_date,
						rolling_average_size
					)

					if scalar > 1:
						if scalar == 100000:
							scalar_label = "100k"
						elif scalar == 1000000:
							scalar_label = "1M"
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

					d = {
						"type": "series",
						"name": series_name,
						"location": loc_tokens,
						"population": total_population,
						"attr": attr,
						"rolling_average_size": rolling_average_size,
						"data": attr_data
					}

					series_list.append(d)
			chart_data["name"] = chart_meta['name']
			if chart_data["name"] is None:
				all_attrs = [attr.replace("_", " ").title() for attr in chart_meta['attributes']]
				chart_data["name"] = "%s in %s" % (" vs ".join(all_attrs), ", ".join(all_location_names))
	return chart_list


def send_api_response(payload):
	return JsonResponse({
		'success': True,
		'api_version': 1,
		'payload': payload,
	}, encoder=MyJSONEncoder)


def get_attr_labelvalues():
	return [
		{"label": datamodeling_service.QUERYABLE_ATTR_LABELS[a], "value": a}
		for a in datamodeling_service.QUERYABLE_ATTRS
	]
