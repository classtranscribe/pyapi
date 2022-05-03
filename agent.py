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

    try:
        body = {
            'Data': '7fc3b0a5-ae81-4a46-b369-d3fb14eb0866',
            # 'Data': 'db2090f7-09f2-459a-84b9-96bd2f506f68',
            'TaskParameters': {'Force': True, 'Metadata': None, 'ReadOnly': True}
        }
        listener.publish(body=body, routing_key='SceneDetection')
        logging.info('Connecting to RabbitMQ: %s' % get_redacted_rmq_uri())
        listener.start_consuming()
        while True:
            time.sleep(1)
    finally:
        logging.warning('Shutting down RabbitMQ connection...')
        listener.close()
        logging.info('RabbitMQ shutdown successfully')
