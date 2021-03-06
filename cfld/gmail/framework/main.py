import pdb
import sys
import json
from time import sleep

import framework.globals
from framework.Logger import Logger
from services.gmail.GMailService import GMailService
from framework.RuleHolder import RuleHolder
from framework.Thread import Thread
from framework.Inbox import Inbox
from framework.RuleFactory import RuleFactory
from framework.BaseValidator import BaseValidator
from services.gmail.SheetService import SheetService


class Main:
    def __init__(self, mail_services, logger, config):
        self.logger = logger
        framework.globals.init(config, self.logger)
        self.mail_services = mail_services
        self.config = config

    def validate_rules(self):
        BaseValidator.set_validate_mode(True)
        for rule_group, user in self.rule_factory.get_rule_groups():
            inbox = self.inboxes[user]
            for thread in inbox.query('label:automation/dev_test_case/validate'):
                self.logger.li('Processing user {} thread {} in validate mode'.format(thread, user))
                rule_group.process(thread)
        BaseValidator.set_validate_mode(False)

    def setup(self):
        self.inboxes = {}
        for service in self.mail_services:
            self.inboxes[service.get_user()] = Inbox(service)
        self.rule_factory = RuleFactory(framework.globals.g_org.get_rule_construction_data(), self.inboxes)

    def run_one(self):
        for rule_group, user in self.rule_factory.get_rule_groups():
            inbox = self.inboxes[user]
            threads = inbox.query(rule_group.get_query())
            for thread in threads:
                self.logger.li('Processing user {} thread {}'.format(user, thread))
                rule_group.process(thread)

    def run(self):
        if 'validate' in self.config and self.config['validate']:
            self.validate_rules()
        loop_count = 0
        while True:
            self.run_one()
            loop_count += 1
            self.logger.li('Finished iteration {} in main'.format(loop_count))

            self.logger.li('Refreshing inboxes and default queries for next loop.')
            for inbox in self.inboxes:
                self.inboxes[inbox].refresh()

            sleep(60)

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
    m.setup()
    m.run()

    logger.li('Shutting down after successful run. Goodbye!')


