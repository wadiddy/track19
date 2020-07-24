import dateparser

from covidtracker import models
from covidtracker.connectors.base_connector import BaseConnector
from covidtracker.connectors.base_connector import get_safe_number, get_non_none


class UsaConnector(BaseConnector):
    def get_csv_url(self):
        return "https://covidtracking.com/api/v1/states/daily.csv"

    def get_date(self, row):
        return dateparser.parse(str(row['date']), date_formats=["%Y%m%d"]).date()

    def get_location_token(self, row):
        return row['state']

    def build_locationdaydata_model(self, location, date, row):
        return models.LocationDayData(
            location=location,
            date=date,
            positive=get_safe_number(row['positive']),
            total_tests=get_safe_number(row['positive'] + row['negative']),
            deaths=get_safe_number(row['deathIncrease']),
            on_ventilator=get_safe_number(row['onVentilatorCurrently']),
            in_hospital=get_safe_number(row['hospitalizedCurrently']),
            in_icu=get_safe_number(row['inIcuCurrently'])
        )

