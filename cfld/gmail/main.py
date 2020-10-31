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
if __name__=='__main__':
    logger = Logger()
    service = GMailService('tyler@cleanfloorslockingdoors.com')
    service_apply = GMailService('apply@cleanfloorslockingdoors.com')
    inbox_apply = Inbox(service_apply)
    holders = []
    #holders.append(RuleHolder(LabelAction('"Signed leases/USC"'), SubjectMatcher('test subject')))
    #holders.append(RuleHolder(DraftAction(), SubjectMatcher('test subject')))

    thread = Thread(service.get_one_thread(), service)
    holders.append(RuleHolder(RedirectAction(inbox_apply), SubjectMatcher('.*')))

    for holder in holders:
        holder.process(thread)
    #for holder in holders:
        #holder.process(thread)










