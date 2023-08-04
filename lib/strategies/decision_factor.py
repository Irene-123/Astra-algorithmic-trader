
# per trade 
'''
Once the decision_factor class is initialized in the backtester: run_logic per trade, the metrics below 
will be updated accordingly 


'''
class DecisionFactor():
    def __init__(self):
        self.human_decision=0 # -1: hold, 0: buy, 1: sell
        self.risk_factor=0 
        self.sell_dodged=0
        self.buy_dodged=0

    def sell_at_higher(self, if_sell, ongoing_trade, bought_price, current_price):
        if if_sell and ongoing_trade:
            if current_price > bought_price + bought_price*(1.10):
                return True
            else:
                self.sell_dodged+= 1 
                return False

        # TODO: check if the stock is rising or seen is higher than the lowest point in past 14 days 

    def risk_factor_estimate(self):
        # check the number of sell decisions dodged by human
        # similarly, for buy as well 
        pass 


    

        