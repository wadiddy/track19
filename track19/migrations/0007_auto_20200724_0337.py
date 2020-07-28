from django.db import migrations

from track19.constants import USA_STATES

DICT_GROUPNAME_LOCATIONTOKENS = {
    "USA": USA_STATES,

    "LA Area": [
        "CA: Los Angeles County",
        "CA: Ventura County",
        "CA: Orange County",
        "CA: Riverside County",
        "CA: San Bernardino County",
    ],

    "San Francisco Bay Area": [
        "CA: Alameda County",
        "CA: Contra Costa County",
        "CA: Marin County",
        "CA: Napa County",
        "CA: San Francisco County",
        "CA: San Mateo County",
        "CA: Santa Clara County",
        "CA: Solano County",
        "CA: Sonoma County"
    ],

    "Delta": [
        "CA: Sacramento County",
        "CA: Yolo County",
        "CA: San Joaquin County"
    ]
}



def create_groups(a1, a2):
    from track19 import models

    for group_name, location_tokens in DICT_GROUPNAME_LOCATIONTOKENS.items():
        token = "".join(group_name.split(" "))
        location_group = models.LocationGroup(token=token, name=group_name)
        location_group.save()
        for l in models.Location.objects.filter(token__in=location_tokens):
            models.LocationGroupLocation(location_group=location_group, location=l).save()


class Migration(migrations.Migration):
    dependencies = [
        ('track19', '0006_locationgroup_locationgrouplocation'),
    ]

    operations = [
        migrations.RunPython(create_groups)
    ]
