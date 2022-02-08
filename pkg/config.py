import datetime
import os
import requests
import tempfile

import logging

from pkg import resolver


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


# JWT Auth
JWT_SECRET = os.getenv('JWT_SECRET', 'thisisnotverysecret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_MINS = os.getenv('JWT_EXP_DELTA_MINS', 300)
JWT_TIMEOUT = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)


SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/sample.yaml')
#SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/swagger.json')


# Downloads a remote swagger spec from the configured SWAGGER_URL and save it to a temp file.
# Returns the path to the temp file created.
def download_remote_swagger_to_temp_file(temp_file_name='swagger-keycloak.yml'):
    try:
        # fetch swagger spec, parse response
        swagger_response = requests.get(SWAGGER_URL)
        swagger_response.raise_for_status()
        swagger_spec_text = swagger_response.text

        # save swagger spec to temp file
        temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
        with open(temp_file_path, 'w') as f:
            f.write(swagger_spec_text)

        return temp_file_path
    except requests.exceptions.RequestException as e:
        logging.error("Failed to fetch swagger spec: %s" % e)
        raise SystemExit(e)


def load_swagger_spec(connex_app):
    # add swagger spec via URL
    if str.startswith(SWAGGER_URL, "http"):
        # fetch remote openapi spec
        connex_app.add_api(download_remote_swagger_to_temp_file(),
                           # resolver=resolver.DebugRestyResolver('api.v2'),
                           resolver=resolver.OperationResolver('api'),
                           arguments={'title': 'ClassTranscribe API'}, resolver_error=501)
    else:
        # use local openapi spec
        connex_app.add_api(SWAGGER_URL,
                           # resolver=resolver.DebugRestyResolver('api.v2'),
                           resolver=resolver.OperationResolver('api'),
                           arguments={'title': 'ClassTranscribe API'}, resolver_error=501)


def get_redacted_db_uri():
    return SQLALCHEMY_DATABASE_URI.replace(POSTGRES_USER, '********', 1).replace(POSTGRES_PASS, '********', 1)


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