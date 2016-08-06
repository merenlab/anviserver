from django.contrib.auth.models import Permission, User
from django.db import models
from django.conf import settings
import os

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    view_key = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' - ' + self.name

    def get_path(self):
        return os.path.join(settings.USER_DATA_DIR, self.user.username, self.name)

class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    email = models.CharField(max_length=250, default="")
    can_write = models.BooleanField(default=False)

    def __str__(self):
        return self.project.user.username + ' - ' + self.project.name + ' - ' + self.email + ' - Write:' + str(self.can_write)

class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    can_write = models.BooleanField(default=False)

