import requests
from decouple import config
from django.http import HttpResponse
from django.shortcuts import redirect
from .strava-swagger import swagger-client


# Create your views here.
def home(request):
    return HttpResponse("Hello, world. You're at the strivers home page index.")

def strava_login(request):
    client_id = config('CLIENT_ID')
    redirect_uri = 'http://localhost:8000/strivers/strava_callback/'
    scope = 'activity:read_all'
    response_type = 'code'

    strava_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type={response_type}&scope={scope}"
    )

    return redirect(strava_url)

def strava_callback(request):
    client_id = config('CLIENT_ID')
    client_secret = config('CLIENT_SECRET')
    code = request.GET.get('code')
    scope = request.GET.get('scope')

    # Exchange code for access token
    token_url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=data)
    response_data = response.json()

    # Save the access token and refresh token
    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')
    expires_at = response_data.get('expires_at')

    # Check that scope was given, if not, recall
    if scope != 'read,activity:read_all':
        return HttpResponse('Strivers results will be limited to public data only. Click here to login again or continue anyway.')
    else:
        return HttpResponse('Successful authorization! Redirecting...')

def get_activities(request):
    activities_url = "https://www.strava.com/api/v3/athlete/activities?before=&after=&page=&per_page=" \

    authorization = "Authorization: Bearer [[token]]"