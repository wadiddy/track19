import os
import pathlib
from pprint import pprint

import dateparser

from track19 import models, common
from track19.connectors.base_connector import BaseConnector
from track19.connectors.base_connector import get_safe_number, get_non_none

map_county_population = {
	"Adams": 20348,
	"Ashland": 15600,
	"Barron": 45164,
	"Bayfield": 15042,
	"Brown": 263378,
	"Buffalo": 13125,
	"Burnett": 15392,
	"Calumet": 50159,
	"Chippewa": 64135,
	"Clark": 34709,
	"Columbia": 57358,
	"Crawford": 16291,
	"Dane": 542364,
	"Dodge": 87847,
	"Door": 27610,
	"Douglas": 43208,
	"Dunn": 45131,
	"Eau Claire": 104534,
	"Florence": 4321,
	"Fond du Lac": 103066,
	"Forest": 8991,
	"Grant": 51554,
	"Green": 36929,
	"Green Lake": 18918,
	"Iowa": 23771,
	"Iron": 5676,
	"Jackson": 20478,
	"Jefferson": 85129,
	"Juneau": 26617,
	"Kenosha": 169290,
	"Kewaunee": 20383,
	"La Crosse": 118230,
	"Lafayette": 16665,
	"Langlade": 19268,
	"Lincoln": 27689,
	"Manitowoc": 79074,
	"Marathon": 135428,
	"Marinette": 40434,
	"Marquette": 15434,
	"Menominee": 4658,
	"Milwaukee": 948201,
	"Monroe": 46051,
	"Oconto": 37830,
	"Oneida": 35470,
	"Outagamie": 187365,
	"Ozaukee": 89147,
	"Pepin": 7289,
	"Pierce": 42555,
	"Polk": 43598,
	"Portage": 70942,
	"Price": 13397,
	"Racine": 196584,
	"Richland": 17377,
	"Rock": 163129,
	"Rusk": 14147,
	"Sauk": 64249,
	"Sawyer": 16489,
	"Shawano": 40796,
	"Sheboygan": 115456,
	"St. Croix": 89694,
	"Taylor": 20412,
	"Trempealeau": 29442,
	"Vernon": 30785,
	"Vilas": 21938,
	"Walworth": 103718,
	"Washburn": 15878,
	"Washington": 135693,
	"Waukesha": 403072,
	"Waupaca": 51128,
	"Waushara": 24263,
	"Winnebago": 171020,
	"Wood": 73055
}


class WisconsinConnector(BaseConnector):
	def get_json_url(self):
		return "https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.geojson?where=GEO%20%3D%20%27County%27"

	def _import_json(self, json_url):
		location_map = {l.pk: l for l in models.Location.objects.all()}
		import urllib.request, json
		with urllib.request.urlopen(json_url) as url:
			data = json.loads(url.read().decode())
			props = []
			for feature in data['features']:
				prop_bucket = feature['properties']
				parsed_date = common.parse_date(prop_bucket['DATE'])
				if parsed_date is not None and prop_bucket['NAME'] is not None:
					prop_bucket["parsed_date"] = parsed_date
					props.append(prop_bucket)

		map_location_previous_hosp = {}
		map_location_previous_icu = {}
		for prop_bucket in sorted(props, key=lambda p:p['parsed_date']):
			date = prop_bucket['parsed_date']
			county_name = prop_bucket['NAME']
			county_token = "wi_county_" + county_name

			if county_token in location_map:
				location = location_map[county_token]
			else:
				location = models.Location(
					token=county_token,
					name="WI: %s County" % county_name,
					population=map_county_population[county_name]
				)
				location.save()
				location_map[county_token] = location

			try:
				ldd = models.LocationDayData.objects.get(location=location, date=date)
			except models.LocationDayData.DoesNotExist:
				ldd = models.LocationDayData(location=location, date=date)

			ldd.positive = get_safe_number(prop_bucket['POS_NEW'])
			ldd.total_tests = get_safe_number(prop_bucket['TEST_NEW'])
			ldd.deaths = get_safe_number(prop_bucket['DTH_NEW'])

			ldd.on_ventilator = 0

			hosp_yes = common.default(get_safe_number(prop_bucket['HOSP_YES']), 0)
			prev_in_hospital = map_location_previous_hosp[location] if location in map_location_previous_hosp else 0
			ldd.in_hospital = hosp_yes- prev_in_hospital
			map_location_previous_hosp[location] = hosp_yes

			ic_yes = common.default(get_safe_number(prop_bucket['IC_YES']), 0)
			prev_in_icu = map_location_previous_icu[location] if location in map_location_previous_icu else 0
			ldd.in_icu = ic_yes- prev_in_icu
			map_location_previous_icu[location] = ic_yes

			ldd.save()
