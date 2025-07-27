from framework.Config import Config
from services.gmail.GMailService import GMailService
from services.gmail.SheetService import SheetService
import logging

class ServiceCreator():
    def __init__(self):
        config = Config() # get singleton

        self.services = []
        self.sheet_service = None
        if config['type'] == 'gmail':
            logging.getLogger('google').setLevel(logging.ERROR)
            logging.getLogger('googleapiclient').setLevel(logging.ERROR)
            self.sheet_service = SheetService(config['sheet_service_email'], config['spreadsheet_id'], config['secret_path'], config['client_token_dir'])

            config.update(self.sheet_service.config_data)
            self.sheet_service.set_rule_sheet_name(config['rule_sheet_name'])

            for email in config['emails']:
                if 'default_query_limit' in config and 'default_query_string' in config:
                    self.services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir'], config['default_query_limit'], config['default_query_string']))
                else:
                    self.services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir']))
        else:
            logger.lf('Only gmail type supported, exiting')
            exit(1)

    def get_services(self):
        return self.services
    
    def get_sheet_service(self):
        return self.sheet_service
