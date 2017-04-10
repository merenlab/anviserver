from django.conf.urls import url, include
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from main.views import projects, index, interactive, teams, profile, redirect, settings
from main.forms import UserRegForm
from main import backend

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/settings/$', settings.show_settings, name="user_settings"),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegForm), {'backend': 'registration.backends.default.DefaultBackend'}, name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),


    url(r'^(?P<access_type>public|private)/(?P<username>\w+)/(?P<share_name>\w+)', redirect.redirect_view, name="redirect_view"),

    url(r'^projects/new', projects.new_project, name="projects_new"),
    url(r'^projects/details/(?P<project_slug>\w+)', projects.details_project, name="projects_details"),
    url(r'^projects/share/(?P<project_slug>\w+)', projects.share_project, name="projects_share"),
    url(r'^projects', projects.list_projects, name="projects"),

    url(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/members', teams.list_members, name="teams_members"),
    url(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/projects', teams.list_projects, name="teams_projects"),
    url(r'^teams', teams.list_teams, name="teams"),

    url(r'^ajax/(?P<username>\w+)/(?P<project_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler),
    url(r'^(?P<username>\w+)/(?P<project_slug>\w+)/download', interactive.download_zip, name="download_zip"),
    url(r'^(?P<username>\w+)/(?P<project_slug>\w+)', interactive.show_interactive, name="show_interactive"),

    url(r'^(?P<username>\w+)', profile.show_user_profile, name="user_profile"),

    url(r'^$', index.show_index, name='index'),
]
