import pprint

import numpy
import pandas

from track19 import models


class BaseConnector():
	def import_data(self):
		self.pre_process()

		print("start count", models.LocationDayData.objects.count())

		csv_url = None
		json_url = None
		try:
			csv_url = self.get_csv_url()
		except:
			json_url = self.get_json_url()

		if csv_url is not None:
			self._import_csv(csv_url)
		elif json_url is not None:
			self._import_json(json_url)

		self.post_process()
		print("end count", models.LocationDayData.objects.count())

	def _import_json(self, csv_url):
		raise Exception("Abstract Method")

	def _import_csv(self, csv_url):
		location_map = {l.pk: l for l in models.Location.objects.all()}
		for idx, row in pandas.read_csv(csv_url).iterrows():
			try:
				row_date = self.get_date(row)
			except:
				print("invalid line", "date", row)
				continue

			row_location_token = self.get_location_token(row)
			if row_location_token not in location_map:
				continue

			location = location_map[row_location_token]
			locdaydata_model = self.build_locationdaydata_model(location, row_date, row)

			try:
				existing_location = models.LocationDayData.objects.get(location=location, date=row_date)
				existing_location.positive = get_non_none(locdaydata_model.positive, existing_location.positive)
				existing_location.total_tests = get_non_none(locdaydata_model.total_tests,
				                                             existing_location.total_tests)
				existing_location.deaths = get_non_none(locdaydata_model.deaths, existing_location.deaths)
				existing_location.on_ventilator = get_non_none(locdaydata_model.on_ventilator,
				                                               existing_location.on_ventilator)
				existing_location.in_hospital = get_non_none(locdaydata_model.in_hospital,
				                                             existing_location.in_hospital)
				existing_location.in_icu = get_non_none(locdaydata_model.in_icu, existing_location.in_icu)
				existing_location.save()
			except models.LocationDayData.DoesNotExist:
				locdaydata_model.save()

	def pre_process(self):
		pass

	def post_process(self):
		pass

	def get_json_url(self):
		raise Exception("abstract method")

	def get_csv_url(self):
		raise Exception("abstract method")

	def get_date(self, csv_line):
		raise Exception("abstract method")

	def get_location_token(self, csv_line):
		raise Exception("abstract method")

	def build_locationdaydata_model(self, location, date, csv_line):
		raise Exception("abstract method")


def get_safe_number(v):
	if v is None:
		return None
	if v == '':
		return None
	elif numpy.isnan(v):
		return None
	else:
		return v


def get_non_none(n1, n2):
	if n1 is not None:
		return n1
	elif n2 is not None:
		return n2
	else:
		return None
