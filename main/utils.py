from main.models import Project
from django.http import Http404
from django.shortcuts import get_object_or_404

import os

def check_view_permission(project, user, view_key):
    if project.view_key == view_key:
        return True

    if project.user == user:
        return True

    return False


def check_write_permission(project, user):
    if project.user == user:
        return True

    return False

def get_project(username, project_name):
    return get_object_or_404(Project, user__username=username, name=project_name)

def put_project_file(project_path, file_name, content):
    with open(os.path.join(project_path, file_name), 'wb+') as destination:
        for chunk in content.chunks():
            destination.write(chunk)
