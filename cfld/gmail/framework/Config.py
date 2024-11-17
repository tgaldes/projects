import json

def wrap_in_quotes(string):
    return '"' + string + '"'

class Config(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False

    def initialize(self, config_file):
        # reads the json config file and keeps a dictionariy of the values
        self.config = {}
        with open(config_file, "r") as f:
            self.config = json.load(f)
        self.initialized = True

    # overload the [] operator to access the config values
    def __getitem__(self, key):
        if not self.initialized:
            raise Exception("Config not initialized")
        return self.config[key]

    def __contains__(self, key):
        if not self.initialized:
            raise Exception("Config not initialized")
        return key in self.config

    def get_automation_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'automation_label' in self.config:
            return wrap_in_quotes(self.config['automation_label'])
        return wrap_in_quotes('automation')
    
    def get_force_skip_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'force_skip_label' in self.config:
            return wrap_in_quotes(self.config['force_skip_label'])
        return wrap_in_quotes(self.get_automation_label() + '/force_skip')
    def get_thread_error_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'thread_error_label' in self.config:
            return wrap_in_quotes(self.config['thread_error_label'])
        return wrap_in_quotes(self.get_automation_label() + '/errors')

