import pprint

import dateparser
from django.core.management.base import BaseCommand

from covidtracker import covid_data_importer, datamodeling_service, models


class Command(BaseCommand):
	def handle(self, *args, **options):
		d = datamodeling_service.get_normalized_data(
			models.Location.objects.filter(token="CA: San Francisco County"),
			lambda ldd: ldd.in_hospital,
			1000000,
			dateparser.parse("2020-05-01"),
			normalize_by_population=True
		)

		pprint.pprint(d)
