from datetime import datetime, date, timedelta
import pdb

from framework.Logger import Logger
from orgs.cfld.util import short_name_from_thread

def room_types_to_string(types, joiner='and'):
    if len(types) == 1:
        return types[0] + 's'
    ret = '{}s {} {}s'.format(types[-2], joiner, types[-1])
    for i in range(-3, -1 * len(types) - 1, -1):
        ret = '{}s, '.format(types[i]) + ret
    return ret

class NewSubmissionHandler(Logger):
    def __init__(self, raw_availability, raw_availability_blurbs, max_availability_index=100):
        super(NewSubmissionHandler, self).__init__(__class__)
        self.suite_bathroom_ending = 'wb'
        self.availability = {}
        for row in raw_availability:
        # short_name, gender, room type, first date available, last date available
            if row[0]:
                last_key_zero = row[0]
                if row[0] in self.availability:
                    raise Exception('Duplicate key in availability data. \'{}\' specified twice.'.format(row[0]))
                self.availability[row[0]] = {}
            if row[1]:
                last_key_one = row[1]
                if row[1] in self.availability[last_key_zero]:
                    raise Exception('Duplicate key in availability data. \'{}\' specified twice.'.format(last_key_zero+ '.' + row[1]))
                self.availability[last_key_zero][row[1]] = {}
            move_in, move_out = None, None
            if len(row) > 3 and row[3]:
                    move_in = datetime.strptime(row[3], '%Y%m%d').date()
            if len(row) > 4 and row[4]:
                move_out = datetime.strptime(row[4], '%Y%m%d').date()
            if row[2] in self.availability[last_key_zero][last_key_one]:
                    raise Exception('Duplicate key in availability data. \'{}\' specified twice.'.format(last_key_zero+ '.' + row[1] + '.' + row[2]))

            self.availability[last_key_zero][last_key_one][row[2]] = [move_in, move_out]

        # key will represent result of 'desired move in date' - 'date available'
        # raw will specify the lowest result of above subtraction for which the blurb is used
        # we'll populate a map with the ranges so we can do a lookup later on when answering the threads
        if len(raw_availability_blurbs) != 3:
            raise Exception('only length 3 raw_availability_blurbs is supported.')
        if len(raw_availability_blurbs[1]) != 6:
            raise Exception('Need 5 values and one key for when move in needs to be delayed')
        max_availability_index = 365
        self.availability_blurbs = {}
        for i, tup in enumerate(raw_availability_blurbs):
            if tup[0] is None or tup[0] is '':
                self.availability_blurbs[None] = tup[1]
                continue
            if i + 1 < len(raw_availability_blurbs): # not the last item
                for x in range(int(tup[0]), int(raw_availability_blurbs[i + 1][0])):
                    if len(tup) > 2:
                        self.availability_blurbs[timedelta(days=x)] = tup[1:]
                    else:
                        self.availability_blurbs[timedelta(days=x)] = tup[1]
            else: # last item
                if max_availability_index <= int(tup[0]):
                    raise Exception('Cannot handle max_availability_index <= max entry in raw_availability blurbs. max_availability_index: {} max entry: {}'.format(max_availability_index, tup[0]))
                for x in range(int(tup[0]), max_availability_index):
                    self.availability_blurbs[timedelta(days=x)] = tup[1]


    def handle_thread(self, thread):
        self.li('Handling thread with id {} subject {}'.format(thread.identifier, thread.subject()))
        short_name = short_name_from_thread(thread) # we use the school to look up the room availability at the school
        if len(thread) == 1:
            return self.__handle_first_msg(thread)
        else:
            self.lw('not configured to respond to threads of more than length 1. Not doing anything')

    # extract the relevant fields of the message
    # return a dictionary of all the fields in the New Submission for short_name message
    # dictionary will look like {'name' : 'Tony K', 'email' : 'tony@ucla.edu' .....}
    def __parse_first_new_submission_message(self, text):
        ret = {}
        for item in text.split('\n'):
            try:
                k, value = item.split(':')
            # handle the case where there is a newline char in the questions text box
            except ValueError as ve:
                if 'questions' not in ret:
                    raise ve
                ret['questions'] += ' {}'.format(item.strip())
                continue
            key = k.lower().strip().replace(' ', '_') # let's use normal python names :)
            if key == 'school':
                ret['short_name'] = value.strip()
            elif key == 'name' \
                    or key == 'gender' \
                    or key == 'email' \
                    or key == 'questions':
                ret[key] = value.strip().lower()
            elif key == 'move_in' or key == 'move_out':
                v = value.strip()
                if not v:
                    ret[key] = None
                    continue
                ret[key] = datetime.strptime(v, '%Y-%m-%d').date()
            # TODO: with suite style bathroom
            elif key == 'room':
                types = []
                for room_selection in value.lower().split(','):
                    types.append(room_selection.strip())
                ret[key] = types
            else:
                raise Exception('Bad key passed to __parse_first_new_submission_message: {}'.format(k))
        return ret

    def __handle_first_msg(self, thread):
        parsed_msg = self.__parse_first_new_submission_message(thread.last_message_text())
        self.li(parsed_msg)
        not_available_types, delay_move_in_types, available_types = [], [], []
        for room_type in parsed_msg['room']:
            date_available = self.__get_date_available(parsed_msg['short_name'], parsed_msg['gender'], room_type)
            if date_available is None:
                not_available_types.append(room_type)
            else:
                delta = parsed_msg['move_in'] - date_available
                if delta >= timedelta(days=0):
                    available_types.append(room_type)
                else:
                    delay_move_in_types.append((room_type, date_available))

        response = ''
        # format a line of the message for each category (available, available after desired move in date, not available)
        # pass in all arguments we MIGHT use to format the string to support add arguments to the string without requiring a code change
        if available_types:
            formatted_list_of_room_types = room_types_to_string(available_types)
            response += self.availability_blurbs[timedelta(days=0)].format(room_type=formatted_list_of_room_types, \
                                desired=datetime.strftime(parsed_msg['move_in'], '%m-%d-%Y'), \
                                available = datetime.strftime(parsed_msg['move_in'], '%m-%d-%Y'), \
                                short_name = short_name_from_thread(thread))
        if delay_move_in_types:
            response += self.availability_blurbs[timedelta(days=-1)][0].format(room_type=delay_move_in_types[0][0], \
                                desired=datetime.strftime(parsed_msg['move_in'], '%m-%d-%Y'), \
                                available = datetime.strftime(delay_move_in_types[0][1], '%m-%d-%Y'), \
                                short_name = short_name_from_thread(thread))
            for room_type, date_available in delay_move_in_types[1:]:
                response += self.availability_blurbs[timedelta(days=-1)][1].format(room_type=room_type, \
                                    desired=datetime.strftime(parsed_msg['move_in'], '%m-%d-%Y'), \
                                    available = datetime.strftime(date_available, '%m-%d-%Y'), \
                                    short_name = short_name_from_thread(thread))
            # Add the end value
            if len(delay_move_in_types) == 1:
                response += self.availability_blurbs[timedelta(days=-1)][2] # 'Let me know if that interests you'
            elif len(delay_move_in_types) == 2:
                response += self.availability_blurbs[timedelta(days=-1)][3] # 'Let me know if either of those interest you'
            else:
                response += self.availability_blurbs[timedelta(days=-1)][4] # 'Let me know if any ...'

        if not_available_types:
            formatted_list_of_room_types = room_types_to_string(not_available_types, joiner='or')
            response += self.availability_blurbs[None].format(room_type=formatted_list_of_room_types, \
                                desired=datetime.strftime(parsed_msg['move_in'], '%m-%d-%Y'), \
                                short_name = short_name_from_thread(thread))
        return response

    def __get_date_available(self, short_name, gender, room_type):
        school_by_gender = self.availability[short_name][gender]
        if room_type in school_by_gender:
            return school_by_gender[room_type][0]
        return None





if __name__=='__main__':
    nsh = NewSubmissionHandler()

