import pdb


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
if __name__=='__main__':
    service = GMailService('tyler@cleanfloorslockingdoors.com')
    #service_apply = GMailService('apply@cleanfloorslockingdoors.com')
    holders = []
    holders.append(RuleHolder(LabelAction('"Signed leases/USC"'), SubjectMatcher('test subject')))
    holders.append(RuleHolder(DraftAction(), SubjectMatcher('test subject')))

    thread = Thread(service.get_one_thread(), service)

    for holder in holders:
        holder.process(thread)
    #for holder in holders:
        #holder.process(thread)










