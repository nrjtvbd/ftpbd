import requests
import re
import base64
import os

# --- CONFIG ---
BASE_URL = "http://180.94.28.28"
STREAM_BASE = "http://180.94.28.28:8097"
GITHUB_TOKEN = os.getenv("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")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "ftpbd.m3u8"

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL
}

# 🔹 STEP 1: Get channel list from homepage
def get_channels():
    print("🔍 Fetching channel list...")
    res = session.get(BASE_URL, headers=HEADERS, timeout=20)
    
    streams = re.findall(r"stream=([A-Za-z0-9\-]+)", res.text)
    unique_streams = list(set(streams))
    
    print(f"✅ Found {len(unique_streams)} channels")
    return unique_streams

# 🔹 STEP 2: Get token for each channel
def get_token(channel):
    try:
        embed_url = f"{STREAM_BASE}/{channel}/embed.html"
        
        res = session.get(embed_url, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": BASE_URL
        }, timeout=20)
        
        token_match = re.search(r'token=([a-zA-Z0-9\-]+)', res.text)
        
        if token_match:
            return token_match.group(1)
        else:
            print(f"⚠️ No token for {channel}")
            return None
    except:
        return None

# 🔹 STEP 3: Build M3U
def build_m3u(channels):
    print("📺 Generating playlist...")
    
    m3u = "#EXTM3U\n"
    
    for ch in channels:
        token = get_token(ch)
        
        if not token:
            continue
        
        stream_url = f"{STREAM_BASE}/{ch}/index.fmp4.m3u8?token={token}"
        referer = f"{STREAM_BASE}/{ch}/embed.html"
        
        m3u += f'#EXTINF:-1, {ch}\n'
        m3u += f'#EXTVLCOPT:http-referrer={referer}\n'
        m3u += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0\n'
        m3u += f"{stream_url}\n"
    
    return m3u

# 🔹 STEP 4: Push to GitHub
def push_github(content):
    print("📤 Uploading to GitHub...")
    
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    encoded = base64.b64encode(content.encode()).decode()
    
    payload = {
        "message": "Auto Update FTPBD Playlist",
        "content": encoded,
        "sha": sha
    }
    
    requests.put(api, headers=headers, json=payload)
    
    print("✅ Done!")

# 🔥 MAIN
if __name__ == "__main__":
    channels = get_channels()
    playlist = build_m3u(channels)
    
    if playlist:
        push_github(playlist)
    else:
        print("❌ Failed to generate playlist")
