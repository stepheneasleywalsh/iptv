import requests
global country
import re

country = "US"  # <------------------

class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'

urls = [
    "https://raw.githubusercontent.com/stepheneasleywalsh/iptv/refs/heads/main/adhoc.m3u8",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_uk.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_usa.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_ireland.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_canada.m3u8",
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
    if country == "IE":
        C = "Free"
    else:
        C = country
    lines = contents.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].startswith("#EXTINF:"):
            key = lines[i + 1]
            value = lines[i]
            channel_name = value.split(",")[-1].strip()
            try:
                old_text = r'group-title=".*?"'
                new_text = "group-title=Region-\"" + C + "\""
                value = re.sub(old_text, new_text, value)
            except:
                pass
            if channel_name:
                m3u8_dict[key] = {
                    "info": value,
                    "channel_name": channel_name
                }
    return m3u8_dict


def is_m3u8_stream_live(url):
    for p in ["playlistIE.m3u8", "playlistUK.m3u8", "playlistUS.m3u8", "playlistCA.m3u8"]:
        with open(p, 'r', encoding='utf-8') as file:
            checked = file.read()
            if url in checked:
                return False
    if ".m3u" in url.lower() or ".ts" in url.lower() or ".mpd" in url.lower():
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.RequestException:
            return False
    else:
        return False


def combine_m3u8_playlists(output_file, *input_files):
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("#EXTM3U\n")
            for input_file in input_files:
                with open(input_file, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        if not line.strip() == "#EXTM3U":
                            outfile.write(line)
        print(f"Combined playlist saved to {output_file}")
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
    except Exception as e:
        print(f"Error combining playlists: {e}")


####################################################################################################################################
combine_m3u8_playlists("playlist.m3u8","playlistIE.m3u8","playlistUK.m3u8","playlistUS.m3u8","playlistCA.m3u8")
m3u8_dict = {}
for url in urls:
    contents = fetch_page_contents(url)
    if contents:
        m3u8_dict = parse_m3u8(contents, m3u8_dict)
sorted_m3u8_dict = dict(sorted(m3u8_dict.items(), key=lambda item: item[1]["channel_name"].lower()))
with open('playlist' + country + '.m3u8', 'w', encoding='utf-8') as file:
    file.write("#EXTM3U\n")
    for key, value in sorted_m3u8_dict.items():
        channel_name = value["channel_name"]
        info = value["info"]
        if "not 24" not in channel_name.lower():
            if is_m3u8_stream_live(key):
                file.write(f"{info}\n{key}\n")
                print(f"{Colors.GREEN}{info}\n{key}\n{Colors.RESET}")
            else:
                print(f"{Colors.RED}{info}\n{key}\n{Colors.RESET}")
combine_m3u8_playlists("playlist.m3u8","playlistIE.m3u8","playlistUK.m3u8","playlistUS.m3u8","playlistCA.m3u8")
####################################################################################################################################