from django.db import models

def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


@auto_str
class Location(models.Model):
    token = models.TextField(primary_key=True)
    population = models.IntegerField(null=False, default=0)

@auto_str
class LocationDayData(models.Model):
    class Meta:
        unique_together = (('location', 'date'),)

    location = models.ForeignKey("Location", on_delete=models.DO_NOTHING)
    date = models.DateField(null=False)
    positive = models.IntegerField(null=True)
    total_tests = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    on_ventilator = models.IntegerField(null=True)
    in_hospital = models.IntegerField(null=True)
    in_icu = models.IntegerField(null=True)

