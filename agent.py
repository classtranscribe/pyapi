import logging
import sys

from pkg.agent.listener import RabbitMqListener
from config import RABBITMQ_QUEUENAME, get_redacted_rmq_uri


if RABBITMQ_QUEUENAME is None or RABBITMQ_QUEUENAME == '':
    logging.error("RABBITMQ_QUEUENAME must be set")
    sys.exit(1)

if __name__ == '__main__':
    listener = RabbitMqListener(RABBITMQ_QUEUENAME)

    try:
        logging.info('Connecting to RabbitMQ: %s' % get_redacted_rmq_uri())
        listener.start_consuming()
    finally:
        logging.warning('Shutting down RabbitMQ connection...')
        listener.close()
        #logging.warning('Shutting down PostgreSQL connection...')
