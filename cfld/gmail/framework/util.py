import pdb
import inspect
from flatten_dict import flatten 
from flatten_dict import unflatten 
import framework.globals

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
    return kw['matches'][index]

def link(link_dest, link_text=None):
    if not link_text:
        link_text = link_dest
    return '<a href="{}">{}</a>'.format(link_dest, link_text)

def evaluate_expression(expression, **kwargs):
    try:
        local_request = __get_imports() + 'local_result = ' + expression.replace('thread', 'kwargs["thread"]')
        exec(local_request)
    except:
        pdb.set_trace()
    return locals()['local_result']

def __get_imports():
    try:
        return '\n'.join(framework.globals.g_org.get_imports()) + '\n'
    except:
        return ''

