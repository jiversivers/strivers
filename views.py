import json

import requests
from decouple import config
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
import swagger_client as sc
from django.urls import reverse
from swagger_client.rest import ApiException

from strivers.clients import client
from strivers.models import Athlete, ActivityOverview


# TODO: Check if user was previously authenticated by looking for a cookie. If so, set client config and redirect to home. Else, redirect to login
def index(request):
    if 'user_id' in request.COOKIES:
        request.session['access_token'] = Athlete.objects.get(pk=request.COOKIES['user_id']) # Get access token for given cookie
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('authorize'))


def home(request):
    if 'access_token' not in request.session:
        return HttpResponseRedirect(reverse('index'))
    elif ActivityOverview.objects.filter(athlete_id=request.session.get('athlete_id')).count() > 0:
        context = {'option-action': zip(['Update Activities', 'Analyze'], ['/get_activities/', '/analysis_tools/'])}
    else:
         context = {'option-action': zip(['Get Activities'], ['/get_activities/'])}

    if Athlete.objects.filter(athlete_id=request.session.get('athlete_id')):
        context['issaved'] = True
        context['username'] = Athlete.objects.get(athlete_id=request.session.get('athlete_id'))
    else:
        context['issaved'] = False

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

    return redirect(strava_url)

def authorization_callback(request):
    client_id = config('CLIENT_ID')
    client_secret = config('CLIENT_SECRET')
    code = request.GET.get('code')
    scope = request.GET.get('scope')

    print(request.POST.get('confirm_limit'))

    # Exchange code for access token
    token_url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }

    if 'auth_response' not in request.session:
        response = requests.post(token_url, data=data)
        response_data = response.json()
        request.session['auth_response'] = response_data
        request.session['athlete_id'] = response_data.get('athlete_id')



    # Check that scope was given, if not, check if they have already confirmed they don't want to
    if scope != 'read,activity:read_all' and 'confirm_limit' not in request.POST:
        return render(request, 'strivers/confirm_limit.html')
    elif 'store_cookie' not in request.POST:
        return render(request,'strivers/cookie_quest.html')
    else:
        # Retrieve and apply the access token
        response_data = request.session['auth_response']
        access_token = response_data.get('access_token')
        request.session['access_token'] = access_token
        client.configuration.access_token = access_token
        response = HttpResponseRedirect(reverse('strivers:home'))

        if request.POST.get('store_cookie') == 'store':
            # Get refresh info
            refresh_token = response_data.get('refresh_token')
            expires_at = response_data.get('expires_at')

            # Put profile and access info into a db indexed by athlete ID
            user_info = Athlete(access_token=access_token,
                                refresh_token=refresh_token,
                                expires_at=expires_at,
                                athlete_id=request.session['athlete_id'])
            user_info.save()

            # Place the cookie
            response.set_cookie('user_id',
                                str(user_info.id),
                                max_age=60 * 60 * 24 * 30,
                                httponly=True,
                                secure=True)
        else:
            return HttpResponseRedirect(response)


def get_activities(request):
    page = 1
    per_page = 100

    try:
        # List Athlete Activities
        api_response = json.dumps(sc.ActivitiesApi(client.get_logged_in_athlete_activities(page=page, per_page=per_page)),
                                  indent=4, sort_keys=True, separators=(',', ': '))
        return HttpResponse(api_response)
    except ApiException as e:
        return HttpResponse("Exception when calling ActivitiesApi->get_logged_in_athlete_activities: %s\n" % e)

def analysis_tools(request):
    pass

def logout(request):
    client.configuration.access_token = None
    request.session.pop('access_token')

    return HttpResponseRedirect(redirect('home'))