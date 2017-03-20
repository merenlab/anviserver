from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from main.models import Project

def show_user_profile(request, username):
    user = get_object_or_404(User, username=username)

    context = {
    	'profile_user': user,
        'projects': Project.objects.filter(user=user, is_public=True),
    }
    
    return render(request, 'profile.html', context)