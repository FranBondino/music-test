# Melodic Techno 2025 Insights

A music data analysis pipeline to identify high-energy, danceable tracks ("bangers") and top artists for playlist curation, using Spotify, YouTube audio, PostgreSQL, and Power BI.

## Overview
This project analyzes 50 melodic techno tracks to curate playlists and promote artists. It answers:
- What are the average audio features? (Energy: 0.347, Danceability: 0.566, Valence_Proxy: 0.734)
- Which tracks are peak-time bangers? (e.g., "Little Void" by El Mundo, Danceability 0.834, Energy 0.395)
- Who are the top artists? (e.g., Wassu, avg Energy 0.439)

The pipeline fetches tracks from Spotify, extracts audio features from YouTube, cleans and queries data in PostgreSQL, and visualizes insights in an interactive Power BI dashboard, supplemented by Python visualizations.

## Key Results
- **Bangers Identified**: Tracks with high `Energy` and `Danceability` (e.g., "Little Void" by El Mundo, Danceability 0.834, Energy 0.395).
- **Artist Insights**: Wassu leads with an average energy of 0.439, ideal for promotion.
- **Stats**: Analyzed 50 tracks, with max `Energy` 0.463, max `Danceability` 0.848, and tempo ranging from 118 to 128 BPM.
- **Visual Fixes**: Corrected Power BI Bar Chart and Scatter Plot to use averages (e.g., `Avg_Energy`, `Avg_Danceability`), ensuring fair artist comparisons.

## Data Cleaning
The data cleaning process refines the raw audio feature data extracted from YouTube, ensuring consistency and quality for analysis:
- **Input Data**: `youtube_melic_techno_analysis.csv` contains 50 tracks with columns: `Name`, `Artist`, `File`, `Tempo`, `Energy`, `Danceability`, `Valence_Proxy`, and `Mood`.
- **Script**: `export_cleaned_data.py` manages the cleaning workflow using PostgreSQL:
  - **Database Setup**: Creates or connects to a `tracks` database, defining a table with columns: `name`, `artist`, `file`, `tempo`, `energy`, `danceability`, `valence_proxy`, and `mood`.
  - **Cleaning Steps**:
    - Removes non-UTF-8 characters from the CSV using Unicode normalization.
    - Eliminates duplicate tracks based on `name` and `artist`.
    - Imputes missing values by setting defaults: `tempo = 125`, `energy = 0.347`, `danceability = 0.560`, `valence_proxy = 0.735`, `mood = 'Neutral'`.
    - Constrains `tempo` to the range 110–140 BPM.
    - Validates `mood` values, defaulting invalid entries to `'Neutral'` (allowed values: `Happy`, `Neutral`, `Energetic`, `Calm`).
  - **Output**: Produces `youtube_melic_techno_cleaned.csv` with 50 cleaned rows, ready for analysis.
- **Analysis Queries**: Executes seven SQL queries to derive insights:
  - `Q1_Averages`: Computes average `tempo` (123.0), `energy` (0.347), `danceability` (0.566), and `valence_proxy` (0.734).
  - `Q2_Bangers_By_Mood`: Identifies top 5 bangers (e.g., "Little Void" by El Mundo, Energy 0.395, Danceability 0.834, Mood `Happy`).
  - `Q3_Tempo_vs_Danceability`: Groups tracks by tempo buckets (e.g., 122 BPM with avg Danceability 0.596).
  - `Q4_Top_Artists`: Ranks artists by average `energy` for tracks with `energy > 0.347` (e.g., Wassu at 0.439).
  - `Q5_Tempo_Distribution`: Categorizes tempo into Slow (110–122), Mid (123–126), and Fast (127–140) ranges.
  - `Q6_Outliers`: Flags tracks with extreme `energy` or `danceability` (e.g., "Little Void" with Danceability 0.834).
  - `Q7_Mood_Distribution`: Shows mood distribution (27 Neutral, 19 Happy, 4 Energetic).

## Visualization
The visualization process transforms cleaned data into actionable insights using Power BI and Python:
- **Input Data**: `youtube_melic_techno_cleaned.csv` is imported into Power BI and used for Python visualizations.
- **Power BI Dashboard Design**:
  - **Scatter Plot**: Plots average `Energy` vs. `Danceability` per artist, with bubble size representing `Valence_Proxy`. Updated to use averages for fair comparisons.
  - **Bar Chart**: Displays top 5 artists by average `Energy`, styled with a Neon Futuristic Theme.
  - **Table**: Lists bangers with `Energy > 0.347` and `Danceability > 0.560`, including `Name`, `Artist`, and `Mood`.
  - **Pie Chart**: Shows tempo range distribution (~70% Slow, 110–122 BPM).
  - **Cards**: Display mean `Energy` (0.347), `Danceability` (0.566), and banger count (5 tracks).
  - **Slicer**: Allows filtering by `Artist` for interactive exploration.
