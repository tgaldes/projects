import pdb
import sys


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
    #sheet_data = [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'body'], \
    #             ['label by school', 'apply', '', '', 'New submission for (.*)', '', '', 'label', '"Schools/" + match(0)', '', '', '']]
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
    inboxes = {}
    if False:
        service = GMailService('tyler@cleanfloorslockingdoors.com')
        inbox_tyler = Inbox(service)
        inboxes['tyler'] = inbox_tyler
    if True:
        service_apply = GMailService('apply@cleanfloorslockingdoors.com')
        inbox_apply = Inbox(service_apply)
        inboxes['apply'] = inbox_apply
    factory = RuleFactory(sheet_service.rule_construction_info(), inboxes)

    for user in inboxes:
        inbox = inboxes[user]
        while True:
            thread = inbox.get_next_thread()
            if not thread:
                break
            for rule in factory.get_rules_for_user(user):
                rule.process(thread)
            pdb.set_trace()

# We can have hardcoded actions available via command line such as:
# remove all drafts
# remove all of X label




