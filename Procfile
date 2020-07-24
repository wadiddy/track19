release: python manage.py migrate covidtracker
web: gunicorn covidtracker.wsgi --log-file -
