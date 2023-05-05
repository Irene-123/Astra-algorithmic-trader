import os
import json

# GLOBAL PATHS
# ===========================================================================================
BASE = os.path.dirname(os.path.abspath(__file__))
MODULES_DIRECTORY = os.path.join(BASE, "lib/modules")
LIVE_DATA_FETCH_DIRECTORY = os.path.join(MODULES_DIRECTORY, "live_data_fetch")
BROKER_CREDENTIALS_FILE = os.path.join(LIVE_DATA_FETCH_DIRECTORY, "broker_credentials.json")
SCRIP_MASTER_FILE = os.path.join(LIVE_DATA_FETCH_DIRECTORY, "script_master.csv")
UI_DIRECTORY = os.path.join(BASE, "lib/ui")

# CREATION OF DIRECTORIES
# ===========================================================================================
EXECUTION_DIRECTORIES = []
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
        json.dump(broker_cred, file)
   
# GLOBAL VARIABLES
# ===========================================================================================     
APPLICATION_REFRESH_TIME = 50   # ms