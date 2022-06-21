import logging
import sys

import rabbitpy
import threading
import time

from config import RABBITMQ_URI, RABBITMQ_EXCHANGE, REQUEUE_TIMEOUT

from pkg.agent.emitter import RabbitMqEmitter
from pkg.agent.constants import RABBITMQ_CALLBACKS

MAX_FAILURES = 5


# RabbitMqEmitter is used to consume messages from a specific queue
# It is advised to run only one listener per-container so that they can be easily scaled up and down
class RabbitMqListener(RabbitMqEmitter):

    def __init__(self, queue_name):
        super().__init__()
        # self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqEmitter')
        self.connection = rabbitpy.Connection(url=RABBITMQ_URI)
        self.channel = self.connection.channel()
        self.channel.prefetch_count(1)
        self.channel.enable_publisher_confirms()
        self.exchange = RABBITMQ_EXCHANGE
        self.queue_name = queue_name
        self.logger = logging.getLogger('agent.listener.%s' % self.queue_name)
        self.init_queue(queue_name)
        self.thread = None
        self.failure_counter = 0  # stops listening if this reaches MAX_FAILURES

    def is_consuming(self):
        if self.thread is not None and self.thread.is_alive():
            return True
        return False

    def start_consuming(self):
        # no-op if already running
        if self.is_consuming():
            return

        # Start up a new consumer thread
        self.logger.info(" [⚠] Starting listening on queue: %s" % self.queue_name)
        callback = RABBITMQ_CALLBACKS[self.queue_name]
        queue = self.init_queue(self.queue_name)
        self.thread = threading.Thread(target=self.process_messages, args=(queue, callback))
        self.thread.start()
        self.logger.debug(" [✓] Started listening on queue: %s" % self.queue_name)

    def process_messages(self, queue, callback):
        while True:
            # Continuously consume any messages in the queue
            for message in queue:
                # message.pprint(True)
                try:
                    callback(message=message, emitter=self)
                    message.ack()
                    self.logger.info(" [✓] Finished processing message")
                except Exception as e:
                    #message.nack(requeue=True)
                    #self.failure_counter += 1
                    self.logger.error(f" [⚠] Failed to consume message, requeuing in {REQUEUE_TIMEOUT}: {str(e)}")
                    time.sleep(5)
                    message.nack(requeue=False)  # will automatically requeue in ~2 hours


                    #self.logger.error(" [⚠] Failed to consume message (attempt # %d/%d)" % (self.failure_counter, MAX_FAILURES))
                    #self.logger.error(" [⚠] Failed to consume message (attempt # %d/%d): %s" % (self.failure_counter, MAX_FAILURES, e))
                    #if self.failure_counter >= MAX_FAILURES:
                    #    sys.exit(1)

    def stop_consuming(self, timeout=3):
        # Join thread, if it is active
        self.logger.debug(" [⚠] Stopping listening on queue: %s" % self.queue_name)
        self.thread.join(timeout=timeout)

        # Wait for thread to die (or timeout)
        #while self.is_consuming():
        #    time.sleep(3)
        self.logger.debug(' [×] Stopped listening on queue: %s' % self.queue_name)
        self.thread = None

    def close(self):
        self.stop_consuming()
        self.cleanup()
