import logging
import connexion

from api import authenticate


def run(user, token_info):
    logging.info(token_info)

    user_token = connexion.request.headers.get('Authorization').split(" ")[1]
    return authenticate.verify_token(user_token)
