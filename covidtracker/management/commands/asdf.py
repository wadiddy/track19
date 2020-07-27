import pprint

import dateparser
from django.core.management.base import BaseCommand

from covidtracker import covid_data_importer, datamodeling_service, models


class Command(BaseCommand):
	def handle(self, *args, **options):
		print(dateparser.parse("20200501"))
		print(dateparser.parse("2020-05-01"))
