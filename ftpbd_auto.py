import requests
import re
import base64
import os

# --- CONFIG ---
STREAM_BASE = "http://180.94.28.28:8097"
GITHUB_TOKEN = os.getenv("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")
REPO = "nrjtvbd/plusbox"
FILE_PATH = "ftpbd.m3u8"

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://180.94.28.28/"
}

# ✅ STATIC CHANNEL LIST (no homepage scraping)
CHANNELS = [
    "T-Sports",
    "BEIN-SPORTS-USA",
    "STAR-SPORTS-1",
    "Star-Sports-2",
    "Star-Sports-Select-1",
    "star-Sports-Select-2",
    "Star-Sports-3",
    "Sony-Ten-1",
    "Sony-Ten-2",
    "Sony-Ten-3",
    "Sony-Ten-5",
    "PTV-Sports",
    "A-Sports",
    "Ten-Sports",
    "Ten-Cricket",
    "SUPERSPORT-CRICKET",
    "SKY-SPORTS-CRICKET",
    "WILLOW-TV",
    "BEIN-SPORTS-ARABIC",
    "BEIN-SPORTS-1-ENG",
    "BEIN-SPORTS-1",
    "BEIN-SPORTS-2",
    "BEIN-SPORTS-3",
    "GEO-SUPER",
    "Sky-Sports-Football",
    "Sky-Sports-Premier-League",

    "BTV",
    "Jamuna-TV",
    "Maasranga-tv",
    "Nagorik-TV",
    "Somoy-TV",
    "GAZI-TV",
    "EKATTOR-TV",
    "CHANNEL-i",
    "CHANNEL-24",
    "CHANNEL-9",
    "DEEPTO-TV",
    "DBC-NEWS",
    "Independent-TV",
    "RTV",
    "ZEE-BANGLA",
    "STAR-JALSHA",
    "JALSHA-MOVIES",
    "ENTER-10-BANGLA",
    "SONY-AATH",
    "COLORS-BANGLA",
    "COLORS-BANGLA-CINEMA",
    "SUN-BANGLA",

    "STAR-PLUS",
    "SONY-MAX",
    "SONY-MAX-2",
    "SONY-PIX",
    "ZEE-CINEMA",
    "MOVIES-NOW",

    "CARTOON-NETWORK",
    "POGO",
    "DISCOVERY-KIDS",
    "Duronto-TV",

    "DISCOVERY-BANGLA",
    "NAT-GEO-BANGLA"
]

# 🔹 Get token per channel
def get_token(channel):
    try:
        embed_url = f"{STREAM_BASE}/{channel}/embed.html"
        
        res = session.get(embed_url, headers=HEADERS, timeout=10)
        
        token_match = re.search(r'token=([a-zA-Z0-9\-]+)', res.text)
        
        if token_match:
            return token_match.group(1)
        else:
            print(f"⚠️ No token: {channel}")
            return None

    except Exception as e:
        print(f"❌ Error {channel}: {e}")
        return None

# 🔹 Build M3U playlist
def build_m3u():
    print("📺 Generating playlist...")
    
    m3u = "#EXTM3U\n"
    
    for ch in CHANNELS:
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

# 🔹 Push to GitHub
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
    
    print("✅ Playlist updated!")

# 🔥 MAIN
if __name__ == "__main__":
    playlist = build_m3u()
    
    if playlist:
        push_github(playlist)
    else:
        print("❌ Failed to generate playlist")
