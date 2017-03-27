from django.contrib.auth.models import Permission, User
from django.db import models
from django.conf import settings

from anvio.dbops import ProfileDatabase, TablesForCollections, TablesForStates, update_description_in_db
from anvio.ccollections import Collections
from anvio import interactive

import random
import argparse
import shutil
import os

def generate_random_pk():
    return random.SystemRandom().getrandbits(32)

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    secret = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    state_autoload = models.CharField(max_length=100, default='default')
    collection_autoload = models.CharField(max_length=100, default='default')

    num_leaves = models.IntegerField(default=0)
    num_layers = models.IntegerField(default=0)

    def __str__(self):
        return 'Project ' + str(self.name) + ' (Created By: ' + str(self.user) + ')'

    def get_path(self):
        return os.path.join(settings.USER_DATA_DIR, self.user.username, self.secret)

    def get_file_path(self, filename, default=None, dont_check_exists=False):
        full_path = os.path.join(self.get_path(), filename)
        
        if dont_check_exists:
            return full_path

        if os.path.exists(full_path):
            return full_path
        
        return default

    def delete_project_path(self):
        shutil.rmtree(self.get_path())

    def create_project_path(self):
        os.makedirs(self.get_path())

    def get_interactive(self, read_only=True):
        args = argparse.Namespace()
        args.read_only = read_only
        args.manual_mode = True

        args.profile_db             = self.get_file_path('profile.db', dont_check_exists=True)
        args.tree                   = self.get_file_path('treeFile'  , default=None)
        args.view_data              = self.get_file_path('dataFile'  , default=None)
        args.fasta_file             = self.get_file_path('fastaFile' , default=None)
        args.samples_information_db = self.get_file_path('samples.db', default=None)
        
        return interactive.InputHandler(args)

class ProjectLink(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    link = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

class Team(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, default=generate_random_pk, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return 'Team ' + str(self.name) + ' (Leader: ' + str(self.owner) + ')'

class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + ' member of ' + str(self.team)

class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    can_write = models.BooleanField(default=False)

    def __str__(self):
        return str(self.project) + ' shared with ' + str(self.team)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    institution = models.CharField(max_length=100, blank=True, null=True)
    orcid = models.CharField(max_length=100, blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username + "'s profile"

class FeedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    teamuser = models.ForeignKey(TeamUser, on_delete=models.CASCADE, blank=True, null=True)
    projectteam = models.ForeignKey(ProjectTeam, on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
