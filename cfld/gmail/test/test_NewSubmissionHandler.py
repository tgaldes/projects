from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
import os
import pathlib
import json

from Thread import Thread
from NewSubmissionHandler import NewSubmissionHandler
import NewLogger


# global config
NewLogger.global_log_level = 'DEBUG' # TODO: use the TestConfig module
parent_path = str(pathlib.Path(__file__).parent.absolute())
# REFACTOR in one test class, duplicated from test_Thread
def dict_from_fn(fn):
    with open(fn, 'r') as f:
        return json.load(f)

class NewSubmissionHandlerTest(unittest.TestCase):
    
    def test_basic(self):
        nsh = NewSubmissionHandler()
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/new_submission_only.txt'))
        t = Thread(d, {})
        t.short_name = MagicMock(return_value='UCLA')
        t.last_message_text = MagicMock(return_value='Email: djssi000000@gmail.com\n  Name: Dan Jassi\n        School: UCLA\n        Room: Single, Double, Triple\n        Move In: 2020-11-29\n        Move Out: \n        Gender: Male\n        Questions: Lease?\n        Can you do a showing?')
        nsh.handle_thread(t)
