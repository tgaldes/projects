import pdb
from framework.Logger import Logger
from framework.util import process_thread_try_catch

class Inbox(Logger):
    def __init__(self, service):
        super(Inbox, self).__init__(__class__)
        self.service = service
        self.thread_id_2_finalized_history_ids = {}
        self.blacklisted_thread_ids = set()

        self.preprocess_groups = []
        self.postprocess_groups = []

        # before returning a thread from querying the first time in an iteration
        # we'll run the preprocess rules
        self.thread_id_2_threads_in_this_iteration = {}
    def set_pre_process_rule_groups(self, g):
        self.preprocess_groups = g
    def set_post_process_rule_groups(self, g):
        self.postprocess_groups = g

    # when limit is left as default we will let the service use it's default value
    def query(self, q, limit=0, ignore_history_id=False):
        res = []
        for thread in self.service.query(q, limit):
            # If we've fully processed this thread, make sure its history id has been incremented before processing it again
            if (thread.id() in self.thread_id_2_finalized_history_ids \
                    and thread.history_id() <= self.thread_id_2_finalized_history_ids[thread.id()] and not ignore_history_id) \
                    or \
                    thread.id() in self.blacklisted_thread_ids:# never return a blacklisted thread
                if thread.id() in self.thread_id_2_finalized_history_ids:
                    self.ld('not returning history id {} finalized hid {} thread: {}'.format(thread.history_id(), self.thread_id_2_finalized_history_ids[thread.id()], thread.id()))
                pass # current history is the same as the last time we finalized
            else:
                if thread.id() in self.thread_id_2_finalized_history_ids:
                    self.ld('returning hid {} finalized hid {} thread: {}'.format(thread.history_id(), self.thread_id_2_finalized_history_ids[thread.id()], thread.id()))
                # do we need to run preprocess rules?
                if thread.id() not in self.thread_id_2_threads_in_this_iteration:
                    self.thread_id_2_threads_in_this_iteration[thread.id()] = thread
                    self.__run_rules(self.preprocess_groups, thread, 'Preprocessing ')
                # we'll return the thread to whoever was querying
                res.append(thread)


        # if we haven't seen any of these threads before, run the preprocess rules on them
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
        # run the postprocess rules on all the ids we have returned since finalizing
        for thread_id, thread in self.thread_id_2_threads_in_this_iteration.items():
            self.__run_rules(self.postprocess_groups, thread, 'Postprocessing ')
        self.thread_id_2_threads_in_this_iteration.clear()
        # We'll no longer return any old emails
        thread_id_2_history_ids = self.service.get_all_history_ids()
        for thread_id, history_id in thread_id_2_history_ids.items():
            self.thread_id_2_finalized_history_ids[thread_id] = int(history_id)

    # Tell the inbox to never return this thread any more.
    def blacklist_id(self, thread_id):
        self.blacklisted_thread_ids.add(thread_id)

    def __run_rules(self, rule_groups, thread, log_msg):
        for rule in rule_groups:
            self.li('{} thread: {}'.format(log_msg, thread))
            process_thread_try_catch(thread, self, rule, self.logger)


