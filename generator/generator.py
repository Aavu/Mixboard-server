import json

from billiard.pool import Pool
from billiard import Process, Queue

from .segment import Segment
from .uiParser import UiParser, Region, Stem
from pydub import AudioSegment
from .config.config import STEMS_DIR, OUTPUT_FILE_PATH, OUT_FILE_TYPE, DOWNLOAD_FOLDER
import os
import base64
from . import utils
import time
from .logger import logger
import io
from redis import Redis

from .modules.enums import StemType, SongSection
import sys
from path import Path

sys.path.append(Path(__file__).parent.parent.abspath())
from .library import Library, UserLibrary
from .song import Song
from .exceptions import *
from .modules.enums import State


# -----------------------------------------------------------------------------------------------------

class Generator:
    def __init__(self, user_id: str, ui_data: UiParser, user_library: UserLibrary, celery_task, num_pool_workers=10,
                 sr=44100,
                 num_bars=32, should_cleanup=False):

        self.user_id = utils.replace_dots(user_id)  # 127.0.0.1 -> 127-0-0-1, test@gmail.com -> test@gmail.com
        self.session_id = ui_data.session_id
        self.celery_task = celery_task
        self.ui_data = ui_data
        self.user_library = user_library
        self.__user_lib_check()

        self.optimal_tempo, self.tempo_change = self.user_library.get_optimal_tempo()
        self.optimal_pitch_class, self.mode = self.user_library.get_optimal_pitch_class(
            self.ui_data.selected_songs
            , self.ui_data.vocal_tracks)
        self.sync_sections = ui_data.should_sync_sections
        self.lane_link = ui_data.should_link_lane
        self.song_duration = (self.ui_data.song_duration * 4 * 60 * 1000) / self.optimal_tempo  # milli seconds
        self.num_pool_workers = num_pool_workers
        self.output_sr = sr
        self.num_of_bars = num_bars
        self.progress = 0
        self.clean_up = should_cleanup
        self.debug_i = 0
        self.segment_queue = None

    def __user_lib_check(self):
        if not self.user_library:
            self.user_library = UserLibrary()

        selected_song_ids = self.ui_data.selected_songs
        if len(self.user_library) != len(selected_song_ids):

            for song_id in selected_song_ids:
                if not self.user_library.has_song(song_id):
                    try:
                        song = Song(song_id=song_id, download_location=DOWNLOAD_FOLDER, load_audio=False,
                                    task=self.celery_task)
                        self.user_library.add_song(song)
                        logger.debug(f"Added: {song_id}")

                    except SongNotFoundError as e:
                        logger.error(e)

    def generate_all_segments(self):
        # Load all required stems onto memory
        song_ids = {}
        for stem_type in StemType:
            song_ids[stem_type] = self.ui_data.get_song_ids(stem_type, return_state=True)

        songs = {}
        for stem_type in StemType:
            songs[stem_type] = {}

        for stem_type, items in song_ids.items():
            for song_id, state in items:
                _song: Song = self.user_library.get_song(song_id)
                if _song is not None:
                    if state != State.Ready:
                        _song.load_stem(stem_type)
                    songs[stem_type][song_id] = _song
                else:
                    logger.error(f"Cannot get song from id: {song_id}")

        # Generate all the segments of the mashup
        regions = self.ui_data.get_regions(include_ready=False).values()

        songs_and_regions = []
        for region in regions:
            songs_and_regions.append((songs[region.stem_type][region.item.song_id], region))

        # segment_queue = Queue(len(regions))
        processes = [Process(target=self.__create_segment,
                             args=(songs[region.stem_type][region.item.song_id], region))
                     for region in regions]

        for p in processes:
            p.start()

    def __create_segment(self, song: Song, region: Region):
        segment = Segment(region, song=song, optimal_tempo=self.optimal_tempo, tempo_change=self.tempo_change,
                          optimal_pitch_class=self.optimal_pitch_class, mode=self.mode,
                          should_sync_sections=self.sync_sections)

        print(f"Create segment for {region.id}")
        if self.segment_queue:
            self.segment_queue.put((segment.segment_id, segment.path, segment.position_samples), block=False)
            logger.debug(f"Put {segment.segment_id} in queue")
        else:
            return segment.segment_id, segment.path, segment.position_samples

    def generate_mashup(self):
        redis = Redis(host='127.0.0.1', port=6379)

        # Generate music and return the data
        logger.info("Generating Mashup")

        # For all regions in layout, generate only if the region is moved. Else use copied audio for segment.
        if self.ui_data.should_copy_last_session:
            self.copy_last_session()

        self.ui_data.set_tempo(self.optimal_tempo)
        self.ui_data.set_pitch(self.optimal_pitch_class)
        utils.save_layout(self.user_id, self.ui_data)

        regions = self.ui_data.get_regions(include_ready=False).values()
        print(f"num regions {len(regions)}")

        self.segment_queue = Queue(len(regions))

        self.generate_all_segments()

        for _ in regions:
            region_id, path, position = self.segment_queue.get()
            if path:
                with open(path, 'rb') as f:
                    snd = base64.b64encode(f.read()).decode('UTF-8')
                tempo, _ = self.user_library.get_optimal_tempo()
                data = {"id": region_id, "snd": snd, "tempo": tempo, "position": position, "valid": True}
                redis.json().set(region_id, '$', data)
            else:
                logger.warning(f"block empty for segment: {region_id}")

        # utils.cleanup(utils.get_region_tmp_directory(self.user_id, self.session_id))
        if self.clean_up:
            user_out_path = os.path.join(OUTPUT_FILE_PATH, self.user_id)
            temp_dir = os.path.join(STEMS_DIR, f"{self.user_id}-{logger.get_time()}")
            utils.cleanup(dir=temp_dir)
            utils.cleanup(dir=user_out_path)

        return 0

    def __update_process_state(self, progress, description=None):
        if not self.celery_task:
            return
        self.celery_task.update_state(state="PROGRESS", meta={'progress': progress, 'description': description})
        time.sleep(0.05)  # 50ms delay to process request
        self.celery_task.update_state(state="PENDING", meta={})

    def copy_last_session(self):
        logger.info("copying last session data")
        session_tmp_dir = utils.get_tmp_directory(self.user_id, self.session_id)
        prev_session_tmp_dir = utils.get_tmp_directory(self.user_id, self.ui_data.previous_session_id)
        utils.recursive_copy(prev_session_tmp_dir, session_tmp_dir)

        prev_session_dir = utils.get_session_directory(self.user_id, self.ui_data.previous_session_id)
        layout = utils.load_layout(os.path.join(prev_session_dir, "layout.json"))
        logger.debug(f"last pitch: {layout.pitch}, last tempo: {layout.tempo}")
        logger.debug(f"pitch: {self.optimal_pitch_class}, tempo: {self.optimal_tempo}")
        if layout.pitch is not None:
            self.optimal_pitch_class = layout.pitch
        if layout.tempo is not None:
            self.optimal_tempo = layout.tempo
