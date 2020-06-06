from ModelEmployee import ModelEmployee
from Google import Google
import pickle
import pdb




class UI:
    def __init__(self, emp):
        self.errorMessage = 'Please try again'
        self.booleans = ['Y', 'N']
        self.booleans_string = '(Y/N)'
        self.numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.employee = emp

        self.menu = [('Send emails', emp.send_intro_emails),
                      ('Make phone calls', emp.make_phone_calls),
                      ('Send snail mail', emp.send_snail_mail)]
                      #('Explore data (I can\'t wait to implement this!', lambda *args: None)]
        self.finished = 'Done'
    def validate_input(self, userInput, options):
        # match strings
        try:
            if userInput in options:
                return True
            if userInput == self.finished:
                return True
        except:
            pass
        try:
            if int(userInput) in options:
                return True
        except:
            pass
        else:
            return False

    def prompt(self, message, errorMessage, options):
        """Prompt for input given a message and return that value after verifying the input.

        Keyword arguments:
        message -- the message to display when asking the user for the value
        errormessage -- the message to display when the value fails validation
        isvalid -- a function that returns True if the value given by the user is valid
        """
        res = None
        while res is None:
            res = input(message +': \n')
            if not self.validate_input(res, options):
                print(errorMessage)
                res = None
        return res

    def prompt_for_number(self, numbers=None):
        if not numbers:
            numbers = self.numbers
        return int(self.prompt_for_input('Please select a number', numbers))
    def prompt_for_bool(self):
        return self.prompt_for_input('Please select a value', self.booleans)
    def prompt_for_school(self):
        return self.prompt_for_input('Please select a house', self.employee.get_school_list)

    def prompt_for_input(self, msg, options):
        msg = '{}: {} or {}'.format(msg, options, self.finished)
        return self.prompt(msg, self.errorMessage, options)

    def get_multiple_selections(self, options):
        last_input = ''
        selections = []
        while True:
            last_input = self.prompt_for_input('Please make selctions one at a time or input \'{}\' when finished'.format(self.finished), options)
            if last_input == self.finished:
                return selections
            selections.append(last_input)
            print('Current selctions are: {}'.format(selections))
        
    def build_filter(self, options): # return (list, bool is_include)
        selections = self.get_multiple_selections(options)
        print('Is filter include?')
        ans = self.prompt_for_bool()
        return (selections, ans)



    def show_menu(self):
        while True:
            print('Select a menu option')
            for i, option in enumerate(self.menu):
                name, func = option
                print('{}: {}'.format(i, name))
            selection = self.prompt_for_number([x for x in range(len(self.menu))])
            f = self.menu[selection][1]
# TODO we should look at the function signature here and use that to determine what arguments we need to prompt for
            self.build_filter(self.employee.get_school_list())
            f()



if __name__=='__main__':
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    emp = ModelEmployee(g2)
    ui = UI(emp)
    ui.show_menu()



