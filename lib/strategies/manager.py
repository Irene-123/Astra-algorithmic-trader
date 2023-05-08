import os
import importlib
from .template import Strategy


class Strat:
    def __init__(self, instance, name) -> None:
        self.name = name
        self.class_instance = instance
        self.is_strategy_active = False
        
        self.successful_executions = 0
        self.unsuccessful_executions = 0
        self.total_profit = 0
        self.total_loss = 0
        self.profit_per_execution = 0
        self.loss_per_execution = 0


class Manager:
    def __init__(self) -> None:
        self.strategies = list()    # List of [Strat]

    def load_strategies(self):
        for file_name in os.listdir(os.path.dirname(__file__)):
            if file_name.endswith(".py") and file_name not in ["__init__.py", "manager.py", "template.py"]:
                module_name = file_name[:-3]
                module = importlib.import_module("." + module_name, package="modules.players")
                for class_name in dir(module):
                    if isinstance(getattr(module, class_name), type):
                        globals()[class_name] = getattr(module, class_name)

        print(Strategy.__subclasses__)
            