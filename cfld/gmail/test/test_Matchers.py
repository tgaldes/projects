from unittest.mock import MagicMock, Mock
import unittest
from Matchers import SubjectMatcher
from Thread import Thread

class SubjectMatcherTest(unittest.TestCase):
    def test_no_match(self):
        sm = SubjectMatcher('test subject')
        thread = Thread({}, None)
        thread.subject = MagicMock(return_value='')
        self.assertFalse(sm.matches(thread))

    def test_match(self):
        sm = SubjectMatcher('test subject')
        thread = Thread({}, None)
        thread.subject = MagicMock(return_value='test subject')
        self.assertTrue(sm.matches(thread))
