import pdb
from Logger import Logger


# ----------- GMail wrapper --------------------
# TESTING: can have this be a part of a global interface
# implented by test class or by GMail class
# TODO: move to thread class


# ----------- End GMail wrapper --------------------

from GMailService import GMailService
from Actions import *
from Matchers import *
from RuleHolder import RuleHolder
from Thread import Thread
from Inbox import Inbox
from RuleFactory import RuleFactory
if __name__=='__main__':
    sheet_data = [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'body'], \
                 ['label by school', 'apply', '', '', 'New submission for (.*)', '', '', 'label', '"Schools/" + match(0)', '', '', '']]
    logger = Logger()
    inboxes = {}
    if False:
        service = GMailService('tyler@cleanfloorslockingdoors.com')
        inbox_tyler = Inbox(service)
        inboxes['tyler'] = inbox_tyler
    if True:
        service_apply = GMailService('apply@cleanfloorslockingdoors.com')
        inbox_apply = Inbox(service_apply)
        inboxes['apply'] = inbox_apply
    factory = RuleFactory(sheet_data, inboxes)

    for user in inboxes:
        inbox = inboxes[user]
        while True:
            thread = inbox.get_next_thread()
            thread.get_new_application_email()
            if not thread:
                break
            for rule in factory.get_rules_for_user(user):
                rule.process(thread)





