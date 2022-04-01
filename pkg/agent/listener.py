import logging
import rabbitpy

from config import RABBITMQ_URI, RABBITMQ_EXCHANGE

from pkg.agent.emitter import RabbitMqEmitter
from pkg.agent.psycopg_wrapper import db
from pkg.agent.constants import RABBITMQ_CALLBACKS


# RabbitMqEmitter is used to consume messages from a specific queue
# It is advised to run only one listener per-container so that they can be easily scaled up and down
class RabbitMqListener(RabbitMqEmitter):

    def __init__(self, queue_name):
        super().__init__()
        self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqEmitter')
        self.connection = rabbitpy.Connection(url=RABBITMQ_URI)
        self.channel = self.connection.channel()
        self.channel.enable_publisher_confirms()
        self.exchange = RABBITMQ_EXCHANGE
        self.queue_name = queue_name
        self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqListener.%s' % queue_name)
        self.init_queue(queue_name)
        self.thread = None

    def start_consuming(self):
        self.logger.debug(" [✓] Started listening on queue: %s" % self.queue_name)
        callback = RABBITMQ_CALLBACKS[self.queue_name]
        queue = self.init_queue(self.queue_name)

        # Consume the message
        for message in queue:
            # message.pprint(True)
            callback(message=message, emitter=self)

    def stop_consuming(self):
        self.logger.debug(" [✓] Stopping listening on queue: %s" % self.queue_name)
        if self.thread is not None:
            self.thread.join(timeout=10)
        self.logger.debug(' [×] Stopped listening on queue: %s' % self.queue_name)

    def close(self):
        self.stop_consuming()
        self.cleanup()
