"""Configuration constants and defaults for the YouTube downloader."""

from pathlib import Path

# Output templates (yt-dlp format)
# Playlists get a subfolder named after the playlist; files go inside it.
OUTPUT_TEMPLATE = "%(playlist_title)s/%(title)s.%(ext)s"
OUTPUT_TEMPLATE_MP3 = "%(playlist_title)s/%(title)s.mp3"  # Force MP3 extension for audio

# Single video fallback when no playlist
SINGLE_VIDEO_TEMPLATE = "%(title)s.%(ext)s"
SINGLE_VIDEO_TEMPLATE_MP3 = "%(title)s.mp3"  # Force MP3 extension for audio
# Force WAV extension so output is always .wav (postprocessor converts to this)
OUTPUT_TEMPLATE_WAV = "%(playlist_title)s/%(title)s.wav"
SINGLE_VIDEO_TEMPLATE_WAV = "%(title)s.wav"

# App-level folder for all downloads: single files go here; playlists get one subfolder by name
DOWNLOAD_DIR_NAME = "download"

# Supported URL patterns
YOUTUBE_DOMAINS = ("youtube.com", "youtu.be", "www.youtube.com")

# Audio postprocessor: extract to this format (e.g. "mp3", "wav")
AUDIO_FORMAT = "wav"
FFMPEG_EXTRACT_AUDIO = "wav"

# Progress reporting
PROGRESS_INTERVAL = 0.5  # seconds between progress updates

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_app_root() -> Path:
    """Return the app root directory (youtube_downloader package parent)."""
    return Path(__file__).resolve().parent.parent


def get_default_output_dir() -> Path:
    """Return the app's download folder. Single files go here; playlists get one subfolder by playlist name."""
    return get_app_root() / DOWNLOAD_DIR_NAME
