from django.contrib.auth.models import Permission, User
from django.db import models
from django.conf import settings

import random
import os

def generate_random_pk():
    return random.SystemRandom().getrandbits(32)

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    view_key = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Project ' + str(self.name) + ' (Created By: ' + str(self.user) + ')'

    def get_path(self):
        return os.path.join(settings.USER_DATA_DIR, self.user.username, self.name)


class Team(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, default=generate_random_pk, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return 'Team ' + str(self.name) + ' (Leader: ' + str(self.owner) + ')'


class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return str(self.user) + ' member of ' + str(self.team)

class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    can_write = models.BooleanField(default=False)

    def __unicode__(self):
        return str(elf.project) + ' shared with ' + str(self.team)