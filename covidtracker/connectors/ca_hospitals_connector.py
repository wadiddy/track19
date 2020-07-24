import pprint

import dateparser

from covidtracker import models
from covidtracker.connectors.base_connector import BaseConnector
from covidtracker.connectors.base_connector import get_safe_number, get_non_none


class CaHospitalsConnector(BaseConnector):
    def get_csv_url(self):
        return "https://data.ca.gov/dataset/529ac907-6ba1-4cb7-9aae-8966fc96aeef/resource/42d33765-20fd-44b8-a978-b083b7542225/download/hospitals_by_county.csv"

    def get_date(self, row):
        return dateparser.parse(row['todays_date']).date()

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
            positive=None,
            total_tests=None,
            deaths=None,
            on_ventilator=None,
            in_hospital=get_safe_number(row['hospitalized_covid_patients']),
            in_icu=get_safe_number(row['icu_covid_confirmed_patients']),
        )
