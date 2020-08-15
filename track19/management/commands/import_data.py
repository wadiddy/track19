from django.core.management.base import BaseCommand

from track19 import covid_data_importer, datamodeling_service


class Command(BaseCommand):
    def handle(self, *args, **options):
        covid_data_importer.exec()
        datamodeling_service.build_report_caches()
