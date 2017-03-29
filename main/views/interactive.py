from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponse

from main.utils import get_project, check_view_permission, check_write_permission
import main.utils as utils

import anvio.bottleroutes as routes

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

    read_only = not check_write_permission(project, request.user)
    
    d = project.get_interactive(read_only=read_only)

    bottle_request = utils.MockBottleRequest(django_request=request)
    bottle_response = utils.MockBottleResponse()

    if requested_url.startswith('data/init'):
        return JsonResponse({ "title": project.name,
                             "description": (d.p_meta['description']),
                             "clusterings": (d.p_meta['default_clustering'], d.p_meta['clusterings']),
                             "views": (d.default_view, dict(list(zip(list(d.views.keys()), list(d.views.keys()))))),
                             "contigLengths": dict([tuple((c, d.splits_basic_info[c]['length']),) for c in d.splits_basic_info]),
                             "defaultView": d.views[d.default_view],
                             "mode": 'server',
                             "readOnly": d.read_only, 
                             "binPrefix": "Bin_",
                             "sessionId": 0,
                             "samplesOrder": d.samples_order_dict,
                             "sampleInformation": d.samples_information_dict,
                             "sampleInformationDefaultLayerOrder": d.samples_information_default_layer_order,
                             "stateAutoload": d.state_autoload,
                             "collectionAutoload": d.collection_autoload,
                             "noPing": True,
                             "inspectionAvailable": d.auxiliary_profile_data_available,
                             "sequencesAvailable": True if d.split_sequences else False,
                             "project": {
                                'username': project.user.username,
                                'fullname': project.user.userprofile.fullname if project.user.userprofile.fullname else project.user.username
                                }
                            })

    elif requested_url.startswith('data/view/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(routes.get_view_data(d, bottle_request, bottle_response, param), content_type='application/json')

    elif requested_url.startswith('tree/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(routes.get_items_ordering(d, bottle_request, bottle_response, param), content_type='application/json')

    elif requested_url.startswith('data/collections'):
        return HttpResponse(routes.get_collections(d, bottle_request, bottle_response), content_type='application/json')

    elif requested_url.startswith('data/collection/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(routes.get_collection_dict(d, bottle_request, bottle_response, param), content_type='application/json')

    elif requested_url.startswith('store_collection'):
        if not check_write_permission(project, request.user):
            raise Http404

        ret = HttpResponse(routes.store_collections_dict(d, bottle_request, bottle_response), content_type='application/json')
        project.synchronize_num_collections(save=True)
        return ret

    elif requested_url.startswith('data/contig/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(routes.get_sequence_for_split(d, bottle_request, bottle_response, param), content_type='application/json')

    elif requested_url.startswith('store_description'):
        if not check_write_permission(project, request.user):
            raise Http404

        return HttpResponse(routes.store_description(d, bottle_request, bottle_response), content_type='application/json')

    elif requested_url.startswith('state/all'):
        return HttpResponse(routes.state_all(d, bottle_response), content_type='application/json')

    elif requested_url.startswith('state/get'):
        return HttpResponse(routes.get_state(d, bottle_request, bottle_response), content_type='application/json')

    elif requested_url.startswith('state/save'):
        if not check_write_permission(project, request.user):
            raise Http404

        ret = HttpResponse(routes.save_state(d, bottle_request, bottle_response), content_type='application/json')
        project.synchronize_num_states(save=True)
        return ret