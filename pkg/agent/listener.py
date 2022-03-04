import logging
import os
import threading

import rabbitpy

from tasks.QueueAwaker import QueueAwaker
from tasks.ExampleTask import ExampleTask

# no pkg dependencies allowed, no access to config
# from .. import config

# pull from env manually (use same keys as pkg/config.py)
RABBITMQ_URI = os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/%2f')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')

RABBITMQ_CALLBACKS = {
    'QueueAwaker': QueueAwaker().callback,
    'ExampleTask': ExampleTask().callback,
}

# RabbitMqEmitter is used to consume messages from a specific queue
# It is advised to run only one listener per-container so that they can be easily scaled up and down
class RabbitMqListener:

    def __init__(self, queue_name):
        self.logger = logging.getLogger('pkg.agent.rabbit.RabbitMqEmitter')
        self.connection = rabbitpy.Connection(url=RABBITMQ_URI)
        self.channel = self.connection.channel()
        self.channel.enable_publisher_confirms()
        self.exchange = RABBITMQ_EXCHANGE
        self.queue_name = queue_name
        self.logger = logging.getLogger('pkg.agent.rabbit.RabbitMqListener.%s' % queue_name)
        self.init_queue(queue_name)
        self.thread = None

    def start_consuming_threaded(self):
        self.thread = threading.Thread(target=self.start_consuming)
        self.thread.start()

    def init_exchange(self):
        if RABBITMQ_EXCHANGE != '':
            self.exchange = rabbitpy.Exchange(channel=self.channel, name=RABBITMQ_EXCHANGE)
            self.exchange.declare()

    def init_queues(self):
        for queue_name in RABBITMQ_CALLBACKS.keys():
            self.init_queue(queue_name=queue_name)

    def init_queue(self, queue_name):
        queue = rabbitpy.Queue(channel=self.channel, name=queue_name, durable=True)
        queue.declare()
        return queue

    def cleanup(self):
        if self.channel is not None:
            self.channel.close()
            self.channel = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def start_consuming(self):
        self.logger.debug(" [✓] Started listening on queue: %s" % self.queue_name)
        callback = RABBITMQ_CALLBACKS[self.queue_name]
        queue = self.init_queue(self.queue_name)

        # Consume the message
        for message in queue:
            # message.pprint(True)
            callback(message=message)

    def stop_consuming(self):
        self.logger.debug(" [✓] Stopping listening on queue: %s" % self.queue_name)
        if self.thread is not None:
            self.thread.join(timeout=10)
        self.logger.debug(' [×] Stopped listening on queue: %s' % self.queue_name)

    def close(self):
        self.stop_consuming()
        self.cleanup()
