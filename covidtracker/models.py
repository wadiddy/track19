from django.db import models

class Location(models.Model):
    token = models.TextField(primary_key=True)
    population = models.IntegerField(null=False, default=0)

class LocationDayData(models.Model):
    location_token = models.ForeignKey("Location", on_delete=models.DO_NOTHING)
    date = models.DateField(null=False)
    positive = models.IntegerField(null=True)
    total_tests = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    on_ventilator = models.IntegerField(null=True)
    in_hospital = models.IntegerField(null=True)
    in_icu = models.IntegerField(null=True)

