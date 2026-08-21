import os

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a"}


def scan_folder(folder):
    songs = []
    if not os.path.isdir(folder):
        return songs
    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in AUDIO_EXTENSIONS:
                full_path = os.path.join(root, f)
                name = os.path.splitext(f)[0]
                songs.append({"name": name, "path": full_path})
    return songs


def scan_folders(folders):
    all_songs = []
    seen = set()
    for folder in folders:
        for song in scan_folder(folder):
            if song["path"] not in seen:
                seen.add(song["path"])
                all_songs.append(song)
    return all_songs
