




class UI:
    def __init__(self):
        self.errorMessage = 'Please try again'
        self.booleans = ['Y', 'N']
        self.booleans_string = '(Y/N)'
        self.houses = ['house1', 'house2']
        self.numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.menu_options = ['Send emails',
                             'Make phone calls',
                             'Send snail mail',
                             'Explore data (I can\'t wait to implement this!']
    def validate_input(self, userInput, options):
        if userInput in options:
            return True
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
            res = input(message +': ')
            if not self.validate_input(res, options):
                print(errorMessage)
                res = None
        return res

    def prompt_for_number(self, numbers=None):
        if not numbers:
            numbers = self.numbers
        return self.prompt_for_input('Please select a number', numbers)
    def prompt_for_bool(self):
        return self.prompt_for_input('Please select a value', self.booleans)
    def prompt_for_house(self):
        return self.prompt_for_input('Please select a house', self.houses)

    def prompt_for_input(self, msg, options):
        msg = '{}: {}'.format(msg, options)
        return self.prompt(msg, self.errorMessage, options)

    def menu(self):
        while True:
            print('Select a menu option')
            for i, option in enumerate(self.menu_options):
                print('{}: {}'.format(i, option))
            self.prompt_for_number([x for x in range(len(self.menu_options))])



if __name__=='__main__':
    ui = UI()
    ui.menu()















