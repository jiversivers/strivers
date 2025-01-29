import swagger_client as sc

def get_configured_client(access_token=None):
    configuration = sc.Configuration()
    if access_token:
        configuration.access_token = access_token  # Set dynamically
    return sc.ApiClient(configuration)