import errno
import glob
import json
import shutil

import numpy as np
import pyrubberband as pyrb
import soundfile as sf
from numba import njit
from pydub import AudioSegment

from .config.config import *
from .logger import logger
from .uiParser import UiParser

# Silence param
BLOCK = 2048
HOP = 512
SILENCE_THRESHOLD = 0.1
HOLE_THRESHOLD = 250
MED_THRESHOLD = 250


def read_audio(input_file_path, return_fs=True):
    seg = AudioSegment.from_file(input_file_path)
    x = seg2np(seg)
    fs = seg.frame_rate
    if x.shape[1] > 1:
        x = x.mean(axis=1)
    if return_fs:
        return x, fs
    return x


def write_audio(output_file_path, x, fs):
    sf.write(output_file_path, x, fs)


def time_and_pitch_shift(x, fs, tempo_ratio, pitch_ratio):
    stretched = pyrb.time_stretch(x, fs, tempo_ratio)
    stretched_and_shifted = pyrb.pitch_shift(stretched, fs, pitch_ratio)
    return stretched_and_shifted


def cleanup(dir):
    logger.info(f"cleaning up '{dir}' directory")
    files = glob.glob(os.path.join(dir, "*"))
    for f in files:
        os.remove(f)
    os.rmdir(dir)


def report_success(job, connection, result, *args, **kwargs):
    print("Success is acheived")
    pass


def get_tmp_directory(user_id, session_id):
    session_dir = get_session_directory(user_id, session_id)
    temp_dir = os.path.join(session_dir, TMP)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_elastique_tmp_directory(user_id: str, session_id: str):
    tmp_dir = get_tmp_directory(user_id, session_id)
    elastique_dir = os.path.join(tmp_dir, ELASTIQUE_TMP)
    os.makedirs(elastique_dir, exist_ok=True)
    return elastique_dir


def get_region_tmp_directory(user_id: str, session_id: str):
    tmp_dir = get_tmp_directory(user_id, session_id)
    region_dir = os.path.join(tmp_dir, REGION_TMP)
    os.makedirs(region_dir, exist_ok=True)
    return region_dir


def get_user_directory(user_id: str):
    dir_path = os.path.join(USERS_DIR, user_id)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


# This directory will contain the layout for the generation session and the audio files required for the session.
def get_session_directory(user_id: str, session_id: str):
    user_dir = get_user_directory(user_id)
    session_dir = os.path.join(user_dir, SESSIONS, session_id)
    os.makedirs(session_dir, exist_ok=True)

    return session_dir


def seg2np(seg: AudioSegment) -> np.ndarray:
    seg_split = seg.split_to_mono()
    samples = [s.get_array_of_samples() for s in seg_split]
    x = np.array(samples, dtype=np.float32).T
    x /= np.iinfo(samples[0].typecode).max
    return x


@njit
def is_silent(activations: np.ndarray, threshold: float):
    return (np.sum(activations) / len(activations)) < threshold


def save_layout(user_id: str, layout: UiParser):
    session_id = layout.session_id
    session_dir = get_session_directory(user_id, session_id)
    with open(os.path.join(session_dir, "layout.json"), mode='w') as f:
        json.dump(layout.ui_data, f, indent=2)


def load_layout(layout_path) -> UiParser:
    with open(layout_path, mode='r') as f:
        layout = json.load(f)
        return UiParser(layout)


def save_audio(user_id, session_id, audio: AudioSegment, bitrate='64k') -> str:
    session_dir = get_session_directory(user_id, session_id)
    audio_path = os.path.join(session_dir, f"{session_id}.{OUT_FILE_TYPE}")
    audio.export(out_f=audio_path, format="adts", bitrate=bitrate)
    return audio_path


def remove_file(file):
    os.remove(file)


def replace_dots(user_id: str) -> str:
    if '@' in user_id:
        return user_id
    return user_id.replace(".", "-")


# https://stackoverflow.com/questions/1994488/copy-file-or-directories-recursively-in-python
def recursive_copy(src, dst):
    try:
        print(f"{src}, {dst}")
        shutil.copytree(src, dst, copy_function=shutil.copy, dirs_exist_ok=True)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            print(f"error copying: {exc}")
