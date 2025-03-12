import requests

url = f"https://api.deezer.com/playlist/3155776842/tracks?limit=2"
response = requests.get(url).json()
for track in response['data']:
    preview_url = track.get('preview')
    print(f"Track: {track['title']}")
    print(f"Preview URL: {preview_url}")
    if preview_url:
        audio_response = requests.get(preview_url)
        print(f"Status: {audio_response.status_code}")
        print(f"Content-Type: {audio_response.headers.get('Content-Type')}")
        print(f"First 10 bytes: {audio_response.content[:10]}")