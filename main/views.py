from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse, Http404
from .models import Project
from sendfile import sendfile
import argparse
import shutil
import os