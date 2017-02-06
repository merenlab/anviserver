from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Team, TeamUser

@login_required
def list_teams(request):
    action = request.POST.get('action')
    teams = Team.objects.filter(teamuser__user=request.user)

    context = {
        'teams': teams,
    }

    if action == 'create_team':
        name = request.POST.get('name')
        if len(name) > 0:
            team = Team(name=name, owner=request.user)
            team.save()

            teamuser = TeamUser(team=team, user=request.user)
            teamuser.save()

        return render(request, '_partial/_list_teams.html', context)

    if action == 'delete_team':
        team_id = request.POST.get('id')
        if team_id:
            team = Team.objects.get(id=team_id)
            if team and team.owner == request.user:
                team.delete()

        return render(request, '_partial/_list_teams.html', context)


    return render(request, 'teams/list.html', context)