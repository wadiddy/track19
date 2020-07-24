from django.shortcuts import render

from . import models


def index_page(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "here.html", context={
        "location_count": models.Location.objects.count()
    })

