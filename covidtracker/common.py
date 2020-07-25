import datetime

import dateparser
from django.core.serializers.json import DjangoJSONEncoder


class MyJSONEncoder(DjangoJSONEncoder):
	def default(self, o):
		if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
			return get_date_key(o)
		else:
			return super().default(o)


def get_date(obj, attr, default_value=None):
	return parse_date(get(obj, attr, default_value))


def get(obj, attr, default_value=None):
	try:
		return obj[attr]
	except:
		return getattr(obj, attr, default_value)


def get_date_key(d):
	d = parse_date(d)
	if d is None:
		return None
	return d.strftime("%Y%m%d")


def parse_date(date_str):
	if date_str is None:
		return None
	elif isinstance(date_str, datetime.date):
		return date_str
	elif isinstance(date_str, datetime.datetime):
		return date_str.date()
	else:
		return dateparser.parse(date_str)
