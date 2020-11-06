from unittest.mock import MagicMock, Mock
import unittest
import NewLogger
NewLogger.global_log_level = 'DEBUG'

from RuleHolder import RuleHolder

class RuleHolderTest(unittest.TestCase):

    def test_no_match(self):
        mock_matcher = Mock()
        mock_matcher.matches = MagicMock(return_value=False)
        mock_matcher.get_matching_groups = MagicMock(return_value=[])
        mock_action = Mock()
        mock_action.process = MagicMock()
        rh = RuleHolder(mock_action, mock_matcher)
        rh.process({})
        mock_matcher.matches.assert_called_once_with({})
        mock_matcher.get_matching_groups.assert_not_called()
        mock_action.process.assert_not_called()

    def test_match(self):
        mock_matcher = Mock()
        mock_matcher.matches = MagicMock(return_value=True)
        l = ['a', 'b', 'c']
        mock_matcher.get_matching_groups = MagicMock(return_value=l)
        mock_action = Mock()
        mock_action.process = MagicMock()
        rh = RuleHolder(mock_action, mock_matcher)
        rh.process({})
        mock_matcher.matches.assert_called_once_with({})
        mock_matcher.get_matching_groups.assert_called_once_with({})
        mock_action.process.assert_called_once_with({}, l)

