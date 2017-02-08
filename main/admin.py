from django.contrib import admin
from .models import Project, Team, ProjectTeam, TeamUser

admin.site.register(Project)
admin.site.register(ProjectTeam)
admin.site.register(Team)
admin.site.register(TeamUser)



