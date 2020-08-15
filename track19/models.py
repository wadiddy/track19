import hashlib
import random
import uuid

from django.db import models
from django.http import QueryDict

from track19 import common


def auto_str(cls):
	def __str__(self):
		return '%s(%s)' % (
			type(self).__name__,
			', '.join('%s=%s' % item for item in vars(self).items())
		)

	cls.__str__ = __str__
	return cls


class LocationGroup(models.Model):
	token = models.TextField(primary_key=True)
	name = models.TextField()


class LocationGroupLocation(models.Model):
	location_group = models.ForeignKey("LocationGroup", on_delete=models.DO_NOTHING)
	location = models.ForeignKey("Location", on_delete=models.DO_NOTHING)


class GuidQuery(models.Model):
	guid = models.CharField(primary_key=True, max_length=40)
	query = models.TextField(db_index=True, unique=True)


	@staticmethod
	def get_query_dict(request):
		gq = GuidQuery.get(request)
		if gq is None:
			return {}
		else:
			d = dict(QueryDict(gq.query).lists())
			d['guid'] = gq.guid
			return d


	@staticmethod
	def get(request):
		try:
			return GuidQuery.objects.get(guid=common.get(request.GET, 'g'))
		except GuidQuery.DoesNotExist:
			uri = request.build_absolute_uri()
			if "?" not in uri:
				return None

			query = uri.split("?")[1]
			try:
				return GuidQuery.objects.get(query=query)
			except GuidQuery.DoesNotExist:
				gq = GuidQuery(
					guid=str(uuid.uuid4().hex),
					query=query
				)
				gq.save()
				return gq


@auto_str
class Location(models.Model):
	token = models.TextField(primary_key=True)
	population = models.IntegerField(null=False, default=0)

	@staticmethod
	def get_locations():
		locations = []
		for lg in LocationGroup.objects.all():
			group_population = 0
			for l in Location.objects.filter(pk__in=[lgl.location_id for lgl in lg.locationgrouplocation_set.all()]):
				group_population += l.population
			locations.append({
				"type": "location_group",
				"token": lg.token,
				"name": lg.name,
				"population": group_population
			})

		for l in Location.objects.all():
			locations.append({
				"type": "location",
				"token": l.token,
				"name": l.token,
				"population": l.population
			})

		return locations

@auto_str
class RollupLocationAttrRecentDelta(models.Model):
	k = models.TextField(primary_key=True, default="0")
	token = models.TextField()
	attr = models.TextField()

	class Meta:
		unique_together = ('token', 'attr',)

	latest_date = models.DateField(null=True)
	two_weeks_ago_date = models.DateField(null=True)
	month_ago_date = models.DateField(null=True)

	peak_date = models.DateField(null=True)
	peak_value = models.FloatField(default=0)

	latest_value = models.FloatField(default=0)
	two_weeks_ago_value = models.FloatField(default=0)
	month_ago_value = models.FloatField(default=0)

	two_week_delta = models.FloatField(default=0)
	month_delta = models.FloatField(default=0)


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
