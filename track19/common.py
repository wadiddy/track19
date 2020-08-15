import datetime

import dateparser
from django.core.serializers.json import DjangoJSONEncoder


class MyJSONEncoder(DjangoJSONEncoder):
	def default(self, o):
		if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
			return get_date_key(o)
		else:
			return super().default(o)


def get_first(obj, attr, default_value=None):
	v = get(obj, attr)
	if v is None:
		return default_value

	if isinstance(v, list):
		if len(v) == 0:
			return default_value
		else:
			return v[0]

def get_int(obj, attr, default_value=None):
	try:
		return int(get_first(obj, attr, default_value))
	except:
		return default_value

def get_date(obj, attr, default_value=None):
	return parse_date(get_first(obj, attr, default_value))


def get(obj, attr, default_value=None):
	try:
		return obj[attr]
	except:
		return getattr(obj, attr, default_value)


def get_date_key(d):
	d = parse_date(d)
	if d is None:
		return None
	return d.strftime("%Y-%m-%d")


def parse_date(date_str):
	if date_str is None:
		return None
	elif isinstance(date_str, datetime.date):
		return date_str
	elif isinstance(date_str, datetime.datetime):
		return date_str.date()
	else:
		return dateparser.parse(date_str, date_formats=["%Y-%m-%d"])


def format_date(d):
	d = parse_date(d)
	if d is None:
		return None

	day = d.day
	suffix = 'th' if 11<=day<=13 else {1:'st',2:'nd',3:'rd'}.get(day%10, 'th')

	return d.strftime("%b %d").lstrip("0").replace(" 0", " ") + suffix


def flip_map(m_in):
	return {v:k for k, v in m_in.items()}


def filter_none(l):
	if l is None:
		return None

	return [r for r in l if r is not None]