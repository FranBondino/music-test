## Attributes

This project analyzes 50 melodic techno tracks, extracting four key attributes: `Tempo`, `Energy`, `Danceability`, and `Valence_Proxy`. These attributes help identify "bangers" (high-energy, danceable tracks) and top artists for playlist curation. Below, each attribute is explained in terms of its **music theory** role, **computation** in the `analyze_youtube_audio.py` script, and **statistical concepts** used to analyze and interpret the data.

### 1. Tempo
- **What It Is (Music Theory)**:
  - **Definition**: Tempo is the speed of a track, measured in **beats per minute (BPM)**. It determines how fast or slow the music feels, setting the rhythmic pulse.
  - **Role in Melodic Techno**: In techno (110–140 BPM), tempo drives the vibe. Slower tempos (110–122 BPM) create a hypnotic, atmospheric feel (e.g., for chill sets), while faster tempos (127–140 BPM) fuel high-energy dance floors.
  - **Example**: A track at 128 BPM (like “RITMO” by Argy) feels driving and intense, with beats hitting ~2.13 times per second (128 ÷ 60).
- **How It’s Computed**:
  - **Tool**: `librosa.beat.tempo` (from `analyze_youtube_audio.py`).
  - **Process**:
    1. Loads the audio file (MP3) with `librosa.load`.
    2. Computes **onset strength** (rhythmic events like kicks or snares) using `librosa.onset.onset_strength`.
    3. Estimates BPM with `librosa.beat.tempo`, analyzing the onset envelope.
    4. Filters tempos to 110–140 BPM (techno range) to avoid errors (e.g., doubling to 240 BPM).
    5. Averages valid tempos and rounds to an integer. If no valid tempos (e.g., weak beats), defaults to 125 BPM (genre median).
  - **Output**: A number (e.g., 122 BPM for “Volar” by Seba Campos).
  - **Scale**: Continuous, constrained to 110–140 BPM.
- **Statistical Concepts**:
  - **Descriptive Statistics**: The mean tempo is 123.06 BPM (from your output), with a standard deviation of 2.325, showing most tracks cluster tightly around 122–125 BPM, typical for melodic techno.
  - **Range Constraint**: Filtering to 110–140 BPM is a statistical preprocessing step to eliminate outliers (e.g., erroneous 60 BPM readings), ensuring data validity.
  - **Example**: Your min tempo (118 BPM) and max (128 BPM) suggest a narrow range, reflecting genre consistency.
- **Why It Matters**: Tempo guides playlist pacing. Your SQL query (Q5) groups tempos into “Slow (110–122)”, “Mid (123–126)”, and “Fast (127–140)” to balance variety, with ~70% of tracks in the “Slow” range (per your Power BI Pie Chart).

### 2. Energy
- **What It Is (Music Theory)**:
  - **Definition**: Energy measures a track’s perceived intensity and activity, combining **loudness** (volume) and **timbral brightness** (high-frequency content).
  - **Role in Melodic Techno**: High-energy tracks (e.g., with loud kicks and sharp synths) drive peak-time sets, while lower-energy tracks suit introspective moments. Energy reflects how “powerful” a track feels.
  - **Example**: “Sierra” by Argy (Energy 0.351) has moderate intensity, balancing loud drums with melodic elements.
- **How It’s Computed**:
  - **Tools**: `librosa.feature.rms`, `librosa.feature.spectral_centroid`.
  - **Process**:
    1. Computes **RMS (Root Mean Square)** amplitude, a measure of loudness, using `librosa.feature.rms`.
    2. Normalizes RMS as `mean(rms) / max(rms)` to scale loudness relative to the track’s peak.
    3. Computes **spectral centroid**, the “center of mass” of frequencies (in Hz), using `librosa.feature.spectral_centroid`. Higher centroids (e.g., 4000 Hz) indicate brighter sounds (e.g., sharp hi-hats).
    4. Combines: `energy_perceptual = 0.7 * rms_normalized + 0.3 * (spectral_centroid / 10000)`.
    5. Caps at 1.0 to prevent overshooting.
  - **Output**: A value from 0 (quiet, dull) to 1 (loud, bright), e.g., 0.463 for your max-energy track.
  - **Scale**: Continuous, 0–1.
