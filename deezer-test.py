import requests
import librosa
import essentia.standard as ess
import pandas as pd
from io import BytesIO
import time

# Deezer playlist ID (example: Melodic Techno playlist)
playlist_id = "3155776842"  # "Melodic Techno" by Deezer
url = f"https://api.deezer.com/playlist/{playlist_id}/tracks?limit=2"
response = requests.get(url).json()
tracks = response.get('data', [])
print(f"Found {len(tracks)} tracks in Deezer playlist.")

track_data = []
start_time = time.time()

for i, track in enumerate(tracks, 1):
    track_name = track['title']
    artist = track['artist']['name']
    preview_url = track.get('preview')

    if not preview_url:
        print(f"[{i}/{len(tracks)}] Skipping {track_name} - No preview available")
        continue

    try:
        print(f"[{i}/{len(tracks)}] Processing: {track_name} by {artist}")
        audio_data = BytesIO(requests.get(preview_url).content)
        
        # Librosa Analysis
        y, sr = librosa.load(audio_data, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        energy = librosa.feature.rms(y=y).mean()
        
        # Essentia Analysis
        audio_data.seek(0)
        audio = ess.MonoLoader(filename=None, audioStream=audio_data, sampleRate=sr)()
        danceability, _ = ess.Danceability()(audio)
        complexity, loudness = ess.DynamicComplexity()(audio)
        
        track_data.append({
            'ID': track['id'],
            'Name': track_name,
            'Artist': artist,
            'Preview_URL': preview_url,
            'Tempo': tempo,
            'Energy': float(energy),
            'Danceability': danceability,
            'DynamicComplexity': complexity,
            'Loudness': loudness
        })
    except Exception as e:
        print(f"Error processing {track_name}: {e}")

if track_data:
    df = pd.DataFrame(track_data)
    df.to_csv("melodic_techno_deezer_preview_analysis.csv", index=False)
    print(f"Data saved. Took {time.time() - start_time:.2f} seconds.")
    print(df.describe())
else:
    print("No tracks processed successfully.")