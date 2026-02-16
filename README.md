# YouTube Playlist / Video Downloader

A minimal CLI tool to download a YouTube playlist or single video as **WAV** (default) or video, using **yt-dlp** and a clean Python layout.

## Requirements

- **Python 3.11+**
- **FFmpeg** (for audio extraction; optional if you only download video)

Audio is extracted as **WAV** (via yt-dlp’s `preferredquality` by default; set `FFMPEG_EXTRACT_AUDIO` to `"mp3"` in `downloader/config.py` for MP3.

Install FFmpeg:

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** [FFmpeg downloads](https://ffmpeg.org/download.html)

## Setup

1. **Clone or copy** the `youtube_downloader` folder.

2. **Create a virtual environment** (recommended):

   ```bash
   cd youtube_downloader
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## How to Run

From the `youtube_downloader` directory (with the venv activated):

```bash
python main.py [URL] [-o OUTPUT_DIR] [--video] [-v]
```

- **URL** — YouTube playlist or single video URL (can be asked interactively if omitted).
- **-o, --output** — Optional. Output folder (default: app’s **`download/`** folder). No prompt; use this only to override. For playlists, one subfolder with the **playlist name** is created inside and files are saved there.
- **--video** — Download video instead of audio (WAV).
- **-v, --verbose** — Debug logging.

If you don’t pass a URL, the script will prompt only for the URL (not for the output folder).

## Where files are saved

- **Default:** All downloads go into the app’s **`download/`** folder (inside `youtube_downloader/`).
- **Single video/audio:** File saved directly in **`download/`** (no subfolder).
- **Playlist:** One subfolder named after the playlist is created (e.g. `download/My Playlist/`), and each track is saved inside it.
- Use **`-o DIR`** to choose a different base folder; structure is the same (single files in that folder, playlists in one subfolder by name).

## Example Commands

```bash
# Playlist → files into download/<Playlist Name>/
python main.py "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

# Single video/audio → file into download/
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Custom folder (single in folder, playlist gets one subfolder by name)
python main.py "https://youtu.be/VIDEO_ID" -o ./my_music

# Video format
python main.py "https://youtu.be/VIDEO_ID" --video -o ./videos

# Interactive: no args, then enter URL when asked (output folder is always download/ unless -o is used)
python main.py
```

## Project Structure (Architecture)

```
youtube_downloader/
├── main.py                 # CLI entry: argparse, prompts, logging, run_download()
├── download/               # Default save location (single files here; playlists in one subfolder by name)
├── downloader/
│   ├── __init__.py         # Package exports
│   ├── config.py           # Constants (templates, formats, defaults)
│   ├── validators.py       # URL validation, path normalization, ensure_output_dir()
│   └── youtube_service.py  # YouTubeDownloadService: get_playlist_info(), download()
├── requirements.txt
└── README.md
```

- **main.py** — Orchestration only: parse args, validate URL/path, set up logging, call the service.
- **downloader/config.py** — Central place for output templates, audio format, and defaults.
- **downloader/validators.py** — Reusable validation and path handling (no I/O in core logic).
- **downloader/youtube_service.py** — All yt-dlp usage: options, progress hooks, single `download(url)` call. Uses `ignoreerrors` so one failure doesn’t stop the rest.

The app uses **yt-dlp’s Python API** (no shell subprocess). Output paths follow the template: `%(playlist_title)s/%(title)s.%(ext)s` for playlists, and `%(title)s.%(ext)s` for a single video. Audio is converted to MP3 via the FFmpeg postprocessor.

## Error Handling

- **Invalid URL** — Rejected before any download; message printed.
- **Private / unavailable / network errors** — Logged; remaining items continue (yt-dlp `ignoreerrors`).
- **Missing output directory** — Created automatically when possible; otherwise a clear error is shown.

## License

Use and modify as needed for your project.
# PlaylistDownloader
