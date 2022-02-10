import logging
import os

import connexion

from pkg import config
from pkg.db.db import db, ma

DEBUG = config.DEBUG
connex_app = connexion.FlaskApp(__name__, debug=DEBUG)
config.load_swagger_spec(connex_app)

# set up internal configuration
app = connex_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['PROPAGATE_EXCEPTIONS'] = config.PROPAGATE_EXCEPTIONS


# init and create database tables
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    PORT = config.PORT

    # configure logging
    if DEBUG:
        logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

    # connect app with sqlalchemy and marshmallow
    db.init_app(app)
    ma.init_app(app)

    if config.USE_SQLITE:
        config.print_sqlite_warning()
    else:
        logging.info('Connecting to Postgres: %s' % (config.get_redacted_db_uri()))

    # start the flask app on the specified port (default=5000)
    logging.info("Serving API on port %d..." % PORT)
    app.run(port=PORT,
            host='0.0.0.0',
            debug=DEBUG)
