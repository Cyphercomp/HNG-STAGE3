import requests
from .storage import get_tokens


# cli/api_client.py (Helper to use in all commands)
def authenticated_request(method, url, **kwargs):
    tokens = get_tokens()
    headers = kwargs.get('headers', {})
    headers.update({
        "X-API-Version": "1",
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    kwargs['headers'] = headers

    response = requests.request(method, url, **kwargs)

    # If access token expired (3 mins)
    if response.status_code == 401:
        # 1. Call /auth/refresh with the refresh_token
        # 2. Update credentials.json
        # 3. Retry the original request
        pass 
        
    return response