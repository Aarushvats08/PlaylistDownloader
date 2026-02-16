"""YouTube playlist and video downloader package."""

from .config import (
    AUDIO_FORMAT,
    FFMPEG_EXTRACT_AUDIO,
    OUTPUT_TEMPLATE,
    SINGLE_VIDEO_TEMPLATE,
    get_default_output_dir,
)
from .validators import (
    ensure_output_dir,
    is_valid_youtube_url,
    normalize_output_path,
)
from .youtube_service import YouTubeDownloadService

__all__ = [
    "YouTubeDownloadService",
    "is_valid_youtube_url",
    "normalize_output_path",
    "ensure_output_dir",
    "get_default_output_dir",
    "OUTPUT_TEMPLATE",
    "SINGLE_VIDEO_TEMPLATE",
    "AUDIO_FORMAT",
    "FFMPEG_EXTRACT_AUDIO",
]
