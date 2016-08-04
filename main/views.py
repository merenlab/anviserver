from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse, Http404
from .models import Project
from sendfile import sendfile
import argparse
import shutil
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

@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def list_projects(request):
    return render(request, 'projects_list.html', {'projects': Project.objects.filter(user=request.user)})

@login_required
@require_POST
def delete_project(request):
    project = get_project(request.user.username, request.POST['name'])
    if project:
        shutil.rmtree(project.get_path())
        project.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})

@login_required
def new_project(request):
    if request.method == "POST":
        name = slugify(request.POST['name']).replace('-', '_')
        project = Project(name=name, user=request.user, desc=request.POST['desc'])

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

    return render(request, 'projects_new.html')


@login_required
def show_project(request, username, project_name):
    project = get_project(username, project_name)
    if not check_view_permission(project, request.user):
        raise Http404

    return render(request, 'interactive.html', {'project': project})


@login_required
def ajax_dispatcher(request, username, project_name, requested_url):
    project = get_project(username, project_name)
    if not check_view_permission(project, request.user):
        raise Http404

    project_path = project.get_path()

    if requested_url.startswith('data/init'):
        return JsonResponse({
            "title": project_name,
            "clusterings": ('treeData', {'treeData': ''}),
            "views": ('single', {'single': ''}),
            "contigLengths": {},
            "mode": "server",
            "readOnly": True,
            "binPrefix": "Bin_",
            "sessionId": 1,
            "samplesOrder": {},
            "sampleInformation": {},
            "sampleInformationDefaultLayerOrder": {},
            "stateAutoload": None,
            "noPing": True,
            "inspectionAvailable": False,
            "sequencesAvailable": False
        })

    elif requested_url.startswith('tree/'):
        return sendfile(request, os.path.join(project_path, 'treeFile'))

    elif requested_url.startswith('data/view/'):
        return sendfile(request, os.path.join(project_path, 'dataFile'))