- **Python Visualizations**:
  - **Script**: `analyze_melic_techno_with_enhanced_visualizations.py` includes optional Matplotlib and Seaborn visualizations for exploratory analysis.
  - **Plots**:
    - **Scatter Plot**: `Energy` vs. `Danceability` for all tracks, colored by `Mood`.
    - **Bar Chart**: Average `Energy` per artist, highlighting top performers.
    - **Histogram**: Distribution of `Tempo` across tracks.
  - **Output**: Generated as `.png` files (e.g., `energy_danceability_plot.png`) in the `visuals` directory, viewable in any image viewer.
  - **Integration**: These plots can be embedded in reports or used to validate Power BI visuals.
- **Styling**: Applies a Neon Futuristic Theme in Power BI; Python plots use a consistent color scheme (e.g., neon green, blue).
- **Output**: An interactive `.pbix` file (`Melodic_Techno_Dashboard.pbix`) and Python-generated `.png` files.

## Pipeline
The ETL pipeline is structured as follows (see diagram description below for visualization):
1. **Extract**:
   - **Source**: Spotify API
   - **Process**: `fetch_spotify_tracks.py`
   - **Output**: `spotify_melic_techno_tracks.csv` (50 tracks with metadata)
2. **Transform**:
   - **Source**: YouTube Audio
   - **Process**: `analyze_melic_techno_with_enhanced_visualizations.py`
   - **Tools**: `yt-dlp` (downloads audio), `librosa`, `essentia` (extracts features: `Tempo`, `Energy`, `Danceability`, `Valence_Proxy`, `Mood`)
   - **Output**: `youtube_melic_techno_analysis.csv` (raw feature data for 50 tracks)
3. **Load & Transform (Cleaning)**:
   - **Source**: `youtube_melic_techno_analysis.csv`
   - **Process**: `export_cleaned_data.py`
   - **Tools**: PostgreSQL (creates `tracks` table), Python (`pandas`, `psycopg2`, `sqlalchemy`)
   - **Steps**:
     - Removes non-UTF-8 characters
     - Eliminates duplicates based on `name` and `artist`
     - Imputes missing values (e.g., `tempo = 125`, `mood = 'Neutral'`)
     - Constrains `tempo` to 110–140 BPM
     - Validates `mood` (accepts `Happy`, `Neutral`, `Energetic`, `Calm`)
   - **Output**: `youtube_melic_techno_cleaned.csv` (50 cleaned rows)
4. **Load & Visualize**:
   - **Source**: `youtube_melic_techno_cleaned.csv`
   - **Process**: Power BI Dashboard (`Melodic_Techno_Dashboard.pbix`) and Python visualizations
   - **Tools**: Power BI (with Python integration), Matplotlib, Seaborn
   - **Output**: Interactive dashboard and `.png` plots

### ETL Pipeline Diagram
- **Title**: "Melodic Techno 2025 Insights ETL Pipeline"
- **Flow**:
  1. **Extract**:
     - **Source**: Spotify API
     - **Process**: `fetch_spotify_tracks.py`
     - **Output**: `spotify_melic_techno_tracks.csv`
  2. **Transform**:
     - **Source**: YouTube Audio
     - **Process**: `analyze_melic_techno_with_enhanced_visualizations.py`
     - **Tools**: `yt-dlp`, `librosa`, `essentia`
     - **Output**: `youtube_melic_techno_analysis.csv`
  3. **Load & Transform (Cleaning)**:
     - **Source**: `youtube_melic_techno_analysis.csv`
     - **Process**: `export_cleaned_data.py`
     - **Tools**: PostgreSQL, `pandas`, `psycopg2`, `sqlalchemy`
     - **Output**: `youtube_melic_techno_cleaned.csv`
  4. **Load & Visualize**:
     - **Source**: `youtube_melic_techno_cleaned.csv`
     - **Process**: Power BI Dashboard and Python visualizations
     - **Tools**: Power BI, Matplotlib, Seaborn
     - **Output**: `Melodic_Techno_Dashboard.pbix`, `.png` plots
- **Suggestion**: Use a horizontal flowchart with four main boxes ("Extract", "Transform", "Load & Transform", "Load & Visualize") connected by arrows. Include subprocess boxes and annotate tools/outputs as described.

## Setup
To explore the project locally:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/melic-techno-insights.git
   cd melic-techno-insights