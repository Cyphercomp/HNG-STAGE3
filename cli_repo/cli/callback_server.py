# cli/callback_server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

class CallbackHandler(BaseHTTPRequestHandler):
    def do_get(self):
        # Capture the code and state sent back by GitHub/Backend
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.server.auth_state = params['state'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication successful! You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()

def start_local_server():
    server = HTTPServer(('127.0.0.1', 8000), CallbackHandler)
    server.auth_code = None
    server.auth_state = None
    # Wait for exactly one request
    server.handle_request() 
    return server.auth_code, server.auth_state