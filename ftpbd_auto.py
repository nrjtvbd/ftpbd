import os
import base64
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

CHANNELS = ["T-Sports", "STAR-SPORTS-1", "Sony-Ten-1", "Jamuna-TV"] # Apnar baki ID gulo ekhane add korun

def sniff_link(channel_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Network logs enable kora jate link sniff kora jay
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    
    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
    url = f"http://180.94.28.28/img/play.php?stream={channel_id}"
    
    try:
        driver.get(url)
        time.sleep(10) # Page load ebong JS run houar somoy dewa
        
        logs = driver.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"]:
                request_url = log["params"]["request"]["url"]
                if "index.fmp4.m3u8?token=" in request_url:
                    driver.quit()
                    return request_url
    except Exception as e:
        print(f"Error sniffing {channel_id}: {e}")
    
    driver.quit()
    return f"http://180.94.28.28:8097//{channel_id}/index.fmp4.m3u8?remote=no_check_ip"

def build_playlist():
    m3u = "#EXTM3U\n"
    for ch in CHANNELS:
        print(f"🔍 Sniffing: {ch}")
        link = sniff_link(ch)
        m3u += f'#EXTINF:-1, {ch}\n{link}\n'
    return m3u

# Baki push_github function-ti apnar ager motoi thakbe...
