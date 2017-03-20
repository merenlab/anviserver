from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import FeedItem

@login_required
def show_index(request):
    context = {
        'feeditems': FeedItem.objects.filter(user=request.user).order_by('-id')[:10]
    }
    return render(request, 'index.html', context)
