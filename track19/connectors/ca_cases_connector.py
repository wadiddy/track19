import pprint

import dateparser

from track19 import models
from track19.connectors.base_connector import BaseConnector
from track19.connectors.base_connector import get_safe_number, get_non_none


class CaCasesConnector(BaseConnector):
    def pre_process(self):
        ca_location = models.Location.objects.get(token='CA')
        california_population = float(ca_location.population)

        map_ca_date_totaltests = {}
        for l in models.LocationDayData.objects.filter(location=ca_location):
            map_ca_date_totaltests[l.date] = l.total_tests

        self.map_location_date_totaltests = {}
        for l in models.Location.objects.filter(token__startswith="CA:"):
            location_date_totaltests = self.map_location_date_totaltests[l] = {}
            percent_of_pop = float(l.population) / california_population
            for d, totaltests in map_ca_date_totaltests.items():
                location_date_totaltests[d] = percent_of_pop * float(map_ca_date_totaltests[d])

    def get_csv_url(self):
        return "https://data.ca.gov/dataset/590188d5-8545-4c93-a9a0-e230f0db7290/resource/926fd08f-cc91-4828-af38-bd45de97f8c3/download/statewide_cases.csv"

    def get_date(self, row):
        return dateparser.parse(row['date']).date()

    def get_location_token(self, row):
        return "CA: %s County" % row['county']

    def build_locationdaydata_model(self, location, date, row):
        try:
            location_date_total_tests = self.map_location_date_totaltests[location]
            total_tests = location_date_total_tests[date]
        except:
            total_tests = 0

        return models.LocationDayData(
            location=location,
            date=date,
            positive=get_safe_number(row['newcountconfirmed']),
            total_tests=total_tests,
            deaths=get_safe_number(row['newcountdeaths']),
            on_ventilator=None,
            in_hospital=None,
            in_icu=None
        )
