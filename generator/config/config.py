import os
from pathlib import Path

LOCK_FILE = "downloadLock"
SONGS_FOLDER = os.path.join(Path(__file__).parent, "songs", "fullSongs")
DOWNLOAD_FOLDER = os.path.join(Path(__file__).parent.parent, "songs", "fullSongs")
SONG_LIST_JSON = os.path.join(Path(__file__).parent.parent, "src", "assets", "data", "tracklist.json")
STEMS_DIR = os.path.join(Path(__file__).parent.parent, "temp")
TEMP_FILE = os.path.join(Path(__file__).parent.parent, "temp", "stemSegment.wav")
LOCK_FILE_PATH = os.path.join(STEMS_DIR, LOCK_FILE)
ELASTIQUE_EXEC_PATH = os.path.join(Path(__file__).parent.parent, "elastiqueProCl")
OUTPUT_TEMP_FILE = os.path.join(Path(__file__).parent.parent, "temp", "stretched.wav")
OUTPUT_FILE_PATH = os.path.join(Path(__file__).parent.parent, "songs", "outputSongs")
AUDIO_DIR_PATH = os.path.join(Path(__file__).parent.parent.parent, "audio")
LOG_DIR_PATH = os.path.join(Path(__file__).parent.parent, "logs")
USERS_DIR = os.path.join(Path(__file__).parent.parent, "users")

TMP = "tmp"
SESSIONS = "sessions"
ELASTIQUE_TMP = "elastique"
TRACK_TMP = "tracks"
REGION_TMP = "regions"

FILE_TYPE = "wav"
OUT_FILE_TYPE = "aac"
