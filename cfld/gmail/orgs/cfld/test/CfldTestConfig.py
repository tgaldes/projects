from datetime import date, timedelta

move_in = date(2020, 1, 1)
move_in_two = move_in + timedelta(days=1)
short_name, gender, room_type, room_type_b, room_type_c = 'UCLA', 'male', 'single', 'triple', 'quad'
unavailable_room = 'double'
raw_availability = [[short_name, gender, room_type, move_in.strftime('%Y%m%d'), '20200514'], \
                    ['', '', unavailable_room, '', ''],
                    ['', '', room_type_b, move_in.strftime('%Y%m%d'), '20200514'],
                    ['', '', room_type_c, move_in_two.strftime('%Y%m%d'), '20200514']]
nothing_open, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three,  open_at_desired_move_in = 'nothing open\n\n', 'delay move in', 'delay move in two', 'let me know if that\n\n', 'let me know if either of those\n\n', 'let me know if any of those\n\n', 'room_type is open at desired date\n\n'

minus_index = '-1000'
zero_index = '0'
max_index = 100
raw_availability_blurbs = \
        [(None , nothing_open), \
        (minus_index, delay_move_in, delay_move_in_two, delay_move_in_end_one, delay_move_in_end_two, delay_move_in_end_three, ), \
        (zero_index, open_at_desired_move_in)]

