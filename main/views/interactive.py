from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse

from main.utils import get_project, check_view_permission, check_write_permission
from main.models import Project
from main.templatetags.gravatar import gravatar
import main.utils as utils

from anvio.bottleroutes import BottleApplication

import zipfile
import hashlib
import json
import os
import io


def short_link_redirect(request, short_link_key):
    project = get_object_or_404(Project, short_link_key=short_link_key)

    if not project.is_public:
        raise Http404

    return redirect('show_interactive', username=project.user.username, project_slug=project.slug)


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
    elif inspection_type == 'geneclusters':
        html_page = 'geneclusters'

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

    interactive = None
    
    if not requested_url.startswith('data/news'):
        interactive = project.get_interactive(read_only=read_only)

    bottleapp = BottleApplication(interactive, bottle_request, bottle_response)

    if requested_url.startswith('data/init'):
        download_zip_url = reverse('download_zip', args=[username, project_slug])
        if view_key != 'no_view_key':
            download_zip_url += '?view_key=' + view_key

        default_view = interactive.default_view
        default_order = interactive.p_meta['default_item_order']
        autodraw = False
        state_dict = None

        if interactive.state_autoload:
            state_dict = json.loads(interactive.states_table.states[interactive.state_autoload]['content'])

            if state_dict['current-view'] in interactive.views:
                default_view = state_dict['current-view']

            if state_dict['order-by'] in interactive.p_meta['item_orders']:
                default_order = state_dict['order-by']

            autodraw = True

        collection_dict = None
        if interactive.collection_autoload:
            collection_dict = json.loads(bottleapp.get_collection_dict(interactive.collection_autoload))

        functions_sources = []
        if interactive.mode == 'full' or interactive.mode == 'gene':
            functions_sources = list(interactive.gene_function_call_sources)
        elif interactive.mode == 'pan':
            functions_sources = list(interactive.gene_clusters_function_sources)

        return JsonResponse({ "title": project.name,
                             "description": interactive.p_meta['description'],
                             "item_orders": (default_order, interactive.p_meta['item_orders'][default_order], list(interactive.p_meta['item_orders'].keys())),
                             "views": (default_view, interactive.views[default_view], list(interactive.views.keys())),
                             "item_lengths": dict([tuple((c, interactive.splits_basic_info[c]['length']),) for c in interactive.splits_basic_info]),
                             "server_mode": True,
                             "mode": interactive.mode,
                             "read_only": interactive.read_only, 
                             "bin_prefix": "Bin_",
                             "session_id": 0,
                             "layers_order": interactive.layers_order_data_dict,
                             "layers_information": interactive.layers_additional_data_dict,
                             "layers_information_default_order": interactive.layers_additional_data_keys,
                             "check_background_process": False,
                             "autodraw": autodraw,
                             "inspection_available": interactive.auxiliary_profile_data_available,
                             "sequences_available": True if interactive.split_sequences else False,
                             "functions_initialized": interactive.gene_function_calls_initiated,
                             "functions_sources": functions_sources,
                             "state": (interactive.state_autoload, state_dict),
                             "collection": collection_dict,
                             "samples": interactive.p_meta['samples'] if interactive.mode in ['full', 'refine'] else [],
                             "load_full_state": True,
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
        return HttpResponse(bottleapp.get_items_order(param), content_type='application/json')

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
        order_name = requested_url.split('/')[-2]
        item_name = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.charts(order_name, item_name), content_type='application/json')

    elif requested_url.startswith('data/geneclusters/'):
        order_name = requested_url.split('/')[-2]
        item_name = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.inspect_gene_cluster(order_name, item_name), content_type='application/json')

    elif requested_url.startswith('data/get_AA_sequences_for_gene_cluster/'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_AA_sequences_for_gene_cluster(param), content_type='application/json')

    elif requested_url.startswith('data/news'):
        return HttpResponse(bottleapp.get_news(), content_type='application/json')

    elif requested_url.startswith('data/gene'):
        param = requested_url.split('/')[-1]
        return HttpResponse(bottleapp.get_sequence_for_gene_call(param), content_type='application/json')

    elif requested_url.startswith('data/completeness'):
        return HttpResponse(bottleapp.completeness(), content_type='application/json')

    elif requested_url.startswith('data/reroot_tree'):
        return HttpResponse(bottleapp.reroot_tree(), content_type='application/json')


    raise Http404

