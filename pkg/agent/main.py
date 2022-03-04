import logging
import os
import sys

from listener import RabbitMqListener

# TODO: No access to config here?
RABBITMQ_QUEUENAME = os.getenv('RABBITMQ_QUEUENAME', '')
RABBITMQ_URI = os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/%2f')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')


if __name__ == '__main__':
    DEBUG = os.getenv('DEBUG', True)

    # configure logging
    if DEBUG:
        logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

    if RABBITMQ_URI is None or RABBITMQ_URI == '':
        logging.error("RABBITMQ_URI must be set")
        sys.exit(1)

    if RABBITMQ_QUEUENAME is None or RABBITMQ_QUEUENAME == '':
        logging.error("RABBITMQ_QUEUENAME must be set")
        sys.exit(1)

    # NOTE: RABBITMQ_EXCHANGE is optional

    listener = RabbitMqListener(RABBITMQ_QUEUENAME)

    try:
        logging.info('Starting RabbitMqListener: %s' % RABBITMQ_QUEUENAME)
        listener.start_consuming()
    finally:
        logging.warning('Shtopping RabbitMqListener: %s' % RABBITMQ_QUEUENAME)
        listener.close()