- **Statistical Concepts**:
  - **Normalization**: Dividing RMS by its max and scaling centroid by 10000 ensures both components are on a 0–1 scale, allowing a weighted sum (0.7 + 0.3 = 1).
  - **Weighted Average**: The 70% RMS, 30% centroid formula prioritizes loudness but adds brightness for perceptual accuracy, a common statistical technique in feature engineering.
  - **Descriptive Statistics**: Mean `Energy` 0.347, std 0.043 (your output) indicate tracks are moderately energetic with low variability, fitting techno’s consistent intensity. Max 0.463 and min 0.264 show a moderate spread.
  - **Outlier Detection**: Your SQL query (Q6) flags tracks with `Energy > mean + 2 * std` (~0.433), identifying unusually intense tracks.
- **Why It Matters**: Energy pinpoints tracks for specific moments (e.g., peak-time vs. warmup). Your Power BI Scatter Plot uses `Avg_Energy` to compare artists, with high-energy ones (e.g., Massano, ~0.404) standing out.

### 3. Danceability
- **What It Is (Music Theory)**:
  - **Definition**: Danceability measures how suitable a track is for dancing, based on rhythmic strength, beat consistency, and tempo stability.
  - **Role in Melodic Techno**: High-danceability tracks have steady, groovy beats that keep dancers moving (e.g., strong 4/4 kicks). Lower danceability might suit ambient or experimental techno.
  - **Example**: “Montana” by Jasch Patrick (Danceability 1.000) has a rock-solid rhythm, perfect for the dance floor.
- **How It’s Computed**:
  - **Tool**: `essentia.standard.Danceability`.
  - **Process**:
    1. Loads audio as mono with `essentia.MonoLoader`.
    2. Applies Essentia’s `Danceability` algorithm, which analyzes beat strength, rhythmic regularity, and tempo consistency.
    3. Outputs a raw value (0 to ~2.5), reflecting dance suitability.
    4. Normalizes: `danceability_normalized = min(raw / 2.5, 1.0)` to match a 0–1 scale (calibrated to Spotify’s scale).
  - **Output**: A value from 0 (non-danceable) to 1 (highly danceable), e.g., 0.848 for “Echoes” by Coeus.
  - **Scale**: Continuous, 0–1.
- **Statistical Concepts**:
  - **Normalization**: Dividing by 2.5 scales Essentia’s raw output to a standard 0–1 range, ensuring comparability with other datasets (e.g., Spotify).
  - **Descriptive Statistics**: Mean `Danceability` 0.560, std 0.097 (your output) show moderate danceability with some variability. Max 0.848 and min 0.395 indicate a range from groovy to less rhythmic tracks.
  - **Outlier Detection**: SQL query (Q6) flags tracks with `Danceability > mean + 2 * std` (~0.754), like “Echoes” (0.844), as ultra-danceable.
  - **Correlation Analysis**: Your SQL query (Q3) groups by tempo to check if danceability varies (e.g., 120 BPM tracks average 0.844), a statistical approach to explore relationships.
- **Why It Matters**: Danceability identifies crowd-pleasers. Your Power BI Table and Scatter Plot highlight tracks with high `Danceability` (e.g., >0.7) as bangers, and `Avg_Danceability` ranks artists.

### 4. Valence_Proxy
- **What It Is (Music Theory)**:
  - **Definition**: Valence represents a track’s emotional mood, from sad/dark (0) to happy/uplifting (1). Your `Valence_Proxy` approximates this using audio features, as direct mood labeling requires human input.
  - **Role in Melodic Techno**: High-valence tracks (e.g., bright, uplifting) suit sunrise sets or euphoric moments, while low-valence tracks (dark, moody) fit late-night vibes.
  - **Example**: “Bulkowa” by Arina Mur (Valence 0.890) feels bright and positive, likely due to a high spectral centroid (~5055 Hz).
- **How It’s Computed**:
  - **Tools**: `essentia.standard.Centroid`, `librosa` (for tempo, energy).
  - **Process**:
    1. Computes **spectral centroid** (average frequency, in Hz) over audio frames (2048 samples, 1024 hop) using `essentia.Centroid`. Higher centroids = brighter sounds.
    2. Uses `Tempo` (from above, normalized by 140 BPM) and `Energy` (from above, already 0–1).
    3. Combines: `valence_proxy = 0.5 * (centroid_mean / 5000) + 0.4 * (tempo / 140) + 0.1 * energy_perceptual`.
    4. Clamps between 0 and 1 to stay in range.
  - **Output**: A value from 0 (sad) to 1 (happy), e.g., 0.735 mean across tracks.
  - **Scale**: Continuous, 0–1.
  - **Why No Key?**: You tried Essentia’s `Key` detection (HPCP-based) but found it unreliable on YouTube audio (e.g., “A minor, Strength: 0.000”). Dropped it to focus on robust features (centroid, tempo, energy).
