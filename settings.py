import os
import json
import logging

# GLOBAL PATHS
# ===========================================================================================
BASE = os.path.dirname(os.path.abspath(__file__))
MODULES_DIRECTORY = os.path.join(BASE, "lib/modules")
BROKER_DIRECTORY = os.path.join(MODULES_DIRECTORY, "broker")
BROKER_CREDENTIALS_FILE = os.path.join(BROKER_DIRECTORY, "broker_credentials.json")
DATABASE_DIRECTORY = os.path.join(MODULES_DIRECTORY, "database")
DB_CREDENTIALS_FILE = os.path.join(DATABASE_DIRECTORY, "db_credentials.json")
SCRIP_MASTER_FILE = os.path.join(BROKER_DIRECTORY, "script_master.csv")
LOGS_DIR = os.path.join(BASE, "logs")

# LOGS
VERBOSE = True
STREAM_HANDLER_LOGGING_LEVEL = logging.INFO
FILE_HANDLER_LOGGING_LEVEL = logging.INFO

# DATABASE
HISTORICAL_DB = "astra_historical_data"
USER_DB = "astra_user_data" 

# CREATION OF DIRECTORIES
# ===========================================================================================
EXECUTION_DIRECTORIES = [LOGS_DIR]
for directory in EXECUTION_DIRECTORIES:
    if not os.path.exists(directory):
        os.makedirs(directory)
        
# CREATION OF CREDENTIAL FILES
# ===========================================================================================
if not os.path.exists(BROKER_CREDENTIALS_FILE):
    broker_cred = {
        "BROKER_NAME": "5Paisa",
        "EMAIL": "",
        "WEB_PASSWORD": "",
        "DOB": "",
        "APP_NAME": "",
        "APP_SOURCE": "",
        "USER_ID": "",
        "APP_PASSWORD": "",
        "USER_KEY": "",
        "ENCRYPTION_KEY": ""
    }
    with open(BROKER_CREDENTIALS_FILE, "w") as file:
        json.dump(broker_cred, file, indent=4)
SCRIPS=['NIFTY50', 'SBIN', 'TITAN', 'FOSECOIND', 'HDFCBANK', 'MRF', 'AMBUJACEM', 'TATAMOTORS']
   
# GLOBAL VARIABLES
# ===========================================================================================     
APPLICATION_REFRESH_TIME = 50   # ms