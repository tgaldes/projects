import pdb

from GMailService import GMailService
from Logger import Logger



class Inbox(Logger):
    def __init__(self, service):
        super(Inbox, self).__init__(__name__)
        self.service = service

    def get_service(self):
        return self.service

    # return a list of all the threads that have involved a message to or from
    # this email address, ordered by most recent activity first
    # Right now the service get_one_thread isn't neccessarily retuning in order from the inbox
    def get_threads_from_email_address(self, email):
        res = []
        for thread in self.service.get_all_threads():
            replies = [x.lower() for x in thread.default_reply()]
            if email.lower() in replies:
                res.append(thread)
        return res
    
    '''def get_unread_threads(self):
        return self.service.get_unread_threads()'''

    def get_all_threads(self):
        return self.service.get_all_threads()
        
