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
                    self.ld('not returning history id {} finalized hid {} thread: {}'.format(self.service.get_history_id(thread.id()), self.thread_id_2_finalized_history_ids[thread.id()], thread.id()))
                pass # current history is the same as the last time we finalized
            else:
                if thread.id() in self.thread_id_2_finalized_history_ids:
                    self.ld('returning hid {} finalized hid {} thread: {}'.format(self.service.get_history_id(thread.id()), self.thread_id_2_finalized_history_ids[thread.id()], thread.id()))
                res.append(thread)
        return res


    # same as query but ignore the history id
    # TODO: this is expanding the external interface when in reality every redirect call
    # should be using this function on the Inbox
    def force_query(self, q, limit=0):
        return self.query(q, limit, ignore_history_id=True)
   
    # split refresh and finalize. call refresh before the loop, finalize after
    # service will hide thread ids that were reinitialized mid run from the return of get_all_history_ids, like the first way I implemented it but instead of if the thread is in memory at the start of the run it's if the thread has been reinit during the run
    def refresh(self):
        self.service.refresh()

    def finalize(self):
        # We'll no longer return any old emails
        thread_id_2_history_ids = self.service.get_all_history_ids()
        for thread_id, history_id in thread_id_2_history_ids.items():
            self.thread_id_2_finalized_history_ids[thread_id] = int(history_id)

    # Tell the inbox to never return this thread any more.
    def blacklist_id(self, thread_id):
        self.blacklisted_thread_ids.add(thread_id)

