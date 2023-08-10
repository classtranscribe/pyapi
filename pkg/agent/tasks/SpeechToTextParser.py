import requests
from .AbstractTask import AbstractTask, TaskNames
from pkg.agent.tasks.lib import whisper

class SpeechToTextParser(AbstractTask):
    @staticmethod
    def get_name():
        return TaskNames.SpeechToTextParser

    def parse_video(self, video_id):
        # fetch video (?)
        video = self.get_video(video_id=video_id)
        if video is None:
            self.logger.error(' [%s] FAILED to lookup videoId=%s' % (video_id, video_id))
            return
        # extract audio
        audio = video["Audio"]

        # whisper parse
        result = whisper.transcribe(audio)
        return result
        

    def run_task(self, body, emitter):
        self.logger.info(' [.] AccessibleGlossary message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        # force = parameters.get('Force', False)
        # readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] AccessibleGlossary started on videoId=%s...' % (video_id, video_id))

        result = self.parse_video(video_id)

        # TODO: switch to actual api
        requests.post(url='%s/api/Task/UpdatePhraseHints?videoId=%s' % (self.target_host, video_id),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                     data=json.dumps({"phraseHints": phrase_hints}))


        self.logger.info(' [%s] AccessibleGlossary complete!' % video_id)
