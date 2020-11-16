from Logger import Logger
from datetime import datetime, date
import pdb




class NewSubmissionHandler(Logger):
    def __init__(self, response_data={}, statements={}):
        super(NewSubmissionHandler, self).__init__(__name__)

        self.response_data = response_data
        if not self.response_data:
            self.response_data = {'UCLA' : 
                                     {'rooms' : 
                                        {'male' : 
                                            { 'single' : ['20210101', '20200514'],
                                              'double' : ['', ''], # we dont have a double available soon enough to tell people
                                            },
                                         'female' : 
                                            { 'single' : ['20210515', '20210831'],
                                              'double' : ['20201101', ''] # available now until forever
                                            },
                                        }
                                     } # end USC
                                 }

        self.statements = statements
        if not self.statements:
            self.statements = {
                None : 'We don\'t have this available for your gender',
                -1000 : 'We have this open now, we could move you in within a week if you are prompt with the application submission'}


    def handle_thread(self, thread):
        short_name = thread.short_name() # key into the response data
        if len(thread) == 1:
            self.__handle_first_msg(thread)
        else:
            self.lw('{} not configured to respond to threads of more than length 1. Not doing anything'.format(__name__))

    # extract the relevant fields of the message
    # return a dictionary of all the fields in the New Submission for short_name message
    # dictionary will look like {'name' : 'Tony K', 'email' : 'tony@ucla.edu' .....}
    def __parse_first_new_submission_message(self, text):
        ret = {}
        for item in text.split('\n'):
            print(item)
            try:
                k, value = item.split(':')
            # handle the case where there is a newline char in the questions text box
            except ValueError as ve:
                if 'questions' not in ret:
                    pdb.set_trace()
                    raise ve
                ret['questions'] += ' {}'.format(item.strip())
                continue
            key = k.lower().strip().replace(' ', '_') # let's use normal python names :)
            if key == 'school' \
                    or key == 'name' \
                    or key == 'gender' \
                    or key == 'email' \
                    or key == 'questions':
                ret[key] = value.strip()
            elif key == 'move_in' or key == 'move_out':
                v = value.strip()
                if not v:
                    ret[key] = None
                    continue
                ret[key] = datetime.strptime(v, '%Y-%m-%d').date
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





if __name__=='__main__':
    nsh = NewSubmissionHandler()

