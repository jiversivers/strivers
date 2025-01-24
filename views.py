import json
from decouple import config

import requests
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
import swagger_client as sc
from django.urls import reverse
from swagger_client.rest import ApiException

from strivers.clients import configured_client
from strivers.models import Athlete, ActivityOverview


# Check for authentication state and route accordingly
def index(request):
    # Session authed...ready to go to home
    if 'access_token' in request.session:
        return redirect('strivers:home')

    # User authed, session not...need to look up and set session. Then go to home
    elif 'user_id' in request.COOKIES:
        request.session['access_token'] = Athlete.objects.get(pk=request.COOKIES['user_id'])
        return redirect('strivers:home')

    # Not authed at all...send to authorization view
    else:
        return redirect('strivers:authorize')


def home(request):
    context = {}
    # If session is not authorized
    if 'access_token' not in request.session and 'user_id' not in request.COOKIES:
            context['option_action'] = [('Authorize on Strava', reverse('strivers:authorize'))]

    # If there is a cookie, set session to match and load athlete details
    if 'user_id' in request.COOKIES:
        request.session['access_token'] = Athlete.objects.get(pk=request.COOKIES['user_id'])
        context['issaved'] = True
        context['username'] = Athlete.objects.get(athlete_id=request.session['athlete_id'])

    # If the session is authorized
    if 'access_token' in request.session:
        # At least some activities have been loaded for the athlete
        if ActivityOverview.objects.filter(athlete_id=request.session['athlete_id']).count() > 0:
            context['option_action'] = [('Update Activities', reverse('strivers:get_activities')),
                                        ('Analyze', reverse('strivers:analysis_tools'))]

        # No activities, so no analyze option
        else:
             context['option_action'] = [('Get Activities', reverse('strivers:get_activities'))]
    for key, value in context.items():
        if key == 'option-action':
            for opt, act in value:
                print(f'{key}: {opt} --> {act}')
        else:
            print(f'{key}: {value}')

    return render(request,
                  'strivers/home.html',
                  context)


def authorize(request):
    client_id = config('CLIENT_ID')
    redirect_uri = 'http://localhost:8000/strivers/callback/'
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

    # Store athlete access info into session (note: swagger client configuration will be updated
    request.session['access_token'] = response_data.get('access_token')
    request.session['refresh_token'] = response_data.get('refresh_token')
    request.session['expires_in'] = response_data.get('expires_in')
    request.session['athlete'] = response_data.get('athlete')


    # Ask about a cookie
    return render(request,'strivers/cookie_quest.html')

def store_cookie(request):
    # Default behavior no matter what
    response = redirect('strivers:home')

    # Set the cookie
    if request.method == 'POST' and request.POST['cookie'] == 'yes':
        expires_at = datetime.now() + timedelta(seconds=request.session['expires_in'])

        # Put profile and access info into a db indexed by athlete ID
        user_info = Athlete(athlete_id=request.session['athlete']['id'],
                            username=request.session['athlete']['username'],
                            first_name=request.session['athlete']['firstname'],
                            last_name=request.session['athlete']['lastname'],
                            access_token=request.session.get('access_token'),
                            refresh_token=request.session['refresh_token'],
                            expires_at=expires_at)
        user_info.save()

        # Place the cookie (unique pk in Athlete objects db)
        response.set_cookie('user_id',
                            str(user_info.id),
                            max_age=60 * 60 * 24 * 30, # 30 days
                            httponly=True,
                            secure=True)
    return response

# TODO: Set up database to store where activity loading left off to accommodate updating activities list
def get_activities(request):
    page = 1
    per_page = 100

    try:
        # List Athlete Activities
        api_instance = sc.ActivitiesApi(configured_client)
        api_response = json.dumps(
            api_instance.get_logged_in_athlete_activities(page=page, per_page=per_page),
                                  indent=4, sort_keys=True, separators=(',', ': ')
        )
        return HttpResponse(api_response)
    except ApiException as e:
        return HttpResponse("Exception when calling ActivitiesApi->get_logged_in_athlete_activities: %s\n" % e)

def analysis_tools(request):
    pass

def logout(request):
    configured_client.configuration.access_token = None
    request.session.pop('access_token')

    return redirect('strivers:home')