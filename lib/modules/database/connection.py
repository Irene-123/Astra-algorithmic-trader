import psycopg2
import json

from lib.modules.exceptions.database_exceptions import *
import settings

DEFAULT_DB = 0
HISTORICAL_DB = 1
USER_DB = 2

def connect_db(db:int):
    try:
        with open(settings.DB_CREDENTIALS_FILE, 'r') as file: 
            credentials = json.load(file)
    except FileNotFoundError:
        raise CredentialsNotFoundException

    db_names = [credentials['DEFAULT_DB'], settings.HISTORICAL_DB, settings.USER_DB] 
    try:
        conn = psycopg2.connect(
            database = db_names[db],
            user = credentials['USERNAME'],
            password = credentials['PASSWORD'],
            host = credentials['HOST'],
            port = credentials['PORT']
        )
        conn.autocommit = True
    except Exception as e:
        raise FailedConnectionException(e)
    return conn



