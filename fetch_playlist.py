import requests
import re

# আপনার দেওয়া ইনস্পেক্ট ডাটা অনুযায়ী কনফিগারেশন
BASE_URL = "http://180.94.28.28:8097"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://180.94.28.28/'
}

# ftpbd.txt থেকে পাওয়া চ্যানেল লিস্ট
channels = [
    {"name": "T-SPORTS HD", "slug": "T-Sports"},
    {"name": "GAZI TV HD", "slug": "Gazi-TV"},
    {"name": "SOMOY TV HD", "slug": "Somoy-TV"},
    {"name": "ZEE BANGLA", "slug": "Zee-Bangla"},
    {"name": "STAR JALSHA", "slug": "Star-Jalsha"},
    {"name": "STAR PLUS", "slug": "Star-Plus"},
    {"name": "SONY EIGHT", "slug": "Sony-Eight"},
    {"name": "DURONTO TV", "slug": "Duronto-TV"},
    {"name": "DISCOVERY BANGLA", "slug": "DISCOVERY-BANGLA"},
    {"name": "NAT GEO BANGLA", "slug": "NAT-GEO-BANGLA"}
]

def get_flussonic_token(slug):
    """ সরাসরি ১৮০.৯৪.২৮.২৮ সার্ভারের এমবেড পেজ থেকে টোকেন সংগ্রহ """
    embed_url = f"{BASE_URL}/{slug}/embed.html?remote=no_check_ip"
    try:
        response = requests.get(embed_url, headers=HEADERS, timeout=10)
        # আপনার ইনস্পেক্ট ডাটার টোকেন ফরম্যাট অনুযায়ী রেগুলার এক্সপ্রেশন
        token_match = re.search(r'token=([a-f0-9\-]+)', response.text)
        if token_match:
            return token_match.group(1)
        
        # বিকল্প ফরম্যাট চেক (যদি স্ক্রিপ্টের ভেতরে থাকে)
        token_match = re.search(r"window\.token\s*=\s*['\"]([^'\"]+)['\"]", response.text)
        return token_match.group(1) if token_match else None
    except:
        return None

def generate_playlist():
    m3u = "#EXTM3U\n"
    print("🚀 Fetching Flussonic Tokens from 180.94.28.28...")

    for ch in channels:
        token = get_flussonic_token(ch['slug'])
        if token:
            # আপনার দেওয়া ইনস্পেক্ট ডাটা অনুযায়ী মাস্টার ইউআরএল ফরম্যাট
            stream_url = f"{BASE_URL}/{ch['slug']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            m3u += f'#EXTINF:-1 tvg-id="{ch["slug"]}" tvg-name="{ch["name"]}", {ch["name"]}\n{stream_url}\n'
            print(f"✅ {ch['name']} - Token: {token[:10]}...")
        else:
            print(f"❌ {ch['name']} - Token not found")

    with open("playlist.m3u", "w") as f:
        f.write(m3u)
    print("\n🎉 Playlist updated successfully!")

if __name__ == "__main__":
    generate_playlist()
