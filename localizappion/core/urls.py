from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^projects$', views.ProjectListView.as_view(), name='project_list'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)$', views.ProjectStatusView.as_view(), name='project'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings$', views.ProjectStringsView.as_view(), name='project_strings'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/strings-commit$', views.ProjectStringsCommitView.as_view(), name='project_strings_commit'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/new-suggestions$', views.ProjectNewSuggestions.as_view(), name='project_new_suggestions'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/new-suggestions/(?P<suggestion_uuid>[0-9a-f-]+)$', views.ProjectNewSuggestion.as_view(), name='project_new_suggestion'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/new-suggestions/(?P<suggestion_uuid>[0-9a-f-]+)/accept$', views.ProjectNewSuggestionAccept.as_view(), name='project_new_suggestion_accept'),
    url(r'^projects/(?P<project_uuid>[0-9a-f-]+)/new-suggestions/(?P<suggestion_uuid>[0-9a-f-]+)/reject$', views.ProjectNewSuggestionReject.as_view(), name='project_new_suggestion_reject'),
)
