from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from track19 import datamodeling_service, models


class Command(BaseCommand):
	def handle(self, *args, **options):
		datamodeling_service.init()
		datamodeling_service.build_report_caches()
