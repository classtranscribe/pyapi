import logging
from abc import ABC, abstractmethod
import time


class AbstractTask(ABC):

    @staticmethod
    def get_name():
        pass

    def __init__(self):
        self.logger = logging.getLogger("pkg.agent.tasks.%s" % self.get_name())

    def rabbitpy_callback(self, message, emitter):
        try:
            body = message.json()
            self.run_timed_task(body=body, emitter=emitter)
            message.ack()
        except Exception as e:
            self.logger.error(" [x] Failed running %s: %s" % (self.get_name(), str(e)))

    @abstractmethod
    def run_task(self, body, emitter):
        pass

    def run_timed_task(self, body, emitter):
        start_time = time.time_ns() / 1000000
        self.logger.debug(" [✓] Running %s: %s" % (self.get_name(), str(body)))
        self.run_task(body=body, emitter=emitter)
        self.logger.debug(" [✓] Done")
        end_time = time.time_ns() / 1000000
        duration = end_time - start_time
        self.logger.debug(' [✓] %s completed in %d ms' % (self.get_name(), duration))