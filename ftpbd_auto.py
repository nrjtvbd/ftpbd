import base64
import requests
import os
import re

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

BASE = "http://180.94.28.28:8097"

# Channels
CHANNELS = [
    "BTV","Jamuna-TV","Maasranga-tv","Nagorik-TV","Somoy-TV",
    "GAZI-TV","EKATTOR-TV","CHANNEL-i","CHANNEL-24","CHANNEL-9","RTV",
    "T-Sports"
]

session = requests.Session()

def get_token(channel):
    try:
        url = f"{BASE}/{channel}/embed.html"
        res = session.get(url, timeout=5)

        token = re.search(r'token=([a-zA-Z0-9\-]+)', res.text)
        return token.group(1) if token else None
    except:
        return None

def build_playlist():
    m3u = "#EXTM3U\n\n"

    for ch in CHANNELS:
        print(f"🔍 Checking {ch}...")

        # 1️⃣ Try direct (no token)
        direct_url = f"{BASE}/{ch}/index.fmp4.m3u8?remote=no_check_ip"

        try:
            r = session.get(direct_url, timeout=5)
            if "#EXTM3U" in r.text:
                print(f"✅ Direct OK: {ch}")
                url = direct_url
            else:
                raise Exception("No playlist")
        except:
            print(f"⚠️ Direct failed: {ch}")

            # 2️⃣ Try token
            token = get_token(ch)
            if token:
                print(f"🔑 Token OK: {ch}")
                url = f"{BASE}/{ch}/index.fmp4.m3u8?token={token}"
            else:
                print(f"❌ Skip: {ch}")
                continue

        m3u += f"#EXTINF:-1 group-title=\"Bangla\",{ch}\n{url}\n\n"

    return m3u

def push_github(content):
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    payload = {
        "message": "Hybrid IPTV Update",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }

    requests.put(api, headers=headers, json=payload)
    print("📤 GitHub Updated!")

if __name__ == "__main__":
    playlist = build_playlist()

    with open("playlist.m3u", "w") as f:
        f.write(playlist)

    print("💾 Saved locally!")

    push_github(playlist)
