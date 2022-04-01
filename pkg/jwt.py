import connexion
import logging
import datetime
import os

#from jsonschema import validate
#from pkg import types

from jose import JWTError, jwt

import config

logger = logging.getLogger('pkg.jwt')


def encode(user_id, user):
    iat = datetime.datetime.utcnow()
    exp = iat + config.JWT_TIMEOUT
    server = os.uname()[1]

    payload = {
        "exp": exp,
        "id": user_id,
        "iat": iat,
        "server": server,
        "user": user
    }

    return jwt.encode(payload, config.JWT_SECRET, config.JWT_ALGORITHM)


def safe_decode(jwt_token):
    try:
        return jwt.decode(jwt_token, config.JWT_SECRET, config.JWT_ALGORITHM)
    except JWTError as e:
        logger.error('Failed to decode JWT: ', e)


def decode(jwt_token):
    return jwt.decode(jwt_token, config.JWT_SECRET, config.JWT_ALGORITHM)


def get_token_from_headers():
    if 'Authorization' not in connexion.request.headers:
        return ''   # Missing credentials / token
    return connexion.request.headers.get('Authorization').replace('Bearer ', '').replace('bearer ', '')



def get_token_from_cookies():
    return connexion.request.cookies.get('token')


def get_username_from_token():
    token = get_token_from_headers()
    claims = safe_decode(token)
    return claims['namespace']


def validate_apikey_header(apikey, required_scopes):
    if 'Authorization' not in connexion.request.headers:
        return 401   # Missing credentials / token

    try:
        # Fetch and decode X-API-TOKEN header
        token = get_token_from_headers()
        claims = decode(token)

        # TODO: Check authorization
        # return 403  # Credentials fine, but user is not allowed

        return 200   # Credentials fine, access granted
    except JWTError as e:
        logger.error('Failed to decode JWT: ', e)
        return 401   # Bad credentials / bad format


def validate_auth_cookie():
    if 'token' not in connexion.request.cookies:
        return 401   # Missing credentials / token

    try:
        # Fetch and decode Cookie
        token = get_token_from_cookies()
        claims = decode(token)

        # TODO: Check authorization
        # return 403  # Credentials fine, but user is not allowed

        return 200  # Credentials fine, access granted
    except JWTError as e:
        logger.error('Failed to decode JWT: ', e)
        return 401  # Bad credentials / bad format

