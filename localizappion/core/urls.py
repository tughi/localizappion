from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^projects$', views.ProjectListView.as_view(), name='project_list'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings$', views.ProjectStringsView.as_view(), name='project_strings'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings-commit', views.ProjectStringsCommitView.as_view(), name='project_strings_commit'),
)
