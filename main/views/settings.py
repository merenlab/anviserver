from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render

from main.forms import SettingsForm

@login_required
def show_settings(request):
    context = {}
    user = request.user
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            user.userprofile.fullname = form.cleaned_data['fullname']
            user.userprofile.institution = form.cleaned_data['institution']
            user.userprofile.orcid = form.cleaned_data['orcid']
            user.userprofile.save()

            context['update_successfull'] = True
    else:
        form = SettingsForm(None, 
            initial={
                'fullname': user.userprofile.fullname,
                'institution': user.userprofile.institution,
                'orcid': user.userprofile.orcid
            })

    context['form'] = form
    return render(request, 'settings.html', context)
