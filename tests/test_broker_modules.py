import pytest
import os
import numpy as np

import settings
from lib.modules import broker
from lib.modules.broker.template import Broker

available_brokers = Broker.__subclasses__()

@pytest.mark.parametrize("broker_instance", available_brokers)
def test_client_connection(broker_instance):
    """Test connection establishment with the broker, for two factor authentication process,
    Ensures the credentials are correct, and connection is succssfully established
    """
    obj = broker_instance()
    obj.check_connection()

@pytest.mark.parametrize("broker_instance", available_brokers)
def test_scrip_master_download(broker_instance):
    """Test downloading of scrip master file.
    """
    try:
        os.remove(settings.SCRIP_MASTER_FILE)
    except Exception:
        pass
    
    _ = broker_instance()
    if not os.path.exists(settings.SCRIP_MASTER_FILE):
        assert False

@pytest.mark.parametrize("broker_instance", available_brokers)
def test_order_placement(broker_instance):
    """Tests order placement by placing a dummy order.
    """
    obj = broker_instance()
    status, order_id = obj.place_order(
        order_type="BUY",
        scrip_name="SBIN",
        price = 1,
        quantity = 1,
        is_intraday = True
    )
    if status != False and order_id != -1:
        assert False

@pytest.mark.parametrize("broker_instance", available_brokers)
def test_historical_data_fetch(broker_instance):
    """Check if historical data is being fetched in the given format
    """
    obj = broker_instance()
    historical_data = obj.fetch_historical_data(
        scrip_name="SBIN",
        time_interval="1d",
        from_dt="2000-01-01",
        to_dt="2023-05-12"
    )
    checks = [
        historical_data['Datetime'].dtypes == object,
        historical_data['Open'].dtypes == np.float64,
        historical_data['High'].dtypes == np.float64,
        historical_data['Low'].dtypes == np.float64,
        historical_data['Close'].dtypes == np.float64,
        historical_data['Volume'].dtypes == np.int64,
    ]
    if False in checks:
        assert False