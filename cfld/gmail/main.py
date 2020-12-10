import pdb
import sys


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
        logger.li('No mode specified, defaulting to using test rules.')
        mode = 'test'
    else:
        mode = sys.argv[1]
    supported_modes = ['test', 'prod']
    if mode not in supported_modes:
        logger.lf('{} is not in supported modes: {}, exiting'.format(mode, supported_modes))
        exit(1)
        
    sheet_service = SheetService('tyler@cleanfloorslockingdoors.com', mode)
    services = []
    services.append(GMailService('tyler@cleanfloorslockingdoors.com'))
    services.append(GMailService('apply@cleanfloorslockingdoors.com'))
    m = Main(services, sheet_service, logger, 'cfld')
    m.run()

    logger.li('Shutting down after successful run. Goodbye!')
    exit(0)

# We can have hardcoded actions available via command line such as:
# remove all drafts
# remove all of X label




