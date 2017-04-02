from django.conf.urls import include, url
from django.contrib import admin

import localizappion.core.urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('localizappion.core.urls')),
]
