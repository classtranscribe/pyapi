import time

from .AbstractTask import AbstractTask

# no internal dependencies


class TranscriptionTask(AbstractTask):
    @staticmethod
    def get_name():
        return "TranscriptionTask"

    def run_task(self, body, emitter):
        video_id = body['video_id']
        self.logger.info(' [.] TranscriptionTask now running for video_id %s' % video_id)

        force = body['force']
        if force.lower() in ('true', '1', 't'):
            # TODO: delete existing captions and wipe transcription status
            return

        else:
            # TODO: short-circuit if transcription already exists
            return

        # TODO: Fetch video by id (to get phrases?)
        # video_id = body['video_id']

        # TODO: Attempt 10 times?

        # TODO: Set source language and target languages

        # ExampleTask just waits for 12 seconds
        # time.sleep(5)
        # self.logger.info(' [.] TranscriptionTask completed!')

