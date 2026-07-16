import requests
import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/gg7965977/YT_ELT/.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"

def get_channel_id(channel_handle):

    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        #print(json.dumps(data, indent=4))

        channel_items = data["items"][0]

        channel_playlisID = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlisID)
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    get_channel_id(CHANNEL_HANDLE) 
else:
    print("get_playlist_id won't be executed")