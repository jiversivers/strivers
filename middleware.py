from decouple import config
import requests
from django.http import Http404
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from strivers.clients import get_configured_client
from strivers.models import Athlete


class EvalAccessToken(MiddlewareMixin):
    def process_request(self, request):
        # If an athlete has been setup for the session (in any way, except state by Strava)
        if 'athlete' in request.session and 'access_token' in request.session['athlete']:
            athlete = request.session.get('athlete')
            print('deserialized: ', athlete)

            # If the athlete is in the database, get it for updating
            try:
                athlete = Athlete.objects.get(athlete_id=athlete['athlete_id'])
                athlete_in_db = True
            except Athlete.DoesNotExist:
                athlete_in_db = False

            # Check if the access token has expired and renew if needed
            if athlete.expires_at < timezone.now().timestamp():
                # Config app specifics for exchange
                client_id = config('CLIENT_ID')
                client_secret = config('CLIENT_SECRET')

                # Get a new token
                token_url = 'https://www.strava.com/oauth/token'
                data = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': athlete['refresh_token'],
                }
                response = requests.post(token_url, data=data)
                response_data = response.json()
                athlete.access_token = response_data.get('access_token')
                athlete.expires_at = response_data.get('expires_at')
                athlete.refresh_token = response_data.get('refresh_token')

                if athlete_in_db:
                    athlete.save()

            # Set an up-to-date access token for the API client
            request.configured_client = get_configured_client(athlete.access_token)

            # Put updated athlete into session
            request.session['athlete'] = athlete
            request.session.save()
