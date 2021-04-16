from unittest.mock import MagicMock, Mock
import unittest
from framework.Inbox import Inbox


class InboxTest(unittest.TestCase):
    
    def test_query(self):
        mock_service = Mock()
        mock_threads = []
        history = {}
        second_history = {}
        for i in range(5):
            t = Mock()
            t.id = MagicMock(return_value=i)
            mock_threads.append(t)
            history[i] = 100
            second_history[i] = 111

        mock_service.query = MagicMock(return_value=mock_threads)
        mock_service.get_history_id = MagicMock(return_value=100)
        inbox = Inbox(mock_service)

        self.assertEqual(5, len(inbox.query('')))

        # Now we'll finalize the history ids of the mock threads
        mock_service.get_all_history_ids = MagicMock(return_value=history)
        mock_service.refresh = MagicMock()
        inbox.refresh()

        # Add in a new thread, it will be the only one returned
        t = Mock()
        t.id = MagicMock(return_value=6)
        history[6] = 100
        second_history[6] = 111
        mock_threads.append(t)
        self.assertEqual(1, len(inbox.query('')))

        # Now update the history id that the mock service returns for one of the threads, and we should get that thread and the new thread back

        mock_service.get_history_id.side_effect = [101, 100, 100, 100, 100, 100]
        self.assertEqual(2, len(inbox.query('')))

        mock_service.get_all_history_ids = MagicMock(return_value=second_history)
        mock_service.get_history_id = MagicMock(return_value=111)
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


