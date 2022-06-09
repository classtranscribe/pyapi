import logging
import sys
import time

from pkg.agent.listener import RabbitMqListener
from config import RABBITMQ_QUEUENAME, get_redacted_rmq_uri
from pkg.agent.tasks.AbstractTask import TaskNames

if RABBITMQ_QUEUENAME is None or RABBITMQ_QUEUENAME == '':
    logging.error("RABBITMQ_QUEUENAME must be set")
    sys.exit(1)

if __name__ == '__main__':
    listener = RabbitMqListener(RABBITMQ_QUEUENAME)

    #{
    #    "Data": "414d71cb-808a-47c0-be3b-b7d6f47710fc",
    #    "TaskParameters": {"Force": true, "Metadata": null, "ReadOnly": false}
    #}
    try:
        logging.info('Connecting to RabbitMQ: %s' % get_redacted_rmq_uri())
        listener.start_consuming()
        while True:
            time.sleep(1)
    finally:
        logging.warning('Shutting down RabbitMQ connection...')
        listener.close()
        logging.info('RabbitMQ shutdown successfully')
