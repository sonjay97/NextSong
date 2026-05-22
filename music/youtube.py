import uuid
from pathlib import Path

import yt_dlp
from django.conf import settings

def search(query: str, limit: int = 10) -> list[dict]:
    """Return YT search results without downloading"""

    if not query.strip():
        return []

    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)

    entries = info.get("entries") or []

    results = []

    for e in entries:
        if not e:
            continue
        results.append({
            "id": e.get("id"),
            "title": e.get("title", "Unknown"),
            "url": e.get("webpage_url") or f"https://www.youtube.com/watch?v={e.get('id')}",
            "duration": e.get("duration"),
            "uploader": e.get("uploader") or e.get("channel")
        })
    
    return results

def download_mp3(url: str) -> dict:
    """Download audio and convert to mp3"""

    out_dir = Path(settings.TMP_DOWNLOADS)
    out_dir.mkdir(parents=True, exist_ok=True)

    job_id = uuid.uuid4().hex

    outtmpl = str(out_dir / f"{job_id}.%(ext)s")

    opts = {
        "format": "bestaudi/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warning": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    mp3_path = out_dir / f"{job_id}.mp3"

    if not mp3_path.exists():
        raise FileNotFoundError(f"Expected MP3 at {mp3_path}")

    return {
        "path": mp3_path,
        "title": info.get("title", "Unknown"),
        "job_id": job_id
    }
    