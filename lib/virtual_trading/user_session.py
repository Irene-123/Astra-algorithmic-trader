class UserSession:
    def __init__(self, session_id:int, total_balance:float, is_intraday_session:bool) -> None:
        self.session_id = session_id    # Unique session id for virtual trading
        self.total_balance = total_balance  # Total user balance
        self.is_intraday_session = is_intraday_session
        self.orders = []
    