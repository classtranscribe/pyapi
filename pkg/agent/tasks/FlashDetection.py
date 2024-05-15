import json
import os
import requests
from .AbstractTask import AbstractTask, TaskNames
from pkg.agent.tasks.lib import flashdetector


class FlashDetection(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.FlashDetection

    @staticmethod
    def get_file_path(video):
        return video['video1']['path']
        # legacy: return os.path.join(DATA_DIRECTORY, '%s.mp4' % video['video1']['id'])

    def detect_flashes(self, video_id, video):

        # get file_path from video
        file_path = self.get_file_path(video=video)

        # run flashdetector and store result 
        try:
            self.logger.info(' [%s] FlashDetection detecting flashes for %s...' % (video_id, file_path))
            timestamps = flashdetector.detect_flashes(video_path=file_path, speed=1)

            # save result to api
            self.jwt = self.update_jwt()
            # resp = requests.post(url='%s/api/Task/UpdateSceneData?videoId=%s' % (self.target_host, video_id),
            #                         headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
            #                         data=json.dumps({"Scenes": scenes, "ScenesMetadata": scenes_meta}))

            # resp.raise_for_status()
            return timestamps
        except Exception as e:
            self.logger.error(
                ' [%s] FlashDetection failed to detect flashing in videoId=%s: %s' % (
                    video_id, file_path, str(e)))
            return None

    # Message Body Format:
    #     {'Data': 'db2090f7-09f2-459a-84b9-96bd2f506f68',
    #     'TaskParameters': {'Force': False, 'Metadata': None}}
    def run_task(self, body, emitter):
        self.logger.info(' [.] FlashDetection message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] FlashDetection started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)
        # print(video)

        # short-circuit if we already have scene data
        # if not force and VIDEO_SCENEDATA_KEY in video and video[VIDEO_SCENEDATA_KEY]:
        #     self.logger.warning(' [%s] Skipping SceneDetection: sceneData already exists' % video_id)
        #     self.logger.info(' [%s] SceneDetection now triggering: PhraseHinter' % video_id)
        #     emitter.publish(routing_key='PhraseHinter', body=body)
        #     return

        # get file_path from video
        # Note that because we're accessing the raw file, we're assuming that
        # we're running on the same server and/or in the same file space
        # TODO: process multiple videos?
        file_path = self.get_file_path(video=video)
        # print(file_path)

        # Short-circuit if we can't find the file
        # fetch the file from server if not found (if DOWNLOAD_MISSING_VIDEOS=True)
        if not self.ensure_file_exists(video_id=video_id, file_path=file_path):
            self.logger.warning(' [%s] Skipping FlashDetection: video file not found locally' % video_id)
            return

        # verify file size
        if 'fileMediaInfo' in video and 'format' in video['fileMediaInfo'] and 'size' in video['fileMediaInfo']['format']:
            expected_size = video['fileMediaInfo']['format']['size']
            actual_size = os.path.getsize(file_path)
            if int(actual_size) != int(expected_size):
                self.logger.warning('Size mismatch on downloaded file: %s (%s bytes, but should be %s)' %
                                    (video_id, actual_size, expected_size))

        # TODO: make sure this works
        self.detect_flashes(video_id, video)

        # if video is None:
        #     self.logger.error(' [%s] SceneDetection FAILED to lookup videoId=%s' % (video_id, video_id))
        #     return

        self.logger.info(' [%s] FlashDetection complete!' % video_id)

        # Trigger TranscriptionTask (which will generate captions in various languages)
        self.logger.info(' [%s] FlashDetection now triggering: PhraseHinter' % video_id)
        #body['Scenes'] = scenes  # json.dumps(scenes)
        emitter.publish(routing_key='PhraseHinter', body=body)

        return
