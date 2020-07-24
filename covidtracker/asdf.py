from covidtracker import constants, covid_data_importer

import django
django.setup()

# covid_data_importer.exec()
# print("asdf", constants.get_usa_population())
constants.add_to_db()
print(constants.get_usa_population())