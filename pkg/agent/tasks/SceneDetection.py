import base64
import json
import os

import requests

from .AbstractTask import AbstractTask, TaskNames

from pkg.agent.tasks.lib import scenedetector, phrasehinter
from config import DATA_DIRECTORY

# from client import client

import config

VIDEO_SCENEDATA_KEY = 'sceneData'

VIDEO_PHRASEHINTS_KEY = 'phrase_hints'
VIDEO_PHRASES_KEY = 'all_phrases'
SCENE_PHRASES_KEY = 'phrases'


class SceneDetection(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.SceneDetection

    @staticmethod
    def get_file_path(video_id, video):
        # return video['video1']['path']
        return os.path.join(DATA_DIRECTORY, '%s.mp4' % video_id)

    def find_scenes(self, video_id, video, readonly):
        # get file_path from video
        # Note that because we're accessing the raw file, we're assuming that
        # we're running on the same server and/or in the same file space
        # TODO: process multiple videos?
        file_path = self.get_file_path(video_id=video_id, video=video)

        # Call scenedetector.find_scenes, store scene data back in api
        try:
            self.logger.info(' [%s] SceneDetection getting scenes for %s...' % (video_id, file_path))
            scenes = scenedetector.find_scenes(video_path=file_path)

            # save found scenes to video in api
            self.logger.debug(' [%s] SceneDetection found scenes: %s' % (video_id, scenes))
            if readonly:
                self.logger.info(' [%s] SceneDetection running as READONLY.. scenes have not been saved' % (video_id))
            else:
                resp = requests.post(url='%s/api/Task/UpdateSceneData?videoId=%s' % (self.target_host, video_id),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                     data=json.dumps({"Scenes": scenes}))

                resp.raise_for_status()
                self.logger.debug(' [%s] SceneDetection successfully saved scenes: %s' % (video_id, scenes))

            return scenes
        except Exception as e:
            self.logger.error(
                ' [%s] SceneDetection failed to detect scenes in videoId=%s: %s' % (
                    video_id, file_path, str(e)))
            return None

    def generate_phrase_hints(self, video_id, video, scenes, readonly):
        # get file_path from video
        # Note that because we're accessing the raw file, we're assuming that
        # we're running on the same server and/or in the same file space
        # TODO: process multiple videos?
        file_path = self.get_file_path(video_id=video_id, video=video)

        # Gather raw phrases from scenes
        self.logger.info(' [%s] SceneDetection gathering raw phrases...' % video_id)
        all_phrases = "\n".join([str(scene[SCENE_PHRASES_KEY]) for scene in scenes])
        # video[VIDEO_PHRASES_KEY] = all_phrases
        self.logger.debug(' [%s] SceneDetection found phrases' % (video_id))

        # Pass raw phrases into phrasehinter.to_phrase_hints
        # Note that this requires 'brown' and 'stopwords' dependencies from NTLK
        try:
            self.logger.info(' [%s] SceneDetection generating phrase hints...' % video_id)
            phrase_hints = phrasehinter.to_phrase_hints(raw_phrases=all_phrases)
            video[VIDEO_PHRASEHINTS_KEY] = phrase_hints

            self.logger.info(' [%s] SceneDetection generated phrase hints: %s' % (video_id, phrase_hints))
            if readonly:
                self.logger.info(' [%s] SceneDetection running as READONLY.. scenes have not been saved: %s' % (video_id, scenes))
            else:
                # save generated phrase_hints to video in api
                resp = requests.post(url='%s/api/Task/UpdatePhraseHints?videoId=%s&phraseHints=%s' % (self.target_host, video_id, phrase_hints),
                                     headers={'Authorization': 'Bearer %s' % self.jwt},
                                     data=phrase_hints)
                resp.raise_for_status()
                self.logger.debug(' [%s] SceneDetection successfully saved phrase hints: %s' % (video_id, phrase_hints))

            return video
        except Exception as e:
            self.logger.error(
                ' [%s] SceneDetection failed to detect scenes in videoId=%s: %s' % (
                    video_id, file_path, str(e)))
            return

    # Message Body Format:
    #     {'Data': 'db2090f7-09f2-459a-84b9-96bd2f506f68',
    #     'TaskParameters': {'Force': False, 'Metadata': None}}
    def run_task(self, body, emitter):
        self.logger.info(' [.] SceneDetection message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', True)
        self.logger.info(' [%s] SceneDetection started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have scene data
        if not force and VIDEO_SCENEDATA_KEY in video and video[VIDEO_SCENEDATA_KEY]:
            self.logger.warning(' [%s] Skipping SceneDetection: sceneData already exists' % video_id)
            self.logger.info(' [%s] SceneDetection now triggering: PhraseHinter' % video_id)
            emitter.publish(routing_key='PhraseHinter', body=body)
            return

        # get file_path from video
        # Note that because we're accessing the raw file, we're assuming that
        # we're running on the same server and/or in the same file space
        # TODO: process multiple videos?
        file_path = self.get_file_path(video_id=video_id, video=video)

        # Short-circuit if we can't find the file
        # fetch the file from server if not found (if DOWNLOAD_MISSING_VIDEOS=True)
        if not self.ensure_file_exists(video_id=video_id, file_path=file_path):
            self.logger.warning(' [%s] Skipping SceneDetection: video file not found locally' % video_id)
            return

        scenes = self.find_scenes(video_id, video, readonly)

        if video is None:
            self.logger.error(' [%s] SceneDetection FAILED to lookup videoId=%s' % (video_id, video_id))
            return

        self.logger.info(' [%s] SceneDetection complete!' % video_id)

        # Trigger TranscriptionTask (which will generate captions in various languages)
        self.logger.info(' [%s] SceneDetection now triggering: PhraseHinter' % video_id)
        #body['Scenes'] = scenes  # json.dumps(scenes)
        emitter.publish(routing_key='PhraseHinter', body=body)

        return


