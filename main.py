from lib.modules.broker.five_paisa import FivePaisa
broker = FivePaisa()
import time



while True:
    values= broker.values
    time.sleep(2)