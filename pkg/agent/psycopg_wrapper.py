import logging
import psycopg2
import sqlite3

from config import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASS, POSTGRES_PORT, POSTGRES_DB, USE_SQLITE, \
    SQLITE_PATH


class DbAdapter:
    def __init__(self):
        self.logger = logging.getLogger('DbAdapter')

        self.connection = None
        self.cursor = None

    def connect(self):
        # Connect to an existing database
        self.connection = psycopg2.connect(user=POSTGRES_USER,
                                           password=POSTGRES_PASS,
                                           host=POSTGRES_HOST,
                                           port=POSTGRES_PORT,
                                           database=POSTGRES_DB)

        # Create a cursor to perform database operations
        self.cursor = self.connection.cursor()

        # Print PostgreSQL details
        self.logger.debug("PostgreSQL server information")
        self.logger.debug(self.connection.get_dsn_parameters())

        # Executing a SQL query
        self.cursor.execute("SELECT version();")

        # Fetch result
        record = self.cursor.fetchone()
        self.logger.info("You are connected to - %s" % str(record))

        return self.connection, self.cursor


    def get_video(self, video_id):
        self.cursor.execute('SELECT * from "Video" where "Id"=\'%s\'' % video_id)


    def save_video_scenes(self, video_id, scenes):
        self.cursor.execute('UPDATE "Video" SET "Scenes"="%s" where "Id"=\'%s\'' % (scenes, video_id))


    def save_video_phrase_hints(self, video_id, phrase_hints):
        self.cursor.execute('UPDATE "Video" SET "PhraseHints"="%s" where "Id"=\'%s\'' % (phrase_hints, video_id))


    def close(self):
        if self.connection is not None:
            if self.cursor is not None:
                self.cursor.close()
            self.connection.close()
            self.logger.info("PostgreSQL connection is closed")


class SqliteDbAdapter:

    def __init__(self):
        self.logger = logging.getLogger('SqliteDbAdapter')

        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(SQLITE_PATH)
        self.cursor = self.connection.cursor()

        # Executing a SQL query
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch result
        record = self.cursor.fetchone()
        self.logger.info("Existing tables: %s" % str(record))

    def close(self):
        if self.connection is not None:
            if self.cursor is not None:
                self.cursor.close()
            self.connection.close()
            self.logger.info("PostgreSQL connection is closed")


db = None
if USE_SQLITE:
    db = SqliteDbAdapter()
else:
    db = DbAdapter()

