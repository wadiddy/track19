from django.urls import path

from django.contrib import admin

admin.autodiscover()

import covidtracker.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", covidtracker.views.index_page, name="index_page"),
    path("about", covidtracker.views.about, name="about"),
    path("api/v1/fetch", covidtracker.views.api_vi_fetch, name="api_vi_fetch"),
    path("api/v1/locations", covidtracker.views.api_vi_locations, name="api_vi_locations"),
    path("api/v1/attributes", covidtracker.views.api_vi_attributes, name="api_vi_attributes"),
]
