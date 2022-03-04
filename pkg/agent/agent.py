import logging
from emitter import RabbitMqEmitter, RABBITMQ_CALLBACKS
from listener import RabbitMqListener

from constants import TaskNames


# NOTE: This is currently unused, be could be modified to provide a less distributed dev option
class RabbitMqAgent:

    def __init__(self):
        self.logger = logging.getLogger('pkg.agent.rabbit.RabbitMqAgent')
        self.emitter = None
        self.executors = []

    # Emitter works as a singleton: we should only need one to send messages to any queue
    def get_emitter(self):
        if self.emitter is None:
            self.emitter = RabbitMqEmitter()
        return self.emitter

    # Close any open channels and clear the RMQ connections from memory
    def close_all(self):
        for e in self.executors:
            e.close()

        self.executors.clear()

    # Creates and starts a new listener for the given queue with the given callback fn
    def add_listener(self, queue, callback):
        self.executors.append(RabbitMqListener(queue_name=queue, callback=callback))

    # Creates and starts a new listener for each known value in the TaskName enum
    def add_listeners(self):
        for queue in TaskNames:
            callback = RABBITMQ_CALLBACKS.get(queue.value)
            if callback is None:
                self.logger.warning('Canceling listener for %s: no callback found' % queue)
            else:
                self.add_listener(queue=queue.value, callback=callback)

    # Reset internal data and set up emitter + all listeners
    def init_app(self):
        self.close_all()
        self.executors.append(self.get_emitter())
        self.add_listeners()



