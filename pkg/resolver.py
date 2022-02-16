import os
import re
import tempfile

import connexion
import requests
from connexion import Resolver

import logging

from pkg.config import SWAGGER_URL


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
                           resolver=OperationResolver('api'),
                           arguments={'title': 'ClassTranscribe API'}, resolver_error=501)
    else:
        # use local openapi spec
        connex_app.add_api(SWAGGER_URL,
                           resolver=OperationResolver('api'),
                           arguments={'title': 'ClassTranscribe API'}, resolver_error=501)


class OperationResolver(Resolver):
    """
    Resolves endpoint functions using REST semantics (unless overridden by specifying operationId)
    """

    def __init__(self, default_module_name, collection_endpoint_name='run'):
        """
        :param default_module_name: Default module name for operations
        :type default_module_name: str
        """
        Resolver.__init__(self)
        self.default_module_name = default_module_name
        self.collection_endpoint_name = collection_endpoint_name

    def resolve_operation_id(self, operation):
        """
        Resolves the operationId using REST semantics unless explicitly configured in the spec

        :type operation: connexion.operations.AbstractOperation
        """
        if operation.operation_id:
            return Resolver.resolve_operation_id(self, operation)

        return self.resolve_operation_id_using_rest_semantics(operation)

    def resolve_operation_id_using_rest_semantics(self, operation):
        """
        Resolves the operationId using REST semantics

        :type operation: connexion.operations.AbstractOperation
        """

        elements = operation.path.split('/')[1:]

        # prefix part of the function name (i.e. file on disk)
        if operation.router_controller:
            name = operation.router_controller
        else:
            name = self.default_module_name

            # append all other paths using _ names, except parameters
            for path in elements:
                if '{' not in path:
                    if name.count('.') < 2:
                        name += '.' + path.replace('-', '_')
                    else:
                        name += '_' + path.replace('-', '_')

        # append method
        method = operation.method.lower()
        if method == 'get' and '{' not in elements[-1]:
            method = self.collection_endpoint_name

        if name.count('.') < 2:
            return name + '.' + method
        else:
            return name + '_' + method



