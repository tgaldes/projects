import json

class Config(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False

    def initialize(self, config_file, d={}):
        # reads the json config file and keeps a dictionariy of the values
        self.config = {}

        if d:
            self.config = d
        else:
            with open(config_file, "r") as f:
                self.config = json.load(f)
        self.initialized = True

    # overload the [] operator to access the config values
    def __getitem__(self, key):
        if not self.initialized:
            raise Exception("Config not initialized")
        return self.config[key]

    def update(self, d):
        for k, v in d.items():
            self.config[k] = v

    def __setitem__(self, key, value):
        if not self.initialized:
            raise Exception("Config not initialized")
        self.config[key] = value

    def __contains__(self, key):
        if not self.initialized:
            raise Exception("Config not initialized")
        return key in self.config

    def get_automation_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'automation_label' in self.config:
            return self.config['automation_label']
        return 'automation'

    def get_force_skip_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'force_skip_label' in self.config:
            return self.config['force_skip_label']
        return self.get_automation_label() + '/force_skip'

    def get_thread_error_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'thread_error_label' in self.config:
            return self.config['thread_error_label']
        return self.get_automation_label() + '/errors'

    def get_browser_use_failed_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'thread_error_label' in self.config:
            return self.config['thread_error_label']
        return self.get_automation_label() + '/browser_use_failed'
    
    def set_found_text(self, text):
        if not self.initialized:
            raise Exception("Config not initialized")
        self.config['found_text'] = text

    def get_found_text(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'found_text' in self.config:
            return self.config['found_text']
        else:
            raise Exception("found_text not set in config")

    def get_automation_training_data_label(self):
        if not self.initialized:
            raise Exception("Config not initialized")
        elif 'automation_training_data_label' in self.config:
            return self.config['automation_training_data_label']
        return self.get_automation_label() + '/training_data/'
