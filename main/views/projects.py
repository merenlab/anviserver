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
        project = get_project(request.user.username, request.POST.get('slug'))

        if project:
            project.delete_project_path()
            project.delete()

    context = {
        'projects': Project.objects.filter(user=request.user),
    }
    return render(request, 'projects/list.html', context)

@login_required
def details_project(request, project_slug):
    project = get_project(request.user.username, project_slug)

    files = []
    for f in os.listdir(project.get_path()):
        files.append({'name': f, 'size': os.path.getsize(os.path.join(project.get_path(), f))})

    context = {
        'project': project,
        'project_files': files
    }
    return render(request, 'projects/details.html', context)


@login_required
def share_project(request, project_slug):
    project = get_project(request.user.username, project_slug)
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
            name = request.POST.get('name')
            slug = slugify(name).replace('-', '_')
            project = Project(name=name,
                              slug=slug,
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

            # try to get number of leaves
            try:
                leaves = get_names_order_from_newick_tree(project.get_file_path('tree.txt', default=None))
                project.num_leaves = len(leaves) if leaves != [''] else 0
            except:
                project.num_leaves = 0

            # try to get number of layers
            try:
                project.num_layers = len(interactive.views['single'][0]) - 1 # <- -1 because first column is contigs
            except:
                project.num_layers = 0

            # store description
            dbops.update_description_in_db(project.get_file_path('profile.db', default=None), request.POST.get('description') or '')

            project.save()
            return JsonResponse({'status': 0})
        except Exception as e:
            project.delete_project_path()
            return JsonResponse({
                    'status': 1,
                    'message': str(e.clear_text()) if 'clear_text' in dir(e) else str(e)
                    })

    return render(request, 'projects/new.html')
