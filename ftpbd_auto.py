import base64
import requests
import os
import re

# গিটহাব কনফিগারেশন
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

# সার্ভার কনফিগারেশন
BASE_PHP_URL = "http://180.94.28.28/img/play.php?stream="

# আপনার ফাইল থেকে নেওয়া চ্যানেলের তালিকা
CHANNELS = [
    "T-Sports", "BEIN-SPORTS-USA", "STAR-SPORTS-1", "Star-Sports-2",
    "Star-Sports-Select-1", "star-Sports-Select-2", "Star-Sports-3",
    "Sony-Ten-1", "Sony-Ten-2", "Sony-Ten-3", "Sony-Ten-5", "PTV-Sports",
    "A-Sports", "Ten-Sports", "Ten-Cricket", "SUPERSPORT-CRICKET",
    "SKY-SPORTS-CRICKET", "WILLOW-TV", "BTV", "Jamuna-TV", "Maasranga-tv",
    "Nagorik-TV", "Somoy-TV", "GAZI-TV", "EKATTOR-TV", "CHANNEL-9",
    "DEEPTO-TV", "DBC-NEWS", "Independent-TV", "RTV", "ZEE-BANGLA",
    "STAR-JALSHA", "JALSHA-MOVIES", "SONY-AATH", "COLORS-BANGLA",
    "SUN-BANGLA", "STAR-PLUS", "SONY-MAX", "SONY-PIX", "ZEE-CINEMA",
    "CARTOON-NETWORK", "POGO", "DISCOVERY-KIDS", "DISCOVERY-BANGLA"
]

def get_token_link(channel_id):
    """সার্ভার থেকে টোকেনসহ অরিজিনাল লিঙ্ক বের করার ফাংশন"""
    try:
        url = f"{BASE_PHP_URL}{channel_id}"
        response = requests.get(url, timeout=15)
        # HTML এর ভেতর থেকে index.fmp4.m3u8?token=... লিঙ্কটি খুঁজে বের করা
        pattern = r'(http://180\.94\.28\.28:8097//[^\s"\']+index\.fmp4\.m3u8\?token=[^\s"\'&]+&remote=no_check_ip)'
        matches = re.findall(pattern, response.text)
        
        if matches:
            return matches[0]
        return None
    except Exception as e:
        print(f"❌ Error fetching {channel_id}: {e}")
        return None

def build_playlist():
    """সব চ্যানেলের টোকেন সংগ্রহ করে প্লেলিস্ট তৈরি করা"""
    m3u = "#EXTM3U\n\n"
    print("🚀 সার্ভার থেকে অটো-টোকেন সংগ্রহ করা হচ্ছে...")
    
    for ch in CHANNELS:
        token_url = get_token_link(ch)
        if token_url:
            m3u += f'#EXTINF:-1 group-title="FTPBD-Auto", {ch}\n'
            m3u += f"{token_url}\n\n"
            print(f"✅ সফল: {ch}")
        else:
            # যদি টোকেন না পাওয়া যায় তবে বেসিক লিঙ্কটি রাখা হবে
            m3u += f'#EXTINF:-1 group-title="Backup", {ch}\n'
            m3u += f"http://180.94.28.28:8097//{ch}/index.fmp4.m3u8?remote=no_check_ip\n\n"
            print(f"⚠️ টোকেন মেলেনি: {ch} (Backup লিঙ্ক যুক্ত করা হলো)")
            
    return m3u

def push_github(content):
    """গিটহাবে ফাইলটি আপডেট করার লজিক"""
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # বর্তমান ফাইলের SHA সংগ্রহ করা (আপডেট করার জন্য প্রয়োজন)
    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    # কন্টেন্ট এনকোড করা
    base64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": "Auto Update Playlist with Token",
        "content": base64_content,
    }
    if sha:
        data["sha"] = sha

    # গিটহাবে পুশ করা
    put_res = requests.put(api, headers=headers, json=data)
    
    if put_res.status_code in [200, 201]:
        print("🎉 সফলভাবে গিটহাবে প্লেলিস্ট আপডেট করা হয়েছে!")
    else:
        print(f"❌ গিটহাবে পুশ করতে সমস্যা হয়েছে: {put_res.text}")

if __name__ == "__main__":
    # ১. প্লেলিস্ট তৈরি করা
    playlist_content = build_playlist()
    
    # ২. গিটহাবে পুশ করা
    if GITHUB_TOKEN:
        push_github(playlist_content)
    else:
        print("❌ GH_TOKEN পাওয়া যায়নি। এনভায়রনমেন্ট চেক করুন।")
