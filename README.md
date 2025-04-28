# Melodic Techno 2025 Insights

A music data analysis pipeline to identify high-energy, danceable tracks ("bangers") and top artists for playlist curation, using Spotify, YouTube audio, PostgreSQL, and Power BI.

## Overview
This project analyzes 50 melodic techno tracks to curate playlists and promote artists. It answers:
- What are the average audio features? (Energy: 0.347, Danceability: 0.560, Valence: 0.735)
- Which tracks are peak-time bangers? (e.g., "Echoes" by Coeus, Danceability 0.844)
- Who are the top artists? (e.g., Massano, avg Energy 0.404)

The pipeline fetches tracks from Spotify, extracts audio features from YouTube, cleans and queries data in PostgreSQL, and visualizes insights in an interactive Power BI dashboard.

## Key Results
- **Bangers Identified**: Tracks with high `Energy_Dance_Score` (e.g., "Montana" by Jasch Patrick, Danceability 1.000).
- **Artist Insights**: Massano leads with an average energy of 0.404, ideal for promotion.
- **Stats**: Analyzed 50 tracks in ~1244 seconds, with max `Energy` 0.463 and max `Danceability` 0.848.
- **Visual Fixes**: Corrected Power BI Bar Chart and Scatter Plot to use averages (e.g., `Avg_Energy_Dance_Score`), ensuring fair artist comparisons.

## Dashboard
- **Scatter Plot**: Average `Energy` vs. `Danceability` per artist, sized by `Valence_Proxy`
- **Bar Chart**: Top 5 artists by average `Energy_Dance_Score` 
- **Table**: Lists bangers with `Energy_Dance_Score > 0.7`.
- **Pie Chart**: Tempo ranges (~70% Slow, 110–122 BPM).
- **Cards**: Display mean `Energy` (0.347), `Danceability` (0.560), and banger count.
- **Slicer**: Filter by artist for interactive exploration.

## Pipeline
1. **Fetch Tracks**: Uses Spotify API (`fetch_spotify_tracks.py`) to retrieve 50 tracks from a melodic techno playlist, saved as `spotify_melic_techno_tracks.csv`.
2. **Analyze Audio**: Downloads YouTube audio (`yt-dlp`) and extracts features (`librosa`, `essentia`) like `Tempo` (mean 123.1 BPM), `Energy`, and `Danceability`, saved as `youtube_melic_techno_analysis.csv`.
3. **SQL Analysis**: Cleans data and runs queries in PostgreSQL (e.g., find outliers with `Danceability > 0.754`), producing `youtube_melic_techno_cleaned.csv`.
4. **Visualize**: Power BI dashboard with interactive visuals, styled in a Neon Futuristic Theme.

## Setup
To explore the project locally:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/melic-techno-insights.git
   cd melic-techno-insights
