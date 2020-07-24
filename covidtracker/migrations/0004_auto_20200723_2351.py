from django.db import migrations


def import_data(a1, a2):
    from covidtracker import constants
    constants.add_to_db()
    print(constants.get_usa_population())


class Migration(migrations.Migration):
    dependencies = [
        ('covidtracker', '0003_auto_20200723_2349'),
    ]

    operations = [
        migrations.RunPython(import_data)
    ]
