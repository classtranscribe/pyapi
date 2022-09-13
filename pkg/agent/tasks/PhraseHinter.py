import json
import os
import requests

from .AbstractTask import AbstractTask, TaskNames

from pkg.agent.tasks.lib import phrasehinter


VIDEO_SCENEDATA_KEY = 'sceneData'

VIDEO_PHRASEHINTS_KEY = 'phrase_hints'
VIDEO_PHRASES_KEY = 'all_phrases'
SCENE_PHRASES_KEY = 'phrases'

class PhraseHinter(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.PhraseHinter

    def generate_phrase_hints(self, video_id, video, scenes, readonly):
        # Gather raw phrases from scenes
        self.logger.info(' [%s] PhraseHinter gathering raw phrases...' % video_id)
        all_phrases = [str(scene[SCENE_PHRASES_KEY]) for scene in scenes]
        # video[VIDEO_PHRASES_KEY] = all_phrases
        self.logger.debug(' [%s] PhraseHinter found phrases' % (video_id))

        # Pass raw phrases into phrasehinter.to_phrase_hints
        # Note that this requires 'brown' and 'stopwords' dependencies from NTLK
        try:
            self.logger.info(' [%s] PhraseHinter generating phrase hints...' % video_id)
            phrase_hints = phrasehinter.to_phrase_hints(raw_phrases=all_phrases)
            # video[VIDEO_PHRASEHINTS_KEY] = phrase_hints

            #self.logger.debug(' [%s] PhraseHinter generated phrase hints: %s' % (video_id, phrase_hints))
            if readonly:
                self.logger.info(' [%s] PhraseHinter running as READONLY.. phrase hints have not been saved: %s' % (video_id, phrase_hints.join('')))
            else:
                # save generated phrase_hints to video in api
                self.jwt = self.update_jwt()
                resp = requests.post(url='%s/api/Task/UpdatePhraseHints?videoId=%s' % (self.target_host, video_id),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                     data=json.dumps({"phraseHints": phrase_hints}))
                resp.raise_for_status()
                #self.logger.debug(' [%s] PhraseHinter successfully saved phrase hints: %s' % (video_id, phrase_hints))

            return video
        except Exception as e:
            self.logger.error(
                ' [%s] PhraseHinter failed to detect scenes in videoId=%s: %s' % (video_id,
                    video_id, str(e)))
            return

    # Message Body Format:
    #     {'Data': 'db2090f7-09f2-459a-84b9-96bd2f506f68',
    #     'TaskParameters': {'Force': False, 'Metadata': None}}
    def run_task(self, body, emitter):
        self.logger.info(' [.] PhraseHinter message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] PhraseHinter started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have phrase hints
        if not force and VIDEO_PHRASEHINTS_KEY in video and video[VIDEO_PHRASEHINTS_KEY]:
            # TODO: trigger TranscriptionTask
            self.logger.warning(' [%s] Skipping PhraseHinter: phraseHints already exist' % video_id)
            return

        if video is None:
            self.logger.error(' [%s] PhraseHinter FAILED to lookup videoId=%s' % (video_id, video_id))
            return

        # TODO: Check for empty scenes / error-handling
        scenes = video[VIDEO_SCENEDATA_KEY]['Scenes']
        # scenes = json.loads(body.get('Scenes', '[]'))
        if len(scenes) == 0:
            self.logger.error(' [%s] PhraseHinter FAILED for videoId=%s: no scenes found' % (video_id, video_id))

        #self.logger.debug("Scenes fetched: %s" % scenes)
        phrases = self.generate_phrase_hints(video_id, video, scenes, readonly)

        if video is None:
            self.logger.error(' [%s] PhraseHinter FAILED for videoId=%s: to_phrase_hints failed' % (video_id, video_id))
            return

        self.logger.info(' [%s] PhraseHinter complete!' % video_id)

        # Trigger TranscriptionTask (which will generate captions in various languages)
        # self.logger.info(' [%s] PhraseHinter now triggering: TranscriptionTask' % video_id)
        # emitter.publish(routing_key='TranscriptionTask', body=body)

        # Trigger AccessibleGlossary (which will generate description for domain terms)
        self.logger.info(' [%s] PhraseHinter now triggering: AccessibleGlossary' % video_id)
        emitter.publish(routing_key='AccessibleGlossary', body=body)

        return


