import os
import urllib.parse
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv, set_key

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/'
PORT = 8080

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if 'code' in query_components:
            code = query_components['code'][0]
            self.wfile.write(b"Authorization successful! You can close this window and check your terminal.")
            
            # Exchange code for token
            print("Received authorization code. Exchanging for tokens...")
            exchange_token(code)
            
            # Stop the server
            self.server.server_close()
            print("Server closed. Auth flow complete.")
        elif 'error' in query_components:
            self.wfile.write(f"Authorization failed: {query_components['error'][0]}".encode())
            self.server.server_close()
        else:
            self.wfile.write(b"No code received.")

def exchange_token(code):
    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        data = response.json()
        print("Successfully obtained tokens.")
        
        # Save tokens to .env
        set_key(dotenv_path, 'STRAVA_ACCESS_TOKEN', data['access_token'])
        set_key(dotenv_path, 'STRAVA_REFRESH_TOKEN', data['refresh_token'])
        set_key(dotenv_path, 'EXPIRES_AT', str(data['expires_at']))
        print("Tokens saved to .env file.")
        
        print("\nAthlete Info:")
        athlete = data.get('athlete', {})
        print(f"Name: {athlete.get('firstname')} {athlete.get('lastname')}")
        print(f"ID: {athlete.get('id')}")
    else:
        print(f"Failed to exchange token. Status code: {response.status_code}")
        print(response.text)

def run_auth_flow():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("ERROR: STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET is missing from .env. Please update the .env file with your API credentials.")

    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&"
        f"redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read,activity:read_all,profile:read_all"
    )

    print("Opening browser to authorize with Strava...")
    print(f"If the browser doesn't open automatically, navigate to:\n{auth_url}")
    webbrowser.open(auth_url)

    print(f"Starting local server to catch the callback on port {PORT}...")
    try:
        server = HTTPServer(('localhost', PORT), OAuthCallbackHandler)
        server.serve_forever()
    except Exception as e:
        # Happens when the server is intentionally closed from the handler
        pass
    
    # Reload environment variables to get the newly saved tokens
    load_dotenv(dotenv_path, override=True)

if __name__ == "__main__":
    run_auth_flow()
