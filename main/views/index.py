from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def show_index(request):
    return render(request, 'index.html')

def show_error_page(request):
	return render(request, 'error.html')
