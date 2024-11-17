import requests
import time
global TIMEOUT
TIMEOUT = 10

urls = [
    "",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_uk.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_usa.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_ireland.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_canada.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_australia.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_zz_news_en.m3u8"
]

def fetch_page_contents(url):
    if url == "":
        return("""#EXTM3U
#EXTINF:-1 tvg-id="CNNGO.us" tvg-logo="https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cnn-us.png" group-title="News",CNN GO
https://turnerlive.warnermediacdn.com/hls/live/586495/cnngo/cnn_slate/VIDEO_0_3564000.m3u8
#EXTINF:-1 tvg-id="CNN576i.us" tvg-logo="https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cnn-us.png" group-title="News",CNN 576i
https://stream1.cinerama.uz/1259/tracks-v1a1/mono.m3u8
#EXTINF:-1 tvg-id="CNNINT.us" tvg-logo="https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cnn-us.png" group-title="News",CNN INT
https://turnerlive.warnermediacdn.com/hls/live/586497/cnngo/cnni/VIDEO_0_3564000.m3u8""")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def parse_m3u8(contents, m3u8_dict):
    lines = contents.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].startswith("#EXTINF:"):
            key = lines[i + 1]
            value = lines[i]
            channel_name = value.split(",")[-1].strip()
            if channel_name:
                m3u8_dict[key] = {
                    "info": value,
                    "channel_name": channel_name
                }
    return m3u8_dict


def is_url_alive(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False

m3u8_dict = {}

for url in urls:
    contents = fetch_page_contents(url)
    if contents:
        m3u8_dict = parse_m3u8(contents, m3u8_dict)

sorted_m3u8_dict = dict(sorted(m3u8_dict.items(), key=lambda item: item[1]["channel_name"].lower()))

with open('playlist.m3u8', 'w', encoding='utf-8') as file:
    file.write("#EXTM3U\n")
    file.write("Generated on "+str(int(time.time()))+"\n")
    for key, value in sorted_m3u8_dict.items():
        channel_name = value["channel_name"]
        info = value["info"]
        if "Not 24/7" not in channel_name:
            if "geo" in info.lower() or "block" in info.lower():
                print(f"Channel: {channel_name}\n")
                file.write(f"{info}\n{key}\n")
            else:
                if is_url_alive(key):
                    print(f"Channel: {channel_name}\n")
                    file.write(f"{info}\n{key}\n")
                else:
                    pass
