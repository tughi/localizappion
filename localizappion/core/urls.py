from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings$', views.ProjectStringsView.as_view(), name='project_strings'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings/upload$', views.ImportStringsXmlView.as_view(), name='project_strings_upload'),
]
