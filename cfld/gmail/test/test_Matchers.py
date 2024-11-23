from unittest.mock import MagicMock, Mock
import unittest
import os
from framework.Matchers import *


class SubjectMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            sm = SubjectMatcher('')
        with self.assertRaises(Exception):
            sm = SubjectMatcher(' ')

    def test_no_match(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='')
        self.assertFalse(sm.matches(thread))

    def test_match(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='test subject')
        self.assertTrue(sm.matches(thread))

    def test_raise_on_no_matching_groups(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='no match')

    def test_force_whole_match(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='test subjectone')
        self.assertFalse(sm.matches(thread))
        

class LabelMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            lm = LabelMatcher('')

    def test_match(self):
        lm = LabelMatcher('automation')
        thread = Mock()
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        self.assertTrue(lm.matches(thread))

        # Now with a regex in our LabelMatcher
        lm = LabelMatcher('automatio(n*)')
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        self.assertTrue(lm.matches(thread))

    def test_no_false_positive_when_falling_back_to_non_re_match(self):
        # When we do a cruder regex match, we only should look freely in the haystack
        # when the regex is preceeded and followed by '.*'
        lm = LabelMatcher('^automation$')
        thread = Mock()

        thread.labels = MagicMock(return_value=['no match', 'automation/contact_form'])
        self.assertFalse(lm.matches(thread))

        lm = LabelMatcher('^automation.*')
        self.assertTrue(lm.matches(thread))

        lm = LabelMatcher('.*automation$')
        self.assertFalse(lm.matches(thread))
        
        lm = LabelMatcher('.*automation.*')
        self.assertTrue(lm.matches(thread))

    def test_raise_on_no_matching_groups(self):
        lm = LabelMatcher('label')
        thread = Mock()
        thread.labels = MagicMock(return_value=['no match', 'still no match'])
        self.assertFalse(lm.matches(thread))

    def test_reverse_match(self):
        lm = LabelMatcher('automation', True)
        thread = Mock()
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        self.assertFalse(lm.matches(thread))
        thread.labels = MagicMock(return_value=['no match'])
        self.assertTrue(lm.matches(thread))



class BodyMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            bm = BodyMatcher('')
        with self.assertRaises(Exception):
            bm = BodyMatcher(' ')

    def test_match(self):
        bm = BodyMatcher('automation')
        thread = Mock()
        thread.last_message_text = MagicMock(return_value='this message has automation in it')
        self.assertTrue(bm.matches(thread))


    def test_raise_on_no_matching_groups(self):
        bm = BodyMatcher('automation')
        thread = Mock()
        thread.last_message_text = MagicMock(return_value='this is not the phrase you are looking for')
        self.assertFalse(bm.matches(thread))

    def test_match_really_big_haystack(self):
        bm = BodyMatcher('additional details')
        thread = Mock()
        # get the path of the current file
        current_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_path, 'matcher_test_inputs/big_haystack.txt'), 'r') as f:
            haystack = str(f.read())
        thread.last_message_text = MagicMock(return_value=haystack)
        self.assertTrue(bm.matches(thread))
    # TODO: generic rent path message shouldn't math the condidtions we='re using in prod to talk about getting in touch with on site manager
    # TODO: generic zillow includes the phrase 'application', so we should be able to not match that when we='re adding a link to our application


class ExpressionMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            em = ExpressionMatcher('')
        with self.assertRaises(Exception):
            em = ExpressionMatcher(' ')

    def test_all(self):
        thread = Mock()

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


class ComboMatcherTest(unittest.TestCase):
    def test_no_creation_with_empty_list(self):
        with self.assertRaises(Exception):
            cm = ComboMatcher([])

    def test_match(self):
        mock_m_1 = Mock()
        mock_m_1.matches = MagicMock(return_value=True)
        l1 = ('match 1',)
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=True)
        l2 = ('match 2', 'match 3')
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        self.assertTrue(cm.matches(thread))

        self.assertEqual(mock_m_1.matches.call_count, 1)
        self.assertEqual(mock_m_2.matches.call_count, 1)

    def test_only_one_matches(self):
        mock_m_1 = Mock()
        mock_m_1.matches = MagicMock(return_value=True)
        l1 = ('match 1',)
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=False)
        l2 = ()
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        self.assertFalse(cm.matches(thread))

        self.assertEqual(mock_m_1.matches.call_count, 1)
        self.assertEqual(mock_m_2.matches.call_count, 1)

    def test_none_match(self):
        mock_m_1 = Mock()
        mock_m_1.matches = MagicMock(return_value=False)
        l1 = ()
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=False)
        l2 = ()
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        self.assertFalse(cm.matches(thread))

        self.assertEqual(mock_m_1.matches.call_count, 1)
        self.assertEqual(mock_m_2.matches.call_count, 0)


