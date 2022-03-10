import datetime
import os
import logging

from pkg.agent import constants

# AMQP Connection
RABBITMQ_URI = constants.RABBITMQ_URI
RABBITMQ_EXCHANGE = constants.RABBITMQ_EXCHANGE


DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', '1', 't')
PORT = os.getenv('PORT', 5000)

if DEBUG:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

# Database connection
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True

USE_SQLITE = constants.USE_SQLITE
SQLALCHEMY_DATABASE_URI = constants.SQLALCHEMY_DATABASE_URI

# JWT Auth
JWT_SECRET = os.getenv('JWT_SECRET', 'thisisnotverysecret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_MINS = os.getenv('JWT_EXP_DELTA_MINS', 300)
JWT_TIMEOUT = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)


#SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/sample.yaml')
SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/swagger.json')
