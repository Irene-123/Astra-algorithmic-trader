from lib.modules.live_data_fetch.api_client import Broker
from lib.strategies.manager import Manager
broker = Broker()
manager= Manager() 
import time

while True:
    values= broker.values
    manager.place_order(values=values) 
    time.sleep(2)