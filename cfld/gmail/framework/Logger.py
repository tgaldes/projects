import logging
from framework.NewLogger import getLogger
from framework.util import class_to_string

class Logger:
    def __init__(self, parent_name):
        self.logger = getLogger('example', class_to_string(parent_name), root=True, stdout=True)

    def ld(self, s):
        self.logger.debug(s)

    def li(self, s):
        self.logger.info(s)

    def lw(self, s):
        self.logger.warning(s)
        
    def le(self, s):
        self.logger.error(s)

    def lf(self, s):
        self.logger.fatal(s)
