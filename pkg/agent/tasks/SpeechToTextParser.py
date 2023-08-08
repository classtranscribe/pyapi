from .AbstractTask import AbstractTask, TaskNames
from pkg.agent.tasks.lib import whisper

class ExampleTask(AbstractTask):
    @staticmethod
    def get_name():
        return TaskNames.SpeechToTextParser

    def parse_video(self, videoid):
        # fetch video (?)
        video = None
        # extract audio

        # whisper parse
        whisper.transcribe(audio)

        

    def run_task(self, body, emitter):
        self.logger.info(' [.] AccessibleGlossary message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] AccessibleGlossary started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have phrase hints
        # if not force and VIDEO_GLOSSARY_KEY in video and video[VIDEO_GLOSSARY_KEY]:
        if not force and VIDEO_PH_ID in video and video[VIDEO_PH_ID]:
            # TODO: trigger TranscriptionTask
            self.logger.warning(' [%s] Skipping AccessibleGlossary: glossary already exist' % video_id)
            return

        if video is None:
            self.logger.error(' [%s] AccessibleGlossary FAILED to lookup terms in videoId=%s' % (video_id, video_id))
            return

        self.generate_accessible_glossary(video_id, video, phrases, readonly)

        self.logger.info(' [%s] AccessibleGlossary complete!' % video_id)
