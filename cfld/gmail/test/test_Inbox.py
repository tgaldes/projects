from unittest.mock import MagicMock, Mock
import unittest
from framework.Inbox import Inbox
import pdb


class InboxTest(unittest.TestCase):
    
    def test_query(self):
        mock_service = Mock()
        mock_threads = []
        history = {}
        second_history = {}
        for i in range(5):
            t = Mock()
            t.id = MagicMock(return_value=i)
            t.history_id = MagicMock(return_value=100)
            mock_threads.append(t)
            history[i] = 100
            second_history[i] = 111

        mock_service.query = MagicMock(return_value=mock_threads)
        inbox = Inbox(mock_service)

        self.assertEqual(5, len(inbox.query('')))

        # Now we'll finalize the history ids of the mock threads
        mock_service.get_all_history_ids = MagicMock(return_value=history)
        mock_service.refresh = MagicMock()
        inbox.finalize()
        inbox.refresh()

        # Add in a new thread, it will be the only one returned
        t = Mock()
        t.id = MagicMock(return_value=6)
        t.history_id = MagicMock(return_value=100)
        history[6] = 100
        second_history[6] = 111
        mock_threads.append(t)
        self.assertEqual(1, len(inbox.query('')))

        # Now update the history id that the mock service returns for one of the threads, and we should get that thread and the new thread back

        mock_threads[0].history_id = MagicMock(return_value=111)
        self.assertEqual(2, len(inbox.query('')))

        mock_service.get_all_history_ids = MagicMock(return_value=second_history)
        inbox.finalize()
        inbox.refresh()
        self.assertEqual(0, len(inbox.query('')))
        
    def test_blacklist_id(self):
        mock_service = Mock()
        mock_threads = []
        history = {}
        for i in range(5):
            t = Mock()
            t.id = MagicMock(return_value=i)
            mock_threads.append(t)
            history[i] = 100


        mock_service.query = MagicMock(return_value=mock_threads)
        mock_service.get_history_id = MagicMock(return_value=100)
        inbox = Inbox(mock_service)

        for i in range(5):
            inbox.blacklist_id(i)
            self.assertEqual(4 - i, len(inbox.query('')))

    def test_pre_and_post_process(self):
        # give the inbox two pre process and two post process groups
        # we sdlkfwon't do anything with the history ids
        # pre will get called when the thread is first returned after construction or after a call to finalize resets the state of the inbox
        # post gets called during finalize

        def create_mock_rule_group():
            m = Mock()
            m.process = MagicMock()
            return m
        pre_groups = [create_mock_rule_group() for x in range(2)]
        post_groups = [create_mock_rule_group() for x in range(2)]
        mock_service = Mock()
        mock_threads = []
        history = {}
        for i in range(2):
            t = Mock()
            t.id = MagicMock(return_value=i)
            mock_threads.append(t)
            history[i] = 99
            t.history_id = MagicMock(return_value=100)
        mock_service.get_all_history_ids = MagicMock(return_value=history)
        mock_service.query = MagicMock(return_value=mock_threads)
        mock_service.get_history_id = MagicMock(return_value=99)
        inbox = Inbox(mock_service)
        inbox.set_pre_process_rule_groups(pre_groups)
        inbox.set_post_process_rule_groups(post_groups)

        # first query will run both pre groups on both threads and then not again
        for i in range(2):
            inbox.query('')
            for g in pre_groups:
                self.assertEqual(2, g.process.call_count)
            for g in post_groups:
                self.assertEqual(0, g.process.call_count)
        # now finalize and run post
        inbox.finalize()
        for g in pre_groups:
            self.assertEqual(2, g.process.call_count)
        for g in post_groups:
            self.assertEqual(2, g.process.call_count)
        # now we can run pre rules on the threads again
        for i in range(2):
            inbox.query('')
            for g in pre_groups:
                self.assertEqual(4, g.process.call_count)
            for g in post_groups:
                self.assertEqual(2, g.process.call_count)
        # now finalize and run post
        inbox.finalize()
        for g in pre_groups:
            self.assertEqual(4, g.process.call_count)
        for g in post_groups:
            self.assertEqual(4, g.process.call_count)

if __name__=='__main__':
    unittest.main()


