import json
import pygpod
from js import document, window
from pyodide.ffi import to_js


MOUNT = "/iPod"

pyodide = None
nativefs = None
db = None

async def load_library():
    
    global db
    

    db = pygpod.Database(MOUNT)

    render_tracks(tracks_to_json())

    track_count = len(json.loads(tracks_to_json()))

    label = "track" if count == 1 else "tracks"

    set_status(f"iPod Connected ({track_count} {label}) Read")



def set_status(text):

    el = document.getElementById("ipod-status")

    if el: 
        el.textContent = text

def escape_html(text):

    s = str(text)
    
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def format_duration(seconds):

    if seconds is None:
        return ""
    
    try:
        total = int(float(seconds))
    
    except (TypeError, ValueError):
        return ""

    minutes, secs = divmod(total, 60)

    return f"{minutes}:{secs:02d}"

def tracks_to_json():

    if db is None:
        return "[]"

    return json.dumps(
        [
            {
                "id": t.track_id,
                "title": t.title or "",
                "artist": t.artist or "",
                "album": t.album or "",
                "duration": t.duration,
            }

            for t in db.tracks
        ]
    )

def render_tracks(json_str):

    container = document.getElementById("ipod-tracks")

    if not container:
        return
    
    tracks = json.loads(json_str)

    if not tracks:
        container.innerHTML = "<p>No tracks on this iPod yet.</p>"
        return

    rows = []

    for track in tracks:
        rows.append(
            "<tr>"
            f"<td>{escape_html(track.get('title', ''))}</td>"
            f"<td>{escape_html(track.get('artist', ''))}</td>"
            f"<td>{escape_html(track.get('album', ''))}</td>"
            f"<td>{format_duration(track.get('duration'))}</td>"
            "</tr>"
        )
    
    container.innerHTML = (
        "<table>"
        "<thead><tr><th>Title</th><th>Artist</th><th>Album</th><th>Duration</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )

async def verify_ipod_structure(handle):
    """
    Require ipod db before mounting
    """

    try:

        control = await handle.getDirectoryHandle("iPod_Control", to_js({"create": False}))

        itunes = await control.getDirectoryHandle("iTunes", to_js({"create": False}))

        await itunes.getFileHandle("iTunesDB", to_js({"create": False}))

        return True
    except Exception:
        return False

async def connect_ipod():

    global nativefs, db


    if pyodide is None:
        set_status("iPod Engine is fucking dead. Oh my god its dead what do we do.")
        return

    if not hasattr(window, "showDirectoryPicker"):

        set_status("Sorry I only work on Chrome (ew disgusting) or yucky yucky Edge (vomit)")

        window.alert("Sorry, connecting yo ipod requires Chrome or Edge ( I know disgusting and abhorrent)")

        return

    set_status("Opening yo file explorer...")

    try:
        handle = await window. showDirectoryPicker(to_js({"mode": "readwrite"}))

    except Exception as e:

        if getattr(e, "name", "") == "AbortError":
            set_status("Not connected")
            return

        set_status("Not connected")
        
        window.alert(f"Could not open yo folder, is it IPOD? hmmm. >{e}")

        return
    if not await verify_ipod_structure(handle):
        
        set_status("Not connected")

        window.alert("That folder doesn't look like an ipod. I might be wrong though. But I think I'm right.")

        return
    
    set_status("Mounting iPod (pause.)")

    try:

        nativefs = await pyodide.mountNativeFS(MOUNT, handle)

    except Exception as e:

        nativefs = None
        db = None

        set_status("Not connected")

        window.alert(f"For some reason I couldn't mount iPod (sus) >{e}")

        return 
    
    set_status("reading yo iTunes library...")

    try: 
        await load_library()

    except Exception as e:

        db = None

        set_status("Not connected")

        window.alert(f"Could not ready ur itunes DB :o > {e}")

async def main(pyodide_instance):

    global pyodide

    pyodide = pyodide_instance
    
    set_status("Not connected")


