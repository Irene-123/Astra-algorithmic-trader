from abc import ABC, abstractmethod


class Broker(ABC):
    """Broker object template.
    """
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def login(self):
        """Creates a session with the broker
        """
        pass

    @abstractmethod
    def check_connection(self):
        """Check if the broker connection is live
        """
        pass

    @abstractmethod
    def fetch_scrip_master(self):
        """Fetches scrip master file.
        """
        pass

    @abstractmethod
    def place_order(self, order_type:str, scrip_code:int, quantity:int, is_intraday:bool=True, price:float=None):
        """Places order with the broker

        Args:
            order_type (str): BUY or SELL
            scrip_code (int): Unique scrip code of the stock
            price (float): Trading price, 0 for market order
            quantity (int): Quantity to trade
            is_intraday (bool): True for intraday order

        Returns:
            status (bool): order successfully placed or not
            order_id (int): unique order id, -1 for failure 
        """

    @abstractmethod
    def fetch_historical_data(self):
        """Fetches historical data of the scrip
        """
        pass