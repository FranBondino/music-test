import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Spotify API credentials (replace with your own from developer.spotify.com)
client_id = "your_client_id_here"
client_secret = "your_client_secret_here"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Search for a melodic techno playlist (e.g., "Melodic Techno Top")
def get_playlist_tracks(query="Melodic Techno Top", limit=50):
    results = sp.search(q=query, type="playlist", limit=1)
    if not results["playlists"]["items"]:
        raise ValueError("No playlist found for query.")
    
    playlist_id = results["playlists"]["items"][0]["id"]
    playlist_name = results["playlists"]["items"][0]["name"]
    print(f"Fetching tracks from playlist: {playlist_name}")

    # Get tracks
    tracks = []
    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=100)
        for item in results["items"]:
            track = item["track"]
            if track:  # Skip null entries
                tracks.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "spotify_id": track["id"],
                    "popularity": track["popularity"]
                })
        offset += 100
        if len(results["items"]) < 100 or len(tracks) >= limit:
            break
    
    return tracks[:limit]

# Main execution
if __name__ == "__main__":
    try:
        tracks = get_playlist_tracks(limit=50)  # Top 50 tracks
        df = pd.DataFrame(tracks)
        df.to_csv("data/spotify_melodic_techno_tracks.csv", index=False)
        print(f"Saved {len(tracks)} tracks to data/spotify_melodic_techno_tracks.csv")
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")