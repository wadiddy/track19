from django.contrib import admin
from django.urls import path

admin.autodiscover()

import track19.views

urlpatterns = [
    path("", track19.views.index_page, name="index_page"),
    path("about", track19.views.about, name="about"),
    path("metric/<attr>/<expand_list>", track19.views.report_attr, name="report_attr"),
    path("metric/<attr>", track19.views.report_attr, name="report_attr"),
    path("metric", track19.views.report_attr, name="report_attr"),
    path("api/v1/fetch", track19.views.api_v1_fetch, name="api_v1_fetch"),
    path("api/v1/locations", track19.views.api_v1_locations, name="api_v1_locations"),
    path("api/v1/attributes", track19.views.api_v1_attributes, name="api_v1_attributes"),
]
