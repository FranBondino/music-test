import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Define your Spotify API credentials
client_id = '620de51ab9df4964a83e46449be4c9b0'
client_secret = '074d515dc4ad4fdc8b6993afcd7184e9'
redirect_uri = 'http://localhost:8888/callback' 

# Define required scopes
scope = "user-library-read playlist-read-private"

# Authenticate using SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                               client_secret=client_secret, 
                                               redirect_uri=redirect_uri, 
                                               scope=scope))

# Get the access token
token_info = sp.auth_manager.get_cached_token()
if token_info:
    access_token = token_info['access_token']
    print(f'Access Token: {access_token}')
else:
    print("Failed to get access token.")
