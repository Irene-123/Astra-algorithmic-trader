import time
from datetime import datetime

from lib.modules.broker.five_paisa import FivePaisa
from lib.modules.database.database_manager import Manager as DbManager


class Manager:
    def __init__(self) -> None:
        self.broker = FivePaisa()
        self.db = DbManager()

    def fetch_new_candle(self, scrip_names:list):
        while True:
            for scrip in scrip_names:
                data = self.broker.fetch_historical_data(
                    scrip_name=scrip,
                    time_interval="1m",
                    from_dt=datetime.now.strftime(),
                    to_dt=datetime.now.strftime()
                )
                self.db.add_historical_data(data)
            time.sleep(60)