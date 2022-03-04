import datetime
import os
import logging

DEBUG = os.getenv('DEBUG', 'true').lower() in ('true', '1', 't')
PORT = os.getenv('PORT', 5000)

if DEBUG:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

# Database connection
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'db.sqlite')
USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() in ('true', '1', 't')

if not USE_SQLITE:
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
    POSTGRES_USER = os.getenv('POSTGRES_USER', '')
    POSTGRES_PASS = os.getenv('POSTGRES_PASS', '')
    POSTGRES_DB = os.getenv('POSTGRES_DB', '')
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s' \
                              % (POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)

# AMQP Connection
RABBITMQ_URI = os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/%2f')
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')

# JWT Auth
JWT_SECRET = os.getenv('JWT_SECRET', 'thisisnotverysecret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_MINS = os.getenv('JWT_EXP_DELTA_MINS', 300)
JWT_TIMEOUT = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)


#SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/sample.yaml')
SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/swagger.json')
