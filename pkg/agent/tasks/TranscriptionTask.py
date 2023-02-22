import time
import json
import os
import requests
import whisper
from .AbstractTask import AbstractTask, TaskNames

# no internal dependencies

class TranscriptionTask(AbstractTask):
    @staticmethod
    def get_name():
        return "TranscriptionTask"


    def transcribe(self, video_id, video, language, model):
        # TODO check video fetching
        model = whisper.load_model(model)
        # TODO get audio file/filepath
        transcription = whisper.transcribe(model=model, audio=audio_filepath, verbose=True)
        return transcription

    def run_task(self, body, emitter):
        video_id = body['video_id']
        self.logger.info(' [.] TranscriptionTask now running for video_id %s' % video_id)

        force = body['force']
        if force.lower() in ('true', '1', 't'):
            # TODO: delete existing captions and wipe transcription status
            return
        else:
            # TODO: short-circuit if transcription already exists
        
        parameters = body.get('TaskParameters', {})
        # TODO check if I can get custom params
        language = parameters.get('language', 'en')

        model = parameters.get('model', 'base')
        self.logger.info(' [%s] Transcription started on videoId=%s...' % (video_id, video_id))

        # Fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        if video is None:
            self.logger.error(' [%s] TranscriptionTask FAILED to fetch video with videoId=%s' % (video_id, video_id))
            return

        transcription = self.transcribe(video_id, video, language, model)
        # TODO send this on API
        self.logger.info(' [.] TranscriptionTask completed for video_id %s' % video_id)

        return
