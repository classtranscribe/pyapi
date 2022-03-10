import os

from enum import Enum

SQLITE_PATH = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLITE_PATH
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() in ('true', '1', 't')

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASS = os.getenv('POSTGRES_PASS', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ct2019db')

if not USE_SQLITE:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s' \
                              % (POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)

RABBITMQ_URI = os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/%2f')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')


# Map task to queuename
class TaskNames(Enum):
    QueueAwaker = 'QueueAwaker'                     # QueueAwaker
    ExampleTask = 'ExampleTask'                     # ExampleTask
    SceneDetection = 'SceneDetection'                     # SceneDetection
    AltExampleTask = 'AltExampleTask'
    # ... Add new tasks here