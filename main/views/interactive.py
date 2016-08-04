from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404, JsonResponse

from main.utils import get_project, check_view_permission

from sendfile import sendfile
import os

@login_required
def show_interactive(request, username, project_name):
    project = get_project(username, project_name)
    if not check_view_permission(project, request.user):
        raise Http404

    return render(request, 'interactive.html', {'project': project})


@login_required
def ajax_handler(request, username, project_name, requested_url):
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
