import requests
import re
import datetime
import time

# আপনার পাঠানো টেক্সট ফাইল থেকে প্রাপ্ত সঠিক চ্যানেল লিস্ট
CHANNELS = [
    {"id": "T-Sports", "name": "T Sports HD"},
    {"id": "GAZI-TV", "name": "Gazi TV HD"},
    {"id": "Somoy-TV", "name": "Somoy TV"},
    {"id": "Jamuna-TV", "name": "Jamuna TV"},
    {"id": "Independent-TV", "name": "Independent TV"},
    {"id": "CHANNEL-24", "name": "Channel 24"},
    {"id": "BTV", "name": "BTV World"},
    {"id": "STAR-JALSHA", "name": "Star Jalsha"},
    {"id": "ZEE-BANGLA", "name": "Zee Bangla"},
    {"id": "SONY-AATH", "name": "Sony Aath"},
    {"id": "Sony-Ten-1", "name": "Sony Ten 1 HD"},
    {"id": "Sony-Ten-2", "name": "Sony Ten 2 HD"},
    {"id": "PTV-Sports", "name": "PTV Sports"},
    {"id": "SKY-SPORTS-CRICKET", "name": "Sky Sports Cricket"},
    {"id": "Duronto-TV", "name": "Duronto TV"}
]

def get_token(ch_id):
    # নতুন সার্ভারের এম্বেড ইউআরএল [cite: 8]
    base_url = f"http://180.94.28.28:8097/{ch_id}/embed.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "http://180.94.28.28/",
        "Accept": "*/*"
    }

    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        # সোর্স কোড থেকে টোকেন এক্সট্রাক্ট করা
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        
        if token_match:
            return token_match.group(1)
    except Exception as e:
        print(f"⚠️ Error for {ch_id}: {e}")
    return None

def main():
    print("🚀 Fetching from FTPBD LIVE Server...")
    entries = []
    
    for ch in CHANNELS:
        print(f"📡 Syncing: {ch['name']}...")
        token = get_token(ch['id'])
        
        if token:
            # remote=no_check_ip ব্যবহার করা হয়েছে যাতে গিটহাবের আইপি ব্লক না হয়
            stream_url = f"http://180.94.28.28:8097/{ch['id']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Failed to get token.")
        
        time.sleep(2) # সার্ভারে চাপ কমাতে বিরতি

    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n# Auto Updated: " + str(datetime.datetime.now()) + "\n" + "\n".join(entries))
    
    print("\n🎉 Playlist updated successfully!")

if __name__ == "__main__":
    main()
