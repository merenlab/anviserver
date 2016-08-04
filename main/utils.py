from main.models import Project

import os

def check_view_permission(project, user):
    if project.user == user:
        return True

    return False


def check_write_permission(project, user):
    if project.user == user:
        return True

    return False


def get_project(username, project_name):
    return Project.objects.get(user__username=username, name=project_name)


def put_project_file(project_path, file_name, content):
    with open(os.path.join(project_path, file_name), 'wb+') as destination:
        for chunk in content.chunks():
            destination.write(chunk)
