# Audio Feature Analysis Algorithm

## Overview
Analyzes 50 melodic techno tracks from Spotify (via `fetch_spotify_tracks.py`) and YouTube audio (via `analyze_youtube_audio.py`), with SQL analysis in PostgreSQL and Power BI visualizations. Outputs: `spotify_melic_techno_tracks.csv`, `youtube_melic_techno_analysis.csv`, `youtube_melic_techno_cleaned.csv`.

## Workflow
1. **Fetch**: Spotify API (`spotipy`) for 50 tracks.
2. **Audio**: `yt-dlp` downloads MP3s, analyzed with `librosa` (tempo, energy) and `essentia` (danceability, valence).
3. **SQL**: PostgreSQL cleaning and queries (6 questions).
4. **Power BI**: Dashboard with Scatter Plot, Bar Chart, Table, Pie Chart, Cards, Slicer.

## Attributes
- **Tempo**: 110-140 BPM (`librosa.beat.tempo`).
- **Energy**: 0-1 (`0.7 * rms_normalized + 0.3 * centroid/10000`).
- **Danceability**: 0-1 (`essentia.Danceability / 2.5`).
- **Valence_Proxy**: 0-1 (`0.5 * centroid/5000 + 0.4 * tempo/140 + 0.1 * energy`).

## Example
- **“Echoes” (Coeus)**: Tempo 120, Energy 0.358, Danceability 0.844, Valence 0.732—prime banger.