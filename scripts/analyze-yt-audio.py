import os
import subprocess
import librosa
import essentia.standard as ess
import pandas as pd
import time
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load tracks from Spotify CSV
input_csv = "data/spotify_melic_techno_tracks.csv"
if not os.path.exists(input_csv):
    raise FileNotFoundError(f"Input CSV not found: {input_csv}")
df_spotify = pd.read_csv(input_csv)
tracks = [{"name": row["name"], "artist": row["artist"]} for _, row in df_spotify.iterrows()]
print(f"Loaded {len(tracks)} tracks from {input_csv}")

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
        # Load audio with Librosa (for tempo)
        y, sr = librosa.load(file_name, sr=None)

        # Tempo: Librosa
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempos = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
        valid_tempos = [t for t in tempos if 110 <= t <= 140]
        final_tempo = round(float(np.mean(valid_tempos))) if valid_tempos else 125
        print(f"Tempo: {final_tempo} BPM")

        # Load audio with Essentia
        audio = ess.MonoLoader(filename=file_name)()

        # Energy: Librosa
        rms = librosa.feature.rms(y=y)
        energy_normalized = rms.mean() / rms.max()
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        spectral_max = 10000
        energy_perceptual = 0.7 * energy_normalized + 0.3 * (spectral_centroid / spectral_max)
        energy_perceptual = min(energy_perceptual, 1.0)
        print(f"Energy: {energy_perceptual:.3f}")

        # Danceability: Essentia
        danceability_raw, _ = ess.Danceability()(audio)
        print(f"Raw Danceability: {danceability_raw}")
        danceability_normalized = min(danceability_raw / 2.5, 1.0)
        print(f"Danceability: {danceability_normalized:.3f}")

        # Valence Proxy with Essentia (no key)
        frame_generator = ess.FrameGenerator(audio, frameSize=2048, hopSize=1024)
        spectrum_algo = ess.Spectrum()
        centroid_algo = ess.Centroid(range=sr/2)
        spectral_centroids = [centroid_algo(spectrum_algo(frame)) for frame in frame_generator]
        centroid_mean = np.mean(spectral_centroids) if spectral_centroids else 3000
        print(f"Spectral Centroid: {centroid_mean:.2f} Hz")

        valence_proxy = (
            0.5 * (centroid_mean / 5000) +
            0.4 * (final_tempo / 140) +
            0.1 * energy_perceptual
        )
        valence_proxy = min(max(valence_proxy, 0), 1)
        print(f"Valence Proxy: {valence_proxy:.3f}")

        track_data.append({
            "Name": track["name"],
            "Artist": track["artist"],
            "File": file_name,
            "Tempo": float(final_tempo),
            "Energy": energy_perceptual,
            "Danceability": danceability_normalized,
            "Valence_Proxy": valence_proxy
        })
    except Exception as e:
        print(f"Error processing {query}: {e}")

if track_data:
    df = pd.DataFrame(track_data)

    # Add mood classification
    conditions = [
        (df["Valence_Proxy"] > 0.7) & (df["Energy"] > 0.35),
        (df["Valence_Proxy"] < 0.65),
        (df["Energy"] > 0.35),
        (df["Valence_Proxy"] < 0.65) & (df["Energy"] < 0.3)
    ]
    choices = ["Happy", "Neutral", "Energetic", "Calm"]
    df["Mood"] = np.select(conditions, choices, default="Neutral")

    # Save to CSV
    output_csv = "data/youtube_melic_techno_analysis.csv"
    df.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv}. Took {time.time() - start_time:.2f} seconds.")
    print(df.describe())

    # Add clustering
    features = ["Tempo", "Energy", "Danceability", "Valence_Proxy"]
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X_scaled)

    # Visualization 1: Scatter Plot with Seaborn
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        x="Danceability",
        y="Energy",
        hue="Mood",
        size="Valence_Proxy",
        palette="Set2",
        alpha=0.7,
        sizes=(20, 200)
    )
    plt.title("Melodic Techno Tracks: Energy vs Danceability")
    plt.xlabel("Danceability")
    plt.ylabel("Energy")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("data/melic_techno_scatter.png")
    print("Saved scatter plot to data/melic_techno_scatter.png")

    # Visualization 2: Violin Plot with Seaborn and Swarm
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.violinplot(x="Mood", y="Energy", data=df, palette="Set2")
    sns.swarmplot(x="Mood", y="Energy", data=df, color="black", size=4, alpha=0.6)
    plt.title("Energy Distribution by Mood")
    plt.subplot(1, 2, 2)
    sns.violinplot(x="Mood", y="Danceability", data=df, palette="Set2")
    sns.swarmplot(x="Mood", y="Danceability", data=df, color="black", size=4, alpha=0.6)
    plt.title("Danceability Distribution by Mood")
    plt.tight_layout()
    plt.savefig("data/melic_techno_violinplot.png")
    print("Saved violin plot to data/melic_techno_violinplot.png")

    # Visualization 3: Heatmap of Feature Correlations
    correlation_matrix = df[features].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, center=0, square=True, fmt=".2f")
    plt.title("Correlation Matrix of Melodic Techno Features")
    plt.savefig("data/melic_techno_heatmap.png")
    print("Saved correlation heatmap to data/melic_techno_heatmap.png")

else:
    print("No tracks processed successfully.")