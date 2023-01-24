###
# Created by Raghavasimhan Sankaranarayanan on 9/28/22.
###
import numpy as np
import requests
from .config.config import DOWNLOAD_FOLDER, AUDIO_DIR_PATH
from .config import spotify
from .modules.url import Url
import inspect
import os
import subprocess
import shutil
import shlex
from time import sleep
import json
from .logger import logger
from collections import defaultdict
import torch
import librosa
from .silenceFilter import SilenceFilter
from . import utils
from numba import njit, prange
from .modules.BeatNet.BeatNet import BeatNet
from .modules.enums import StemType
from .exceptions import *


class Song:
    def __init__(self, song_id: str = None, song_data: dict = None, download_location: str = DOWNLOAD_FOLDER,
                 load_audio: bool = False, task=None, silence_threshold: float = 0.4):

        if song_id is None and song_data is None:
            raise IllegalArgumentError("Provide either song id or song_data. Both cannot be None")

        self._task = task
        self._path = download_location
        self._song_id = song_id
        self._load_audio = load_audio

        self._beat_detector = BeatNet()

        if song_data is not None:
            self._song: dict = song_data
            self._output_path = os.path.join(AUDIO_DIR_PATH, self.get_id())
            if self._load_audio:
                self.load_stems()
            return

        self._url = Url(spotify.PREPEND_URL).append(song_id)
        self._output_path = os.path.join(AUDIO_DIR_PATH, self.get_id())
        self._th = silence_threshold

        # Download and process only if the song is not part of the library
        self._song: dict = self.__download_metadata()

        if self._song is None:
            raise Exception(f"Cannot download metadata for {self.get_id()}")

        self.__download_and_process()

    def is_valid(self):
        return bool(self._song)

    def __download(self):
        """Download the song using the spotify url

        Returns:
            str or None: Returns the path of the downloaded wav file if successful. Else returns None
        """
        song_path = os.path.join(self._path, self.get_id() + ".wav")
        # Check if the song is already there
        if os.path.exists(song_path):
            return song_path

        # Try first with YTM
        result = subprocess.run(
            ['spotdl', self._url.get(), '--path-template', song_path, '--output-format', 'wav'],
            stdout=subprocess.PIPE)

        if not os.path.exists(song_path) and result.returncode != 0:
            # Try with youtube when YTM fails
            result = subprocess.run(
                ['spotdl', '--use-youtube', self._url.get(), '--path-template', song_path, '--output-format', 'wav'],
                stdout=subprocess.PIPE)

            if not os.path.exists(song_path) and result.returncode != 0:
                raise SongNotFoundError("Song download failed...")

        return song_path

    def __download_and_process(self):
        if not 'non_silent_bounds' in self._song:
            # Download song
            logger.info(f"Downloading {self.get_id()}...")
            self.__update_process_state(10, "Downloading Audio")
            path = self.__download()
            audio, _ = self.__validate_song(path)

            # Get Downbeats
            self.__update_process_state(30, "Computing Downbeats")
            logger.info(f"Getting Downbeats...")
            downbeats = self.__get_downbeats(audio)

            # Source separate
            self.__update_process_state(50, "Separating Instruments")
            self.__source_separate()

            # load stems onto memory
            self.__update_process_state(75, "Loading Stems")
            self.load_stems()

            # Filter silence
            logger.info("Getting non-silent boundaries")
            self.__update_process_state(85, "Filtering silence")
            self.__filter_silence(threshold=self._th, down_beats=downbeats)

            # Store Metadata. This needs to be called last so as to update all the above features in the json file
            self.__store_metadata()
            self.__delete_full_song()
            logger.info("Download complete!")
            self.__update_process_state(99, "Download complete!")

    def __source_separate(self):
        model = "0d19c1c6"  # Use a single model on CPU
        if torch.cuda.is_available():
            model = "mdx_extra"  # Use bag of 4 model on GPU
        demucs_out_path = os.path.join(self._output_path, model, self.get_id())

        # Check if the song is already there
        if os.path.exists(self._output_path):
            return self._output_path

        logger.info(f"Separating Sources...")
        print("Separating sources...")

        song_path = self.__download()

        os.system(f"demucs demucs.separate {shlex.quote(song_path)} -n {model} --out {shlex.quote(self._output_path)}")

        # move the tracks from demucs dir to song id dir
        tracks = os.listdir(demucs_out_path)
        for track in tracks:
            shutil.move(os.path.join(demucs_out_path, track), self._output_path, copy_function=shutil.copytree)

        # remove the dir created by demucs
        shutil.rmtree(os.path.join(self._output_path, model))

    def __validate_song(self, song_path):
        audio, fs = librosa.load(song_path, sr=22050)
        spotify_duration = self._song["duration_ms"] / 1000.0
        audio_duration = (1.0 * len(audio)) / fs

        # This is to check if the downloaded version of the song matches spotify.
        # If the duration difference > 10 seconds, it probably downloaded the wrong version from youtube
        if abs(spotify_duration - audio_duration) > 10:
            raise SongNotFoundError(
                f"Song download failed due to duration mismatch ({spotify_duration} vs {audio_duration})...")

        return audio, fs

    def __get_downbeats(self, audio):
        down_beats = self._beat_detector.get_downbeats(audio)
        return down_beats

    def __filter_silence(self, threshold, down_beats):
        filter = SilenceFilter(down_beats, threshold)
        self._song['non_silent_bounds'] = {}
        for stem_type in self._song['audio']:
            stem = self._song['audio'][stem_type]
            fs = self._song['fs']
            # stem = np.frombuffer(stem, dtype=np.float32)
            bounds = filter.get_non_silent_bounds(stem, fs)
            self._song['non_silent_bounds'][stem_type] = bounds

    def load_stems(self):
        files = os.listdir(self._output_path)
        self._song['audio'] = {}
        for f in files:
            if not f.endswith(".wav"):
                continue

            stem_type = os.path.splitext(f)[0]
            fpath = os.path.join(self._output_path, f)
            stem, fs = utils.read_audio(fpath)
            self._song['audio'][stem_type] = stem
            self._song['fs'] = fs

    def load_stem(self, stem_type: StemType) -> np.ndarray or None:
        if self._song.get('audio') is None:
            self._song['audio'] = {}

        stem = self._song['audio'].get(stem_type)
        if stem is not None:
            logger.debug(f"{stem_type.value} stem for {self.get_name()} already loaded.")
            return stem

        for f in os.listdir(self._output_path):
            if not f.endswith(".wav"):
                continue

            stem_type_str = os.path.splitext(f)[0]
            if stem_type_str == stem_type.value:
                fpath = os.path.join(self._output_path, f)
                logger.info(f"loading {stem_type_str} stem for {self.get_name()}")
                stem, fs = utils.read_audio(fpath)
                self._song['audio'][stem_type] = stem
                self._song['fs'] = fs
                return stem
        return None

    def get_id(self) -> str:
        if self._song_id:
            return self._song_id
        return self._song.get('id')

    def get_name(self) -> str:
        return self._song.get('name')

    def get_artist(self) -> str or None:
        try:
            return self._song.get('artists')[0]['name']
        except:
            try:
                return self._song.get('artist')
            except:
                return None

    def get_album(self) -> str or None:
        try:
            return self._song.get('album')['name']
        except:
            try:
                return self._song.get('album')
            except:
                return None

    def get_preview_url(self):
        return self._song.get('preview_url')

    def get_img_url(self):
        try:
            return self._song.get('album')['images'][0]['url']
        except:
            try:
                return self._song.get('img_url')
            except:
                return None

    def get_release_date(self) -> str or None:
        try:
            return self._song.get('album')['release_date']
        except:
            try:
                return self._song.get('release_date')
            except:
                return None

    def get_external_url(self):
        try:
            return self._song['external_urls']['spotify']
        except:
            try:
                return self._song.get('external_url')
            except:
                return None

    def get_fs(self):
        return self._song.get('fs')

    def get_tempo(self) -> float or None:
        try:
            return float(self._song.get('tempo'))
        except:
            return None

    def get_key_and_mode(self):
        try:
            return int(self._song.get('key')), int(self._song.get('mode'))
        except:
            try:
                return self._song.get('key_and_mode')
            except:
                return None, None

    def get_non_silent_bounds(self, stem_type: StemType = None, bar_length: int = None) -> dict or None:
        if not self._song.get('non_silent_bounds'):
            return None

        if stem_type and not bar_length:
            return self._song['non_silent_bounds'][stem_type.value]

        if stem_type and bar_length:
            if bar_length > 32:
                return None

            nsb = self._song['non_silent_bounds'][stem_type.value]

            # The key could be either stored as int or str i.e.-> 4 : [] or '4' : [] depending on which version was used to create it
            # Try both and see which one works
            try:
                return nsb[str(int(bar_length))]
            except:
                try:
                    return nsb[int(bar_length)]
                except:
                    return None  # Incase of key not found, return None which can be handled later

        return self._song['non_silent_bounds']

    def get_stem(self, stem_type: StemType):
        return self._song['audio'][stem_type.value]

    def get_metadata(self) -> dict:
        data = {}
        member_functions = inspect.getmembers(Song, predicate=inspect.isfunction)

        excluded_func = ["get_metadata", "get_stem"]
        for (func_name, obj) in member_functions:
            if func_name.startswith('get_') and (func_name not in excluded_func):
                key = func_name[4:]
                data[key] = obj(self)

        return data

    def to_json(self):
        return self.get_metadata()

    def __store_metadata(self):
        json_file = os.path.join(self._output_path, 'metadata.json')
        song_data = {i: self._song[i] for i in self._song if i != 'audio'}
        json_object = json.dumps(song_data)

        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)

        with open(json_file, 'w') as outfile:
            outfile.write(json_object)

    def __download_metadata(self):

        # Check if the song metadata is already there
        path = os.path.join(self._output_path, "metadata.json")
        if os.path.exists(path):
            return self.__load_metadata()

        logger.info("Downloading Metadata...")
        # POST, convert the response to JSON and save access token
        access_token = requests.post(spotify.AUTH_URL, {'grant_type': 'client_credentials',
                                                        # 'client_id': os.environ.get("CLIENT_ID"),
                                                        # 'client_secret': os.environ.get("CLIENT_SECRET"),
                                                        'client_id': "9cc782e618e04cfbbb447abe7d1d4902",
                                                        'client_secret': "52b3cc1ab3934ec6beaf28a837a134c4"
                                                        }).json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        r = requests.get(Url(spotify.BASE_URL).append('tracks/').append(self.get_id()).get(), headers=headers)
        if r.status_code != 200:
            logger.error("Bad server response")
            return None

        song = r.json()
        features = requests.get(Url(spotify.BASE_URL).append('audio-features/').append(self.get_id()).get(),
                                headers=headers).json()
        song.update(features)   # merge the 2 dictionaries
        return song

    def __load_metadata(self):
        # path example: ~/mixboard/audio/<song-id>/metadata.json
        path = os.path.join(self._output_path, "metadata.json")
        if not os.path.exists(path):
            return None

        with open(path, 'r') as f:
            return defaultdict(lambda: None, json.load(f))

    def __update_process_state(self, percent, description=None):
        if self._task is None:
            return
        self._task.update_state(state="PROGRESS", meta={'progress': percent, 'description': description})
        sleep(0.05)  # 50ms delay to process request
        self._task.update_state(state="PENDING", meta={})

    def __delete_full_song(self):
        song_path = os.path.join(self._path, self.get_id() + ".wav")
        if os.path.exists(song_path):
            os.remove(song_path)


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(dotenv.find_dotenv())
    song = Song("34UIACMGAJw6PKsLA2k3Gx", download_location=DOWNLOAD_FOLDER, load_audio=True)
    print(song.get_metadata())
    print("-" * 25)

    song2 = Song(song_data=json.loads(song.to_json()))

    with open("sample.json", "w") as outfile:
        outfile.write(song2.to_json())
    # print(song._song)
