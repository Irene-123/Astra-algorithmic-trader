from lib.modules.live_data_fetch.api_client import Broker
obj = Broker()
import time

while True:
    values= obj.values
    print(values)
    time.sleep(2)