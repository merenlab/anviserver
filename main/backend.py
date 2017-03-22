from main.models import UserProfile, TeamUser, ProjectTeam, FeedItem, Project
from main.forms import UserRegForm
from registration.signals import user_registered
from django.db.models.signals import post_save

def user_created(sender, user, request, **kwargs):
    form = UserRegForm(request.POST)
    data = UserProfile(user=user)
    data.institution = form.data["institution"]
    data.orcid = form.data["orcid"]
    data.fullname = form.data["fullname"]

    data.save()

user_registered.connect(user_created)


def object_created(sender, instance, created, **kwargs):
    if created == False:
        return

    if isinstance(instance, TeamUser):
        for membership in instance.team.teamuser_set.all():
            feeditem = FeedItem()
            feeditem.user = membership.user
            feeditem.teamuser = instance
            feeditem.save()

    elif isinstance(instance, ProjectTeam):
        for membership in instance.team.teamuser_set.all():
            feeditem = FeedItem()
            feeditem.user = membership.user
            feeditem.projectteam = instance
            feeditem.save()

    elif isinstance(instance, Project):
        feeditem = FeedItem()
        feeditem.user = instance.user
        feeditem.project = instance
        feeditem.save()

post_save.connect(object_created)