import base64
import requests
import os
import json

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "nrjtvbd/ftpbd"
CF_WORKER_URL = "https://ftpbd.drrkrana.workers.dev/?id=" # Apnar worker link

CHANNELS = ["T-Sports", "STAR-SPORTS-1", "Sony-Ten-1", "Jamuna-TV", "ZEE-BANGLA"] # List barate paren

def build_files():
    m3u = "#EXTM3U\n"
    json_data = []

    print("🚀 Fetching fresh tokens via Cloudflare...")
    for ch in CHANNELS:
        try:
            # Cloudflare theke fresh link ana
            res = requests.get(f"{CF_WORKER_URL}{ch}", timeout=10)
            final_link = res.text.strip()
            
            # M3U Format
            m3u += f'#EXTINF:-1 group-title="FTPBD", {ch}\n{final_link}\n'
            
            # JSON Format
            json_data.append({
                "name": ch,
                "url": final_link,
                "logo": f"http://180.94.28.28/assets/images/{ch}.png"
            })
            print(f"✅ {ch} updated.")
        except:
            print(f"❌ Failed: {ch}")

    return m3u, json.dumps(json_data, indent=4)

def push_to_github(filename, content):
    api = f"https://api.github.com/repos/{REPO}/contents/{filename}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {"message": f"Update {filename}", "content": encoded}
    if sha: data["sha"] = sha
    
    requests.put(api, headers=headers, json=data)

if __name__ == "__main__":
    m3u_content, json_content = build_files()
    push_to_github("playlist.m3u", m3u_content)
    push_to_github("playlist.json", json_content)
    print("🎉 All files updated on GitHub!")
