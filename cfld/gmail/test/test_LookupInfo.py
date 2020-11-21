from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest

from LookupInfo import LookupInfo

class LookupInfoTest(unittest.TestCase):

    def test_basic(self):
        data = [[1, 2, 3], \
                ['', 4, 5], \
                [2, 12, 67], \
                ['', 'three', 'four']]
        li = LookupInfo(data)
        self.assertEqual(3, li.lookup_info(1, 2))
        self.assertEqual(5, li.lookup_info(1, 4))
        self.assertEqual(67, li.lookup_info(2, 12))
        self.assertEqual('four', li.lookup_info(2, 'three'))

    def test_raise_in_constructor(self):
        data = [[1, 2, 3], \
                ['', 4, 5], \
                [2, 12, 67], \
                ['', 'three', 'four'], \
                [1, 2, 3]]
        with self.assertRaises(Exception):
            li = LookupInfo(data)


