from contextlib import contextmanager
from pathlib import Path

import pygpod


@contextmanager
def open_db(mountpoint: str):
    """
    Open iTunes DB and auto save
    """

    if not Path(mountpoint).exists():
        raise FileNotFoundError(f"iPod not mounted at {mountpoint}")

    with pygpod.Database(mountpoint) as db:
        yield db


def list_tracks(mountpoint: str) -> list[dict]:
    """

    """

    with open_db(mountpoint) as db:
        return [
            {
                "id": t.track_id,
                "title": t.title,
                "artist": t.artist,
                "album": t.album,
                "duration": t.duration,
            }
            for t in db.tracks
        ]

def add_track(mountpoint: str, src: str | Path, **overrides) -> dict:
    """

    """

    with open_db(mountpoint) as db:
        track = db.add_track(str(src), **overrides)
        
        return {"id": track.track_id, "title": track.title, "ipod_path": track.ipod_path}


def remove_track(mountpoint: str, track_id: int, delete_file: bool = True) -> None:

    with open_db(mountpoint) as db:
        track = next((t for t in db.tracks if t.track_id == track_id), None)

        if track is None:
            raise LookupError(f"No track with id {track_id}")
        
        db.remove_track(track, delete_file=delete_file)






