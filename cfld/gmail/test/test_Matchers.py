from unittest.mock import MagicMock, Mock
import unittest
import os
from framework.Matchers import *
from test.TestConfig import parent_path


class SubjectMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            sm = SubjectMatcher('')

    def test_no_match(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='')
        thread.id = MagicMock(return_value='mock id')
        self.assertFalse(sm.matches(thread))

    def test_match(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='test subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(sm.matches(thread))

    def test_raise_on_no_matching_groups(self):
        sm = SubjectMatcher('test subject')
        thread = Mock()
        thread.subject = MagicMock(return_value='no match')
        thread.id = MagicMock(return_value='mock id')
        with self.assertRaises(Exception):
            sm.get_matching_groups({})
        

class LabelMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            lm = LabelMatcher('')

    def test_match(self):
        lm = LabelMatcher('automation')
        thread = Mock()
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(lm.matches(thread))
        self.assertEqual((), lm.get_matching_groups(thread))

        # Now with a regex in our LabelMatcher
        lm = LabelMatcher('automatio(n*)')
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(lm.matches(thread))
        self.assertEqual(('n',), lm.get_matching_groups(thread))

    def test_raise_on_no_matching_groups(self):
        lm = LabelMatcher('label')
        thread = Mock()
        thread.labels = MagicMock(return_value=['no match', 'still no match'])
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertFalse(lm.matches(thread))
        with self.assertRaises(Exception):
            lm.get_matching_groups({})


class BodyMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            bm = BodyMatcher('')

    def test_match(self):
        bm = BodyMatcher('.*automation.*')
        thread = Mock()
        thread.last_message_text = MagicMock(return_value='this message has automation in it')
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(bm.matches(thread))
        self.assertEqual((), bm.get_matching_groups(thread))

        # Now with a regex in our BodyMatcher
        bm = BodyMatcher('.*automatio(n*).*')
        thread.last_message_text = MagicMock(return_value='this message also has automation in it')
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(bm.matches(thread))
        self.assertEqual(('n',), bm.get_matching_groups(thread))

        # Now with a different case than our regex
        # Right now we are treating body matches as case insensitive
        bm = BodyMatcher('.*automatio(n*).*')
        thread.last_message_text = MagicMock(return_value='this message also has AuTomation in it')
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(bm.matches(thread))
        self.assertEqual(('n',), bm.get_matching_groups(thread))

    def test_raise_on_no_matching_groups(self):
        bm = BodyMatcher('.*automation.*')
        thread = Mock()
        thread.last_message_text = MagicMock(return_value='this is not the phrase you are looking for')
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertFalse(bm.matches(thread))
        with self.assertRaises(Exception):
            bm.get_matching_groups({})

    def test_match_really_big_haystack(self):
        bm = BodyMatcher('.*additional details.*')
        thread = Mock()
        with open(os.path.join(parent_path, 'matcher_test_inputs/big_haystack.txt'), 'r') as f:
            haystack = str(f.read())
        thread.last_message_text = MagicMock(return_value=haystack)
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(bm.matches(thread))
        self.assertEqual((), bm.get_matching_groups(thread))
    # TODO: generic rent path message shouldn't math the condidtions we='re using in prod to talk about getting in touch with on site manager
    # TODO: generic zillow includes the phrase 'application', so we should be able to not match that when we='re adding a link to our application


class ExpressionMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            em = ExpressionMatcher('')

    def test_all(self):
        thread = Mock()
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')

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
        mock_m_1.get_matching_groups = MagicMock(return_value=l1)
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=True)
        l2 = ('match 2', 'match 3')
        mock_m_2.get_matching_groups = MagicMock(return_value=l2)
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertTrue(cm.matches(thread))
        self.assertEqual(['match 1', 'match 2', 'match 3'], cm.get_matching_groups(thread))

        self.assertEqual(mock_m_1.matches.call_count, 2)
        self.assertEqual(mock_m_1.get_matching_groups.call_count, 1)
        self.assertEqual(mock_m_2.matches.call_count, 2)
        self.assertEqual(mock_m_2.get_matching_groups.call_count, 1)

    def test_only_one_matches(self):
        mock_m_1 = Mock()
        mock_m_1.matches = MagicMock(return_value=True)
        l1 = ('match 1',)
        mock_m_1.get_matching_groups = MagicMock(return_value=l1)
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=False)
        l2 = ()
        mock_m_2.get_matching_groups = MagicMock()
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertFalse(cm.matches(thread))
        with self.assertRaises(Exception):
            cm.get_matching_groups({})

        self.assertEqual(mock_m_1.matches.call_count, 2)
        self.assertEqual(mock_m_1.get_matching_groups.call_count, 1)
        self.assertEqual(mock_m_2.matches.call_count, 2)
        self.assertEqual(mock_m_2.get_matching_groups.call_count, 0)

    def test_none_match(self):
        mock_m_1 = Mock()
        mock_m_1.matches = MagicMock(return_value=False)
        l1 = ()
        mock_m_1.get_matching_groups = MagicMock(return_value=l1)
        mock_m_2 = Mock()
        mock_m_2.matches = MagicMock(return_value=False)
        l2 = ()
        mock_m_2.get_matching_groups = MagicMock()
        cm = ComboMatcher([mock_m_1, mock_m_2])
        thread = Mock()
        thread.subject = MagicMock(return_value='mock subject')
        thread.id = MagicMock(return_value='mock id')
        self.assertFalse(cm.matches(thread))
        with self.assertRaises(Exception):
            cm.get_matching_groups({})

        self.assertEqual(mock_m_1.matches.call_count, 2)
        self.assertEqual(mock_m_1.get_matching_groups.call_count, 0)
        self.assertEqual(mock_m_2.matches.call_count, 0)
        self.assertEqual(mock_m_2.get_matching_groups.call_count, 0)


