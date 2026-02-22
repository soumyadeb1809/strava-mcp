import os
import time
import requests
from dotenv import load_dotenv, set_key

class StravaClient:
    def __init__(self):
        self.dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(self.dotenv_path)
        
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.expires_at = os.getenv('EXPIRES_AT')

    def is_token_expired(self):
        if not self.expires_at:
            return True
        # Refresh if expiring in the next 60 seconds
        return int(time.time()) + 60 >= int(self.expires_at)

    def refresh_access_token(self):
        if not self.refresh_token:
            raise ValueError("No refresh token available. Please run auth.py first.")

        print("Refreshing Strava access token...")
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.expires_at = str(data['expires_at'])

            # Update .env
            set_key(self.dotenv_path, 'STRAVA_ACCESS_TOKEN', self.access_token)
            set_key(self.dotenv_path, 'STRAVA_REFRESH_TOKEN', self.refresh_token)
            set_key(self.dotenv_path, 'EXPIRES_AT', self.expires_at)
            print("Token refreshed successfully.")
        else:
            raise Exception(f"Failed to refresh token: {response.text}")

    def get_headers(self):
        if not self.access_token:
            raise ValueError("No access token. Please run auth.py first.")
        
        if self.is_token_expired():
            self.refresh_access_token()

        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    # Example API call
    def get_athlete_profile(self):
        url = "https://www.strava.com/api/v3/athlete"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

if __name__ == "__main__":
    # Test checking if the token is valid, or refresh it
    try:
        client = StravaClient()
        profile = client.get_athlete_profile()
        print("Successfully queried Strava API!")
        print(f"Athlete: {profile.get('firstname')} {profile.get('lastname')}")
    except Exception as e:
        print(f"Error checking API: {e}")
