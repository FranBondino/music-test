import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Set up your credentials
SPOTIPY_CLIENT_ID = "620de51ab9df4964a83e46449be4c9b0"
SPOTIPY_CLIENT_SECRET = "074d515dc4ad4fdc8b6993afcd7184e9"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

# Step 1: Read the existing CSV file
df = pd.read_csv("melodic_techno_tracks.csv")

# Step 2: Extract track IDs
track_ids = df['ID'].tolist()

# Step 3: Fetch audio features for all tracks (Spotify allows up to 100 IDs at a time)
audio_features = sp.audio_features(track_ids)

# Step 4: Extract relevant audio features into a list of dictionaries
features_data = []
for feature in audio_features:
    if feature:  # Check if the feature exists (sometimes it might be None)
        features_data.append({
            'ID': feature['id'],
            'Danceability': feature['danceability'],
            'Energy': feature['energy'],
            'Speechiness': feature['speechiness'],
            'Acousticness': feature['acousticness'],
            'Instrumentalness': feature['instrumentalness'],
            'Liveness': feature['liveness'],
            'Valence': feature['valence'],  # Positivity of the track
            'Tempo': feature['tempo'],
            'Key': feature['key'],
            'Mode': feature['mode'],
            'Duration_ms': feature['duration_ms']
        })

# Step 5: Convert audio features to a DataFrame
features_df = pd.DataFrame(features_data)

# Step 6: Merge the original DataFrame with the audio features DataFrame on 'ID'
combined_df = pd.merge(df, features_df, on='ID', how='left')

# Step 7: Drop the 'Genres' column if it’s not useful (it’s likely 'N/A' from your original code)
if 'Genres' in combined_df.columns:
    combined_df = combined_df.drop(columns=['Genres'])

# Step 8: Save the combined data to a new CSV file
combined_df.to_csv("melodic_techno_audio_features.csv", index=False)

print("Data with audio features saved to melodic_techno_audio_features.csv")