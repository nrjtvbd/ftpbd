import os
import base64
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

# Channel List (Apnar ftpbd.txt file onuzayi)
CHANNELS = [
    "T-Sports", "BEIN-SPORTS-USA", "STAR-SPORTS-1", "Star-Sports-2",
    "Star-Sports-Select-1", "star-Sports-Select-2", "Star-Sports-3",
    "Sony-Ten-1", "Sony-Ten-2", "Sony-Ten-3", "Sony-Ten-5", "PTV-Sports",
    "A-Sports", "Ten-Sports", "Ten-Cricket", "BTV", "Jamuna-TV", 
    "Maasranga-tv", "Nagorik-TV", "Somoy-TV", "GAZI-TV", "EKATTOR-TV", 
    "ZEE-BANGLA", "STAR-JALSHA", "SONY-AATH", "COLORS-BANGLA", 
    "DISCOVERY-BANGLA", "NAT-GEO-BANGLA"
]

def sniff_link(channel_id):
    """Headless browser diye network traffic theke token-sho link sniff kora"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Network logging enable kora
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    
    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
    url = f"http://180.94.28.28/img/play.php?stream={channel_id}"
    
    found_url = None
    try:
        driver.get(url)
        print(f"⌛ Waiting for {channel_id} to generate token...")
        time.sleep(12) # JS execute houar jonno somoy
        
        logs = driver.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"]:
                request_url = log["params"]["request"]["url"]
                # Link-e token ache kina check kora
                if "index.fmp4.m3u8?token=" in request_url:
                    found_url = request_url
                    if "remote=no_check_ip" not in found_url:
                        found_url += "&remote=no_check_ip"
                    break
    except Exception as e:
        print(f"❌ Error sniffing {channel_id}: {e}")
    
    driver.quit()
    
    # Link na pawa gele backup link dewa
    if not found_url:
        found_url = f"http://180.94.28.28:8097//{channel_id}/index.fmp4.m3u8?remote=no_check_ip"
    
    return found_url

def build_playlist():
    """Playlist toiri kora"""
    m3u = "#EXTM3U\n\n"
    print("🚀 Sniffing session started...")
    
    for ch in CHANNELS:
        final_link = sniff_link(ch)
        m3u += f'#EXTINF:-1 group-title="Auto-Update", {ch}\n'
        m3u += f"{final_link}\n\n"
        print(f"✅ Finished: {ch}")
            
    return m3u

def push_github(content):
    """GitHub-e playlist update kora"""
    api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # SHA check kora (File replace korar jonno dorkar)
    res = requests.get(api_url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    # Content-ke Base64 encode kora
    base64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": "Update playlist with auto-sniffed tokens",
        "content": base64_content,
    }
    if sha:
        data["sha"] = sha

    # Put request pathano
    put_res = requests.put(api_url, headers=headers, json=data)
    
    if put_res.status_code in [200, 201]:
        print("🎉 Successfully updated playlist.m3u on GitHub!")
    else:
        print(f"❌ Failed to push: {put_res.text}")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Error: GH_TOKEN not found in environment secrets!")
    else:
        playlist_data = build_playlist()
        push_github(playlist_data)
