import requests



# মনিরুলের মতো আমরা বিভিন্ন সোর্স থেকে লিঙ্ক সংগ্রহ করবো

SOURCES = [

    "https://raw.githubusercontent.com/Hadi-The-Developer/BDIX-IPTV/main/playlist.m3u",

    "https://raw.githubusercontent.com/M3U-Sourcer/BD-IPTV/main/index.m3u"

]



def main():

    final_playlist = ["#EXTM3U"]

    print("🚀 Combining Playlists like Monirul...")

    

    for url in SOURCES:

        try:

            r = requests.get(url, timeout=10)

            if r.status_code == 200:

                lines = r.text.splitlines()

                # প্রথম লাইন (#EXTM3U) বাদ দিয়ে বাকিগুলো যোগ করা

                final_playlist.extend(lines[1:])

                print(f"✅ Source Success: {url[:30]}...")

        except:

            print(f"❌ Source Failed: {url[:30]}...")



    with open("playlist.m3u", "w") as f:

        f.write("\n".join(final_playlist))

    print("\n🎉 Playlist Updated Successfully!")



if __name__ == "__main__":

    main()
