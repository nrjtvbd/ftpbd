import requests
import re
import time

CHANNELS = [
    {"id": "T-Sports", "name": "T Sports HD"},
    {"id": "GAZI-TV", "name": "Gazi TV HD"},
    {"id": "Somoy-TV", "name": "Somoy TV"},
    {"id": "ZEE-BANGLA", "name": "Zee Bangla"}
]

def get_token(ch_id):
    url = f"http://180.94.28.28:8097/{ch_id}/embed.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://180.94.28.28/"
    }
    try:
        # টাইমাউট বাড়িয়ে দেওয়া হলো যাতে বিডিআইএক্স রেসপন্স করার সময় পায়
        response = requests.get(url, headers=headers, timeout=30)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        return token_match.group(1) if token_match else None
    except:
        return None

def main():
    entries = ["#EXTM3U"]
    print("🚀 Fetching Tokens...")
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            stream_url = f"http://180.94.28.28:8097/{ch['id']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            # যদি টোকেন না পায়, তবে আগের জানা ফরম্যাটটি রেখে দিবে যাতে অন্তত লিঙ্ক থাকে
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\nhttp://180.94.28.28:8097/{ch["id"]}/index.fmp4.m3u8')
            print(f"❌ {ch['name']} Failed (Added fallback)")
    
    with open("playlist.m3u", "w") as f:
        f.write("\n".join(entries))

if __name__ == "__main__":
    main()
