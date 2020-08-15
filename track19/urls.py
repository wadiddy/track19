from django.urls import path

from django.contrib import admin

admin.autodiscover()

import track19.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", track19.views.index_page, name="index_page"),
    path("about", track19.views.about, name="about"),
    path("metric/<attr>/<expand_list>", track19.views.report_attr, name="report_attr"),
    path("metric/<attr>", track19.views.report_attr, name="report_attr"),
    path("metric", track19.views.report_attr, name="report_attr"),
    path("api/v1/fetch", track19.views.api_vi_fetch, name="api_vi_fetch"),
    path("api/v1/locations", track19.views.api_vi_locations, name="api_vi_locations"),
    path("api/v1/attributes", track19.views.api_vi_attributes, name="api_vi_attributes"),
]
