from django.contrib.auth.models import Permission, User
from django.db import models

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    project_hash = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    hasData = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' - ' + self.name


