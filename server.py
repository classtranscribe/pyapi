import logging
import os

import connexion
from pkg import config

logger = logging.getLogger("server")


from pkg.resolver import OperationResolver, DebugRestyResolver

if __name__ == '__main__':
    debug = os.getenv('DEBUG', False)

    # Configure logging
    if debug:
        logging.basicConfig(
            format='%(asctime)-15s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(
            format='%(asctime)-15s %(message)s', level=logging.INFO)

    app = connexion.FlaskApp(__name__, debug=debug)

    if str.startswith(config.SWAGGER_URL, "http"):
        # fetch remote openapi spec
        app.add_api(config.download_remote_swagger_to_temp_file(),
                    # resolver=DebugRestyResolver('api.v2'),
                    resolver=OperationResolver('api'),
                    arguments={'title': 'ClassTranscribe API'}, resolver_error=501)
    else:
        # use local openapi spec
        app.add_api(config.SWAGGER_URL,
                    # resolver=DebugRestyResolver('api.v2'),
                    resolver=OperationResolver('api'),
                    arguments={'title': 'ClassTranscribe API'}, resolver_error=501)

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

    app.run(port=5000, host='0.0.0.0', server='flask', debug=debug)
