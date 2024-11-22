import pdb
import bdb
import sys
import json
from time import sleep
import traceback

from framework.Logger import Logger
from services.ServiceCreator import ServiceCreator
from framework.RuleHolder import RuleHolder
from framework.Thread import Thread
from framework.Inbox import Inbox
from framework.RuleFactory import RuleFactory
from framework.util import process_thread_try_catch
from framework.Config import Config


class Main:
    def __init__(self, mail_services, sheet_service, logger, config):
        self.logger = logger
        self.mail_services = mail_services
        self.sheet_service = sheet_service
        self.config = config

    def setup(self):
        self.inboxes = {}
        for service in self.mail_services:
            self.inboxes[service.get_user()] = Inbox(service)
        self.rule_factory = RuleFactory(
                self.sheet_service.get_rule_construction_data(), 
                self.inboxes, 
                llm_draft_data=self.sheet_service.get_llm_draft_info(), 
                llm_label_data=self.sheet_service.get_llm_label_info(), 
                action_data=self.sheet_service.get_action_info())
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
        return self.sheet_service.check_reload()



if __name__=='__main__':
    if len(sys.argv) < 2:
        print('No path specified for json config, exiting')
        exit(1)

    config = Config()
    config.initialize(sys.argv[1])

    sc = ServiceCreator()
    logger = Logger('root', config['log_path'], root=True)
    

    m = Main(sc.get_services(), sc.get_sheet_service(), logger, config)
    m.setup()
    # loops forever
    m.run()



