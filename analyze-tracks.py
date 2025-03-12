import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the audio features data
df = pd.read_csv("melodic_techno_audio_features.csv")

# Example 1: Analyzing BPM vs Popularity
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="BPM", y="Popularity", hue="Popularity", palette="viridis")
plt.title("BPM vs Popularity in Melodic Techno Tracks")
plt.xlabel("BPM (Tempo)")
plt.ylabel("Popularity")
plt.show()

# Example 2: Analyzing Energy vs Danceability
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="Energy", y="Danceability", hue="Popularity", palette="coolwarm")
plt.title("Energy vs Danceability in Melodic Techno Tracks")
plt.xlabel("Energy")
plt.ylabel("Danceability")
plt.show()

# Example 3: Plotting a correlation heatmap for audio features
correlation_matrix = df[['BPM', 'Energy', 'Danceability', 'Valence', 'Loudness']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap for Audio Features")
plt.show()
