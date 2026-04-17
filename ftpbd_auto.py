import base64
import requests
import os

BASE_PAGE = "http://180.94.28.28/"

REPO = "nrjtvbd/ftpbd"
FILE_PATH = "playlist.m3u"

GITHUB_TOKEN = os.getenv("GH_TOKEN")


# ---------------------------
# FETCH & PARSE HTML
# ---------------------------
def get_channels():
    r = requests.get(BASE_PAGE, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    channels = []

    for a in soup.find_all("a"):
        onclick = a.get("onclick")
        img = a.find("img")

        if onclick and "stream=" in onclick:
            try:
                stream = onclick.split("stream=")[-1].split("'")[0]

                name = img.get("alt") if img and img.get("alt") else stream

                url = f"http://180.94.28.28/img/play.php?stream={stream}"

                channels.append((name, url))
            except:
                pass

    return channels


# ---------------------------
# BUILD M3U
# ---------------------------
def build_playlist(channels):
    m3u = "#EXTM3U\n\n"

    for name, url in channels:
        m3u += f'#EXTINF:-1 group-title="Live TV",{name}\n'
        m3u += f"{url}\n\n"

    return m3u


# ---------------------------
# PUSH TO GITHUB
# ---------------------------
def push_github(content):
    api = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.get(api, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    payload = {
        "message": "Auto IPTV HTML Scraper Update",
        "content": base64.b64encode(content.encode()).decode(),
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(api, headers=headers, json=payload)

    print("GitHub Status:", r.status_code)
    print(r.json())


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":

    print("Fetching channels...")
    channels = get_channels()

    print(f"Total channels found: {len(channels)}")

    playlist = build_playlist(channels)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(playlist)

    print("💾 Local playlist created!")

    push_github(playlist)

    print("✅ Done!")
