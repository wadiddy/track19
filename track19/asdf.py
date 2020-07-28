from track19 import constants, covid_data_importer

import django
django.setup()

covid_data_importer.exec()
