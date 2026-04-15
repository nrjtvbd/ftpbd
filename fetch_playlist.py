import requests
import re

# আপনার দেওয়া ইনস্পেক্ট ডাটা থেকে পাওয়া কনফিগারেশন
BASE_URL = "http://180.94.28.28:8097"
# এই Referer এবং User-Agent না থাকলে সার্ভার টোকেন দিবে না
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'Referer': 'http://180.94.28.28/'
}

# ftpbd.txt থেকে পাওয়া চ্যানেলের নামগুলো
channels = [
    {"name": "T-SPORTS HD", "slug": "T-Sports"},
    {"name": "GAZI TV HD", "slug": "Gazi-TV"},
    {"name": "SOMOY TV HD", "slug": "Somoy-TV"},
    {"name": "ZEE BANGLA", "slug": "Zee-Bangla"},
    {"name": "SONY EIGHT", "slug": "Sony-Eight"},
    {"name": "DURONTO TV", "slug": "Duronto-TV"}
]

def get_token(slug):
    """ সরাসরি ১৮০.৯৪.২৮.২৮ এর এম্বেড পেজ থেকে হাশ টোকেন বের করা """
    # প্লেয়ার পেজ যেখানে টোকেন থাকে
    player_url = f"http://180.94.28.28/img/play.php?stream={slug}"
    try:
        response = requests.get(player_url, headers=HEADERS, timeout=10)
        # আপনার ইনস্পেক্ট ডাটা অনুযায়ী টোকেন ফরম্যাট স্ক্র্যাপ করা
        # এটি টোকেনের ওই লম্বা হাশ কোডটি খুঁজে বের করবে
        token_match = re.search(r'token=([a-f0-9\-]+)', response.text)
        if token_match:
            return token_match.group(1)
        
        # যদি অন্য ফরম্যাটে থাকে (যেমন স্ক্রিপ্ট ভেরিয়েবল)
        token_match = re.search(r'["\']token["\']\s*:\s*["\']([^"\']+)["\']', response.text)
        return token_match.group(1) if token_match else None
    except:
        return None

def main():
    m3u_content = "#EXTM3U\n"
    print("🚀 Fetching Flussonic Hash Tokens...")

    for ch in channels:
        token = get_token(ch['slug'])
        if token:
            # আপনার দেওয়া ইনস্পেক্ট ডাটায় দেখা মাস্টার ইউআরএল ফরম্যাট: 
            # index.fmp4.m3u8?token=HASH&remote=no_check_ip
            final_url = f"{BASE_URL}/{ch['slug']}/index.fmp4.m3u8?token={token}&remote=no_check_ip"
            m3u_content += f'#EXTINF:-1 tvg-id="{ch["slug"]}" tvg-name="{ch["name"]}", {ch["name"]}\n{final_url}\n'
            print(f"✅ {ch['name']} - Token Updated")
        else:
            print(f"❌ {ch['name']} - Failed to fetch token")

    with open("playlist.m3u", "w", encoding='utf-8') as f:
        f.write(m3u_content)
    print("\n🎉 Done! GitHub Action can now push this.")

if __name__ == "__main__":
    main()
