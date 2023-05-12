import os
import importlib
from .template import Strategy
from .towards_sma import TowardsSMA
sma_obj= TowardsSMA() 

class Strat:
    def __init__(self, instance, name) -> None:
        self.name = name    # Name of the strategy
        self.class_instance = instance  # Class instance for the strategy
        self.is_strategy_active = False # Is strategy running
        
        self.will_provide_exit = False  # Is exit singnal sent by strategy or by target

        self.successful_executions = 0  # Successful trades executed by the strategy
        self.unsuccessful_executions = 0    # Unsuccessful trades executed by the strategy
        self.total_profit = 0   # Total profit made by successful trades
        self.total_loss = 0 # Total loss made by unsuccessful trades
        self.profit_per_execution = 0   # Profit per successful trade (in percent)
        self.loss_per_execution = 0 # Loss per successful trade (in percent)
        self.transactions=0 # total num of transactions/day 
    
class Manager:
    def __init__(self) -> None:
        self.strategies = list()    # List of [Strat]

    def load_strategies(self):
        for file_name in os.listdir(os.path.dirname(__file__)):
            if file_name.endswith(".py") and file_name not in ["__init__.py", "manager.py", "template.py"]:
                module_name = file_name[:-3]
                module = importlib.import_module("." + module_name, package="lib.strategies")
                for class_name in dir(module):
                    if isinstance(getattr(module, class_name), type):
                        globals()[class_name] = getattr(module, class_name)

        print(Strategy.__subclasses__())
        
    def place_order(self, order_values): 
        strat_obj= Strat() 
        # Strategy to be used, which will return the buy or sell signal 
        signal = sma_obj.run_strategy(order_values) 
        if signal=='BUY' or signal=='SELL': 
            strat_obj.transactions+= 1 
        
            

            