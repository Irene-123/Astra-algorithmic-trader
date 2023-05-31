import time
from datetime import datetime
import logging
from lib.modules.broker.five_paisa import FivePaisa
from lib.modules.database.database_manager import Manager as DbManager


class Manager:
    def __init__(self, scrip_names) -> None:
        self.scrip_names= scrip_names
        self.broker = FivePaisa(scrip_names)
        self.db = DbManager()

    def fetch_new_candle(self, timeframes: list):
        """
        Fetches new candle data for the given scrips with timeframe and returns the dataframe 
        """
        while True: 
            for scrip, timeframe in zip(self.scrip_names, timeframes):
                from_dt, to_dt= timeframe[0], timeframe[1]
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
                elif (from_dt==0 and to_dt!=0) or (from_dt!=0 and to_dt==0):
                    raise Exception("Both from_dt and to_dt should be provided")
                else:
                    rows= self.db.fetch_candles_from_db(scrip_name=scrip, start_datetime=from_dt,end_datetime=to_dt)
                    if len(rows)==0:
                        if len(rows)==0:
                            logging.warn(f"Could not fetch data for {scrip} in the database either because the table is empty or the daterange is invalid")
                            logging.warn(f"Fetching data from broker for {scrip}")
                        data = self.broker.fetch_historical_data(
                            scrip_name=scrip,
                            time_interval="1m",
                            from_dt=from_dt,
                            to_dt=to_dt, 
                            # from_dt=datetime.now.strftime(),
                            # to_dt=datetime.now.strftime()
                        )
                        self.db.dump_historical_data(scrip, data)
                        return data
                    return rows 


    def fetch_candles_per_minute(self):
        """
        Fetches candle data for the given scrips with timeframe and returns the dataframe 
        """
        self.broker.fetch_candle_per_minute()
    
    