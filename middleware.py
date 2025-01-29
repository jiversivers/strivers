from django.utils.deprecation import MiddlewareMixin
from strivers.clients import get_configured_client

class SetAccessToken(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.session.get('access_token')
        if access_token:
            request.configured_client = get_configured_client(access_token)
