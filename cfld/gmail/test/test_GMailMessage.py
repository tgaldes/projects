from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
import pdb

from services.gmail.GMailMessage import GMailMessage, extract_email, extract_emails

class GMailMessageTest(unittest.TestCase):

    def test_extract_emails(self):
        one = 'tgaldes@gmail.com'
        list_one = [one]
        two = '<tgaldes@gmail.com>'
        three = 'Tyler Galdes, <tgaldes@gmail.com>'
        four = 'Tyler Galdes <tgaldes@gmail.com>, Tyler Galdes <tyler@cf-ld.com>'
        #five = 'tgaldes@gmail.com, tyler@cf-ld.com'
        six = '"King, Kristin" <Kristin.King@nemoves.com>'

        self.assertEqual(list_one, extract_emails(one))
        self.assertEqual(list_one, extract_emails(two))
        self.assertEqual(list_one, extract_emails(three))
        self.assertEqual([one, 'tyler@cf-ld.com'], extract_emails(four))
        #self.assertEqual([one, 'tyler@cf-ld.com'], extract_emails(five))
        self.assertEqual(['Kristin.King@nemoves.com'], extract_emails(six))
