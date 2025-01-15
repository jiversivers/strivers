import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json
import pycurl
from io import BytesIO

from socks import HTTPError


# Create your views here.
def home(request):
    return HttpResponse("Hello, world. You're at the strivers home page index.")

def strava_login(request):
    client_id = '85428'
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
    code = request.GET.get('code')
    scope = request.GET.get('scope')
    client_id = "85428"
    client_secret = 'c7bd4b8cb5b6e340abe0b91214ba2f91d0dd87bd'

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
