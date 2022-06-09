import datetime
import os
import logging
import sys

PORT = os.getenv('PORT', 5000)
DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', '1', 't')
DOWNLOAD_MISSING_VIDEOS = os.getenv('DOWNLOAD_MISSING_VIDEOS', 'false').lower() in ('true', '1', 't')

# Where to store uploaded/downloaded files
# DATA_DIRECTORY = os.getenv('DATA_DIRECTORY', '.')

if DEBUG:
    logging.basicConfig(format='%(name)s\t%(asctime)-15s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(name)s\t%(asctime)-15s %(message)s', level=logging.INFO)


def print_sqlite_warning():
    logging.warning('''DEV ONLY: Using SQLITE for persistent storage...
    Please configure the following environment variables to enable persistent storage in production:
        - USE_SQLITE=0
        - POSTGRES_HOST=<postgres hostname>
        - POSTGRES_PORT=<postgres port number>
        - POSTGRES_USER=<postgres username>
        - POSTGRES_PASS=<postgres password>
        - POSTGRES_DB=<postgres database>
    ''')


def get_redacted_rmq_uri():
    prefix = RABBITMQ_URI.split('@', 1)[0]
    return RABBITMQ_URI.replace(prefix, 'amqp://********:********')


def get_redacted_db_uri():
    return SQLALCHEMY_DATABASE_URI.replace(POSTGRES_USER, '********', 1).replace(POSTGRES_PASS, '********', 1)


# Database connection
basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_PATH = '%s/db.sqlite' % basedir
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLITE_PATH
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() in ('true', '1', 't')

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASS = os.getenv('POSTGRES_PASS', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ct2019db')

SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True

# AMQP Connection
RABBITMQ_URI = os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/%2f')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')

# Listener only (emitter can publish to any queue)
RABBITMQ_QUEUENAME = os.getenv('RABBITMQ_QUEUENAME', '')

# JWT Auth
JWT_SECRET = os.getenv('JWT_SECRET', 'thisisnotverysecret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_MINS = os.getenv('JWT_EXP_DELTA_MINS', 300)
JWT_TIMEOUT = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)


#SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/sample.yaml')
SWAGGER_URL = os.getenv('SWAGGER_URL', basedir + '/openapi/swagger.json')


if RABBITMQ_URI is None or RABBITMQ_URI == '':
    logging.error("RABBITMQ_URI must be set")
    sys.exit(1)

# NOTE: RABBITMQ_EXCHANGE is optional
if RABBITMQ_EXCHANGE is None or RABBITMQ_EXCHANGE == '':
    logging.warning("Using RabbitMQ default exchange")
else:
    logging.warning("Using RabbitMQ exchange: %s" % RABBITMQ_EXCHANGE)
