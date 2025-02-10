import json
from decouple import config

import requests
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
import swagger_client as sc
from django.urls import reverse
from swagger_client.rest import ApiException

from strivers.models import Athlete, ActivityOverview


# Check for authentication state and route accordingly
def index(request):
    request.session['index'] = 'passed'
    # Session authed...ready to go to home
    if 'athlete' in request.session:
        return redirect('strivers:home')

    # User authed, session not...need to look up and set session. Then go to home
    elif 'user_id' in request.COOKIES:
        try:
            request.session['athlete'] = Athlete.objects.get(pk=request.COOKIES['user_id'])
            return redirect('strivers:home')
        except Athlete.DoesNotExist:
            response = redirect('strivers:authorize')
            response.delete_cookie('user_id')
            return response

    # Not authed at all...send to authorization view
    else:
        return redirect('strivers:authorize')


def home(request):
    context = {}
    # If session is not authorized
    if 'athlete' not in request.session and 'user_id' not in request.COOKIES:
            context['option_action'] = [('Authorize on Strava', reverse('strivers:authorize'))]

    # If there is a cookie, set session to match and load athlete details
    if 'user_id' in request.COOKIES:
        try:
            athlete = Athlete.objects.get(pk=request.COOKIES['user_id'])
        except Athlete.DoesNotExist:
            return HttpResponse('ERROR: Bad cookie. Clear your cookies and try again.', status=404)
        request.session['athlete'] = athlete
        context['issaved'] = True
        context['name'] = athlete.first_name

    # If the session is authorized
    if 'athlete' in request.session:
        athlete = request.session.get('athlete')
        if 'username' not in context:
            context['name'] = athlete.first_name

        # At least some activities have been loaded for the athlete
        if ActivityOverview.objects.filter(athlete_id=athlete.id).count() > 0:
            context['option_action'] = [('Update Activities', reverse('strivers:get_activities')),
                                        ('Analyze', reverse('strivers:analysis_tools'))]

        # No activities, so no analyze option
        else:
             context['option_action'] = [('Get Activities', reverse('strivers:get_activities'))]

    return render(request,
                  'strivers/home.html',
                  context)


def authorize(request):
    client_id = config('CLIENT_ID')
    redirect_uri = config('DOMAIN') + '/strivers/callback/'
    scope = 'activity:read_all'
    response_type = 'code'

    strava_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type={response_type}&scope={scope}"
    )
    return HttpResponseRedirect(strava_url)

def authorization_callback(request):
    # Get auth returns
    code = request.GET.get('code')
    scope = request.GET.get('scope')

    # Config app specifics for exchange
    client_id = config('CLIENT_ID')
    client_secret = config('CLIENT_SECRET')

    # Check if full scope was given and confirm selection if not
    if scope != 'read,activity:read_all' and ('confirm_limit' not in request.POST or request.POST.get('confirm_limit') == 'reauthorize'):
        return render(request, 'strivers/confirm_limit.html')
    elif scope != 'read,activity:read_all':
        scope = False
    else:
        scope = True

    # Exchange code for user access token
    token_url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data)
    response_data = response.json()

    # Store athlete info into session (note: swagger client configuration will be updated in middleware)
    # (model of data only saved in db past session if cookie is accepted)
    athlete = Athlete(athlete_id=response_data['athlete']['id'],
                      username=response_data['athlete']['username'],
                      first_name=response_data['athlete']['firstname'],
                      last_name=response_data['athlete']['lastname'],
                      access_token=response_data['access_token'],
                      refresh_token=response_data['refresh_token'],
                      expires_at=response_data['expires_at'],
                      scope=scope)
    request.session['athlete'] = athlete.to_dict()

    # Ask about a cookie
    return render(request,'strivers/cookie_quest.html')

def store_cookie(request):
    # Default behavior no matter what
    response = redirect('strivers:home')
    athlete = request.session.get('athlete')
    print(athlete)

    # Set the cookie and save to/update database
    if request.method == 'POST' and request.POST['cookie'] == 'yes':

        # Check if athlete is already in database (even if reauthorizing)
        if Athlete.objects.filter(athlete_id=athlete.athlete_id).count() == 0:
            athlete.save()
        else:
            athlete = Athlete.objects.get(athlete_id=athlete.athlete_id)

        # Place the cookie (unique pk in Athlete objects db)
        response.set_cookie('user_id',
                            str(athlete.id),
                            max_age=60 * 60 * 24 * 30, # 30 days
                            httponly=True,
                            secure=True)

    return response

# TODO: Set up database to store where activity loading left off to accommodate updating activities list
def get_activities(request):
    client = getattr(request, 'configured_client', None)
    page = 1
    per_page = 100
    if client:
        try:
            # List Athlete Activities
            api_instance = sc.ActivitiesApi(client)
            api_response = api_instance.get_logged_in_athlete_activities(page=page, per_page=per_page)
            return HttpResponse(api_response)
        except ApiException as e:
            return HttpResponse("Exception when calling ActivitiesApi->get_logged_in_athlete_activities: %s\n" % e)
    else:
        return redirect('strivers:authorize')
def analysis_tools(request):
    pass

def logout(request):
    request.session.pop('access_token')

    return redirect('strivers:home')