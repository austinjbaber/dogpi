import json
import os

class Config:
    '''
    A singleton Config object that can be used across the app. Values are loaded from the config.json file.

    Usage: 
        config = Config()
        some_var = config.key
    '''
    
    _instance = None # Class level variable
    path = "config.json"

    # Override __new__ to control when an object is created.
    # We only ever want one instance because it's supposed to be a singleton.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"The file '{self.path}' does not exist in the current directory. Current directory: {os.path.curdir}")
        
        with open(self.path, "r") as f:
            self._data = json.load(f)

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"There is no configuration key named {name}")