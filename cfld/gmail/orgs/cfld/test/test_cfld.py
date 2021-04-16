from unittest.mock import MagicMock, Mock
import unittest
import os

import framework.globals

from orgs.cfld.util import signature, get_new_application_email, short_name_from_thread, get_new_application_name, get_approved_application_name, get_lease_sent_out_email, get_signed_lease_email


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

    def test_new_application_name(self):
        target_name = 'tyler galdes'
        target_list = target_name.split()
        mock_thread = Mock()
        mock_thread.last_message_text = MagicMock(return_value='some garbage etc etc etc <tr><th>Applicant:</th><td>{}<more formatting> some more text etc etc'.format(target_name))
        self.assertEqual(target_name, get_new_application_name(mock_thread))
        self.assertEqual(target_list, get_new_application_name(mock_thread, return_as_list=True))

        mock_thread.last_message_text = MagicMock(return_value='we can\'t find the delimiter in {} this string'.format(target_name))
        with self.assertRaises(Exception):
            get_new_application_name(mock_thread)

    def test_approved_application_name(self):
        target_name = 'tyler galdes'
        target_list = target_name.split()
        mock_thread = Mock()
        mock_thread.last_message_text = MagicMock(return_value='some garbage etc etc etc <tr><th>Applicant name:</th><td>{}<more formatting> some more text etc etc'.format(target_name))
        self.assertEqual(target_name, get_approved_application_name(mock_thread))
        self.assertEqual(target_list, get_approved_application_name(mock_thread, return_as_list=True))

        mock_thread.last_message_text = MagicMock(return_value='we can\'t find the delimiter in {} this string'.format(target_name))
        with self.assertRaises(Exception):
            get_approved_application_name(mock_thread)

    def test_thread_short_name(self):
        mock_thread = Mock()

        mock_thread.labels = MagicMock(return_value=['Schools/USC', 'another label'])
        self.assertEqual('USC', short_name_from_thread(mock_thread))

        mock_thread.labels = MagicMock(return_value=['another label', 'Schools/USC'])
        self.assertEqual('USC', short_name_from_thread(mock_thread))

        mock_thread.labels = MagicMock(return_value=['another label', ' blah '])
        self.assertEqual('the campus', short_name_from_thread(mock_thread))

    def test_get_lease_sent_out_email(self):

        self.assertEqual('ivan.gonzalez@cimat.mx', get_lease_sent_out_email('j.stan.hill@gmail.com and ivan.gonzalez@cimat.mx', 'mharrel@jhtech.com,j.stan.hill@gmail.com'))
        self.assertEqual('ivan.gonzalez@cimat.mx', get_lease_sent_out_email('ivan.gonzalez@cimat.mx', 'mharrel@jhtech.com,j.stan.hill@gmail.com'))
        with self.assertRaises(Exception):
            get_lease_sent_out_email('ivan.gonzalez@cimat.mx and another@email.com', 'mharrel@jhtech.com,j.stan.hill@gmail.com')
        with self.assertRaises(Exception):
            get_lease_sent_out_email('no emails found.here', 'mharrel@jhtech.com,j.stan.hill@gmail.com')

    def test_get_signed_lease_email(self):
        mock_thread = Mock()

        mock_thread.default_reply = MagicMock(return_value=['adobe@echosign.com', 'tyler@cleanfloorslockingdoors.com', 'asdf@one.com'])
        self.assertEqual('asdf@one.com', get_signed_lease_email(mock_thread))

        mock_thread.default_reply = MagicMock(return_value=['adobe@echosign.com', 'asdf@one.com', 'tyler@cleanfloorslockingdoors.com'])
        self.assertEqual('asdf@one.com', get_signed_lease_email(mock_thread))
        

