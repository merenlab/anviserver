from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.shortcuts import redirect
from django.http import Http404

from main.models import Project, OldLinks, ProjectLink

def sanitize_username(username):
    if '@' in username:
        username = username.split('@')[0]

    username = slugify(username).replace('-', '_')

    return username

def redirect_view(request, access_type, username, share_name):
    link = None

    if access_type == 'public':
        link = OldLinks.objects.filter(name=share_name, user=sanitize_username(username), is_public=True)
    else:
        link = OldLinks.objects.filter(name=share_name, user=sanitize_username(username), is_public=False, token=request.GET.get('code'))


    if len(link) > 0:
        link = link[0]
        return redirect(reverse('show_interactive', kwargs={'username': link.user, 'project_slug': link.project.slug}) + '?view_key=' + link.token)
    else:
        raise Http404
