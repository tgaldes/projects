import pdb
import sys
import json

import globals
from Logger import Logger
from GMailService import GMailService
from Actions import *
from Matchers import *
from RuleHolder import RuleHolder
from Thread import Thread
from Inbox import Inbox
from RuleFactory import RuleFactory
from SheetService import SheetService


class Main:
    def __init__(self, mail_services, sheet_service, logger, org_name):
        globals.init(sheet_service.get_lookup_info_data(), \
                     sheet_service.get_availability(), \
                     sheet_service.get_availability_blurbs(),
                     org_name)
        self.inboxes = {}
        for service in mail_services:
            self.inboxes[service.get_user()] = Inbox(service)

        self.rule_factory = RuleFactory(sheet_service.get_rule_construction_data(), self.inboxes)
        self.logger = logger

    def run(self):
        count = 0
        for rule_group, user in self.rule_factory.get_rule_groups():
            inbox = self.inboxes[user]
            for thread in inbox.get_all_threads():
                rule_group.process(thread)
                count += 1
        self.logger.li('Processed an email {} times'.format(count))
        
        
if __name__=='__main__':
    logger = Logger('main')
    if len(sys.argv) < 2:
        logger.li('No path specified for json config, exiting')
        exit(1)
    fn = sys.argv[1]
    with open(fn, 'r') as f:
        config = json.load(f)
    

    if config['type'] == 'gmail':
        sheet_service = SheetService(config['sheet_service_email', config['sheet_name'], config['spreadsheet_id'], config['secret_path'], config['client_token_dir'])
        services = []
        for email in config['emails']:
            services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir']))
    else:
        logger.lf('Only gmail type supported, exiting')
        exit(1)
    m = Main(services, sheet_service, logger, config)
    m.run()

    logger.li('Shutting down after successful run. Goodbye!')
    exit(0)

# We can have hardcoded actions available via command line such as:
# remove all drafts
# remove all of X label




