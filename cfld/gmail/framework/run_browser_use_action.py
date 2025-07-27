# add current directory to python path
import sys
sys.path.append('.')
# reads the json path as the first command line arg
import pdb
import bdb
import sys
import json
from time import sleep
import traceback

from framework.Logger import Logger
from services.ServiceCreator import ServiceCreator
from framework.RuleHolder import RuleHolder
from framework.Thread import Thread
from framework.Inbox import Inbox
from framework.RuleFactory import RuleFactory
from framework.util import process_thread_try_catch
from framework.Config import Config

from framework.Actions import BrowserUseAction


if __name__=='__main__':
    if len(sys.argv) < 2:
        print('No path specified for json config, exiting')
        exit(1)

    config = Config()
    config.initialize(sys.argv[1])

    sc = ServiceCreator()

    action = BrowserUseAction('new_applicant', sc.get_sheet_service().get_action_info())

    action.process('unused')
