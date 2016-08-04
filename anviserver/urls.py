"""anviserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from main.views import index, list_projects, new_project, ajax_dispatcher, show_project, delete_project

urlpatterns = [
    url(r'^admin/'          , admin.site.urls),
    url(r'^accounts/'       , include('registration.backends.default.urls')),

    url(r'^projects/new'    , new_project     , name="projects_new"),
    url(r'^projects/delete' , delete_project  , name="projects_delete"),
    url(r'^projects/'       , list_projects   , name="projects"),

    url(r'^project/(?P<username>\w+)/(?P<project_name>\w+)/', show_project, name="project"),

    url(r'^ajax/(?P<username>\w+)/(?P<project_name>\w+)/(?P<requested_url>.*)', ajax_dispatcher),
    url(r'^$', index, name='index'),
]