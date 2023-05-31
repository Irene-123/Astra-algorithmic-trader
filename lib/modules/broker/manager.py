import time
from datetime import datetime

from lib.modules.broker.five_paisa import FivePaisa
from lib.modules.database.database_manager import Manager as DbManager


class Manager:
    def __init__(self, scrip_names) -> None:
        self.broker = FivePaisa(scrip_names)
        self.db = DbManager()

    def fetch_new_candle(self, scrip_names:list, from_dt=0, to_dt=0):
        """
        Fetches new candle data for the given scrips with timeframe and returns the dataframe 
        """
        while True: 
            for scrip in scrip_names:
                if not from_dt:
                    last_row= self.db.fetch_latest_candle_from_db(scrip_name=scrip)
                    if last_row==False:
                        data= self.broker.fetch_historical_data(
                            scrip_name=scrip,
                            time_interval="1m",
                            from_dt=datetime.now().strftime("%Y-%m-%d"),
                            to_dt=datetime.now().strftime("%Y-%m-%d"),
                        )
                        self.db.dump_historical_data(scrip_name=scrip, historical_data=data)
                        return data 
                    return last_row
                elif from_dt^to_dt:
                    raise Exception("Both from_dt and to_dt should be provided")
                else:
                    rows= self.db.fetch_candles_from_db(scrip_name=scrip, start_datetime=from_dt,end_datetime=to_dt)
                    if rows==False:
                        data = self.broker.fetch_historical_data(
                            scrip_name=scrip,
                            time_interval="1m",
                            from_dt=from_dt,
                            to_dt=to_dt, 
                            # from_dt=datetime.now.strftime(),
                            # to_dt=datetime.now.strftime()
                        )
                        self.db.add_historical_data(data)
                        return data 
                    return rows 
            time.sleep(60)


    def fetch_candles_per_minute(self):
        """
        Fetches candle data for the given scrips with timeframe and returns the dataframe 
        """
        self.broker.fetch_candle_per_minute()
    
    