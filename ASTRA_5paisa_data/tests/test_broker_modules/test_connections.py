from lib.modules.live_data_fetch.API_client import API

def test_client_connection():
    """Test connection establishment with the broker, for two factor authentication process,
    Ensures the credentials are correct, and connection is succssfully established
    """
    obj = API()
    if obj.client.client_code == "INVALID CODE":
        raise Exception("Login Unsuccessful, Invalid credentials")
    elif obj.client.client_code == "":
        raise Exception("Login not attempted")