from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Team, TeamUser, ProjectTeam
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, JsonResponse

@login_required
def list_teams(request):
    action = request.POST.get('action')

    if action == 'create_team':
        name = request.POST.get('name')
        if len(name) > 0:
            team = Team(name=name, owner=request.user)
            team.save()

            teamuser = TeamUser(team=team, user=request.user)
            teamuser.save()

    if action == 'delete_team':
        team_id = request.POST.get('id')
        if team_id:
            team = Team.objects.get(id=team_id)
            if team and team.owner == request.user:
                team.delete()

    teams = Team.objects.filter(teamuser__user=request.user)
    context = {
        'teams': teams,
    }
    return render(request, 'teams/list.html', context)

@login_required
def list_members(request, team_id, team_name):
    team = get_object_or_404(Team, id=team_id)

    is_owner = (request.user == team.owner)
    is_member = TeamUser.objects.filter(team__id=team_id, user__id=request.user.id)

    action = request.POST.get('action')

    if is_owner and action == 'add_member':
        criteria = request.POST.get('criteria')
        user = User.objects.filter(Q(username=criteria) | Q(email=criteria))

        if len(user) == 1:
            already_member = TeamUser.objects.filter(team__id=team_id, user__id=user[0].id)

            if already_member:
                return JsonResponse({'status': 'User already member of this team'})
            else:
                teamuser = TeamUser(team=team, user=user[0])
                teamuser.save()
                return JsonResponse({'status': 0})

        else:
            return JsonResponse({'status': 'We could not find any user with this username or e-mail.'})

    if action == 'remove_member':
        if is_owner:
            user_id = request.POST.get('user_id')
        else:
            # regular user can only remove themselves.
            user_id = request.user.id 

        membership = TeamUser.objects.filter(team__id=team_id, user__id=user_id)
        if membership:
            membership.delete()
            if is_owner:
                # just refresh the page
                return JsonResponse({'status': 0})
            else:
                # redirect to teams page
                return JsonResponse({'status': 1})


    if is_member or is_owner:
        context = {
            'team': team,
            'members': TeamUser.objects.filter(team__id=team_id)
        }
        return render(request, 'teams/members.html', context)
    else:
        raise Http404

@login_required
def list_projects(request, team_id, team_name):
    team = get_object_or_404(Team, id=team_id)
    
    is_member = TeamUser.objects.filter(team__id=team_id, user__id=request.user.id)

    if is_member:
        context = {
            'team': team,
            'projectteams': ProjectTeam.objects.filter(team__id=team_id)
        }
        return render(request, 'teams/projects.html', context)
    else:
        raise Http404