import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Set up your credentials
SPOTIPY_CLIENT_ID = "620de51ab9df4964a83e46449be4c9b0"
SPOTIPY_CLIENT_SECRET = "074d515dc4ad4fdc8b6993afcd7184e9"

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

# Example: Melodic Techno playlist ID (find relevant playlist IDs)
playlist_id = "5n1zRXFeRONJoMdVw18M34"  # Example: Melodic Techno Essentials

results = sp.playlist_tracks(playlist_id)

# Extract track data
track_data = []
for item in results['items']:
    track = item['track']
    track_data.append({
        'Name': track['name'],
        'Artist': track['artists'][0]['name'],
        'Popularity': track['popularity'],
        'ID': track['id'],
        'Genres': track['genres'] if 'genres' in track else 'N/A'
    })

# Save to CSV
df = pd.DataFrame(track_data)
df.to_csv("melodic_techno_tracks.csv", index=False)

print("Data saved to melodic_techno_tracks.csv")
