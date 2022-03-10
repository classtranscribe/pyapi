import time

from .AbstractTask import AbstractTask

# no internal dependencies


class ExampleTask(AbstractTask):
    @staticmethod
    def get_name():
        return "ExampleTask"

    def run_task(self, body, emitter):
        self.logger.info(' [.] ExampleTask now running...')
        # ExampleTask just waits for 12 seconds
        time.sleep(5)
        self.logger.info(' [.] ExampleTask completed!')

