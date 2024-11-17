import requests

urls = [
    "https://raw.githubusercontent.com/stepheneasleywalsh/iptv/refs/heads/main/adhoc.m3u8",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_uk.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_usa.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_ireland.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_canada.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_australia.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_zz_news_en.m3u8"
]

def fetch_page_contents(url):
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

def is_m3u8_stream_live(url):
    if "m3u" not in url.lower():
        return False
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "#EXTM3U" in response.text and "#EXTINF" in response.text:
            return True
        return False
    except requests.exceptions.RequestException:
        return False

m3u8_dict = {}

for url in urls:
    contents = fetch_page_contents(url)
    if contents:
        m3u8_dict = parse_m3u8(contents, m3u8_dict)

sorted_m3u8_dict = dict(sorted(m3u8_dict.items(), key=lambda item: item[1]["channel_name"].lower()))

with open('playlist.m3u8', 'w', encoding='utf-8') as file:
    file.write("#EXTM3U\n")
    for key, value in sorted_m3u8_dict.items():
        channel_name = value["channel_name"]
        info = value["info"]
        if "Not 24/7" not in channel_name:
            if "geo" in info.lower() or "block" in info.lower():
                print(f"MAYBE: {channel_name} {key}")
                file.write(f"{info}\n{key}\n")
            else:
                print(f"testing: {channel_name} {key}")
                if is_m3u8_stream_live(key):
                    print(f"YES: {channel_name} {key}")
                    file.write(f"{info}\n{key}\n")
                else:
                    print(f"NO: {channel_name} {key}")
        else:
            print(f"MAYBE: {channel_name} {key}")
            file.write(f"{info}\n{key}\n")
