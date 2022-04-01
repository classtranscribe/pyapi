import logging
import rabbitpy


from config import RABBITMQ_URI, RABBITMQ_EXCHANGE
from pkg.agent.constants import RABBITMQ_CALLBACKS
# AMQP Connection



# RabbitMqEmitter is used to publish messages to a specific queue
class RabbitMqEmitter:
    def __init__(self):
        self.logger = logging.getLogger('pkg.agent.rabbit.RabbitMqEmitter')
        self.connection = rabbitpy.Connection(url=RABBITMQ_URI)
        self.channel = self.connection.channel()
        self.channel.enable_publisher_confirms()
        self.exchange = RABBITMQ_EXCHANGE
        self.init_queues()

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

    def publish(self, body, routing_key=''):
        if routing_key in list(RABBITMQ_CALLBACKS.keys()):
            message = rabbitpy.Message(channel=self.channel, body_value=body)
            message.publish(exchange=self.exchange, routing_key=routing_key, mandatory=True)
        else:
            self.logger.warning('Unrecognized queue name: %s' % routing_key)

    def close(self):
        self.logger.debug(' [⚠] Stopping emitter...')
        self.cleanup()
        self.logger.debug(' [×] Stopped emitter')

