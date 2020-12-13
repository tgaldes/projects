from unittest.mock import MagicMock, Mock
import unittest
from framework.Inbox import Inbox


class InboxTest(unittest.TestCase):
    
    def test_get_threads_from_email_address(self):
        mock_service = Mock()
        email_one, email_two = 'one@a.com', 'two@a.com'
        mock_thread_one, mock_thread_two, mock_thread_three = Mock(), Mock(), Mock()
        mock_thread_one.default_reply = MagicMock(return_value=[email_one])
        mock_thread_two.default_reply = MagicMock(return_value=[email_two])
        mock_service.get_unread_threads = MagicMock(return_value=[])
        mock_service.get_all_threads = MagicMock(return_value=[mock_thread_one, mock_thread_two])

        i = Inbox(mock_service)

        email_one_matches = i.get_threads_from_email_address(email_one)
        self.assertEqual(1, len(email_one_matches))
        self.assertEqual(mock_thread_one, email_one_matches[0])

        email_two_matches = i.get_threads_from_email_address(email_two)
        self.assertEqual(1, len(email_two_matches))
        self.assertEqual(mock_thread_two, email_two_matches[0])

        # Now a test where we'll get back multiple threads

        email_three = email_one
        mock_thread_three.default_reply = MagicMock(return_value=[email_three])
        mock_service.get_all_threads = MagicMock(return_value=[mock_thread_one, mock_thread_two, mock_thread_three])
        i = Inbox(mock_service)
        email_multiple_matches = i.get_threads_from_email_address(email_one)
        self.assertEqual(2, len(email_multiple_matches))
        self.assertEqual(mock_thread_one, email_multiple_matches[0])
        self.assertEqual(mock_thread_three, email_multiple_matches[1])
