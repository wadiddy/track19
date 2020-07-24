import dateparser
from django.shortcuts import render

from . import models, datamodeling_service


def index_page(request):
    d = datamodeling_service.get_normalized_data(
        models.Location.objects.filter(token="CA: San Francisco County"),
        lambda ldd: float(ldd.positive) / float(ldd.total_tests),
        1,
        dateparser.parse("2020-05-01"),
        normalize_by_population=False
    )

    d = datamodeling_service.get_normalized_data(
        models.Location.objects.filter(token="CA: San Francisco County"),
        lambda ldd: ldd.positive,
        100000,
        dateparser.parse("2020-05-01")
    )

    d = datamodeling_service.get_normalized_data(
        models.Location.objects.filter(token="CA: San Francisco County"),
        lambda ldd: ldd.deaths,
        1000000,
        dateparser.parse("2020-05-01"),
        normalize_by_population=True
    )

    d = datamodeling_service.get_normalized_data(
        models.Location.objects.filter(token="CA: San Francisco County"),
        lambda ldd: ldd.in_hospital,
        1000000,
        dateparser.parse("2020-05-01"),
        normalize_by_population=True
    )

    d = datamodeling_service.get_normalized_data(
        models.Location.objects.filter(token="CA: San Francisco County"),
        lambda ldd: ldd.in_hospital,
        1000000,
        dateparser.parse("2020-05-01"),
        normalize_by_population=True
    )



    return render(request, "here.html", context={
        "location_count": models.LocationDayData.objects.count()
    })
