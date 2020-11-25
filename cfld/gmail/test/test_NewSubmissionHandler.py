from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
import os
import pathlib
import json
from datetime import date, timedelta
import pdb

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
    
    def test_first_message(self):
        move_in = date(2020, 1, 1)
        move_in_two = move_in + timedelta(days=1)
        short_name, gender, room_type, room_type_b, room_type_c = 'UCLA', 'male', 'single', 'triple', 'quad'
        unavailable_room = 'double'
        email = 'djssi000000@gmail.com'
        raw_email_text = 'Email: {}\n  Name: Dan Jassi\n        School: UCLA\n        Room: {}\n        Move In: {}\n        Move Out: \n        Gender: Male\n        Questions: Lease?\n        Can you do a showing?'
        raw_availability = [[short_name, gender, room_type, move_in.strftime('%Y%m%d'), '20200514'], \
                            ['', '', unavailable_room, '', ''],
                            ['', '', room_type_b, move_in.strftime('%Y%m%d'), '20200514'],
                            ['', '', room_type_c, move_in_two.strftime('%Y%m%d'), '20200514']]
        nothing_open, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three,  open_at_desired_move_in = 'nothing open\n\n', 'delay move in', 'delay move in two', 'let me know if that\n\n', 'let me know if either of those\n\n', 'let me know if any of those\n\n', 'room_type is open at desired date\n\n'

        minus_index = -1000
        zero_index = 0
        max_index = 100
        raw_availability_blurbs = \
                [(None , nothing_open), \
                (minus_index, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three, ), \
                (zero_index, open_at_desired_move_in)]
        nsh = NewSubmissionHandler(raw_availability=raw_availability, raw_availability_blurbs=raw_availability_blurbs, max_availability_index=max_index)
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/new_submission_only.txt'))
        t = Thread(d, {})
        t.short_name = MagicMock(return_value=short_name)

        # one room type desired open for move in
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type, move_in.strftime('%Y-%m-%d')))
        t.append_to_draft = MagicMock()
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_once_with(open_at_desired_move_in, [email])

        # two rooms type's open for move in # TODO: we can get more extensive with the test by having open_at_desired_move_in contain arguments that must be formatted with the room type
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type + ', ' + room_type_b, move_in.strftime('%Y-%m-%d')))
        t.append_to_draft = MagicMock()
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_once_with(open_at_desired_move_in, [email])

        # one room type desired before it's available
        desired_move_in = move_in - timedelta(days=1)
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(delay_move_in + delay_move_in_end_one, [email])

        # two rooms types desired before they are availble
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type + ', ' + room_type_b, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(delay_move_in + delay_move_in_two + delay_move_in_end_two, [email])

        # three rooms types desired before they are availble
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type + ', ' + room_type_b + ', ' + room_type_c, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(delay_move_in + delay_move_in_two + delay_move_in_two + delay_move_in_end_three, [email])

        # one room type not availalbe
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, unavailable_room, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(nothing_open, [email])

        unavailable_room_two = 'garbarge value' # we should be able to handle user checking a box where the type of room isn't configured at all for that school
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, unavailable_room_two, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(nothing_open, [email])

        # two room types not available
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, unavailable_room + ', ' + unavailable_room_two, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(nothing_open, [email])

        # one ready for move in, one desired before available, one room type not available
        desired_move_in = move_in
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, room_type_c + ', ' + room_type + ',' + unavailable_room_two, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(open_at_desired_move_in + delay_move_in + delay_move_in_end_one + nothing_open, [email])

        # change the order of args
        t.last_message_text = MagicMock(return_value=raw_email_text.format(email, unavailable_room_two + ', ' + room_type_c + ',' + room_type, desired_move_in.strftime('%Y-%m-%d')))
        nsh.handle_thread(t)
        t.append_to_draft.assert_called_with(open_at_desired_move_in + delay_move_in + delay_move_in_end_one + nothing_open, [email])

# ------------------- Constructor stuff ----------------------------

    def test_throw_with_bad_availability_data(self):
        raw_availability = [['UCLA', 'male', 'single', '20200101', '20200514'], \
                            # double occurence of key one
                            ['UCLA', '', 'double', '', '']]
        with self.assertRaises(Exception):
            nsh = NewSubmissionHandler(raw_availability=raw_availability)

        raw_availability = [['UCLA', 'male', 'single', '20200101', '20200514'], \
                            # double occurence of key one
                            ['', 'male', 'double', '', '']]
        with self.assertRaises(Exception):
            nsh = NewSubmissionHandler(raw_availability=raw_availability)
        raw_availability = [['UCLA', 'male', 'single', '20200101', '20200514'], \
                            # double occurence of key two
                            ['', '', 'single', '', '']]
        with self.assertRaises(Exception):
            nsh = NewSubmissionHandler(raw_availability=raw_availability)

    def test_support_empty_date_string_in_raw_availability(self):
        short_name, gender, room_type = 'UCLA', 'male', 'double'
        raw_availability = [[short_name, gender, 'single', '20200101', '20200514'], \
                            ['', '', room_type, '', '']]
        nsh = NewSubmissionHandler(raw_availability=raw_availability)
        self.assertEqual(None, nsh.availability[short_name][gender][room_type][0])
        self.assertEqual(None, nsh.availability[short_name][gender][room_type][1])

    def test_parse_date_in_raw_availability(self):
        short_name, gender, room_type = 'UCLA', 'male', 'double'
        room_type_b = 'single'
        move_in, move_out = date(2020, 1, 1), date(2020, 5, 14)
        raw_availability = [[short_name, gender, room_type_b, move_in.strftime('%Y%m%d'), move_out.strftime('%Y%m%d')], \
                            ['', '', room_type, '20190101', '']]
        nsh = NewSubmissionHandler(raw_availability=raw_availability)
        self.assertEqual(date(2019, 1, 1), nsh.availability[short_name][gender][room_type][0])
        self.assertEqual(None, nsh.availability[short_name][gender][room_type][1])
        self.assertEqual(move_in, nsh.availability[short_name][gender][room_type_b][0])
        self.assertEqual(move_out, nsh.availability[short_name][gender][room_type_b][1])

    def test_populate_availability_blurbs(self):
        raw_availability = [['UCLA', 'male', 'single', '20200101', '20200514'], \
                            ['', '', 'double', '20190101', '']]
        nothing_open, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three,  open_at_desired_move_in = 'nothing open\n\n', 'delay move in', 'delay move in two', 'let me know if that\n\n', 'let me know if either of those\n\n', 'let me know if any of those\n\n', 'room_type is open at desired date\n\n'

        minus_index = -1000
        zero_index = 0
        max_index = 100
        raw_availability_blurbs = \
                [(None , nothing_open), \
                (minus_index, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three, ), \
                (zero_index, open_at_desired_move_in)]

        nsh = NewSubmissionHandler(raw_availability=raw_availability, raw_availability_blurbs=raw_availability_blurbs, max_availability_index=max_index)
        self.assertEqual(nothing_open, nsh.availability_blurbs[None])
        for i in range(minus_index, zero_index):
            self.assertEqual(delay_move_in, nsh.availability_blurbs[timedelta(days=i)][0])
        for i in range(zero_index, max_index):
            self.assertEqual(open_at_desired_move_in, nsh.availability_blurbs[timedelta(days=i)])

# ------------------- End constructor stuff ----------------------------
