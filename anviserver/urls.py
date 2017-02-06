from django.conf.urls import url, include
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from main.views import projects, index, interactive, teams

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationFormUniqueEmail), name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^projects/new', projects.new_project, name="projects_new"),
    url(r'^projects/edit/(?P<project_name>\w+)/', projects.edit_project, name="projects_edit"),
    url(r'^projects/share/(?P<project_name>\w+)/', projects.share_project, name="projects_share"),
    url(r'^projects/shared', projects.list_shared, name="shared"),
    url(r'^projects/', projects.list_projects, name="projects"),

    url(r'^teams/', teams.list_teams, name="teams"),

    url(r'^ajax/(?P<username>\w+)/(?P<project_name>\w+)/(?P<view_key>\w+)/(?P<requested_url>.*)', interactive.ajax_handler),
    url(r'^(?P<username>\w+)/(?P<project_name>\w+)/', interactive.show_interactive, name="show_interactive"),
    url(r'^$', index.show_index, name='index'),
]
