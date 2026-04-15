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
        # Timeout বাড়িয়ে এবং verify=False দিয়ে ট্রাই করা হচ্ছে
        response = requests.get(url, headers=headers, timeout=25, verify=False)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
    except Exception as e:
        print(f"DEBUG Error for {ch_id}: {e}")
    return None

def main():
    entries = ["#EXTM3U"]
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            stream_url = f"http://180.94.28.28:8097/{ch['id']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(2)

    with open("playlist.m3u", "w") as f:
        f.write("\n".join(entries))

if __name__ == "__main__":
    main()
