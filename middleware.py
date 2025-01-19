from django.utils.deprecation import MiddlewareMixin
import swagger_client as sc
from strivers.clients import client

class SetAccessToken(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.session.get('access_token')
        if access_token:
            client.configuration.access_token = access_token
