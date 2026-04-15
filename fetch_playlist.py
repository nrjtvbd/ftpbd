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
    url = f"http://180.94.28.28:8097/{ch_id}/embed.html"
    
    # আপনার পাঠানো লগ থেকে হুবহু হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "http://180.94.28.28/",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        # verify=False দেওয়া হয়েছে যাতে SSL ইস্যু না হয়
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        
        # টোকেন এক্সট্রাকশন
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
        else:
            # ডিবাগিংয়ের জন্য সোর্স কোড চেক
            print(f"DEBUG: Token not found in HTML for {ch_id}")
    except Exception as e:
        print(f"DEBUG: Connection Error for {ch_id}: {e}")
    return None

def main():
    entries = ["#EXTM3U"]
    print("🚀 Attempting to Fetch from FTPBD...")
    
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            # remote=no_check_ip প্যারামিটারটি এখানে ম্যাজিকের মতো কাজ করে
            stream_url = f"http://180.94.28.28:8097/{ch['id']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(2)

    with open("playlist.m3u", "w") as f:
        f.write("\n".join(entries))

if __name__ == "__main__":
    main()
