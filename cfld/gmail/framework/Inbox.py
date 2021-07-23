import pdb
from framework.Logger import Logger

class Inbox(Logger):
    def __init__(self, service):
        super(Inbox, self).__init__(__class__)
        self.service = service
        self.thread_id_2_finalized_history_ids = {}
        self.blacklisted_thread_ids = set()

    def get_service(self):
        return self.service

    # Note that current implementation will only pick up preloaded 20 threads
    # when q == ''
    # when limit is left as default we will let the service use it's default value
    def query(self, q, limit=0, ignore_history_id=False):
        res = []
        for thread in self.service.query(q, limit):
            # If we've fully processed this thread, make sure its history id has been incremented before processing it again
            if (thread.id() in self.thread_id_2_finalized_history_ids \
                    and self.service.get_history_id(thread.id()) <= self.thread_id_2_finalized_history_ids[thread.id()] and not ignore_history_id) \
                    or \
                    thread.id() in self.blacklisted_thread_ids:# never return a blacklisted thread
                if thread.id() in self.thread_id_2_finalized_history_ids:
                    self.ld('service hid {} finalized hid {} thread: {}'.format(self.service.get_history_id(thread.id()), self.thread_id_2_finalized_history_ids[thread.id()], thread.id()))
                pass # current history is the same as the last time we finalized
            else:
                res.append(thread)
        return res


    # same as query but ignore the history id
    # TODO: this is expanding the external interface when in reality every redirect call
    # should be using this function on the Inbox
    def force_query(self, q, limit=0):
        return self.query(q, limit, ignore_history_id=True)
   
    def refresh(self):
        # We'll no longer return any old emails
        thread_id_2_history_ids = self.service.get_all_history_ids()
        for thread_id, history_id in thread_id_2_history_ids.items():
            self.thread_id_2_finalized_history_ids[thread_id] = int(history_id)
        # Call the service refresh second, because in the function it might re query
        # the state which will update the history ids with new values
        self.service.refresh()

    # Tell the inbox to never return this thread any more.
    def blacklist_id(self, thread_id):
        self.blacklisted_thread_ids.add(thread_id)

