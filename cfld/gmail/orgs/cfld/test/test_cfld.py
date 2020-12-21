from unittest.mock import MagicMock, Mock
import unittest
import os

import framework.globals

from orgs.cfld.util import signature, get_new_application_email, short_name_from_thread


class CfldTest(unittest.TestCase):
    
    '''def __init__(self, *args, **kwargs):
        super(CfldTest, self).__init__(*args, **kwargs)
        test_config = {}
        test_config['org'] = {}
        test_config['org']['name'] = 'cfld'
        test_config['org']['imports'] = ['from orgs.cfld.util import signature as imported_signature_implementation']
        globals.init(test_config)'''

    def test_signature(self):
        mock_thread = Mock()
        count = 0
        user = 'tyler'
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        mock_thread.get_user_name = MagicMock(return_value=user)
        self.assertEqual('Best,<br>Tyler Galdes<br>Clean Floors & Locking Doors Team<br>', signature(mock_thread))
        count = 1
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        self.assertEqual('Best,<br>Tyler<br>CF&LD Team<br>', signature(mock_thread))
        count = 2
        mock_thread.get_user_message_count = MagicMock(return_value=count)
        self.assertEqual('Best,<br>Tyler<br>', signature(mock_thread))

        mock_thread.get_user_name = MagicMock(return_value='wyatt')
        self.assertEqual('Best,<br>Wyatt<br>', signature(mock_thread))

    def test_new_application_email(self):
        target_email = 'tyler@asdf.com'
        mock_thread = Mock()
        mock_thread.last_message_text = MagicMock(return_value='some garbage etc etc etc <tr><th>Email:</th><td>{}<more formatting> some more text etc etc'.format(target_email))
        self.assertEqual(target_email, get_new_application_email(mock_thread))

        mock_thread.last_message_text = MagicMock(return_value='we can\'t find the delimiter in {} this string'.format(target_email))
        with self.assertRaises(Exception):
            get_new_application_email(mock_thread)

    def test_thread_short_name(self):
        mock_thread = Mock()

        mock_thread.labels = MagicMock(return_value=['Schools/USC', 'another label'])
        self.assertEqual('USC', short_name_from_thread(mock_thread))

        mock_thread.labels = MagicMock(return_value=['another label', 'Schools/USC'])
        self.assertEqual('USC', short_name_from_thread(mock_thread))

        mock_thread.labels = MagicMock(return_value=['another label', ' blah '])
        self.assertEqual('the campus', short_name_from_thread(mock_thread))





