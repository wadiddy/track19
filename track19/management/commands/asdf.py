import pprint

import dateparser
from django.core.management.base import BaseCommand

from track19 import covid_data_importer, datamodeling_service, models


class Command(BaseCommand):
	def handle(self, *args, **options):
		models.GuidQuery.objects.all().delete()
