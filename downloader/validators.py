"""URL and path validation for the YouTube downloader."""

import re
from pathlib import Path
from urllib.parse import urlparse

from .config import YOUTUBE_DOMAINS

# Relaxed YouTube URL pattern: supports watch, playlist, embed, shorts
YOUTUBE_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(youtube\.com|youtu\.be)/.+",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """
    Check if the string looks like a valid YouTube URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL appears to be a valid YouTube URL, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url:
        return False
    if not YOUTUBE_URL_PATTERN.match(url):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and any(
            domain in parsed.netloc for domain in YOUTUBE_DOMAINS
        )
    except Exception:
        return False


def normalize_output_path(path: str | Path) -> Path:
    """
    Convert user path to an absolute Path. Does not create the directory.

    Args:
        path: User-provided path string or Path.

    Returns:
        Absolute Path for the output directory.
    """
    p = Path(path).expanduser().resolve()
    return p


def ensure_output_dir(path: Path) -> Path:
    """
    Create the output directory if it does not exist.

    Args:
        path: Directory path to ensure.

    Returns:
        The same path for chaining.

    Raises:
        OSError: If the directory cannot be created (e.g. permission error).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
