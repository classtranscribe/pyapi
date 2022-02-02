import logging

import json
import connexion
import datetime
import os

from werkzeug.exceptions import Unauthorized
from jose import JWTError, JWSError, jwt, jws
import six

#from helper import etcdClient

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_MINS = 300


def run():
    logging.info("Token info - "+connexion.context['token_info'])

    return None


def post_authenticate():
    reqJSON = connexion.request.json
    username = reqJSON['username']
    password = reqJSON['password']
    print(username, password)

    if True:  # etcdClient.checkPassword(username, password):
        token = {"token": generate_token(username)}
        return token, 200
    else:
        return '', 401


def delete_authenticate():
    print(connexion.request.auth)
    return True


def generate_token(user_id):
    iat = datetime.datetime.utcnow()
    timeout = datetime.timedelta(minutes=JWT_EXP_DELTA_MINS)
    exp = iat + timeout
    server = os.uname()[1]

    payload = {
        "exp": exp,
        "id": user_id,
        "iat": iat,
        "server": server,
        "user": user_id
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def get_secret(user, token_info) -> str:
    return '''
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    '''.format(user=user, token_info=token_info)


def verify_token(token):
    try:
        jws.verify(token, JWT_SECRET, JWT_ALGORITHM)
        return True, 200
    except JWSError:
        return JWSError, 401
