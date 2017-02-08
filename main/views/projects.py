from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse

from main.models import Project, Team, TeamUser, ProjectTeam
from main.utils import get_project, put_project_file

import shutil
import os


@login_required
def list_projects(request):
    template = 'projects/list.html'
    action = request.POST.get('action')

    if action == 'delete':
        project = get_project(request.user.username, request.POST.get('name'))

        if project:
            shutil.rmtree(project.get_path())
            project.delete()
            template = '_partial/_list_projects.html'

    context = {
        'projects': Project.objects.filter(user=request.user),
        'page_title': 'My Projects'
    }
    return render(request, template, context)

@login_required
def edit_project(request, project_name):
    project = get_project(request.user.username, project_name)

    files = []
    for f in os.listdir(project.get_path()):
        files.append({'name': f, 'size': os.path.getsize(os.path.join(project.get_path(), f))})

    context = {
        'project': project,
        'project_files': files
    }
    return render(request, 'projects/edit.html', context)


@login_required
def share_project(request, project_name):
    project = get_project(request.user.username, project_name)
    action = request.POST.get('action')

    if action == 'generate_view_key':
        project.view_key = get_random_string(length=16)
        project.save()
        context = {
            'status': 'ok',
            'view_key': project.view_key
        }
        return JsonResponse(context)

    shared_teams = ProjectTeam.objects.filter(project=project)

    if action == 'share_with_team':
        team_id = request.POST.get('team_id')

        if team_id:
            team = Team.objects.get(id=team_id)

            is_member = TeamUser.objects.filter(user=request.user, team=team)
            already_shared = ProjectTeam.objects.filter(project=project, team=team)

            if not already_shared and is_member:
                ProjectTeam(project=project, team=team).save()

        return render(request, '_partial/_shared_team_list.html', {'shared_teams': shared_teams})

    if action == 'delete_team' or action == 'set_team_write_permission':
        team_id = request.POST.get('team_id')

        if team_id:
            team = Team.objects.get(id=team_id)
            sharing = ProjectTeam.objects.get(project=project, team=team)

            if sharing:
                if action == 'delete_team':
                    sharing.delete()
                elif action == 'set_team_write_permission':
                    sharing.can_write = True if request.POST.get('permission') == 'true' else False
                    sharing.save()

        return render(request, '_partial/_shared_team_list.html', {'shared_teams': shared_teams})

    teams = Team.objects.filter(teamuser__user=request.user)

    context = {
        'project': project,
        'shared_teams': shared_teams,
        'teams': teams
    }
    return render(request, 'projects/share.html', context)


@login_required
def new_project(request):
    if request.method == "POST":
        name = slugify(request.POST.get('name')).replace('-', '_')
        project = Project(name=name,
                          user=request.user,
                          desc=request.POST.get('desc'),
                          view_key=get_random_string(length=16))

        project_path = project.get_path()
        try:
            os.makedirs(project_path)
        except:
            pass

        fileTypes = ['treeFile', 'dataFile', 'fastaFile', 'samplesOrderFile', 'samplesInfoFile']

        for fileType in fileTypes:
            if fileType in request.FILES:
                put_project_file(project_path, fileType, request.FILES[fileType])

        project.save()

    return render(request, 'projects/new.html')
