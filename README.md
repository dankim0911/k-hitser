# K-Pop Hitster

A homebrew K-pop version of **HITSTER**, using QR codes to play timed song clips from YouTube.

## How It Works

Each physical card has:

* **Front:** QR code
* **Back:** Song title, artist, and release year

Scanning the QR code opens the web app with a specific card:

```text
https://YOUR-USERNAME.github.io/kpop-hitster/?card=42
```

The app loads the corresponding YouTube video and plays only the configured portion of the song.

## Project Structure

```text
kpop-hitster/
├── .gitignore
├── generate_songs.py
├── khitser-songs.csv
├── index.html
├── README.md
├── requirements.txt
└── songs.json
```

## Setup

Install Python 3.8 or newer. The song generator uses only Python's standard library, so there are no third-party packages to install. `requirements.txt` is kept as the dependency list if external packages are added later.

On Windows, create a virtual environment and use its Python executable:

```powershell
py -m venv .venv
.venv\Scripts\python.exe generate_songs.py
```

On macOS or Linux:

```sh
python3 -m venv .venv
.venv/bin/python generate_songs.py
```

To preview the site locally, start Python's built-in web server from the project folder:

```text
python -m http.server 8000
```

Then open `http://localhost:8000/?card=1` in a browser. Use `py -m http.server 8000` on Windows if `python` is not on your PATH.

## Song Data

Songs are stored in `songs.json`:

```json
{
  "id": 1,
  "title": "Gee",
  "artist": "Girls' Generation",
  "year": 2009,
  "videoId": "YOUTUBE_VIDEO_ID",
  "start": 47,
  "end": 77
}
```

* `id` — Unique card number
* `title` — Song title
* `artist` — Artist/group
* `year` — Release year
* `videoId` — YouTube video ID
* `start` — Clip start time in seconds
* `end` — Clip end time in seconds

To regenerate `songs.json` after editing `khitser-songs.csv`, run:

```text
python generate_songs.py
```

The CSV columns are `Artist,Title,Year,VideoId,Start,End`. `VideoId` accepts a YouTube video ID or URL. You can also pass input and output paths:

```text
python generate_songs.py path/to/songs.csv path/to/songs.json
```

## Hosting

The app is designed to run as a **static GitHub Pages site**. No backend or database is required.

Enable GitHub Pages under:

**Repository → Settings → Pages → Deploy from branch → main → `/ (root)`**

## Future Plans

* Generate QR codes automatically from card IDs
* Generate printable card sheets
* Add a play button to handle browser autoplay restrictions
* Support hundreds of cards
* Make it easy to replace unavailable YouTube videos
