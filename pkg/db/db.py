import logging

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from pkg import config

db = SQLAlchemy()
ma = Marshmallow()


def get_redacted_db_uri():
    return config.SQLALCHEMY_DATABASE_URI\
            .replace(config.POSTGRES_USER, '********', 1)\
            .replace(config.POSTGRES_PASS, '********', 1)


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
