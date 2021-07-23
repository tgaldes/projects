import logging
from framework.NewLogger import getLogger
from framework.util import class_to_string
import framework.globals

class Logger:
    def __init__(self, parent_name, path='./log/', root=False):
        self.logger = getLogger('gmail_service_log', class_to_string(parent_name), path=path, root=root)

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
