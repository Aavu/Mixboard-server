import os
import time

from generator.generator import Generator
from celery import Celery
from celery.result import AsyncResult
from redis import Redis
from generator.song import Song
from generator.logger import logger
from generator.config.config import DOWNLOAD_FOLDER
from generator.library import UserLibrary
from generator.exceptions import *
from generator.uiParser import UiParser

celery_app = Celery(__name__, backend='redis://127.0.0.1:6379', broker='redis://127.0.0.1:6379')


@celery_app.task(name="create_library", bind=True)
def create_library(self, ip):
    logger.create_log()
    logger.debug(f"New library for {ip}")
    redis = Redis(host='127.0.0.1', port=6379)  # Redis Connection operation is super cheap. DO NOT create a globals
    for key in redis.scan_iter(f"{ip}:*"):
        logger.debug(f"deleting {key} from redis cache")
        redis.delete(key)

    redis.json().set(ip, '$', UserLibrary().to_json())
    return 0


@celery_app.task(name="create_task", bind=True)
def create_task(self, data, user_id):
    redis = Redis(host='127.0.0.1', port=6379)
    lib = UserLibrary(user_lib_data=redis.json().get(user_id))
    ui_data = UiParser(data)
    # song_ids = ui_data.selected_songs

    # # wait for all the required songs to load
    # for song_id in song_ids:
    #     if redis.exists(f"{ip}:{song_id}"):
    #         task_id = redis.get(f"{ip}:{song_id}")
    #         task_result = AsyncResult(task_id, app=celery_app)
    #         while not task_result.ready():
    #             task_result = AsyncResult(task_id, app=celery_app)
    #             self.update_state(state="PROGRESS", meta={'progress': 5, 'description': "Downloading song"})
    #             time.sleep(0.05)  # 50ms delay to process request
    #             self.update_state(state="PENDING", meta={})
    #             time.sleep(0.5)

    #         redis.delete(f"{ip}:{song_id}")
    #     else:
    #         pass
    #         # The code cannot get here unless there's a bug.
    #         # Even if it does, it's not an issue because there is a redundant check inside generator that will
    #         # load the songs anyway

    data_back = Generator(user_id, ui_data, lib, self).generate_mashup()
    logger.info(
        "--------------------------------------------------------")  # Separate between different mashups within session
    return data_back


@celery_app.task(name="add_track", bind=True)
def add_track(self, song_id, ip):
    redis = Redis(host='127.0.0.1', port=6379)
    if redis.exists(ip):
        lib = UserLibrary(user_lib_data=redis.json().get(ip))

        if redis.exists(f"{ip}:{song_id}"):
            print(f"{song_id} already in redis cache")
            return 0

        # Will be used before generating to check if all the songs are downloaded
        redis.set(f"{ip}:{song_id}", self.request.id)

        if not lib.has_song(song_id):
            logger.info(f"Adding track - {song_id}")

            try:
                song = Song(song_id=song_id, download_location=DOWNLOAD_FOLDER, load_audio=False, task=self)
                lib.add_song(song)
                logger.info(f"Added: {song_id}")

            except SongNotFoundError as e:
                logger.error(e)
                redis.delete(f"{ip}:{song_id}")
                return e.code
    else:
        logger.error(f"User library is None")
        return -1

    redis.json().set(ip, '$', lib.to_json())
    return 0


@celery_app.task(name="remove_track", bind=True)
def remove_track(self, song_id, ip):
    redis = Redis(host='127.0.0.1', port=6379)

    if redis.exists(ip):
        redis.sadd(f"{ip}:task_id", self.request.id)
        lib = UserLibrary(user_lib_data=redis.json().get(ip))
        logger.info(f"Remove track - {song_id}")
        lib.remove_song(song_id)
        redis.json().set(ip, '$', lib.to_json())
    else:
        logger.error(f"User library is None")


def request_region(region_id):
    redis = Redis(host='127.0.0.1', port=6379)
    if redis.exists(region_id):
        data = redis.json().get(region_id)
        redis.json().delete(region_id)
        return data

    print(f"No region with id {region_id} found in redis")
    return {"id": region_id, "snd": "", "tempo": -1, "position": 0, "valid": False}


@celery_app.task
def error_handler(request, exc, traceback):
    print(f'Task {request.id} raised exception: {exc}\n{traceback}')
