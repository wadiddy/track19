from django.core.management.base import BaseCommand

from covidtracker import covid_data_importer


class Command(BaseCommand):
    def handle(self, *args, **options):
        covid_data_importer.exec()