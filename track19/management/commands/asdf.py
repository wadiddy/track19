from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from track19 import datamodeling_service, models


class Command(BaseCommand):
	def handle(self, *args, **options):
		# models.RollupLocationAttrRecentDelta.objects.all().delete()
		datamodeling_service.build_report_caches()
		# for asdf in models.RollupLocationAttrRecentDelta.objects.all():
		# 	print(str(asdf))

		# print(models.RollupLocationAttrRecentDelta.objects.count())
