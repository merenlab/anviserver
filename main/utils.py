from main.models import Project, ProjectLink, ProjectTeam, Team
from django.http import Http404
from django.shortcuts import get_object_or_404

import os

def check_view_permission(project, user, view_key):
    if project.is_public:
        return True

    if project.user == user:
        return True

    if ProjectLink.objects.filter(project=project, link=view_key):
        return True

    project_teams = set(Team.objects.filter(projectteam__project=project).values_list('id', flat=True))
    user_teams = set(Team.objects.filter(teamuser__user=user).values_list('id', flat=True))

    if len(project_teams & user_teams) > 0:
        return True

    return False


def check_write_permission(project, user):
    if user.is_anonymous():
        return False

    if project.user == user:
        return True

    project_teams = set(Team.objects.filter(projectteam__project=project, projectteam__can_write=True).values_list('id', flat=True))
    user_teams = set(Team.objects.filter(teamuser__user=user).values_list('id', flat=True))

    if len(project_teams & user_teams) > 0:
        return True

    return False

def get_project(username, project_slug):
    return get_object_or_404(Project, user__username=username, slug=project_slug)

def put_project_file(project_path, file_name, content):
    with open(os.path.join(project_path, file_name), 'wb+') as destination:
        for chunk in content.chunks():
            destination.write(chunk)

class MockBottleResponse():
    def set_header(self, key, value):
        pass

class MockBottleRequest():
    def __init__(self, django_request=None):
        #self.forms = Forms()
        self.forms = {}

        if django_request:
            for key in django_request.POST:
                self.forms[key] = django_request.POST[key]