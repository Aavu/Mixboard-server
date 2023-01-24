import json
import os
import numpy as np
from generator.song import Song
from .config.config import AUDIO_DIR_PATH
from collections import defaultdict
from enum import Enum
from .logger import logger


class Library:
    def __init__(self, audio_dir_path=AUDIO_DIR_PATH) -> None:
        self._audio_path = audio_dir_path
        self.songs = defaultdict(lambda: None)
        self.metadata = None
        self.load_songs()

    def load_song_ids(self):
        for dir in os.listdir(self._audio_path):
            if os.path.isdir(dir):
                self._song_ids.append(dir)

    def _get_song_metadata(self, song_id):
        file_path = os.path.join(self._audio_path, song_id, 'metadata.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

    def load_songs(self):
        for id in os.listdir(self._audio_path):
            if os.path.isdir(os.path.join(self._audio_path, id)):
                if id not in self.songs.keys():
                    print(f"Loading song : {id}")
                    self.songs[id] = Song(id)

    def load_metadata(self):
        metadata = {"version": "1.0",
                    "statusCode": 200,
                    "items": {},
                    "total": len(self.songs)}
        for song in self.songs.values():
            data = song.get_metadata()
            metadata["items"][song.get_id()] = data
        self.metadata = metadata
        print("Metadata Loaded")

    def get_metadata(self):
        self.load_songs()
        self.load_metadata()
        return self.metadata


class UserLibrary:
    def __init__(self, song_ids: list = None, user_lib_data: dict = None):
        self._songs: dict[str: Song] = {}
        if user_lib_data:
            self.load_from_data(user_lib_data)
            return

        self.__load_user_songs(song_ids)

    def get_all_songs(self):
        return self._songs.values()

    def __len__(self):
        return len(self._songs)

    def is_empty(self):
        return len(self._songs) == 0

    def load_from_data(self, data: dict):
        for sid in data:
            self._songs[sid] = Song(song_data=data[sid])

    def __load_user_songs(self, song_ids: list):
        if song_ids is None:
            return
            # for each song, load it's stems
        for _id in song_ids:
            self.add_song(_id)

    def load_stems(self):
        for sid in self._songs:
            self._songs[sid].load_stems()

    def add_song(self, song: str or Song):
        if type(song) == str:
            if self.has_song(song):
                return
            self._songs[song] = Song(song)
        elif type(song) == Song:
            if self.has_song(song.get_id()):
                return
            self._songs[song.get_id()] = song
        else:
            raise Exception(f"Unknown type '{type(song)}' for variable song")

        for _id in self._songs:
            print(self._songs.get(_id).get_name())

    def has_song(self, song_id):
        return song_id in self._songs

    def remove_song(self, song_id):
        if self.has_song(song_id):
            del self._songs[song_id]

        for _id in self._songs:
            print(self._songs.get(_id).get_name())

    def reset(self):
        self._songs = defaultdict(lambda: None)

    def get_song(self, song_id):
        return self._songs.get(song_id)

    class PitchCalculationMethod(Enum):
        VocalOnly = 0
        AllStems = 1

    def get_optimal_pitch_class(self, selected_songs, selected_vocal_songs):
        delta_all, avg_pitch_class_all, mode_all = self.get_average_pitch_class(selected_songs,
                                                                                selected_vocal_songs,
                                                                                UserLibrary.PitchCalculationMethod.AllStems)
        delta_vocals, avg_pitch_class_vocals, mode_vocals = self.get_average_pitch_class(selected_songs,
                                                                                         selected_vocal_songs,
                                                                                         UserLibrary.PitchCalculationMethod.VocalOnly
                                                                                         )
        if delta_all < delta_vocals:
            return avg_pitch_class_all, mode_all
        else:
            return avg_pitch_class_vocals, mode_vocals

    def get_average_pitch_class(self, selected_songs, selected_vocal_songs, pitch_calculation_method):
        if not selected_vocal_songs:
            pitch_calculation_method = UserLibrary.PitchCalculationMethod.AllStems

        if pitch_calculation_method == UserLibrary.PitchCalculationMethod.VocalOnly:
            user_songs = {selected_vocal_songs[i]: self.get_song(selected_vocal_songs[i]) for i in
                          range(len(selected_vocal_songs))}
        elif pitch_calculation_method == UserLibrary.PitchCalculationMethod.AllStems:
            user_songs = {selected_songs[i]: self.get_song(selected_songs[i]) for i in range(len(selected_songs))}
        else:
            user_songs = None

        relative_minors = np.array([])
        for song in user_songs.values():
            key, mode = song.get_key_and_mode()
            if mode == 1:
                key = (key - 3) % 12
            relative_minors = np.append(relative_minors, key)
        avg_pitch_relative_minors = np.sum(relative_minors) / relative_minors.shape[0]
        sum_delta_minor = sum(abs(relative_minors - avg_pitch_relative_minors))

        relative_majors = np.array([])
        for song in user_songs.values():
            key, mode = song.get_key_and_mode()
            if mode == 0:
                key = (key + 3) % 12
            relative_majors = np.append(relative_majors, key)
        avg_pitch_relative_majors = np.sum(relative_majors) / relative_majors.shape[0]
        sum_delta_major = sum(abs(relative_majors - avg_pitch_relative_majors))

        if sum_delta_major < sum_delta_minor:
            return sum_delta_major, avg_pitch_relative_majors, 1  # mode = 1
        else:
            return sum_delta_minor, avg_pitch_relative_minors, 0  # mode = 0

    def get_optimal_tempo(self):
        # TODO: Optimize tempo for only selected songs
        selected_songs = list(self._songs.keys())
        song_tempos = np.zeros(len(selected_songs))
        for i, song in enumerate(self._songs.values()):
            song_tempos[i] = song.get_tempo()
        tempo_change = {selected_songs[i]: 0 for i in range(len(selected_songs))}

        for i in range(2):
            tempo_selection_matrix = np.tile(song_tempos, (len(song_tempos) * 2 + 1, 1)).transpose()

            half_matrix = np.diag(np.ones(len(selected_songs)) * 0.5)
            half_matrix[half_matrix == 0] = 1
            double_matrix = np.diag(np.ones(len(selected_songs)) * 2)
            double_matrix[double_matrix == 0] = 1

            tempo_selection_matrix[:, 1:len(selected_songs) + 1] = tempo_selection_matrix[:,
                                                                   1:len(selected_songs) + 1] * half_matrix
            tempo_selection_matrix[:, len(selected_songs) + 1:] = tempo_selection_matrix[:,
                                                                  len(selected_songs) + 1:] * double_matrix

            # Choose the combination with the least standard deviation
            std_dev_array = np.std(tempo_selection_matrix, axis=0)
            selected_tempo_change_idx = np.where(std_dev_array == min(std_dev_array))[0][0]

            if 0 < selected_tempo_change_idx < len(song_tempos) + 1:
                song_tempo_to_change = selected_tempo_change_idx - 1
                tempo_change[selected_songs[song_tempo_to_change]] = 0.5
                song_tempos[song_tempo_to_change] = 0.5 * song_tempos[song_tempo_to_change]

            elif selected_tempo_change_idx >= len(song_tempos) + 1:
                song_tempo_to_change = selected_tempo_change_idx - (len(song_tempos) + 1)
                tempo_change[selected_songs[song_tempo_to_change]] = 2
                song_tempos[song_tempo_to_change] = 2 * song_tempos[song_tempo_to_change]

        optimal_tempo = np.mean(song_tempos)
        return optimal_tempo, tempo_change

    def to_json(self):
        lib_data = {}
        for id in self._songs:
            lib_data[id] = self._songs[id].to_json()

        return lib_data
