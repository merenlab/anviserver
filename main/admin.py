from django.contrib import admin
from .models import Project, ProjectUser, Team, ProjectTeam, TeamUser

admin.site.register(Project)
admin.site.register(ProjectUser)
admin.site.register(ProjectTeam)
admin.site.register(Team)
admin.site.register(TeamUser)



