import logging
import os

import connexion

from pkg import config
from pkg.db.db import db, ma
from pkg.resolver import OperationResolver

logger = logging.getLogger("server")
debug = os.getenv('DEBUG', True)

# configure logging
if debug:
    logging.basicConfig(
        format='%(asctime)-15s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(
        format='%(asctime)-15s %(message)s', level=logging.INFO)

connex_app = connexion.FlaskApp(__name__, debug=debug)

# add swagger spec via URL
if str.startswith(config.SWAGGER_URL, "http"):
    # fetch remote openapi spec
    connex_app.add_api(config.download_remote_swagger_to_temp_file(),
                       # resolver=DebugRestyResolver('api.v2'),
                       resolver=OperationResolver('api'),
                       arguments={'title': 'ClassTranscribe API'}, resolver_error=501)
else:
    # use local openapi spec
    connex_app.add_api(config.SWAGGER_URL,
                       # resolver=DebugRestyResolver('api.v2'),
                       resolver=OperationResolver('api'),
                       arguments={'title': 'ClassTranscribe API'}, resolver_error=501)

app = connex_app.app

# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True


# init and create database tables
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    # connect app with sqlalchemy and marshmallow
    db.init_app(app)
    ma.init_app(app)

    # start the flask app on the specified port (default=5000)
    connex_app.run(port=os.getenv('PORT', 5000),
                   host='0.0.0.0',
                   server='flask',
                   debug=True)  # debug)
