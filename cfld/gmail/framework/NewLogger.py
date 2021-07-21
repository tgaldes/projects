import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler

import logging.config
import datetime
import os.path
import sys
import pdb

global_log_level = logging.DEBUG
def getLogger(file_name, module_name, path='./log/', root=False):
    file_name = os.path.join(path, file_name + '.log')
    if not os.path.isdir(path): os.makedirs(path)
    format = '%(asctime)s [%(levelname)7s] %(name)20s:- %(message)s'
    if root:
        logger = logging.getLogger()
        logger.setLevel(global_log_level)
        # new file every minute
        rotation_logging_handler = TimedRotatingFileHandler(file_name, 
                                       when='midnight', 
                                       interval=1)
        rotation_logging_handler.setLevel(global_log_level)

        rotation_logging_handler.setFormatter(logging.Formatter(format))
        rotation_logging_handler.suffix = '%Y%m%d'
        logger.addHandler(rotation_logging_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(global_log_level)
        console_handler.setFormatter(logging.Formatter(format))
        logger.addHandler(console_handler)
        return logger

    else:
        return logging.getLogger(module_name)
