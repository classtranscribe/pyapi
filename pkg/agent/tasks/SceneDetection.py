import base64
import json
import os

import requests

from .AbstractTask import AbstractTask, TaskNames

from pkg.agent.tasks.lib import scenedetector, phrasehinter

# from client import client

import config

target_host = 'https://ct-dev.ncsa.illinois.edu'

# TODO: fetch service account jwt (from config / env?)
jwt = 'example'

class SceneDetection(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.SceneDetection

    def ensure_file_exists(self, video_id, file_path):
        # file not found, attempt to fetch it
        # FIXME: ct-dev returning 403 for remote requests
        if config.DOWNLOAD_MISSING_VIDEOS and not os.path.exists(file_path):
            # fetch video file using static data path
            self.logger.info(' [%s] SceneDetection downloading video data locally: %s' % (video_id, file_path))
            try:
                with requests.get('%s%s' % (target_host, file_path), stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            # If you have chunk encoded response uncomment if
                            # and set chunk_size parameter to None.
                            # if chunk:
                            f.write(chunk)
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
        resp = requests.get(url='%s/api/Task/Video?videoId=%s' % (target_host, video_id),
                            headers={'Authorization': 'Bearer %s' % jwt})
        self.logger.info(' [%s] SceneDetection fetched video: %s' % (video_id, resp.text))
        video = resp.json()
        return video

    def run_task(self, body, emitter):
        video_id = body['video_id']
        force = body['force'] if 'force' in body else False

        self.logger.info(' [%s] SceneDetection started on videoId=%s...' % (video_id, video_id))

        # TODO: fetch video metadata by id
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have scene data
        if not force and video['sceneData']:
            # TODO: trigger transcription?
            self.logger.warning(' [%s] Skipping SceneDetection: sceneData already exists' % video_id)
            return

        # get file_path from video
        # Note that because we're accessing the raw file, we're assuming that
        # we're running on the same server and/or in the same file space
        # TODO: process multiple videos?
        file_path = video['video1']['path']

        # Short-circuit if we can't find the file
        if not self.ensure_file_exists(video_id=video_id, file_path=file_path):
            self.logger.error(' [%s] Skipping SceneDetection: video file not found locally' % video_id)
            return

        # Call scenedetector.find_scenes, store scene data
        try:
            self.logger.info(' [%s] SceneDetection getting scenes for %s...' % (video_id, file_path))
            scenes = json.loads(scenedetector.find_scenes(video_path=file_path))
            video['sceneData'] = scenes
            #requests.post(url='%s/api/Task/UpdateSceneData?videoId=%s' % (target_host, video_id),
            #              headers={'Authorization': 'Bearer %s' % jwt},
            #              data=json.dumps(video))
            self.logger.info(' [%s] SceneDetection found scenes: %s' % (video_id, scenes))
        except Exception as e:
            self.logger.error(
                ' [%s] SceneDetection failed to detect scenes in videoId=%s: %s' % (
                    video_id, file_path, str(e)))
            return

        # Gather raw phrases from scenes
        self.logger.info(' [%s] SceneDetection gathering raw phrases...' % video_id)
        all_phrases = ''
        for scene in scenes:
            all_phrases += str(scene['phrases'])
        video['all_phrases'] = all_phrases.join("\n")

        # Pass raw phrases into phrasehinter.to_phrase_hints
        # Note that this requires 'brown' and 'stopwords' dependencies from NTLK
        try:
            self.logger.info(' [%s] SceneDetection generating phrase hints...' % video_id)
            phrase_hints = phrasehinter.to_phrase_hints(raw_phrases=all_phrases)
            video['phrase_hints'] = phrase_hints

            # TODO: Save generated hints to video in database
            #requests.post(url='%s/api/Task/UpdatePhraseHints?videoId=%s&phraseHints=%s' % (target_host, video_id, phrase_hints),
            #              headers={'Authorization': 'Bearer %s' % jwt},
            #              data=json.dumps(video))
            self.logger.info(' [%s] SceneDetection generated phrase hints: %s' % (video_id, phrase_hints))

        except Exception as e:
            self.logger.error(
                ' [%s] SceneDetection failed to detect scenes in videoId=%s: %s' % (
                    video_id, file_path, str(e)))
            return

        self.logger.info(' [%s] SceneDetection complete!' % video_id)

        # TODO: Trigger TranscriptionTask (which will generate captions in various languages)
        # self.logger.info(' [.] SceneDetection now triggering: TranscriptionTask...')
        # emitter.publish(routing_key='TranscriptionTask', body=body)

        return


