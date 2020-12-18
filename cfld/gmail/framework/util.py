import pdb
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
    return kw['matches'][index]

def link(link_dest, link_text=None):
    if not link_text:
        link_text = link_dest
    return '<a href="{}">{}</a>'.format(link_dest, link_text)

def evaluate_expression(expression, **kwargs):
    try:
        local_request = get_imports() + 'local_result = ' + expression.replace('thread', 'kwargs["thread"]')
        exec(local_request)
    except:
        raise Exception("threw on local_request: {}".format(local_request))
    return locals()['local_result']

def get_imports():
    try:
        return '\n'.join(framework.globals.g_org.get_imports()) + '\n'
    except:
        return ''

