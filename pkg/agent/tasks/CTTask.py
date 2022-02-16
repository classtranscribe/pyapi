import logging
import time
from enum import Enum
from abc import ABC, abstractmethod


# Map task to queuename
class TaskNames(Enum):
    QueueAwaker = 'QueueAwaker'                     # QueueAwaker
    BuildElasticIndex = 'BuildElasticIndex'         # BuildElasticIndex
    CleanUpElasticIndex = 'CleanUpElasticIndex'     # CleanUpElasticIndex
    CreateBoxToken = 'CreateBoxToken'               # CreateBoxToken
    UpdateBoxToken = 'UpdateBoxToken'               # UpdateBoxToken
    ProcessVideo = 'ProcessVideo'                   # ProcessVideo
    GenerateVTTFile = 'GenerateVTTFile'             # GenerateVTTFile
    SceneDetection = 'SceneDetection'               # SceneDetection
    TranscribeVideo = 'TranscribeVideo'             # TranscribeVideo
    DownloadMedia = 'DownloadMedia'                 # DownloadMedia
    DownloadPlaylistInfo = 'DownloadPlaylistInfo'   # DownloadPlaylistInfo
    ExampleTask = 'ExampleTask'                     # ExampleTask


class CTTask(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.get_name())

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def run_task(self):
        pass

    def rmq_callback(self, ch, method, properties, body):
        task_name = self.get_name()
        start_time = time.time()
        self.run_task()
        end_time = time.time()
        duration = end_time - start_time
        self.logger.debug('%s completed in %d ms' % (task_name, duration))
        ch.basic_ack(delivery_tag=method.delivery_tag)
