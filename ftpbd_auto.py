import base64
import requests
import os

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

BASE = "http://180.94.28.28:8097"

CHANNELS = [
    "BTV","Jamuna-TV","Maasranga-tv","Nagorik-TV","Somoy-TV",
    "GAZI-TV","EKATTOR-TV","CHANNEL-i","CHANNEL-24","CHANNEL-9","RTV"
]

def build_playlist():
    m3u = "#EXTM3U\n\n"
    for ch in CHANNELS:
        url = f"{BASE}/{ch}/index.fmp4.m3u8?remote=no_check_ip"
        m3u += f"#EXTINF:-1 group-title=\"Bangla\",{ch}\n{url}\n\n"
    return m3u

def push_github(content):
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.get(api, headers=headers)

    sha = None
    if res.status_code == 200:
        sha = res.json()["sha"]

    payload = {
        "message": "Auto IPTV Update",
        "content": base64.b64encode(content.encode()).decode(),
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(api, headers=headers, json=payload)

    print(r.status_code)
    print(r.json())

if __name__ == "__main__":
    playlist = build_playlist()

    with open("playlist.m3u", "w") as f:
        f.write(playlist)

    print("💾 Local file created!")
    push_github(playlist)
