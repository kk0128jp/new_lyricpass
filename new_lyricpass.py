import argparse
import urllib.request
import urllib.parse
import json
import datetime
import os
import sys
import re
import time
from bs4 import BeautifulSoup

LYRIC_FILE = "raw-lyrics-{:%Y-%m-%d-%H.%M.%S}.txt".format(datetime.datetime.now())
PASS_FILE = "wordlist-{:%Y-%m-%d-%H.%M.%S}.txt".format(datetime.datetime.now())
HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

allowed_chars = re.compile(r'[^a-zA-Z0-9\s\']')


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape song lyrics")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--artist", type=str, help="Single artist to scrape")
    group.add_argument("-i", "--infile", type=str, help="File with one artist per line")
    parser.add_argument("--min", type=int, default=8, help="Minimum passphrase length")
    parser.add_argument("--max", type=int, default=40, help="Maximum passphrase length")
    args = parser.parse_args()
    if args.infile and not os.access(args.infile, os.R_OK):
        print("[!] Cannot access input file")
        sys.exit(1)
    return args


def make_phrases(line, args):
    clean_lines = []
    final_lines = []

    line = re.sub('[àáâãäå]', 'a', line)
    line = re.sub('[èéêë]', 'e', line)
    line = re.sub('[ìíîï]', 'i', line)
    line = re.sub('[òóôõö]', 'o', line)
    line = re.sub('[ùúûü]', 'u', line)
    line = re.sub('[ñ]', 'n', line)
    line = allowed_chars.sub('', line)
    line = re.sub(r'\s\s+', ' ', line).strip()

    if "'" in line:
        clean_lines.append(re.sub("'", "", line))
    if ' and ' in line:
        clean_lines.append(re.sub(' and ', ' & ', line))
    if '&' in line:
        newline = re.sub('&', ' and ', line)
        newline = re.sub(r'\s+', ' ', newline).strip()
        clean_lines.append(newline)

    clean_lines.append(line)

    for item in clean_lines:
        if args.min <= len(item) <= args.max:
            final_lines.append(item)

    return final_lines


def search_genius_artist(artist_name):
    print(f"[+] Looking up artist {artist_name}")
    search_url = f"https://genius.com/api/search/multi?per_page=5&q={urllib.parse.quote(artist_name)}"
    try:
        req = urllib.request.Request(search_url, headers=HEADER)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))

        for section in data['response']['sections']:
            if section['type'] == 'artist':
                artist_info = section['hits'][0]['result']
                artist_id = artist_info['id']
                return get_artist_songs_by_id(artist_id)
    except Exception as e:
        print(f"[!] Error searching for artist: {e}")
        return []


def get_artist_songs_by_id(artist_id):
    song_urls = []
    page = 1
    per_page = 50

    while True:
        api_url = f"https://genius.com/api/artists/{artist_id}/songs?sort=popularity&per_page={per_page}&page={page}"
        try:
            req = urllib.request.Request(api_url, headers=HEADER)
            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))

            songs = data['response']['songs']
            if not songs:
                break

            for song in songs:
                if song['url'] not in song_urls:
                    song_urls.append(song['url'])

            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"[!] Error fetching songs: {e}")
            break

    print(f"[+] Found {len(song_urls)} songs for artist ID {artist_id}")
    return song_urls


def scrape_genius_lyrics(url):
    try:
        req = urllib.request.Request(url, headers=HEADER)
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})
        if lyrics_divs:
            lyrics_text = ""
            for div in lyrics_divs:
                for br in div.find_all('br'):
                    br.replace_with('\n')
                lyrics_text += div.get_text() + "\n"
            return lyrics_text.strip()
        return None
    except Exception:
        return None


def scrape_all_lyrics(url_list):
    raw_lyrics = set()
    for count, url in enumerate(url_list, 1):
        print(f"\rChecking song {count}/{len(url_list)}...       ", end='', flush=True)
        lyrics = scrape_genius_lyrics(url)
        if lyrics:
            raw_lyrics.add(lyrics)
        else:
            print(f"\n[!] Found no lyrics at {url}")
        time.sleep(1)
    print("\n")
    return raw_lyrics


def main():
    args = parse_args()
    artists = [args.artist] if args.artist else [line.strip() for line in open(args.infile)]
    all_urls = []
    for artist in artists:
        urls = search_genius_artist(artist)
        all_urls.extend(urls)

    if not all_urls:
        print("[!] No songs found, exiting")
        sys.exit(1)

    print(f"[+] Scraping lyrics from {len(all_urls)} songs...")
    raw_lyrics = scrape_all_lyrics(all_urls)

    if not raw_lyrics:
        print("[!] No lyrics found, exiting")
        sys.exit(1)

    print(f"[+] Found lyrics for {len(raw_lyrics)} songs")

    all_phrases = set()
    with open(LYRIC_FILE, 'w', encoding='utf-8') as outfile:
        for lyric in raw_lyrics:
            outfile.write(lyric + "\n\n")
            for line in lyric.split('\n'):
                line = line.strip()
                if line and not line.startswith('[') and not line.endswith(']'):
                    phrases = make_phrases(line, args)
                    all_phrases.update(phrases)

    print(f"[+] Wrote raw lyrics to {LYRIC_FILE}")

    with open(PASS_FILE, 'w', encoding='utf-8') as outfile:
        for phrase in sorted(all_phrases):
            outfile.write(phrase + "\n")

    print(f"[+] Wrote {len(all_phrases)} passphrases to {PASS_FILE}")
    print("[+] Done!")


if __name__ == "__main__":
    main()
