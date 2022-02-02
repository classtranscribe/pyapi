
import connexion


def run():
    token_user_id = connexion.context['token_info']['user']

    return token_user_id


def get(account_id):
    #token_user_id = connexion.context['token_info']['user']

    account_info = etcdClient.getAccountInfo(account_id)

    if account_info == '':
        return '', 204
    else:
        return account_info, 200


def put(account_id):
    print(connexion.request.json)
    account_info = connexion.request.json
    # if types.validate_account_info(account_info):
    #    return etcdClient.setAccountInfo(connexion.request.json), 200
    # else:
    #    return '', 204
    return etcdClient.setAccountInfo(connexion.request.json), 200


def delete(account_id):
    return etcdClient.deleteAccountInfo(account_id)
