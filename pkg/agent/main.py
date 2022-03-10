import logging
import os
import sys

from psycopg2 import Error

from listener import RabbitMqListener
from constants import RABBITMQ_URI, RABBITMQ_EXCHANGE, SQLALCHEMY_DATABASE_URI
from psycopg_wrapper import db

RABBITMQ_QUEUENAME = os.getenv('RABBITMQ_QUEUENAME', '')


if __name__ == '__main__':
    DEBUG = os.getenv('DEBUG', False)

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
    if RABBITMQ_EXCHANGE is None or RABBITMQ_EXCHANGE == '':
        logging.warning("Using RabbitMQ default exchange")
    else:
        logging.warning("Using RabbitMQ exchange: %s" % RABBITMQ_EXCHANGE)

    listener = RabbitMqListener(RABBITMQ_QUEUENAME)

    try:
        logging.info('Connecting to PostgreSQL: %s' % SQLALCHEMY_DATABASE_URI)
        db.connect()

        logging.info('Connecting to RabbitMQ: %s' % RABBITMQ_URI)
        listener.start_consuming()

    except (Exception, Error) as error:
        logging.error("Error while connecting to PostgreSQL: %s" % str(error))
    finally:
        logging.warning('Shutting down RabbitMQ connection...')
        listener.close()
        logging.warning('Shutting down PostgreSQL connection...')
        db.close()
