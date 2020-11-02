import logging
import logging.config
import datetime
import os.path
import sys

def getLogger(file_name, module_name, level='INFO', path='./log/', root=True, stdout=True):
    file_name = path + '/' + file_name + '.log'
    if not os.path.isdir(path): os.makedirs(path)
    dict_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(funcName)s:- %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream' : sys.stdout
            },
            'file_handler': {
                'level': level,
                'filename': file_name,
                'class': 'logging.FileHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            module_name: {
                'handlers': ['file_handler', 'default'],
                'level': 'DEBUG',
                'propagate': True
            }
        },
        'disable_existing_loggers': False
    }
    if not root:
        dict_config.pop('handlers', None)  # All messages will be propagated to the root logger
        dict_config['loggers'][module_name].pop('handlers', None)
        dict_config['loggers'][module_name].pop('level', None)

    if root and not stdout:
        dict_config['handlers']['default']['level'] = 'ERROR'
    logging.config.dictConfig(dict_config)
    logger = logging.getLogger(module_name)
    for h in logger.handlers:
        if type(h) == logging.handlers.TimedRotatingFileHandler:
            h.suffix = '_%Y%m%d.log'
    return logger

