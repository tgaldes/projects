from unittest.mock import MagicMock, Mock
import unittest
from Matchers import SubjectMatcher, ExpressionMatcher, LabelMatcher, ComboMatcher
from Thread import Thread
import NewLogger
NewLogger.global_log_level = 'DEBUG'

class SubjectMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            sm = SubjectMatcher('')

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

    def test_raise_on_no_matching_groups(self):
        sm = SubjectMatcher('test subject')
        thread = Thread({}, None)
        thread.subject = MagicMock(return_value='no match')
        with self.assertRaises(Exception):
            sm.get_matching_groups({})
        

class ExpressionMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            em = ExpressionMatcher('')

    def test_all(self):
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

class LabelMatcherTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            lm = LabelMatcher('')

    def test_match(self):
        lm = LabelMatcher('automation')
        thread = Thread({}, None)
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        self.assertTrue(lm.matches(thread))
        self.assertEqual((), lm.get_matching_groups(thread))

        # Now with a regex in our LabelMatcher
        lm = LabelMatcher('automatio(n*)')
        thread.labels = MagicMock(return_value=['no match', 'automation'])
        self.assertTrue(lm.matches(thread))
        self.assertEqual(('n',), lm.get_matching_groups(thread))

    def test_no_match(self):
        pass

    def test_raise_on_no_matching_groups(self):
        lm = LabelMatcher('label')
        thread = Thread({}, None)
        thread.labels = MagicMock(return_value=['no match', 'still no match'])
        with self.assertRaises(Exception):
            lm.get_matching_groups({})

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
        self.assertTrue(cm.matches('input'))
        self.assertEqual(['match 1', 'match 2', 'match 3'], cm.get_matching_groups('input'))

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
        self.assertFalse(cm.matches('input'))
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
        self.assertFalse(cm.matches('input'))
        with self.assertRaises(Exception):
            cm.get_matching_groups({})

        self.assertEqual(mock_m_1.matches.call_count, 2)
        self.assertEqual(mock_m_1.get_matching_groups.call_count, 0)
        self.assertEqual(mock_m_2.matches.call_count, 0)
        self.assertEqual(mock_m_2.get_matching_groups.call_count, 0)
