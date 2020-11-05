import logging
from NewLogger import getLogger
import pdb

class Logger:
    def __init__(self, parent_name):
        self.logger = getLogger('example', parent_name, root=True, stdout=True)

    def ld(self, s):
        self.logger.debug(s)

    def li(self, s):
        self.logger.info(s)

    def lw(self, s):
        self.logger.warn(s)
        
    def le(self, s):
        self.logger.error(s)

    def lf(self, s):
        self.logger.fatal(s)
