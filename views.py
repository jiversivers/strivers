import requests
from decouple import config
from django.http import HttpResponse
from django.shortcuts import redirect
import swagger_client as sc
from swagger_client.rest import ApiException


# Create your views here.
def home(request):
    return HttpResponse("Hello, world. You're at the Strivers home page index.")

def authorize(request):
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

def authorization_callback(request):
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
    # Configure OAuth2 access token for authorization: strava_oauth
    configuration = sc.Configuration()
    configuration.access_token = '675c1854baabb592e9aca1a6fb3a00284c7536f2'

    # create an instance of the API class
    api_instance = sc.ActivitiesApi(sc.ApiClient(configuration))
    before = 56  # int | An epoch timestamp to use for filtering activities that have taken place before a certain time. (optional)
    after = 56  # int | An epoch timestamp to use for filtering activities that have taken place after a certain time. (optional)
    page = 56  # int | Page number. Defaults to 1. (optional)
    per_page = 30  # int | Number of items per page. Defaults to 30. (optional) (default to 30)

    try:
        # List Athlete Activities
        api_response = api_instance.get_logged_in_athlete_activities(before=before, after=after, page=page,
                                                                     per_page=per_page)
        return HttpResponse(api_response)
    except ApiException as e:
        return HttpResponse("Exception when calling ActivitiesApi->get_logged_in_athlete_activities: %s\n" % e)