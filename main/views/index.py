from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import FeedItem

def show_index(request):
    if request.user.is_authenticated():
        context = {
            'feeditems': FeedItem.objects.filter(user=request.user).order_by('-id')[:10]
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')
