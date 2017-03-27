from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse

from main.models import Project, Team, TeamUser, ProjectTeam, ProjectLink
from django.contrib.auth.models import Permission, User

from main.utils import get_project, put_project_file
from anvio.utils import get_names_order_from_newick_tree
from anvio import dbops

import shutil
import os

@login_required
def list_projects(request):
    action = request.POST.get('action')

    if action == 'delete':
        project = get_project(request.user.username, request.POST.get('name'))

        if project:
            project.delete_project_path()
            project.delete()

    context = {
        'projects': Project.objects.filter(user=request.user),
    }
    return render(request, 'projects/list.html', context)

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

    if action == 'generate_link':
        newlink = ProjectLink(project=project, link=get_random_string(length=16))
        newlink.save()
        context = {
            'status': 'ok'
        }
        return JsonResponse(context)

    if action == 'delete_link':
        link = ProjectLink.objects.filter(project=project, link=request.POST.get('link'))
        if link:
            link.delete()

        context = {
            'status': 'ok'
        }
        return JsonResponse(context)

    if action == 'set_public':
        project.is_public = True if request.POST.get('permission') == 'true' else False
        project.save(update_fields=["is_public"])
        context = {
            'status': 'ok'
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
        try:
            name = slugify(request.POST.get('name')).replace('-', '_')
            project = Project(name=name,
                              user=request.user,
                              secret=get_random_string(length=32))

            project.create_project_path()

            fileTypes = ['tree.txt', 'data.txt', 'fasta.fa', 'samples-order.txt', 'samples-info.txt']

            for fileType in fileTypes:
                if fileType in request.FILES:
                    put_project_file(project.get_path(), fileType, request.FILES[fileType])

            samples_info = project.get_file_path('samples-order.txt', default=None)
            samples_order = project.get_file_path('samples-info.txt', default=None)
            
            if samples_info or samples_order:
                s = dbops.SamplesInformationDatabase(project.get_file_path('samples.db', dont_check_exists=True), quiet=True)
                s.create(samples_order, samples_info)

            interactive = project.get_interactive()
            project.save()
            return JsonResponse({'status': 0})
        except Exception as e:
            project.delete_project_path()
            return JsonResponse({
                    'status': 1,
                    'message': str(e.clear_text()) if 'clear_text' in dir(e) else str(e)
                    })

        # if 'treeFile' in request.FILES:
        #     project.num_leaves = len(get_names_order_from_newick_tree(os.path.join(project_path, 'treeFile')))

        # if 'dataFile' in request.FILES:
        #     project.num_layers = len(open(os.path.join(project_path, 'dataFile')).readline().rstrip().split('\t')) - 1

        # project.create_profile_db(request.POST.get('desc'))
        #project.save()

    return render(request, 'projects/new.html')
