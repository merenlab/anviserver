from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponse

from main.utils import get_project, check_view_permission, check_write_permission
from main.templatetags.gravatar import gravatar
import main.utils as utils

from anvio.bottleroutes import BottleApplication

import zipfile
import hashlib
import json
import os
import io

def show_interactive(request, username, project_slug):
    project = get_project(username, project_slug)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    return render(request, 'interactive.html', {'project': project, 'view_key': view_key})

def show_inspect(request, username, project_slug, inspection_type):
    project = get_project(username, project_slug)

    view_key = request.GET.get('view_key')
    if view_key is None:
        view_key = "no_view_key"

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    html_page = ''
    if inspection_type == 'inspect':
        html_page = 'charts'
    elif inspection_type == 'proteinclusters':
        html_page = 'proteinclusters'

    return render(request, 'inspect.html', {'project': project, 
                                           'view_key': view_key,
                                           'id': request.GET.get('id'),
                                           'html_page': html_page
                                           })

def download_zip(request, username, project_slug):
    project = get_project(username, project_slug)

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
    response['Content-Disposition'] = 'attachment; filename=%s' % project.slug + ".zip"
    response['Content-Length'] = zip_io.tell()
    return response


def ajax_handler(request, username, project_slug, view_key, requested_url):
    if not request.is_ajax():
        raise Http404

    project = get_project(username, project_slug)

    if not check_view_permission(project, request.user, view_key):
        raise Http404

    read_only = not check_write_permission(project, request.user)

    bottle_request = utils.MockBottleRequest(django_request=request)
    bottle_response = utils.MockBottleResponse()

    interactive = project.get_interactive(read_only=read_only)
    bottleapp = BottleApplication(interactive, interactive.args, bottle_request, bottle_response)

    if requested_url.startswith('data/init'):
        download_zip_url = reverse('download_zip', args=[username, project_slug])
        if view_key != 'no_view_key':
            download_zip_url += '?view_key=' + view_key

        return JsonResponse({ "title": project.name,
                             "description": (interactive.p_meta['description']),
                             "item_orders": (interactive.p_meta['default_item_order'], interactive.p_meta['item_orders']),
                             "views": (interactive.default_view, dict(list(zip(list(interactive.views.keys()), list(interactive.views.keys()))))),
                             "contigLengths": dict([tuple((c, interactive.splits_basic_info[c]['length']),) for c in interactive.splits_basic_info]),
                             "defaultView": interactive.views[interactive.default_view],
                             "server_mode": True,
                             "mode": interactive.mode,
                             "readOnly": interactive.read_only, 
                             "binPrefix": "Bin_",
                             "sessionId": 0,
                             "samplesOrder": interactive.samples_order_dict,
                             "sampleInformation": interactive.samples_information_dict,
                             "sampleInformationDefaultLayerOrder": interactive.samples_information_default_layer_order,
                             "stateAutoload": interactive.state_autoload,
                             "collectionAutoload": interactive.collection_autoload,
                             "noPing": True,
                             "inspectionAvailable": interactive.auxiliary_profile_data_available,
                             "sequencesAvailable": True if interactive.split_sequences else False,
                             "project": {
                                'username': project.user.username,
                                'fullname': project.user.userprofile.fullname if project.user.userprofile.fullname else project.user.username,
                                'user_avatar': gravatar(project.user.email),
                                'download_zip_url': download_zip_url
                                }
                            })

    elif requested_url.startswith('data/view/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_view_data(param), content_type='application/json')

    elif requested_url.startswith('tree/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_items_ordering(param), content_type='application/json')

    elif requested_url.startswith('data/collections'):
        return HttpResponse(bottleapp.get_collections(), content_type='application/json')

    elif requested_url.startswith('data/collection/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_collection_dict(param), content_type='application/json')

    elif requested_url.startswith('store_collection'):
        if not check_write_permission(project, request.user):
            raise Http404

        ret = HttpResponse(bottleapp.store_collections_dict(), content_type='application/json')
        project.synchronize_num_collections(save=True)
        return ret

    elif requested_url.startswith('data/contig/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_sequence_for_split(param), content_type='application/json')

    elif requested_url.startswith('store_description'):
        if not check_write_permission(project, request.user):
            raise Http404

        return HttpResponse(bottleapp.store_description(), content_type='application/json')

    elif requested_url.startswith('state/all'):
        return HttpResponse(bottleapp.state_all(), content_type='application/json')

    elif requested_url.startswith('state/get'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_state(param), content_type='application/json')

    elif requested_url.startswith('state/save'):
        if not check_write_permission(project, request.user):
            raise Http404

        param = requested_url.split('/')[-1]
        ret = HttpResponse(bottleapp.save_state(param), content_type='application/json')
        project.synchronize_num_states(save=True)
        return ret

    elif requested_url.startswith('data/charts/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.charts(param), content_type='application/json')

    elif requested_url.startswith('data/proteinclusters/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.inspect_pc(param), content_type='application/json')

    elif requested_url.startswith('data/get_AA_sequences_for_PC/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_AA_sequences_for_PC(param), content_type='application/json')

    elif requested_url.startswith('data/news'):
        return HttpResponse(bottleapp.get_news(), content_type='application/json')

    elif requested_url.startswith('data/gene'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_sequence_for_gene_call(param), content_type='application/json')

    elif requested_url.startswith('data/completeness'):
        return HttpResponse(bottleapp.completeness(), content_type='application/json')

    raise Http404

