import os
import importlib

for file_name in os.listdir(os.path.dirname(__file__)):
    if file_name.endswith(".py") and file_name not in ["template.py", "__init__.py", "manager.py"]:
        module_name = file_name[:-3]
        module = importlib.import_module("." + module_name, package="lib.modules.broker")
        for class_name in dir(module):
            if isinstance(getattr(module, class_name), type):
                globals()[class_name] = getattr(module, class_name)
