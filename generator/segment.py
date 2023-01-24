import os
import time
from sys import platform
import numpy as np
from pydub import AudioSegment
from . import utils
from .config.config import *
import subprocess
from .logger import logger
from generator.song import Song
from .modules.enums import SongSection
from .uiParser import Region
from .modules.enums import State, StemType


#######################################


class Segment:
    def __init__(self, region: Region, song: Song, optimal_tempo, tempo_change, optimal_pitch_class, mode,
                 should_sync_sections: bool):
        self._region = region
        self._song = song
        self._optimal_tempo = optimal_tempo
        self._tempo = song.get_tempo()
        self._tempo_change_factor = self.__tempo_change(tempo_change)  # 1, 0.5, 2 ; # 60 -> 120 F=2
        self._optimal_pitch_class = optimal_pitch_class
        self._mode = mode
        self._should_sync_sections = should_sync_sections

        elastique_tmp_dir = utils.get_elastique_tmp_directory(self._region.user_id, self._region.session_id)
        self.audio_path = os.path.join(elastique_tmp_dir, f"{self._region.id}.{FILE_TYPE}")
        self.stretched_audio_path = os.path.join(elastique_tmp_dir, f"{self._region.id}_stretched.{FILE_TYPE}")

        self._segment_path, self._is_new_segment = self.create_segment()

    @property
    def segment_id(self):
        return self._region.id

    @property
    def stem_type(self):
        return self._region.stem_type

    @property
    def position_ms(self):
        return int(self._region.x * 4 * 60 * 1000 / self._optimal_tempo)

    @property
    def position_samples(self) -> int:
        fs = self._song.get_fs()
        if fs is None:
            fs = 44100
        return int(round((self.position_ms / 1000.0) * fs))

    @property
    def path(self):
        return self._segment_path

    @property
    def is_new(self):
        return self._is_new_segment

    # Public method
    def create_segment(self) -> (str, bool):
        fname = f"{self._song.get_name()}/{self.stem_type.value}"

        bar_length = self._region.w

        if self.__segment_ready():
            if os.path.exists(self.audio_path):
                logger.info(f"{fname} segment already exists. No need to create a new one")
                return self.audio_path, False

        logger.info(f"Reading {fname}")

        stem = self._song.load_stem(self.stem_type)
        if stem is None:
            logger.error(f"Could not load stem for {self.stem_type}")
            return None, True

        logger.info(f"processing {fname}")

        corrected_bar_length = bar_length * 1 / self._tempo_change_factor

        # Find bounds to cut stem to segments
        bounds, num_loops = self.__segment_bounds(corrected_bar_length)

        if not bounds:
            return None, True

        # Cut segment to appropriate length
        stem = stem[bounds[0]:bounds[1]]
        # Stretch audio to tempo and pitch
        now = time.time()
        segment = self.__stretch_segments(stem)
        logger.debug(f"Elastique took {time.time() - now} seconds")
        # Loop segment
        segment = self.__loop_segment(segment, num_loops, bar_length)

        # Export segment for debug
        # dbg_out = os.path.join(self._temp_dir, f"{self._song.get_id()}_{self.stem_type.value}_dbg.wav")
        # segment.export(os.path.join(dbg_out), format='wav')

        # Export segment
        segment.fade_in(10).fade_out(10).export(self.audio_path, format="adts")

        return self.audio_path, True

    # Private methods
    def __segment_ready(self) -> bool:
        return self._region.state is State.Ready

    def __segment_bounds(self, corrected_bar_length) -> (tuple, int):
        # find the closest larger number of bar_length to cut from
        quantized_bar_lengths = np.array([4, 8, 16, 32, 64])
        quantized_bar_length = quantized_bar_lengths[quantized_bar_lengths >= corrected_bar_length][0]
        num_loops = 1
        while True:
            non_silent_bounds = self._song.get_non_silent_bounds(self.stem_type, quantized_bar_length)
            if non_silent_bounds:
                break

            quantized_bar_length /= 2
            num_loops *= 2

            if quantized_bar_length < 2:
                logger.error(f"{self._song.get_name()} has no non_silent {self.stem_type.value}..returning 'None'")
                return None, None  # returns None if no non_silent segments are found

        bounds = self.__choose_segment(non_silent_bounds, corrected_bar_length, quantized_bar_length)
        return bounds, num_loops

    def __choose_segment(self, non_silent_bounds, bar_length, quantized_bar_length):
        if not len(non_silent_bounds) >= 3:
            song_section = SongSection.Any  # Making up for len(non_silent_bounds) == 1

        bound = 0
        if self.song_section == SongSection.Any:
            bound = np.random.choice(len(non_silent_bounds))  # Select randomly from the entire song
        elif self.song_section == SongSection.First:
            bound = 0
        elif self.song_section == SongSection.Start:
            bound = np.random.choice(len(non_silent_bounds) // 3)  # Select randomly from first third of the song
        elif self.song_section == SongSection.Middle:
            s = len(non_silent_bounds) // 3
            e = (len(non_silent_bounds) // 3 * 2) + 1  # Add 1 since randint picks from a half open interval [low, high)
            bound = np.random.randint(s, e)  # Select randomly between 1/3 and 2/3 of the song
        elif self.song_section == SongSection.End:
            s = len(non_silent_bounds) // 3 * 2
            e = len(non_silent_bounds)
            bound = np.random.randint(s, e)  # Select randomly between 2/3 and end of song
        elif self.song_section == SongSection.Last:
            bound = len(non_silent_bounds) - 1

        logger.debug(f"Song: {self._song.get_name()}, section: {self.song_section.name}, Bound: {bound}")
        segment_start_in_samps = int(non_silent_bounds[bound] * self._song.get_fs())
        q_bar_length_in_samples = self._song.get_fs() * (60 / (self._tempo / 4)) * quantized_bar_length
        bar_length_in_samples = self._song.get_fs() * (60 / (self._tempo / 4)) * bar_length
        segment_end_in_samps = int(segment_start_in_samps + q_bar_length_in_samples)
        segment_end_in_samps = int(min(segment_start_in_samps + bar_length_in_samples, segment_end_in_samps))
        bounds = (segment_start_in_samps, segment_end_in_samps)
        logger.debug(f"BOUNDS: {self._song.get_name()}, Bounds: {bounds}")
        return bounds

    def __stretch_segments(self, stem):
        regions_tmp_dir = utils.get_region_tmp_directory(self._region.user_id, self._region.session_id)

        if platform.startswith("linux"):  # linux
            # elastiqueProVersion
            in_name = os.path.join(regions_tmp_dir, f"{self._region.id}.{FILE_TYPE}")
            utils.write_audio(in_name, stem, self._song.get_fs())
            tempo_ratio = str(1 / self.tempo_ratio)
            pitch_ratio = str(self.pitch_ratio_elastique)

            mode = "0" if self.stem_type == StemType.Vocals else "2"
            cmd = [ELASTIQUE_EXEC_PATH, "-i", in_name, "-o", self.stretched_audio_path, "-s", tempo_ratio, "-p",
                   pitch_ratio, "-m", mode, "-f", "1"]
            subprocess.call(cmd)
        else:
            # pyrb version
            tempo_ratio = self.tempo_ratio
            pitch_ratio = self.pitch_ratio
            stretched_stem = utils.time_and_pitch_shift(stem, self._song.get_fs(), tempo_ratio, pitch_ratio)
            utils.write_audio(self.stretched_audio_path, stretched_stem, self._song.get_fs())

        segment = AudioSegment.from_wav(self.stretched_audio_path)
        return segment

    def __loop_segment(self, segment, num_loops, bar_length) -> AudioSegment:
        looped = segment * num_loops
        bar_length_in_ms = int((60 / (self._optimal_tempo / 4)) * bar_length * 1000)
        logger.debug(f"region: {self._region.id}, num_loops: {num_loops}, bar_length: {bar_length}")
        return looped[:bar_length_in_ms]

    @property
    def tempo_ratio(self):
        return self._optimal_tempo / self._tempo

    @property
    def pitch_ratio_elastique(self):
        pitch_class, song_mode = self._song.get_key_and_mode()
        if self._mode == 1 and song_mode == 0:
            pitch_class = (pitch_class + 3) % 12

        elif self._mode == 0 and song_mode == 1:
            pitch_class = (pitch_class - 3) % 12

        pitch_ratio = (2 ** ((self._optimal_pitch_class - pitch_class) / 12))
        logger.info(f"pitch_ratio {self._song.get_name()}, {self.stem_type} -> {pitch_ratio}")
        return pitch_ratio

    @property
    def pitch_ratio(self):
        pitch_class, song_mode = self._song.get_key_and_mode()
        if self._mode == 1 and song_mode == 0:
            pitch_class = (pitch_class + 3) % 12
        elif self._mode == 0 and song_mode == 1:
            pitch_class = (pitch_class - 3) % 12
        pitch_ratio = self._optimal_pitch_class - pitch_class
        logger.info(f"pitch_ratio {self._song.get_name()}, {self.stem_type} -> {pitch_ratio}")
        return pitch_ratio

    def __tempo_change(self, tempo_change):
        if tempo_change[self._song.get_id()]:
            self._tempo = self._tempo * tempo_change[self._song.get_id()]
            return tempo_change[self._song.get_id()]
        return 1

    @property
    def song_section(self) -> SongSection:
        if not self._should_sync_sections:
            return SongSection.Any

        position = self._region.x
        end_bar = self._region.x + self._region.w
        song_section = SongSection.First
        if position == 0:
            song_section = SongSection.First
        elif position < 8:
            song_section = SongSection.Start
        elif 8 <= position < 24:
            song_section = SongSection.Middle
        elif position >= 24:
            song_section = SongSection.End
        if position >= 24 and end_bar == 32:
            song_section = SongSection.Last
        return song_section
