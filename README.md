# 🎤 lyricpass-genius

A command-line utility to scrape song lyrics from [Genius](https://genius.com) and generate passphrase-style wordlists from them.

This tool is inspired by and adapted from the original [`lyricpass`](https://github.com/initstring/lyricpass) project by [initstring](https://github.com/initstring), which used lyrics.com. This version uses the Genius public API (no API key required) and supports full artist discographies via pagination.

---

## 📌 Overview

`lyricpass-genius` allows you to:

- Search for an artist on Genius
- Retrieve all available song lyrics for that artist
- Clean and filter the lyrics into usable passphrases
- Output two files:
  - `raw-lyrics-<timestamp>.txt`: all scraped lyrics
  - `wordlist-<timestamp>.txt`: cleaned passphrase candidates

This is useful for generating human-readable passphrases, CTF wordlists, or just exploring lyrical content programmatically.

---

## 🚀 Usage

### Scrape a single artist:

```bash
python test_lyricpass.py -a "Artist Name"
```

### Scrape multiple artists from a file:

```bash
python test_lyricpass.py -i /path/to/artists.txt
```

### Optional arguments:

- `--min`: Minimum passphrase length (default: 8)
- `--max`: Maximum passphrase length (default: 40)

### Example:

```bash
python test_lyricpass.py -a "Adele" --min 10 --max 30
```

---

## 📂 Output

After running, two files will be created in the current directory:

- `raw-lyrics-YYYY-MM-DD-HH.MM.SS.txt`: Full lyrics scraped from Genius
- `wordlist-YYYY-MM-DD-HH.MM.SS.txt`: Cleaned, deduplicated passphrases

---

## 🛠 Features

- ✅ No Genius API key required
- ✅ Handles artist pagination to retrieve full discographies
- ✅ Filters out brackets, special characters, and short/long lines
- ✅ Supports multiple artists via input file
- ✅ Generates passphrase variants (e.g., with/without apostrophes, and/&)

---

## 📎 Credits

This project is based on [`lyricpass`](https://github.com/initstring/lyricpass) by [initstring](https://github.com/initstring), originally designed to scrape lyrics from lyrics.com. This version adapts the concept for Genius and improves coverage by using their public API with pagination.

---

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Respect copyright laws and the terms of service of any site you scrape.

