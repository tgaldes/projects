import pdb
from interface import implements
from framework.Logger import Logger
from framework.util import class_to_string

class BaseValidator(Logger):

    force_matches = False

    def __init__(self, child_name):
        if BaseValidator.force_matches:
            raise Exception("BaseValidator.force_matches set to true before all validators are created.")
        super(BaseValidator, self).__init__(child_name)

    @classmethod
    def set_validate_mode(cls, val):
    # TODO: it would be cool if we somehow created a try block in our scope when we set this to true, and set it to false if an exception was raise to keep the state correct
        BaseValidator.force_matches = val

    def force_match(self):
        return BaseValidator.force_matches

