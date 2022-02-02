
from pkg import config

class PostgresStore:

    def __init__(self, host=config.POSTGRES_HOST, port=config.POSTGRES_PASS):
        self.client =


data_store = PostgresStore()
