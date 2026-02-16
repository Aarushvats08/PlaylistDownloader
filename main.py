#!/usr/bin/env python3
"""
YouTube Playlist / Video Downloader — CLI entry point.

Accepts a YouTube playlist or single video URL and downloads audio (MP3) or video
into a user-selected folder.
"""

import argparse
import logging
import sys
from pathlib import Path

from downloader import (
    YouTubeDownloadService,
    ensure_output_dir,
    get_default_output_dir,
    is_valid_youtube_url,
    normalize_output_path,
)
from downloader.config import LOG_DATE_FORMAT, LOG_FORMAT


def setup_logging(verbose: bool = False) -> None:
    """Configure console logging with a clean, structured format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        stream=sys.stdout,
        force=True,
    )
    # Reduce noise from yt-dlp
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Download a YouTube playlist or single video as MP3 (default) or video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/playlist?list=PLxxx"
  %(prog)s "https://www.youtube.com/watch?v=VIDEO_ID" -o ./my_music
  %(prog)s "https://youtu.be/VIDEO_ID" --video
        """,
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="YouTube playlist or single video URL",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        metavar="DIR",
        help="Output folder (default: app's download/; playlists get one subfolder by playlist name)",
    )
    parser.add_argument(
        "--video",
        action="store_true",
        help="Download video instead of audio (MP3)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def get_user_input(prompt: str, default: str | None = None) -> str:
    """Read a line from stdin with optional default."""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    try:
        value = input(prompt).strip()
        return value if value else (default or "")
    except (EOFError, KeyboardInterrupt):
        return default or ""


def run_download(url: str, output_dir: Path, download_video: bool) -> int:
    """
    Run the download and return exit code (0 = success, 1 = failure).
    """
    logger = logging.getLogger(__name__)

    def progress_callback(current: int, total: int | None, filename: str, status: str) -> None:
        if total is not None and total > 0:
            logger.info("[%d/%d] %s — %s", current, total, status, filename)
        else:
            logger.info("%s — %s", status, filename)

    service = YouTubeDownloadService(
        output_dir=output_dir,
        download_video=download_video,
        progress_callback=progress_callback,
    )
    try:
        success, failure = service.download(url)
    except RuntimeError as e:
        logger.error("%s", e)
        return 1
    logger.info("Done. Success: %d, Failed: %d", success, failure)
    return 0 if failure == 0 else 1


def main() -> int:
    """Entry point: validate input, then run download."""
    args = parse_args()
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    url = args.url or get_user_input("YouTube playlist or video URL")
    if not url:
        logger.error("No URL provided.")
        return 1

    if not is_valid_youtube_url(url):
        logger.error("Invalid YouTube URL: %s", url)
        return 1

    # Use -o if provided; otherwise default download folder (no prompt)
    output_dir = normalize_output_path(args.output) if args.output else get_default_output_dir()

    try:
        ensure_output_dir(output_dir)
    except OSError as e:
        logger.error("Cannot create output folder %s: %s", output_dir, e)
        return 1

    logger.info("URL: %s", url)
    logger.info("Output: %s | Mode: %s", output_dir, "video" if args.video else "audio (WAV)")
    return run_download(url, output_dir, args.video)


if __name__ == "__main__":
    sys.exit(main())
