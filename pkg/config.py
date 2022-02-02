import datetime
import os
import requests
import tempfile

import logging

logger = logging.getLogger('config')


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'db.sqlite')




### REMOVEME

DOMAIN = 'local.ndslabs.org'

# v1

# EtcdStore
ETCD_HOST = os.getenv('ETCD_HOST', '127.0.0.1')
ETCD_PORT = os.getenv('ETCD_PORT', 4001)
ETCD_BASE_PATH = os.getenv('ETCD_BASE_PATH', '/ndslabs')

# MongoStore
MONGO_HOST = os.getenv('MONGO_HOST', '127.0.0.1')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_DATABASE = os.getenv('MONGO_DB', 'ndslabs')

# Kubernetes
KUBE_HOST = os.getenv('KUBE_HOST', 'localhost')
KUBE_PORT = os.getenv('KUBE_PORT', 6443)
KUBE_TOKENPATH = os.getenv('KUBE_TOKENPATH', '/run/secrets/kubernetes.io/serviceaccount/token')
KUBE_QPS = os.getenv('KUBE_QPS', 50)
KUBE_BURST = os.getenv('KUBE_BURST', 100)

# JWT Auth
JWT_SECRET = os.getenv('JWT_SECRET', 'thisisnotverysecret')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_DELTA_MINS = os.getenv('JWT_EXP_DELTA_MINS', 300)
JWT_TIMEOUT = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)


# v2
MONGO_USER = 'admin'
MONGO_PASS = 'mysupersecretamazingawesomepasswordthatnobodycouldeverguess'
MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DATABASE)


KUBE_WORKBENCH_RESOURCE_PREFIX = ''
KUBE_WORKBENCH_NAMESPACE = ''
KUBE_SINGLEPOD = False   # TODO: Should we continue want to support this?
KUBE_PVC_STORAGECLASS = 'hostpath'

# Use central Keycloak
KC_HOST = 'https://keycloak.workbench.ndslabs.org'
KC_REALM = 'workbench-dev'
KC_ENDPOINT = '%s/auth/realms/%s/.well-known/openid-configuration' % (KC_HOST, KC_REALM)


# TODO: fetch token
# curl https://keycloak.workbench.ndslabs.org/auth/realms/workbench-dev/protocol/openid-connect/token -XPOST --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'client_id=workbench-local' --data-urlencode 'grant_type=password' --data-urlencode 'username=test' --data-urlencode 'password=mysamplepasswordissupersecure' --data-urlencode 'scope=openid' --data-urlencode 'client_secret=73305daa-c3d9-4ec7-aec0-caa9b030e182'

SWAGGER_URL = os.getenv('SWAGGER_URL', 'openapi/swagger-ndslabs.yaml')


def get_resource_name(*args):
    if KUBE_WORKBENCH_NAMESPACE and KUBE_WORKBENCH_RESOURCE_PREFIX:
        return "%s-%s" % (KUBE_WORKBENCH_RESOURCE_PREFIX, "-".join(args))
    else:
        return "-".join(args)


def get_resource_namespace(username):
    if KUBE_WORKBENCH_NAMESPACE:
        return KUBE_WORKBENCH_NAMESPACE
    else:
        return username


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
        logger.error("Failed to fetch swagger spec: %s" % e)
        raise SystemExit(e)


def load_kc_realm_config():
    try:
        resp = requests.get('%s/auth/realms/%s' % (KC_HOST, KC_REALM))
        resp.raise_for_status()
        open_id_config = resp.json()
        return open_id_config
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch keycloak realm config: %s" % e)
        raise SystemExit(e)


KC_REALM_CONFIG = load_kc_realm_config()


# TODO: fetch from https://keycloak.workbench.ndslabs.org/auth/realms/workbench-dev
KC_PUBLICKEY_BODY = KC_REALM_CONFIG['public_key']
KC_PUBLICKEY = '''
-----BEGIN PUBLIC KEY-----
%s
-----END PUBLIC KEY-----
''' % KC_PUBLICKEY_BODY
