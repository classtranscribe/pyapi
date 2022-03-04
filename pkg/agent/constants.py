
from enum import Enum


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