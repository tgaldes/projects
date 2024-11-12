import bdb
import inspect
import traceback
from framework.Config import Config

def evaluate_expression(expression, **kwargs):
    # TODO: throw better exception message
    try:
        local_request = 'local_result = ' + expression.replace('thread,', 'kwargs["thread"],').replace('thread)', 'kwargs["thread"])').replace('(thread', '(kwargs["thread"]').replace('thread.', 'kwargs["thread"].').replace('inbox.', 'kwargs["inbox"].')
        exec(local_request)
    except bdb.BdbQuit as e:
        exit(0)
    except Exception as e:
        raise Exception("threw on local_request: {}. Exception:\n{}".format(local_request, e))
    return locals()['local_result']

def process_thread_try_catch(thread, inbox, rule_group, logger):
    try:
        rule_group.process(thread)
    except bdb.BdbQuit as e:
        exit(0)
    except Exception as e:
        logger.le('Caught exception while processing: {}. Will continue execution of rules while skipping this thread'.format(thread))
        logger.le('Trace: {}'.format(traceback.format_exc()))
        logger.le(str(e))
        thread.set_label(Config().get_thread_error_label())
        inbox.blacklist_id(thread.id())
