import logging
import time

# no internal dependencies

class QueueAwaker:
    @staticmethod
    def get_name():
        return "QueueAwaker"

    def __init__(self):
        self.logger = logging.getLogger(QueueAwaker.get_name())

    def callback(self, message):
        start_time = time.time_ns() / 1000000
        body = message.json()
        self.logger.info(" [✓] Running QueueAwaker: %s" % str(body))

        # Insert task logic here

        self.logger.info(" [✓] Done")
        end_time = time.time_ns() / 1000000
        duration = end_time - start_time
        self.logger.debug(' [✓] %s completed in %d ms' % (self.get_name(), duration))
        message.ack()
