"""YouTube download logic using yt-dlp."""

import logging
import shutil
from pathlib import Path
from typing import Callable

import yt_dlp

from .config import (
    FFMPEG_EXTRACT_AUDIO,
    OUTPUT_TEMPLATE,
    OUTPUT_TEMPLATE_WAV,
    SINGLE_VIDEO_TEMPLATE,
    SINGLE_VIDEO_TEMPLATE_WAV,
)
from .validators import ensure_output_dir

logger = logging.getLogger(__name__)

# Type for progress callback: (current: int, total: int | None, filename: str, status: str) -> None
ProgressCallback = Callable[[int, int | None, str, str], None]


class YouTubeDownloadService:
    """
    Service class for downloading YouTube playlists or single videos via yt-dlp.
    """

    def __init__(
        self,
        output_dir: Path,
        download_video: bool = False,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """
        Initialize the download service.

        Args:
            output_dir: Base directory where files will be saved.
            download_video: If True, download video; if False, download audio (WAV by default, see config).
            progress_callback: Optional callback(current_index, total, filename, status).
        """
        self._output_dir = ensure_output_dir(Path(output_dir))
        self._download_video = download_video
        self._progress_callback = progress_callback

    def _check_ffmpeg(self) -> None:
        """Raise if FFmpeg is not available (required for audio extraction)."""
        if shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "FFmpeg is not installed or not in PATH. "
                "Audio extraction to WAV requires FFmpeg. "
                "Install: macOS: brew install ffmpeg | Ubuntu: sudo apt install ffmpeg"
            )

    def _build_opts(self, is_playlist: bool) -> dict:
        """Build yt-dlp options dict. Audio mode: WAV with explicit .wav output path."""
        if self._download_video:
            outtmpl = OUTPUT_TEMPLATE if is_playlist else SINGLE_VIDEO_TEMPLATE
        else:
            # Force .wav extension so output is always WAV (postprocessor converts to this)
            outtmpl = OUTPUT_TEMPLATE_WAV if is_playlist else SINGLE_VIDEO_TEMPLATE_WAV
        outtmpl = str(self._output_dir / outtmpl)
        opts: dict = {
            "format": "bestaudio/best" if not self._download_video else "bestvideo+bestaudio/best",
            "outtmpl": outtmpl,
            "ignoreerrors": True,
            "no_warnings": False,
            "quiet": False,
            "extract_flat": False,
        }
        if not self._download_video:
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": FFMPEG_EXTRACT_AUDIO,
                }
            ]
            # Standard WAV for DJ software: 44.1kHz, stereo, 16-bit PCM (DJUCED-compatible)
            opts["postprocessor_args"] = {
                "extractaudio+ffmpeg": [
                    "-ar", "44100",
                    "-ac", "2",
                    "-acodec", "pcm_s16le",
                ],
            }
        return opts

    def _progress_hook(self, d: dict, current: int, total: int | None) -> None:
        """Internal progress hook that forwards to callback and logs."""
        status = d.get("status", "downloading")
        filename = d.get("filename", "?") or d.get("info_dict", {}).get("title", "?")
        if isinstance(filename, Path):
            filename = filename.name
        elif "/" in filename:
            filename = filename.split("/")[-1]
        if self._progress_callback:
            self._progress_callback(current, total, filename, status)
        if status == "finished":
            logger.info("Finished: %s", filename)
        elif status == "downloading" and d.get("_percent_str"):
            logger.debug("Progress: %s %s", filename, d.get("_percent_str", ""))

    def get_playlist_info(self, url: str) -> dict | None:
        """
        Fetch playlist or video info without downloading.

        Args:
            url: YouTube playlist or video URL.

        Returns:
            Dict with 'entries' (list of entries) and 'title' or similar, or None on error.
        """
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except yt_dlp.utils.DownloadError as e:
            logger.error("Failed to fetch playlist info: %s", e)
            return None
        except Exception as e:
            logger.exception("Unexpected error fetching info: %s", e)
            return None

    def download(self, url: str) -> tuple[int, int]:
        """
        Download a playlist or single video.

        Args:
            url: YouTube playlist or single video URL.

        Returns:
            Tuple of (success_count, failure_count).
        """
        if not self._download_video:
            self._check_ffmpeg()
        info = self.get_playlist_info(url)
        if not info:
            logger.error("Invalid or inaccessible URL: %s", url)
            return 0, 0

        entries = info.get("entries") or []
        if not entries:
            total = 1
        else:
            entries = [e for e in entries if e]
            total = len(entries)

        logger.info("Total items to process: %s", total)
        is_playlist = total > 1

        opts = self._build_opts(is_playlist)
        success_count: list[int] = [0]  # mutable for closure
        current: list[int] = [0]

        def progress_hook(d: dict) -> None:
            status = d.get("status", "")
            if status == "finished":
                success_count[0] += 1
            # Current index: we don't have it from yt-dlp for playlist, use success + downloading
            if status == "downloading":
                current[0] = success_count[0] + 1
            elif status == "finished":
                current[0] = success_count[0]
            self._progress_hook(d, current[0], total)

        opts["progress_hooks"] = [progress_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            logger.error("Download error: %s", e)
        except Exception as e:
            logger.exception("Download failed: %s", e)

        failures = total - success_count[0]
        return success_count[0], failures
