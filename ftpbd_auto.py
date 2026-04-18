import requests
import base64
import os
import asyncio
import aiohttp
import re

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

# 🔹 External source
SOURCES = [
    "https://raw.githubusercontent.com/sm-monirulislam/SM-Live-TV/main/SM+BDIX.m3u"
]

# 🔹 Local FTPBD
BASE = "http://180.94.28.28:8097"
LOCAL_CHANNELS = [
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

# 🔹 Clean name
def clean_name(name):
    return re.sub(r'#EXTINF.*?,', '', name).strip()

# 🔹 Detect group
def detect_group(name):
    n = name.lower()
    if any(x in n for x in ["sports","cricket","ten","bein","tsports"]):
        return "Sports"
    elif any(x in n for x in ["cartoon","kids","pogo"]):
        return "Kids"
    else:
        return "Bangla"

# 🔹 Parse m3u
def parse_m3u(text):
    lines = text.splitlines()
    channels = []
    name = None

    for line in lines:
        if line.startswith("#EXTINF"):
            name = line
        elif line.startswith("http"):
            channels.append((name, line))

    return channels

# 🔹 Async GET checker (FIXED)
async def check_url(session, name, url):
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                return (name, url)
    except:
        return None

# 🔹 Fetch external
def fetch_external():
    all_channels = []
    for src in SOURCES:
        try:
            print(f"🌐 Fetching: {src}")
            res = requests.get(src, timeout=10)
            all_channels += parse_m3u(res.text)
        except:
            print("❌ Source failed")
    return all_channels

# 🔹 Build local
def build_local():
    channels = []
    for ch in LOCAL_CHANNELS:
        url = f"{BASE}/{ch}/index.fmp4.m3u8?remote=no_check_ip"
        name = f"#EXTINF:-1,{ch}"
        channels.append((name, url))
    return channels

# 🔹 Remove duplicates
def remove_duplicates(channels):
    seen = set()
    result = []

    for name, url in channels:
        key = (clean_name(name).lower(), url)

        if key not in seen:
            seen.add(key)
            result.append((name, url))

    return result

# 🔹 Async filter with fallback
async def filter_channels(channels):
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, n, u) for n, u in channels]
        results = await asyncio.gather(*tasks)

    working = [r for r in results if r]

    if not working:
        print("⚠️ সব filter হয়ে গেছে → fallback ব্যবহার")
        return channels

    return working

# 🔹 Build playlist
def build_playlist(channels):
    m3u = "#EXTM3U\n\n"

    for name, url in channels:
        cname = clean_name(name)
        group = detect_group(cname)

        m3u += f'#EXTINF:-1 group-title="{group}",{cname}\n{url}\n\n'

    return m3u

# 🔹 Push GitHub
def push_github(content):
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    payload = {
        "message": "🔥 Advanced IPTV Auto Update FIXED",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }

    requests.put(api, headers=headers, json=payload)
    print("✅ GitHub Updated!")

# 🔹 MAIN
async def main():
    print("🚀 Starting Advanced IPTV System...")

    external = fetch_external()
    local = build_local()

    merged = local + external
    merged = remove_duplicates(merged)

    print(f"📊 Total merged: {len(merged)}")

    working = await filter_channels(merged)

    print(f"✅ Final channels: {len(working)}")

    playlist = build_playlist(working)

    with open("playlist.m3u", "w") as f:
        f.write(playlist)

    print("💾 Playlist saved")

    push_github(playlist)

if __name__ == "__main__":
    asyncio.run(main())