- **Statistical Concepts**:
  - **Weighted Sum**: The formula (0.5 + 0.4 + 0.1 = 1) is a weighted average, prioritizing brightness (50%), then tempo (40%), and energy (10%) for mood estimation, a statistical method to combine features.
  - **Normalization**: Scaling centroid by 5000 Hz and tempo by 140 BPM ensures each term is 0–1, making the sum interpretable.
  - **Descriptive Statistics**: Mean `Valence_Proxy` 0.735, std 0.067 (your output) suggest most tracks are uplifting, with low variability. Max 0.890 and min 0.629 show a range from moody to euphoric.
  - **Feature Engineering**: Combining centroid, tempo, and energy to proxy valence is a statistical technique to approximate a complex variable (mood) without direct data.
- **Why It Matters**: Valence helps curate mood-driven playlists. Your Power BI Scatter Plot sizes dots by `Avg_Valence`, highlighting uplifting artists (e.g., Arina Mur).

### Statistical Concepts in Context
- **Normalization**: Used across all attributes to scale values to 0–1 (e.g., `Energy_Dance_Score` combines normalized `Energy` and `Danceability`). This ensures comparability and prevents any single feature from dominating due to scale differences.
- **Descriptive Statistics**: Your output (`mean`, `std`, `min`, `max`) summarizes the dataset, shown in Power BI Cards (e.g., mean `Energy` 0.347). These stats help understand the dataset’s central tendency and spread.
- **Outlier Detection**: SQL query (Q6) uses `mean + 2 * std` to flag exceptional tracks (e.g., `Danceability` > 0.754), a statistical method to identify anomalies for review.
- **Grouping and Aggregation**: SQL queries (Q3, Q5) group by tempo or tempo ranges, computing averages (e.g., avg `Danceability` per tempo bucket), a statistical approach to uncover patterns.
- **Feature Engineering**: `Energy_Dance_Score` (0.5 * `Energy` + 0.5 * `Danceability`) and `Valence_Proxy` are engineered features, combining raw metrics to capture higher-level concepts (banger potential, mood), a key statistical technique in data analysis.

### Music Theory in Context
- **Rhythm and Tempo**: Techno’s 4/4 time signature and 110–140 BPM range create a steady pulse, analyzed via `Tempo`. Your Pie Chart shows most tracks are “Slow” (110–122 BPM), aligning with melodic techno’s hypnotic style.
- **Timbre and Energy**: Timbre (sound quality, e.g., bright synths vs. dull pads) influences `Energy` via spectral centroid. High-energy tracks (e.g., >0.347) have brighter, louder timbres, suiting peak moments.
- **Groove and Danceability**: Danceability reflects the strength of techno’s kick-snare patterns and syncopation. Tracks like “Montana” (1.000) have consistent grooves, ideal for dancing.
- **Mood and Valence**: Valence ties to techno’s emotional arc (dark vs. uplifting). High-valence tracks (e.g., “Bulkowa”) use brighter timbres and moderate tempos, evoking positivity.

### Example Interpretation
- **Track**: “Echoes” by Coeus (hypothetical, based on prior data):
  - **Tempo**: 120 BPM (slow, hypnotic).
  - **Energy**: 0.358 (above mean 0.347, intense).
  - **Danceability**: 0.844 (top outlier, super groovy).
  - **Valence_Proxy**: 0.732 (near mean 0.735, balanced mood).
  - **Takeaway**: A peak-time banger (high `Energy_Dance_Score`), shown in your Power BI Table and Scatter Plot.

### Notes
- **Why These Attributes?**: They mimic Spotify’s features (tempo, energy, danceability, valence) but are computed from YouTube audio, bypassing API limits. This makes your pipeline unique and practical.
- **Limitations**: YouTube audio quality varies, affecting centroid accuracy. `Valence_Proxy` is an approximation, as true valence requires listener feedback.
