from django.conf.urls import re_path, include, handler400, handler403, handler404, handler500
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from main.views import projects, index, interactive, teams, profile, redirect, settings
from main.forms import UserRegForm
from main import backend

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^accounts/settings/$', settings.show_settings, name="user_settings"),
    re_path(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegForm), {'backend': 'registration.backends.default.DefaultBackend'}, name='registration_register'),
    re_path(r'^accounts/', include('registration.backends.default.urls')),


    re_path(r'^(?P<access_type>public|private)/(?P<username>\w+)/(?P<share_name>\w+)', redirect.redirect_view, name="redirect_view"),

    re_path(r'^projects/new', projects.new_project, name="projects_new"),
    re_path(r'^projects/details/(?P<project_slug>\w+)', projects.details_project, name="projects_details"),
    re_path(r'^projects/share/(?P<project_slug>\w+)', projects.share_project, name="projects_share"),
    re_path(r'^projects', projects.list_projects, name="projects"),

    re_path(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/members', teams.list_members, name="teams_members"),
    re_path(r'^teams/(?P<team_id>\w+)/(?P<team_name>\w+)/projects', teams.list_projects, name="teams_projects"),
    re_path(r'^teams', teams.list_teams, name="teams"),

    re_path(r'^p/(?P<short_link_key>\w+)', interactive.short_link_redirect, name='short_link_redirect'),
    re_path(r'^ajax/(?P<username>\w+)/(?P<project_slug>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler),
    re_path(r'^(?P<username>\w+)/(?P<project_slug>\w+)/download', interactive.download_zip, name="download_zip"),
    re_path(r'^(?P<username>\w+)/(?P<project_slug>\w+)/(?P<inspection_type>\w+)', interactive.show_inspect, name="show_inspect"),
    re_path(r'^(?P<username>\w+)/(?P<project_slug>\w+)', interactive.show_interactive, name="show_interactive"),

    re_path(r'^(?P<username>\w+)', profile.show_user_profile, name="user_profile"),

    re_path(r'^$', index.show_index, name='index'),
]

handler400 = index.Errorhandler404
handler403 = index.Errorhandler404
handler404 = index.Errorhandler404
handler500 = index.Errorhandler500
