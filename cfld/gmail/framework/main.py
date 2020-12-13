import pdb
import sys
import json

import framework.globals
from framework.Logger import Logger
from services.gmail.GMailService import GMailService
from framework.RuleHolder import RuleHolder
from framework.Thread import Thread
from framework.Inbox import Inbox
from framework.RuleFactory import RuleFactory
from services.gmail.SheetService import SheetService


class Main:
    def __init__(self, mail_services, logger, config):
        framework.globals.init(config)
        self.inboxes = {}
        for service in mail_services:
            self.inboxes[service.get_user()] = Inbox(service)

        self.rule_factory = RuleFactory(framework.globals.g_org.get_rule_construction_data(), self.inboxes)
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
        services = []
        for email in config['emails']:
            services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir']))
    else:
        logger.lf('Only gmail type supported, exiting')
        exit(1)
    m = Main(services, logger, config)
    m.run()

    logger.li('Shutting down after successful run. Goodbye!')
    exit(0)

# We can have hardcoded actions available via command line such as:
# remove all drafts
# remove all of X label




