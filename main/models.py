from django.contrib.auth.models import Permission, User
from django.db import models
from django.conf import settings
import os

class Project(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    hasData = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' - ' + self.name

    def get_path(self):
    	return os.path.join(settings.USER_DATA_DIR, self.user.username, self.name)

