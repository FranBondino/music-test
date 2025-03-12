import requests
import librosa
import essentia.standard as ess
from io import BytesIO

preview_url = "https://cdnt-preview-2.dzcdn.net/stream/c-2e6a68eecf8f986d904b96f6d2f545e9-4.mp3"
audio_data = BytesIO(requests.get(preview_url).content)

# Test Librosa with ffmpeg backend
try:
    y, sr = librosa.load(audio_data, sr=None)
    print(f"Librosa: Sample rate {sr}, Duration {len(y)/sr:.2f}s")
except Exception as e:
    print(f"Librosa error: {e}")

# Test Essentia
try:
    audio_data.seek(0)
    audio = ess.MonoLoader(filename=None, audioStream=audio_data)()  # Let Essentia pick sample rate
    print(f"Essentia: Duration {len(audio)/audio.sampleRate:.2f}s")
except Exception as e:
    print(f"Essentia error: {e}")