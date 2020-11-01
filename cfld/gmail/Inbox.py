from GMailService import GMailService
from Thread import Thread



class Inbox:
    def __init__(self, service):
        self.service = service

    def get_service(self):
        return self.service

    # return a list of all the threads that have involved a message to or from
    # this email address, ordered by most recent activity first
    # Right now the service get_one_thread isn't neccessarily retuning in order from the inbox
    def get_threads_from_email_address(self, email):
        return self.service.get_next_thread() # TODO
        pass
    
    # return the next thread to process or None if we have gone through all the threads
    # TODO: what logic are we using to determine what messages we'll read?
    # we should always have a 'processed' label, and we'll go through all threads from
    # most to least recent until we find one where the last message has a processed label
    def get_next_thread(self):
        raw_thread = self.service.get_next_thread()  # TODO
        if not raw_thread:
            return None
        return Thread(raw_thread, self.service)
        
