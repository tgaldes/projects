from unittest.mock import MagicMock, Mock
import unittest
import os
import globals

from orgs.cfld.util import signature as cfld_signature


class CfldTest(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(CfldTest, self).__init__(*args, **kwargs)
        test_config = {}
        test_config['org'] = {}
        test_config['org']['name'] = 'cfld'
        test_config['org']['imports'] = ['from orgs.cfld.util import signature as imported_signature_implementation']
        globals.init([], [], ['', '', ''], test_config)

    def test_signature(self):
        mock_thread = Mock()

        count = 0
        user = 'tyler'
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        mock_thread.get_user_name = MagicMock(return_value=user)
        from util import signature

        self.assertEqual(signature(mock_thread), cfld_signature(count, user))
        count = 1
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        self.assertEqual(signature(mock_thread), cfld_signature(count, user))
        count = 2
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        self.assertEqual(signature(mock_thread), cfld_signature(count, user))



