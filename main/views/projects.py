from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.shortcuts import render
from django.http import JsonResponse

from main.models import Project, ProjectUser
from main.utils import get_project, put_project_file

import shutil
import os


@login_required
def list_projects(request):
    context = {
        'projects': Project.objects.filter(user=request.user),
        'shared_with_me': False,
        'page_title': 'My Projects'
    }
    return render(request, 'projects/list.html', context)


@login_required
def list_shared(request):
    context = {
        'projects': Project.objects.filter(projectuser__email__iexact=request.user.email).distinct(),
        'shared_with_me': True,
        'page_title': 'Shared with me'
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

    if request.method == "POST":
        if request.POST.get('action') == 'generate_view_key':
            project.view_key = get_random_string(length=16)
            project.save()
            context = {
                'status': 'ok',
                'view_key': project.view_key
            }
            return JsonResponse(context)

        if request.POST.get('action') == 'share_with_email':
            email = request.POST.get('email') 
            already_shared = ProjectUser.objects.filter(project=project, email__iexact=email)
            if already_shared or not email:
                context = {'status': 'error'}
            else:
                ProjectUser(project=project, email=email).save()
                context = {'status': 'ok'}            
            return JsonResponse(context)

            
        if request.POST.get('action') == 'delete_email':
            email = request.POST.get('email') 
            sharing = ProjectUser.objects.filter(project=project, email__iexact=email)
            if sharing:
                context = {'status': 'ok'}
                sharing.delete()
            else:
                context = {'status': 'error'}            
            return JsonResponse(context)


    context = {
        'project': project,
        'shared_emails': ProjectUser.objects.filter(project=project),
        'teams': Teams.objects.filter(user=request.user),
    }
    return render(request, 'projects/share.html', context)


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
        project = Project(name=name, 
                          user=request.user, 
                          desc=request.POST['desc'],
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
