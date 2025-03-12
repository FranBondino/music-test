import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

TOKEN_URL = "https://accounts.spotify.com/api/token"

def get_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {"Authorization": f"Basic {auth_base64}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    token = response.json()["access_token"]

    return token

ACCESS_TOKEN = get_token()
print(f"Access Token: {ACCESS_TOKEN}")  # This expires in ~1 hour
