from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from main.models import Project, Team, ProjectTeam, TeamUser, ProjectLink, UserProfile, FeedItem, OldLinks

admin.site.register(Project)
admin.site.register(ProjectTeam)
admin.site.register(Team)
admin.site.register(TeamUser)
admin.site.register(ProjectLink)
admin.site.register(FeedItem)
admin.site.register(OldLinks)

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    UserAdmin.list_display = ('email', 'is_active', 'date_joined', 'is_staff')
    inlines = [ UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)
