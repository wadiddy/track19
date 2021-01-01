import json
import pprint

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from . import models, datamodeling_service, common
from .common import MyJSONEncoder


def index_page(request):
	if 'woodcrestdrive.com' in common.get(request.META, 'HTTP_HOST'):
		from track19 import views_mapper
		return views_mapper.mapper_page(request)

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
			"attributes": [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE],
			"markers": [
				{
					"date": common.get_date_key(common.parse_date("2020-11-26")),
					"text": "Thanksgiving"
				},
				{
					"date": common.get_date_key(common.parse_date("2020-12-25")),
					"text": "Christmas"
				}
			]
		})

	chart_data = build_chart_data(page_model)

	description = "; ".join([c['name'] for c in chart_data])

	return _send_response(request, "index.html", {
		"description": description,
		"chart_data": chart_data,
		"chart_data_json": json.dumps(chart_data),
		"page_model": page_model,
		"page_model_json": json.dumps(page_model),
		"avail_locations": models.Location.get_locations()
	})


def report_attr(request, attr=None, expand_list=None):
	loc_name_map = {l.token:l.name for l in models.Location.objects.all()}
	map_attrs = {lv['value']: lv['label'] for lv in get_attr_labelvalues()}
	if attr not in map_attrs:
		attr = datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE

	if attr in [datamodeling_service.QUERYABLE_ATTR_POSITIVE_RATE]:
		suffix = "%"
	else:
		suffix = ""

	lists = common.filter_none([
		build_metric_table_data(loc_name_map, "bad_now", "Where's it bad right now?", attr, "latest_value", lambda r: suffix, True, expand_list),
		# build_metric_table_data(loc_name_map, "ok_now", "Where's it OK right now?", attr, "latest_value", lambda r: suffix, False, expand_list),
		# build_metric_table_data(loc_name_map, "worse_30d", "Where's it getting worse over last 30 days?", attr, "month_delta", "% worse", True, expand_list),
		# build_metric_table_data(loc_name_map, "better_30d", "Where's it getting better over last 30 days?", attr, "month_delta", "% better", False, expand_list),
		build_metric_table_data(loc_name_map, "worse", "Where's it getting worse over last two weeks?", attr, "two_week_delta", lambda r: "% worse" if r.two_week_delta > 0 else "% better", True, expand_list, filter_zero=True),
		build_metric_table_data(loc_name_map, "better", "Where's it getting better over last two weeks?", attr, "two_week_delta", lambda r: "% worse" if r.two_week_delta > 0 else "% better", False, expand_list, filter_zero=True),
		build_metric_table_data(loc_name_map, "highest_peak", "Who had the highest peak?", attr, "peak_value", lambda r: " on %s" % common.format_date(r.peak_date), True, expand_list, filter_zero=True),
		build_metric_table_data(loc_name_map, "lowest_peak", "Who had the lowest peak?", attr, "peak_value", lambda r: " on %s" % common.format_date(r.peak_date), False, expand_list, filter_zero=True)
	])

	return _send_response(request, "report_attr.html", {
		"description":  datamodeling_service.QUERYABLE_ATTR_LABELS[attr] + " details",
		"location_lists": lists,
		"attr_name": map_attrs[attr],
		"secondary_attrs": [],
		"attr_token": attr
	})


def build_metric_table_data(loc_name_map, list_token, name, query_attr, model_field_name, suffix_lambda, descending=False, expand_list=None, filter_zero=False):
	if expand_list is not None and expand_list != list_token:
		return None


	data = [
		{
			"loc": r.token,
			"loc_name": loc_name_map[r.token],
			"value": abs(getattr(r, model_field_name)),
			"suffix": suffix_lambda(r)
		} for r in models.RollupLocationAttrRecentDelta.objects
			                   .filter(attr=query_attr)
			                   .order_by(("-" if descending else "") + model_field_name)
	]

	if filter_zero:
		data = [d for d in data if d['value'] != 0.0]

	if expand_list is None:
		data = data[0:10]

	return {
		"list_token": list_token,
		"name": name,
		"data": data,
	}


def _send_response(request, tmpl, ctx=None):
	if ctx is None:
		ctx = {}

	qs = request.META['QUERY_STRING']
	ctx["full_url"] = request.META['PATH_INFO'] + ("?" + qs if qs is not None and len(qs) > 0 else "")
	ctx["avail_attributes"] = get_attr_labelvalues()

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

	if common.get(ctx, "title") is None:
		ctx["title"] = "Track 19"

	if common.get(ctx, "description") is None:
		ctx["description"] = "America's best covid tracker"


	r = render(request, tmpl, context=ctx)

	return r


def about(request):
	return _send_response(request, "about.html", {
		"metrics": get_attr_labelvalues()
	})


def build_page_model(request, default_chart=None):
	from track19 import datamodeling_service
	request_dict, guid_query = models.GuidQuery.get_query_dict(request)

	page_model = {
		"api_url": reverse(api_v1_fetch) + ("?" + guid_query.query if guid_query is not None else ""),
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
			attributes = [a for a in common.get(request_dict, "attr" + suffix, []) if a in datamodeling_service.QUERYABLE_ATTRS]

			markers = []
			for md in common.get(request_dict, "md" + suffix, []):
				if "~" in md:
					md_parts = md.split("~")
					markers.append({
						"date": md_parts[0],
						"text": "~".join(md_parts[1:]),
					})

			if len(locations) > 0 and len(attributes) > 0:
				page_model['charts'].append({
					"name": common.get_first(request_dict, "name" + suffix),
					"locations": locations,
					"attributes": attributes,
					"markers": markers
				})

		if len(page_model['charts']) == 0 and default_chart is not None:
			page_model['charts'].append(default_chart)

	return page_model


@cache_page(60 * 5)
def api_v1_attributes(request):
	return send_api_response(get_attr_labelvalues())


@cache_page(60 * 5)
def api_v1_locations(request):
	return send_api_response(models.Location.get_locations())


@cache_page(60 * 5)
def api_v1_fetch(request):
	return send_api_response(
		build_chart_data(
			build_page_model(request)
		)
	)


def build_chart_data(page_model):
	loc_name_map = {l.token:l.name for l in models.Location.objects.all()}
	rolling_average_size = page_model['rolling_average_size']
	earliest_date = common.parse_date(page_model['earliest_date'])
	latest_date = common.parse_date(page_model['latest_date'])

	chart_list = []
	for chart_meta in page_model['charts']:
		all_location_names = []
		chart_data = {
			"markers": chart_meta["markers"],
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
					if lt not in loc_name_map:
						continue

					location_tokens.append(lt)
					location_names.append(loc_name_map[lt])

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
