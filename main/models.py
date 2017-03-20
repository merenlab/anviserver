from django.contrib.auth.models import Permission, User
from django.db import models
from django.conf import settings

from anvio.dbops import ProfileDatabase, TablesForCollections, TablesForStates, update_description_in_db
from anvio.ccollections import Collections

import random
import shutil
import os

def generate_random_pk():
    return random.SystemRandom().getrandbits(32)

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    secret = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    state_autoload = models.CharField(max_length=100, default='default')
    collection_autoload = models.CharField(max_length=100, default='default')

    num_leaves = models.IntegerField(default=0)
    num_layers = models.IntegerField(default=0)

    def __str__(self):
        return 'Project ' + str(self.name) + ' (Created By: ' + str(self.user) + ')'

    def get_path(self):
        return os.path.join(settings.USER_DATA_DIR, self.user.username, self.secret, self.name)

    def delete_project_path(self):
        shutil.rmtree(os.path.join(settings.USER_DATA_DIR, self.user.username, self.secret))

    def get_profile_path(self):
        return os.path.join(self.get_path(), 'PROFILE.db')

    def get_profile_db(self):
        return ProfileDatabase(self.get_profile_path(), quiet=True)

    def create_profile_db(self, desc):
        profile_db = self.get_profile_db()
        profile_db.create({'db_type': 'profile', 'merged': True, 'contigs_db_hash': None, 'samples': '', 'description': desc})

    def get_description(self):
        return self.get_profile_db().meta['description']

    def set_description(self, description):
        update_description_in_db(self.get_profile_path(), description)

    def get_collections(self):
        collections = Collections()
        collections.populate_collections_dict(self.get_profile_path())
        return collections

    def get_states(self):
        return TablesForStates(self.get_profile_path()).states

    def get_states_count(self):
        return len(TablesForStates(self.get_profile_path()).states)

    def store_state(self, name, content):
        try:
            TablesForStates(self.get_profile_path()).store_state(name, content)
            return {'status_code': '1'}
        except:
            return {'status_code': '0'}

    def get_collection_count(self):
        return len(self.get_collections().collections_dict)

    def get_collection(self, collection_name):
        collections = self.get_collections()
        collection_dict = collections.get_collection_dict(collection_name)
        bins_info_dict = collections.get_bins_info_dict(collection_name)

        colors_dict = {}
        for bin_name in bins_info_dict:
            colors_dict[bin_name] = bins_info_dict[bin_name]['html_color']

        return {'data': collection_dict, 'colors': colors_dict}

    def store_collection(self, source, data, colors):
        if not len(source):
            return "Error: Collection name cannot be empty."

        num_splits = sum(len(l) for l in list(data.values()))
        if not num_splits:
            return "Error: There are no selections to store (you haven't selected anything)."

        bins_info_dict = {}
        for bin_name in data:
            bins_info_dict[bin_name] = {'html_color': colors[bin_name], 'source': "anvi-interactive"}

        collections = TablesForCollections(self.get_profile_path())
        collections.append(source, data, bins_info_dict)

        msg = "New collection '%s' with %d bin%s been stored." % (source, len(data), 's have' if len(data) > 1 else ' has')
        return msg

class ProjectLink(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    link = models.CharField(max_length=16)
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
    institution = models.CharField(max_length=100)
    orcid = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username + "'s profile"

class FeedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    teamuser = models.ForeignKey(TeamUser, on_delete=models.CASCADE, blank=True, null=True)
    projectteam = models.ForeignKey(ProjectTeam, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
