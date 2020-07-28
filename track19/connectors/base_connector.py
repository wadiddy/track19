import pprint

import numpy
import pandas

from track19 import models


class BaseConnector():
    def import_csv(self):
        self.pre_process()

        location_map = {l.pk:l for l in models.Location.objects.all()}

        print("start count", models.LocationDayData.objects.count())
        for idx, row in pandas.read_csv(self.get_csv_url()).iterrows():
            try:
                row_date = self.get_date(row)
            except:
                print("invalid line", "date", row)
                continue

            row_location_token = self.get_location_token(row)
            if row_location_token not in location_map:
                continue

            location = location_map[row_location_token]
            locdaydata_model = self.build_locationdaydata_model(location, row_date, row)

            try:
                existing_location = models.LocationDayData.objects.get(location=location, date=row_date)
                existing_location.positive = get_non_none(locdaydata_model.positive, existing_location.positive)
                existing_location.total_tests = get_non_none(locdaydata_model.total_tests, existing_location.total_tests )
                existing_location.deaths = get_non_none(locdaydata_model.deaths, existing_location.deaths )
                existing_location.on_ventilator = get_non_none(locdaydata_model.on_ventilator, existing_location.on_ventilator )
                existing_location.in_hospital = get_non_none(locdaydata_model.in_hospital, existing_location.in_hospital )
                existing_location.in_icu = get_non_none(locdaydata_model.in_icu, existing_location.in_icu )
                existing_location.save()
            except models.LocationDayData.DoesNotExist:
                locdaydata_model.save()

        self.post_process()
        print("end count", models.LocationDayData.objects.count())

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def get_csv_url(self):
        raise Exception("abstract method")

    def get_date(self, csv_line):
        raise Exception("abstract method")

    def get_location_token(self, csv_line):
        raise Exception("abstract method")

    def build_locationdaydata_model(self, location, date, csv_line):
        raise Exception("abstract method")

def get_safe_number( v):
    if numpy.isnan(v):
        return None
    else:
        return v

def get_non_none(n1, n2):
    if n1 is not None:
        return n1
    elif n2 is not None:
        return n2
    else:
        return None
