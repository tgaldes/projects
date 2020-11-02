from unittest.mock import MagicMock, Mock
import unittest
from Matchers import SubjectMatcher, ExpressionMatcher
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

class ExpressionMatcherTest(unittest.TestCase):

    def test_no_match(self):
        thread = Thread({}, None)

        em = ExpressionMatcher('False')
        self.assertFalse(em.matches(thread))

        em = ExpressionMatcher('True')
        self.assertTrue(em.matches(thread))

        em = ExpressionMatcher('True == False')
        self.assertFalse(em.matches(thread))
        
        em = ExpressionMatcher('False == False')
        self.assertTrue(em.matches(thread))

        em = ExpressionMatcher('1 in [3, 4, 5]')
        self.assertFalse(em.matches(thread))

        em = ExpressionMatcher('int(thread.last_ts()) > 1000')
        thread.last_ts = MagicMock(return_value='1001')
        self.assertTrue(em.matches(thread))
        thread.last_ts = MagicMock(return_value='1000')
        self.assertFalse(em.matches(thread))
