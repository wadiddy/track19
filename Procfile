release: python manage.py migrate --app covidtracker
web: gunicorn covidtracker.wsgi --log-file -
