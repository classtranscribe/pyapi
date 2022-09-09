import shutil
import tempfile
from abc import ABC, abstractmethod
from enum import Enum
import logging
import os
import requests
import time

import config


TARGET_HOST = os.getenv('TARGET_HOST', 'http://api')
TARGET_HOST_JWT = os.getenv('TARGET_HOST_JWT', 'example')


# Map task to queuename
class TaskNames(Enum):
    QueueAwaker = 'QueueAwaker'                     # QueueAwaker
    ExampleTask = 'ExampleTask'                     # ExampleTask
    SceneDetection = 'SceneDetection'               # SceneDetection
    PhraseHinter = 'PhraseHinter'                   # PhraseHinter
    TranscriptionTask = 'TranscriptionTask'         # TranscriptionTask
    # ... Add new tasks here
    AccessibleGlossary = 'AccessibleGlossary'       # AccessibleGlossary


class AbstractTask(ABC):

    @staticmethod
    @abstractmethod
    def get_name():
        pass

    def __init__(self):
        self.logger = logging.getLogger("agent.listener.%s" % self.get_name())

        # TODO: fetch service account jwt (from config / env?)
        self.target_host = TARGET_HOST
        self.jwt = TARGET_HOST_JWT

    def rabbitpy_callback(self, message, emitter):
        self.run_timed_task(body=message.json(), emitter=emitter)

    @abstractmethod
    def run_task(self, body, emitter):
        pass

    def run_timed_task(self, body, emitter):
        start_time = time.time_ns() / 1000000
        self.logger.debug(" [✓] Running %s: %s" % (self.get_name(), str(body)))
        self.run_task(body=body, emitter=emitter)
        self.logger.info(" [✓] Done")
        end_time = time.time_ns() / 1000000
        duration = end_time - start_time
        self.logger.debug(' [✓] %s completed in %d ms' % (self.get_name(), duration))

    def ensure_file_exists(self, video_id, file_path):
        # file not found? attempt to fetch it
        if config.DOWNLOAD_MISSING_VIDEOS and not os.path.exists(file_path):
            # fetch video file using static data path
            self.logger.info(' [%s] SceneDetection attempting to download video data locally: %s' % (video_id, file_path))
            try:
                with requests.get('%s%s' % (self.target_host, file_path), headers={'Referer': self.target_host}, stream=True) as r:
                    r.raise_for_status()
                    self.logger.info(' [%s] SceneDetection now downloading video data locally: %s' % (video_id, file_path))

                    # make sure that destination directory exists
                    data_dirname = os.path.dirname(file_path)
                    data_filename = os.path.basename(file_path)
                    if not os.path.exists(data_dirname):
                        os.makedirs(data_dirname)

                    with tempfile.NamedTemporaryFile(mode='wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            # If you have chunk encoded response uncomment if
                            # and set chunk_size parameter to None.
                            # if chunk:
                            f.write(chunk)

                        f.flush()
                        os.sync()

                        # when we've finished writing bytes to temp, rename file and move to destination folder
                        os.rename(f.name, data_filename)
                        shutil.move(data_filename, data_dirname)
                        os.sync()

                    return True
            except Exception as e:
                self.logger.error(
                    ' [%s] SceneDetection failed to fetch video when DOWNLOAD_MISSING_VIDEOS=True: %s' % (
                    video_id, str(e)))
                return False
        elif os.path.exists(file_path):
            self.logger.error(' [%s] SceneDetection using local video file (DOWNLOAD_MISSING_VIDEOS=False): %s' % (video_id, file_path))
            return True

        return False

    def get_video(self, video_id):
        # fetch video metadata by id
        try:
            resp = requests.get(url='%s/api/Task/Video?videoId=%s' % (self.target_host, video_id),
                                headers={'Authorization': 'Bearer %s' % self.jwt})
            # self.logger.debug(' [%s] SceneDetection fetched video: %s' % (video_id, resp.text))
            resp.raise_for_status()
            video = resp.json()
            return video
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            self.logger.error("Failed to fetch videoId=%s: %s" % (video_id, e))
            return None
