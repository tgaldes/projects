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
    # update indiv messages
    for message in thread['messages']:
        for new_message in new_messages['messages']:
            if message['id'] == new_message['id']:
                message.update(new_message)
                break

    # update thread attributes
    for item in new_messages:
        if item != 'messages':
            thread[item] = new_messages[item]

def short_name(key):
    return lookup_info('short_name', key.strip())

def lookup_info(k1, k2):
    names = {'short_name' : 
        {'2715 Portland St' : 'USC',
         '123 S 11th St' : 'SJSU',
         '649 Gayley Ave' : 'UCLA',
         '165 4th St NW' : 'Georgia Tech',
         '165 4th Street Northwest' : 'Georgia Tech',
         '1000 5th St SE' : 'UMN'}} # TODO: read from sheets
    return names[k1][k2]



