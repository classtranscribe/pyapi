import time

from .AbstractTask import AbstractTask


class QueueAwaker(AbstractTask):
    @staticmethod
    def get_name():
        return "QueueAwaker"

    def run_task(self, body, emitter):
        self.logger.info(' [.] QueueAwaker triggering SceneDetection in 10s...')

        # Insert task logic here
        time.sleep(10)

        # Proof-of-concept execution of DAGs
        self.logger.info(' [.] QueueAwaker now triggering: SceneDetection...')
        emitter.publish(routing_key='SceneDetection', body=body)

        # Insert more task logic here
        time.sleep(3)
        return
