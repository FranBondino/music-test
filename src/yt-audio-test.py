import os
import subprocess
import librosa
import essentia.standard as ess
import pandas as pd
import time
import numpy as np

tracks = [
    {"name": "Return to Oz (ARTBAT Remix)", "artist": "Monolink"},
    {"name": "Sierra", "artist": "Argy"},
    {"name": "Echoes", "artist": "Coeus"},
    {"name": "Transmission - Joris Voorn Remix", "artist": "Eelke Kleijn"},
    {"name": "Breathe", "artist": "Massano"},
    {"name": "Alone", "artist": "Massano"},
    {"name": "Horizon", "artist": "Artbat"}
]

track_data = []
start_time = time.time()

for i, track in enumerate(tracks, 1):
    query = f"{track['name']} {track['artist']} track"
    file_name = f"{query.replace(' ', '_')}.mp3"

    if not os.path.exists(file_name):
        print(f"[{i}/{len(tracks)}] Downloading: {query}")
        try:
            subprocess.run([
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                f"ytsearch:{query}",
                "--match-filter", "duration <= 600",
                "-o", file_name
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {query}: {e}")
            continue
    else:
        print(f"[{i}/{len(tracks)}] Using cached: {query}")

    try:
        print(f"[{i}/{len(tracks)}] Analyzing: {query}")
        y, sr = librosa.load(file_name, sr=None)

        # Tempo: Estimate with wider range, pick strongest in 110-140 BPM, round to integer
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempos = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
        valid_tempos = [t for t in tempos if 110 <= t <= 140]
        final_tempo = round(float(np.mean(valid_tempos))) if valid_tempos else 125  # Round to int
        print(f"Tempo: {final_tempo} BPM")  # Integer output

        # Energy: Normalized + perceptual
        rms = librosa.feature.rms(y=y)
        energy_normalized = rms.mean() / rms.max()
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        spectral_max = 10000
        energy_perceptual = 0.7 * energy_normalized + 0.3 * (spectral_centroid / spectral_max)
        energy_perceptual = min(energy_perceptual, 1.0)
        print(f"Energy: {energy_perceptual:.3f}")

        # Danceability: Normalized 0-1
        audio = ess.MonoLoader(filename=file_name)()
        danceability_raw, _ = ess.Danceability()(audio)
        danceability_normalized = min(danceability_raw / 2, 1.0)
        print(f"Danceability: {danceability_normalized:.3f}")

        track_data.append({
            "Name": track['name'],
            "Artist": track['artist'],
            "File": file_name,
            "Tempo": float(final_tempo),  # Still float for CSV consistency
            "Energy": energy_perceptual,
            "Danceability": danceability_normalized
        })
    except Exception as e:
        print(f"Error processing {query}: {e}")

if track_data:
    df = pd.DataFrame(track_data)
    df.to_csv("youtube_melic_techno_analysis.csv", index=False)
    print(f"Data saved to youtube_melic_techno_analysis.csv. Took {time.time() - start_time:.2f} seconds.")
    print(df.describe())
else:
    print("No tracks processed successfully.")