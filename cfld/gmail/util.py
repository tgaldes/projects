import pdb
import inspect
from flatten_dict import flatten 
from flatten_dict import unflatten 
def list_of_emails_to_string_of_emails(l):
    ret = ''
    for item in l:
        ret = ret + item + ', '
    return ret[:-2]

def match(index):
    frame = inspect.currentframe()
    kw = frame.f_back.f_locals['kwargs']
    return kw['matches'][index]

def evaluate_expression(expression, **kwargs):
    local_request = 'local_result = ' + expression.replace('thread.', 'kwargs["thread"].')
    exec(local_request)
    return locals()['local_result']

def update_thread(thread, new_messages):
    if 'messages' not in thread or 'messages' not in new_messages:
        return thread
    for message in thread['messages']:
        for new_message in new_messages['messages']:
            if message['id'] == new_message['id']:
                message.update(new_message)
                break

def lookup_info(k1, k2):
    names = {'short_name' : {'2715 Portland Street' : 'USC'}} # TODO: read from sheets
    return names[k1][k2]



