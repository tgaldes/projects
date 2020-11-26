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
    globals.init(sheet_service.get_lookup_info_data(), \
                 sheet_service.get_availability(), \
                 sheet_service.get_availability_blurbs())

    inboxes = {}
    if True:
        service = GMailService('tyler@cleanfloorslockingdoors.com')
        inbox_tyler = Inbox(service)
        inboxes['tyler'] = inbox_tyler
    if True:
        service_apply = GMailService('apply@cleanfloorslockingdoors.com')
        inbox_apply = Inbox(service_apply)
        inboxes['apply'] = inbox_apply
    factory = RuleFactory(sheet_service.get_rule_construction_data(), inboxes)

    count = 0
    for rule_group, user in factory.get_rule_groups():
        inbox = inboxes[user]
        for thread in inbox.get_all_threads():
            rule_group.process(thread)
            count += 1

            #pdb.set_trace()
    logger.li('Processed {} emails'.format(count))
    logger.li('Shutting down after successful run. Goodbye!')
    exit(0)

# We can have hardcoded actions available via command line such as:
# remove all drafts
# remove all of X label




