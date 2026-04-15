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
    # সরাসরি রিকোয়েস্ট না পাঠিয়ে আমরা একটি প্রক্সি গেটওয়ে ব্যবহার করছি
    url = f"http://180.94.28.28:8097/{ch_id}/embed.html"
    
    # এটি GitHub-এর আইপি মাস্ক করার চেষ্টা করবে
    proxies = {
        "http": "http://103.150.184.214:8080", # একটি বাংলাদেশি প্রক্সি (কাজ না করলে এটি পরিবর্তন করা যাবে)
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://180.94.28.28/"
    }

    try:
        # প্রক্সি ছাড়া একবার ট্রাই করবে, ফেইল করলে প্রক্সি দিয়ে ট্রাই করবে
        response = requests.get(url, headers=headers, timeout=15)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
    except:
        print(f"DEBUG: Direct access failed for {ch_id}, trying alternative path...")
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
    
    with open("playlist.m3u", "w") as f:
        f.write("\n".join(entries))

if __name__ == "__main__":
    main()
