import pdb
import bdb
import sys
import json
from time import sleep
import traceback

import framework.globals
from framework.Logger import Logger
from services.gmail.GMailService import GMailService
from framework.RuleHolder import RuleHolder
from framework.Thread import Thread
from framework.Inbox import Inbox
from framework.RuleFactory import RuleFactory
from framework.BaseValidator import BaseValidator
from services.gmail.SheetService import SheetService
from framework import constants
import logging
import logging_tree
from framework.util import process_thread_try_catch


class Main:
    def __init__(self, mail_services, logger, config):
        self.logger = logger
        framework.globals.init(config, self.logger)
        self.mail_services = mail_services
        self.config = config

    def validate_rules(self):
        BaseValidator.set_validate_mode(True)
        for rule_group in self.rule_factory.get_rule_groups():
            user = rule_group.get_user()
            inbox = self.inboxes[user]
            for thread in inbox.query('label:automation/dev_test_case/validate'):
                self.logger.li('Processing user {} thread {} in validate mode'.format(thread, user))
                rule_group.process(thread)
        BaseValidator.set_validate_mode(False)

    def setup(self):
        self.inboxes = {}
        for service in self.mail_services:
            self.inboxes[service.get_user()] = Inbox(service)
        self.rule_factory = RuleFactory(framework.globals.g_org.get_rule_construction_data(), self.inboxes, framework.globals.g_org.get_llm_info(), framework.globals.g_org.get_action_info())
        for user, inbox in self.inboxes.items():
            inbox.set_pre_process_rule_groups(self.rule_factory.get_pre_process_rule_groups(user))
            inbox.set_post_process_rule_groups(self.rule_factory.get_post_process_rule_groups(user))

    def refresh(self):
        for inbox in self.inboxes:
            self.inboxes[inbox].refresh()
    def finalize(self):
        for inbox in self.inboxes:
            self.inboxes[inbox].finalize()

    def run_one(self):
        try:

            self.logger.li('Refreshing inboxes and default queries for upcoming loop.')
            self.refresh()

            for rule_group in self.rule_factory.get_rule_groups():
                user = rule_group.get_user()
                inbox = self.inboxes[user]
                threads = inbox.query(rule_group.get_query())
                self.logger.li('Query: "{}" returned {} threads for user {}'.format(rule_group.get_query(), len(threads), user))
                for thread in threads:
                    self.logger.li('Processing user {} thread {}'.format(user, thread))
                    process_thread_try_catch(thread, inbox, rule_group, self.logger)
            # will tell Inbox to not process Threads a second time

            self.finalize()

            return
        except bdb.BdbQuit as e:
            exit(0)
        except Exception as e:
            self.logger.lw('Caught exception in main. Stack: {}'.format(traceback.format_exc()))
        self.logger.li('Attempting to refresh again before continuing.')
        for i in range(10):
            try:
                self.refresh()
                return
            except bdb.BdbQuit as e:
                exit(0)
            except Exception as e:
                self.logger.lw('Caught exception while trying to refresh. Stack: {}'.format(traceback.format_exc()))
        self.refresh() # at this point just let the exception refresh is creating kill the program

    def run(self):
        if 'validate' in self.config and self.config['validate']:
            self.validate_rules()
        loop_count = 0
        
        while True:
            self.run_one()
            loop_count += 1
            self.logger.li('Finished iteration {} in main'.format(loop_count))
            sleep(60)

            # check if we need to reload everything
            if self.check_reload():
                self.logger.li('Reloading everything')
                self.setup()

    def check_reload(self):
        return framework.globals.g_org.check_reload()



if __name__=='__main__':
    if len(sys.argv) < 2:
        print('No path specified for json config, exiting')
        exit(1)
    fn = sys.argv[1]
    with open(fn, 'r') as f:
        config = json.load(f)
    logger = Logger('root', config['log_path'], root=True)
    #logging_tree.printout()
    

    if config['type'] == 'gmail':
        logging.getLogger('google').setLevel(logging.ERROR)
        logging.getLogger('googleapiclient').setLevel(logging.ERROR)
        services = []
        for email in config['emails']:
            if 'default_query_limit' and 'default_query_string' in config:
                services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir'], config['default_query_limit'], config['default_query_string']))
            else:
                services.append(GMailService(email, config['domains'], config['secret_path'], config['client_token_dir']))
    else:
        logger.lf('Only gmail type supported, exiting')
        exit(1)
    m = Main(services, logger, config)
    m.setup()
    m.run()

    logger.li('Shutting down after successful run. Goodbye!')


