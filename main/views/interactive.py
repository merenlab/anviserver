from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponse

from main.utils import get_project, check_view_permission, check_write_permission

from anvio.utils import get_names_order_from_newick_tree

import zipfile
import hashlib
import json
import os
import io

def show_interactive(request, username, project_name):
    project = get_project(username, project_name)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    return render(request, 'interactive.html', {'project': project, 'view_key': view_key})


def download_zip(request, username, project_name):
    project = get_project(username, project_name)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for f in os.listdir(project.get_path()):
            backup_zip.write(os.path.join(project.get_path(), f), f)

    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=%s' % project.name + ".zip"
    response['Content-Length'] = zip_io.tell()
    return response


def ajax_handler(request, username, project_name, view_key, requested_url):
    if not request.is_ajax():
        raise Http404

    project = get_project(username, project_name)
    if not check_view_permission(project, request.user, view_key):
        raise Http404

    project_path = project.get_path()

    if requested_url.startswith('data/init'):
        return JsonResponse({"title": project.name,
                             "description": (project.get_description()),
                             "clusterings": ('treeData', {'treeData': ''}),
                             "views": ('single', {'single': ''}),
                             "contigLengths": {},
                             "mode": "server",
                             "readOnly": not check_write_permission(project, request.user),
                             "binPrefix": "Bin_",
                             "sessionId": 1,
                             "samplesOrder": {},
                             "sampleInformation": {},
                             "sampleInformationDefaultLayerOrder": {},
                             "stateAutoload": None,
                             "collectionAutoload": None,
                             "noPing": True,
                             "inspectionAvailable": False,
                             "sequencesAvailable": False})

    elif requested_url.startswith('tree/'):
        return HttpResponse(open(os.path.join(project_path, 'treeFile')), content_type='text/plain')

    elif requested_url.startswith('data/view/'):
        
        # If data file exists convert tab separated file to json and return.
        if os.path.exists(os.path.join(project_path, 'dataFile')):
            data = []
            with open(os.path.join(project_path, 'dataFile'), 'r') as f:
                for line in f:
                    data.append(line.replace('\n', '').split('\t'))

        # If data file does not exists, open newick tree generate dummy data file using leaf labels.
        else:
            data = [['contigs', 'names']]
            for leaf_name in get_names_order_from_newick_tree(os.path.join(project_path, 'treeFile'), reverse=True):
                data.append([leaf_name, leaf_name])

        return JsonResponse(data, safe=False)

    elif requested_url.startswith('data/collections'):
        return JsonResponse(project.get_collections().collections_dict, safe=False)

    elif requested_url.startswith('data/collection/'):
        return JsonResponse(project.get_collection(requested_url.split('/')[-1]), safe=False)

    elif requested_url.startswith('store_collection'):
        if not check_write_permission(project, request.user):
            raise Http404

        source = request.POST.get('source')
        data = json.loads(request.POST.get('data'))
        colors = json.loads(request.POST.get('colors'))

        return JsonResponse(project.store_collection(source, data, colors), safe=False)

    elif requested_url.startswith('store_description'):
        if not check_write_permission(project, request.user):
            raise Http404

        description = request.POST.get('description')
        project.set_description(description)
        return JsonResponse(None, safe=False)

    elif requested_url.startswith('state/all'):
        return JsonResponse(project.get_states(), safe=False)

    elif requested_url.startswith('state/get'):
        name = request.POST.get('name')
        states = project.get_states()
        if name in states:
            return JsonResponse(states[name]['content'], safe=False)
        else:
            return JsonResponse(None, safe=False)

    elif requested_url.startswith('state/save'):
        if not check_write_permission(project, request.user):
            raise Http404

        name = request.POST.get('name')
        content = request.POST.get('content')

        return JsonResponse(project.store_state(name, content), safe=False)

    elif requested_url.startswith('project'):
        content = {
            'project_name': project.name,
            'username': project.user.username,
            'user_email_hash': hashlib.md5(project.user.email.encode('utf-8')).hexdigest()
        }
        return JsonResponse(content, safe=False)