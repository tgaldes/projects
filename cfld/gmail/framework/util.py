import pdb
import bdb
import inspect
from flatten_dict import flatten 
from flatten_dict import unflatten 
import framework.globals
# TODO: diff list of user utils and framework utils that aren't exposed to user
def class_to_string(c):
    temp = str(c)
    temp = temp[temp.rfind('.') + 1:]
    if temp.find('\'') == -1:
        return temp
    return temp[:temp.find('\'')]

def list_of_emails_to_string_of_emails(l):
    if type(l) == str:
        return l
    ret = ''
    for item in l:
        ret = ret + item + ', '
    return ret[:-2]

def match(index):
    frame = inspect.currentframe()
    kw = frame.f_back.f_locals['kwargs']
    if index < len(kw['matches']):
        return kw['matches'][index]
    framework.globals.g_logger.lw('Index {} out of range, len(matches) == {}'.format(index, len(kw['matches'])))
    return ''

def link(link_dest, link_text=None):
    if not link_text:
        link_text = link_dest
    return '<a href="{}">{}</a>'.format(link_dest, link_text)

def evaluate_expression(expression, **kwargs):
    # TODO: throw better exception message
    try:
        local_request = get_imports() + 'local_result = ' + expression.replace('thread,', 'kwargs["thread"],').replace('thread)', 'kwargs["thread"])').replace('(thread', '(kwargs["thread"]').replace('thread.', 'kwargs["thread"].').replace('inbox.', 'kwargs["inbox"].')
        exec(local_request)
    except bdb.BdbQuit as e:
        exit(0)
    except Exception as e:
        raise Exception("threw on local_request: {}. Exception:\n{}".format(local_request, e))
    return locals()['local_result']

def get_imports():
    try:
        return '\n'.join(framework.globals.g_org.get_imports()) + '\n'
    except:
        return ''

