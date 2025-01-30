from decouple import config
import requests
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from strivers.clients import get_configured_client
from strivers.models import Athlete


class EvalAccessToken(MiddlewareMixin):
    def process_request(self, request):
        # If an athlete has been setup for the session (in any way, except state by Strava)
        athlete = request.session.get('athlete')
        if athlete and 'access_token' in athlete:
            # Check if the access token has expired and renew if needed
            if athlete['expires_at'] < timezone.now().timestamp():
                # Config app specifics for exchange
                client_id = config('CLIENT_ID')
                client_secret = config('CLIENT_SECRET')

                # Get a new token
                token_url = 'https://www.strava.com/oauth/token'
                data = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': athlete.refresh_token,
                }
                response = requests.post(token_url, data=data)
                response_data = response.json()

                # Store athlete access info into session (note: swagger client configuration will be updated
                request.session['athlete']['access_token'] = response_data.get('access_token')
                request.session['athlete']['refresh_token'] = response_data.get('refresh_token')
                request.session['athlete']['expires_at'] = response_data.get('expires_at')

                # If the athlete is in the database, update it
                athlete = Athlete.objects.get(athlete_id=athlete['id'])
                if athlete:
                    athlete.access_token = response_data.get('access_token')
                    athlete.expires_at = response_data.get('expires_at')
                    athlete.refresh_token = response_data.get('refresh_token')
                    athlete.save()

            # Set an up-to-date access token for the API client
            request.configured_client = get_configured_client(athlete['access_token'])
