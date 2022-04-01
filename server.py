import logging

import connexion

import config

from pkg import resolver
from config import USE_SQLITE, SQLALCHEMY_DATABASE_URI, POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, get_redacted_db_uri, print_sqlite_warning
from pkg.db.db import db, ma
from pkg.agent.rabbitpy_wrapper import rabbitpy_emitter as emitter

DEBUG = config.DEBUG

# set up Flask + Connexion app
connex_app = connexion.FlaskApp(__name__, debug=DEBUG)
app = connex_app.app

# set up internal configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['PROPAGATE_EXCEPTIONS'] = config.PROPAGATE_EXCEPTIONS

# configure database connection
if USE_SQLITE:
    logging.info('Using SQLite: %s' % SQLALCHEMY_DATABASE_URI)
    print_sqlite_warning()
else:
    logging.info('Connecting to Postgres: %s' % (get_redacted_db_uri()))
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s' \
                            % (POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)


# init and create database tables
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    PORT = config.PORT

    # configure Flask + Connexion app
    resolver.load_swagger_spec(connex_app)

    # connect app with sqlalchemy and marshmallow
    db.init_app(app)
    ma.init_app(app)

    try:
        # start the flask app on the specified port (default=5000)
        logging.info("Serving API on port %d..." % PORT)
        app.run(port=PORT, host='0.0.0.0', debug=DEBUG)
    finally:
        logging.warning('Shutting down all RabbitMQ executors...')
        emitter.close()

