import psycopg2
import json
from lib.modules.exceptions.database_exceptions import *
import settings

def connect_db(db):
    try:
        with open(settings.DB_CREDENTIALS_FILE, 'r') as file: 
            credentials = json.load(file)
    except FileNotFoundError:
        raise CredentialsNotFoundException
    username= credentials[db]['USERNAME']
    password= credentials[db]['PASSWORD']
    host= credentials[db]['HOST']
    db_name= credentials[db]['DATABASE']
    try:
        conn= psycopg2.connect(f'postgresql://{username}:{password}@localhost:{host}/{db_name}') 
    except Exception as e:
        raise FailedConnectionException(e)  
    return conn