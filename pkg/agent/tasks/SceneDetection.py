import time

from .AbstractTask import AbstractTask

# no internal dependencies


class SceneDetection(AbstractTask):

    @staticmethod
    def get_name():
        return "SceneDetection"

    def run_task(self, body, emitter):
        self.logger.info(' [.] SceneDetection triggering ExampleTask in 10s...')

        # Insert task logic here
        time.sleep(10)

        # Proof-of-concept execution of DAGs
        self.logger.info(' [.] SceneDetection now triggering: ExampleTask...')
        emitter.publish(routing_key='ExampleTask', body=body)

        # Insert more task logic here
        time.sleep(3)
        self.logger.info(' [.] SceneDetection awaiting task completion')

        return


