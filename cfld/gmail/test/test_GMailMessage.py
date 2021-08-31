from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
import pdb

from services.gmail.GMailMessage import GMailMessage, extract_email, extract_emails
from test.TestUtil import get_thread_constructor_args

def create_messages(fn):
    id, messages = get_thread_constructor_args(fn)
    return messages

class GMailMessageTest(unittest.TestCase):
    
    def test_extract_emails(self):
        one = 'tgaldes@gmail.com'
        list_one = [one]
        two = '<tgaldes@gmail.com>'
        three = 'Tyler Galdes, <tgaldes@gmail.com>'
        four = 'Tyler Galdes <tgaldes@gmail.com>, Tyler Galdes <tyler@cf-ld.com>'
        five = 'tgaldes@gmail.com, tyler@cf-ld.com'
        six = '"King, Kristin" <Kristin.King@nemoves.com>'
        seven = 'Stan Hill <j.stan.hill@gmail.com>, Kenneth Akers <akers.kenneth66@gmail.com>, ivan.gonzalez@cimat.mx'
        eight = '<one@o>,<two@o>'


        self.assertEqual(list_one, extract_emails(one))
        self.assertEqual(list_one, extract_emails(two))
        self.assertEqual(list_one, extract_emails(three))
        self.assertEqual([one, 'tyler@cf-ld.com'], extract_emails(four))
        self.assertEqual([one, 'tyler@cf-ld.com'], extract_emails(five))
        self.assertEqual(['Kristin.King@nemoves.com'], extract_emails(six))
        self.assertEqual(['j.stan.hill@gmail.com', 'akers.kenneth66@gmail.com', 'ivan.gonzalez@cimat.mx'], extract_emails(seven))
        self.assertEqual(['one@o', 'two@o'], extract_emails(eight))


    def test_delimiter(self):
        m = create_messages('gmail_message_inputs/test_delimiter_1.txt')
        self.assertEqual(13, len(m))
        self.assertEqual(' Thank you', m[-5].content())
