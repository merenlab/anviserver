import os
import re
import shutil
import argparse
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse, Http404

from main.models import Project, Team, TeamUser, ProjectTeam, ProjectLink
from main.utils import get_project, put_project_file

from anvio import dbops
from anvio.tables import miscdata, collections
from anvio.utils import get_TAB_delimited_file_as_dictionary

@login_required
def list_projects(request):
    action = request.POST.get('action')

    if action == 'delete':
        project = get_project(request.user.username, request.POST.get('slug'))

        if project:
            project.delete_project_path()
            project.delete()
        else:
            raise Http404

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

            if len(slug) < 1:
                raise Exception("Project name should not be empty.")

            project = Project.objects.filter(user=request.user, slug=slug)
            if project:
                if request.POST.get('delete-if-exists'):
                    project[0].delete_project_path()
                    project[0].delete()
                else:
                    raise Exception("Project with same name already exists, please give another name.")

            project = Project(name=name,
                              slug=slug,
                              user=request.user,
                              secret=get_random_string(length=32))

            project.create_project_path()

            fileTypes = ['tree.txt', 'data.txt', 'fasta.fa', 
                         'samples-order.txt', 'samples-info.txt',
                         'additional-layers.txt', 'state.json', 
                         'bins.txt', 'bins-info.txt', 'items-order.txt']

            for fileType in fileTypes:
                if fileType in request.FILES:
                    put_project_file(project.get_path(), fileType, request.FILES[fileType])

            interactive = project.get_interactive()
            profile_db_path = project.get_file_path('profile.db', default=None)

            samples_info = project.get_file_path('samples-info.txt', default=None)
            if samples_info:
                miscdata.MiscDataTableFactory(argparse.Namespace(target_data_table='layers', profile_db=profile_db_path)).populate_from_file(samples_info)

            samples_order = project.get_file_path('samples-order.txt', default=None)
            if samples_order:
                miscdata.MiscDataTableFactory(argparse.Namespace(target_data_table='layer_orders', profile_db=profile_db_path)).populate_from_file(samples_order)


            state_file = project.get_file_path('state.json', default=None)
            if state_file:
                interactive.states_table.store_state('default', open(state_file, 'r').read(), datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
                project.num_states = 1

            bins_file = project.get_file_path('bins.txt', default=None)
            bins_info_file = project.get_file_path('bins-info.txt', default=None)
            if bins_file and bins_info_file:
                collections_table = collections.TablesForCollections(profile_db_path)

                bins = get_TAB_delimited_file_as_dictionary(bins_file, no_header = True, column_names = ['split_id', 'bin_name'])
                bins_info = get_TAB_delimited_file_as_dictionary(bins_info_file, no_header = True, column_names = ['bin_name', 'source', 'html_color'])

                bin_data = {}
                for split_name in bins:
                    bin_name = bins[split_name]['bin_name']
                    if not bin_name in bin_data:
                        bin_data[bin_name] = set([])

                    bin_data[bin_name].add(split_name)

                collections_table.append('default', bin_data, bins_info)
                project.num_collections = 1

            # try to get number of leaves
            try:
                project.num_leaves = len(interactive.displayed_item_names_ordered)
            except:
                project.num_leaves = 0

            # try to get number of layers
            try:
                project.num_layers = len(interactive.views['single'][0]) - 1 # <- -1 because first column is contigs
            except:
                project.num_layers = 0

            # store description
            dbops.update_description_in_db(profile_db_path, request.POST.get('description') or '')

            project.save()
            return JsonResponse({'status': 0})
        except Exception as e:
            try:
                project.delete_project_path()
            except:
                # slug is not unique, so there is no project instance or direcotry created.
                pass

            message = str(e.clear_text()) if 'clear_text' in dir(e) else str(e)

            # trim the full path from exception message, show only file name
            message = re.sub(r"(\'.*\/)(.+?)(\.txt\')", r"'\2'", message)

            return JsonResponse({
                    'status': 1,
                    'message': message
                    })

    return render(request, 'projects/new.html')
