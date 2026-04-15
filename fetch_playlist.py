import requests
import re
import datetime
import time

CHANNELS = [
    {"id": "T-Sports", "name": "T Sports HD"},
    {"id": "GAZI-TV", "name": "Gazi TV HD"},
    {"id": "Somoy-TV", "name": "Somoy TV"},
    {"id": "ZEE-BANGLA", "name": "Zee Bangla"},
    {"id": "STAR-JALSHA", "name": "Star Jalsha"},
    {"id": "SONY-AATH", "name": "Sony Aath"}
]

def get_token(ch_id):
    # FTPBD এর ইমবেড ইউআরএল
    url = f"http://180.94.28.28:8097/{ch_id}/embed.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "http://180.94.28.28/"
    }
    try:
        # টাইমআউট বাড়িয়ে ৩০ সেকেন্ড করা হয়েছে
        response = requests.get(url, headers=headers, timeout=30)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
    except:
        return None
    return None

def main():
    entries = ["#EXTM3U"]
    print("🚀 Updating Playlist...")
    
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            # remote=no_check_ip প্যারামিটারটি মনিরুলের মতো করে যোগ করা হয়েছে
            stream_url = f"http://180.94.28.28:8097/{ch['id']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(1)

    with open("playlist.m3u", "w") as f:
        f.write("\n".join(entries))

if __name__ == "__main__":
    main()
