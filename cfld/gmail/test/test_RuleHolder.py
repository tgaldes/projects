from unittest.mock import MagicMock, Mock
import unittest

from framework.RuleHolder import RuleHolder

class RuleHolderTest(unittest.TestCase):

    def test_no_match(self):
        mock_matcher = Mock()
        mock_matcher.matches = MagicMock(return_value=False)
        mock_action = Mock()
        mock_action.process = MagicMock()
        rh = RuleHolder(mock_action, mock_matcher)
        self.assertFalse(rh.process({}))
        mock_matcher.matches.assert_called_once_with({})
        mock_action.process.assert_not_called()

    def test_match(self):
        mock_matcher = Mock()
        mock_matcher.matches = MagicMock(return_value=True)
        l = ['a', 'b', 'c']
        mock_action = Mock()
        mock_action.process = MagicMock()
        rh = RuleHolder(mock_action, mock_matcher)
        self.assertTrue(rh.process({}))
        mock_matcher.matches.assert_called_once_with({})
        mock_action.process.assert_called_once_with({})

