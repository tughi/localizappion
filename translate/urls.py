from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<translator_uuid>[0-9a-f-]+)/projects/(?P<project_uuid>[0-9a-f-]+)/languages/(?P<language_code>[a-z]{2}(_[A-Z]{2})?)/status$',
        views.status,
        name='status'),
    url(r'^(?P<translator_uuid>[0-9a-f-]+)/projects/(?P<project_uuid>[0-9a-f-]+)/languages/(?P<language_code>[a-z]{2}(_[A-Z]{2})?)$',
        views.translate,
        name='translate'),
]
